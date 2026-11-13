# ArtiQ Server, Cloud & Web Stack (`ArtiQ/`)

## 📑 Language Options / Pilihan Bahasa
* 🇬🇧 **[English Documentation (Current)](README.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](README_MY.md)**

---

## 🧩 Technology Stack Summary

| Layer | Technology | Role |
|---|---|---|
| **Backend API** | FastAPI + Uvicorn (Python 3.10) | Modular REST endpoints, JWT authentication, MQTT telemetry ingestion |
| **Database** | PostgreSQL 15 Alpine + SQLAlchemy | Persistent user accounts, OTP records, and patient exercise sessions |
| **Message Broker** | Eclipse Mosquitto 2.0 | Real-time MQTT pub/sub bridge for ESP32 MyoWare 2.0 nodes |
| **Email Dispatch** | Resend API (`mail.flowkraft.xyz`) | 6-digit registration and password-reset OTP delivery with inline ArtiQ branding |
| **Frontend & Edge AI** | HTML5 + Tailwind CSS + Vanilla JS + MediaPipe Hands | Liquid Glass AR physiotherapy dashboard & client-side grip tracking |

---

## 🚀 Quick Deployment

```bash
cd ArtiQ
cp .env.example .env
# Populate POSTGRES_*, DATABASE_URL, RESEND_API_KEY, and SECRET_KEY in .env
docker network inspect pwn20wnd-network >/dev/null 2>&1 || docker network create pwn20wnd-network
docker compose up -d --build
```

---

## 📚 Subsystem Server Guides

* 🌐 **[API Documentation](API_DOCUMENTATION.md)** — REST routes, request schemas, response envelopes, and authentication rules.
* 🐳 **[Docker & Services](DOCKER_AND_SERVICES.md)** — Container topology, ports, log rotation, and `Asia/Kuala_Lumpur` timezone synchronization.
* 🔒 **[Security & Architecture](SECURITY_AND_ARCHITECTURE.md)** — Modular backend structure, Bcrypt/JWT/OTP policies, CSRF/security headers, and Edge AI CV logic.
