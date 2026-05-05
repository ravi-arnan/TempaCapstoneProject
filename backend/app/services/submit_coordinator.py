"""Submit pipeline orchestrator.

Per ARCHITECTURE.md §9: orchestrates the full submit flow —
get quiz from storage → evaluate → classify → insight → recommend → response.

This module is intentionally thin. It does NOT implement any business
logic; it just wires together the services that do.

OWNER: orchestrator (any backend dev — change with team agreement).
"""

from datetime import datetime, timezone

from app.schemas.internal import EvaluationResult
from app.schemas.quiz import Answer
from app.schemas.result import (
    ChartData,
    QuizSubmitResponse,
    ScoreSummary,
)
from app.services import (
    insight_engine,
    quiz_evaluator,
    quiz_storage,
    recommendation_engine,
    understanding_classifier,
)
from app.utils.errors import ApiException, QUIZ_NOT_FOUND


def process_submission(
    quiz_id: str,
    answers: list[Answer],
    time_taken_seconds: int,
) -> QuizSubmitResponse:
    """End-to-end submit pipeline.

    Raises ApiException for any validation/business error. The route
    handler does not need to catch — the global exception handler in
    main.py converts ApiException into the JSON envelope.
    """
    quiz = quiz_storage.get_quiz(quiz_id)
    if quiz is None:
        raise ApiException(
            status_code=404,
            code=QUIZ_NOT_FOUND,
            detail="Kuis tidak ditemukan atau sudah kedaluwarsa. Mulai ulang dari halaman utama.",
        )

    eval_result: EvaluationResult = quiz_evaluator.evaluate(
        quiz=quiz,
        answers=answers,
        time_taken_seconds=time_taken_seconds,
    )
    level = understanding_classifier.classify(eval_result)
    insight = insight_engine.generate_insight(level, eval_result)
    recommendation = recommendation_engine.generate_recommendation(level, eval_result)

    return QuizSubmitResponse(
        quiz_id=quiz_id,
        score=ScoreSummary(
            score_percentage=eval_result.score_percentage,
            correct_count=eval_result.correct_count,
            wrong_count=eval_result.wrong_count,
            unanswered_count=eval_result.unanswered_count,
            total_questions=eval_result.total_questions,
        ),
        time_taken_seconds=time_taken_seconds,
        understanding_level=level,
        insight=insight,
        recommendation=recommendation,
        chart_data=ChartData(
            correct=eval_result.correct_count,
            wrong=eval_result.wrong_count,
            unanswered=eval_result.unanswered_count,
        ),
        submitted_at=datetime.now(timezone.utc),
    )
