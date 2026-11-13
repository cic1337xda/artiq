# Security Controls & Edge AI Architecture (`SECURITY_AND_ARCHITECTURE.md`)

## 📑 Language Options
* 🇬🇧 **[English Documentation (Current)](SECURITY_AND_ARCHITECTURE.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu](SECURITY_AND_ARCHITECTURE_MY.md)**

---

## 🛡️ Security Controls

1. **HttpOnly JWT Session Cookies:** Authentication tokens are issued as signed HS256 JWTs inside `HttpOnly`, `Secure`, `SameSite=Lax` cookies. Session tokens are never stored in `localStorage` or `sessionStorage`.
2. **Server-Side Access Control & IDOR Prevention:** All protected endpoints (including session management and EMG hardware endpoints) enforce FastAPI `Depends(get_current_user)` checks and verify ownership (`ExerciseSession.user_id == current_user.id`).
3. **Cryptographic OTP & Verification:** Both registration and password reset flows generate 6-digit OTPs via Python `secrets.randbelow`, enforce a `10-minute` expiration in GMT+8, cap failed attempts at `5`, and invalidate OTPs immediately after use.
4. **Password Strength & Hashing:** Passwords must contain at least 8 characters (max 70), including uppercase, lowercase, numeric, and special characters before hashing with Bcrypt.
5. **Rate Limiting & Account Lockout:** Authentication routes are rate-limited (`3/min` for OTP/reset emails, `5/min` for login/register). Accounts automatically lock for `15 minutes` after `5` consecutive failed login attempts.
6. **CSRF & HTTP Security Headers:** `SecurityAndTracingMiddleware` validates `Origin`/`Referer` against `Host` on state-changing requests (`POST`, `PUT`, `DELETE`, `PATCH`), attaches `X-Request-ID`, and injects:
   * `X-Frame-Options: DENY`
   * `X-Content-Type-Options: nosniff`
   * `Referrer-Policy: strict-origin-when-cross-origin`

---

## 🧠 Edge AI Computer Vision & Chroma Key Engine

### 1. Client-Side MediaPipe Hands Grip Tracking
* Video frames remain 100% local in the browser (`app.js`) — no camera frames are transmitted to the server.
* The pipeline measures Euclidean distance from wrist landmark (`0`) to the index (`8`), middle (`12`), and ring (`16`) fingertips:
  * **Grip Engaged:** Average normalized distance `< 0.15` transitions state to `GRIPPING`.
  * **Repetition Counted:** Releasing past `> 0.20` with an `800 ms` debounce cooldown increments the repetition counter cleanly without ghost reps.

### 2. Real-Time Chroma Key Guide Video
* `guide.mp4` is composited onto `#chromaCanvas` using per-pixel alpha masking in JavaScript, stripping green-screen pixels smoothly so clinicians and patients see a floating exercise reference overlay.

### 3. Desktop & Webcam Optimization
* Displays narrower than `900 px` trigger a Liquid Glass **Mobile Blocker** overlay (`@media (max-width: 900px)`) because MediaPipe hand tracking and side-by-side telemetry require desktop webcam ergonomics.
