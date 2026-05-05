"""Understanding classifier — maps EvaluationResult to UnderstandingLevel.

OWNER: Desta (Backend — Logic, Insight & Recommendation)

Pure function — rule-based per CLAUDE.md and PRD.md §15.

Inputs you have access to (from EvaluationResult):
    - score_percentage (0-100)
    - time_taken_seconds
    - correct_count, wrong_count, unanswered_count, total_questions

Output: UnderstandingLevel enum (HIGH | MEDIUM | LOW)

Reference rules (PRD.md §15 — adjust as you implement):
    - Tinggi (HIGH):  high score, low wrong count, time within reasonable bounds
    - Sedang (MEDIUM): moderate score OR good score with very long time
    - Rendah (LOW):   low score OR many wrong/unanswered
"""

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel


def classify(eval_result: EvaluationResult) -> UnderstandingLevel:
    """Apply rule-based classification.

    The function is pure: same input always produces same output.
    """
    # TODO(Desta): implement classification rules.
    #
    # Starting point (tweak thresholds as needed):
    #
    #   score = eval_result.score_percentage
    #   time = eval_result.time_taken_seconds
    #   total = eval_result.total_questions
    #
    #   # Rough heuristic: ~60s per question is "reasonable"
    #   reasonable_time = total * 60
    #
    #   if score >= 80 and time <= reasonable_time * 1.5:
    #       return UnderstandingLevel.HIGH
    #   if score >= 50:
    #       return UnderstandingLevel.MEDIUM
    #   return UnderstandingLevel.LOW
    raise NotImplementedError(
        "Desta: implement understanding classification per PRD.md §15"
    )
