# Rujukan RESTful API (`API_DOCUMENTATION_MY.md`)

## 📑 Pilihan Bahasa
* 🇬🇧 **[English Documentation](API_DOCUMENTATION.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](API_DOCUMENTATION_MY.md)**

---

## 📦 Format Respons JSON Piawai

Semua respons API (kecuali `GET /api/v1/health`) menggunakan struktur piawai berikut:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {},
  "error": null
}
```

Setiap respons turut menyertakan header `X-Request-ID` untuk tujuan pengesanan log.

---

## 🩺 Laluan Semakan Kesihatan (*Healthcheck*)

| Kaedah | Laluan | Pengesahan | Penerangan |
|---|---|---|---|
| `GET` | `/api/v1/health` | Awam | Menguji sambungan PostgreSQL (`SELECT 1`) dan memulangkan cap masa GMT+8. |

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-11-12T14:20:00+08:00"
}
```

---

## 🔐 Laluan Pengesahan & OTP

| Kaedah | Laluan | Had Kadar | Pengesahan | Penerangan |
|---|---|---|---|---|
| `POST` | `/api/send-otp` | `3/minit` | Awam | Menghantar OTP pendaftaran 6-digit kriptografi (luput 10 minit). |
| `POST` | `/api/register` | `5/minit` | Awam | Mengesahkan OTP (maks 5 cubaan), semak kekuatan kata laluan, daftar admin. |
| `POST` | `/api/login` | `5/minit` | Awam | Mengesahkan akaun, kunci 15 minit selepas 5 kegagalan, set kuki JWT `HttpOnly`. |
| `POST` | `/api/forgot-password` | `3/minit` | Awam | Menghantar OTP tetapan semula kata laluan melalui Resend. |
| `POST` | `/api/reset-password` | `5/minit` | Awam | Mengesahkan OTP tetapan semula dan mengemas kini kata laluan baharu. |
| `POST` | `/api/logout` | — | Awam | Memadam kuki `access_token`. |
| `GET` | `/api/user` | — | Kuki | Memulangkan nama pengguna dan e-mel pentadbir yang sedang log masuk. |

*(Laluan berversi di bawah `/api/v1/auth/*` turut disediakan.)*

---

## 🏋️ Laluan Sesi Senaman

Semua laluan sesi memerlukan kuki `access_token` dan menguatkuasakan semakan pemilikan (`user_id == current_user.id`):

| Kaedah | Laluan | Badan Permintaan | Penerangan |
|---|---|---|---|
| `POST` | `/api/session/start` | `{"name": "Patient Name", "age": 45}` | Memulakan sesi ulangan klinikal baharu dan memulangkan `session_id`. |
| `POST` | `/api/session/stop` | `{"session_id": 1, "reps": 12}` | Menyimpan `end_time` (GMT+8) dan `total_reps` bagi sesi berkenaan. |
| `GET` | `/api/history` | — | Memulangkan 15 rekod sesi terkini milik pentadbir yang sedang aktif. |

---

## ⚡ Laluan Telemetri & Kawalan EMG

Semua laluan EMG memerlukan kuki `access_token`:

| Kaedah | Laluan | Badan / Parameter | Penerangan |
|---|---|---|---|
| `GET` | `/api/emg/telemetry` | — | Memulangkan status langsung nod (`mac`, `is_online`, `raw`, `percent`, `mvc`, `calibrating`). |
| `POST` | `/api/emg/set-mac` | `{"mac": "A1B2C3D4E5F6"}` | Mengunci penerimaan telemetri dan arahan kepada alamat MAC ESP32 tertentu. |
| `POST` | `/api/emg/command/{cmd}` | `cmd`: `calibrate \| reset \| relax \| baseline` | Menerbitkan arahan MQTT (`QoS 1`) ke topik `artiq/emg/command/{mac}`. |
