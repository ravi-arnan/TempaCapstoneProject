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

## 🔵 PART 2: DL Setup (modified — fine-tuning skipped)

> **Update 2026-05-08**: fine-tuning attempt gagal karena fp16 NaN issue (T5 known instability). Decision: ship MVP dengan base pretrained `Wikidepia/IndoT5-base` (tanpa fine-tune), dengan quality check di wrapper yang fall back ke rule-based saat DL output garbage.
>
> Detail di [`/ML.md` §3 "MVP decision: SKIP fine-tuning"](../../ML.md).

### Yang perlu dilakukan untuk DL setup (sekarang minimal)

#### Step 1: Verify HF account ready
Token HF kamu masih valid (dari setup earlier). Tidak perlu push apapun karena kita pakai base model `Wikidepia/IndoT5-base` yang sudah public.

#### Step 2: Test inference pakai base model
```bash
cd backend
source .venv/bin/activate
python -m ml.generator.inference
```

Expected behavior:
- **Best case**: model output beberapa pertanyaan yang masuk akal (T5 base kadang nangkep prompt "buat pertanyaan:" dan output question-like text)
- **Realistic case**: banyak output garbage (`aaaaa` atau paraphrase). Quality check di `inference.py` akan filter ini, dan wrapper di `app/services/quiz_generator.py` akan fall back ke rule-based generator.

#### Step 3: Test full backend
```bash
uvicorn app.main:app --reload
```

Lalu:
```bash
curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  --max-time 90 \
  -d '{"material_text": "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di kloroplas dan menghasilkan oksigen sebagai produk samping."}'
```

Cek log backend — harusnya muncul **salah satu** dari:
- `INFO ml.generator: Loaded IndoT5 ...` + `INFO quiz_generator: DL path produced 5 questions` → DL ada output yang lolos quality check ✓
- `INFO ml.generator: skipping low-quality output ...` (multiple) + `WARNING quiz_generator: DL path produced only N questions, falling back` → DL output garbage, fallback ke rule-based ✓

**Keduanya OK** untuk demo. Yang penting endpoint return valid quiz.

### Optional: re-attempt fine-tuning post-MVP

Kalau setelah demo ada waktu dan mau improve quality DL, edit notebook:

1. Buka `backend/ml/generator/notebooks/train_quiz_generator.ipynb`
2. Cari cell `Seq2SeqTrainingArguments`
3. Ganti `fp16=True` → `bf16=True` (T4 support bf16 stable untuk T5)
4. Re-run notebook di Colab
5. Push ke HF Hub
6. Update `_MODEL_NAME` di `inference.py`

Tapi ini **tidak perlu untuk MVP**.

---

## ✅ Definition of Done

### Frontend
- [ ] Loading state polish dengan progress messages
- [ ] Frontend timeout configured (90s untuk generateQuiz)
- [ ] Quiz progress indicator
- [ ] Sticky submit button
- [ ] Mobile responsive verified
- [ ] Error states tested

### DL Setup (revised — no fine-tuning)
- [x] HF account setup + token generated
- [x] Decision: skip fine-tuning, use base IndoT5 (per ML.md §3)
- [ ] Verify base model loading works (`python -m ml.generator.inference`)
- [ ] Verify backend `/quiz/generate` returns valid quiz (DL or fallback)
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
