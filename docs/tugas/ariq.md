# 🟢 Tugas Ariq — Data & Analisis

Halo Ariq! Tugasmu adalah **mengevaluasi jawaban kuis user** — hitung skor, jumlah benar/salah/tidak dijawab, dan output detail per soal. **Tidak wajib pakai ML** untuk MVP, tapi ada **bonus opsional** kalau kamu mau eksplor pandas analytics.

## 📌 Big picture

Setelah Audry's DL model generate kuis, dan user kerjakan quiz-nya, **kamu** yang menerima jawaban dan compute hasil-nya. Output kamu (`EvaluationResult`) jadi input untuk Desta's classifier.

```
    User answers
         ↓
    Ariq's evaluator (kamu di sini)
         ↓
    EvaluationResult { score, correct_count, wrong_count, ... }
         ↓
    Desta's classifier
```

---

## ⚙️ Setup awal (sekali aja, ~10 menit)

### 1. Clone repo & install backend

```bash
git clone https://github.com/ravi-arnan/TempaCapstoneProject.git
cd TempaCapstoneProject/backend

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run backend dev server (untuk verify setup)

```bash
uvicorn app.main:app --reload --port 8000
```

Buka browser: http://localhost:8000/health

Kalau muncul `{"status":"ok","version":"0.1.0"}` → setup sukses. Stop server (`Ctrl+C`).

---

## 🚀 Tugas utama: Implementasi Quiz Evaluator

### Step 1: Pahami yang sudah ada

Buka file `backend/app/services/quiz_evaluator.py`. **Sudah ada placeholder implementation** yang bisa kamu replace atau extend.

Function utama yang kamu kerjain:

```python
def evaluate(
    quiz: QuizInternal,                # quiz lengkap dari storage (Audry's output)
    answers: list[Answer],             # jawaban user dari frontend
    time_taken_seconds: int,           # durasi pengerjaan
) -> EvaluationResult:
    """Compute score, counts, per-question detail."""
    ...
```

### Step 2: Pahami input & output shape

**Input** — sudah didefinisi di `backend/app/schemas/`:

```python
# QuizInternal — quiz lengkap (with correct answers, server-only)
class QuizInternal(BaseModel):
    quiz_id: str
    questions: list[QuestionInternal]   # each has correct_option_index 0-3
    ...

# Answer — single user answer
class Answer(BaseModel):
    question_id: int
    selected_option_index: int | None    # 0-3 atau None kalau skip
```

**Output** — yang kamu produce:

```python
class EvaluationResult(BaseModel):
    correct_count: int
    wrong_count: int
    unanswered_count: int
    total_questions: int
    score_percentage: int                # 0-100
    time_taken_seconds: int
    question_results: list[QuestionResult]   # detail per soal
```

> ⚠️ **PENTING**: `EvaluationResult` adalah **handoff ke Desta**. Kalau kamu mau ubah shape ini, **sync ke Desta dulu** — modulnya consume EvaluationResult.

### Step 3: Implementasi logic

Berikut pseudocode yang udah ada di placeholder. Kamu bisa improve atau pakai apa adanya:

```python
def evaluate(quiz, answers, time_taken_seconds):
    # 1. Validate length
    if len(answers) != quiz.total_questions:
        raise ApiException(400, ANSWERS_LENGTH_MISMATCH, "...")

    # 2. Map answers by question_id for fast lookup
    questions_by_id = {q.id: q for q in quiz.questions}

    results = []
    correct = wrong = unanswered = 0

    # 3. Loop tiap answer
    for ans in answers:
        q = questions_by_id.get(ans.question_id)
        if q is None:
            raise ApiException(400, INVALID_QUESTION_ID, "...")

        is_unanswered = ans.selected_option_index is None
        is_correct = (
            not is_unanswered
            and ans.selected_option_index == q.correct_option_index
        )

        # Increment counters
        if is_correct: correct += 1
        elif is_unanswered: unanswered += 1
        else: wrong += 1

        # Append per-question detail
        results.append(QuestionResult(
            question_id=q.id,
            selected_option_index=ans.selected_option_index,
            correct_option_index=q.correct_option_index,
            is_correct=is_correct,
            is_unanswered=is_unanswered,
        ))

    # 4. Compute score percentage
    total = quiz.total_questions
    score_percentage = round((correct / total) * 100) if total > 0 else 0

    return EvaluationResult(
        correct_count=correct,
        wrong_count=wrong,
        unanswered_count=unanswered,
        total_questions=total,
        score_percentage=score_percentage,
        time_taken_seconds=time_taken_seconds,
        question_results=results,
    )
```

### Step 4 (BONUS, opsional): Tambah analytics dengan pandas

Kalau kamu mau tambah ML/analytics flavor:

- Hitung average time per question
- Detect "rushing" pattern (waktu sangat cepat) atau "stuck" pattern (waktu sangat lama)
- Per-topic accuracy (kalau materi multi-topik) — pakai TF-IDF clustering

Tapi ini **opsional**. MVP jalan tanpa pandas pun OK.

### Step 5: Tulis unit tests

Buat file `backend/tests/test_quiz_evaluator.py`. Cover minimal 5 cases:

```python
from app.services import quiz_evaluator
from app.schemas.internal import QuizInternal, QuestionInternal
from app.schemas.quiz import Answer
from datetime import datetime, timezone


def make_quiz(num_questions=5):
    return QuizInternal(
        quiz_id="test-quiz",
        questions=[
            QuestionInternal(
                id=i,
                question=f"Q{i}",
                options=["A", "B", "C", "D"],
                correct_option_index=0,  # A is always correct
            )
            for i in range(1, num_questions + 1)
        ],
        generated_at=datetime.now(timezone.utc),
    )


def test_all_correct():
    quiz = make_quiz(5)
    answers = [Answer(question_id=i, selected_option_index=0) for i in range(1, 6)]
    result = quiz_evaluator.evaluate(quiz, answers, time_taken_seconds=120)
    assert result.score_percentage == 100
    assert result.correct_count == 5
    assert result.wrong_count == 0


def test_all_wrong():
    quiz = make_quiz(5)
    answers = [Answer(question_id=i, selected_option_index=1) for i in range(1, 6)]
    result = quiz_evaluator.evaluate(quiz, answers, time_taken_seconds=120)
    assert result.score_percentage == 0
    assert result.wrong_count == 5


def test_mixed():
    quiz = make_quiz(5)
    answers = [
        Answer(question_id=1, selected_option_index=0),  # correct
        Answer(question_id=2, selected_option_index=0),  # correct
        Answer(question_id=3, selected_option_index=1),  # wrong
        Answer(question_id=4, selected_option_index=None),  # unanswered
        Answer(question_id=5, selected_option_index=None),  # unanswered
    ]
    result = quiz_evaluator.evaluate(quiz, answers, time_taken_seconds=300)
    assert result.correct_count == 2
    assert result.wrong_count == 1
    assert result.unanswered_count == 2
    assert result.score_percentage == 40


def test_length_mismatch_raises():
    import pytest
    from app.utils.errors import ApiException

    quiz = make_quiz(5)
    answers = [Answer(question_id=1, selected_option_index=0)]   # only 1 answer
    with pytest.raises(ApiException) as exc:
        quiz_evaluator.evaluate(quiz, answers, time_taken_seconds=10)
    assert exc.value.code == "ANSWERS_LENGTH_MISMATCH"


def test_invariants_hold():
    """Ensure correct + wrong + unanswered = total."""
    quiz = make_quiz(5)
    answers = [
        Answer(question_id=1, selected_option_index=0),
        Answer(question_id=2, selected_option_index=1),
        Answer(question_id=3, selected_option_index=None),
        Answer(question_id=4, selected_option_index=2),
        Answer(question_id=5, selected_option_index=None),
    ]
    result = quiz_evaluator.evaluate(quiz, answers, time_taken_seconds=200)
    assert result.correct_count + result.wrong_count + result.unanswered_count == result.total_questions
```

Run tests:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_quiz_evaluator.py -v
```

Kalau semua green ✅ → tugas inti selesai.

### Step 6: Branch + PR

```bash
git checkout -b feat/ariq-evaluator
git add backend/app/services/quiz_evaluator.py backend/tests/test_quiz_evaluator.py
git commit -m "feat(evaluator): implement quiz evaluator with full scoring + per-question detail"
git push origin feat/ariq-evaluator

# Buka PR di GitHub, request review dari Ravi/Audry/Desta
```

---

## ✅ Definition of Done

Tugasmu selesai kalau:

- [ ] `evaluate()` function di `quiz_evaluator.py` implement penuh
- [ ] Validasi: length mismatch + invalid question_id raise ApiException benar
- [ ] Invariant tetap hold: `correct + wrong + unanswered === total_questions`
- [ ] Score percentage dihitung benar (rounded)
- [ ] Per-question detail di `question_results` lengkap
- [ ] Minimal 5 unit tests pass
- [ ] PR merged ke `main`

---

## 🛠️ Common problems + solusi

### "Import error: cannot import name 'EvaluationResult'"
Pastikan kamu import dari path yang benar:
```python
from app.schemas.internal import EvaluationResult, QuestionResult
```

### "Score percentage selalu 0 padahal banyak benar"
Cek division: kalau `total_questions = 0`, division by zero. Tambahkan guard:
```python
score_percentage = round((correct / total) * 100) if total > 0 else 0
```

### "Test gagal di test_invariants_hold"
Pastikan urutan increment: tiap answer increment **exactly satu** counter (correct OR wrong OR unanswered, tidak boleh dua). Pakai if/elif/else.

### "Stuck di step lain"
Tanya di chat tim dengan format:
```
Stuck di Step [X]
Error: [paste error]
Sudah dicoba: [apa aja]
```

---

## 📚 Resources

- **`/API.md` §4.3, §5.5** — HTTP contract submit endpoint + ScoreSummary shape
- **`/ARCHITECTURE.md` §6.3, §9** — internal types + sequence diagram submit flow
- **`/PRD.md` §10.4-10.5** — Hasil Kuis + Deteksi Tingkat Pemahaman
- **`/backend/app/schemas/internal.py`** — definisi `EvaluationResult`, `QuestionResult`

---

## 🎯 Setelah selesai

Setelah PR kamu merged, **Desta langsung bisa mulai implementasi classifier**. Mereka pakai output `EvaluationResult` kamu sebagai input.

Kasih kabar di chat tim kalau PR sudah merged supaya Desta tahu bisa mulai.

Selamat ngerjain Ariq! 🚀
