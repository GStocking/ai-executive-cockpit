import asyncio
from dataclasses import dataclass, field
from typing import Literal


TaskStatus = Literal["running", "completed", "cancelled", "timeout", "error"]


@dataclass
class ChatTask:
    task_id: str
    status: TaskStatus = "running"
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)


class RuntimeState:
    def __init__(self) -> None:
        self._tasks: dict[str, ChatTask] = {}
        self._lock = asyncio.Lock()

    async def register(self, task_id: str) -> tuple[ChatTask, bool]:
        async with self._lock:
            existing = self._tasks.get(task_id)
            if existing is not None:
                return existing, False
            task = ChatTask(task_id=task_id)
            self._tasks[task_id] = task
            return task, True

    async def cancel(self, task_id: str) -> str:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return "not_found"
            if task.status != "running":
                return "already_finished"
            task.cancel_event.set()
            task.status = "cancelled"
            return "cancelled"

    async def cancel_all(self) -> None:
        async with self._lock:
            for task in self._tasks.values():
                if task.status == "running":
                    task.cancel_event.set()
                    task.status = "cancelled"

    def clear(self) -> None:
        self._tasks.clear()


runtime_state = RuntimeState()
