"""Internal-only schemas — never exposed over HTTP.

Mirrors ARCHITECTURE.md §6. These types live entirely server-side and
hold the fields that must NOT leak to the client (e.g., correct answers).
"""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, conlist

from app.schemas.quiz import Question


class QuestionInternal(BaseModel):
    """Question with the correct answer attached. Stored server-side only."""

    id: int = Field(..., ge=1)
    type: str = Field(default="multiple_choice", pattern="^(multiple_choice|true_false|short_answer)$")
    question: str
    options: Optional[Annotated[list[str], conlist(str, min_length=2, max_length=4)]] = None
    correct_option_index: Optional[int] = Field(default=None, ge=0, le=3)
    correct_answer_text: Optional[str] = None

    def to_public(self) -> Question:
        """Strip the correct answer for client transport."""
        return Question(
            id=self.id,
            type=self.type,
            question=self.question,
            options=list(self.options) if self.options else None,
        )


class QuizInternal(BaseModel):
    """Full quiz as stored server-side."""

    quiz_id: str
    questions: list[QuestionInternal]
    generated_at: datetime
    # Full source material (capped at MAX_LENGTH in source_extractor = 20k chars).
    # Kept verbatim so "Asah Lagi" can regenerate a fresh quiz from the same input.
    source_material: str = Field(default="", max_length=20_000)
    difficulty: str = "medium"
    topic: str = "Umum"

    @property
    def total_questions(self) -> int:
        return len(self.questions)


class QuestionResult(BaseModel):
    """Per-question evaluation detail."""

    question_id: int
    selected_option_index: Optional[int]
    correct_option_index: Optional[int]
    text_answer: Optional[str] = None
    correct_answer_text: Optional[str] = None
    is_correct: bool
    is_unanswered: bool


class EvaluationResult(BaseModel):
    """Output of quiz_evaluator.evaluate(). Consumed by all 3 of Desta's modules.

    This is the handoff point between Ariq and Desta. If this shape changes,
    all three of Desta's modules (classifier, insight, recommendation) must
    be updated.
    """

    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    unanswered_count: int = Field(..., ge=0)
    total_questions: int = Field(..., ge=1)
    score_percentage: int = Field(..., ge=0, le=100)
    time_taken_seconds: int = Field(..., ge=0)
    average_time_per_question: float = Field(default=0.0, ge=0)
    question_results: list[QuestionResult]

    def model_post_init(self, __context: object) -> None:
        if self.average_time_per_question == 0.0 and self.total_questions > 0:
            object.__setattr__(
                self,
                "average_time_per_question",
                self.time_taken_seconds / self.total_questions,
            )