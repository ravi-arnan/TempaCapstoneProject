# TASKS.md

## Project
**Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data**
**Brand**: Asahlagi — _Asah lagi sampai paham._
**Team ID**: TP-G005

## Objective
Membangun aplikasi web sederhana yang dapat:
- menerima materi pembelajaran dalam bentuk teks,
- menghasilkan kuis otomatis,
- memfasilitasi pengerjaan kuis,
- menganalisis hasil,
- menampilkan tingkat pemahaman, insight, rekomendasi, dan grafik sederhana.

---

## 📸 Status Snapshot (per 2026-05-06)

Sebelum Week 1 coding dimulai, **semua scaffolding sudah selesai**. Setiap orang punya file yang siap diisi (placeholder implementations sudah jalan end-to-end, tinggal direplace dengan logic proper).

### ✅ Sudah selesai
- Repo + GitHub setup (https://github.com/ravi-arnan/TempaCapstoneProject)
- Dokumentasi planning lengkap: `CLAUDE.md`, `PRD.md`, `README.md`, `DESIGN.md`, `API.md`, `ARCHITECTURE.md`, `BRAND.md`
- Frontend scaffolding (Vite + React + TS + Tailwind): pages, components, hooks, types, API client, i18n labels, theme system (light/dark)
- Backend scaffolding (FastAPI): main app, CORS + exception handler, routes, schemas (public + internal), in-memory storage, submit coordinator
- Brand identity: nama "Asahlagi", logo SVG (V1 slash-crossbar), favicon
- Placeholder implementations untuk **3 service** yang masih menunggu implementasi proper:
  - `quiz_generator.py` (Audry's stub — fill-in-the-blank rule-based)
  - `quiz_evaluator.py` (Ariq's stub — standard scoring)
  - `understanding_classifier.py` (Desta's stub — rules dari PRD §15)
- Base templates di `insight_engine.py` dan `recommendation_engine.py` dari BRAND.md §7.6-7.7

### ⏳ Yang harus dikerjakan tim
Replace placeholder implementations dengan logic proper masing-masing. Detail di section "Task Breakdown Per Member".

---

## Team Members

| Nama | ID | Role |
|---|---|---|
| Audry Nabila Anastasya | AIC161BX0012 | Backend - Quiz Generator |
| Ariq Marwan Permana | AIC012B6Y0004 | Backend - Data & Analisis |
| Desta Anandhika Rajendra Maheswara | AIC183B6Y0048 | Backend - Logic, Insight & Recommendation |
| Ravi Arnan Irianto | AIC014B6Y0008 | Frontend - React & TypeScript |

---

## Working Rules

- **Pendekatan sequential**: Audry → Ariq → Desta. Tiap minggu ada 1 "main owner" yang fokus implementasi inti, sementara yang lain support (review, polish, polishing dokumen demo, dll). Tidak ada anggota yang idle.
- Fokus pada MVP, jangan menambah fitur di luar scope tanpa diskusi tim.
- Prioritaskan flow end-to-end yang berjalan.
- Semua task besar harus punya owner yang jelas.
- **Branch per fitur** dengan prefix owner: `feat/audry-quiz-generator`, `feat/ariq-evaluator`, dll.
- **PR review wajib** dari minimal 1 anggota lain sebelum merge ke `main`.
- **Kalau ubah `backend/app/schemas/internal.py`** (`QuizInternal`, `EvaluationResult`, dll) — HARUS sync ke tim dulu. Itu integration boundary.
- Sync meeting **minimal 1× per minggu** + daily progress update di chat saat sedang giliran main owner.
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`.

---

## MVP Deliverables (status di-update tiap minggu)

- [x] Input materi teks (frontend skeleton sudah jalan)
- [x] Quiz generator sederhana (placeholder; **Audry refine**)
- [x] Halaman pengerjaan kuis (frontend skeleton sudah jalan)
- [x] Penghitungan skor dan waktu (placeholder; **Ariq refine**)
- [x] Klasifikasi tingkat pemahaman (placeholder; **Desta refine**)
- [x] Insight otomatis (base template; **Desta refine** dengan sub-conditions)
- [x] Rekomendasi belajar (base template; **Desta refine** dengan sub-conditions)
- [x] Grafik hasil sederhana (frontend ScoreChart sudah jalan)
- [x] Integrasi frontend dan backend (sudah verified end-to-end)
- [ ] Demo siap presentasi (Week 5)

> Catatan: checkmark `[x]` di atas berarti **sudah berfungsi end-to-end di level placeholder**, bukan berarti final. Tim refine selama Week 2-4.

---

## 🛤️ Critical Path

```
Week 1     Week 2          Week 3          Week 4         Week 5
─────────  ─────────       ─────────       ─────────      ─────────
Setup &    AUDRY ⭐         ARIQ ⭐          DESTA ⭐        Polish
Sync       quiz_generator  quiz_evaluator  classifier     +
                                            insight        Demo
                                            recommendation
                ↓               ↓               ↓
            All review      Desta start     All integrate
                            mendekati impl
```

**Aturan critical path**:
- Kalau **main owner minggu ini meleset**, downstream geser. Kabari secepatnya kalau bakal late.
- Buffer ada di Week 5. Jangan jadwalkan coding berat di Week 5.
- Frontend (Ravi) work paralel di semua minggu (polish, integration testing) tapi tidak di critical path.

---

## Milestone Mingguan

### Minggu 1 — Setup & Sync (semua orang aktif)

**Goal**: semua orang setup environment, baca dokumentasi, sepakat soal `EvaluationResult` shape.

| Owner | Task |
|---|---|
| All | Clone repo, install dependencies (frontend + backend), run dev server lokal |
| All | Baca `API.md` (HTTP contract) + `ARCHITECTURE.md` §6 (internal types) + `ARCHITECTURE.md` §10 (dependency graph) |
| All | Baca section spesifik masing-masing di `BRAND.md` §7 (copy library) |
| All | **Sign-off**: tick checklist di `API.md` §12, `ARCHITECTURE.md` §14, `BRAND.md` §11 |
| All | **Lock `EvaluationResult` shape** — kalau ada usulan perubahan, raise di sync meeting Week 1 |
| Audry | Riset approach quiz generator. Siapkan 2-3 sampel materi belajar untuk testing (fotosintesis, fotografi, ekonomi mikro, dll). |
| Ariq | Riset apakah perlu pandas/scikit-learn. Sketch pseudocode evaluator + test cases. |
| Desta | List edge cases klasifikasi (boundary score 79% vs 80%, all unanswered, dll). Refine template insight & recommendation berdasarkan BRAND.md §7.6-7.7. |
| Ravi | Polish frontend: tambah loading states, error toast, mobile responsive verification. |

---

### Minggu 2 — Audry's Week ⭐

**Goal**: `quiz_generator.py` selesai diimplementasi + di-merge ke `main`.

| Owner | Task |
|---|---|
| **Audry** ⭐ | Implementasi quiz_generator — replace placeholder dengan logic kamu. Output: `QuizInternal` per ARCHITECTURE.md §6.1-6.2. |
| **Audry** | Tulis unit tests di `backend/tests/test_quiz_generator.py` (minimal 3-5 cases: normal text, empty, very short, very long, edge cases). |
| **Audry** | Daily progress update di chat. |
| **Audry** | Open PR `feat/audry-quiz-generator` → review by 1+ anggota → merge. |
| Ariq | Review PR Audry. Sketch evaluator pseudocode. Mulai familiar dengan `EvaluationResult` shape. |
| Desta | Refine insight/recommendation TEMPLATES (text saja, belum coding). Brainstorm sub-conditions: "high score + slow time", "low score + many unanswered", dll. |
| Ravi | Polish frontend: cek behavior dengan placeholder backend, fix any UX issues, test di multiple screen sizes. |

**Definition of Done untuk Week 2**: PR Audry merged, full flow `POST /quiz/generate` return real questions (bukan placeholder fallback).

---

### Minggu 3 — Ariq's Week ⭐ + Desta start

**Goal**: `quiz_evaluator.py` selesai + Desta mulai coding modulnya.

| Owner | Task |
|---|---|
| **Ariq** ⭐ | Implementasi quiz_evaluator. Audry's `QuizInternal` shape sudah stable. Output: `EvaluationResult` per ARCHITECTURE.md §6.3. |
| **Ariq** | Eksplorasi pandas kalau perlu (per-question time, distribution analysis, dll) — tapi MVP boleh tanpa. |
| **Ariq** | Tests di `backend/tests/test_quiz_evaluator.py`. |
| **Ariq** | Open PR `feat/ariq-evaluator` → review → merge. |
| Desta | Mulai implement `understanding_classifier.py` pakai `EvaluationResult` dari Ariq. Tweak thresholds dari PRD §15. |
| Audry | Review PR Ariq + Desta. Fix bug di generator kalau ada laporan. |
| Ravi | Integration testing dengan real backend. Verify edge cases UI: error responses, slow responses, empty results. |

**Definition of Done Week 3**: PR Ariq merged. Submit endpoint return real `EvaluationResult` (bukan placeholder).

---

### Minggu 4 — Desta's Week ⭐ + integration

**Goal**: ketiga modul Desta selesai + full flow end-to-end pass test.

| Owner | Task |
|---|---|
| **Desta** ⭐ | Tweak `understanding_classifier.py` thresholds berdasarkan testing dengan materi nyata. |
| **Desta** | Implement sub-conditions di `insight_engine.py` — bukan cuma base template, tapi variasi based on score+time pattern. |
| **Desta** | Implement sub-conditions di `recommendation_engine.py`. |
| **Desta** | Tests untuk ketiga modul. |
| **Desta** | Open PR `feat/desta-classifier-insight-recommendation` → review → merge. |
| All | Integration testing: `pytest tests/test_routes.py::test_generate_then_submit_full_flow` HARUS pass. Test 5 skenario: high/medium/low + edge cases. |
| Ravi | Result page polish: tuning chart visualization, animation pada result reveal, mobile-responsive verification. |

**Definition of Done Week 4**: full E2E flow jalan dengan real implementations (no placeholders), PR Desta merged.

---

### Minggu 5 — Polish & Demo

**Goal**: aplikasi siap demo, bug bersih, presentasi siap.

| Owner | Task |
|---|---|
| All | **Bug bash session** (1-2 hari): cari & fix critical bugs |
| All | Siapkan 2-3 contoh materi demo dengan hasil berbeda (high/medium/low) |
| All | Siapkan slide presentasi + narasi |
| All | Rehearsal demo 1-2× |
| Ravi | Final UI polish, mobile responsive verification |
| Audry/Ariq/Desta | Address any final integration issues |

**Definition of Done Week 5**: demo berjalan tanpa critical error, presentasi siap.

---

## Task Breakdown Per Member

### 1. Audry — Backend Quiz Generator

**Main file**: `backend/app/services/quiz_generator.py`

**Status saat ini**: Placeholder rule-based fill-in-the-blank sudah jalan (split kalimat → pick keyword → fill blank). Output sesuai `QuizInternal` shape.

**Tasks**:
- [ ] Review placeholder code & tentukan apakah replace total atau extend
- [ ] Tentukan strategi quiz generator (rule-based, template-based, dll)
- [ ] Tentukan jumlah soal default (sekarang 5, bisa di-tweak)
- [ ] Implementasi proper di `quiz_generator.py`
- [ ] Validasi minimal panjang materi (sudah ada, bisa diperkuat)
- [ ] Siapkan 3-5 dummy materi untuk testing (variasi: sains, sosial, teknologi)
- [ ] Unit tests di `tests/test_quiz_generator.py` (minimal 5 cases)
- [ ] Dokumentasikan asumsi generator di docstring file

**Kontrak yang harus dijaga** (jangan diubah tanpa diskusi):
- Input: `material_text: str`
- Output: `QuizInternal` (`schemas/internal.py`) dengan exactly 4 options per question, satu `correct_option_index`
- Errors: raise `ApiException` dengan code dari `app/utils/errors.py`

**Reference**:
- `API.md` §4.2 (HTTP layer)
- `ARCHITECTURE.md` §6.1-6.2, §8 (data flow)
- `BRAND.md` §6 (voice & tone — kalau bikin question prompt seperti "Lengkapi kalimat berikut...")

---

### 2. Ariq — Backend Data & Analisis

**Main file**: `backend/app/services/quiz_evaluator.py`

**Status saat ini**: Placeholder standard scoring sudah jalan. Output sesuai `EvaluationResult` shape termasuk `question_results: list[QuestionResult]`.

**Tasks**:
- [ ] Review placeholder code & tentukan extension yang dibutuhkan
- [ ] Decide: pakai pandas atau cukup native Python untuk MVP
- [ ] Implementasi/extend `quiz_evaluator.py` — score, counts, per-question detail
- [ ] (Opsional) Eksplorasi analitik tambahan: time-per-question distribution, pattern detection, dll
- [ ] Unit tests di `tests/test_quiz_evaluator.py`
- [ ] Pastikan invariants di API.md §4.3 selalu hold:
  - `correct_count + wrong_count + unanswered_count === total_questions`
  - `score_percentage === round(correct_count / total_questions × 100)`

**Kontrak yang harus dijaga**:
- Input: `QuizInternal`, `list[Answer]`, `time_taken_seconds: int`
- Output: `EvaluationResult` (`schemas/internal.py`)
- Errors: raise `ApiException`

> ⚠️ **PENTING**: `EvaluationResult` adalah handoff ke 3 modul Desta. Kalau mau ubah shape-nya, sync ke Desta dulu.

**Reference**:
- `API.md` §4.3, §5.5 (HTTP & ScoreSummary)
- `ARCHITECTURE.md` §6.3, §9 (data flow + signatures)

---

### 3. Desta — Backend Logic, Insight & Recommendation

**Main files**:
- `backend/app/services/understanding_classifier.py`
- `backend/app/services/insight_engine.py`
- `backend/app/services/recommendation_engine.py`

**Status saat ini**:
- Classifier: rules dari PRD §15 sudah jalan (high/medium/low based on score + time)
- Insight engine: base templates per level (BRAND.md §7.6) sudah ada
- Recommendation engine: base templates per level (BRAND.md §7.7) sudah ada — termasuk brand callback "...lalu asah lagi."

**Tasks**:
- [ ] Review classifier thresholds — test dengan beberapa skenario, tweak kalau perlu
- [ ] Implement sub-conditions di insight_engine:
  - [ ] High score + fast time → "kamu paham dan cepat"
  - [ ] High score + slow time → "kamu paham tapi mungkin masih ragu"
  - [ ] Medium + many unanswered → "kamu skip beberapa soal"
  - [ ] Low + all answered → "kamu coba semua tapi banyak salah"
  - [ ] dll (minimal 6-8 variasi total)
- [ ] Implement sub-conditions di recommendation_engine (paralel dengan insight)
- [ ] Pastikan voice consistency (BRAND.md §6): "kamu" not "Anda", honest, calm, no patronizing
- [ ] Unit tests untuk ketiga modul
- [ ] Pastikan brand callback "asah lagi" tetap muncul di recommendation low/medium

**Kontrak yang harus dijaga**:
- Classifier input: `EvaluationResult`. Output: `UnderstandingLevel` (high/medium/low)
- Insight & Recommendation input: `UnderstandingLevel + EvaluationResult`. Output: `str` (Indonesian, 1-2 sentences)

**Reference**:
- `PRD.md` §15 (rule starting point)
- `BRAND.md` §6 (voice rules)
- `BRAND.md` §7.6-7.7 (base templates)
- `ARCHITECTURE.md` §6.3, §9

---

### 4. Ravi — Frontend React & TypeScript

**Main folder**: `frontend/src/`

**Status saat ini**: Full skeleton sudah jalan end-to-end. Pages, components, hooks, API client, theme system, i18n labels — semua sudah scaffolded.

**Tasks**:
- [ ] Polish loading states (saat generate quiz + submit)
- [ ] Polish error display (sekarang inline; pertimbangkan toast notification)
- [ ] Quiz page: tambah progress indicator ("3 dari 5 terjawab")
- [ ] Quiz page: sticky submit button
- [ ] Result page: animation pada reveal (opsional, P2-P3)
- [ ] Mobile responsive verification (test di chrome devtools mobile mode)
- [ ] Edge cases: backend offline, very long material, very long question text
- [ ] (Opsional) Frontend snapshot/component tests
- [ ] Final UI polish untuk demo

**Sudah selesai (tinggal di-verify)**:
- Pages: `HomePage`, `QuizPage`, `ResultPage` — full routing & state passing
- Components: `Layout`, `Logo`, `ThemeToggle`, `MaterialInputForm`, `QuizQuestionCard`, `QuizTimer`, `ResultSummary`, `UnderstandingBadge`, `InsightCard`, `RecommendationCard`, `ScoreChart`
- Hooks: `useTheme`, `useQuiz`, `useTimer`
- API client: `services/api.ts` (generateQuiz, submitQuiz, checkHealth)
- i18n: `utils/i18n.ts` lengkap dengan copy dari BRAND.md §7

**Reference**:
- `BRAND.md` §7 (copy library)
- `DESIGN.md` (visual tokens)
- `frontend/README.md` (setup & structure)

---

## Shared Tasks (semua minggu)

### Repository & Collaboration
- [x] Branch strategy (feat/<owner>-<topic>)
- [x] Naming convention (Conventional Commits)
- [x] Struktur folder final (sudah scaffolded)
- [ ] Issue/task tracking system (GitHub Issues atau Notion atau yang tim setuju)
- [ ] Review PR internal — tiap minggu

### Testing
- [x] Test scenario utama (sudah ada di `tests/test_routes.py`)
- [ ] Uji input kosong (sudah ada test, tinggal cover di owner module)
- [ ] Uji materi sangat pendek (idem)
- [ ] Uji generate quiz normal (dilakukan saat owner refine modulnya)
- [ ] Uji submit dengan jawaban lengkap
- [ ] Uji submit dengan jawaban sebagian
- [ ] Uji hasil kategori tinggi/sedang/rendah
- [ ] Uji integrasi frontend-backend (Week 4-5)

### Demo Preparation (Week 5)
- [ ] Menyiapkan 2–3 contoh materi demo
- [ ] Menyiapkan skenario demo dengan hasil berbeda
- [ ] Menyiapkan screenshot/video jika diperlukan
- [ ] Menyiapkan narasi presentasi
- [ ] Rehearsal

---

## Suggested Branch Naming

Convention: `<type>/<owner>-<topic>` atau `<type>/<topic>` untuk shared tasks.

- `feat/audry-quiz-generator` — Audry's main implementation
- `feat/ariq-evaluator` — Ariq's main implementation
- `feat/desta-classifier-insight-recommendation` — Desta's modules (atau pisah jadi 3 PR kalau prefer)
- `feat/ravi-frontend-polish` — Ravi's polish work
- `fix/api-contract` — bug fix di shared schemas
- `docs/readme` — dokumentasi update
- `test/integration` — shared integration tests

---

## Suggested Definition of Done

Sebuah task dianggap selesai jika:
- [ ] Fiturnya berjalan secara end-to-end (bukan cuma unit-pass)
- [ ] Tidak break flow utama (run `pytest` + manual test browser)
- [ ] Sudah diuji minimal secara manual oleh owner
- [ ] Sudah ada minimal 2-3 unit tests untuk happy path + edge case
- [ ] Sudah commit ke branch yang benar dengan Conventional Commit message
- [ ] PR sudah di-review oleh minimal 1 anggota
- [ ] Tidak ada regression di test suite (`pytest` semua pass)

---

## Priority Order

### P1 — Wajib (Week 1-4 critical path)
- [ ] Quiz generator proper (Audry)
- [ ] Quiz evaluator proper (Ariq)
- [ ] Understanding classifier proper (Desta)
- [ ] Insight & recommendation dengan sub-conditions (Desta)
- [ ] Full E2E test pass

### P2 — Penting (Week 4-5 polish)
- [ ] Frontend loading states & error handling
- [ ] Mobile responsive
- [ ] Demo materials siap
- [ ] UI polish presentable untuk demo

### P3 — Opsional (kalau ada waktu)
- [ ] Pandas analytics di evaluator (Ariq)
- [ ] Animation pada result reveal
- [ ] Frontend component tests
- [ ] Penyimpanan hasil lokal (out of MVP per PRD §22)

---

## Risks to Watch

- **Critical path slip**: kalau Audry meleset, Ariq + Desta geser. Mitigasi: daily update saat giliran main owner.
- **API contract drift**: ubahan di `schemas/internal.py` tanpa sync = breakage. Mitigasi: review PR yang sentuh schema dengan extra hati-hati.
- **Integrasi terlambat**: integrasi muncul masalah di Week 4-5 → demo berisiko. Mitigasi: integration test (`test_generate_then_submit_full_flow`) HARUS pass setiap PR backend.
- **Quiz generator menghasilkan soal lemah**: rule-based ada batasan. Mitigasi: Audry siapkan dummy materi yang well-structured untuk demo.
- **Scope creep**: tambah fitur out-of-MVP. Mitigasi: P3 strict, semua addition perlu diskusi tim.

---

## Weekly Check-in Questions

Tiap minggu (sync meeting), jawab:

- Apa yang sudah selesai minggu ini?
- Apa blocker terbesar? (siapa bisa bantu?)
- Apakah ada perubahan scope?
- Apakah API contract / internal types masih konsisten?
- Apa target konkret minggu berikutnya?
- Apakah main owner minggu depan sudah unblocked?

---

## Cara Memulai (TL;DR)

1. **Clone repo**: `git clone https://github.com/ravi-arnan/TempaCapstoneProject.git`
2. **Baca docs critical**: `API.md` + `ARCHITECTURE.md` §6 + §10 + section spesifik kamu di TASKS.md
3. **Setup environment**: lihat `frontend/README.md` dan `backend/README.md`
4. **Sign-off internal types**: tick checklist di `API.md` §12, `ARCHITECTURE.md` §14, `BRAND.md` §11
5. **Tunggu giliran (sequential)**: lihat critical path. Saat bukan giliran kamu jadi main owner, kerjakan support tasks per "Milestone Mingguan" di atas.
6. **Daily update saat giliran main owner**: post progress di chat tim — apa yang done hari ini, blocker, ETA.

— Ravi
