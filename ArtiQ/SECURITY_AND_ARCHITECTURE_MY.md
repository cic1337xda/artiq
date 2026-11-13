# Kawalan Keselamatan & Seni Bina Edge AI (`SECURITY_AND_ARCHITECTURE_MY.md`)

## 📑 Pilihan Bahasa
* 🇬🇧 **[English Documentation](SECURITY_AND_ARCHITECTURE.md)**
* 🇲🇾 **[Dokumentasi Bahasa Melayu (Semasa)](SECURITY_AND_ARCHITECTURE_MY.md)**

---

## 🛡️ Kawalan Keselamatan

1. **Kuki Sesi JWT `HttpOnly`:** Token pengesahan dijana sebagai JWT HS256 bertandatangan di dalam kuki `HttpOnly`, `Secure`, `SameSite=Lax`. Token sesi tidak pernah disimpan dalam `localStorage` atau `sessionStorage`.
2. **Kawalan Akses Pelayan & Pencegahan IDOR:** Semua laluan terlindung (termasuk pengurusan sesi dan kawalan EMG) mewajibkan `Depends(get_current_user)` di pelayan serta menyemak pemilikan rekod (`ExerciseSession.user_id == current_user.id`).
3. **OTP Kriptografi & Pengesahan:** Aliran pendaftaran dan tetapan semula kata laluan menjana OTP 6-digit menggunakan modul `secrets.randbelow`, tempoh sah `10 minit` (GMT+8), had `5` percubaan salah, dan pengesahan guna-sekali (*single-use*).
4. **Kekuatan & Pencincangan Kata Laluan:** Kata laluan mesti sekurang-kurangnya 8 aksara (maks 70) dengan gabungan huruf besar, huruf kecil, nombor, dan aksara khas sebelum dicincang menggunakan Bcrypt.
5. **Had Kadar & Penguncian Akaun:** Laluan pengesahan dihadkan kadar permintaan (`3/minit` bagi OTP/tetapan semula, `5/minit` bagi log masuk/daftar). Akaun dikunci secara automatik selama `15 minit` selepas `5` kegagalan log masuk berturut-turut.
6. **Perlindungan CSRF & Header Keselamatan HTTP:** `SecurityAndTracingMiddleware` mengesahkan header `Origin`/`Referer` terhadap `Host` bagi permintaan pengubah keadaan (`POST`, `PUT`, `DELETE`, `PATCH`), menjana `X-Request-ID`, serta menyuntik:
   * `X-Frame-Options: DENY`
   * `X-Content-Type-Options: nosniff`
   * `Referrer-Policy: strict-origin-when-cross-origin`

---

## 🧠 Penglihatan Komputer Edge AI & Enjin Chroma Key

### 1. Penjejakan Genggaman Tangan MediaPipe di Pelayar
* Strim kamera diproses 100% secara tempatan di dalam pelayar (`app.js`) — tiada bingkai video dimuat naik ke pelayan.
* Saluran penglihatan mengira purata jarak Euclidean dari titik pergelangan tangan (`0`) ke hujung jari telunjuk (`8`), jari hantu (`12`), dan jari manis (`16`):
  * **Genggaman Aktif:** Purata jarak ternormal `< 0.15` menukar status kepada `GRIPPING`.
  * **Kiraan Ulangan:** Membuka tangan melebihi `> 0.20` dengan selang penyejukan `800 ms` menambah kiraan ulangan tanpa kiraan palsu.

### 2. Panduan Video Chroma Key Masa Nyata
* Fail `guide.mp4` diproses pada `#chromaCanvas` menggunakan penapisan alfa latar hijau secara langsung untuk memaparkan panduan senaman terapung yang kemas.

### 3. Pengoptimuman Desktop & Webcam
* Skrin di bawah lebar `900 px` memaparkan tindanan **Liquid Glass Mobile Blocker** (`@media (max-width: 900px)`) bagi memastikan pengalaman penjejakan webcam dan telemetri yang tepat pada komputer desktop atau komputer riba.
