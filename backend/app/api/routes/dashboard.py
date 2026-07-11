from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.dashboard import DashboardSnapshot
from app.services.dashboard_service import dashboard_service

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardSnapshot)
async def get_dashboard(
    range_: Annotated[str, Query(alias="range", pattern="^(7d|30d|90d|ytd)$")] = "30d",
    region: Annotated[str, Query(min_length=1, max_length=30)] = "all",
    category: Annotated[str, Query(min_length=1, max_length=30)] = "all",
) -> DashboardSnapshot:
    return dashboard_service.get_snapshot(range_, region, category)
