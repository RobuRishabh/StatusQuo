import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.session import async_session
from app.services.collector_orchestrator import run_collection_for_all
from app.services.report_service import compile_all_reports
from app.delivery.router import DeliveryRouter

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def friday_report_job():
    """Runs every Friday at 6 PM EST: collect data, compile reports, deliver."""
    logger.info("Starting Friday weekly report job")
    async with async_session() as db:
        try:
            await run_collection_for_all(db)
            await db.commit()
        except Exception as e:
            logger.error(f"Collection phase failed: {e}")
            await db.rollback()

    async with async_session() as db:
        try:
            reports = await compile_all_reports(db)
            await db.commit()

            router = DeliveryRouter()
            await router.deliver_all(reports)
            await db.commit()

            logger.info(f"Friday report job complete: {len(reports)} reports delivered")
        except Exception as e:
            logger.error(f"Report/delivery phase failed: {e}")
            await db.rollback()


async def nightly_collection_job():
    """Runs nightly to keep contribution data fresh."""
    logger.info("Starting nightly collection job")
    async with async_session() as db:
        try:
            await run_collection_for_all(db)
            await db.commit()
            logger.info("Nightly collection complete")
        except Exception as e:
            logger.error(f"Nightly collection failed: {e}")
            await db.rollback()


def start_scheduler():
    scheduler.add_job(
        friday_report_job,
        CronTrigger(day_of_week="fri", hour=18, minute=0, timezone="US/Eastern"),
        id="friday_report",
        replace_existing=True,
    )

    scheduler.add_job(
        nightly_collection_job,
        CronTrigger(hour=2, minute=0, timezone="US/Eastern"),
        id="nightly_collection",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started: Friday 6PM EST reports, nightly 2AM collections")


def stop_scheduler():
    scheduler.shutdown()
