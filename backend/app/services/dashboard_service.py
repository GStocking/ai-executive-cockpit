import hashlib
import math
import random
import time
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.dashboard import DashboardFilters, DashboardSnapshot, Metric


class DashboardService:
    """Builds reproducible demo data for each two-second snapshot bucket."""

    _range_factor = {"7d": 0.25, "30d": 1.0, "90d": 2.8, "ytd": 6.2}
    _region_factor = {"all": 1.0, "east": 1.12, "south": 0.93, "north": 0.86, "west": 0.72}
    _category_factor = {"all": 1.0, "womens": 1.18, "mens": 0.91, "kids": 0.74, "sports": 0.82, "accessories": 0.68}

    def get_snapshot(self, range_: str, region: str, category: str) -> DashboardSnapshot:
        bucket = int(time.time() // settings.snapshot_interval_seconds)
        key = f"{bucket}:{range_}:{region.lower()}:{category.lower()}"
        rng = random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16], 16))
        scale = self._range_factor[range_] * self._region_factor.get(region.lower(), 0.8) * self._category_factor.get(category.lower(), 0.85)
        pulse = math.sin(bucket / 7) * 0.012

        def metric(value: float, unit: str, change: float, digits: int = 2) -> Metric:
            change = round(change, 2)
            return Metric(value=round(value, digits), unit=unit, change=change, trend="up" if change > 0 else "down" if change < 0 else "flat")

        sales_change = rng.uniform(-2.2, 6.8) + pulse * 100
        generated_at = datetime.fromtimestamp(bucket * settings.snapshot_interval_seconds, tz=timezone.utc)
        return DashboardSnapshot(
            snapshot_id=hashlib.sha1(key.encode()).hexdigest()[:16],
            generated_at=generated_at,
            filters=DashboardFilters(range=range_, region=region, category=category),
            sales_amount=metric(3_860_000 * scale * (1 + pulse + rng.uniform(-0.008, 0.008)), "CNY", sales_change, 0),
            sales_volume=metric(128_600 * scale * (1 + pulse + rng.uniform(-0.01, 0.01)), "件", sales_change - rng.uniform(0.2, 1.4), 0),
            discount_rate=metric(18.6 + rng.uniform(-0.7, 0.7), "%", rng.uniform(-1.2, 0.8)),
            inventory_turnover=metric(5.7 + rng.uniform(-0.15, 0.15), "次/年", rng.uniform(-0.5, 0.9)),
            productivity_per_capita=metric(236_000 * (1 + rng.uniform(-0.012, 0.012)), "CNY/人", rng.uniform(-1, 4), 0),
            on_time_delivery_rate=metric(94.8 + rng.uniform(-0.35, 0.35), "%", rng.uniform(-0.5, 1.2)),
        )


dashboard_service = DashboardService()
