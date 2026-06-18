from abc import ABC, abstractmethod
from app.models.report import WeeklyReport


class BaseDelivery(ABC):
    @abstractmethod
    async def deliver(self, reports: list[WeeklyReport]) -> bool:
        """Deliver compiled reports. Returns True on success."""
        ...
