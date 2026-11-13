# MQTT Protocol & Telemetry Specification (`MQTT_SPECIFICATION.md`)

## 📑 Language Options
* 🇬🇧 **[English Documentation (Current)](MQTT_SPECIFICATION.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](MQTT_SPECIFICATION_MY.md)**

---

## 📡 Broker Connection Parameters

| Parameter | Value / Placeholder | Notes |
|---|---|---|
| **Protocol** | MQTT v3.1.1 over TCP | Handled by `PubSubClient` |
| **Broker Port** | `1883` (or external mapped stream port) | Configured via `mqtt_port` in `artiq_emg_node.ino` |
| **Client ID Format** | `ArtiQ-Node-{MAC}` | Unique MAC address with colons stripped (e.g., `ArtiQ-Node-A1B2C3D4E5F6`) |
| **Last Will & Testament (LWT)** | Topic: `artiq/emg/status/{MAC}` | QoS `1`, Retain `true`, Payload `"offline"` |

---

## 📬 Topic Architecture

All topics are scoped dynamically per hardware MAC address (uppercase, no colons):

| Direction | Topic | QoS / Retain | Payload Format |
|---|---|---|---|
| **ESP32 → Broker** | `artiq/emg/status/{MAC}` | QoS `1`, Retain `true` | `"online"` on connect; `"offline"` via LWT |
| **ESP32 → Broker** | `artiq/emg/data/{MAC}` | QoS `0`, Retain `false` | JSON telemetry published every `50 ms` (`20 Hz`) |
| **Backend → ESP32** | `artiq/emg/command/{MAC}` | QoS `1`, Retain `false` | Plaintext command string |

---

## 📦 Telemetry Payload Schema (`artiq/emg/data/{MAC}`)

```json
{
  "raw": 842,
  "percent": 68,
  "mvc": 1240,
  "calibrating": false
}
```

| Field | Type | Description |
|---|---|---|
| `raw` | `integer` | Current smoothed envelope amplitude above baseline (`0 – 4095`) |
| `percent` | `integer \| null` | Normalized `%MVC` (`0 – 150`), or `null` when `mvc == 0` (uncalibrated) |
| `mvc` | `integer` | Stored Maximum Voluntary Contraction reference peak (`0` if unset) |
| `calibrating` | `boolean` | `true` during the 3-second MVC peak capture window |

---

## 🎛️ Supported Remote Commands (`artiq/emg/command/{MAC}`)

| Command | Action on ESP32 Firmware |
|---|---|
| `calibrate` | Starts a non-blocking 3-second (`3000 ms`) MVC peak capture window. Updates `mvcValue` if `calibratePeak > 50`. |
| `reset` | Resets `mvcValue = 0` so the dashboard reverts to raw uncalibrated preview mode. |
| `relax` / `baseline` | Samples 100 smoothed ADC readings (~500 ms) while forearm is relaxed and updates `baseline`. |

---

## ⏱️ Non-Blocking Timing Loop

The firmware uses `micros()` and `millis()` non-blocking timers in `loop()` so `client.loop()` processes incoming MQTT commands immediately without interrupting high-frequency ADC sampling:
* **ADC Sampling & Envelope Filter:** Every `1000 µs` (`1000 Hz`)
* **MQTT Telemetry Publish:** Every `50 ms` (`20 Hz`)
* **Serial Monitor Diagnostics:** Every `500 ms` (`2 Hz`)
