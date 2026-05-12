"""Asahlagi Quiz Generator — Hugging Face Space (FastAPI + IndoT5).

Hosted at: https://<username>-asahlagi-quizgen.hf.space

Endpoints:
    GET  /            — health check
    POST /generate    — generate quiz from material text

The local backend (backend/app/services/quiz_generator.py) calls this Space.
If unreachable, backend falls back to local CPU inference, then rule-based.
"""

from __future__ import annotations

import logging
import random
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Config
# ============================================================================

MODEL_NAME = "Wikidepia/IndoT5-base"
MAX_INPUT_LENGTH = 512
MAX_OUTPUT_LENGTH = 48
NUM_BEAMS = 4
REPETITION_PENALTY = 1.8
NO_REPEAT_NGRAM_SIZE = 3
NUM_QUESTIONS = 5


# ============================================================================
# Lifespan: load model once at startup
# ============================================================================

_tokenizer = None
_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model at startup, before any request comes in."""
    global _tokenizer, _model
    from transformers import T5ForConditionalGeneration, T5Tokenizer

    logger.info("Loading IndoT5 from HF Hub: %s", MODEL_NAME)
    _tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    _model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    _model.eval()
    logger.info(
        "Model loaded (%dM params)",
        sum(p.numel() for p in _model.parameters()) // 1_000_000,
    )
    yield
    # On shutdown — nothing to clean up
    logger.info("Shutting down")


app = FastAPI(
    title="Asahlagi Quiz Generator (HF Space)",
    description="Indonesian question generator using fine-tunable IndoT5",
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================================
# Models
# ============================================================================


class GenerateRequest(BaseModel):
    material_text: str = Field(..., min_length=100, max_length=20_000)


class GeneratedQuestion(BaseModel):
    question: str
    options: list[str]
    correct_option_index: int


class GenerateResponse(BaseModel):
    questions: list[GeneratedQuestion]


# ============================================================================
# Inference helpers (mirror local ml/generator/inference.py)
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


def _split_passages(text: str, n: int = NUM_QUESTIONS) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= n:
        return sentences[:n]
    step = max(1, len(sentences) // n)
    return [sentences[i * step] for i in range(n) if i * step < len(sentences)]


def _generate_question_for_passage(passage: str) -> str:
    if _model is None or _tokenizer is None:
        raise RuntimeError("Model not loaded")

    prompt = f"buat pertanyaan: {passage}"
    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        max_length=MAX_INPUT_LENGTH,
        truncation=True,
    )
    outputs = _model.generate(
        **inputs,
        max_length=MAX_OUTPUT_LENGTH,
        num_beams=NUM_BEAMS,
        repetition_penalty=REPETITION_PENALTY,
        no_repeat_ngram_size=NO_REPEAT_NGRAM_SIZE,
        early_stopping=True,
    )
    decoded = _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # Clean up output (same logic as local inference)
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


def _is_quality_acceptable(question: str) -> bool:
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


# ============================================================================
# Routes
# ============================================================================


@app.get("/")
async def root():
    return {
        "service": "asahlagi-quizgen",
        "model": MODEL_NAME,
        "status": "ready" if _model is not None else "loading",
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if _model is None or _tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not yet loaded")

    text = req.material_text.strip()
    passages = _split_passages(text)
    if len(passages) < 3:
        raise HTTPException(status_code=400, detail="Material too short or homogeneous")

    keywords_pool = _extract_keywords(text)
    if len(keywords_pool) < 4:
        raise HTTPException(status_code=400, detail="Not enough distinct keywords")

    rng = random.Random(abs(hash(text)) & 0xFFFFFFFF)
    questions: list[GeneratedQuestion] = []

    for i, passage in enumerate(passages):
        try:
            q_text = _generate_question_for_passage(passage)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Question gen failed for passage %d: %s", i, exc)
            continue

        if not _is_quality_acceptable(q_text):
            logger.info("Skipping low-quality output for passage %d: %r", i, q_text[:60])
            continue

        passage_keywords = _extract_keywords(passage)
        if not passage_keywords:
            continue
        correct = max(passage_keywords, key=len)

        distractor_pool = [k for k in keywords_pool if k.lower() != correct.lower()]
        if len(distractor_pool) < 3:
            continue
        distractors = rng.sample(distractor_pool, 3)
        options = [correct, *distractors]
        rng.shuffle(options)
        correct_idx = options.index(correct)

        questions.append(GeneratedQuestion(
            question=q_text,
            options=options,
            correct_option_index=correct_idx,
        ))

        if len(questions) >= NUM_QUESTIONS:
            break

    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate any valid questions")

    return GenerateResponse(questions=questions)
