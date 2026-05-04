# PRD — Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data

## 1. Ringkasan Produk

Produk ini adalah aplikasi pembelajaran yang membantu mahasiswa mengukur tingkat pemahaman mereka setelah mempelajari materi digital seperti modul, ringkasan, atau artikel. Sistem menerima materi berbentuk teks, menghasilkan kuis secara otomatis, mencatat hasil pengerjaan pengguna, lalu menampilkan tingkat pemahaman, insight singkat, dan rekomendasi belajar lanjutan. [file:42]

Proyek ini berada dalam tema **Digital Education & Skill Development** dan dikembangkan sebagai capstone project oleh tim **TP-G005** dengan empat anggota aktif dari learning path AI. [file:42]

## 2. Latar Belakang Masalah

Dalam proses pembelajaran mandiri, mahasiswa sering membaca materi tanpa mengetahui apakah mereka benar-benar memahami isi pembelajaran tersebut. Di sisi lain, pembuatan kuis sebagai alat evaluasi masih banyak dilakukan secara manual dan tidak selalu tersedia setelah materi dipelajari. [file:42]

Akibatnya, ada gap antara proses belajar dan proses evaluasi. Pengguna dapat mengonsumsi materi, tetapi tidak memperoleh umpan balik yang cukup untuk mengetahui tingkat penguasaan, kelemahan, atau langkah belajar berikutnya. [file:42]

## 3. Problem Statement

Bagaimana membangun sistem sederhana yang dapat mengubah materi pembelajaran menjadi kuis secara otomatis, menganalisis hasil pengerjaan kuis, lalu mendeteksi tingkat pemahaman pengguna beserta insight dan rekomendasi belajar dalam satu alur yang terintegrasi. [file:42]

## 4. Research Questions

1. Bagaimana sistem dapat mengubah materi pembelajaran menjadi kuis secara otomatis. [file:42]
2. Bagaimana mendeteksi tingkat pemahaman mahasiswa berdasarkan hasil kuis. [file:42]
3. Bagaimana memberikan insight dan rekomendasi belajar berdasarkan hasil analisis data. [file:42]

## 5. Tujuan Produk

### Goals

- Membantu mahasiswa mengevaluasi pemahaman setelah membaca materi.
- Mengurangi kebutuhan pembuatan kuis manual.
- Menyediakan hasil evaluasi yang lebih informatif daripada skor saja.
- Mengintegrasikan proses input materi, pembuatan kuis, pengerjaan kuis, analisis, dan rekomendasi dalam satu aplikasi. [file:42]

### Non-goals

- Tidak mendukung input materi kompleks seperti PDF, video, atau audio pada MVP. [file:42]
- Tidak membangun sistem login, autentikasi, atau manajemen akun yang kompleks pada MVP. [file:42]
- Tidak menggunakan model AI/ML kompleks sebagai komponen utama analisis pada MVP. [file:42]
- Tidak membangun learning management system penuh seperti manajemen kelas, forum, atau penugasan multi-user.

## 6. Target Pengguna

### Primary User
- Mahasiswa yang belajar secara mandiri menggunakan materi digital berbentuk teks. [file:42]

### Secondary User
- Pengguna umum atau pelajar lain yang ingin menguji pemahaman dari materi bacaan singkat.

## 7. Nilai Utama Produk

Produk ini tidak hanya memberikan nilai akhir, tetapi juga:
- Menghasilkan kuis dari materi yang dimasukkan pengguna.
- Menunjukkan performa pengerjaan seperti skor dan waktu.
- Mengklasifikasikan tingkat pemahaman menjadi kategori sederhana.
- Memberikan insight yang menjelaskan kemungkinan alasan hasil tersebut.
- Memberikan rekomendasi belajar yang dapat ditindaklanjuti. [file:42]

## 8. Asumsi Produk

- Input materi diberikan dalam bentuk teks atau hasil copy-paste.
- Quiz generator pada MVP menggunakan pendekatan sederhana berbasis aturan atau ekstraksi informasi dasar dari teks. [file:42]
- Analisis pemahaman menggunakan rule-based logic, bukan model AI kompleks. [file:42]
- Backend dibangun dengan Python untuk logika quiz dan analisis, sedangkan frontend dibangun dengan React + TypeScript sesuai proposal. [file:42]

## 9. User Flow

### Flow utama
1. Pengguna membuka aplikasi.
2. Pengguna menempelkan materi pembelajaran dalam bentuk teks.
3. Sistem memproses teks dan menghasilkan kuis.
4. Pengguna mengerjakan kuis dalam antarmuka web.
5. Sistem menghitung hasil seperti jumlah benar, jumlah salah, skor, dan waktu pengerjaan.
6. Sistem menganalisis hasil dengan aturan sederhana.
7. Sistem menampilkan tingkat pemahaman, insight, rekomendasi, dan grafik sederhana. [file:42]

## 10. Fitur Inti MVP

### 10.1 Input Materi
Pengguna dapat memasukkan materi pembelajaran dalam bentuk teks melalui text area.

**Acceptance criteria**
- Pengguna dapat paste teks minimal 1 paragraf.
- Sistem menolak input kosong.
- Sistem menampilkan pesan validasi jika teks terlalu pendek.

### 10.2 Quiz Generator
Sistem menghasilkan kuis otomatis dari materi yang dimasukkan.

**Scope MVP**
- Format soal pilihan ganda.
- Jumlah soal dapat dibuat tetap, misalnya 5–10 soal.
- Soal dibangun dengan pendekatan sederhana, bukan generasi AI kompleks. [file:42]

**Acceptance criteria**
- Setelah materi dikirim, sistem menampilkan daftar soal.
- Setiap soal memiliki pertanyaan, beberapa opsi jawaban, dan satu jawaban benar.
- Soal tetap relevan dengan isi materi input.

### 10.3 Halaman Pengerjaan Kuis
Pengguna menjawab kuis pada halaman interaktif.

**Acceptance criteria**
- Pengguna bisa memilih jawaban satu per soal.
- Pengguna bisa submit jawaban setelah semua atau sebagian soal dijawab.
- Sistem merekam total jawaban benar, salah, dan waktu pengerjaan.

### 10.4 Hasil Kuis
Sistem menampilkan hasil dasar pengerjaan kuis.

**Acceptance criteria**
- Sistem menampilkan skor akhir.
- Sistem menampilkan jumlah benar dan salah.
- Sistem menampilkan durasi pengerjaan.
- Sistem menampilkan ringkasan performa.

### 10.5 Deteksi Tingkat Pemahaman
Sistem mengklasifikasikan tingkat pemahaman pengguna.

**Kategori awal**
- Tinggi
- Sedang
- Rendah

**Input analisis**
- Persentase skor
- Waktu pengerjaan
- Pola salah atau jumlah soal yang tidak dijawab

**Acceptance criteria**
- Setiap hasil kuis memiliki satu kategori tingkat pemahaman.
- Logika klasifikasi terdokumentasi dan konsisten.
- Hasil klasifikasi muncul langsung di halaman hasil.

### 10.6 Insight Otomatis
Sistem menjelaskan kenapa pengguna mendapat kategori tertentu.

**Contoh pendekatan**
- Skor tinggi dan waktu stabil → pemahaman baik.
- Skor sedang dengan waktu lama → kemungkinan memahami sebagian, tetapi masih ragu.
- Skor rendah dengan banyak salah → materi belum dipahami secara cukup.

**Acceptance criteria**
- Insight ditampilkan dalam bahasa yang mudah dipahami.
- Insight selaras dengan data hasil kuis.
- Insight tidak hanya mengulang skor mentah.

### 10.7 Rekomendasi Belajar
Sistem memberikan saran langkah selanjutnya.

**Contoh rekomendasi**
- Ulangi membaca bagian inti materi.
- Fokus ke konsep yang paling banyak salah.
- Kerjakan kuis ulang setelah review singkat.
- Gunakan ringkasan poin penting sebelum mengulang tes.

**Acceptance criteria**
- Setiap kategori pemahaman memiliki rekomendasi yang sesuai.
- Rekomendasi bersifat praktis dan dapat dilakukan pengguna.

### 10.8 Grafik Sederhana
Sistem menampilkan visualisasi sederhana dari hasil pengerjaan.

**Contoh**
- Bar chart benar vs salah
- Donut/pie chart persentase hasil
- Indikator kategori pemahaman

**Acceptance criteria**
- Grafik tampil di halaman hasil.
- Data grafik konsisten dengan hasil analisis.

## 11. Kebutuhan Fungsional

- Sistem harus menerima input materi dalam bentuk teks. [file:42]
- Sistem harus dapat mengubah materi menjadi kuis sederhana. [file:42]
- Sistem harus menyediakan halaman pengerjaan kuis.
- Sistem harus menghitung skor, benar, salah, dan waktu pengerjaan. [file:42]
- Sistem harus menentukan tingkat pemahaman berdasarkan rule tertentu. [file:42]
- Sistem harus menampilkan insight otomatis. [file:42]
- Sistem harus menampilkan rekomendasi belajar. [file:42]
- Sistem harus menampilkan grafik sederhana. [file:42]

## 12. Kebutuhan Non-Fungsional

### Usability
- Antarmuka sederhana dan mudah dipahami oleh pengguna pertama.
- Alur utama dapat diselesaikan tanpa panduan panjang.

### Performance
- Waktu generate kuis untuk input teks normal sebaiknya tidak lebih dari beberapa detik pada lingkungan demo.
- Hasil analisis ditampilkan segera setelah submit.

### Reliability
- Validasi input harus mencegah error umum seperti teks kosong.
- Sistem harus tetap berjalan untuk materi pendek hingga sedang.

### Maintainability
- Arsitektur modular antara generator kuis, evaluator hasil, engine insight, dan frontend.
- Rule klasifikasi dapat diubah tanpa membongkar seluruh sistem.

## 13. Batasan Sistem

- Input hanya berupa teks, bukan PDF, DOCX, video, atau link. [file:42]
- Quiz generation masih sederhana dan tidak mengejar kualitas setara platform komersial berbasis LLM. [file:42]
- Analisis memakai metode sederhana tanpa model AI kompleks sebagai inti sistem. [file:42]
- Tidak ada sistem login dan database kompleks pada versi awal. [file:42]

## 14. Arsitektur Teknis

### Frontend
- React
- TypeScript [file:42]

### Backend
- Python untuk logika quiz dan analisis data. [file:42]

### Library/Tools
- Pandas untuk pengolahan data. [file:42]
- Scikit-learn opsional bila dibutuhkan untuk eksplorasi analisis tambahan. [file:42]
- GitHub untuk version control. [file:42]
- VS Code sebagai development environment. [file:42]

### Arsitektur logis
- Frontend menerima input materi dan menampilkan hasil.
- Backend menerima materi, memproses generator kuis, menyimpan hasil sementara, menjalankan analisis, lalu mengembalikan hasil ke frontend.
- Komponen analisis terdiri dari scoring, classification rules, insight generator, dan recommendation rules.

## 15. Logika Analisis Awal

Berikut rule awal yang bisa dipakai sebagai MVP:

### Variabel
- `score_percentage`
- `completion_time`
- `correct_count`
- `wrong_count`
- `unanswered_count`

### Rule kategori
- **Tinggi**: skor tinggi, kesalahan rendah, waktu masih wajar.
- **Sedang**: skor menengah atau skor cukup baik tetapi waktu terlalu lama.
- **Rendah**: skor rendah atau banyak jawaban salah/tidak dijawab.

### Rule insight
- Jika skor tinggi dan waktu efisien → pengguna cenderung memahami materi dengan baik.
- Jika skor sedang dan waktu lama → pengguna memahami sebagian, tetapi masih memerlukan penguatan.
- Jika skor rendah → pengguna perlu meninjau ulang konsep utama materi.

### Rule rekomendasi
- Tinggi → lanjut ke kuis lanjutan atau materi berikutnya.
- Sedang → ulangi bagian penting dan kerjakan kuis ulang.
- Rendah → baca ulang materi, fokus pada poin dasar, lalu ulangi evaluasi.

## 16. Metrik Keberhasilan MVP

### Product metrics
- Pengguna berhasil membuat kuis dari materi teks.
- Pengguna berhasil menyelesaikan kuis tanpa error.
- Sistem menampilkan hasil, kategori, insight, dan rekomendasi secara lengkap.

### Quality metrics
- Relevansi soal terhadap materi dinilai layak oleh tim penguji internal.
- Hasil klasifikasi konsisten terhadap rule yang sudah didefinisikan.
- Tidak ada blocker bug pada flow utama demo.

## 17. Skenario Demo

### Skenario 1
- Pengguna memasukkan materi singkat.
- Sistem menghasilkan 5 soal pilihan ganda.
- Pengguna mengerjakan kuis.
- Sistem menampilkan skor 80, kategori tinggi, insight, dan rekomendasi.

### Skenario 2
- Pengguna memasukkan materi lain.
- Pengguna mengerjakan kuis dengan banyak jawaban salah.
- Sistem menampilkan kategori rendah dan rekomendasi review.

## 18. Timeline Pengembangan

### Minggu 1
- Finalisasi ide dan desain sistem.
- Finalisasi requirement produk.
- Setup environment React dan backend Python. [file:42]

### Minggu 2
- Implementasi input materi.
- Implementasi quiz generator sederhana. [file:42]

### Minggu 3
- Implementasi halaman pengerjaan kuis.
- Implementasi penyimpanan dan pengolahan hasil kuis. [file:42]

### Minggu 4
- Implementasi analisis hasil.
- Implementasi fitur insight dan rekomendasi. [file:42]

### Minggu 5
- Integrasi frontend dan backend.
- Testing, debugging, dan finalisasi presentasi. [file:42]

## 19. Pembagian Tugas Tim

| Anggota | Peran | Tanggung Jawab |
|---|---|---|
| Audry Nabila Anastasya | Backend — Quiz Generator | Mengembangkan fitur perubahan materi menjadi kuis [file:42] |
| Ariq Marwan Permana | Backend — Data & Analisis | Mengolah hasil kuis dan menghitung performa pengguna [file:42] |
| Desta Anandhika Rajendra Maheswara | Backend — Logic & Insight | Membuat aturan deteksi pemahaman, insight, dan rekomendasi [file:42] |
| Ravi Arnan Irianto | Frontend — React & TypeScript | Mengembangkan UI dan integrasi frontend-backend [file:42] |

## 20. Risiko dan Mitigasi

### Kompleksitas sistem terlalu tinggi
Sistem yang terlalu luas dapat menghambat progres dan menurunkan kualitas. Mitigasinya adalah menjaga scope tetap kecil, modular, dan fokus pada fitur inti. [file:42]

### Keterbatasan waktu
Waktu 4–5 minggu dapat menyebabkan fitur tidak selesai jika scope melebar. Mitigasinya adalah milestone mingguan, prioritas MVP, dan evaluasi progres rutin. [file:42]

### Kekurangan data atau contoh materi
Kurangnya bahan uji dapat memengaruhi kualitas quiz generation dan analisis. Mitigasinya adalah memakai data dummy, materi sintetis, dan hasil kuis pengguna sebagai bahan evaluasi awal. [file:42]

### Koordinasi tim kurang efektif
Miskomunikasi dapat memperlambat integrasi. Mitigasinya adalah pembagian peran jelas, meeting mingguan, dan tracking progres bersama. [file:42]

## 21. MVP Acceptance Checklist

- [ ] Pengguna dapat memasukkan materi teks.
- [ ] Sistem dapat menghasilkan kuis otomatis.
- [ ] Pengguna dapat mengerjakan kuis sampai submit.
- [ ] Sistem menghitung skor dan waktu.
- [ ] Sistem menampilkan kategori pemahaman.
- [ ] Sistem menampilkan insight otomatis.
- [ ] Sistem menampilkan rekomendasi belajar.
- [ ] Sistem menampilkan grafik sederhana.
- [ ] Frontend dan backend terintegrasi dengan baik.
- [ ] Flow demo berjalan tanpa error kritis.

## 22. Future Enhancements

- Dukungan file PDF atau dokumen.
- Analisis berbasis topik atau per submateri.
- Riwayat pengerjaan kuis.
- Dashboard perkembangan pengguna.
- Login dan penyimpanan data persisten.
- Peningkatan kualitas quiz generation dengan pendekatan NLP/LLM.
