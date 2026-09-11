"""Core models and persistence for the masseuse task tracker."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path


class TaskStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass(slots=True)
class Task:
    id: int
    client: str
    service: str
    due_date: str
    priority: int = 3
    status: TaskStatus = TaskStatus.PENDING
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Task":
        return cls(
            id=int(data["id"]),
            client=str(data["client"]),
            service=str(data["service"]),
            due_date=str(data["due_date"]),
            priority=int(data.get("priority", 3)),
            status=TaskStatus(str(data.get("status", TaskStatus.PENDING))),
            notes=str(data.get("notes", "")),
        )


class TaskTracker:
    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)
        self.tasks: list[Task] = []
        self.next_id = 1

    def load(self) -> None:
        if not self.storage_path.exists():
            return
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Task database must contain a JSON list")
        self.tasks = [Task.from_dict(item) for item in data]
        self.next_id = max((task.id for task in self.tasks), default=0) + 1

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(task) for task in self.tasks]
        self.storage_path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    def add(
        self,
        client: str,
        service: str,
        due_date: str,
        priority: int,
        notes: str = "",
    ) -> Task:
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
        task = Task(
            id=self.next_id,
            client=client.strip(),
            service=service.strip(),
            due_date=due_date.strip(),
            priority=priority,
            notes=notes.strip(),
        )
        self.tasks.append(task)
        self.next_id += 1
        return task

    def complete(self, task_id: int) -> bool:
        task = self._find(task_id)
        if task is None:
            return False
        task.status = TaskStatus.COMPLETED
        return True

    def remove(self, task_id: int) -> bool:
        task = self._find(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        return True

    def pending_by_priority(self) -> list[Task]:
        return sorted(
            (task for task in self.tasks if task.status == TaskStatus.PENDING),
            key=lambda task: (task.priority, task.due_date),
        )

    def _find(self, task_id: int) -> Task | None:
        return next((task for task in self.tasks if task.id == task_id), None)
