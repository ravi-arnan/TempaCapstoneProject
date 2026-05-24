# Gamification — Pembagian Task Tim

**Status**: Aktif. Tim sudah setuju jalur Hybrid (Jalur B di GAMIFICATION.md).
**Database**: Neon Postgres (akses lewat FastAPI, identitas anonymous device ID).
**Last updated**: 2026-05-19

Acuan: `GAMIFICATION.md` (keputusan jalur), `backend/app/db/README.md` (setup DB + kontrak endpoint).

---

## Status saat ini

**Backend Fase 1 SELESAI** (XP/streak/level engine + persistence + 4 endpoint + 9 unit test):
- `app/services/xp_engine.py` — rumus XP/streak/level (pure, teruji)
- `app/services/achievements.py` — 6 badge deterministik
- `app/services/gamification_service.py` — persistence
- `app/routes/gamification.py` — endpoint
- `app/db/` — models, session, schema, init

**Sisa**: wiring frontend (Fase 1) + fitur Fase 2 & 3.

---

## Fase 1 — Core loop (XP + streak + level)

| Task | Owner | Acceptance Criteria | Status |
|---|---|---|---|
| Backend XP/streak/level engine + endpoint | Desta + Ariq | XP dihitung server-side, 4 endpoint jalan, unit test lulus | Selesai |
| Neon setup + migration | Ariq | Tabel ada di Neon, `GET /gamification/stats` balikin data | Selesai (DB sudah dikonfigurasi) |
| Frontend: device ID + API client | Ravi | UUID di localStorage, header `X-Device-Id` terkirim, method `recordAttempt`/`getStats` | Selesai |
| Frontend: trigger record setelah submit | Ravi | Setiap submit kuis memanggil `record-attempt` | Selesai |
| Frontend: tampilkan XP/level/streak di nav | Ravi | Nav menampilkan level, progress XP, streak (Lucide icon, no emoji) | Selesai |
| Frontend: feedback "XP +N" / "Level up" di result | Ravi | Banner reward muncul setelah submit (XP, level up, badge baru) | Selesai |

> **Fase 1 SELESAI end-to-end (backend + frontend), terverifikasi dengan Neon.**
> Verifikasi browser 2026-05-19: nav menampilkan Lv + XP + streak, RewardBanner muncul di result page.

---

## Bug fixes & tech debt (sambil jalan)

| Task | Owner | Detail | Status |
|---|---|---|---|
| CORS: izinkan header `X-Device-Id` | Ravi | Tanpa ini browser preflight memblokir semua call gamifikasi (curl lolos, browser tidak) | Selesai |
| Classifier guardrail: skor rendah tidak boleh "high" | Ravi (tambal) | ML sempat klasifikasi 20% sebagai "high" untuk waktu cepat (29s) | Selesai (sabuk pengaman, dipertahankan) |
| Retrain classifier dengan range waktu realistis | Ravi (ambil alih) | Root cause: `data_generation.py` melatih `time_taken_seconds` di range (60, 1800). Diubah ke `(10, 1800)` dan di-retrain. Model sekarang benar tanpa perlu guardrail (akurasi 94.1%, sklearn 1.8.0, tidak ada version mismatch lagi). | Selesai |

---

## Fase 2 — Daily goal + Achievements UI

| Task | Owner | Acceptance Criteria |
|---|---|---|
| Backend: daily goal logic (target XP harian + progress) | Desta | Endpoint/`stats` memuat progress harian; logika deterministik |
| Backend: tambah badge baju baru sesuai kebutuhan | Desta | Badge baru di `achievements.py`, ada test |
| Frontend: daily goal ring/progress di home atau nav | Ravi | Progress harian terlihat, reset tiap hari |
| Frontend: achievements list + unlock animation | Ravi | Semua badge tampil (locked/unlocked), Lucide icon, badge baru kasih notifikasi |
| Analitik: agregasi data attempt (rata-rata skor, tren) | Ariq | Query agregasi tersedia untuk dashboard |

---

## Fase 3 — Profil + Riwayat

| Task | Owner | Acceptance Criteria |
|---|---|---|
| Backend: endpoint history sudah ada; tambah agregat ringkasan | Ariq | `GET /gamification/history` + ringkasan (total kuis, rata-rata skor) |
| Frontend: ProfilePage (dashboard XP/level/streak/badges) | Ravi | Halaman profil menampilkan semua stat + badge |
| Frontend: HistoryPage (10 kuis terakhir + skor) | Ravi | Daftar riwayat, klik untuk lihat detail/asah ulang |
| Frontend: "Bandingkan dengan attempt sebelumnya" di result | Ravi | Tampilkan delta skor vs attempt sebelumnya pada materi sama |
| Integrasi riwayat dengan quiz generator | Audry | Quiz_id tersimpan konsisten, bisa di-regenerate dari riwayat |

---

## Catatan teknis untuk tim

- **Identitas**: anonymous device ID (UUID di localStorage, header `X-Device-Id`). Tidak ada login. Skema sudah siap di-upgrade ke auth nanti tanpa migrasi.
- **Anti-cheat**: XP/streak/level dihitung di backend, bukan client. Jangan pindahkan logika ini ke frontend.
- **Brand voice**: Lucide icon bukan emoji (`Zap` XP, `Flame` streak, `TrendingUp` level, `Trophy`/`Star`/`Sparkles` badge). Tetap "kamu", tetap honest (bukan "GREAT JOB!!!").
- **Graceful degradation**: kalau `DATABASE_URL` kosong, endpoint gamifikasi balikin 503 dan fitur kuis inti tetap jalan. Frontend harus handle 503 dengan menyembunyikan UI gamifikasi, bukan crash.

---

## Catatan capstone

Ekspansi ini (DB + identitas user) keluar dari scope proposal awal. **Sudah/akan dibahas dengan advisor (Rosyiidah) di sesi 23 Mei.** Kalau advisor minta scope dikembalikan, gamifikasi bisa di-toggle off via `DATABASE_URL` kosong tanpa mengganggu demo kuis inti.
