"""Public schemas for gamification endpoints.

Any change here must be mirrored in frontend/src/types/gamification.ts.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class RecordAttemptRequest(BaseModel):
    """POST /gamification/record-attempt body."""

    quiz_id: str = Field(..., min_length=1, max_length=64)
    score: int = Field(..., ge=0, le=100)
    understanding_level: str = Field(..., min_length=1, max_length=16)


class StatsResponse(BaseModel):
    total_xp: int
    level: int
    xp_into_level: int
    xp_for_next_level: int
    current_streak: int
    longest_streak: int


class BadgeResponse(BaseModel):
    code: str
    label: str
    description: str
    icon: str
    unlocked_at: datetime | None = None


class RecordAttemptResponse(BaseModel):
    xp_earned: int
    daily_bonus_earned: int = 0
    leveled_up: bool
    new_level: int
    stats: StatsResponse
    newly_unlocked: list[BadgeResponse]


class HistoryItem(BaseModel):
    quiz_id: str
    score: int
    understanding_level: str
    xp_earned: int
    completed_at: datetime
    topic: str | None = None


class HistorySummary(BaseModel):
    total_quizzes: int
    average_score: int
    total_xp: int
    best_score: int
    worst_score: int
    most_recent_topic: str | None = None


class HistoryResponse(BaseModel):
    summary: HistorySummary | None = None
    items: list[HistoryItem]


class TrendPoint(BaseModel):
    date: date
    average_score: int
    attempt_count: int


class TopicMasteryItem(BaseModel):
    topic: str
    average_score: int
    attempt_count: int


class AnalyticsResponse(BaseModel):
    quiz_count: int
    average_score: int
    total_xp: int
    score_trend: list[TrendPoint]
    topic_mastery: list[TopicMasteryItem]
