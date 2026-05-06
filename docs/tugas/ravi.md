# 🔵 Tugas Ravi — Frontend + DL Training

Halo Ravi (yourself, hi!) 👋. Tugasmu **dual-role**:
1. **Frontend** — kamu owner UI, sudah ada skeleton end-to-end, tinggal polish
2. **DL Training** — handle Colab + Hugging Face setup karena lebih familiar dengan Hugging Face workflow

Setelah model ter-train dan ter-push ke HF, kamu **handoff URL ke Audry** untuk integrate ke inference.py + testing.

---

## 📌 Big picture role split

```
                     RAVI (kamu)                       AUDRY
                          │                              │
              ┌───────────┴────────────┐                 │
              ▼                        ▼                 ▼
    Frontend polish              DL Training       DL Integration
    (existing skeleton)         (Colab + HF Hub)   (inference.py +
                                                     distractor logic +
                                                     testing)
                                          │            ▲
                                          └─ HF URL ───┘
```

**Handoff point**: setelah training selesai, kamu kasih Audry URL HF model + dataset stats. Audry yang implement bagian backend integration + run unit tests.

---

## 🔵 PART 1: Frontend Polish

Skeleton frontend sudah lengkap — pages, components, hooks, theme system, API client, i18n labels — semua jalan end-to-end. Tugas kamu: **polish biar siap demo**.

### Setup awal (sekali aja)

```bash
cd /home/ravi/Projects/TempaCapstoneProject/frontend
npm install
cp .env.example .env.development
npm run dev    # buka http://localhost:5173
```

### Tasks frontend

#### 1. Loading state untuk DL inference (HIGH PRIORITY)
File: `src/pages/HomePage.tsx`

DL inference butuh 15-40s untuk generate quiz. Sekarang cuma button disabled — UX kurang bagus untuk wait selama itu. Tambah:

- **Skeleton loader** atau **animated progress** saat `generating === true`
- **Progress messages** yang berubah tiap ~5s biar user tidak terasa "stuck":
  ```
  [0-5s]    "Membaca materimu..."
  [5-15s]   "Menyusun pertanyaan..."
  [15-30s]  "Hampir selesai..."
  [30-40s]  "Memeriksa kualitas pertanyaan..."
  ```
- Pertimbangkan: countdown timer "estimasi 30 detik" biar user expect wait

Sample implementation:
```tsx
const [loadingMessage, setLoadingMessage] = useState("Membaca materimu...");
useEffect(() => {
  if (!generating) return;
  const messages = [
    "Membaca materimu...",
    "Menyusun pertanyaan...",
    "Hampir selesai...",
    "Memeriksa kualitas pertanyaan...",
  ];
  let idx = 0;
  const interval = setInterval(() => {
    idx = (idx + 1) % messages.length;
    setLoadingMessage(messages[idx]);
  }, 5000);
  return () => clearInterval(interval);
}, [generating]);
```

#### 2. Frontend timeout
File: `src/services/api.ts`

Browser default fetch timeout sekitar 30s. Untuk DL endpoint yang bisa 40s+, tambah AbortController dengan timeout 90s untuk `generateQuiz`:

```typescript
async function postJson<TReq, TRes>(path: string, body: TReq, timeoutMs = 60000): Promise<TRes> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    // ... rest of logic
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiException({ detail: "Permintaan terlalu lama. Coba lagi." }, 408);
    }
    throw err;
  }
}

// generateQuiz pakai timeout 90s
export function generateQuiz(req: QuizGenerateRequest) {
  return postJson<...>("/quiz/generate", req, 90000);
}
```

#### 3. Quiz progress indicator
File: `src/pages/QuizPage.tsx`

Tambah indikator "X dari Y soal terjawab" di header quiz page. Currently user tidak tau progress mereka.

```tsx
const answeredCount = answers.filter(a => a.selected_option_index !== null).length;
// di JSX:
<div className="text-sm text-text-muted">
  {answeredCount} dari {quiz.total_questions} soal terjawab
</div>
```

#### 4. Sticky submit button
File: `src/pages/QuizPage.tsx`

Sekarang button submit di bawah list — kalau quiz panjang user harus scroll. Make sticky di bottom screen:

```tsx
<div className="sticky bottom-0 bg-bg-page border-t border-border-standard p-4">
  <button>Selesai & Lihat Hasil</button>
</div>
```

#### 5. Mobile responsive verification
- Test di Chrome DevTools mobile mode (iPhone 12, Pixel 5, iPad)
- Pastikan:
  - Logo + theme toggle tidak overlap
  - Textarea readable di mobile
  - Buttons tap-target minimal 44×44px
  - Quiz options stack vertically dengan spacing cukup

#### 6. Error states polish
- Backend offline → friendly message + retry button
- Network slow → tetap show progress, jangan switch ke error
- Network timeout → "Coba lagi" dengan suggested action

---

## 🔵 PART 2: DL Training (taken over from Audry)

Karena kamu lebih familiar dengan Hugging Face workflow, kamu yang handle bagian ini. Setelah model ter-published ke HF, kasih URL ke Audry untuk integrate.

### Pre-requisites

- Akun Hugging Face (gratis): https://huggingface.co/join
- Akses Google Colab (gratis): https://colab.research.google.com/
- Browser modern (Chrome/Firefox)

### Step 1: Setup HF account

1. Daftar di https://huggingface.co/join
2. Verifikasi email
3. Generate access token:
   - https://huggingface.co/settings/tokens
   - Klik **"New token"**
   - Nama: `asahlagi-training`
   - Type: **Write** (penting!)
   - Save token (hidden setelah ini, simpan baik-baik)

### Step 2: Buka Colab notebook

Cara paling cepat (setelah scaffolding di-push ke main):

```
https://colab.research.google.com/github/ravi-arnan/TempaCapstoneProject/blob/main/backend/ml/generator/notebooks/train_quiz_generator.ipynb
```

Atau manual upload:
1. https://colab.research.google.com/
2. `File → Upload notebook`
3. Upload `backend/ml/generator/notebooks/train_quiz_generator.ipynb`

### Step 3: Aktifkan GPU

`Runtime → Change runtime type → T4 GPU → Save`.

### Step 4: Run all cells

Klik `Runtime → Run all`, atau run cell per cell pakai `Shift+Enter`.

| Cell | Aksi | Durasi |
|---|---|---|
| Install deps | pip install transformers, datasets, dll | ~2 menit |
| HF login | paste access token | instant (manual) |
| Load TyDiQA-id | download Indonesian QA dataset | ~1 menit |
| Load IndoT5 base | download `Wikidepia/IndoT5-base` (~1GB) | ~3 menit |
| Preprocess | tokenize dataset | ~1 menit |
| Setup args | training arguments | instant |
| **Train** | fine-tune 3 epochs | **1-2 jam** ⏰ |
| Eval | manual review 3 sample passages | ~30 detik |
| Push to HF | upload model | ~5 menit |

**Saat training (Cell #7)**: bisa kamu tinggal makan/kerja lain. Tab Colab WAJIB tetap aktif (jangan close, bisa minimize). Tips anti-disconnect:

```javascript
// Buka DevTools (F12) → Console → paste & enter:
function ClickConnect(){console.log("Working"); document.querySelector("colab-connect-button").click()} setInterval(ClickConnect,60000)
```

### Step 5: Edit username sebelum push

Di cell terakhir, ada line:
```python
HF_USERNAME = "audry-asahlagi"     # ← REPLACE
```

Ganti dengan **username HF kamu sendiri**. Misal username kamu `ravi-arnan-irianto`:
```python
HF_USERNAME = "ravi-arnan-irianto"
```

Run cell. Setelah selesai, model kamu live di:
```
https://huggingface.co/ravi-arnan-irianto/indot5-quizgen-asahlagi
```

### Step 6: Manual quality review

Sebelum handoff ke Audry, review minimal 10 generated questions di cell sebelumnya. Kriteria:
- ✅ Pertanyaan grammatical Bahasa Indonesia
- ✅ Pertanyaan relevant ke passage input
- ✅ Question mark di akhir
- ❌ Bukan summary atau paraphrase
- ❌ Bukan kalimat random

Kalau >70% pertanyaan acceptable, model bisa di-handoff. Kalau di bawah, rerun training dengan epoch lebih banyak (5 instead of 3) atau learning rate lebih rendah (5e-5 instead of 1e-4).

### Step 7: Handoff ke Audry

Post di chat tim:

```
@Audry — DL training selesai. Modelmu siap di:

Model URL: https://huggingface.co/<username>/indot5-quizgen-asahlagi
Final eval BLEU: <X.XX>
Sample questions: [paste 5-10 dari Cell #8 evaluation]

Tugas kamu lanjut:
1. Edit backend/ml/generator/inference.py line 30:
   _MODEL_NAME = "<username>/indot5-quizgen-asahlagi"
2. Test: python -m ml.generator.inference
3. Improve distractor logic (currently keyword-based, bisa lebih smart)
4. Unit tests + PR

Detail: docs/tugas/audry.md
```

---

## ✅ Definition of Done

### Frontend
- [ ] Loading state polish dengan progress messages
- [ ] Frontend timeout configured (90s untuk generateQuiz)
- [ ] Quiz progress indicator
- [ ] Sticky submit button
- [ ] Mobile responsive verified
- [ ] Error states tested

### DL Training
- [ ] HF account setup + token generated
- [ ] Colab notebook completed (all cells run sukses)
- [ ] Model published to HF Hub: `<username>/indot5-quizgen-asahlagi`
- [ ] Manual quality review: ≥7/10 questions acceptable
- [ ] Handoff message posted ke Audry dengan URL + sample
- [ ] PR untuk frontend changes merged

---

## 🛠️ Common problems + solusi

### Frontend

#### "Loading state masih flash too quick saat development"
Backend di local mungkin lebih cepat (kalau model cached). Test dengan throttling:
```ts
// Add artificial delay untuk testing UX
await new Promise(r => setTimeout(r, 20000));
```

#### "Tailwind class baru tidak ke-pickup"
Restart `npm run dev`. Tailwind only scans files saat dev server start.

### DL Training

#### "Colab disconnect saat training"
Pakai script anti-idle JS di atas. Atau upgrade ke Colab Pro ($10/bulan) kalau training sering disconnect.

#### "Out of memory di T4"
Reduce batch size dari 8 → 4 di training arguments cell. Training jadi lebih lama tapi tidak crash.

#### "BLEU score sangat rendah (< 0.10)"
Indikasi model tidak belajar. Coba:
- Lower learning rate: `1e-4 → 5e-5`
- More epochs: `3 → 5`
- Cek tokenizer cocok dengan dataset language

#### "Push HF gagal: 401 Unauthorized"
Token expired atau Read-only. Generate new token dengan **Write** permissions.

### Stuck di hal lain

Sebagai dev paling senior, kamu yang bantuin orang lain. Kalau kamu sendiri stuck di bagian DL, search HF docs / Stack Overflow / tanya di [HF Discord](https://discord.gg/hugging-face-879548962464493619).

---

## 📚 Resources

### Frontend
- `/BRAND.md` §7 — copy library
- `/DESIGN.md` — visual tokens
- `/frontend/README.md` — setup & structure
- React Router docs: https://reactrouter.com/en/main

### DL Training
- `/ML.md` §3 — DL strategy lengkap
- `/backend/ml/README.md` — practical ML guide
- HF Transformers docs: https://huggingface.co/docs/transformers
- TyDiQA: https://huggingface.co/datasets/tydiqa
- T5 paper: https://arxiv.org/abs/1910.10683

---

## 🎯 Suggested timeline

Asumsi dimulai Week 1:

| Hari | Frontend | DL Training |
|---|---|---|
| Mon-Tue | Setup + loading state | Setup HF account + open Colab |
| Wed | Quiz progress + sticky button | Run training (1-2h Colab) |
| Thu | Mobile responsive | Manual quality review + push HF |
| Fri | Error states polish | Handoff ke Audry |

Setelah handoff (mid Week 2), kamu fokus full ke frontend polish + integration testing dengan real DL backend.

---

Selamat ngerjain! Karena kamu juga memimpin team ini secara teknis, kasih kabar di chat saat handoff supaya orang lain bisa proceed.
