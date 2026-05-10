import pytest
from app.services import quiz_generator
from app.schemas.internal import QuizInternal, QuestionInternal
from app.utils.errors import ApiException

def test_too_short_raises():
    with pytest.raises(ApiException) as exc:
        quiz_generator.generate_quiz("Pendek banget.")
    assert exc.value.code == "MATERIAL_TOO_SHORT"

def test_normal_material_returns_quiz(monkeypatch):
    # Ensure we use the fallback logic to test it without needing HF space
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    assert isinstance(quiz, QuizInternal)
    assert len(quiz.questions) >= 2
    assert all(len(q.options) == 4 for q in quiz.questions)
    assert all(0 <= q.correct_option_index <= 3 for q in quiz.questions)

def test_questions_have_unique_ids(monkeypatch):
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    ids = [q.id for q in quiz.questions]
    assert len(ids) == len(set(ids)), "Question IDs must be unique"

def test_options_are_distinct(monkeypatch):
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    for q in quiz.questions:
        assert len(set(q.options)) == 4, f"Q{q.id}: duplicate options"

def test_fallback_on_dl_failure(monkeypatch):
    """Even if DL model unavailable, generator should fall back to rule-based."""
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)

    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    assert isinstance(quiz, QuizInternal)
    assert len(quiz.questions) >= 2

def test_is_duplicate():
    """Test the deduplication logic directly."""
    existing = [
        QuestionInternal(id=1, question="Apa itu fotosintesis?", options=["A", "B", "C", "D"], correct_option_index=0)
    ]
    
    # Highly similar (should be true)
    assert quiz_generator._is_duplicate("Apakah itu fotosintesis?", existing) is True
    
    # Not similar (should be false)
    assert quiz_generator._is_duplicate("Dimana proses reaksi gelap terjadi?", existing) is False
