"""Insight engine — generates a 1-2 sentence Indonesian explanation.

OWNER: Desta (Backend — Logic, Insight & Recommendation)

Pure function. Use the templates in BRAND.md §7.6 as the starting point.

Voice rules (BRAND.md §6):
    - Honest: don't pretend the system is more sophisticated than it is
    - Encouraging but not cheesy: no "GREAT JOB!!!", no excessive emoji
    - Calm, focused: library-vibe, not arcade
    - Use "kamu" not "Anda"
"""

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel

# Base templates from BRAND.md §7.6.
# Desta can extend with sub-conditions (e.g., high score but slow time → custom variant).
_BASE_TEMPLATES: dict[UnderstandingLevel, str] = {
    UnderstandingLevel.HIGH: (
        "Skor tinggi dengan waktu pengerjaan efisien menunjukkan kamu menguasai konsep utama materi."
    ),
    UnderstandingLevel.MEDIUM: (
        "Kamu memahami sebagian besar materi, tapi ada beberapa konsep yang masih perlu diteguhkan."
    ),
    UnderstandingLevel.LOW: (
        "Banyak konsep dasar yang masih perlu dipelajari ulang sebelum kamu lanjut ke materi berikutnya."
    ),
}


def generate_insight(
    level: UnderstandingLevel,
    eval_result: EvaluationResult,
) -> str:
    """Generate a 1-2 sentence insight in Indonesian."""
    # TODO(Desta): consider sub-conditions before falling back to base.
    # Examples of refinements:
    #   - high score but slow time → "Kamu paham, tapi mungkin masih ragu di beberapa bagian."
    #   - low score with mostly unanswered → "Kamu belum mengerjakan sebagian besar soal."
    _ = eval_result  # suppress unused warning until logic is added
    return _BASE_TEMPLATES[level]
