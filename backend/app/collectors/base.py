from abc import ABC, abstractmethod
from datetime import date
from dataclasses import dataclass


@dataclass
class CollectedItem:
    source: str
    source_instance: str
    contribution_type: str
    external_id: str
    external_url: str
    title: str
    description: str | None = None
    status: str | None = None
    proof_url: str | None = None
    raw_metadata: dict | None = None


class BaseCollector(ABC):
    @abstractmethod
    async def collect(self, username: str, week_start: date, week_end: date) -> list[CollectedItem]:
        """Collect contributions for a user within a date range."""
        ...
