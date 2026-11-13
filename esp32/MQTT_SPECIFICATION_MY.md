# Spesifikasi Protokol MQTT & Telemetri (`MQTT_SPECIFICATION_MY.md`)

## 📑 Pilihan Bahasa
* 🇬🇧 **[English Documentation](MQTT_SPECIFICATION.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](MQTT_SPECIFICATION_MY.md)**

---

## 📡 Parameter Sambungan Broker

| Parameter | Nilai / Pemegang Tempat | Catatan |
|---|---|---|
| **Protokol** | MQTT v3.1.1 melalui TCP | Dikendalikan oleh `PubSubClient` |
| **Port Broker** | `1883` (atau port strim luaran) | Ditetapkan melalui `mqtt_port` dalam `artiq_emg_node.ino` |
| **Format Client ID** | `ArtiQ-Node-{MAC}` | Alamat MAC unik tanpa titik bertindih (cth. `ArtiQ-Node-A1B2C3D4E5F6`) |
| **Last Will & Testament (LWT)** | Topik: `artiq/emg/status/{MAC}` | QoS `1`, Retain `true`, Payload `"offline"` |

---

## 📬 Seni Bina Topik

Semua topik diasingkan secara dinamik mengikut alamat MAC perkakasan (huruf besar, tanpa `:`):

| Arah | Topik | QoS / Retain | Format Payload |
|---|---|---|---|
| **ESP32 → Broker** | `artiq/emg/status/{MAC}` | QoS `1`, Retain `true` | `"online"` semasa sambung; `"offline"` melalui LWT |
| **ESP32 → Broker** | `artiq/emg/data/{MAC}` | QoS `0`, Retain `false` | JSON telemetri diterbitkan setiap `50 ms` (`20 Hz`) |
| **Backend → ESP32** | `artiq/emg/command/{MAC}` | QoS `1`, Retain `false` | Rentetan arahan teks biasa |

---

## 📦 Skema Payload Telemetri (`artiq/emg/data/{MAC}`)

```json
{
  "raw": 842,
  "percent": 68,
  "mvc": 1240,
  "calibrating": false
}
```

| Medan | Jenis | Penerangan |
|---|---|---|
| `raw` | `integer` | Amplitud sampul terlicin semasa melebihi garis dasar (`0 – 4095`) |
| `percent` | `integer \| null` | Nilai `%MVC` ternormal (`0 – 150`), atau `null` jika `mvc == 0` |
| `mvc` | `integer` | Nilai puncak rujukan Maximum Voluntary Contraction (`0` jika belum diset) |
| `calibrating` | `boolean` | `true` sepanjang tempoh tangkapan puncak MVC 3 saat |

---

## 🎛️ Arahan Kawalan Jauh Disokong (`artiq/emg/command/{MAC}`)

| Arahan | Tindakan pada Firmware ESP32 |
|---|---|
| `calibrate` | Memulakan tetingkap tangkapan puncak MVC 3 saat (`3000 ms`) tanpa menyekat gelung. Mengemas kini `mvcValue` jika `calibratePeak > 50`. |
| `reset` | Menetapkan semula `mvcValue = 0` supaya papan pemuka kembali ke mod pratonton mentah. |
| `relax` / `baseline` | Mengambil 100 sampel ADC terlicin (~500 ms) semasa otot rehat dan mengemas kini `baseline`. |

---

## ⏱️ Gelung Pemasaan Tanpa Sekatan (*Non-Blocking*)

Firmware menggunakan pemasa `micros()` dan `millis()` dalam `loop()` supaya `client.loop()` memproses arahan MQTT masuk dengan serta-merta tanpa mengganggu pensampelan ADC frekuensi tinggi:
* **Pensampelan ADC & Penapis Sampul:** Setiap `1000 µs` (`1000 Hz`)
* **Penerbitan Telemetri MQTT:** Setiap `50 ms` (`20 Hz`)
* **Diagnostik Serial Monitor:** Setiap `500 ms` (`2 Hz`)
