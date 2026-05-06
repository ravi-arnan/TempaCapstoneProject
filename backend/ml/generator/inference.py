"""Inference for the quiz generator (DL — fine-tuned IndoT5).

OWNER: Audry

Loads a fine-tuned T5 model from Hugging Face Hub at module import.
Inference happens on CPU at runtime (no GPU). First load downloads ~1GB
to ~/.cache/huggingface/.

Audry: after you train and push your model to HF Hub, update _MODEL_NAME
below to point to YOUR repo (e.g., "audry-asahlagi/indot5-quizgen-asahlagi").

If the model fails to load (network down, model not yet published, etc.),
this module sets _USE_DL = False and the wrapper service falls back to
rule-based generation.
"""

from __future__ import annotations

import logging
import random
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIG — Audry, edit this after pushing your fine-tuned model to HF Hub
# ============================================================================

# Replace with your own HF Hub repo after fine-tuning + pushing.
# Until then, fall back to the base pretrained model (lower quality).
_MODEL_NAME = "Wikidepia/IndoT5-base"
# Once Audry's fine-tuned model is published, change to:
# _MODEL_NAME = "audry-asahlagi/indot5-quizgen-asahlagi"

# Generation hyperparameters
_MAX_INPUT_LENGTH = 512
_MAX_OUTPUT_LENGTH = 64
_NUM_BEAMS = 4  # set to 1 for greedy (faster, slightly lower quality)
_NUM_QUESTIONS = 5

# ============================================================================
# Module-level state
# ============================================================================

_tokenizer = None
_model = None
_load_error: Optional[str] = None


def _load_model() -> None:
    """Try to load tokenizer + model from HF Hub. Set globals on success."""
    global _tokenizer, _model, _load_error
    try:
        from transformers import T5ForConditionalGeneration, T5Tokenizer

        logger.info("ml.generator: Loading IndoT5 from %s ...", _MODEL_NAME)
        _tokenizer = T5Tokenizer.from_pretrained(_MODEL_NAME)
        _model = T5ForConditionalGeneration.from_pretrained(_MODEL_NAME)
        _model.eval()  # inference mode
        logger.info(
            "ml.generator: Loaded IndoT5 from HF Hub: %s (params=%dM)",
            _MODEL_NAME,
            sum(p.numel() for p in _model.parameters()) // 1_000_000,
        )
    except Exception as exc:  # noqa: BLE001
        _load_error = f"{type(exc).__name__}: {exc}"
        logger.warning(
            "ml.generator: Failed to load model (%s) — fallback to rule-based",
            _load_error,
        )


# Load eagerly at import time
_load_model()


def is_available() -> bool:
    """Return True if the DL model is loaded and ready for inference."""
    return _model is not None and _tokenizer is not None


# ============================================================================
# Inference logic
# ============================================================================


def _generate_question_for_passage(passage: str) -> str:
    """Run T5 inference on one passage to generate a question."""
    if _model is None or _tokenizer is None:
        raise RuntimeError("Model not loaded")

    # Prompt format depends on how the model was fine-tuned.
    # Standard QG prompt for T5:
    prompt = f"buat pertanyaan: {passage}"

    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        max_length=_MAX_INPUT_LENGTH,
        truncation=True,
    )
    outputs = _model.generate(
        **inputs,
        max_length=_MAX_OUTPUT_LENGTH,
        num_beams=_NUM_BEAMS,
        early_stopping=True,
    )
    return _tokenizer.decode(outputs[0], skip_special_tokens=True)


# Simple keyword extractor for distractor selection (Audry can replace
# with smarter approach — e.g., embedding-based similarity).
_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{4,}")
_STOP_WORDS = frozenset({
    "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "ini",
    "itu", "atau", "adalah", "akan", "tidak", "juga", "dapat", "sebagai",
    "telah", "oleh", "dalam", "saat", "yaitu", "namun", "agar", "karena",
})


def _extract_keywords(text: str) -> list[str]:
    """Get unique non-stopword candidates."""
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


def _split_passages(text: str, n: int = _NUM_QUESTIONS) -> list[str]:
    """Split material into N passages for question generation."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= n:
        return sentences[:n]
    # Even-spaced selection: take every Nth sentence so questions cover the whole material
    step = max(1, len(sentences) // n)
    return [sentences[i * step] for i in range(n) if i * step < len(sentences)]


def generate(material_text: str) -> list[dict]:
    """Generate a quiz from material text.

    Returns:
        list of dicts with keys: question, options (4), correct_option_index (0-3)

    Raises:
        RuntimeError: if model isn't loaded. Caller should check is_available()
            and fall back to rule-based generation.
    """
    if not is_available():
        raise RuntimeError(
            f"ml.generator model not available: {_load_error}. "
            "Use rule-based fallback."
        )

    passages = _split_passages(material_text)
    if len(passages) < 3:
        raise RuntimeError("Material too short or homogeneous to generate questions")

    keywords_pool = _extract_keywords(material_text)
    if len(keywords_pool) < 4:
        raise RuntimeError("Not enough distinct keywords to generate distractors")

    rng = random.Random(abs(hash(material_text)) & 0xFFFFFFFF)

    questions: list[dict] = []
    for i, passage in enumerate(passages):
        try:
            generated_question = _generate_question_for_passage(passage)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ml.generator: question gen failed for passage %d: %s", i, exc)
            continue

        # Pick a correct answer keyword from the passage (longest non-stopword)
        passage_keywords = _extract_keywords(passage)
        if not passage_keywords:
            continue
        correct = max(passage_keywords, key=len)

        # Pick 3 distractors from the broader pool (different from correct)
        distractor_candidates = [k for k in keywords_pool if k.lower() != correct.lower()]
        if len(distractor_candidates) < 3:
            continue
        distractors = rng.sample(distractor_candidates, 3)

        options = [correct, *distractors]
        rng.shuffle(options)
        correct_idx = options.index(correct)

        questions.append({
            "question": generated_question,
            "options": options,
            "correct_option_index": correct_idx,
        })

        if len(questions) >= _NUM_QUESTIONS:
            break

    if not questions:
        raise RuntimeError("Failed to generate any valid questions")

    return questions


if __name__ == "__main__":
    # Smoke test
    if not is_available():
        print(f"Model not available: {_load_error}")
        print("Possible reasons:")
        print("  1. Network unavailable (HF Hub unreachable)")
        print("  2. Audry hasn't published the fine-tuned model yet")
        print("  3. transformers/torch not installed (run pip install -r requirements.txt)")
    else:
        sample = (
            "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
            "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
            "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
            "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
            "di stroma."
        )
        print(f"Generating quiz from sample material ({len(sample)} chars)...")
        try:
            quiz = generate(sample)
            for i, q in enumerate(quiz, 1):
                print(f"\nQ{i}: {q['question']}")
                for j, opt in enumerate(q["options"]):
                    marker = " ✓" if j == q["correct_option_index"] else "  "
                    print(f" {chr(65 + j)}.{marker} {opt}")
        except RuntimeError as exc:
            print(f"Failed: {exc}")
