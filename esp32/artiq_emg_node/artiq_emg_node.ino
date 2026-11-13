#include <WiFi.h>
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <PubSubClient.h>

// --- MQTT BROKER CONFIGURATION ---
const char* mqtt_server = "YOUR_MQTT_BROKER_IP"; // Broker IP or hostname
const int mqtt_port = 1883;                      // Standard MQTT TCP port (or mapped proxy port)
const char* ap_name = "ArtiQ-EMG-Setup";         // Captive Portal AP SSID

WiFiClient espClient;
PubSubClient client(espClient);

// --- EMG PIN & VARIABLES (MyoWare 2.0 ENV Output) ---
const int emgPin = 32; // Connect MyoWare 2.0 ENV pin to GPIO 32 (3.3V power)
int baseline = 0;
float envelope = 0;
float attack = 0.9;
float decay = 0.99;

float mvcValue = 0;
bool isCalibrating = false;
unsigned long calibrateStart = 0;
float calibratePeak = 0;

String macAddr = "";
String topicData = "";
String topicStatus = "";
String topicCommand = "";

// Read averaged ADC sample to reduce single-spike jitter on MyoWare 2.0 ENV pin
int readSmoothedADC() {
    long sum = 0;
    const int samples = 8;
    for (int i = 0; i < samples; i++) {
        sum += analogRead(emgPin);
        delayMicroseconds(50);
    }
    return sum / samples;
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String msg = "";
    for (int i = 0; i < length; i++) msg += (char)payload[i];
    msg.trim();

    if (msg == "calibrate") {
        isCalibrating = true;
        calibrateStart = millis();
        calibratePeak = 0;
        Serial.println("[COMMAND] MVC Calibration Started (3s)!");
    } else if (msg == "reset") {
        mvcValue = 0;
        Serial.println("[COMMAND] MVC Reset!");
    } else if (msg == "relax" || msg == "baseline") {
        long sum = 0;
        for (int i = 0; i < 100; i++) {
            sum += readSmoothedADC();
            delay(5);
        }
        baseline = sum / 100;
        envelope = 0;
        Serial.printf("[COMMAND] Baseline (Relax) Re-calibrated: %d\n", baseline);
    }
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Connecting to MQTT Broker...");
        String clientId = "ArtiQ-Node-" + macAddr;

        // Setup LWT: Topic status, QoS 1, Retain True, Payload "offline"
        if (client.connect(clientId.c_str(), NULL, NULL, topicStatus.c_str(), 1, true, "offline")) {
            Serial.println(" CONNECTED!");
            client.publish(topicStatus.c_str(), "online", true);
            client.subscribe(topicCommand.c_str());
        } else {
            Serial.print(" FAILED, rc=");
            Serial.print(client.state());
            Serial.println(". Retry in 5s...");
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(115200);

    // Pin & ADC Setup (12-bit 0-4095, 0-3.3V range for MyoWare 2.0)
    pinMode(emgPin, INPUT);
    analogReadResolution(12);
    analogSetPinAttenuation(emgPin, ADC_11db);

    Serial.println("\n=== ARTIQ EMG PRODUCTION NODE (MYOWARE 2.0) ===");

    // WiFiManager Provisioning (20s timeout on saved Wi-Fi before opening Captive Portal)
    WiFi.mode(WIFI_STA);
    WiFiManager wm;
    wm.setConnectTimeout(20);       // Open portal if saved network is not found within 20s
    wm.setConfigPortalTimeout(180); // Reboot fallback if portal is idle for 3 minutes

    Serial.println("[WIFI] Attempting saved Wi-Fi connection (20s timeout)...");
    if (!wm.autoConnect(ap_name)) {
        Serial.println("[WIFI] Portal timeout or connection failed. Rebooting...");
        delay(1000);
        ESP.restart();
    }

    // Calibrate Baseline (Relax 0%)
    Serial.println("Relax your forearm muscle for baseline calibration (2 seconds)...");
    delay(2000);
    long sum = 0;
    for (int i = 0; i < 200; i++) {
        sum += readSmoothedADC();
        delay(5);
    }
    baseline = sum / 200;
    Serial.printf("Registered baseline (Relax): %d\n", baseline);

    macAddr = WiFi.macAddress();
    macAddr.replace(":", "");

    topicData = "artiq/emg/data/" + macAddr;
    topicStatus = "artiq/emg/status/" + macAddr;
    topicCommand = "artiq/emg/command/" + macAddr;

    Serial.println("\nWiFi Connected! IP: " + WiFi.localIP().toString() + " | Node MAC: " + macAddr);

    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(mqttCallback);
}

void loop() {
    if (!client.connected()) reconnect();
    client.loop();

    // 1000Hz Sampling
    static unsigned long lastSample = 0;
    if (micros() - lastSample < 1000) return;
    lastSample = micros();

    int raw = readSmoothedADC();

    // MyoWare 2.0 ENV pin outputs hardware-rectified DC envelope (0V - 3.3V / 0 - 4095)
    int signalDiff = raw - baseline;
    if (signalDiff < 0) signalDiff = 0;

    if (signalDiff > envelope) envelope = (attack * signalDiff) + ((1.0 - attack) * envelope);
    else envelope = (decay * envelope) + ((1.0 - decay) * signalDiff);

    if (isCalibrating) {
        if (envelope > calibratePeak) calibratePeak = envelope;
        if (millis() - calibrateStart > 3000) {
            if (calibratePeak > 50) {
                mvcValue = calibratePeak;
                Serial.printf("[MVC] Calibrated successfully! Peak: %.0f\n", mvcValue);
            } else {
                Serial.println("[MVC] Squeeze signal was too weak during calibration!");
            }
            isCalibrating = false;
            calibratePeak = 0;
        }
    }

    float percent = 0;
    if (mvcValue > 0) {
        percent = (envelope / mvcValue) * 100.0;
        if (percent > 150) percent = 150;
    }

    // Publish data to Broker every 50ms
    static unsigned long lastSend = 0;
    if (millis() - lastSend >= 50) {
        lastSend = millis();

        String json = "{";
        json += "\"raw\":" + String((int)envelope) + ",";
        if (mvcValue > 0) json += "\"percent\":" + String((int)percent) + ",";
        else json += "\"percent\":null,";
        json += "\"mvc\":" + String((int)mvcValue) + ",";
        json += "\"calibrating\":" + String(isCalibrating ? "true" : "false");
        json += "}";

        client.publish(topicData.c_str(), json.c_str());
    }

    // Live Serial Monitor Debug (every 500ms)
    static unsigned long lastDebug = 0;
    if (millis() - lastDebug >= 500) {
        lastDebug = millis();
        Serial.printf("ADC Live: %4d | Base: %4d | Env: %4.0f | MVC: %4.0f | %%MVC: %3.0f%% | MQTT: %s\n",
                      raw, baseline, envelope, mvcValue, percent, client.connected() ? "OK" : "DISCONNECTED");
    }
}
