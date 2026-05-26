"""Gamification persistence service.

Ties the pure XP/achievement engines to the database. Each public function
manages its own transaction via get_session().

OWNER: Ariq (data/persistence) + Desta (rules via xp_engine/achievements).
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select

from app.db.models import Achievement, QuizAttempt, User, UserStats
from app.db.session import get_session
from app.services import achievements as ach
from app.services import xp_engine


def _get_or_create_user(session, device_id: str) -> User:
    user = session.scalar(select(User).where(User.device_id == device_id))
    if user is None:
        user = User(device_id=device_id)
        session.add(user)
        session.flush()  # assign user.id
        session.add(UserStats(user_id=user.id))
        session.flush()
    return user


def _get_or_create_stats(session, user_id) -> UserStats:
    stats = session.get(UserStats, user_id)
    if stats is None:
        stats = UserStats(user_id=user_id)
        session.add(stats)
        session.flush()
    return stats


def _stats_payload(stats: UserStats) -> dict:
    return {
        "total_xp": stats.total_xp,
        "level": stats.level,
        "xp_into_level": xp_engine.xp_into_level(stats.total_xp),
        "xp_for_next_level": xp_engine.xp_for_next_level(stats.total_xp),
        "current_streak": stats.current_streak,
        "longest_streak": stats.longest_streak,
    }


def record_attempt(
    device_id: str,
    quiz_id: str,
    score: int,
    understanding_level: str,
    today: date | None = None,
) -> dict:
    """Record a completed quiz: update XP/streak/level, unlock achievements.
    Grants +50 XP bonus for the first successful Daily Challenge of the day.
    """
    today = today or date.today()
    with get_session() as session:
        user = _get_or_create_user(session, device_id)
        stats = _get_or_create_stats(session, user.id)

        new_streak = xp_engine.next_streak(
            stats.current_streak, stats.last_active_date, today
        )
        xp_base = xp_engine.compute_xp(score, new_streak)
        xp_earned = xp_base

        # Daily Challenge bonus XP logic
        is_daily = quiz_id.startswith("daily-")
        daily_bonus_earned = 0
        if is_daily:
            # Check if this exact daily quiz has already been attempted by this user
            already_attempted = session.scalar(
                select(func.count(QuizAttempt.id))
                .where(QuizAttempt.user_id == user.id)
                .where(QuizAttempt.quiz_id == quiz_id)
            ) > 0
            
            if not already_attempted:
                daily_bonus_earned = 50
                xp_earned += daily_bonus_earned

        old_level = stats.level
        stats.total_xp += xp_earned
        stats.level = xp_engine.level_for_xp(stats.total_xp)
        stats.current_streak = new_streak
        stats.longest_streak = max(stats.longest_streak, new_streak)
        stats.last_active_date = today

        session.add(
            QuizAttempt(
                user_id=user.id,
                quiz_id=quiz_id,
                score=score,
                understanding_level=understanding_level,
                xp_earned=xp_earned,
            )
        )
        session.flush()

        total_attempts = session.scalar(
            select(func.count(QuizAttempt.id)).where(QuizAttempt.user_id == user.id)
        )

        ctx = ach.AchievementContext(
            total_xp=stats.total_xp,
            level=stats.level,
            current_streak=stats.current_streak,
            longest_streak=stats.longest_streak,
            total_attempts=total_attempts or 0,
            last_score=score,
        )
        earned_codes = ach.evaluate(ctx)

        already = set(
            session.scalars(
                select(Achievement.badge_code).where(Achievement.user_id == user.id)
            ).all()
        )
        newly_unlocked: list[dict] = []
        for code in earned_codes:
            if code in already:
                continue
            session.add(Achievement(user_id=user.id, badge_code=code))
            definition = ach.ACHIEVEMENTS_BY_CODE[code]
            newly_unlocked.append(
                {
                    "code": definition.code,
                    "label": definition.label,
                    "description": definition.description,
                    "icon": definition.icon,
                    "unlocked_at": None,
                }
            )

        return {
            "xp_earned": xp_earned,
            "daily_bonus_earned": daily_bonus_earned,
            "leveled_up": stats.level > old_level,
            "new_level": stats.level,
            "stats": _stats_payload(stats),
            "newly_unlocked": newly_unlocked,
        }


def get_stats(device_id: str) -> dict:
    """Return current stats for a device. Creates a fresh user if unseen."""
    with get_session() as session:
        user = _get_or_create_user(session, device_id)
        stats = _get_or_create_stats(session, user.id)
        return _stats_payload(stats)


def get_history(device_id: str, limit: int = 10) -> list[dict]:
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        if user is None:
            return []
        rows = session.scalars(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user.id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
        ).all()
        return [
            {
                "quiz_id": r.quiz_id,
                "score": r.score,
                "understanding_level": r.understanding_level,
                "xp_earned": r.xp_earned,
                "completed_at": r.completed_at,
            }
            for r in rows
        ]


def get_achievements(device_id: str) -> list[dict]:
    """Return all badges with unlocked timestamps (locked ones have None)."""
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        unlocked: dict[str, object] = {}
        if user is not None:
            for row in session.scalars(
                select(Achievement).where(Achievement.user_id == user.id)
            ).all():
                unlocked[row.badge_code] = row.unlocked_at
        return [
            {
                "code": a.code,
                "label": a.label,
                "description": a.description,
                "icon": a.icon,
                "unlocked_at": unlocked.get(a.code),
            }
            for a in ach.ACHIEVEMENTS
        ]
