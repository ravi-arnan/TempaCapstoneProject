"""Quiz generator — turns learning material text into a quiz.

OWNER: Audry (Backend — Quiz Generator)

This file currently contains a PLACEHOLDER implementation that generates
fill-in-the-blank multiple-choice questions deterministically. It works
end-to-end so the frontend can be demoed before the proper implementation
lands.

Audry: feel free to replace this entirely with your own approach. The only
contract you need to honor is:
    - input: material_text: str
    - output: QuizInternal with `DEFAULT_QUESTION_COUNT` questions, each
      with exactly 4 options and one correct_option_index
    - errors: raise ApiException with codes from app/utils/errors.py

See ARCHITECTURE.md §8 for the data flow this slots into.
"""

import random
import re
import uuid
from datetime import datetime, timezone

from app.schemas.internal import QuestionInternal, QuizInternal
from app.utils.errors import (
    ApiException,
    MATERIAL_TOO_SHORT,
    QUIZ_GENERATION_FAILED,
)

DEFAULT_QUESTION_COUNT = 5
MIN_QUESTION_COUNT = 3
MIN_MATERIAL_LENGTH = 100

# Indonesian + English common stop words to skip when picking key words.
# Not exhaustive — just enough to avoid trivial blanks like "yang" or "the".
_STOP_WORDS: frozenset[str] = frozenset(
    {
        # Indonesian
        "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "ini",
        "itu", "atau", "adalah", "akan", "tidak", "juga", "dapat", "sebagai",
        "telah", "oleh", "dalam", "saat", "yaitu", "namun", "agar", "karena",
        "lebih", "secara", "menjadi", "sangat", "harus", "bahwa", "hanya",
        "kita", "mereka", "kami", "kamu", "saya", "anda", "tetapi", "sehingga",
        "sudah", "belum", "masih", "bisa", "tersebut", "ialah", "ada", "tiap",
        # English fallbacks
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "and", "or", "but", "of", "in", "on", "at", "to", "for", "with",
        "this", "that", "these", "those", "it", "its", "they", "them",
        "from", "as", "by", "has", "have", "had",
    }
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{4,}")  # words with 4+ letters


def _split_sentences(text: str) -> list[str]:
    """Split into sensible-length sentences."""
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    return [s for s in sentences if 30 <= len(s) <= 280]


def _extract_keywords(text: str) -> list[str]:
    """Unique non-stopword candidates from the text, longest first."""
    seen: set[str] = set()
    words: list[str] = []
    for m in _WORD_RE.finditer(text):
        w = m.group(0)
        wl = w.lower()
        if wl in _STOP_WORDS or wl in seen:
            continue
        seen.add(wl)
        words.append(w)
    return sorted(words, key=len, reverse=True)


def _pick_keyword_from(sentence: str, used_lower: set[str]) -> str | None:
    """Pick the longest unused non-stopword from this sentence."""
    for w in _extract_keywords(sentence):
        if w.lower() not in used_lower:
            used_lower.add(w.lower())
            return w
    return None


def _build_question(
    qid: int,
    sentence: str,
    correct: str,
    pool: list[str],
    rng: random.Random,
) -> QuestionInternal | None:
    """Construct a fill-in-the-blank question from a sentence + correct word."""
    pattern = re.compile(r"\b" + re.escape(correct) + r"\b")
    blanked = pattern.sub("____", sentence, count=1)
    if blanked == sentence:
        return None  # word not found via word boundary; skip

    distractor_candidates = [w for w in pool if w.lower() != correct.lower()]
    if len(distractor_candidates) < 3:
        return None
    distractors = rng.sample(distractor_candidates, 3)

    options: list[str] = [correct, *distractors]
    rng.shuffle(options)
    correct_idx = options.index(correct)

    return QuestionInternal(
        id=qid,
        question=f'Lengkapi kalimat berikut: "{blanked}"',
        options=options,  # type: ignore[arg-type]
        correct_option_index=correct_idx,
    )


def generate_quiz(material_text: str) -> QuizInternal:
    """Generate a multiple-choice quiz from raw material text.

    Returns:
        QuizInternal with up to `DEFAULT_QUESTION_COUNT` questions.

    Raises:
        ApiException(MATERIAL_TOO_SHORT) when text is below threshold.
        ApiException(QUIZ_GENERATION_FAILED) when text is too uniform to
            yield enough questions or distractors.
    """
    text = material_text.strip()
    if len(text) < MIN_MATERIAL_LENGTH:
        raise ApiException(
            status_code=400,
            code=MATERIAL_TOO_SHORT,
            detail="Materinya terlalu pendek. Tambahkan minimal 100 karakter agar sistem bisa membuat kuis.",
        )

    try:
        sentences = _split_sentences(text)
        if len(sentences) < MIN_QUESTION_COUNT:
            raise ApiException(
                status_code=500,
                code=QUIZ_GENERATION_FAILED,
                detail="Materi belum cukup variatif untuk membuat kuis. Coba teks dengan lebih banyak kalimat.",
            )

        all_keywords = _extract_keywords(text)
        if len(all_keywords) < 4:
            raise ApiException(
                status_code=500,
                code=QUIZ_GENERATION_FAILED,
                detail="Materi belum cukup variatif untuk membuat distraktor jawaban.",
            )

        # Deterministic per-material seed: same input -> same quiz
        rng = random.Random(abs(hash(text)) & 0xFFFFFFFF)

        used_correct_lower: set[str] = set()
        questions: list[QuestionInternal] = []
        target = min(DEFAULT_QUESTION_COUNT, len(sentences))

        for sentence in sentences[: DEFAULT_QUESTION_COUNT * 3]:
            if len(questions) >= target:
                break
            correct = _pick_keyword_from(sentence, used_correct_lower)
            if not correct:
                continue
            q = _build_question(len(questions) + 1, sentence, correct, all_keywords, rng)
            if q is not None:
                questions.append(q)

        if len(questions) < MIN_QUESTION_COUNT:
            raise ApiException(
                status_code=500,
                code=QUIZ_GENERATION_FAILED,
                detail="Gagal membuat kuis dari materi ini. Coba materi yang lebih panjang dan beragam.",
            )

        return QuizInternal(
            quiz_id=str(uuid.uuid4()),
            questions=questions,
            generated_at=datetime.now(timezone.utc),
            source_material_excerpt=text[:500],
        )
    except ApiException:
        raise
    except Exception as exc:  # noqa: BLE001 — surface anything unexpected as a typed error
        raise ApiException(
            status_code=500,
            code=QUIZ_GENERATION_FAILED,
            detail="Gagal membuat kuis. Coba materi lain atau ulangi sebentar lagi.",
        ) from exc
