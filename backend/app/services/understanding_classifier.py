"""Understanding classifier — maps EvaluationResult to UnderstandingLevel.

OWNER: Desta (Backend — Logic, Insight & Recommendation)

Pure function — rule-based per CLAUDE.md and PRD.md §15.

This file currently contains a PLACEHOLDER implementation following the
rules described in PRD.md §15. Desta should review and refine — e.g.,
add sub-conditions for "high score but slow time" or "low score with
many unanswered" to make insights and recommendations richer.
"""

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel

# Tunable thresholds — Desta, adjust based on real test runs.
HIGH_SCORE_THRESHOLD = 80
MEDIUM_SCORE_THRESHOLD = 50

# "Reasonable" pace: 60 seconds per question. The high-tier requires that
# the user finish within 1.5x of this baseline; otherwise their pace
# suggests hesitation and we downgrade them to medium.
SECONDS_PER_QUESTION_BASELINE = 60
HIGH_TIME_MULTIPLIER = 1.5


def classify(eval_result: EvaluationResult) -> UnderstandingLevel:
    """Apply rule-based classification.

    Rules (per PRD.md §15):
        - HIGH:   score >= 80 AND time within 1.5x of baseline pace
        - MEDIUM: score >= 50 (or HIGH score with slow pace)
        - LOW:    everything else
    """
    score = eval_result.score_percentage
    time = eval_result.time_taken_seconds
    total = eval_result.total_questions

    reasonable_time = total * SECONDS_PER_QUESTION_BASELINE
    time_within_high_window = time <= reasonable_time * HIGH_TIME_MULTIPLIER

    if score >= HIGH_SCORE_THRESHOLD and time_within_high_window:
        return UnderstandingLevel.HIGH
    if score >= MEDIUM_SCORE_THRESHOLD:
        return UnderstandingLevel.MEDIUM
    return UnderstandingLevel.LOW
