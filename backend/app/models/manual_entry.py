from sqlalchemy import String, Text, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import date
import uuid

from app.models.base import Base, TimestampMixin


class ManualEntry(Base, TimestampMixin):
    __tablename__ = "manual_entries"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)

    entry_type: Mapped[str] = mapped_column(String(30))  # blog, talk, award, org_membership, other
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proof_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    proof_photos: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    event_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    week_of: Mapped[date] = mapped_column(Date, index=True)

    user = relationship("User", back_populates="manual_entries")
