from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date, datetime

from app.db.session import get_db
from app.models.report import WeeklyReport
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportResponse(BaseModel):
    id: str
    user_id: str
    week_of: date
    report_data: dict
    status: str
    published_at: datetime | None = None
    delivered_via: list[str] | None = None

    class Config:
        from_attributes = True


@router.get("/me", response_model=list[ReportResponse])
async def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WeeklyReport)
        .where(WeeklyReport.user_id == current_user.id)
        .order_by(WeeklyReport.week_of.desc())
    )
    return result.scalars().all()


@router.get("/user/{username}", response_model=list[ReportResponse])
async def get_user_reports(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(WeeklyReport)
        .where(WeeklyReport.user_id == user.id, WeeklyReport.status == "published")
        .order_by(WeeklyReport.week_of.desc())
    )
    return result.scalars().all()


@router.get("/week/{week_of}", response_model=list[ReportResponse])
async def get_reports_for_week(
    week_of: date,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WeeklyReport)
        .where(WeeklyReport.week_of == week_of, WeeklyReport.status == "published")
        .order_by(WeeklyReport.created_at.desc())
    )
    return result.scalars().all()


@router.post("/trigger-collection")
async def trigger_collection(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger data collection for the current user."""
    from app.services.collector_orchestrator import run_collection_for_user
    await run_collection_for_user(current_user, db)
    return {"detail": "Collection triggered"}


@router.post("/trigger-report")
async def trigger_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger report generation for the current user."""
    from app.services.report_service import compile_report_for_user
    report = await compile_report_for_user(current_user, db)
    return {"detail": "Report generated", "report_id": report.id}
