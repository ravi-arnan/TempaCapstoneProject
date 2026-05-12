/**
 * Indonesian-default copy library — mirrors BRAND.md §7.
 * Source of truth: /BRAND.md
 *
 * Components MUST NOT inline copy strings. Always import from here.
 */

import type { UnderstandingLevel } from "@/types/result";

// ============================================================================
// Page titles & headers (BRAND.md §7.1)
// ============================================================================

export const PAGE_TITLES = {
  home: "Asahlagi — Asah lagi sampai paham.",
  quiz: "Kuis sedang berlangsung",
  result: "Hasil — Asahlagi",
} as const;

export const HOMEPAGE = {
  hero: "Asah lagi sampai paham.",
  subtitle:
    "Tempel materi belajarmu, kerjakan kuis otomatis, dan ukur tingkat pemahamanmu.",
} as const;

// ============================================================================
// Button labels (BRAND.md §7.2)
// ============================================================================

export const BUTTON_LABELS = {
  homePrimary: "Mulai Mengasah",
  homePrimaryReturn: "Asah Lagi",
  homeLoading: "Sedang menyiapkan kuis...",
  submitQuiz: "Selesai & Lihat Hasil",
  skipQuestion: "Lewati",
  prevQuestion: "Sebelumnya",
  nextQuestion: "Lanjut",
  resultRetry: "Asah Lagi",
  resetAll: "Mulai Ulang",
  backToHome: "Kembali ke Beranda",
} as const;

// ============================================================================
// Empty states (BRAND.md §7.3)
// ============================================================================

export const EMPTY_STATES = {
  materialPlaceholder: "Tempel materi belajarmu di sini...",
  materialHelp:
    "Minimal 100 karakter. Bisa berupa ringkasan, artikel, atau bab buku.",
  urlPlaceholder: "https://contoh.com/artikel-pelajaran",
  urlHelp:
    "Tempel link artikel pelajaran. Sistem akan mengambil isi artikelnya secara otomatis.",
  pdfHelp:
    "Upload file PDF (max 10 MB). Sistem akan ekstrak teks dari PDF — pastikan PDF berisi teks, bukan scan/gambar.",
  pdfDropzone: "Klik atau seret file PDF ke sini",
  quizLoading: "Sedang menyusun pertanyaan...",
  submitProcessing: "Menganalisis hasil...",
} as const;

// ============================================================================
// Source type labels (for HomePage tabs)
// ============================================================================

export const SOURCE_TYPE_LABELS = {
  text: "Teks",
  url: "Tautan Web",
  pdf: "File PDF",
} as const;

// ============================================================================
// Loading progress messages — rotated during DL inference (~9s wait)
// ============================================================================

export const LOADING_PROGRESS_MESSAGES = [
  "Membaca materimu...",
  "Menyusun pertanyaan...",
  "Memeriksa kualitas pertanyaan...",
  "Hampir selesai...",
] as const;

// ============================================================================
// Error messages (BRAND.md §7.4 + API.md §6)
// ============================================================================

export const ERROR_MESSAGES: Record<string, string> = {
  MATERIAL_EMPTY: "Materi belum ada. Tempel teks materimu dulu, ya.",
  MATERIAL_TOO_SHORT:
    "Materinya terlalu pendek. Tambahkan minimal 100 karakter agar sistem bisa membuat kuis.",
  MATERIAL_TOO_LONG:
    "Materinya terlalu panjang. Maksimal 20.000 karakter — coba ringkas dulu bagian intinya.",
  QUIZ_GENERATION_FAILED:
    "Gagal membuat kuis. Coba materi lain atau ulangi sebentar lagi.",
  PDF_INVALID:
    "File PDF tidak bisa diproses. Pastikan file PDF valid dan tidak rusak.",
  PDF_EMPTY:
    "PDF tidak punya teks yang bisa diekstrak. Mungkin PDF berupa scan/gambar — coba ketik ulang materinya.",
  PDF_TOO_SHORT:
    "Teks PDF terlalu pendek. Coba PDF dengan konten lebih banyak.",
  PDF_TOO_LONG:
    "PDF terlalu panjang. Sistem ambil 20.000 karakter pertama saja.",
  URL_INVALID: "URL tidak valid. Pastikan dimulai dengan http:// atau https://",
  URL_FETCH_FAILED:
    "Gagal mengambil halaman dari URL. Pastikan URL bisa diakses publik.",
  URL_EMPTY_CONTENT:
    "Halaman tidak punya artikel yang bisa diambil. Mungkin butuh login atau isinya kebanyakan gambar.",
  URL_TOO_SHORT:
    "Artikel di URL terlalu pendek. Coba artikel yang lebih panjang.",
  URL_TOO_LONG:
    "Artikel terlalu panjang. Sistem ambil 20.000 karakter pertama saja.",
  QUIZ_NOT_FOUND:
    "Kuis tidak ditemukan atau sudah kedaluwarsa. Mulai ulang dari halaman utama.",
  ANSWERS_LENGTH_MISMATCH:
    "Ada ketidaksesuaian jumlah jawaban. Coba mulai kuis dari awal.",
  INVALID_OPTION_INDEX: "Pilihan jawaban tidak valid. Coba pilih ulang.",
  INVALID_QUESTION_ID: "Soal tidak ditemukan dalam kuis. Coba mulai ulang.",
  INVALID_TIME: "Waktu pengerjaan tidak valid. Coba mulai ulang.",
  EVALUATION_FAILED:
    "Gagal menganalisis hasil kuis. Coba kirim ulang sebentar lagi.",
  INTERNAL_ERROR: "Ada hambatan dari sisi kami. Coba lagi sebentar.",
};

export function getErrorMessage(code: string | undefined, fallback?: string) {
  if (code && ERROR_MESSAGES[code]) return ERROR_MESSAGES[code];
  return fallback ?? ERROR_MESSAGES.INTERNAL_ERROR!;
}

// ============================================================================
// Result page dynamic headers (BRAND.md §7.5)
// ============================================================================

export const RESULT_HEADERS: Record<
  UnderstandingLevel,
  { headline: string; subhead: string }
> = {
  high: {
    headline: "Pemahamanmu mantap.",
    subhead: "Konsep utama materi sudah kamu kuasai.",
  },
  medium: {
    headline: "Pemahamanmu sudah baik, masih bisa lebih tajam.",
    subhead: "Beberapa konsep masih perlu diteguhkan.",
  },
  low: {
    headline: "Yuk asah lagi.",
    subhead: "Materi ini perlu dibaca ulang dengan fokus.",
  },
};

// ============================================================================
// Status badge labels (BRAND.md §7.9)
// ============================================================================

export const UNDERSTANDING_LEVEL_LABEL: Record<UnderstandingLevel, string> = {
  high: "TINGGI",
  medium: "SEDANG",
  low: "RENDAH",
};

// ============================================================================
// Stat labels (BRAND.md §7.8)
// ============================================================================

export const STAT_LABELS = {
  score: "SKOR",
  time: "WAKTU",
  correct: "BENAR",
  wrong: "SALAH",
  unanswered: "TIDAK DIJAWAB",
} as const;

// ============================================================================
// Helpers
// ============================================================================

export function formatSeconds(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
