# Pinout & Hardware Wiring Guide (`PINOUT_AND_WIRING.md`)

## 📑 Language Options
* 🇬🇧 **[English Documentation (Current)](PINOUT_AND_WIRING.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](PINOUT_AND_WIRING_MY.md)**

---

## 📐 Schematic Reference

The circuit schematic for the **ArtiQ EMG Node** (Rev 1.0) is available in the repository root:
* 🖼️ **Preview:** [`../Schematic_artiq_2026-11-12.png`](../Schematic_artiq_2026-11-12.png)
* 📄 **CAD PDF:** [`../Schematic_artiq_2026-11-12.pdf`](../Schematic_artiq_2026-11-12.pdf)

---

## 🔌 ESP32 to MyoWare 2.0 Pinout Table

| ESP32 Pin | ADC Channel | MyoWare 2.0 Pin | Voltage / Logic | Description |
|---|---|---|---|---|
| **3V3** | — | **VIN** (Pin 1) | `3.3V DC` | Regulated 3.3V supply from ESP32 onboard LDO |
| **GND** | — | **GND** (Pin 2) | `0V` | Common ground reference |
| **GPIO 32 (D32)** | `ADC1_CH4` | **ENV** (Pin 3) | `0.0V – 3.3V` Analog | Hardware-rectified and integrated EMG envelope signal |

> **Why `GPIO 32` (`ADC1`)?**
> ESP32 `ADC2` channels (`GPIO 0, 2, 4, 12–15, 25–27`) cannot be read reliably when the Wi-Fi radio is active. `GPIO 32` belongs to `ADC1`, ensuring uninterrupted 12-bit (`0–4095`) analog sampling alongside continuous MQTT over Wi-Fi.

---

## 🩹 Biomedical Electrode Placement (Forearm Flexors)

1. **Mid-Muscle Snap (On-Board):** Center over the flexor digitorum superficialis / forearm muscle belly, aligned parallel to the muscle fibers.
2. **End-Muscle Snap (On-Board):** Located along the same muscle group toward the wrist/elbow boundary.
3. **Reference Snap (Cable / Off-Board):** Place over a bony prominence with minimal muscle mass (e.g., the ulnar head near the wrist or elbow olecranon).

---

## ⚠️ Electrical Safety & Hardware Precautions

* **Power Strictly at 3.3V:** Never power MyoWare 2.0 from `5V VIN` when connected directly to an ESP32 GPIO, as ESP32 ADC pins are not 5V-tolerant and `ENV` can exceed `3.3V`.
* **Skin Isolation:** Power the ESP32 from an isolated USB power bank or medical-grade isolated 5V adapter when electrodes are attached to a human subject. Never connect directly to mains-grounded equipment without isolation.
* **Skin Preparation:** Clean skin with an alcohol wipe and allow it to dry before snapping Ag/AgCl electrodes to minimize contact impedance and baseline noise.
