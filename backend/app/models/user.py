from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import uuid

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    github_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    gitlab_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    jira_account_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    confluence_account_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    auth_provider: Mapped[str] = mapped_column(String(20), default="github")
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    contributions = relationship("Contribution", back_populates="user", lazy="selectin")
    manual_entries = relationship("ManualEntry", back_populates="user", lazy="selectin")
    weekly_reports = relationship("WeeklyReport", back_populates="user", lazy="selectin")
