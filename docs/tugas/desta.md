# 🟢 Tugas Desta — ML Classifier + Insight + Recommendation

Halo Desta! Tugasmu **paling banyak file** (3 modul) tapi semua relatif manageable. Kamu kerjain:
1. **ML Classifier** — train sklearn Random Forest untuk klasifikasi tingkat pemahaman (high/medium/low)
2. **Insight Engine** — generate insight text Indonesian based on hasil
3. **Recommendation Engine** — generate rekomendasi belajar Indonesian

## 📌 Big picture

Setelah Ariq compute `EvaluationResult`, **kamu** yang menentukan:
- Tingkat pemahaman user (Tinggi / Sedang / Rendah) — pakai **ML model**
- Insight text yang menjelaskan _kenapa_ — pakai template + sub-conditions
- Rekomendasi langkah selanjutnya — pakai template + sub-conditions

```
Ariq's EvaluationResult
       ↓
Desta's classifier (ML)        ← Tugas #1
       ↓
UnderstandingLevel (high/medium/low)
       ↓
   ┌─────────────────────┐
   ↓                     ↓
Insight engine       Recommendation engine
(Tugas #2)           (Tugas #3)
   ↓                     ↓
"Kamu paham..."     "Lanjut ke materi..."
```

---

## ⚙️ Setup awal (sekali aja, ~5 menit)

### 1. Clone repo & install backend

```bash
git clone https://github.com/ravi-arnan/TempaCapstoneProject.git
cd TempaCapstoneProject/backend

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Catatan**: install ringan (~450MB venv) — sklearn + numpy + pandas. **Tidak ada torch/transformers** karena DL inference di cloud (Audry's domain). Kamu murni pakai sklearn untuk classifier.

### 2. Quick verify

```bash
python -c "import sklearn, joblib; print('sklearn:', sklearn.__version__, '| joblib:', joblib.__version__)"
# Should print: sklearn: 1.5.2 | joblib: 1.4.2
```

---

## 🚀 Tugas #1: Train ML Classifier

### Step 1.1: Pahami yang sudah ada

Buka folder `backend/ml/classifier/`. Sudah ada 3 file:

```
backend/ml/classifier/
├── data_generation.py   # generate synthetic training data
├── train.py             # train sklearn Random Forest
└── inference.py         # load model + predict
```

**Plus** placeholder rule-based di `backend/app/services/understanding_classifier.py`.

### Step 1.2: Run training script

Cara paling simple:

```bash
cd backend
source .venv/bin/activate
python -m ml.classifier.train
```

Ini akan:
1. Generate 10,000 synthetic samples (dengan rule-based labels + 5% noise)
2. Split 80/20 train/test
3. Train Random Forest (n_estimators=100, max_depth=10)
4. Print accuracy + classification report + feature importances
5. Save model ke `backend/ml/classifier/artifacts/classifier.pkl`

Output expected (angka bisa beda dikit karena random):
```
Generating synthetic dataset...
Total samples: 10000
Label distribution:
  high  : 3289 (32.9%)
  low   : 3354 (33.5%)
  medium: 3357 (33.6%)
Score range: [0.0, 100.0], mean=50.1
Time range:  [60, 1800]s, mean=929s

Splitting train/test...
  Train: 8000 samples
  Test:  2000 samples

Training RandomForestClassifier(n=100, max_depth=10)...
  Training done.

==================================================
Test set evaluation
==================================================
Accuracy: 0.9420 (94.20%)

Classification report:
              precision    recall  f1-score
        high      0.96      0.94      0.95
      medium      0.92      0.94      0.93
         low      0.95      0.95      0.95

Feature importances:
  score_percentage          0.5103
  time_taken_seconds        0.2837
  wrong_count               0.1325
  unanswered_count          0.0735

Saved model to: backend/ml/classifier/artifacts/classifier.pkl
Artifact size: 1234.5 KB
```

**Target accuracy**: ≥ 85%. Kalau di atas 95% itu wajar (synthetic data dengan noise 5% memang predictable). Kalau di bawah 85%, ada bug — tanya di chat.

### Step 1.3: Verify inference jalan

```bash
python -m ml.classifier.inference
```

Expected output:
```
  features=[95.0, 200.0, 0.0, 0.0] → high  (expected: high)
  features=[60.0, 500.0, 2.0, 0.0] → medium  (expected: medium)
  features=[20.0, 400.0, 4.0, 2.0] → low  (expected: low)
```

### Step 1.4: Commit `.pkl` artifact

File `classifier.pkl` itu output trained model. Kecil (~1-2MB), commit langsung ke repo:

```bash
git add backend/ml/classifier/artifacts/classifier.pkl
git commit -m "feat(classifier): commit trained Random Forest model"
```

> **Catatan**: file ini perlu di-commit karena backend lain (Ravi, Audry, Ariq) butuh untuk testing. Tanpa file ini, classifier akan fallback ke rule-based.

### Step 1.5 (opsional): Tweak data_generation.py

Kalau kamu mau coba scenario berbeda (e.g., classifier yang lebih strict di "high" level), edit `backend/ml/classifier/data_generation.py`:

```python
HIGH_SCORE_THRESHOLD = 80      # ← bisa naikin ke 85 atau 90
MEDIUM_SCORE_THRESHOLD = 50
NOISE_RATE = 0.05               # ← bisa naikin ke 0.10 untuk lebih realistic noise
```

Lalu re-run `python -m ml.classifier.train` untuk retrain.

---

## 🚀 Tugas #2: Insight Engine

### Step 2.1: Pahami yang sudah ada

Buka `backend/app/services/insight_engine.py`. Sudah ada **base templates** dari `BRAND.md` §7.6:

```python
_BASE_TEMPLATES: dict[UnderstandingLevel, str] = {
    UnderstandingLevel.HIGH: "Skor tinggi dengan waktu pengerjaan efisien menunjukkan kamu menguasai konsep utama materi.",
    UnderstandingLevel.MEDIUM: "Kamu memahami sebagian besar materi, tapi ada beberapa konsep yang masih perlu diteguhkan.",
    UnderstandingLevel.LOW: "Banyak konsep dasar yang masih perlu dipelajari ulang sebelum kamu lanjut ke materi berikutnya.",
}
```

### Step 2.2: Tambah sub-conditions

**Tugas kamu**: extend dengan minimal 6-8 variasi total. Berikut idenya — sesuaikan voice dengan `BRAND.md` §6 (tone: honest, encouraging tanpa cheesy, calm, casual-professional dengan "kamu").

```python
def generate_insight(
    level: UnderstandingLevel,
    eval_result: EvaluationResult,
) -> str:
    score = eval_result.score_percentage
    time = eval_result.time_taken_seconds
    unanswered = eval_result.unanswered_count
    total = eval_result.total_questions

    # Threshold "fast time": 60s per question = baseline
    fast = time <= total * 60
    slow = time > total * 90

    if level == UnderstandingLevel.HIGH:
        if fast:
            return "Skor tinggi dengan waktu pengerjaan efisien menunjukkan kamu menguasai konsep utama materi."
        else:
            return "Skor kamu tinggi, tapi waktu pengerjaan agak lama — mungkin masih ada bagian yang bikin kamu ragu."

    if level == UnderstandingLevel.MEDIUM:
        if unanswered > total * 0.3:   # > 30% unanswered
            return "Kamu skip beberapa soal — coba lebih confident di pengerjaan berikutnya."
        if slow:
            return "Kamu memahami sebagian, tapi waktu pengerjaan menunjukkan kamu masih sering ragu."
        return "Kamu memahami sebagian besar materi, tapi ada beberapa konsep yang masih perlu diteguhkan."

    # LOW
    if unanswered > total * 0.5:        # > 50% unanswered
        return "Sebagian besar soal tidak kamu jawab — kamu perlu baca ulang materi sebelum mengerjakan kuis lagi."
    if score < 30:
        return "Skor sangat rendah — konsep dasar materi ini perlu kamu pelajari ulang dari awal."
    return "Banyak konsep dasar yang masih perlu dipelajari ulang sebelum kamu lanjut ke materi berikutnya."
```

> Voice rules dari `BRAND.md` §6:
> - "kamu" not "Anda"
> - Honest, tidak janjiin sesuatu
> - Tidak cheesy / patronizing ("kamu hebat!" ❌)
> - Calm, tidak excessive `!`
> - 1-2 kalimat saja

---

## 🚀 Tugas #3: Recommendation Engine

### Step 3.1: Pahami yang sudah ada

Buka `backend/app/services/recommendation_engine.py`. Sudah ada base templates dari `BRAND.md` §7.7:

```python
_BASE_TEMPLATES: dict[UnderstandingLevel, str] = {
    UnderstandingLevel.HIGH: "Lanjut ke materi berikutnya, atau coba kuis dengan tingkat kesulitan lebih tinggi.",
    UnderstandingLevel.MEDIUM: "Tinjau ulang bagian yang masih ragu, lalu asah lagi dalam 1-2 hari.",
    UnderstandingLevel.LOW: "Baca ulang materi dari awal, fokus pada poin dasar, lalu asah lagi.",
}
```

### Step 3.2: Tambah sub-conditions

Sama pola seperti insight engine. **Pertahankan brand callback "asah lagi"** di akhir recommendation untuk medium dan low:

```python
def generate_recommendation(
    level: UnderstandingLevel,
    eval_result: EvaluationResult,
) -> str:
    score = eval_result.score_percentage
    unanswered = eval_result.unanswered_count
    total = eval_result.total_questions
    time = eval_result.time_taken_seconds
    fast = time <= total * 60
    slow = time > total * 90

    if level == UnderstandingLevel.HIGH:
        if fast and score == 100:
            return "Kamu siap untuk materi berikutnya. Coba topik lanjutan atau kuis dengan tingkat kesulitan lebih tinggi."
        return "Lanjut ke materi berikutnya, atau coba kuis dengan tingkat kesulitan lebih tinggi."

    if level == UnderstandingLevel.MEDIUM:
        if unanswered > total * 0.3:
            return "Coba alokasikan waktu lebih untuk setiap soal — jangan skip kalau ragu, ambil tebakan terbaik. Lalu asah lagi."
        if slow:
            return "Bagian yang membuat ragu kemungkinan jadi penyebab waktu lama. Tinjau ulang konsep itu dulu, lalu asah lagi."
        return "Tinjau ulang bagian yang masih ragu, lalu asah lagi dalam 1-2 hari."

    # LOW
    if unanswered > total * 0.5:
        return "Baca dan pahami materi dari awal sebelum mengerjakan kuis. Setelah itu asah lagi sambil cek pemahamanmu."
    return "Baca ulang materi dari awal, fokus pada poin dasar, lalu asah lagi."
```

---

## 🧪 Tugas #4: Tulis tests

### Step 4.1: Test classifier wrapper

Buat `backend/tests/test_understanding_classifier.py`:

```python
from app.services import understanding_classifier
from app.schemas.internal import EvaluationResult, QuestionResult
from app.schemas.result import UnderstandingLevel


def make_eval(score, time, correct=4, wrong=1, unanswered=0, total=5):
    return EvaluationResult(
        correct_count=correct,
        wrong_count=wrong,
        unanswered_count=unanswered,
        total_questions=total,
        score_percentage=score,
        time_taken_seconds=time,
        question_results=[
            QuestionResult(
                question_id=i, selected_option_index=0, correct_option_index=0,
                is_correct=True, is_unanswered=False
            ) for i in range(1, total + 1)
        ],
    )


def test_high_score_fast():
    result = understanding_classifier.classify(make_eval(score=95, time=200))
    assert result == UnderstandingLevel.HIGH


def test_medium_score():
    result = understanding_classifier.classify(make_eval(score=60, time=400))
    assert result == UnderstandingLevel.MEDIUM


def test_low_score():
    result = understanding_classifier.classify(make_eval(score=20, time=400))
    assert result == UnderstandingLevel.LOW


def test_returns_valid_enum():
    """Classifier must always return one of 3 valid enum values."""
    result = understanding_classifier.classify(make_eval(score=50, time=300))
    assert result in [UnderstandingLevel.HIGH, UnderstandingLevel.MEDIUM, UnderstandingLevel.LOW]
```

### Step 4.2: Test insight + recommendation engines

Buat `backend/tests/test_insight_engine.py` dan `backend/tests/test_recommendation_engine.py` dengan pattern serupa. Cover semua sub-conditions yang kamu implement.

```python
from app.services import insight_engine
from app.schemas.result import UnderstandingLevel
# ... import make_eval helper from above (or duplicate)


def test_high_with_fast_time():
    result = insight_engine.generate_insight(
        UnderstandingLevel.HIGH,
        make_eval(score=95, time=180)
    )
    assert "efisien" in result or "menguasai" in result


def test_medium_with_many_unanswered():
    result = insight_engine.generate_insight(
        UnderstandingLevel.MEDIUM,
        make_eval(score=60, time=300, unanswered=2)
    )
    assert "skip" in result.lower()


# ... dst untuk tiap sub-condition
```

### Step 4.3: Run tests

```bash
pytest backend/tests/test_understanding_classifier.py -v
pytest backend/tests/test_insight_engine.py -v
pytest backend/tests/test_recommendation_engine.py -v
```

---

## 📝 Branch + PR

Sebenarnya kamu boleh buat 2 PR (1 untuk classifier, 1 untuk insight+recommendation), atau 1 PR gabungan. Tergantung preferensi tim.

Recommended: **2 PR**

```bash
# PR 1: Classifier
git checkout -b feat/desta-classifier-ml
git add backend/ml/classifier/artifacts/classifier.pkl \
        backend/app/services/understanding_classifier.py \
        backend/tests/test_understanding_classifier.py
git commit -m "feat(classifier): integrate trained Random Forest classifier"
git push origin feat/desta-classifier-ml
# Buka PR

# PR 2: Insight + Recommendation
git checkout main && git pull
git checkout -b feat/desta-insight-recommendation
git add backend/app/services/insight_engine.py \
        backend/app/services/recommendation_engine.py \
        backend/tests/test_insight_engine.py \
        backend/tests/test_recommendation_engine.py
git commit -m "feat(insight): add sub-conditions for richer insight & recommendation"
git push origin feat/desta-insight-recommendation
# Buka PR
```

---

## ✅ Definition of Done

Tugasmu selesai kalau:

### Classifier (Tugas #1)
- [ ] `python -m ml.classifier.train` jalan tanpa error, accuracy ≥ 85%
- [ ] `classifier.pkl` di-commit ke repo
- [ ] `python -m ml.classifier.inference` print prediction yang masuk akal
- [ ] `app/services/understanding_classifier.py` panggil `ml.classifier` dengan benar
- [ ] Fallback ke rule-based kalau model fail load
- [ ] Test pass

### Insight + Recommendation (Tugas #2 & #3)
- [ ] Minimal 6-8 sub-conditions per engine
- [ ] Voice consistent dengan BRAND.md §6 ("kamu", honest, calm)
- [ ] Brand callback "asah lagi" tetap muncul di recommendation medium/low
- [ ] Test pass

### Overall
- [ ] PR(s) merged ke `main`

---

## 🛠️ Common problems + solusi

### "ImportError: cannot import name 'predict' from ml.classifier.inference"
Pastikan kamu run dari `backend/` directory, bukan dari `ml/`. PYTHONPATH harus include `backend/`.

```bash
cd /home/ravi/Projects/TempaCapstoneProject/backend
python -m ml.classifier.inference
```

### "Model accuracy 100%"
Itu artinya noise injection tidak jalan. Cek `data_generation.py` line `if rng.random() < noise_rate`. NOISE_RATE harus 0.05 (5%).

### "Test gagal di test_returns_valid_enum"
Pastikan return value bener-bener `UnderstandingLevel` enum, bukan string. Convert string → enum:
```python
return UnderstandingLevel(label_str)
```

### "Stuck di step lain"
Tanya di chat tim:
```
Stuck di [Tugas #X, Step Y]
Error: [paste error]
Sudah dicoba: [apa aja]
```

---

## 📚 Resources

- **`/ML.md` §4** — strategi ML konvensional, kenapa Random Forest
- **`/PRD.md` §15** — rule starting point untuk classifier
- **`/BRAND.md` §6** — voice rules
- **`/BRAND.md` §7.6-7.7** — base templates yang harus diperluas
- **`/ARCHITECTURE.md` §5b** — kenapa `ml/` dipisah dari `app/`
- **sklearn Random Forest docs** — https://scikit-learn.org/stable/modules/ensemble.html#random-forests

---

## 🎯 Tips

1. **Mulai dari Tugas #1** (classifier) — paling cepat, output langsung kelihatan
2. **Tugas #2 & #3** bisa dikerjakan paralel — kerangkanya sama
3. **Ditest dulu sebelum PR** — kalau ada bug ketahuan, sayang waktunya kalau menunggu review
4. **Pakai sample fixtures** dari `tests/conftest.py` — sudah ada `sample_eval_result` yang bisa dipakai

Selamat ngerjain Desta! 🚀
