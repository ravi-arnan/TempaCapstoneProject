"""FastAPI application entry point.

Wires up:
    - CORS middleware (per API.md §9)
    - Global exception handlers for ApiException + unhandled exceptions
    - Routers from app/routes/

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import os
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.routes import health, quiz
from app.utils.errors import ApiException, INTERNAL_ERROR


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return ["http://localhost:5173", "http://localhost:3000"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("asahlagi")


app = FastAPI(
    title="Asahlagi API",
    description="Asah lagi sampai paham. — capstone TP-G005 backend.",
    version=__version__,
)

# CORS — per API.md §9
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_origins(os.getenv("CORS_ALLOWED_ORIGINS")),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ============================================================================
# Exception handlers — per API.md §2 (response envelope + global error policy)
# ============================================================================


@app.exception_handler(ApiException)
async def api_exception_handler(_: Request, exc: ApiException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ada hambatan dari sisi kami. Coba lagi sebentar.",
            "code": INTERNAL_ERROR,
        },
    )


# ============================================================================
# Routers
# ============================================================================

app.include_router(health.router)
app.include_router(quiz.router)
