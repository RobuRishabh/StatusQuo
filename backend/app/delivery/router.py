import logging
from app.delivery.ui_delivery import UIDelivery
from app.delivery.email_delivery import EmailDelivery
from app.delivery.slack_delivery import SlackDelivery
from app.models.report import WeeklyReport

logger = logging.getLogger(__name__)


class DeliveryRouter:
    def __init__(self):
        self.channels = {
            "ui": UIDelivery(),
            "email": EmailDelivery(),
            "slack": SlackDelivery(),
        }
        self.active_channels = ["ui"]  # Phase 1: UI only

    async def deliver_all(self, reports: list[WeeklyReport]):
        for channel_name in self.active_channels:
            channel = self.channels.get(channel_name)
            if channel:
                try:
                    success = await channel.deliver(reports)
                    if success:
                        logger.info(f"Delivered via {channel_name}")
                    else:
                        logger.warning(f"Delivery via {channel_name} returned False")
                except Exception as e:
                    logger.error(f"Delivery via {channel_name} failed: {e}")
