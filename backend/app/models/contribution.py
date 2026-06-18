from sqlalchemy import String, Text, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import date
import uuid

from app.models.base import Base, TimestampMixin


class Contribution(Base, TimestampMixin):
    __tablename__ = "contributions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)

    source: Mapped[str] = mapped_column(String(30))  # github, gitlab, jira, confluence
    source_instance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # cloud, enterprise, self
    contribution_type: Mapped[str] = mapped_column(String(30))  # pr_raised, pr_reviewed, ticket_created, ticket_assigned, doc_created, doc_updated

    external_id: Mapped[str] = mapped_column(String(200))  # PR number, ticket key, page id
    external_url: Mapped[str] = mapped_column(String(500), index=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # open, merged, closed, in_progress, done
    proof_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(default=False)

    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    week_of: Mapped[date] = mapped_column(Date, index=True)

    user = relationship("User", back_populates="contributions")
