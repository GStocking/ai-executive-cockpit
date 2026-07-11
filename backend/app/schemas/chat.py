from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.dashboard import DashboardSnapshot


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    request_id: str = Field(alias="requestId", min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)
    snapshot: DashboardSnapshot | None = None
    range: Literal["7d", "30d", "90d", "ytd"] = "30d"
    region: str = "all"
    category: str = "all"
    timeout_ms: int | None = Field(default=None, alias="timeoutMs", ge=50, le=60_000)
    max_retries: int | None = Field(default=None, alias="maxRetries", ge=0, le=5)


class CancelResponse(BaseModel):
    task_id: str
    status: Literal["cancelled", "not_found", "already_finished"]
