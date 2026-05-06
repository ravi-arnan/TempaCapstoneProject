# 🟢 Tugas Audry — Quiz Generator (Integration & Quality)

Halo Audry! Tugasmu adalah **integrate Ravi's trained DL model** ke backend, **improve question quality**, dan **make sure the wrapper works end-to-end**.

> **Catatan**: bagian Colab + Hugging Face training di-handle Ravi karena dia lebih familiar dengan workflow-nya. Kamu fokus ke integrasi + kualitas + testing — tetap bagian penting karena ini yang **menentukan apa yang user lihat**.

## 📌 Big picture

```
Ravi train model di Colab → push ke HF Hub
                                  │
                                  ▼  (handoff: Ravi kasih kamu URL)
            Audry (kamu): integrate ke backend
                                  │
                ┌────────────────────────────┐
                ▼                            ▼
      backend/ml/generator/      backend/app/services/
        inference.py              quiz_generator.py
       (DL inference logic)       (wrapper: validate, fallback)
                                  │
                                  ▼
                              Frontend
```

Jobs kamu:
1. **Plug in** model URL ke `inference.py`
2. **Improve distractor logic** (yang bikin opsi B, C, D)
3. **Test end-to-end** dari `/quiz/generate` endpoint
4. **Manual review** quality output sebelum demo

---

## ⚙️ Setup awal (sekali aja, ~15 menit)

### 1. Clone repo & install backend

```bash
git clone https://github.com/ravi-arnan/TempaCapstoneProject.git
cd TempaCapstoneProject/backend

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Catatan**: install pertama akan download `torch` (~700MB) — sabar, ini sekali aja.

### 2. Quick verify

```bash
python -c "from transformers import T5Tokenizer; print('OK')"
# Should print: OK
```

### 3. Tunggu handoff dari Ravi

Sebelum kamu bisa mulai, **tunggu Ravi finish training**. Indikasi siap:
- Ravi post di chat tim: "DL training selesai, model di HF Hub: `<URL>`"
- URL HF accessible (bisa kamu cek dengan buka URL-nya di browser)

Sambil nunggu, kamu bisa kerjain **Step 1 baca docs** di bawah.

---

## 🚀 Step 1: Pahami codebase

Buka file-file ini sebelum coding:

1. **`backend/ml/generator/inference.py`** — DL inference logic. Ini yang kamu modify.
2. **`backend/app/services/quiz_generator.py`** — wrapper yang panggil inference.py
3. **`backend/app/schemas/internal.py`** — definisi `QuestionInternal` dan `QuizInternal`
4. **`/ML.md` §3** — strategi DL lengkap, kenapa T5
5. **`/API.md` §4.2** — HTTP contract endpoint kamu

Kunci yang harus kamu pahami:

- Inference flow: `material_text` → split sentences → generate question per sentence pakai T5 → extract distractors → return `QuestionInternal`
- Fallback flow: kalau model fail load atau inference gagal, wrapper jatuh ke rule-based fill-in-the-blank
- Contract output: setiap question butuh **exactly 4 options** + `correct_option_index` 0-3

---

## 🚀 Step 2: Plug in Ravi's model

Setelah Ravi handoff URL, edit `backend/ml/generator/inference.py` line ~30:

```python
# Ganti baris ini:
_MODEL_NAME = "Wikidepia/IndoT5-base"

# Jadi (pakai username HF Ravi):
_MODEL_NAME = "ravi-arnan-irianto/indot5-quizgen-asahlagi"  # ← Ravi's HF repo
```

### Test: model bisa load

```bash
cd backend
source .venv/bin/activate
python -m ml.generator.inference
```

Expected output (request pertama lambat karena download model ~1GB):
```
[INFO] ml.generator: Loading IndoT5 from ravi-arnan-irianto/indot5-quizgen-asahlagi ...
[INFO] ml.generator: Loaded IndoT5 from HF Hub: ... (params=220M)
Generating quiz from sample material (XX chars)...

Q1: Apa peran utama klorofil dalam fotosintesis?
 A.  Menyimpan glukosa
 B. ✓ Menyerap cahaya matahari
 C.  Menghasilkan oksigen
 D.  Memecah air
...
```

Kalau output muncul + grammatical → model loaded, integration sukses ✅

---

## 🚀 Step 3: Improve distractor logic

Sekarang ini bagian yang **paling impactful untuk kualitas quiz**. Logic yang ada di `inference.py` simple — extract longest non-stopword keywords dari material sebagai distractor.

Buka `backend/ml/generator/inference.py`. Cari function `generate()` di sekitar line 130+.

### Current behavior (simple keyword extraction)

```python
keywords_pool = _extract_keywords(material_text)
# untuk tiap question:
correct = max(passage_keywords, key=len)        # longest word di passage
distractors = rng.sample(distractor_pool, 3)    # 3 random keywords lain
```

### Masalah dengan approach ini

- Distractor random keyword bisa jadi **tidak relevan** dengan pertanyaan
- "Correct answer" cuma longest word, bukan answer yang benar dari T5
- Tidak ada validation: distractor mungkin **terlalu mirip** correct answer

### Improvements yang bisa kamu lakukan

#### Option A: Length-similar distractors (mudah, ~30 menit)
Distractors yang panjangnya mirip sama correct answer biar lebih plausible:

```python
def _pick_similar_length_distractors(correct: str, pool: list[str], n: int = 3) -> list[str]:
    """Pick distractors with similar length to correct answer."""
    target_len = len(correct)
    candidates = sorted(
        [w for w in pool if w.lower() != correct.lower()],
        key=lambda w: abs(len(w) - target_len)  # closest length first
    )
    return candidates[:n] if len(candidates) >= n else candidates
```

#### Option B: Same part-of-speech distractors (medium, ~1-2 jam)
Pakai library NLP simple seperti `nltk` untuk classify POS, pick distractors dengan POS sama:

```python
# pip install nltk (sudah di requirements? cek)
import nltk
nltk.download('punkt')

def _same_pos_distractors(correct: str, pool: list[str], n: int = 3) -> list[str]:
    correct_pos = nltk.pos_tag([correct])[0][1]
    candidates = []
    for word in pool:
        if word.lower() == correct.lower():
            continue
        if nltk.pos_tag([word])[0][1] == correct_pos:
            candidates.append(word)
    return candidates[:n]
```

#### Option C: Embedding-based (advanced, opsional)
Pakai sentence embeddings untuk pick distractors yang **semantically similar** tapi tidak identik:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def _semantic_distractors(correct: str, pool: list[str], n: int = 3) -> list[str]:
    embeddings = model.encode([correct] + pool)
    correct_emb, pool_embs = embeddings[0], embeddings[1:]
    similarities = (pool_embs @ correct_emb)
    # Pick "moderately similar" — too similar means same word, too different means random
    sweet_spot = sorted(zip(pool, similarities), key=lambda x: -x[1])[5:5 + n]
    return [w for w, _ in sweet_spot]
```

**Rekomendasi**: mulai dengan **Option A** (paling cepat, observable improvement). Kalau waktu masih ada, coba Option B atau C.

### Test improvement

Generate 10 quizzes dari materi yang berbeda. Manual review:
- Apakah distractor-nya plausible? (orang awam bisa kira-kira "mungkin benar")
- Apakah distractor jelas berbeda dari correct answer? (bukan duplicate)
- Apakah panjang option mirip-mirip? (kalau satu jauh lebih pendek, suspicious)

---

## 🚀 Step 4: Improve correct answer extraction

Saat ini correct answer = `max(passage_keywords, key=len)` (longest word di passage). Ini **tidak akurat** karena T5 generate question yang mungkin bertanya tentang kata SPESIFIK, bukan kata terpanjang.

### Improvement: extract correct answer dari T5 output

T5 bisa di-prompt untuk generate **(question, answer) pair**, bukan cuma question:

```python
# Tambah function baru di inference.py
def _generate_question_and_answer(passage: str) -> tuple[str, str]:
    """Generate question + answer pair from passage."""
    prompt = f"buat pertanyaan dan jawaban: {passage}"
    inputs = _tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = _model.generate(**inputs, max_length=128, num_beams=4)
    full_output = _tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Parse "Pertanyaan: ... Jawaban: ..." format
    if "Jawaban:" in full_output:
        parts = full_output.split("Jawaban:")
        question = parts[0].replace("Pertanyaan:", "").strip()
        answer = parts[1].strip()
        return question, answer
    return full_output, ""
```

> ⚠️ **Note**: ini butuh model di-train dengan prompt format ini. Kalau Ravi train pake prompt `"buat pertanyaan: {passage}"`, model tidak akan tau format Q&A. Discuss dengan Ravi: apakah retrain dengan format Q&A combined, atau pakai approach berbeda.

**Alternative simpler**: extract answer dari TyDiQA's `answer_text` field saat training. Ravi bisa adjust notebook untuk include ini.

---

## 🚀 Step 5: Test full flow

### 5a: Inference standalone

```bash
python -m ml.generator.inference
```

Cek outputnya, manual evaluate quality.

### 5b: Backend full flow

```bash
# Terminal 1
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait sampai `Application startup complete`. Catat **first request latency** (cold start).

```bash
# Terminal 2 — first request
time curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  --max-time 90 \
  -d '{"material_text": "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung di stroma."}'
```

Expected:
- First request: 25-50s
- Second + onwards: 15-40s
- Quiz output: 5 questions, masing-masing ada 4 options, format JSON valid

### 5c: Full submit cycle

```bash
# Setelah dapat quiz_id dari response generate:
QUIZ_ID="<paste quiz_id dari response>"

curl -X POST http://localhost:8000/quiz/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"quiz_id\": \"$QUIZ_ID\",
    \"answers\": [
      {\"question_id\": 1, \"selected_option_index\": 0},
      {\"question_id\": 2, \"selected_option_index\": 1},
      {\"question_id\": 3, \"selected_option_index\": 2},
      {\"question_id\": 4, \"selected_option_index\": 0},
      {\"question_id\": 5, \"selected_option_index\": 0}
    ],
    \"time_taken_seconds\": 240
  }"
```

Expected: response dengan score, level, insight, recommendation. Itu integration confirmed.

---

## 🚀 Step 6: Tulis unit tests

Buat `backend/tests/test_quiz_generator.py`:

```python
import pytest
from app.services import quiz_generator
from app.schemas.internal import QuizInternal
from app.utils.errors import ApiException


def test_too_short_raises():
    with pytest.raises(ApiException) as exc:
        quiz_generator.generate_quiz("Pendek banget.")
    assert exc.value.code == "MATERIAL_TOO_SHORT"


def test_normal_material_returns_quiz():
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    assert isinstance(quiz, QuizInternal)
    assert len(quiz.questions) >= 3
    assert all(len(q.options) == 4 for q in quiz.questions)
    assert all(0 <= q.correct_option_index <= 3 for q in quiz.questions)


def test_questions_have_unique_ids():
    material = "..." # any normal length material
    quiz = quiz_generator.generate_quiz(material)
    ids = [q.id for q in quiz.questions]
    assert len(ids) == len(set(ids)), "Question IDs must be unique"


def test_options_are_distinct():
    material = "..." # normal material
    quiz = quiz_generator.generate_quiz(material)
    for q in quiz.questions:
        assert len(set(q.options)) == 4, f"Q{q.id}: duplicate options"


def test_fallback_on_dl_failure(monkeypatch):
    """Even if DL model unavailable, generator should fall back to rule-based."""
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)

    material = "..."  # normal material
    quiz = quiz_generator.generate_quiz(material)
    assert isinstance(quiz, QuizInternal)
    assert len(quiz.questions) >= 3
```

Run:
```bash
pytest backend/tests/test_quiz_generator.py -v
```

---

## 🚀 Step 7: Branch + PR

```bash
git checkout -b feat/audry-quiz-generator-integration
git add backend/ml/generator/inference.py \
        backend/app/services/quiz_generator.py \
        backend/tests/test_quiz_generator.py
git commit -m "feat(generator): integrate Ravi's fine-tuned IndoT5 + improve distractor logic"
git push origin feat/audry-quiz-generator-integration

# Buka PR di GitHub, request review dari Ravi/Ariq/Desta
```

---

## ✅ Definition of Done

Tugasmu selesai kalau:

- [ ] `_MODEL_NAME` di `inference.py` sudah point ke Ravi's HF model
- [ ] `python -m ml.generator.inference` jalan tanpa error, output grammatical
- [ ] Distractor logic improved (minimum Option A, lebih bagus B atau C)
- [ ] Manual quality review: ≥4/5 quiz dari 3 sample materials acceptable
- [ ] Backend `/quiz/generate` return real DL questions (cek log: "DL path produced N questions")
- [ ] Minimum 4 unit tests pass (including fallback test)
- [ ] PR merged ke `main`

---

## 🛠️ Common problems + solusi

### "Model load error: 401 Unauthorized"
Model HF Ravi mungkin private. Tanya Ravi untuk make public, atau set up HF token di backend env.

### "Model load error: model not found"
Cek `_MODEL_NAME` di inference.py — typo di username Ravi? Cek URL di browser dulu untuk verify.

### "Out of memory saat inference"
T5 base masih cukup besar untuk 8GB RAM. Solutions:
- Ganti model lebih kecil: `Wikidepia/IndoT5-small` (cek apakah Ravi punya yang lebih kecil)
- Add `low_cpu_mem_usage=True` saat load model

### "Generated questions tidak grammatical / weird"
Ini bukan bug kamu — ini quality issue dari training. Discuss dengan Ravi:
- Mungkin training perlu lebih banyak epochs
- Atau dataset perlu di-filter lebih ketat

Sambil nunggu fix, kamu bisa fokus improve distractor logic.

### "Inference sangat lambat (> 60s per quiz)"
Tweak inference parameters di `inference.py`:
```python
_NUM_BEAMS = 1   # greedy decoding (faster, slightly lower quality)
_MAX_OUTPUT_LENGTH = 48   # shorter questions
```

### "Stuck di hal lain"
Tanya di chat tim:
```
Stuck di Step [X]
Error: [paste error]
Sudah dicoba: [apa aja]
```

---

## 📚 Resources

- **`/ML.md` §3** — strategi DL lengkap, kenapa pilih IndoT5
- **`/ARCHITECTURE.md` §5b** — kenapa `ml/` dipisah dari `app/`
- **`/API.md` §4.2** — HTTP contract endpoint kamu
- **`/backend/ml/README.md`** — practical guide ML layer
- **`/backend/ml/generator/inference.py`** — current implementation
- **HF Transformers Generation docs** — https://huggingface.co/docs/transformers/main_classes/text_generation
- **NLTK POS tagging** (Option B) — https://www.nltk.org/book/ch05.html

---

## 🎯 Bonus (optional, post-MVP)

Kalau MVP kamu selesai cepat:

- **Question difficulty estimator**: tag questions sebagai easy/medium/hard berdasarkan vocab complexity
- **Topic classification**: pakai TF-IDF untuk grouped questions per topik
- **Distractor diversity check**: pastikan 4 options cover variety (bukan semua synonyms)
- **Performance optimization**: profile inference, identify bottleneck

Tapi ini semua **nice to have**, fokus dulu integrasi + kualitas dasar.

---

## 🤝 Coordination dengan Ravi

Karena pekerjaanmu downstream dari Ravi:
- **Sebelum Ravi handoff**: kamu standby, baca docs, pahami codebase
- **Setelah Ravi handoff**: kamu prioritize integrate dulu (Step 2), lalu improve quality (Step 3-4)
- **Kalau ada quality issue dari model**: file issue ke Ravi dengan sample bad output, bisa di-iterasi

Selamat ngerjain Audry! 🚀
