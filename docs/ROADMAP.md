# Roadmap — Asahlagi

**Status**: OPEN. Living document.
**Owner**: Ravi
**Created**: 2026-05-18
**Last updated**: 2026-06-07

---

## Context

Setelah batch polishing + UX delight (lihat git history 2026-05-18), state product sekarang:
- Frontend end-to-end working: text/URL/PDF input, one-question-at-a-time quiz, keyboard shortcuts, auto-save, score animation, confetti, "Asah Lagi" regenerate, per-question breakdown
- Backend: HF Space DL + rule-based mix fallback, all-mode reliability
- 43 backend tests + typecheck/build hijau
- Belum di-deploy publik, belum ada frontend tests

Dokumen ini menangkap arah pengembangan setelah batch hari ini, supaya keputusan bisa diambil saat sudah punya bandwidth tanpa harus brainstorming ulang.

---

## 1. Buat orang lain bisa coba (high ROI untuk capstone)

### 1.1 Deploy public URL (lihat `DEPLOY.md`)
- Frontend: Vercel (auto-deploy dari GitHub branch `main`)
- Backend: **Hugging Face Spaces (Docker)** — tanpa kartu kredit; config di `huggingface/backend/`. HTTPS otomatis (`*.hf.space`). Render disimpan sebagai alternatif (`render.yaml`).
- HF Space quiz-gen: sudah live di `https://raviarnan-asahlagi-quizgen.hf.space`
- Secrets di Space backend: `HF_SPACE_URL`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS` (point ke Vercel + origin Capacitor `https://localhost`)
- Frontend env: `VITE_API_BASE_URL` (point ke URL Space backend)

**Hasil**: link publik yang bisa di-share ke pembimbing/audience, sekaligus prasyarat untuk app Android (lihat #6.4 + `MOBILE.md`).

**Effort**: ~2-3 jam (setup awal + debugging CORS + healthcheck)

### 1.2 README screenshots + demo GIF
- Setelah deploy, screen-record 60-90 detik full flow
- Embed di README sebagai hero
- Tambah 3-4 screenshot (homepage, quiz, result) di section "Demo"

**Effort**: ~1 jam

---

## 2. Doc sync (cepat tapi penting)

Beberapa dokumen drift dari kode setelah banyak perubahan hari ini.

### 2.1 API.md
- Tambah section §4.X untuk `POST /quiz/regenerate`
- Tambah field `question_reviews[]` di `QuizSubmitResponse`
- Update field name di internal note: `source_material_excerpt` → `source_material`
- Update endpoint count: 5 → 6 endpoints

### 2.2 ARCHITECTURE.md
- §7.1 storage: update "excerpt" mention jadi full material
- §8 atau baru: dokumentasikan mix DL+rule-based strategy
- §5: tambah regenerate endpoint ke routing table
- Update quiz layout: scrolling list → single-question

### 2.3 BRAND.md
- §7.2 button labels: tambah `jumpToUnanswered`, `resultRetryLoading`
- §7.X loading: tambah `LOADING_PROGRESS_MESSAGES` series
- Catat brand-callback "asah lagi" sekarang juga dipakai di "Asah Lagi" button (tidak cuma di recommendation copy)

### 2.4 TASKS.md
- Centang/move tasks yang sudah selesai
- Refleksi: backend trio selesai, frontend delight layer selesai
- Tambah open backlog items dari ROADMAP.md ini

### 2.5 PRD.md
- Update scope: tambah multi-source input (PDF/URL) — sudah keluar dari "Out of Scope"
- Tambah feature "regenerate" (Asah Lagi) ke list MVP

**Effort total**: ~2 jam

---

## 3. Reliability / quality

### 3.1 Frontend tests (Vitest + RTL)
Saat ini 0 tests di frontend.

**Minimum viable suite**:
- Smoke: HomePage renders, sample button populates textarea
- QuizPage: keyboard 1-4 selects option, J/K navigates, Enter advances
- ResultPage: count-up animates to target value
- useQuizPersistence: save → load → clear

**Setup**:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**Effort**: ~3-4 jam (setup + 6-8 tests)

### 3.2 Material quality pre-check
**Owner: Ariq** (assigned 2026-06-06)

Sebelum kirim ke generator, score "quizability" cepat:
- Word count, sentence count, alpha ratio
- Cek brand/junk pattern density (mirror filter di quiz_generator.py)
- Kalau jelek → kasih warning + saran ("Materi ini sebagian besar tabel/sitasi. Mungkin tidak menghasilkan kuis bagus.") sebelum loading 15 detik

**Effort**: ~2 jam (logic + UI warning component)

### 3.3 Smart distractors via embeddings
Saat ini distractor = random keyword similar length. Quality bisa naik signifikan dengan semantic similarity:
- Tambah `sentence-transformers` ke HF Space (model `indobenchmark/indobert-base-p1` atau `firqaaa/indo-sentence-bert-base`)
- Generator: encode correct answer + pool, pick 3 dengan similarity 0.5-0.8 (mirip tapi tidak identik)
- Alternative lite: pakai word frequency + POS tagging untuk filter kata kerja vs kata benda

**Effort**: ~1 hari (HF Space change + integration)

### 3.4 Rate limiting backend
**Owner: Ariq** (assigned 2026-06-06)

Per-IP throttle untuk `/quiz/generate*` (3 request/menit), pakai `slowapi` middleware.

**Effort**: ~30 menit

---

## 4. Feature additions (post-MVP)

### 4.1 History page
- LocalStorage based, no backend change
- List 10 kuis terakhir + skor + understanding level
- Click → re-display result page (kalau result masih cached) atau "Asah Lagi" dari kuis itu
- "Bandingkan dengan attempt sebelumnya" di result page (apa kemajuan?)

**Effort**: ~3-4 jam

### 4.2 Share result URL
- Copy URL dengan `?quiz_id=X` (atau short hash)
- Result page accept query param, fetch atau decode
- Optional: OG image generator untuk preview di Twitter/WA
- Optional: download result as image

**Effort**: ~3-5 jam (basic) sampai 1 hari (dengan OG)

### 4.3 Quiz settings (pre-generate)
User pilih sebelum generate:
- Jumlah soal: 3 / 5 / 7 / 10
- Difficulty (kalau ada): mudah / sedang / sulit
- Toggle "Acak urutan opsi"

Implementasi: backend terima parameter, generator hormati.

**Effort**: ~2-3 jam

### 4.4 Per-topic mastery tracking (BIG)
Selaras dengan judul capstone "Sistem Deteksi Tingkat Pemahaman".
- Tag tiap kuis dengan topik (auto-extract dari materi atau user input)
- Track score per topik over time
- Dashboard: "Pemahaman kamu di topik X naik dari 60% → 80%"
- Identifikasi weak spots: topik dengan skor rendah konsisten

**Effort**: ~2-3 hari

### 4.5 Landing page — jelaskan fitur aplikasi (BARU 2026-06-06)
**Owner: Audry · polish: Ravi**

Halaman publik sebelum masuk app, buat menjelaskan apa & kenapa aplikasi ini ada.
- App pindah ke route `/app` (atau `/mulai`); `/` jadi landing.
- Section: hero + value prop ("Asah lagi sampai paham"), feature grid (input multi-source teks/URL/PDF, kuis satu-per-satu, analisis tingkat pemahaman, insight + rekomendasi, gamifikasi XP/streak, mastery per-topik), "cara kerja" 3 langkah, CTA "Coba sekarang".
- Pakai Lucide icons, tokens dari `DESIGN.md`, suara dari `BRAND.md` (hindari template generic — lihat anti-template policy).
- Dark/light mode + responsive.

**Effort**: ~1 hari (build) + polish

### 4.6 Step-by-step tour — onboarding (BARU 2026-06-06)
**Owner: Desta · polish: Ravi**

Guided tour saat kunjungan pertama, highlight elemen kunci satu per satu.
- Sorot: input materi → tombol generate → timer → navigasi soal (J/K, 1-4) → halaman hasil (skor, level, insight, rekomendasi, chart).
- Library: **driver.js** (ringan, tanpa dep berat) atau `react-joyride`.
- Trigger: first visit (flag di localStorage) + tombol "?" di nav untuk ulang kapan saja.
- Copy tiap langkah konsisten `BRAND.md` (suara "kamu", calm, no patronizing) — Desta cocok karena sudah pegang voice insight/recommendation.
- Respect `prefers-reduced-motion`.

**Effort**: ~0.5-1 hari

### 4.7 Login — Third-party OAuth (BARU 2026-06-06)
**Owner: Ravi (full) · review: Ariq (data layer)**

> ⚠️ **Scope expansion**: `CLAUDE.md` menandai auth sebagai *Out of Scope*. Disepakati masuk sebagai **post-MVP**, pakai jalur paling ringan: **Google Identity Services (GIS) langsung** — login "beneran" tanpa hand-roll password/JWT, dan tanpa layanan auth pihak ketiga (gratis, nol infrastruktur baru).

Ravi pegang full (frontend + backend tipis) karena OAuth mayoritas frontend + verify token, nyambung dengan kerja polishing-nya.
- Frontend: tombol "Masuk dengan Google" (`@react-oauth/google`), avatar + menu di nav, state guest vs logged-in.
- Backend tipis: verify Google ID token pakai public key Google (`google-auth`), tabel `user` minimal di Postgres (`DATABASE_URL` sudah ada), link quiz attempts ke `user_id`. Ariq review bagian data layer (domain-nya).
- Manfaat: history / mastery per-topik (#4.4) / gamifikasi (#6.3) bisa ter-link ke akun, bukan cuma localStorage.
- Tetap bisa dipakai tanpa login (guest mode) supaya demo nggak terblok.

**Effort**: ~1-1.5 hari

> ✅ **Status 2026-06-07**: SELESAI & live. GIS langsung, `/auth/google` verify via `google-auth`, kolom `users.google_sub/email/avatar_url` (migrasi 0003), guest mode utuh. Deployed: Neon migrated, HF Space `GOOGLE_CLIENT_ID` set, Vercel `VITE_GOOGLE_CLIENT_ID` set. (PR #6/#7/#8.)

---

### 4.8 User Hub & fitur akun — post-login (BARU 2026-06-07)
**Owner: Ravi (frontend) · review: Ariq (data layer untuk endpoint baru)**

Cluster fitur yang mengarah ke user, dibangun di atas login (#4.7). Status fondasi ditandai: 🟢 = endpoint/data sudah ada (mostly frontend), 🟡 = butuh backend baru.

- **a) Halaman Profil (hub)** 🟢 — identitas (avatar/nama/email) + ringkasan gamifikasi (level/XP/streak/total kuis) + grid badge + link ke Progress (#4.4). Konsumsi endpoint yang sudah ada (`/gamification/stats`, `/gamification/achievements`, `/gamification/analytics`). Guest → ajak login.
- **b) Halaman Settings** 🟢 — tema (light/dark), info akun, tombol Keluar. Opsi lanjut 🟡: edit nama tampilan (`PATCH /auth/me`), hapus akun & data (`DELETE` + cascade) — review Ariq.
- **c) Halaman Riwayat Kuis (History)** 🟢 — `GET /gamification/history` (items + summary) **sudah jalan**; tinggal UI. List: skor, level pemahaman, topik, XP, tanggal; klik → detail / "Asah Lagi". (Menggantikan rencana #4.1 yang localStorage — kini DB-backed + ter-link akun.)
- **d) Leaderboard** 🟡 — ranking by XP/level. **Desain privasi**: tampil display name (login) atau "Anonim" (guest), idealnya opt-in. Endpoint baru `GET /gamification/leaderboard` (top N). (GAMIFICATION.md dulu menandai ini "far future"; sekarang feasible karena sudah ada auth.)
- **e) Edit preferensi belajar** 🟡 — default jumlah soal, difficulty, acak opsi, topik favorit; disimpan per-user + di-wire ke `/quiz/generate`. Nyambung dengan #4.3 (Quiz settings).
- **f) Target/Goal mingguan** 🟡 — "X kuis minggu ini" + progress bar; booster retensi.
- **g) Simpan materi (bookmark)** 🟡 — simpan materi yang ditempel untuk diasah ulang nanti. Butuh tabel baru. Relevan untuk use-case belajar.
- **h) Badge/Pencapaian showcase** 🟢 — `/gamification/achievements` sudah ada (locked/unlocked); section di Profil atau halaman sendiri.
- **i) Kartu Tantangan Harian + streak** 🟢 — backend `daily-challenge` sudah ada; surface di Home/Profil + streak calendar.
- **j) Share hasil / Export progress** 🟡 — share URL hasil kuis (nyambung #4.2) + export ringkasan progres (gambar/PDF).

**Catatan scope** (CLAUDE.md: utamakan flow end-to-end, jangan semua sekaligus). Saran batching:
- **Batch 1 — "User Hub"** (cepat, mostly frontend): a) Profil + c) History + b) Settings (tema/logout) + h) badge. **~1-1.5 hari.**
- **Batch 2** (butuh backend, review Ariq): e) edit preferensi + d) leaderboard + f) goal + g) bookmark. **~2-3 hari.**
- **Batch 3**: j) share/export + i) daily challenge surfacing. **~0.5-1 hari.**
- **Hati-hati / skip**: teman/social (berat, butuh relasi), notifikasi (butuh push infra → lihat #6.4).

---

## 5. Polish layer 3 (kecil-kecil)

- **Toast notifications** untuk feedback non-fatal (network blip, retry success)
- **Skeleton loader** saat generate (sekarang masih bullet-text rotation)
- **Drag-and-drop PDF anywhere** di homepage (sekarang cuma di dropzone area)
- **Empty state illustration** di homepage (text-only, Lucide-style icon)
- **Visual audit dark mode**: cek semua `bg-brand-button` apakah harusnya stay dark (button action) atau emerald (status indicator). PulsingDot fix tadi indikasi mungkin ada yang lain.
- **prefers-reduced-motion** audit di seluruh app (sekarang baru count-up + question-in animation yang respect)

---

## 6. Bigger directions

### 6.1 Multi-language (Indonesian + English)
- i18n.ts arsitektur sudah siap (`{ id: {...}, en: {...} }`)
- Backend insight/recommendation perlu translation atau parallel template
- Toggle bahasa di nav

**Effort**: 2-3 hari

### 6.2 More question types
**Owner: Ariq** (assigned 2026-06-06)
- True/False
- Isian singkat (free text, butuh string matching atau LLM grading)
- Matching (cocok pernyataan A dengan jawaban B)

Backend evaluator + UI both perlu refactor untuk handle question type variant.

**Effort**: 3-5 hari

### 6.3 Gamification (lihat `GAMIFICATION.md`)
Jalur B (hybrid) disetujui tim. Fase 1 (XP/streak/level) sudah selesai.
Pembagian Fase 2-4 ada di `GAMIFICATION_TASKS.md`.

### 6.4 Mobile app — Capacitor, Android-first (lihat `MOBILE.md`)
Bungkus React web yang ada jadi APK Android via Capacitor. **Keputusan**: Android dulu,
iOS ditunda. **Prasyarat**: backend deploy ke HTTPS publik (lihat #1.1).

Roadmap mobile (ditunda, urut prioritas):
- **Push notification** (Capacitor Push + Firebase Cloud Messaging) — reminder streak,
  daily goal, level-up nudge. Nyambung ke Fase 4 (Desta) nudge logic. Nilai jual mobile
  terbesar untuk gamifikasi.
- iOS support — dibatalkan (tim tidak punya Mac); tinjau ulang jika ada akses Mac nanti
- Native storage + file picker (`@capacitor/preferences`, `@capacitor/filesystem`)
- Publish Play Store ($25 sekali bayar)
- Offline mode (rule-based generator + cache)

**Effort wrap dasar**: ~0.5-1 hari (setelah backend ter-deploy). Push notification: +1-2 hari.

---

## Saran prioritas

**Saat demo capstone deket (≤ 1 minggu)**:
1. **#2 Doc sync** (~2 jam, wajib)
2. **#1 Deploy public URL** (~3 jam, audience impact terbesar)
3. **#1.2 Demo video/screenshots** (~1 jam)

**Pasca demo, kalau lanjut sebagai produk**:
4. **#3.1 Frontend tests** (reliability)
5. **#4.1 History page** + **#4.2 Share URL** (meaningful feature add)
6. **#4.4 Per-topic mastery** (DNA capstone tetap utuh, value naik signifikan)

**Bisa di-defer ke versi 2**:
- #3.3 Smart distractors (real ML upgrade)
- #6 Bigger directions

---

## Decision log

| Tanggal | Keputusan | Reason |
|---|---|---|
| 2026-05-18 | (OPEN) | Dokumen dibuat. Menunggu Ravi pilih prioritas pasca push hari ini. |
| 2026-06-06 | Tambah 3 fitur: landing page (#4.5), onboarding tour (#4.6), login OAuth (#4.7) | Ravi mau fokus polishing; fitur frontend-heavy dibagi ke tim. |
| 2026-06-06 | Owner: Landing→Audry, Tour→Desta, Login→Ravi (full), polish semua→Ravi | Tiap teman bangun frontend fitur-nya end-to-end; Ravi review + polish. Login OAuth ringan jadi Ravi pegang sendiri. |
| 2026-06-06 | Login pakai third-party OAuth (Google/Supabase), bukan auth custom | Login "beneran" tanpa hand-roll password/JWT; scope expansion dari CLAUDE.md disepakati sebagai post-MVP. |
| 2026-06-06 | Provider login: **Google Identity Services (GIS) langsung**, bukan Supabase Auth | GIS gratis tanpa kuota & nol layanan eksternal baru (sejalan KISS/anti over-engineering). Hindari risiko Supabase free-tier auto-pause (~7 hari idle) yang bisa ganggu demo. Verify ID token via public key Google. |
| 2026-06-06 | Ariq ambil track Data & Quality: #3.2 + #3.4 + #6.2 | Ariq tidak ambil fitur baru; kerjakan task roadmap lama yang belum jalan, sesuai domain Data & Analisis. |
| 2026-06-07 | Login (#4.7) selesai & deployed (Neon migrated, HF + Vercel env set) | Verified live: `/auth/google`→401 untuk token invalid, guest mode utuh. Hotfix `requests` dep (PR #8) setelah Space crash di rebuild pertama. |
| 2026-06-07 | Tambah cluster #4.8 "User Hub & fitur akun" (profil, settings, history, leaderboard, edit preferensi, goal, bookmark, badge, daily challenge, share/export) | Lanjutan natural dari login. Owner Ravi (frontend), Ariq review data layer untuk endpoint baru. Dibatch: User Hub dulu (mostly FE), backend-heavy menyusul. |

---

## Reference

- `GAMIFICATION.md` — gamification options (3 jalur)
- `BRAND.md` — voice, copy library
- `CLAUDE.md` — scope lock
- `PRD.md` — capstone requirements
- `TASKS.md` — original 5-week plan
- `API.md` — HTTP contract
- `ARCHITECTURE.md` — internal structure
