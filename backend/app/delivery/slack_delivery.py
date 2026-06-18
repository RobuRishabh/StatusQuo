import logging
from app.delivery.base import BaseDelivery
from app.models.report import WeeklyReport

logger = logging.getLogger(__name__)


class SlackDelivery(BaseDelivery):
    """Stubbed Slack delivery for Phase 2.

    Production implementation will use Slack Bot API to post
    a formatted weekly report to a designated channel.
    """

    async def deliver(self, reports: list[WeeklyReport]) -> bool:
        logger.info(f"[STUB] Slack delivery would post {len(reports)} reports")
        # Phase 2: Slack Bot API integration
        # for report in reports:
        #     blocks = render_report_slack_blocks(report)
        #     slack_client.chat_postMessage(channel=CHANNEL_ID, blocks=blocks)
        return True
