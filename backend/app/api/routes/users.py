from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: str
    username: str
    display_name: str
    email: str | None = None
    avatar_url: str | None = None
    github_username: str | None = None
    gitlab_username: str | None = None
    jira_account_id: str | None = None
    confluence_account_id: str | None = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: str | None = None
    email: str | None = None
    github_username: str | None = None
    gitlab_username: str | None = None
    jira_account_id: str | None = None
    confluence_account_id: str | None = None


@router.get("/search", response_model=list[UserResponse])
async def search_users(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    pattern = f"%{q}%"
    result = await db.execute(
        select(User).where(
            or_(
                User.username.ilike(pattern),
                User.display_name.ilike(pattern),
                User.github_username.ilike(pattern),
                User.gitlab_username.ilike(pattern),
            )
        ).limit(20)
    )
    return result.scalars().all()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.add(current_user)
    await db.flush()
    return current_user


@router.get("/{username}", response_model=UserResponse)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
