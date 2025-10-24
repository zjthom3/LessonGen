"""Health check endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Application health check")
def healthcheck() -> dict[str, str]:
    """Return a simple health response."""

    return {"status": "ok"}


@router.get("/version", summary="Application version")
def version() -> dict[str, str]:
    """Return the deployed application version."""

    return {"version": settings.app_version}
