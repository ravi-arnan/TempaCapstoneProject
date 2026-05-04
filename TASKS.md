# TASKS.md

## Project
**Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data**  
**Team ID:** TP-G005 [file:42]

## Objective
Membangun aplikasi web sederhana yang dapat:
- menerima materi pembelajaran dalam bentuk teks,
- menghasilkan kuis otomatis,
- memfasilitasi pengerjaan kuis,
- menganalisis hasil,
- menampilkan tingkat pemahaman, insight, rekomendasi, dan grafik sederhana. [file:42]

---

## Team Members

| Nama | ID | Role |
|---|---|---|
| Audry Nabila Anastasya | AIC161BX0012 | Backend - Quiz Generator |
| Ariq Marwan Permana | AIC012B6Y0004 | Backend - Data & Analisis |
| Desta Anandhika Rajendra Maheswara | AIC183B6Y0048 | Backend - Logic, Insight & Recommendation |
| Ravi Arnan Irianto | AIC014B6Y0008 | Frontend - React & TypeScript | [file:42]

---

## Working Rules

- Fokus pada MVP, jangan menambah fitur di luar scope tanpa diskusi tim.
- Prioritaskan flow end-to-end yang berjalan.
- Semua task besar harus punya owner yang jelas.
- Gunakan branch terpisah untuk fitur utama.
- Lakukan sync minimal 1 kali per minggu. [file:42]

---

## MVP Deliverables

- [ ] Input materi teks
- [ ] Quiz generator sederhana
- [ ] Halaman pengerjaan kuis
- [ ] Penghitungan skor dan waktu
- [ ] Klasifikasi tingkat pemahaman
- [ ] Insight otomatis
- [ ] Rekomendasi belajar
- [ ] Grafik hasil sederhana
- [ ] Integrasi frontend dan backend
- [ ] Demo siap presentasi [file:42]

---

## Milestone Mingguan

### Minggu 1 — Finalisasi dan Setup
- [ ] Finalisasi kebutuhan sistem
- [ ] Finalisasi flow aplikasi
- [ ] Setup repository GitHub
- [ ] Setup frontend React + TypeScript
- [ ] Setup backend Python
- [ ] Menentukan API contract awal
- [ ] Menentukan format data quiz dan result [file:42]

### Minggu 2 — Input Materi dan Quiz Generator
- [ ] Membuat form input materi
- [ ] Validasi input kosong/terlalu pendek
- [ ] Implementasi quiz generator sederhana
- [ ] Menentukan struktur question object
- [ ] Menyiapkan dummy material untuk testing [file:42]

### Minggu 3 — Quiz Session dan Result Processing
- [ ] Membuat halaman pengerjaan kuis
- [ ] Menangani state jawaban user
- [ ] Menambahkan timer pengerjaan
- [ ] Submit jawaban ke backend
- [ ] Hitung skor, benar, salah, dan waktu [file:42]

### Minggu 4 — Analisis, Insight, Recommendation
- [ ] Implementasi rule klasifikasi pemahaman
- [ ] Implementasi generator insight
- [ ] Implementasi generator rekomendasi
- [ ] Menyiapkan chart sederhana
- [ ] Uji konsistensi hasil analisis [file:42]

### Minggu 5 — Integrasi dan Finalisasi
- [ ] Integrasi penuh frontend-backend
- [ ] Perbaikan bug utama
- [ ] Uji semua flow utama
- [ ] Rapikan UI
- [ ] Finalisasi bahan demo/presentasi [file:42]

---

## Task Breakdown Per Member

## 1. Audry — Backend Quiz Generator

### Main Responsibility
Mengembangkan fitur untuk mengubah materi menjadi kuis. [file:42]

### Tasks
- [ ] Menentukan strategi quiz generator berbasis rule sederhana
- [ ] Menentukan jumlah soal default untuk MVP
- [ ] Menentukan format output soal:
  - [ ] id
  - [ ] question
  - [ ] options
  - [ ] correct_answer
- [ ] Implementasi service `quiz_generator.py`
- [ ] Menangani input materi teks
- [ ] Menambahkan validasi minimal panjang materi
- [ ] Menyediakan dummy dataset materi untuk pengujian
- [ ] Menulis unit test sederhana untuk generator
- [ ] Dokumentasikan asumsi generator

### Dependencies
- Perlu sinkron dengan frontend untuk bentuk data soal
- Perlu sinkron dengan backend evaluator untuk `question_id` dan `correct_answer`

---

## 2. Ariq — Backend Data & Analisis

### Main Responsibility
Mengolah hasil kuis dan menghitung performa pengguna. [file:42]

### Tasks
- [ ] Menentukan schema hasil submit quiz
- [ ] Implementasi evaluator jawaban
- [ ] Menghitung:
  - [ ] correct_count
  - [ ] wrong_count
  - [ ] unanswered_count
  - [ ] score_percentage
  - [ ] time_taken
- [ ] Menyiapkan formatter output hasil kuis
- [ ] Menyiapkan data untuk visualisasi chart
- [ ] Opsional: eksplorasi penggunaan pandas/scikit-learn bila dibutuhkan [file:42]
- [ ] Menulis test untuk evaluasi hasil
- [ ] Sinkronisasi response JSON dengan frontend

### Dependencies
- Butuh format soal dari Audry
- Butuh rule klasifikasi dari Desta
- Butuh kebutuhan chart dari Ravi

---

## 3. Desta — Backend Logic, Insight & Recommendation

### Main Responsibility
Membuat aturan deteksi pemahaman serta insight dan rekomendasi. [file:42]

### Tasks
- [ ] Menentukan kategori pemahaman:
  - [ ] Tinggi
  - [ ] Sedang
  - [ ] Rendah
- [ ] Menentukan rule klasifikasi berdasarkan:
  - [ ] score_percentage
  - [ ] time_taken
  - [ ] jumlah salah
  - [ ] unanswered_count
- [ ] Implementasi `understanding_classifier.py`
- [ ] Implementasi `insight_engine.py`
- [ ] Implementasi `recommendation_engine.py`
- [ ] Menulis template insight untuk tiap kategori
- [ ] Menulis template rekomendasi belajar untuk tiap kategori
- [ ] Uji konsistensi rule
- [ ] Dokumentasikan logika if-else yang digunakan

### Dependencies
- Butuh output evaluasi dari Ariq
- Butuh final display structure dari Ravi

---

## 4. Ravi — Frontend React & TypeScript

### Main Responsibility
Mengembangkan tampilan aplikasi dan integrasi dengan backend. [file:42]

### Tasks
- [ ] Setup project React + TypeScript
- [ ] Menentukan struktur folder frontend
- [ ] Membuat halaman utama input materi
- [ ] Membuat halaman quiz
- [ ] Membuat halaman hasil
- [ ] Membuat komponen:
  - [ ] MaterialInputForm
  - [ ] QuizQuestionCard
  - [ ] QuizTimer
  - [ ] ResultSummary
  - [ ] UnderstandingBadge
  - [ ] InsightCard
  - [ ] RecommendationCard
  - [ ] ScoreChart
- [ ] Integrasi API generate quiz
- [ ] Integrasi API submit quiz
- [ ] Menangani state loading/error/success
- [ ] Menyusun UI yang sederhana dan presentable
- [ ] Menyesuaikan response backend ke tampilan

### Dependencies
- Butuh API contract dari semua backend owner
- Perlu sinkron cepat soal field response final

---

## Shared Tasks

### Repository & Collaboration
- [ ] Membuat branch strategy
- [ ] Menentukan naming convention
- [ ] Menentukan struktur folder final
- [ ] Menentukan issue/task tracking system
- [ ] Review PR internal

### Testing
- [ ] Menyusun test scenario utama
- [ ] Uji input kosong
- [ ] Uji materi sangat pendek
- [ ] Uji generate quiz normal
- [ ] Uji submit dengan jawaban lengkap
- [ ] Uji submit dengan jawaban sebagian
- [ ] Uji hasil kategori tinggi/sedang/rendah
- [ ] Uji integrasi frontend-backend

### Demo Preparation
- [ ] Menyiapkan 2–3 contoh materi demo
- [ ] Menyiapkan skenario demo dengan hasil berbeda
- [ ] Menyiapkan screenshot/video jika diperlukan
- [ ] Menyiapkan narasi presentasi

---

## Suggested Branch Naming

- `feat/material-input`
- `feat/quiz-generator`
- `feat/quiz-session`
- `feat/result-analysis`
- `feat/insight-recommendation`
- `feat/frontend-results`
- `fix/api-contract`
- `docs/readme`

---

## Suggested Definition of Done

Sebuah task dianggap selesai jika:
- [ ] fiturnya berjalan
- [ ] tidak merusak flow utama
- [ ] sudah diuji minimal secara manual
- [ ] sudah commit ke branch yang benar
- [ ] siap di-review oleh anggota lain

---

## Priority Order

### P1 — Wajib
- [ ] Input materi
- [ ] Generate quiz
- [ ] Kerjakan quiz
- [ ] Hitung hasil
- [ ] Tampilkan kategori, insight, dan rekomendasi

### P2 — Penting
- [ ] Chart sederhana
- [ ] Validasi input dan error handling
- [ ] UI yang rapi untuk demo

### P3 — Opsional
- [ ] Penyimpanan hasil lokal
- [ ] Percobaan analisis tambahan
- [ ] Penyempurnaan tampilan

---

## Risks to Watch

- Scope creep
- API contract berubah di tengah jalan
- Integrasi terlambat
- Rule analisis tidak konsisten
- Quiz generator menghasilkan soal yang terlalu lemah [file:42]

---

## Weekly Check-in Questions

- Apa yang sudah selesai minggu ini?
- Apa blocker terbesar?
- Apakah ada perubahan scope?
- Apakah API contract masih konsisten?
- Apa target konkret minggu berikutnya?
