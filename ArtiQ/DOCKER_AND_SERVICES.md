# Docker Topology & Container Services (`DOCKER_AND_SERVICES.md`)

## 📑 Language Options
* 🇬🇧 **[English Documentation (Current)](DOCKER_AND_SERVICES.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](DOCKER_AND_SERVICES_MY.md)**

---

## 🐳 Multi-Container Architecture

| Service Name | Container Name | Image / Build | Port Mapping | Role |
|---|---|---|---|---|
| `db` | `artiq_db` | `postgres:15-alpine` | `${DB_PORT}:5432` | Relational persistence (`pgdata` volume) |
| `ar_engine` | `artiq_backend` | `./backend/Dockerfile` | `${APP_PORT}:8000` | Modular FastAPI backend + static Liquid Glass UI |
| `mosquitto` | `artiq_mqtt` | `eclipse-mosquitto:latest` | `1891:1883` | MQTT broker for ESP32 MyoWare 2.0 telemetry |

---

## ⚙️ Operational Standards

* **Dual Network Isolation:** Containers share an isolated `artiq_internal` bridge network for internal service resolution (`db`, `artiq_mqtt`) alongside the external `pwn20wnd-network` for upstream reverse proxy integration (Nginx Proxy Manager & Cloudflare).
* **Dedicated Broker Hostname:** `ar_engine` connects explicitly to `MQTT_BROKER=artiq_mqtt` (`MQTT_PORT=1883`) to prevent DNS name collisions on shared Docker networks.
* **Non-Root Execution:** `backend/Dockerfile` creates and runs under the dedicated unprivileged user `appuser` (UID `1000`).
* **Malaysia Timezone Synchronization (`Asia/Kuala_Lumpur` / GMT+8):**
  * `TZ=Asia/Kuala_Lumpur` is enforced across `db`, `ar_engine`, and `mosquitto`.
  * `PGTZ=Asia/Kuala_Lumpur` is enforced on PostgreSQL.
  * Python backend timestamps use `ZoneInfo("Asia/Kuala_Lumpur")` with `tzdata`.
* **Log Rotation:** Every service uses `json-file` driver capped at `max-size: "10m"` and `max-file: "3"`.

---

## 🔧 Environment Variable Matrix (`.env`)

| Variable | Description |
|---|---|
| `APP_PORT` | Host port mapped to FastAPI (`8000`) |
| `DB_PORT` | Host port mapped to PostgreSQL (`5432`) |
| `POSTGRES_USER` | PostgreSQL database user |
| `POSTGRES_PASSWORD` | PostgreSQL user password |
| `POSTGRES_DB` | Database name (`physiotherapy`) |
| `DATABASE_URL` | Full SQLAlchemy PostgreSQL connection URI |
| `RESEND_API_KEY` | Resend transactional email API key (server-side only) |
| `SECRET_KEY` | Cryptographic secret key used to sign HS256 JWT tokens |

---

## 💻 Essential Docker Commands

```bash
# Ensure shared network exists
docker network inspect pwn20wnd-network >/dev/null 2>&1 || docker network create pwn20wnd-network

# Build and start all services in detached mode
docker compose up -d --build

# Inspect container status and logs
docker compose ps
docker compose logs -f ar_engine
```
