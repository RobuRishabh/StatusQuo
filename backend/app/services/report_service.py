import logging
from datetime import date, timedelta, datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.contribution import Contribution
from app.models.manual_entry import ManualEntry
from app.models.report import WeeklyReport

logger = logging.getLogger(__name__)


def get_current_week_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


async def compile_report_for_user(user: User, db: AsyncSession) -> WeeklyReport:
    week_of = get_current_week_monday()

    existing = await db.execute(
        select(WeeklyReport).where(
            WeeklyReport.user_id == user.id,
            WeeklyReport.week_of == week_of,
        )
    )
    report = existing.scalar_one_or_none()

    contribs_result = await db.execute(
        select(Contribution).where(
            Contribution.user_id == user.id,
            Contribution.week_of == week_of,
            Contribution.is_duplicate == False,
        ).order_by(Contribution.source, Contribution.contribution_type)
    )
    contributions = contribs_result.scalars().all()

    manuals_result = await db.execute(
        select(ManualEntry).where(
            ManualEntry.user_id == user.id,
            ManualEntry.week_of == week_of,
        ).order_by(ManualEntry.entry_type)
    )
    manual_entries = manuals_result.scalars().all()

    prs_raised = [_contrib_to_dict(c) for c in contributions if c.contribution_type in ("pr_raised", "mr_raised")]
    prs_reviewed = [_contrib_to_dict(c) for c in contributions if c.contribution_type in ("pr_reviewed", "mr_reviewed")]
    tickets = [_contrib_to_dict(c) for c in contributions if c.contribution_type in ("ticket_created", "ticket_assigned")]
    docs = [_contrib_to_dict(c) for c in contributions if c.contribution_type in ("doc_created", "doc_updated")]
    manual_items = [_manual_to_dict(m) for m in manual_entries]

    report_data = {
        "user": {
            "username": user.username,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
        },
        "week_of": str(week_of),
        "summary": {
            "total_prs_raised": len(prs_raised),
            "total_prs_reviewed": len(prs_reviewed),
            "total_tickets": len(tickets),
            "total_docs": len(docs),
            "total_manual_entries": len(manual_items),
        },
        "sections": {
            "prs_raised": prs_raised,
            "prs_reviewed": prs_reviewed,
            "jira_tickets": tickets,
            "confluence_docs": docs,
            "manual_entries": manual_items,
        },
    }

    if report:
        report.report_data = report_data
        report.status = "published"
        report.published_at = datetime.now(timezone.utc)
    else:
        report = WeeklyReport(
            user_id=user.id,
            week_of=week_of,
            report_data=report_data,
            status="published",
            published_at=datetime.now(timezone.utc),
            delivered_via=["ui"],
        )
        db.add(report)

    await db.flush()
    logger.info(f"Report compiled for {user.username} (week of {week_of})")
    return report


def _contrib_to_dict(c: Contribution) -> dict:
    return {
        "id": c.id,
        "source": c.source,
        "type": c.contribution_type,
        "title": c.title,
        "summary": c.ai_summary or c.title,
        "url": c.external_url,
        "status": c.status,
        "proof_url": c.proof_url,
    }


def _manual_to_dict(m: ManualEntry) -> dict:
    return {
        "id": m.id,
        "type": m.entry_type,
        "title": m.title,
        "description": m.description,
        "proof_url": m.proof_url,
        "photos": m.proof_photos or [],
        "event_date": str(m.event_date) if m.event_date else None,
    }


async def compile_all_reports(db: AsyncSession):
    result = await db.execute(select(User).where(User.is_active == True))
    users = result.scalars().all()
    reports = []
    for user in users:
        try:
            report = await compile_report_for_user(user, db)
            reports.append(report)
        except Exception as e:
            logger.error(f"Report compilation failed for {user.username}: {e}")
    return reports
