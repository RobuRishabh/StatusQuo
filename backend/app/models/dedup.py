from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
import uuid

from app.models.base import Base, TimestampMixin


class DedupLog(Base, TimestampMixin):
    __tablename__ = "dedup_log"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contribution_id: Mapped[str] = mapped_column(
        String, ForeignKey("contributions.id"), index=True
    )
    duplicate_of_id: Mapped[str] = mapped_column(
        String, ForeignKey("contributions.id"), index=True
    )
    match_reason: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
