import logging
from app.delivery.base import BaseDelivery
from app.models.report import WeeklyReport

logger = logging.getLogger(__name__)


class UIDelivery(BaseDelivery):
    async def deliver(self, reports: list[WeeklyReport]) -> bool:
        for report in reports:
            if report.delivered_via is None:
                report.delivered_via = []
            if "ui" not in report.delivered_via:
                report.delivered_via.append("ui")
            logger.info(f"Report for {report.user_id} available in UI")
        return True
