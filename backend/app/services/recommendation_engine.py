"""Recommendation engine — generates an actionable next step in Indonesian.

OWNER: Desta (Backend — Logic, Insight & Recommendation)

Pure function. Use the templates in BRAND.md §7.7 as starting points.

Brand mechanic note (BRAND.md §6 + §7.7):
    The medium and low recommendations end with "asah lagi" — the brand
    name as a callback to the next user action. Preserve this when
    extending templates.
"""

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel

# Base templates from BRAND.md §7.7.
_BASE_TEMPLATES: dict[UnderstandingLevel, str] = {
    UnderstandingLevel.HIGH: (
        "Lanjut ke materi berikutnya, atau coba kuis dengan tingkat kesulitan lebih tinggi."
    ),
    UnderstandingLevel.MEDIUM: (
        "Tinjau ulang bagian yang masih ragu, lalu asah lagi dalam 1-2 hari."
    ),
    UnderstandingLevel.LOW: (
        "Baca ulang materi dari awal, fokus pada poin dasar, lalu asah lagi."
    ),
}


def generate_recommendation(
    level: UnderstandingLevel,
    eval_result: EvaluationResult,
) -> str:
    """Generate a 1-2 sentence Indonesian recommendation."""
    # TODO(Desta): consider sub-conditions for richer recommendations.
    # Example: many unanswered → "Coba alokasikan waktu lebih untuk setiap soal."
    _ = eval_result  # suppress unused warning until logic is added
    return _BASE_TEMPLATES[level]
