# ArtiQ EMG Hardware Node (`esp32/`)

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](README.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](README_MY.md)**

---

## 🔍 Hardware Overview

The **ArtiQ EMG Hardware Node** is a wireless surface electromyography (sEMG) acquisition unit built on an **ESP32** microcontroller and a **MyoWare 2.0 Muscle Sensor**. It provisions Wi-Fi dynamically via **WiFiManager** (auto-opening the `ArtiQ-EMG-Setup` captive portal if no saved network connects within `20 seconds`), captures forearm muscle activation via the MyoWare 2.0 rectified envelope (`ENV`) output at `1000 Hz`, computes smoothed envelope and `%MVC` (Maximum Voluntary Contraction) values locally, and streams telemetry to the ArtiQ clinical backend over **MQTT** at `20 Hz` (`50 ms` intervals).

---

## 📦 Bill of Materials (BOM)

| Item | Component | Quantity | Purpose / Notes |
|---|---|---|---|
| 1 | **ESP32 Development Board** | 1 | Dual-core Wi-Fi MCU with 12-bit SAR ADC (`GPIO 32`) |
| 2 | **MyoWare 2.0 Muscle Sensor** | 1 | 3.3V surface EMG sensor with onboard `ENV` envelope output |
| 3 | **Ag/AgCl Biomedical Electrodes** | 3 | Snap-on disposable surface electrodes (Mid-muscle, End-muscle, Reference) |
| 4 | **Jumper Wires / Harness** | 3 | `3V3`, `GND`, and analog `ENV` signal interconnection |
| 5 | **USB Power / LiPo Supply** | 1 | Regulated 5V USB (ESP32 onboard 3.3V LDO powers MyoWare) |

---

## 🧱 Firmware Signal Processing Pipeline

```text
MyoWare 2.0 (ENV Pin, 0–3.3V)
       │
       ▼
ESP32 GPIO 32 (ADC1_CH4, 12-bit, ADC_11db)
       │  8-sample oversampling average (readSmoothedADC)
       ▼
Baseline Subtraction (raw - baseline >= 0)
       │
       ▼
Attack / Decay Envelope Follower (attack=0.9, decay=0.99 @ 1000 Hz)
       │
       ├──► MVC Calibration (3-second peak capture on "calibrate" command)
       └──► %MVC Normalization ((envelope / mvcValue) * 100, capped at 150%)
       │
       ▼
MQTT Publish @ 20 Hz -> artiq/emg/data/{MAC}
```

---

## 📚 Subsystem Hardware Guides

* ⚡ **[Pinout & Wiring Guide](PINOUT_AND_WIRING.md)** — GPIO mapping, CAD schematic reference, electrode placement, and electrical safety.
* 📡 **[MQTT Specification](MQTT_SPECIFICATION.md)** — Topics, JSON payload formats, Last Will and Testament (LWT), and remote commands.
* 💾 **[Flashing & Setup Guide](FLASHING_AND_SETUP.md)** — Arduino IDE / `arduino-cli` toolchain, required libraries, and MAC pairing workflow.
