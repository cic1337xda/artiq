# Nod Perkakasan EMG ArtiQ (`esp32/`)

## 📑 Pilihan Bahasa / Language Options
* 🇬🇧 **[English Documentation](README.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](README_MY.md)**

---

## 🔍 Gambaran Keseluruhan Perkakasan

**Nod Perkakasan EMG ArtiQ** ialah unit pemerolehan elektromiografi permukaan (sEMG) tanpa wayar yang dibina menggunakan mikropengawal **ESP32** dan **Sensor Otot MyoWare 2.0**. Unit ini mengkonfigurasi Wi-Fi secara dinamik melalui **WiFiManager** (membuka portal tawanan `ArtiQ-EMG-Setup` secara automatik jika rangkaian tersimpan tidak ditemui dalam `20 saat`), membaca isyarat sampul terterus (`ENV`) otot lengan bawah pada kadar `1000 Hz`, mengira nilai sampul terlicin serta `%MVC` (Maximum Voluntary Contraction) secara tempatan, dan menghantar telemetri ke pelayan klinikal ArtiQ melalui **MQTT** pada kadar `20 Hz` (selang `50 ms`).

---

## 📦 Senarai Bahan (BOM)

| Bil | Komponen | Kuantiti | Tujuan / Catatan |
|---|---|---|---|
| 1 | **Papan Pembangunan ESP32** | 1 | MCU Wi-Fi dwi-teras dengan ADC 12-bit (`GPIO 32`) |
| 2 | **Sensor Otot MyoWare 2.0** | 1 | Sensor sEMG 3.3V dengan output sampul `ENV` terbina |
| 3 | **Elektrod Biomedikal Ag/AgCl** | 3 | Elektrod permukaan pakai buang (Tengah otot, Hujung otot, Rujukan) |
| 4 | **Wayar Penyambung** | 3 | Sambungan `3V3`, `GND`, dan isyarat analog `ENV` |
| 5 | **Bekalan Kuasa USB / LiPo** | 1 | Bekalan 5V USB teratur (LDO 3.3V ESP32 membekalkan kuasa kepada MyoWare) |

---

## 🧱 Saluran Pemprosesan Isyarat Firmware

```text
MyoWare 2.0 (Pin ENV, 0–3.3V)
       │
       ▼
ESP32 GPIO 32 (ADC1_CH4, 12-bit, ADC_11db)
       │  Purata 8 sampel (readSmoothedADC)
       ▼
Penolakan Garis Dasar (raw - baseline >= 0)
       │
       ▼
Penapis Sampul Attack / Decay (attack=0.9, decay=0.99 @ 1000 Hz)
       │
       ├──► Kalibrasi MVC (Tangkapan puncak 3 saat melalui arahan "calibrate")
       └──► Penormalan %MVC ((envelope / mvcValue) * 100, had 150%)
       │
       ▼
Penerbitan MQTT @ 20 Hz -> artiq/emg/data/{MAC}
```

---

## 📚 Panduan Subsistem Perkakasan

* ⚡ **[Panduan Pinout & Pendawaian](PINOUT_AND_WIRING_MY.md)** — Pemetaan GPIO, rujukan skematik CAD, penempatan elektrod, dan keselamatan elektrik.
* 📡 **[Spesifikasi MQTT](MQTT_SPECIFICATION_MY.md)** — Topik, format payload JSON, Last Will and Testament (LWT), dan arahan kawalan jauh.
* 💾 **[Panduan Flashing & Tetapan](FLASHING_AND_SETUP_MY.md)** — Persediaan Arduino IDE / `arduino-cli`, pustaka diperlukan, dan pemadanan MAC.
