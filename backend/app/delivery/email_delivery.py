import logging
from app.delivery.base import BaseDelivery
from app.models.report import WeeklyReport

logger = logging.getLogger(__name__)


class EmailDelivery(BaseDelivery):
    """Stubbed email delivery for Phase 2.

    Production implementation will use SendGrid or AWS SES to blast
    weekly reports to the org mailing list.
    """

    async def deliver(self, reports: list[WeeklyReport]) -> bool:
        logger.info(f"[STUB] Email delivery would send {len(reports)} reports")
        # Phase 2: SendGrid / SES integration
        # for report in reports:
        #     html = render_report_email(report)
        #     send_email(to=org_mailing_list, subject=f"Weekly Status - {report.week_of}", html=html)
        return True
