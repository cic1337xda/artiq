# Panduan Pinout & Pendawaian Perkakasan (`PINOUT_AND_WIRING_MY.md`)

## 📑 Pilihan Bahasa
* 🇬🇧 **[English Documentation](PINOUT_AND_WIRING.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](PINOUT_AND_WIRING_MY.md)**

---

## 📐 Rujukan Skematik

Skematik litar untuk **Nod EMG ArtiQ** (Rev 1.0) tersedia di direktori utama repositori:
* 🖼️ **Pratonton:** [`../Schematic_artiq_2026-11-12.png`](../Schematic_artiq_2026-11-12.png)
* 📄 **Fail PDF CAD:** [`../Schematic_artiq_2026-11-12.pdf`](../Schematic_artiq_2026-11-12.pdf)

---

## 🔌 Jadual Pinout ESP32 ke MyoWare 2.0

| Pin ESP32 | Saluran ADC | Pin MyoWare 2.0 | Voltan / Logik | Penerangan |
|---|---|---|---|---|
| **3V3** | — | **VIN** (Pin 1) | `3.3V DC` | Bekalan kuasa 3.3V teratur daripada LDO papan ESP32 |
| **GND** | — | **GND** (Pin 2) | `0V` | Rujukan bumi sepunya (*common ground*) |
| **GPIO 32 (D32)** | `ADC1_CH4` | **ENV** (Pin 3) | Analog `0.0V – 3.3V` | Isyarat sampul EMG terterus & terintegrasi |

> **Mengapa `GPIO 32` (`ADC1`)?**
> Saluran `ADC2` ESP32 (`GPIO 0, 2, 4, 12–15, 25–27`) tidak boleh dibaca secara stabil semasa modul Wi-Fi aktif. `GPIO 32` berada pada `ADC1`, membolehkan bacaan analog 12-bit (`0–4095`) yang stabil serentak dengan penghantaran MQTT melalui Wi-Fi.

---

## 🩹 Penempatan Elektrod Biomedikal (Otot Fleksor Lengan Bawah)

1. **Elektrod Tengah Otot (*Mid-Muscle*):** Letakkan di bahagian tengah isi otot fleksor lengan bawah, selari dengan arah gentian otot.
2. **Elektrod Hujung Otot (*End-Muscle*):** Terletak selari di atas kumpulan otot yang sama menghala ke pergelangan tangan atau siku.
3. **Elektrod Rujukan (*Reference*):** Tampalkan pada bahagian tulang yang kurang tisu otot (contohnya tulang ulna di pergelangan tangan atau siku).

---

## ⚠️ Keselamatan Elektrik & Langkah Berjaga-jaga

* **Gunakan Kuasa 3.3V Sahaja:** Jangan sekali-kali menyambungkan MyoWare 2.0 ke `5V VIN` apabila disambung terus ke GPIO ESP32 kerana pin ADC ESP32 tidak menyokong input melebihi `3.3V`.
* **Pengasingan Kuasa (*Power Isolation*):** Gunakan *power bank* USB terasing semasa elektrod dilekatkan pada kulit manusia bagi mengelakkan gangguan elektrik atau risiko renjatan.
* **Penyediaan Kulit:** Bersihkan kulit dengan pad alkohol dan biarkan kering sebelum menampal elektrod Ag/AgCl bagi mengurangkan hingar garis dasar.
