import asyncio
import logging
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.contribution import Contribution
from app.collectors.github_collector import get_github_collectors
from app.collectors.gitlab_collector import get_gitlab_collectors
from app.collectors.jira_collector import get_jira_collector
from app.collectors.confluence_collector import get_confluence_collector
from app.collectors.base import CollectedItem
from app.services.summarizer_service import generate_summary
from app.services.dedup_service import run_dedup_for_user

logger = logging.getLogger(__name__)


def get_current_week_range() -> tuple[date, date]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday


async def run_collection_for_user(user: User, db: AsyncSession):
    week_start, week_end = get_current_week_range()
    logger.info(f"Collecting for {user.username} ({week_start} to {week_end})")

    all_items: list[CollectedItem] = []

    tasks = []

    if user.github_username:
        for collector in get_github_collectors():
            tasks.append(collector.collect(user.github_username, week_start, week_end))

    if user.gitlab_username:
        for collector in get_gitlab_collectors():
            tasks.append(collector.collect(user.gitlab_username, week_start, week_end))

    jira_collector = get_jira_collector()
    if jira_collector:
        username = user.jira_account_id or user.email or user.username
        tasks.append(jira_collector.collect(username, week_start, week_end))

    confluence_collector = get_confluence_collector()
    if confluence_collector:
        username = user.confluence_account_id or user.email or user.username
        tasks.append(confluence_collector.collect(username, week_start, week_end))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Collector error: {result}")
            continue
        all_items.extend(result)

    logger.info(f"Collected {len(all_items)} items for {user.username}")

    for item in all_items:
        existing = await db.execute(
            select(Contribution).where(
                Contribution.user_id == user.id,
                Contribution.external_url == item.external_url,
                Contribution.week_of == week_start,
            )
        )
        if existing.scalar_one_or_none():
            continue

        item_type_map = {
            "pr_raised": "pull request",
            "pr_reviewed": "pull request review",
            "mr_raised": "merge request",
            "mr_reviewed": "merge request review",
            "ticket_created": "Jira ticket",
            "ticket_assigned": "Jira ticket",
            "doc_created": "Confluence page",
            "doc_updated": "Confluence page update",
        }
        ai_summary = await generate_summary(
            item.title,
            item.description,
            item_type_map.get(item.contribution_type, "contribution"),
        )

        contribution = Contribution(
            user_id=user.id,
            source=item.source,
            source_instance=item.source_instance,
            contribution_type=item.contribution_type,
            external_id=item.external_id,
            external_url=item.external_url,
            title=item.title,
            description=item.description,
            ai_summary=ai_summary,
            status=item.status,
            proof_url=item.proof_url,
            raw_metadata=item.raw_metadata,
            week_of=week_start,
        )
        db.add(contribution)

    await db.flush()
    await run_dedup_for_user(user.id, week_start, db)


async def run_collection_for_all(db: AsyncSession):
    result = await db.execute(select(User).where(User.is_active == True))
    users = result.scalars().all()
    for user in users:
        try:
            await run_collection_for_user(user, db)
        except Exception as e:
            logger.error(f"Collection failed for {user.username}: {e}")
