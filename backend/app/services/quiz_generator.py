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
import difflib
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
MIN_QUESTION_COUNT = 3        # for DL path — we expect quality
FALLBACK_MIN_COUNT = 2        # rule-based fallback — accept fewer if needed
MIN_MATERIAL_LENGTH = 100


# Indonesian question starters.
_QUESTION_STARTERS = (
    "Apa", "Apakah", "Bagaimana", "Mengapa", "Kenapa", "Siapa", "Kapan",
    "Di mana", "Dimana", "Berapa", "Manakah", "Mana yang", "Sebutkan",
    "Jelaskan", "Tulislah", "Tuliskan", "Tentukan", "Hitunglah",
)

def _normalize_for_dedup(text: str) -> str:
    # Remove punctuation and normalize whitespace
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Remove common question starters to focus on the core topic
    for starter in _QUESTION_STARTERS:
        if text.startswith(starter.lower()):
            text = text[len(starter):].strip()
    return " ".join(text.split())

def _is_duplicate(new_q_text: str, existing_questions: list[QuestionInternal], threshold: float = 0.8) -> bool:
    norm_new = _normalize_for_dedup(new_q_text)
    for q in existing_questions:
        norm_existing = _normalize_for_dedup(q.question)
        # Sequence matching on core text
        similarity = difflib.SequenceMatcher(None, norm_new, norm_existing).ratio()
        
        # Word overlap check (Jaccard similarity)
        words_new = set(norm_new.split())
        words_exist = set(norm_existing.split())
        jaccard = len(words_new & words_exist) / len(words_new | words_exist) if words_new and words_exist else 0.0
            
        if similarity > threshold or jaccard > 0.65:
            return True
    return False


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
                cleaned = _clean_question_text(q["question"])
                if cleaned is None:
                    continue  # cleanup made it invalid; skip
                
                if _is_duplicate(cleaned, questions):
                    logger.info("quiz_generator: skipping duplicate question from DL")
                    continue
                    
                questions.append(
                    QuestionInternal(
                        id=len(questions) + 1,  # renumber after dropping
                        question=cleaned,
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
# Quality cleanup (defense-in-depth — runs on top of ml/generator output)
# ============================================================================

import re

# Patterns to strip from the start (and embedded) of generated questions.
# Non-fine-tuned T5 sometimes echoes instruction prefixes back into output.
_PROMPT_PREFIX_PATTERNS = (
    "buat pertanyaan:",
    "buatlah pertanyaan:",
    "pertanyaan seperti ini:",
    "pertanyaan:",
)

# Indonesian question starters (moved to top for dedup logic)

_MIN_CLEANED_LENGTH = 15  # after cleanup, need at least this much text

# Compile a regex to find any question starter as a word boundary
_QUESTION_STARTER_RE = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in _QUESTION_STARTERS) + r")\b",
    re.IGNORECASE,
)


def _clean_question_text(raw: str) -> str | None:
    """Defense-in-depth cleanup on each generated question.

    Strips prompt-prefix leakage, leading garbage, and rejects outputs that
    don't look like proper questions. Returns None if not salvageable.
    """
    if not raw:
        return None

    text = raw.strip()

    # Iteratively strip prompt-prefix patterns from the start.
    # Loop because models sometimes repeat: "Buat pertanyaan: Buat pertanyaan: ..."
    for _ in range(4):
        stripped = False
        for pattern in _PROMPT_PREFIX_PATTERNS:
            if text.lower().startswith(pattern):
                text = text[len(pattern):].strip()
                stripped = True
                break
        if not stripped:
            break

    # Aggressive scan: find the FIRST Indonesian question starter and trim
    # everything before it. Handles cases like "Inflasi  Buat pertanyaan: Apa..."
    # where the prefix isn't at position 0.
    match = _QUESTION_STARTER_RE.search(text)
    if match:
        text = text[match.start():].strip()
    else:
        # No proper question starter found → not a valid question
        return None

    # Truncate at first '?' if present (drops trailing artifacts)
    if "?" in text:
        text = text.split("?", 1)[0].strip() + "?"

    # Drop leading non-letter chars (defensive — should be moot after starter match)
    while text and not text[0].isalnum():
        text = text[1:].strip()

    # Capitalize first letter for readability
    if text and text[0].islower():
        text = text[0].upper() + text[1:]

    # Ensure ends with '?' (model sometimes truncates mid-sentence)
    if text and text[-1] not in "?.!":
        text += "?"

    # Reject if too short
    if len(text) < _MIN_CLEANED_LENGTH:
        return None

    # Reject single-character-dominated output (model collapse)
    letters = [c for c in text.lower() if c.isalpha()]
    if not letters:
        return None
    if letters.count(max(letters, key=letters.count)) / len(letters) > 0.5:
        return None

    # Reject if no meaningful content (need at least 1 word with 5+ chars)
    if not any(
        len("".join(c for c in w if c.isalpha())) >= 5 for w in text.split()
    ):
        return None

    return text


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
    """Split text into sensible-length sentences (bulletproof — always returns >= 1 if text is non-trivial).

    Fallback chain:
        1. Sentence terminators (. ! ?)
        2. Line breaks (handles list-style content)
        3. Punctuation breaks (commas, semicolons, dashes)
        4. Sliding window (90-char chunks — last resort for unstructured text)
    """
    # Path 1: proper sentences
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    sensible = [s for s in sentences if 30 <= len(s) <= 280]
    if len(sensible) >= FALLBACK_MIN_COUNT:
        return sensible

    # Path 2: line-based
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    line_sensible = [l for l in lines if 30 <= len(l) <= 280]
    if len(line_sensible) >= FALLBACK_MIN_COUNT:
        return line_sensible

    # Path 3: punctuation-based (split on commas, semicolons, dashes)
    chunks = re.split(r"[,;—–-]\s+", text)
    chunks = [c.strip() for c in chunks if c.strip()]
    chunk_sensible = [c for c in chunks if 30 <= len(c) <= 280]
    if len(chunk_sensible) >= FALLBACK_MIN_COUNT:
        return chunk_sensible

    # Path 4: sliding window — guarantees >= 2 chunks for any text >= 90 chars
    window_size = 90
    overlap = 30
    windowed: list[str] = []
    text_clean = " ".join(text.split())  # collapse whitespace
    pos = 0
    while pos < len(text_clean):
        chunk = text_clean[pos : pos + window_size]
        if len(chunk) >= 30:
            windowed.append(chunk)
        pos += window_size - overlap
    if len(windowed) >= 1:
        return windowed

    # Absolute fallback: return whole text as single chunk
    cleaned = text.strip()
    return [cleaned] if cleaned else []


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

    from app.services._distractors import _pick_similar_length_distractors
    distractors = _pick_similar_length_distractors(correct, pool, 3)
    if len(distractors) < 3:
        return None

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
    """Rule-based fill-in-the-blank quiz generator. Used as fallback.

    Bulletproof: any text >= MIN_MATERIAL_LENGTH (100 chars) should produce
    at least 2 questions. Returns 400 only when input genuinely can't be
    used (e.g., < 4 distinct keywords).
    """
    try:
        sentences = _split_sentences(text)

        # If even sliding-window can't produce 2 chunks, content is too thin
        if len(sentences) < 1:
            raise ApiException(
                status_code=400,
                code=QUIZ_GENERATION_FAILED,
                detail=(
                    "Materi tidak cocok untuk membuat kuis. "
                    "Sistem butuh teks dengan minimal 100 karakter berisi konten substantif."
                ),
            )

        all_keywords = _extract_keywords(text)
        if len(all_keywords) < 4:
            raise ApiException(
                status_code=400,
                code=QUIZ_GENERATION_FAILED,
                detail=(
                    "Materi terlalu seragam untuk membuat kuis pilihan ganda. "
                    "Sistem butuh minimal 4 kata bermakna yang berbeda. "
                    "Coba materi dengan kosakata lebih beragam."
                ),
            )

        rng = random.Random(abs(hash(text)) & 0xFFFFFFFF)
        used_correct_lower: set[str] = set()
        questions: list[QuestionInternal] = []
        target = min(DEFAULT_QUESTION_COUNT, max(len(sentences), 2))

        # Try sentences first — generates richest questions
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
                if _is_duplicate(q.question, questions):
                    continue
                questions.append(q)

        # Last-resort: if still no questions, generate from whole-text passages
        # using different keywords as the blank
        if len(questions) < 2 and len(all_keywords) >= 4:
            whole_text = " ".join(text.split())[:280]  # collapse whitespace + truncate
            for keyword in all_keywords[:DEFAULT_QUESTION_COUNT]:
                if len(questions) >= 2:
                    break
                if keyword.lower() in used_correct_lower:
                    continue
                used_correct_lower.add(keyword.lower())
                q = _build_rule_question(
                    len(questions) + 1, whole_text, keyword, all_keywords, rng
                )
                if q is not None:
                    if _is_duplicate(q.question, questions):
                        continue
                    questions.append(q)

        if not questions:
            raise ApiException(
                status_code=400,
                code=QUIZ_GENERATION_FAILED,
                detail=(
                    "Tidak bisa membuat pertanyaan dari materi ini. "
                    "Coba materi yang lebih panjang dengan konten penjelasan, "
                    "bukan sekadar daftar atau angka."
                ),
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
