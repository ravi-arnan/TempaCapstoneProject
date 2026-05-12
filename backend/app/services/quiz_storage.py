"""In-memory quiz store.

Implementation per ARCHITECTURE.md §7.1. Single-process, FIFO-evicted at
100 entries. Stores quizzes (with correct answers) keyed by quiz_id, so
that /quiz/submit can validate without trusting the client.

Migration path to SQLite is documented in ARCHITECTURE.md §7.2 — function
signatures here will not need to change.
"""

from collections import OrderedDict
from typing import Optional

from app.schemas.internal import QuizInternal

_MAX_QUIZZES = 100
_store: "OrderedDict[str, QuizInternal]" = OrderedDict()


def save_quiz(quiz: QuizInternal) -> str:
    """Store a quiz, returning its quiz_id. Evicts oldest if over capacity."""
    _store[quiz.quiz_id] = quiz
    if len(_store) > _MAX_QUIZZES:
        _store.popitem(last=False)
    return quiz.quiz_id


def get_quiz(quiz_id: str) -> Optional[QuizInternal]:
    """Retrieve a quiz by id, or None if not found."""
    return _store.get(quiz_id)


def clear_all() -> None:
    """Reset the store. Used by tests; do not call from production code."""
    _store.clear()
