# Panduan Flashing & Tetapan Peranti (`FLASHING_AND_SETUP_MY.md`)

## 📑 Pilihan Bahasa
* 🇬🇧 **[English Documentation](FLASHING_AND_SETUP.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](FLASHING_AND_SETUP_MY.md)**

---

## 🛠️ Perisian & Pustaka Diperlukan

1. **Teras Papan (*Board Core*):** `esp32` oleh Espressif Systems (diuji pada versi `3.3.x`, FQBN: `esp32:esp32:esp32`).
2. **Pustaka Diperlukan:**
   * `PubSubClient` (v2.8) oleh Nick O'Leary
   * `WiFiManager` (v2.0.17+) oleh tzapu

Pasang melalui Arduino Library Manager atau `arduino-cli`:
```bash
arduino-cli lib install "PubSubClient" "WiFiManager"
```

---

## ⚙️ Konfigurasi Firmware

Maklumat Wi-Fi **tidak lagi di-hardcode** — ia dikonfigurasi secara tanpa wayar melalui **Portal Tawanan WiFiManager**. Buka [`artiq_emg_node/artiq_emg_node.ino`](artiq_emg_node/artiq_emg_node.ino) dan tetapkan hanya maklumat broker MQTT anda:

```cpp
const char* mqtt_server = "YOUR_MQTT_BROKER_IP";
const int mqtt_port = 1883;
const char* ap_name = "ArtiQ-EMG-Setup";
```

---

## 📶 Penyediaan Portal Tawanan WiFiManager

1. Semasa boot, ESP32 cuba menyambung ke rangkaian Wi-Fi yang telah disimpan dengan **had masa `20 saat`** (`wm.setConnectTimeout(20)`).
2. Jika rangkaian tersimpan tidak ditemui atau gagal disambung dalam tempoh `20 saat`, ESP32 akan membuka Access Point portal tawanan bernama **`ArtiQ-EMG-Setup`** secara automatik.
3. Sambungkan telefon atau komputer riba ke **`ArtiQ-EMG-Setup`**, buka `192.168.4.1` (jika tidak dibuka automatik), pilih Wi-Fi 2.4 GHz anda, masukkan kata laluan, dan tekan **Save**.
4. Selepas berjaya, ESP32 menyimpan kelayakan ke memori flash, menjalankan kalibrasi garis dasar rehat selama 2 saat, dan menyambung ke MQTT. (Jika portal terbiar `180 saat`, nod akan dimulakan semula.)

---

## 🚀 Kompilasi & Muat Naik (*Flashing*)

### Pilihan A: Arduino IDE
1. Pilih **Tools → Board → ESP32 Arduino → ESP32 Dev Module**.
2. Tetapkan **Upload Speed** kepada `115200` (atau `921600`) dan pilih port bersiri USB yang betul.
3. Klik **Upload**, kemudian buka **Serial Monitor** pada `115200 baud`.

### Pilihan B: `arduino-cli`
```bash
arduino-cli compile --fqbn esp32:esp32:esp32 esp32/artiq_emg_node/artiq_emg_node.ino
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 esp32/artiq_emg_node/artiq_emg_node.ino
```

---

## 🔗 Aliran Kerja Kalibrasi & Pemadanan Papan Pemuka

1. **Penyediaan Wi-Fi:** Hidupkan ESP32 dan tunggu sambungan Wi-Fi tersimpan (atau tetapkan melalui portal **`ArtiQ-EMG-Setup`** jika tiada rangkaian ditemui dalam `20 saat`).
2. **Kalibrasi Garis Dasar Semasa Boot (Rehat 0%):** Pastikan otot lengan bawah rehat sepenuhnya sepanjang tempoh `2 saat` sejurus selepas Wi-Fi bersambung. Serial Monitor akan memaparkan `Registered baseline (Relax): <value>`.
3. **Dapatkan Alamat MAC Nod:** Serial Monitor memaparkan `WiFi Connected! IP: <ip> | Node MAC: A1B2C3D4E5F6`.
4. **Pautkan Nod pada Papan Pemuka ArtiQ:** Buka laman web ArtiQ, log masuk, buka **Settings (ikon gear)**, masukkan alamat MAC di ruangan **EMG Hardware Node**, dan klik **LINK NODE**.
5. **Kalibrasi MVC (Maksimum 100%):** Klik **Calibrate** pada kad Muscle Activation dan genggam sekuat mungkin selama `3 saat` untuk menetapkan rujukan `%MVC` klinikal anda.
