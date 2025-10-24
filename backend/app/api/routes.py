"""API router configuration."""
from __future__ import annotations

from fastapi import APIRouter

from . import health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
