"""Quiz generator — turns learning material text into a quiz.

OWNER: Audry (Backend — Quiz Generator)

This is a THIN WRAPPER around `ml/generator/inference.py` (the DL model).
The wrapper:
    1. Validates input (length checks)
    2. Tries DL inference via ml.generator
    3. Falls back to rule-based generation if DL is unavailable
    4. Wraps result in QuizInternal with a fresh quiz_id

The actual model loading + question generation logic lives in
`backend/ml/generator/inference.py`. See ML.md §3 for details.

If you want to swap the DL approach for something else, edit
`ml/generator/inference.py`. This wrapper file should rarely change.
"""

from __future__ import annotations

import logging
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
from ml.generator import inference as ml_generator

logger = logging.getLogger(__name__)

DEFAULT_QUESTION_COUNT = 5
MIN_QUESTION_COUNT = 3
MIN_MATERIAL_LENGTH = 100


def generate_quiz(material_text: str) -> QuizInternal:
    """Generate a multiple-choice quiz from raw material text.

    Tries DL first; falls back to rule-based on failure.
    """
    text = material_text.strip()
    if len(text) < MIN_MATERIAL_LENGTH:
        raise ApiException(
            status_code=400,
            code=MATERIAL_TOO_SHORT,
            detail="Materinya terlalu pendek. Tambahkan minimal 100 karakter agar sistem bisa membuat kuis.",
        )

    # === Path 1: DL via ml/generator (preferred) ===
    if ml_generator.is_available():
        try:
            raw_questions = ml_generator.generate(text)
            questions: list[QuestionInternal] = []
            for i, q in enumerate(raw_questions, start=1):
                questions.append(
                    QuestionInternal(
                        id=i,
                        question=q["question"],
                        options=q["options"],
                        correct_option_index=q["correct_option_index"],
                    )
                )
            if len(questions) >= MIN_QUESTION_COUNT:
                logger.info("quiz_generator: DL path produced %d questions", len(questions))
                return QuizInternal(
                    quiz_id=str(uuid.uuid4()),
                    questions=questions,
                    generated_at=datetime.now(timezone.utc),
                    source_material_excerpt=text[:500],
                )
            logger.warning(
                "quiz_generator: DL path produced only %d questions (need %d), falling back",
                len(questions),
                MIN_QUESTION_COUNT,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "quiz_generator: DL path failed (%s), falling back to rule-based",
                exc,
            )

    # === Path 2: rule-based fallback ===
    return _generate_rule_based(text)


# ============================================================================
# Rule-based fallback (used when DL unavailable or fails)
# ============================================================================

_STOP_WORDS: frozenset[str] = frozenset(
    {
        "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "ini",
        "itu", "atau", "adalah", "akan", "tidak", "juga", "dapat", "sebagai",
        "telah", "oleh", "dalam", "saat", "yaitu", "namun", "agar", "karena",
        "lebih", "secara", "menjadi", "sangat", "harus", "bahwa", "hanya",
        "kita", "mereka", "kami", "kamu", "saya", "anda", "tetapi", "sehingga",
        "sudah", "belum", "masih", "bisa", "tersebut", "ialah", "ada", "tiap",
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "and", "or", "but", "of", "in", "on", "at", "to", "for", "with",
        "this", "that", "these", "those", "it", "its", "they", "them",
        "from", "as", "by", "has", "have", "had",
    }
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{4,}")


def _split_sentences(text: str) -> list[str]:
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    return [s for s in sentences if 30 <= len(s) <= 280]


def _extract_keywords(text: str) -> list[str]:
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
    for w in _extract_keywords(sentence):
        if w.lower() not in used_lower:
            used_lower.add(w.lower())
            return w
    return None


def _build_rule_question(
    qid: int,
    sentence: str,
    correct: str,
    pool: list[str],
    rng: random.Random,
) -> QuestionInternal | None:
    pattern = re.compile(r"\b" + re.escape(correct) + r"\b")
    blanked = pattern.sub("____", sentence, count=1)
    if blanked == sentence:
        return None

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


def _generate_rule_based(text: str) -> QuizInternal:
    """Rule-based fill-in-the-blank quiz generator. Used as fallback."""
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
            q = _build_rule_question(
                len(questions) + 1, sentence, correct, all_keywords, rng
            )
            if q is not None:
                questions.append(q)

        if len(questions) < MIN_QUESTION_COUNT:
            raise ApiException(
                status_code=500,
                code=QUIZ_GENERATION_FAILED,
                detail="Gagal membuat kuis dari materi ini. Coba materi yang lebih panjang dan beragam.",
            )

        logger.info("quiz_generator: rule-based path produced %d questions", len(questions))
        return QuizInternal(
            quiz_id=str(uuid.uuid4()),
            questions=questions,
            generated_at=datetime.now(timezone.utc),
            source_material_excerpt=text[:500],
        )
    except ApiException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ApiException(
            status_code=500,
            code=QUIZ_GENERATION_FAILED,
            detail="Gagal membuat kuis. Coba materi lain atau ulangi sebentar lagi.",
        ) from exc
