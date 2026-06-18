from sqlalchemy import String, Date, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import date, datetime
import uuid

from app.models.base import Base, TimestampMixin


class WeeklyReport(Base, TimestampMixin):
    __tablename__ = "weekly_reports"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)

    week_of: Mapped[date] = mapped_column(Date, index=True)
    report_data: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, published
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_via: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    user = relationship("User", back_populates="weekly_reports")
