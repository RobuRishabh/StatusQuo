from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date
from typing import Optional
import os
import uuid
import aiofiles

from app.config import get_settings
from app.db.session import get_db
from app.models.manual_entry import ManualEntry
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/manual-entries", tags=["manual_entries"])
settings = get_settings()


class ManualEntryResponse(BaseModel):
    id: str
    user_id: str
    entry_type: str
    title: str
    description: str | None = None
    proof_url: str | None = None
    proof_photos: list[str] | None = None
    event_date: date | None = None
    week_of: date

    class Config:
        from_attributes = True


class ManualEntryCreate(BaseModel):
    entry_type: str
    title: str
    description: str | None = None
    proof_url: str | None = None
    event_date: date | None = None


def get_current_week_monday() -> date:
    today = date.today()
    return today - __import__("datetime").timedelta(days=today.weekday())


@router.post("/", response_model=ManualEntryResponse)
async def create_manual_entry(
    entry: ManualEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manual_entry = ManualEntry(
        user_id=current_user.id,
        entry_type=entry.entry_type,
        title=entry.title,
        description=entry.description,
        proof_url=entry.proof_url,
        event_date=entry.event_date,
        week_of=get_current_week_monday(),
    )
    db.add(manual_entry)
    await db.flush()
    return manual_entry


@router.post("/{entry_id}/photos")
async def upload_photos(
    entry_id: str,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ManualEntry).where(
            ManualEntry.id == entry_id,
            ManualEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    upload_dir = os.path.join(settings.upload_dir, current_user.id)
    os.makedirs(upload_dir, exist_ok=True)

    photos = entry.proof_photos or []
    for file in files:
        ext = os.path.splitext(file.filename or "photo.jpg")[1]
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(upload_dir, filename)
        async with aiofiles.open(filepath, "wb") as f:
            content = await file.read()
            await f.write(content)
        photos.append(f"/uploads/{current_user.id}/{filename}")

    entry.proof_photos = photos
    db.add(entry)
    await db.flush()
    return {"photos": photos}


@router.get("/me", response_model=list[ManualEntryResponse])
async def get_my_manual_entries(
    week_of: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(ManualEntry).where(ManualEntry.user_id == current_user.id)
    if week_of:
        query = query.where(ManualEntry.week_of == week_of)
    query = query.order_by(ManualEntry.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/user/{username}", response_model=list[ManualEntryResponse])
async def get_user_manual_entries(
    username: str,
    week_of: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = select(ManualEntry).where(ManualEntry.user_id == user.id)
    if week_of:
        query = query.where(ManualEntry.week_of == week_of)
    query = query.order_by(ManualEntry.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.delete("/{entry_id}")
async def delete_manual_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ManualEntry).where(
            ManualEntry.id == entry_id,
            ManualEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    await db.delete(entry)
    return {"detail": "Deleted"}
