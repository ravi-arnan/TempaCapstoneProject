"""Gamification endpoints — XP, streak, level, history, achievements.

Identity is an anonymous device id sent in the `X-Device-Id` header
(generated client-side, stored in localStorage). No login required.

All endpoints require DATABASE_URL to be configured; otherwise they return
503 so the core quiz features keep working without a database.
"""

from __future__ import annotations

from fastapi import APIRouter, Header

from app.db.session import is_db_configured
from app.schemas.gamification import (
    AnalyticsResponse,
    HistoryResponse,
    RecordAttemptRequest,
    RecordAttemptResponse,
    StatsResponse,
)
from app.services import gamification_service
from app.utils.errors import ApiException

router = APIRouter(prefix="/gamification", tags=["gamification"])

GAMIFICATION_UNAVAILABLE = "GAMIFICATION_UNAVAILABLE"
DEVICE_ID_REQUIRED = "DEVICE_ID_REQUIRED"


def _require_db() -> None:
    if not is_db_configured():
        raise ApiException(
            status_code=503,
            code=GAMIFICATION_UNAVAILABLE,
            detail="Fitur progres belum aktif. Hubungi pengelola aplikasi.",
        )


def _require_device_id(x_device_id: str | None) -> str:
    if not x_device_id or not x_device_id.strip():
        raise ApiException(
            status_code=400,
            code=DEVICE_ID_REQUIRED,
            detail="Identitas perangkat tidak ditemukan. Muat ulang halaman.",
        )
    return x_device_id.strip()


@router.post("/record-attempt", response_model=RecordAttemptResponse)
def record_attempt_endpoint(
    req: RecordAttemptRequest,
    x_device_id: str | None = Header(default=None),
) -> RecordAttemptResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    result = gamification_service.record_attempt(
        device_id=device_id,
        quiz_id=req.quiz_id,
        score=req.score,
        understanding_level=req.understanding_level,
    )
    return RecordAttemptResponse(**result)


@router.get("/stats", response_model=StatsResponse)
def stats_endpoint(
    x_device_id: str | None = Header(default=None),
) -> StatsResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return StatsResponse(**gamification_service.get_stats(device_id))


@router.get("/history", response_model=HistoryResponse)
def history_endpoint(
    x_device_id: str | None = Header(default=None),
    limit: int = 10,
) -> HistoryResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    limit = max(1, min(limit, 50))
    return HistoryResponse(
        summary=gamification_service.get_history_summary(device_id),
        items=gamification_service.get_history(device_id, limit),
    )


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics_endpoint(
    x_device_id: str | None = Header(default=None),
) -> AnalyticsResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return AnalyticsResponse(**gamification_service.get_analytics(device_id))


@router.get("/achievements")
def achievements_endpoint(
    x_device_id: str | None = Header(default=None),
) -> list[dict]:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return gamification_service.get_achievements(device_id)
