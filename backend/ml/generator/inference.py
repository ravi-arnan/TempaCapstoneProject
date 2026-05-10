"""Inference for the quiz generator (DL — IndoT5).

Inference strategy (in order of preference):
    1. HF Space (cloud) via HTTP — set HF_SPACE_URL env var
    2. Local CPU via transformers — auto-loads if HF Space unreachable
    3. Caller (app/services/quiz_generator.py) falls back to rule-based

This 3-tier approach gives demo resilience: if HF Space sleeps or
internet is down, local CPU still works; if local model isn't installed,
rule-based still works.

OWNER: Audry (integration + quality), Ravi (HF Space setup)
"""

from __future__ import annotations

import logging
import os
import random
import re
import difflib
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIG
# ============================================================================

# DECISION (2026-05-08): use base pretrained IndoT5 without fine-tuning.
# See ML.md §3 for rationale (fp16 NaN issue with T5 fine-tuning).

_LOCAL_MODEL_NAME = "Wikidepia/IndoT5-base"

# HF Space endpoint (cloud inference). Set via env var:
#   export HF_SPACE_URL="https://<username>-asahlagi-quizgen.hf.space"
# If unset or unreachable, falls back to local CPU inference.
_HF_SPACE_URL = os.getenv("HF_SPACE_URL", "").rstrip("/")
_HF_SPACE_TIMEOUT_SECONDS = 60.0

# Generation hyperparameters (used only by local fallback)
_MAX_INPUT_LENGTH = 512
_MAX_OUTPUT_LENGTH = 48
_NUM_BEAMS = 4
_REPETITION_PENALTY = 1.8
_NO_REPEAT_NGRAM_SIZE = 3
_NUM_QUESTIONS = 5

# ============================================================================
# Module-level state for LOCAL inference (loaded lazily)
# ============================================================================

_local_tokenizer = None
_local_model = None
_local_load_attempted = False
_local_load_error: Optional[str] = None


def _load_local_model() -> None:
    """Try to load local model. Called lazily — only if HF Space is unavailable."""
    global _local_tokenizer, _local_model, _local_load_attempted, _local_load_error
    if _local_load_attempted:
        return
    _local_load_attempted = True
    try:
        from transformers import T5ForConditionalGeneration, T5Tokenizer

        logger.info("ml.generator: Loading local IndoT5 from %s ...", _LOCAL_MODEL_NAME)
        _local_tokenizer = T5Tokenizer.from_pretrained(_LOCAL_MODEL_NAME)
        _local_model = T5ForConditionalGeneration.from_pretrained(_LOCAL_MODEL_NAME)
        _local_model.eval()
        logger.info(
            "ml.generator: Loaded local IndoT5 (params=%dM)",
            sum(p.numel() for p in _local_model.parameters()) // 1_000_000,
        )
    except Exception as exc:  # noqa: BLE001
        _local_load_error = f"{type(exc).__name__}: {exc}"
        logger.warning(
            "ml.generator: Failed to load local model (%s) — only HF Space + rule-based fallback available",
            _local_load_error,
        )


# ============================================================================
# HF Space client
# ============================================================================

_hf_space_available_cached: Optional[bool] = None


def _check_hf_space_available() -> bool:
    """Quick health check on HF Space (cached after first call)."""
    global _hf_space_available_cached
    if _hf_space_available_cached is not None:
        return _hf_space_available_cached
    if not _HF_SPACE_URL:
        _hf_space_available_cached = False
        return False
    try:
        import httpx

        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{_HF_SPACE_URL}/")
            if response.status_code == 200 and response.json().get("status") == "ready":
                logger.info("ml.generator: HF Space available at %s", _HF_SPACE_URL)
                _hf_space_available_cached = True
                return True
            logger.warning(
                "ml.generator: HF Space at %s returned status=%d",
                _HF_SPACE_URL,
                response.status_code,
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("ml.generator: HF Space unreachable (%s)", exc)
    _hf_space_available_cached = False
    return False


def _generate_via_hf_space(material_text: str) -> list[dict]:
    """Call HF Space /generate endpoint. Returns list of question dicts."""
    import httpx

    with httpx.Client(timeout=_HF_SPACE_TIMEOUT_SECONDS) as client:
        response = client.post(
            f"{_HF_SPACE_URL}/generate",
            json={"material_text": material_text},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("questions", [])


# ============================================================================
# Public API
# ============================================================================


def is_available() -> bool:
    """Return True if EITHER HF Space OR local model is loadable."""
    if _check_hf_space_available():
        return True
    _load_local_model()
    return _local_model is not None


def generate(material_text: str) -> list[dict]:
    """Generate quiz from material. Tries HF Space, falls back to local CPU.

    Returns: list of dicts with keys {question, options, correct_option_index}
    Raises: RuntimeError if both HF Space and local model unavailable.
    """
    # Path 1: HF Space (cloud)
    if _check_hf_space_available():
        try:
            questions = _generate_via_hf_space(material_text)
            if questions:
                logger.info(
                    "ml.generator: HF Space produced %d questions",
                    len(questions),
                )
                return questions
            logger.warning("ml.generator: HF Space returned empty list, trying local")
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "ml.generator: HF Space request failed (%s), trying local",
                exc,
            )

    # Path 2: local CPU
    _load_local_model()
    if _local_model is None:
        raise RuntimeError(
            f"ml.generator unavailable: HF Space + local both failed. "
            f"Local error: {_local_load_error}"
        )
    return _generate_locally(material_text)


# ============================================================================
# Local inference logic (fallback path)
# ============================================================================

_STOP_WORDS = frozenset({
    "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "ini",
    "itu", "atau", "adalah", "akan", "tidak", "juga", "dapat", "sebagai",
    "telah", "oleh", "dalam", "saat", "yaitu", "namun", "agar", "karena",
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "but", "of", "in", "on", "at", "to", "for", "with",
    "this", "that", "these", "those", "it", "its", "they", "them",
})

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{4,}")


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
    return words


from app.services._distractors import _pick_similar_length_distractors


def _split_passages(text: str, n: int = _NUM_QUESTIONS) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= n:
        return sentences[:n]
    step = max(1, len(sentences) // n)
    return [sentences[i * step] for i in range(n) if i * step < len(sentences)]


def _generate_local_question(passage: str) -> str:
    if _local_model is None or _local_tokenizer is None:
        raise RuntimeError("Local model not loaded")

    # Add prompt variation for local generation
    prompts = [
        f"buat pertanyaan dari kalimat berikut: {passage}",
        f"buatlah soal pilihan ganda berdasarkan teks ini: {passage}",
        f"pertanyaan untuk teks: {passage}",
        f"buat pertanyaan: {passage}",
        f"tuliskan satu pertanyaan dari: {passage}"
    ]
    prompt = random.choice(prompts)
    inputs = _local_tokenizer(
        prompt,
        return_tensors="pt",
        max_length=_MAX_INPUT_LENGTH,
        truncation=True,
    )
    outputs = _local_model.generate(
        **inputs,
        max_length=_MAX_OUTPUT_LENGTH,
        num_beams=_NUM_BEAMS,
        repetition_penalty=_REPETITION_PENALTY,
        no_repeat_ngram_size=_NO_REPEAT_NGRAM_SIZE,
        early_stopping=True,
    )
    decoded = _local_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    for prefix in ("pertanyaan:", "Pertanyaan:", "PERTANYAAN:"):
        if decoded.lower().startswith(prefix.lower()):
            decoded = decoded[len(prefix):].strip()
            break
    if "?" in decoded:
        decoded = decoded.split("?", 1)[0].strip() + "?"
    if decoded and decoded[0].islower():
        decoded = decoded[0].upper() + decoded[1:]
    if decoded and decoded[-1] not in "?.!":
        decoded += "?"
    return decoded


def _is_question_quality_acceptable(question: str) -> bool:
    stripped = question.strip()
    if len(stripped) < 15:
        return False
    words = [w for w in stripped.split() if any(c.isalpha() for c in w)]
    if len(words) < 3:
        return False
    if not any(len("".join(c for c in w if c.isalpha())) >= 5 for w in words):
        return False
    letters = [c for c in stripped.lower() if c.isalpha()]
    if not letters:
        return False
    most_common = max(letters, key=letters.count)
    if letters.count(most_common) / len(letters) > 0.5:
        return False
    return True


def _generate_locally(material_text: str) -> list[dict]:
    """Local CPU fallback when HF Space unavailable."""
    passages = _split_passages(material_text)
    if len(passages) < 3:
        raise RuntimeError("Material too short or homogeneous")

    keywords_pool = _extract_keywords(material_text)
    if len(keywords_pool) < 4:
        raise RuntimeError("Not enough distinct keywords for distractors")

    rng = random.Random(abs(hash(material_text)) & 0xFFFFFFFF)
    questions: list[dict] = []

    for i, passage in enumerate(passages):
        try:
            q_text = _generate_local_question(passage)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ml.generator: local question gen failed for passage %d: %s", i, exc)
            continue

        if not _is_question_quality_acceptable(q_text):
            logger.info(
                "ml.generator: skipping low-quality output for passage %d: %r",
                i,
                q_text[:60],
            )
            continue

        passage_keywords = _extract_keywords(passage)
        if not passage_keywords:
            continue
        correct = max(passage_keywords, key=len)

        distractors = _pick_similar_length_distractors(correct, keywords_pool, 3)
        if len(distractors) < 3:
            continue
        options = [correct, *distractors]
        rng.shuffle(options)
        correct_idx = options.index(correct)

        questions.append({
            "question": q_text,
            "options": options,
            "correct_option_index": correct_idx,
        })

        if len(questions) >= _NUM_QUESTIONS:
            break

    if not questions:
        raise RuntimeError("Failed to generate any valid questions locally")
    logger.info("ml.generator: local CPU produced %d questions", len(questions))
    return questions


if __name__ == "__main__":
    sample = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    print(f"HF_SPACE_URL: {_HF_SPACE_URL or '(not set)'}")
    if not is_available():
        print("Both HF Space and local model unavailable")
    else:
        print(f"Generating quiz from sample ({len(sample)} chars)...")
        try:
            quiz = generate(sample)
            for i, q in enumerate(quiz, 1):
                print(f"\nQ{i}: {q['question']}")
                for j, opt in enumerate(q["options"]):
                    marker = " ✓" if j == q["correct_option_index"] else "  "
                    print(f" {chr(65 + j)}.{marker} {opt}")
        except RuntimeError as exc:
            print(f"Failed: {exc}")
