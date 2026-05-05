"""Quiz evaluator — computes score, counts, and per-question detail.

OWNER: Ariq (Backend — Data & Analisis)

Input:  QuizInternal (from quiz_storage) + list[Answer] + time_taken_seconds
Output: EvaluationResult — consumed by all 3 of Desta's modules

This is the handoff point between Audry's storage shape and Desta's logic.
If EvaluationResult shape changes, classifier/insight/recommendation must
all be updated. See ARCHITECTURE.md §6.3 and §10.

Pure function — no I/O, no globals. Testable with simple assertions.
"""

from app.schemas.internal import EvaluationResult, QuestionResult, QuizInternal
from app.schemas.quiz import Answer
from app.utils.errors import (
    ANSWERS_LENGTH_MISMATCH,
    ApiException,
    EVALUATION_FAILED,
    INVALID_QUESTION_ID,
)


def evaluate(
    quiz: QuizInternal,
    answers: list[Answer],
    time_taken_seconds: int,
) -> EvaluationResult:
    """Score the user's answers against the stored quiz.

    Validates:
        - len(answers) == quiz.total_questions
        - every Answer.question_id maps to a question in the quiz

    Computes:
        - correct_count, wrong_count, unanswered_count
        - score_percentage = round(correct / total * 100)
        - per-question result detail (selected vs correct vs unanswered)

    Raises:
        ApiException(ANSWERS_LENGTH_MISMATCH) on length mismatch
        ApiException(INVALID_QUESTION_ID) if an answer references a
            non-existent question
        ApiException(EVALUATION_FAILED) on any unexpected failure
    """
    if len(answers) != quiz.total_questions:
        raise ApiException(
            status_code=400,
            code=ANSWERS_LENGTH_MISMATCH,
            detail="Ada ketidaksesuaian jumlah jawaban. Coba mulai kuis dari awal.",
        )

    # TODO(Ariq): implement evaluator.
    #
    # Suggested skeleton:
    #
    #   q_by_id = {q.id: q for q in quiz.questions}
    #   results: list[QuestionResult] = []
    #   correct = wrong = unanswered = 0
    #
    #   for answer in answers:
    #       q = q_by_id.get(answer.question_id)
    #       if q is None:
    #           raise ApiException(400, INVALID_QUESTION_ID, "...")
    #
    #       is_unanswered = answer.selected_option_index is None
    #       is_correct = (
    #           not is_unanswered
    #           and answer.selected_option_index == q.correct_option_index
    #       )
    #
    #       if is_correct: correct += 1
    #       elif is_unanswered: unanswered += 1
    #       else: wrong += 1
    #
    #       results.append(QuestionResult(
    #           question_id=q.id,
    #           selected_option_index=answer.selected_option_index,
    #           correct_option_index=q.correct_option_index,
    #           is_correct=is_correct,
    #           is_unanswered=is_unanswered,
    #       ))
    #
    #   total = quiz.total_questions
    #   return EvaluationResult(
    #       correct_count=correct,
    #       wrong_count=wrong,
    #       unanswered_count=unanswered,
    #       total_questions=total,
    #       score_percentage=round(correct / total * 100),
    #       time_taken_seconds=time_taken_seconds,
    #       question_results=results,
    #   )
    raise ApiException(
        status_code=500,
        code=EVALUATION_FAILED,
        detail="Gagal menganalisis hasil kuis. Coba kirim ulang sebentar lagi.",
    )
