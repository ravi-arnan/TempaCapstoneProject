"""Quiz generator — turns learning material text into a quiz.

OWNER: Audry (Backend — Quiz Generator)

Strategy: rule-based, deterministic. Per CLAUDE.md and PRD.md, MVP avoids
LLM/NLP-heavy approaches. Use simple text processing (sentence splitting,
keyword extraction, distractor generation from material).

Output shape is QuizInternal (with correct_option_index per question).
The route handler then strips correct_option_index for the public response
via QuestionInternal.to_public().

See ARCHITECTURE.md §8 for the data flow this slots into.
"""

from app.schemas.internal import QuizInternal
from app.utils.errors import ApiException, MATERIAL_TOO_SHORT, QUIZ_GENERATION_FAILED

# Tunable: number of questions per generated quiz.
DEFAULT_QUESTION_COUNT = 5

# Minimum material length (after trim) for which generation is attempted.
# Validation also occurs at the Pydantic layer; this is a defense in depth.
MIN_MATERIAL_LENGTH = 100


def generate_quiz(material_text: str) -> QuizInternal:
    """Generate a multiple-choice quiz from raw material text.

    Args:
        material_text: learning material (already trimmed by caller)

    Returns:
        QuizInternal with `DEFAULT_QUESTION_COUNT` questions, each with
        exactly 4 options and one correct_option_index in [0, 3].

    Raises:
        ApiException(MATERIAL_TOO_SHORT) if text is too short to generate a
            sensible quiz.
        ApiException(QUIZ_GENERATION_FAILED) on any internal failure.
    """
    text = material_text.strip()
    if len(text) < MIN_MATERIAL_LENGTH:
        raise ApiException(
            status_code=400,
            code=MATERIAL_TOO_SHORT,
            detail="Materinya terlalu pendek. Tambahkan minimal 100 karakter agar sistem bisa membuat kuis.",
        )

    # TODO(Audry): implement quiz generation per CLAUDE.md/PRD.md guidance.
    # Suggested approach:
    #   1. Split text into sentences.
    #   2. Pick N sentences with sufficient information density.
    #   3. For each, build a "fill-in-the-blank" or "what does X mean"
    #      question with the correct answer + 3 distractors from the
    #      same material (or close variants).
    #   4. Shuffle option order and capture the correct_option_index.
    #   5. Return QuizInternal with a uuid4 quiz_id.
    #
    # While implementing, raise ApiException(QUIZ_GENERATION_FAILED) for
    # internal errors (don't let raw exceptions bubble up).
    raise ApiException(
        status_code=500,
        code=QUIZ_GENERATION_FAILED,
        detail="Gagal membuat kuis. Coba materi lain atau ulangi sebentar lagi.",
    )
