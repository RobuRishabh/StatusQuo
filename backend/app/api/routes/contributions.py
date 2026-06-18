from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.models.contribution import Contribution
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/contributions", tags=["contributions"])


class ContributionResponse(BaseModel):
    id: str
    user_id: str
    source: str
    source_instance: str | None = None
    contribution_type: str
    external_id: str
    external_url: str
    title: str
    description: str | None = None
    ai_summary: str | None = None
    status: str | None = None
    proof_url: str | None = None
    is_duplicate: bool
    week_of: date

    class Config:
        from_attributes = True


@router.get("/me", response_model=list[ContributionResponse])
async def get_my_contributions(
    week_of: date | None = None,
    source: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Contribution).where(
        Contribution.user_id == current_user.id,
        Contribution.is_duplicate == False,
    )
    if week_of:
        query = query.where(Contribution.week_of == week_of)
    if source:
        query = query.where(Contribution.source == source)
    query = query.order_by(Contribution.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/user/{username}", response_model=list[ContributionResponse])
async def get_user_contributions(
    username: str,
    week_of: date | None = None,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = select(Contribution).where(
        Contribution.user_id == user.id,
        Contribution.is_duplicate == False,
    )
    if week_of:
        query = query.where(Contribution.week_of == week_of)
    if source:
        query = query.where(Contribution.source == source)
    query = query.order_by(Contribution.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
