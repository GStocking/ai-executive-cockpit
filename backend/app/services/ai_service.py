from collections.abc import AsyncIterator

from app.schemas.dashboard import DashboardSnapshot
from app.services.ai_contract import AIStreamEvent
from app.services.mock_ai import DemoMode, analyze_stream


class MockAIAdapter:
    """Adapts the transport-neutral mock agent to the backend AI contract."""

    @staticmethod
    def _mode(message: str) -> DemoMode:
        lowered = message.lower()
        if "模拟错误" in message or "transient-error" in lowered:
            return "error"
        if "模拟超时" in message or "timeout" in lowered:
            return "timeout"
        return "normal"

    @staticmethod
    def _snapshot_payload(snapshot: DashboardSnapshot) -> dict:
        """Expose the cockpit KPIs under names understood by the mock agent."""
        return {
            "period": snapshot.filters.range,
            "snapshot_id": snapshot.snapshot_id,
            "filters": snapshot.filters.model_dump(),
            "kpis": {
                "sales_amount": snapshot.sales_amount.model_dump(),
                "sales_volume": snapshot.sales_volume.model_dump(),
                "discount_rate": snapshot.discount_rate.model_dump(),
                "inventory_turnover": snapshot.inventory_turnover.model_dump(),
                "productivity_per_capita": snapshot.productivity_per_capita.model_dump(),
                "on_time_delivery_rate": snapshot.on_time_delivery_rate.model_dump(),
            },
        }

    async def stream(self, message: str, snapshot: DashboardSnapshot) -> AsyncIterator[AIStreamEvent]:
        async for event in analyze_stream(
            message,
            self._snapshot_payload(snapshot),
            demo_mode=self._mode(message),
        ):
            if event["event"] == "chunk":
                yield AIStreamEvent(content=event["content"])
            elif event["event"] == "final":
                yield AIStreamEvent(
                    evidence=event.get("evidence", []),
                    limitations=event.get("limitations", []),
                )


ai_service = MockAIAdapter()
