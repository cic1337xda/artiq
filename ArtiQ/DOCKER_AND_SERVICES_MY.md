# Topologi Docker & Perkhidmatan Kontena (`DOCKER_AND_SERVICES_MY.md`)

## 📑 Pilihan Bahasa
* 🇬🇧 **[English Documentation](DOCKER_AND_SERVICES.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](DOCKER_AND_SERVICES_MY.md)**

---

## 🐳 Seni Bina Pelbagai Kontena

| Nama Servis | Nama Kontena | Imej / Binaan | Pemetaan Port | Peranan |
|---|---|---|---|---|
| `db` | `artiq_db` | `postgres:15-alpine` | `${DB_PORT}:5432` | Penyimpanan pangkalan data (`pgdata` volume) |
| `ar_engine` | `artiq_backend` | `./backend/Dockerfile` | `${APP_PORT}:8000` | Backend modular FastAPI + fail statik UI Liquid Glass |
| `mosquitto` | `artiq_mqtt` | `eclipse-mosquitto:latest` | `1891:1883` | Broker MQTT untuk telemetri ESP32 MyoWare 2.0 |

---

## ⚙️ Piawaian Operasi

* **Pengasingan Dwi-Rangkaian:** Kontena berkongsi rangkaian dalaman `artiq_internal` untuk resolusi servis dalaman (`db`, `artiq_mqtt`) di samping rangkaian luaran `pwn20wnd-network` bagi integrasi proksi berbalik (Nginx Proxy Manager & Cloudflare).
* **Nama Hos Broker Khusus:** `ar_engine` menyambung secara khusus ke `MQTT_BROKER=artiq_mqtt` (`MQTT_PORT=1883`) bagi mengelakkan perlanggaran DNS pada rangkaian Docker berkongsi.
* **Pengguna Bukan-Root:** `backend/Dockerfile` menjalankan proses FastAPI menggunakan akaun tanpa keistimewaan `appuser` (UID `1000`).
* **Penyelarasan Zon Masa Malaysia (`Asia/Kuala_Lumpur` / GMT+8):**
  * `TZ=Asia/Kuala_Lumpur` ditetapkan pada `db`, `ar_engine`, dan `mosquitto`.
  * `PGTZ=Asia/Kuala_Lumpur` ditetapkan pada PostgreSQL.
  * Cap masa Python menggunakan `ZoneInfo("Asia/Kuala_Lumpur")` bersama `tzdata`.
* **Putaran Log (*Log Rotation*):** Semua servis mengehadkan log `json-file` kepada `max-size: "10m"` dan `max-file: "3"`.

---

## 🔧 Matriks Pemboleh Ubah Persekitaran (`.env`)

| Pemboleh Ubah | Penerangan |
|---|---|
| `APP_PORT` | Port hos dipetakan ke FastAPI (`8000`) |
| `DB_PORT` | Port hos dipetakan ke PostgreSQL (`5432`) |
| `POSTGRES_USER` | Nama pengguna pangkalan data PostgreSQL |
| `POSTGRES_PASSWORD` | Kata laluan pengguna PostgreSQL |
| `POSTGRES_DB` | Nama pangkalan data (`physiotherapy`) |
| `DATABASE_URL` | Rentetan sambungan penuh SQLAlchemy PostgreSQL |
| `RESEND_API_KEY` | Kunci API e-mel transaksi Resend (pelayan sahaja) |
| `SECRET_KEY` | Kunci rahsia kriptografi untuk tandatangan token JWT HS256 |

---

## 💻 Arahan Asas Docker

```bash
# Pastikan rangkaian bersama wujud
docker network inspect pwn20wnd-network >/dev/null 2>&1 || docker network create pwn20wnd-network

# Bina dan jalankan semua kontena di latar belakang
docker compose up -d --build

# Semak status kontena dan log
docker compose ps
docker compose logs -f ar_engine
```
