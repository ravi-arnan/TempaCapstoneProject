# 📋 Tugas Tim TP-G005 — Asahlagi

Halo tim! 👋 Folder ini berisi tugas masing-masing anggota dalam format step-by-step yang gampang diikutin.

## File mana yang harus kamu baca?

| Anggota | File | Fokus utama |
|---|---|---|
| Ravi Arnan Irianto | [`ravi.md`](./ravi.md) | Frontend polish + DL Training (Colab + HF) |
| Audry Nabila Anastasya | [`audry.md`](./audry.md) | Quiz Generator integration + quality |
| Ariq Marwan Permana | [`ariq.md`](./ariq.md) | Quiz Evaluator (skor, jumlah, dll) |
| Desta Anandhika R. M. | [`desta.md`](./desta.md) | ML Classifier + Insight + Recommendation |

**Cuma baca file kamu**. Tidak perlu baca file orang lain (kecuali penasaran).

> **Architecture update (2026-05-09)**: DL inference (Quiz Generator) sekarang di **cloud Hugging Face Space**, bukan local. Backend cuma manggil Space via HTTP. Implication: tim **tidak perlu install torch/transformers locally** — backend ringan (~450MB venv).
>
> Ravi sudah deploy Space di `https://raviarnan-asahlagi-quizgen.hf.space`. Audry tinggal set `HF_SPACE_URL` di `.env` dan focus ke integration + quality improvement (distractor logic dll).
>
> Fine-tuning di-skip untuk MVP (fp16 NaN issue). Detail di [`/ML.md`](../ML.md).

---

## Aturan main

### 🟢 Yang harus dilakukan sebelum mulai coding

1. **Clone repo & setup environment** (dijelasin di file kamu masing-masing)
2. **Baca dokumen kamu** di folder ini sampai paham
3. **Sign-off** di checklist berikut (centang `[x]` pas kamu sudah baca + setuju):
   - `API.md` §12 (HTTP contract)
   - `ARCHITECTURE.md` §14 (sistem arsitektur)
   - `BRAND.md` §11 (brand identity & copy)
   - `ML.md` §9 (strategi ML/DL)

### 🟡 Selama coding

1. **Branch sendiri**: `feat/<nama-kamu>-<topik>` — contoh: `feat/audry-quiz-generator-dl`
2. **Conventional commits**: `feat:`, `fix:`, `docs:`, `test:` di awal commit message
3. **Daily update di chat tim** kalau kamu lagi giliran "main owner" minggu itu (lihat TASKS.md untuk timeline)
4. **PR review wajib** dari minimal 1 anggota lain sebelum merge ke `main`
5. **Kalau ubah `backend/app/schemas/internal.py`** (`EvaluationResult` dll), HARUS sync ke tim dulu — itu integration boundary

### 🔴 Yang harus dihindari

- Jangan ngubah file yang bukan owner-mu tanpa diskusi
- Jangan langsung push ke `main`
- Jangan skip review PR
- Jangan invent copy/text sendiri — pakai dari `BRAND.md` §7

---

## Cara minta bantuan

Kalau stuck:

1. **Baca docs lengkap** dulu (link ada di file tugas masing-masing)
2. **Tanya di chat tim** dengan format:
   ```
   Stuck di: [step yang mana]
   Error: [paste error message]
   Sudah dicoba: [apa aja yang sudah dicoba]
   ```
3. **Minta sync call** kalau perlu screen share

---

## Timeline ringkas (5 minggu)

| Minggu | Fokus | Main owner |
|---|---|---|
| 1 | Setup + sync + baca docs | Semua |
| 2 | DL training (Colab + HF) **Ravi** ⭐ → handoff → Audry integrate | **Ravi** + **Audry** |
| 3 | Data evaluator + ML Classifier | **Ariq** ⭐ + **Desta** ⭐ |
| 4 | Insight & Recommendation + integration | **Desta** ⭐ |
| 5 | Polish + demo | Semua |

Detail timeline lengkap: [TASKS.md](../TASKS.md)

---

## Selamat ngerjain! 🚀

Kalau ada pertanyaan general (tidak spesifik tugas), tanya di chat tim. Kalau pertanyaan spesifik tugas kamu, lihat dulu file tugasmu — biasanya jawabannya di sana.
