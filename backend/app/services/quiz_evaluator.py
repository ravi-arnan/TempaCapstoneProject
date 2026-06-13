"""Quiz evaluator — computes score, counts, and per-question detail.

OWNER: Ariq (Backend — Data & Analisis)

Input:  QuizInternal (from quiz_storage) + list[Answer] + time_taken_seconds
Output: EvaluationResult — consumed by all 3 of Desta's modules

This is the handoff point between Audry's storage shape and Desta's logic.
If EvaluationResult shape changes, classifier/insight/recommendation must
all be updated. See ARCHITECTURE.md §6.3 and §10.

Pure function — no I/O, no globals. Testable with simple assertions.

NOTE: This file currently contains a PLACEHOLDER implementation. Ariq
should review and extend (e.g., per-topic stats, time-per-question
analysis with pandas if needed). The base scoring logic below is
relatively standard and Ariq can keep or replace it.
"""

import re

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
    """Score the user's answers against the stored quiz."""
    if len(answers) != quiz.total_questions:
        raise ApiException(
            status_code=400,
            code=ANSWERS_LENGTH_MISMATCH,
            detail="Ada ketidaksesuaian jumlah jawaban. Coba mulai kuis dari awal.",
        )

    try:
        questions_by_id = {q.id: q for q in quiz.questions}
        results: list[QuestionResult] = []
        correct = wrong = unanswered = 0

        for ans in answers:
            q = questions_by_id.get(ans.question_id)
            if q is None:
                raise ApiException(
                    status_code=400,
                    code=INVALID_QUESTION_ID,
                    detail="Soal tidak ditemukan dalam kuis. Coba mulai ulang.",
                )

            q_type = getattr(q, 'type', 'multiple_choice')
            
            if q_type == 'short_answer':
                is_unanswered = not ans.text_answer or not ans.text_answer.strip()
                is_correct = False
                if not is_unanswered and q.correct_answer_text:
                    # Simple string matching: ignore case and punctuation.
                    # NOTE (MVP): exact-match is acceptable here because
                    # short_answer blanks are always a single word extracted
                    # from the source material. For future improvement,
                    # consider fuzzy/Levenshtein matching for typo tolerance.
                    user_ans = re.sub(r'[^\w\s]', '', ans.text_answer).strip().lower()
                    correct_ans = re.sub(r'[^\w\s]', '', q.correct_answer_text).strip().lower()
                    is_correct = (user_ans == correct_ans)
            else:
                # handles multiple_choice and true_false
                is_unanswered = ans.selected_option_index is None
                is_correct = (
                    not is_unanswered
                    and ans.selected_option_index == q.correct_option_index
                )

            if is_correct:
                correct += 1
            elif is_unanswered:
                unanswered += 1
            else:
                wrong += 1

            results.append(
                QuestionResult(
                    question_id=q.id,
                    selected_option_index=ans.selected_option_index,
                    correct_option_index=q.correct_option_index,
                    text_answer=ans.text_answer,
                    correct_answer_text=q.correct_answer_text,
                    is_correct=is_correct,
                    is_unanswered=is_unanswered,
                )
            )

        total = quiz.total_questions
        score_percentage = round((correct / total) * 100) if total > 0 else 0
        # Bonus analytics: average time per question is useful for downstream
        # reporting or understanding pacing, but it is not required by the
        # core scoring contract.
        average_time_per_question = (
            round(time_taken_seconds / total, 1) if total > 0 else 0.0
        )

        return EvaluationResult(
            correct_count=correct,
            wrong_count=wrong,
            unanswered_count=unanswered,
            total_questions=total,
            score_percentage=score_percentage,
            time_taken_seconds=time_taken_seconds,
            average_time_per_question=average_time_per_question,
            question_results=results,
        )
    except ApiException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ApiException(
            status_code=500,
            code=EVALUATION_FAILED,
            detail="Gagal menganalisis hasil kuis. Coba kirim ulang sebentar lagi.",
        ) from exc
