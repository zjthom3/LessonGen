"""Analytics API endpoints."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_session
from app.schemas import AnalyticsSummaryResponse
from app.services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse, status_code=status.HTTP_200_OK)
def analytics_summary(
    days: int = Query(30, ge=1, le=90),
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_session),
) -> AnalyticsSummaryResponse:
    service = AnalyticsService(db)
    summary = service.get_summary(current_user.tenant_id, days=days)
    return AnalyticsSummaryResponse(**asdict(summary))
