"""Quiz endpoints — POST /quiz/generate and POST /quiz/submit.

Routes are intentionally thin (per ARCHITECTURE.md §5.2). They:
    - parse the request (Pydantic validation)
    - call ONE service function
    - shape the response (only when needed — submit_coordinator already
      returns the full response shape)

NO business logic lives here. NO try/except for generic exceptions —
the global exception handler in main.py catches ApiException and
unhandled exceptions.
"""

from fastapi import APIRouter

from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
)
from app.schemas.result import QuizSubmitResponse
from app.services import quiz_generator, quiz_storage, submit_coordinator

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/generate", response_model=QuizGenerateResponse)
def generate_quiz_endpoint(req: QuizGenerateRequest) -> QuizGenerateResponse:
    """POST /quiz/generate — see API.md §4.2."""
    quiz_internal = quiz_generator.generate_quiz(req.material_text)
    quiz_storage.save_quiz(quiz_internal)
    return QuizGenerateResponse(
        quiz_id=quiz_internal.quiz_id,
        questions=[q.to_public() for q in quiz_internal.questions],
        total_questions=quiz_internal.total_questions,
        generated_at=quiz_internal.generated_at,
    )


@router.post("/submit", response_model=QuizSubmitResponse)
def submit_quiz_endpoint(req: QuizSubmitRequest) -> QuizSubmitResponse:
    """POST /quiz/submit — see API.md §4.3."""
    return submit_coordinator.process_submission(
        quiz_id=req.quiz_id,
        answers=req.answers,
        time_taken_seconds=req.time_taken_seconds,
    )
