import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.schemas.chat import CancelResponse, ChatRequest
from app.services.ai_contract import AIStreamEvent
from app.services.ai_service import ai_service
from app.services.dashboard_service import dashboard_service
from app.state.runtime import ChatTask, runtime_state

router = APIRouter(tags=["chat"])


def sse(event: str, task_id: str, **data: object) -> str:
    payload = {"requestId": task_id, "type": event, "timestamp": datetime.now(timezone.utc).isoformat(), **data}
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def next_chunk(iterator: AsyncIterator[AIStreamEvent], task: ChatTask, timeout: float) -> AIStreamEvent:
    chunk_task = asyncio.create_task(anext(iterator))
    cancel_task = asyncio.create_task(task.cancel_event.wait())
    done, pending = await asyncio.wait({chunk_task, cancel_task}, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
    for pending_task in pending:
        pending_task.cancel()
    if not done:
        raise TimeoutError
    if cancel_task in done and cancel_task.result():
        chunk_task.cancel()
        raise asyncio.CancelledError
    return chunk_task.result()


async def event_stream(body: ChatRequest, task: ChatTask) -> AsyncIterator[str]:
    snapshot = body.snapshot or dashboard_service.get_snapshot(body.range, body.region, body.category)
    yield sse("start", task.task_id, snapshotId=snapshot.snapshot_id)
    retries = body.max_retries if body.max_retries is not None else settings.chat_max_retries
    timeout = (body.timeout_ms / 1000) if body.timeout_ms else settings.chat_timeout_seconds
    for attempt in range(retries + 1):
        try:
            evidence: list[dict] = []
            limitations: list[str] = []
            iterator = ai_service.stream(body.message, snapshot).__aiter__()
            while True:
                try:
                    ai_event = await next_chunk(iterator, task, timeout)
                except StopAsyncIteration:
                    task.status = "completed"
                    yield sse(
                        "done",
                        task.task_id,
                        snapshotId=snapshot.snapshot_id,
                        evidence=evidence,
                        limitations=limitations,
                    )
                    return
                if ai_event.content is not None:
                    yield sse("delta", task.task_id, content=ai_event.content)
                if ai_event.evidence is not None:
                    evidence = ai_event.evidence
                if ai_event.limitations is not None:
                    limitations = ai_event.limitations
        except asyncio.CancelledError:
            task.status = "cancelled"
            yield sse("cancelled", task.task_id)
            return
        except TimeoutError:
            if attempt < retries:
                yield sse("retry", task.task_id, attempt=attempt + 1, reason="timeout")
                continue
            task.status = "timeout"
            yield sse("timeout", task.task_id, message="AI 响应超时")
            return
        except Exception as exc:
            if attempt < retries:
                yield sse("retry", task.task_id, attempt=attempt + 1, reason="service_error")
                continue
            task.status = "error"
            yield sse("error", task.task_id, code="AI_SERVICE_ERROR", message=str(exc))
            return


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest) -> StreamingResponse:
    task, created = await runtime_state.register(body.request_id)
    if not created:
        async def duplicate() -> AsyncIterator[str]:
            yield sse("duplicate", body.request_id, status=task.status)
        return StreamingResponse(duplicate(), media_type="text/event-stream")
    return StreamingResponse(
        event_stream(body, task),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "X-Task-Id": body.request_id or str(uuid4())},
    )


@router.post("/chat/{task_id}/cancel", response_model=CancelResponse)
async def cancel_chat(task_id: str) -> CancelResponse:
    status = await runtime_state.cancel(task_id)
    return CancelResponse(task_id=task_id, status=status)
