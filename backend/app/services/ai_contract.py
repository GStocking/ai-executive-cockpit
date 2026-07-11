from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from app.schemas.dashboard import DashboardSnapshot


@dataclass(frozen=True)
class AIStreamEvent:
    content: str | None = None
    evidence: list[dict] | None = None
    limitations: list[str] | None = None


class AIService(Protocol):
    async def stream(self, message: str, snapshot: DashboardSnapshot) -> AsyncIterator[AIStreamEvent]:
        """Yield transport-neutral AI events; raise transient errors for retry."""
        ...
