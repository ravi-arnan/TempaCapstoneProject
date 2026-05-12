"""Quiz endpoints — text, URL, and PDF inputs.

Routes are intentionally thin (per ARCHITECTURE.md §5.2). They:
    - parse the request (Pydantic validation or multipart for PDF)
    - call extractor + generator services
    - shape the response

NO business logic lives here. NO try/except for generic exceptions —
the global exception handler in main.py catches ApiException and
unhandled exceptions.
"""

from fastapi import APIRouter, File, UploadFile

from app.schemas.quiz import (
    QuizGenerateFromUrlRequest,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
)
from app.schemas.result import QuizSubmitResponse
from app.services import (
    quiz_generator,
    quiz_storage,
    source_extractor,
    submit_coordinator,
)
from app.utils.errors import ApiException, MATERIAL_TOO_LONG

router = APIRouter(prefix="/quiz", tags=["quiz"])

# Hard limit on PDF file size — prevent abuse / OOM
MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


def _quiz_internal_to_response(quiz_internal) -> QuizGenerateResponse:
    """Strip correct_option_index for client transport."""
    return QuizGenerateResponse(
        quiz_id=quiz_internal.quiz_id,
        questions=[q.to_public() for q in quiz_internal.questions],
        total_questions=quiz_internal.total_questions,
        generated_at=quiz_internal.generated_at,
    )


# ============================================================================
# Text input — original endpoint
# ============================================================================


@router.post("/generate", response_model=QuizGenerateResponse)
def generate_quiz_endpoint(req: QuizGenerateRequest) -> QuizGenerateResponse:
    """POST /quiz/generate — see API.md §4.2."""
    quiz_internal = quiz_generator.generate_quiz(req.material_text)
    quiz_storage.save_quiz(quiz_internal)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# URL input — extract article, then generate
# ============================================================================


@router.post("/generate-from-url", response_model=QuizGenerateResponse)
def generate_from_url_endpoint(
    req: QuizGenerateFromUrlRequest,
) -> QuizGenerateResponse:
    """POST /quiz/generate-from-url — fetch article from URL, generate quiz.

    See API.md §4.4.
    """
    material_text = source_extractor.extract_text_from_url(req.url)
    quiz_internal = quiz_generator.generate_quiz(material_text)
    quiz_storage.save_quiz(quiz_internal)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# PDF input — extract text, then generate
# ============================================================================


@router.post("/generate-from-pdf", response_model=QuizGenerateResponse)
async def generate_from_pdf_endpoint(
    file: UploadFile = File(...),
) -> QuizGenerateResponse:
    """POST /quiz/generate-from-pdf — multipart PDF upload, generate quiz.

    See API.md §4.5.
    """
    # Read with size cap to avoid memory blowup on huge files
    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise ApiException(
            status_code=400,
            code=MATERIAL_TOO_LONG,
            detail=f"File PDF terlalu besar. Maksimal {MAX_PDF_BYTES // (1024 * 1024)} MB.",
        )

    material_text = source_extractor.extract_text_from_pdf(pdf_bytes)
    quiz_internal = quiz_generator.generate_quiz(material_text)
    quiz_storage.save_quiz(quiz_internal)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# Submit (no input-type variation — same flow for all)
# ============================================================================


@router.post("/submit", response_model=QuizSubmitResponse)
def submit_quiz_endpoint(req: QuizSubmitRequest) -> QuizSubmitResponse:
    """POST /quiz/submit — see API.md §4.3."""
    return submit_coordinator.process_submission(
        quiz_id=req.quiz_id,
        answers=req.answers,
        time_taken_seconds=req.time_taken_seconds,
    )
