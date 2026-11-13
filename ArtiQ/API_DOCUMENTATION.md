# RESTful API Reference (`API_DOCUMENTATION.md`)

## 📑 Language Options
* 🇬🇧 **[English Documentation (Current)](API_DOCUMENTATION.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](API_DOCUMENTATION_MY.md)**

---

## 📦 Standardized JSON Response Envelope

All API responses (except `GET /api/v1/health`) follow this envelope:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {},
  "error": null
}
```

Every response also includes an `X-Request-ID` header for distributed request tracing.

---

## 🩺 Healthcheck Endpoint

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | Public | Verifies PostgreSQL connectivity (`SELECT 1`) and returns GMT+8 timestamp. |

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-11-12T14:20:00+08:00"
}
```

---

## 🔐 Authentication & OTP Endpoints

| Method | Endpoint | Rate Limit | Auth | Description |
|---|---|---|---|---|
| `POST` | `/api/send-otp` | `3/minute` | Public | Sends a cryptographic 6-digit registration OTP (10-min expiry). |
| `POST` | `/api/register` | `5/minute` | Public | Validates OTP (max 5 attempts), enforces password strength, creates admin user. |
| `POST` | `/api/login` | `5/minute` | Public | Authenticates user, enforces 15-min lockout after 5 failures, sets `HttpOnly` JWT cookie. |
| `POST` | `/api/forgot-password` | `3/minute` | Public | Dispatches a 6-digit password reset OTP via Resend. |
| `POST` | `/api/reset-password` | `5/minute` | Public | Verifies reset OTP, validates new password strength, updates hash, clears lockouts. |
| `POST` | `/api/logout` | — | Public | Clears the `access_token` cookie. |
| `GET` | `/api/user` | — | Cookie | Returns the authenticated administrator's username and email. |

*(Versioned aliases under `/api/v1/auth/*` are also exposed for all auth routes.)*

---

## 🏋️ Exercise Session Endpoints

All session endpoints require an authenticated `access_token` cookie and enforce strict ownership (`user_id == current_user.id`):

| Method | Endpoint | Body / Params | Description |
|---|---|---|---|
| `POST` | `/api/session/start` | `{"name": "Patient Name", "age": 45}` | Starts a new clinical repetition session and returns `session_id`. |
| `POST` | `/api/session/stop` | `{"session_id": 1, "reps": 12}` | Saves `end_time` (GMT+8) and `total_reps` for the owned session. |
| `GET` | `/api/history` | — | Returns the latest 15 exercise sessions belonging to the authenticated admin. |

---

## ⚡ EMG Telemetry & Hardware Control Endpoints

All EMG endpoints require an authenticated `access_token` cookie:

| Method | Endpoint | Body / Params | Description |
|---|---|---|---|
| `GET` | `/api/emg/telemetry` | — | Returns live node state (`mac`, `is_online`, `raw`, `percent`, `mvc`, `calibrating`). |
| `POST` | `/api/emg/set-mac` | `{"mac": "A1B2C3D4E5F6"}` | Locks telemetry ingestion and commands to a specific ESP32 MAC address. |
| `POST` | `/api/emg/command/{cmd}` | `cmd` in `calibrate \| reset \| relax \| baseline` | Publishes an MQTT command (`QoS 1`) to `artiq/emg/command/{mac}`. |
