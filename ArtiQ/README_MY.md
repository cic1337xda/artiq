# Pelayan, Awan & Tindanan Web ArtiQ (`ArtiQ/`)

## 📑 Pilihan Bahasa / Language Options
* 🇬🇧 **[English Documentation](README.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](README_MY.md)**

---

## 🧩 Ringkasan Tindanan Teknologi

| Lapisan | Teknologi | Peranan |
|---|---|---|
| **API Backend** | FastAPI + Uvicorn (Python 3.10) | Laluan REST modular, pengesahan JWT, penyerapan telemetri MQTT |
| **Pangkalan Data** | PostgreSQL 15 Alpine + SQLAlchemy | Akaun pengguna, rekod OTP, dan log sesi senaman pesakit |
| **Broker Mesej** | Eclipse Mosquitto 2.0 | Jambatan pub/sub MQTT masa nyata untuk nod ESP32 MyoWare 2.0 |
| **Penghantaran E-mel** | Resend API (`mail.flowkraft.xyz`) | Penghantaran OTP 6-digit untuk pendaftaran dan tetapan semula kata laluan |
| **Frontend & Edge AI** | HTML5 + Tailwind CSS + Vanilla JS + MediaPipe Hands | Papan pemuka AR Liquid Glass & pengiraan ulangan genggaman |

---

## 🚀 Pelancaran Pantas

```bash
cd ArtiQ
cp .env.example .env
# Lengkapkan POSTGRES_*, DATABASE_URL, RESEND_API_KEY, dan SECRET_KEY dalam .env
docker network inspect pwn20wnd-network >/dev/null 2>&1 || docker network create pwn20wnd-network
docker compose up -d --build
```

---

## 📚 Panduan Subsistem Pelayan

* 🌐 **[Dokumentasi API](API_DOCUMENTATION_MY.md)** — Laluan REST, skema permintaan, format respons piawai, dan peraturan pengesahan.
* 🐳 **[Docker & Perkhidmatan](DOCKER_AND_SERVICES_MY.md)** — Topologi kontena, pemetaan port, putaran log, dan penyelarasan masa `Asia/Kuala_Lumpur`.
* 🔒 **[Keselamatan & Seni Bina](SECURITY_AND_ARCHITECTURE_MY.md)** — Struktur modular backend, polisi Bcrypt/JWT/OTP, CSRF/header keselamatan, dan logik Edge AI CV.
