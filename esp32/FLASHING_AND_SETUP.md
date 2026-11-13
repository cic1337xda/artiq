# Flashing & Device Setup Guide (`FLASHING_AND_SETUP.md`)

## 📑 Language Options
* 🇬🇧 **[English Documentation (Current)](FLASHING_AND_SETUP.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](FLASHING_AND_SETUP_MY.md)**

---

## 🛠️ Required Toolchain & Libraries

1. **Board Core:** `esp32` by Espressif Systems (tested on `3.3.x`, FQBN: `esp32:esp32:esp32`).
2. **Required Libraries:**
   * `PubSubClient` (v2.8) by Nick O'Leary
   * `WiFiManager` (v2.0.17+) by tzapu

Install via Arduino Library Manager or `arduino-cli`:
```bash
arduino-cli lib install "PubSubClient" "WiFiManager"
```

---

## ⚙️ Firmware Configuration

Wi-Fi credentials are **never hardcoded** — they are provisioned wirelessly via the **WiFiManager Captive Portal**. Open [`artiq_emg_node/artiq_emg_node.ino`](artiq_emg_node/artiq_emg_node.ino) and set only your MQTT broker details:

```cpp
const char* mqtt_server = "YOUR_MQTT_BROKER_IP";
const int mqtt_port = 1883;
const char* ap_name = "ArtiQ-EMG-Setup";
```

---

## 📶 WiFiManager Captive Portal Provisioning

1. On boot, the ESP32 attempts to connect to any previously saved Wi-Fi network with a **`20-second` timeout** (`wm.setConnectTimeout(20)`).
2. If no saved Wi-Fi network is found or reachable within `20 seconds`, the ESP32 automatically launches a captive portal Access Point named **`ArtiQ-EMG-Setup`**.
3. Connect your phone or laptop to **`ArtiQ-EMG-Setup`**, open `192.168.4.1` (if the portal does not pop up automatically), select your 2.4 GHz Wi-Fi SSID, enter the password, and click **Save**.
4. Once connected, the ESP32 saves the credentials to flash, runs the 2-second relaxed baseline calibration, and connects to MQTT. (If the portal remains idle for `180 seconds`, the node reboots and retries.)

---

## 🚀 Compiling & Flashing

### Option A: Arduino IDE
1. Select **Tools → Board → ESP32 Arduino → ESP32 Dev Module**.
2. Set **Upload Speed** to `115200` (or `921600`) and select your USB serial port.
3. Click **Upload**, then open **Serial Monitor** at `115200 baud`.

### Option B: `arduino-cli`
```bash
arduino-cli compile --fqbn esp32:esp32:esp32 esp32/artiq_emg_node/artiq_emg_node.ino
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 esp32/artiq_emg_node/artiq_emg_node.ino
```

---

## 🔗 Calibration & Dashboard Pairing Workflow

1. **Wi-Fi Provisioning:** Power on the ESP32 and wait for saved Wi-Fi connection (or configure via **`ArtiQ-EMG-Setup`** captive portal if unavailable within `20 seconds`).
2. **Boot Baseline Calibration (Relax 0%):** Keep your forearm completely relaxed during the `2-second` calibration window immediately after Wi-Fi connects. Serial Monitor will display `Registered baseline (Relax): <value>`.
3. **Obtain Node MAC Address:** Serial Monitor prints `WiFi Connected! IP: <ip> | Node MAC: A1B2C3D4E5F6`.
4. **Link Node in ArtiQ Dashboard:** Open the ArtiQ web dashboard, sign in, open **Settings (gear icon)**, enter the MAC address under **EMG Hardware Node**, and click **LINK NODE**.
5. **Calibrate MVC (Max 100%):** Click **Calibrate** on the Muscle Activation card and squeeze at maximum grip effort for `3 seconds` to set your clinical `%MVC` reference.
