"""Public quiz-related schemas — mirror API.md §5.2-5.4.

These shapes are part of the HTTP contract. Any change here must be
reflected in:
- /API.md §5
- /frontend/src/types/quiz.ts
"""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, conlist


class Question(BaseModel):
    """Quiz question as exposed over HTTP. No correct_option_index here —
    that lives in QuestionInternal (schemas/internal.py)."""

    id: int = Field(..., ge=1)
    question: str = Field(..., min_length=1)
    options: Annotated[list[str], conlist(str, min_length=4, max_length=4)]


class Answer(BaseModel):
    """A user's answer for a single question."""

    question_id: int = Field(..., ge=1)
    selected_option_index: Optional[int] = Field(default=None, ge=0, le=3)


class QuizGenerateRequest(BaseModel):
    """POST /quiz/generate request body."""

    material_text: str = Field(..., min_length=1, max_length=20_000)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")


class QuizGenerateFromUrlRequest(BaseModel):
    """POST /quiz/generate-from-url request body."""

    url: str = Field(..., min_length=1, max_length=2048)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")


class QuizGenerateResponse(BaseModel):
    """POST /quiz/generate success response."""

    quiz_id: str
    questions: list[Question]
    total_questions: int = Field(..., ge=1)
    generated_at: datetime
    difficulty: str = Field(default="medium")


class QuizSubmitRequest(BaseModel):
    """POST /quiz/submit request body."""

    quiz_id: str
    answers: list[Answer]
    time_taken_seconds: int = Field(..., ge=0, le=7200)


class QuizRegenerateRequest(BaseModel):
    """POST /quiz/regenerate request body."""

    quiz_id: str
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
