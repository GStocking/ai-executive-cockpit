from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Metric(BaseModel):
    value: float
    unit: str
    change: float
    trend: str


class DashboardFilters(BaseModel):
    range: str
    region: str
    category: str


class DashboardSnapshot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    snapshot_id: str
    generated_at: datetime
    refresh_interval_ms: int = 2000
    filters: DashboardFilters
    sales_amount: Metric
    sales_volume: Metric
    discount_rate: Metric
    inventory_turnover: Metric
    productivity_per_capita: Metric
    on_time_delivery_rate: Metric
