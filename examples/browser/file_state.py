"""Bounded observations for the two optional file examples."""

from __future__ import annotations

import json
import asyncio
from typing import Literal, TypeVar
from contextvars import ContextVar
from collections.abc import Callable, Awaitable
from typing_extensions import TypedDict, NotRequired


def browser_outcome(receipt: str, interrupted: bool, cleanup: str) -> dict[str, object]:
    """Project this call's receipt, never the owner's current concurrent transfer."""
    result = json.loads(receipt)
    effect = "completed" if result["completed"] else "unknown" if result["attempted"] else "none"
    status = "completed" if result["completed"] else "interrupted" if interrupted else result["status"]
    return {"version": 1, "status": status, "effect": effect, "cleanup": cleanup}


Status = Literal["in_progress", "refused", "interrupted", "unknown", "completed"]
Effect = Literal["none", "unknown", "completed"]
Cleanup = Literal["not_started", "pending", "completed"]


class TransferOutcome(TypedDict):
    status: Status
    effect: Effect


class FileChange(TypedDict):
    phase: Literal["prepare", "transfer", "cleanup"]
    status: Status | Literal["pending"]
    effect: NotRequired[Effect]


class FileStateV1(TypedDict):
    version: Literal[1]
    direction: Literal["upload", "download"]
    current: TransferOutcome | None
    cleanup: Cleanup
    earlier_omitted: bool
    recent: list[FileChange]


class FileCleanupIncompleteError(RuntimeError):
    pass


async def wait_for_file_cleanup(task: asyncio.Task[None]) -> None:
    # Match the file example's three-second transport bound without cancelling the owned task.
    done, _ = await asyncio.wait({task}, timeout=3)
    if not done:
        raise FileCleanupIncompleteError("File cleanup incomplete.")
    task.result()


class FileState:
    def __init__(self, direction: Literal["upload", "download"]) -> None:
        self.direction: Literal["upload", "download"] = direction
        self.current: TransferOutcome | None = None
        self.cleanup: Cleanup = "not_started"
        self.earlier_omitted = False
        self.recent: list[FileChange] = []

    def _append(self, change: FileChange) -> None:
        self.recent.append(change)
        if len(self.recent) > 32:
            del self.recent[0]
            self.earlier_omitted = True

    def prepare(self, status: Literal["refused", "interrupted"]) -> None:
        self._append({"phase": "prepare", "status": status, "effect": "none"})

    def transfer(self, status: Status, effect: Effect, *, current: bool = True) -> None:
        if current:
            self.current = {"status": status, "effect": effect}
        self._append({"phase": "transfer", "status": status, "effect": effect})

    def clean(self, status: Literal["pending", "completed"]) -> None:
        if self.cleanup != status and self.cleanup != "completed":
            self.cleanup = status
            self._append({"phase": "cleanup", "status": status})

    def snapshot(self) -> FileStateV1:
        return {
            "version": 1,
            "direction": self.direction,
            "current": None if self.current is None else self.current.copy(),
            "cleanup": self.cleanup,
            "earlier_omitted": self.earlier_omitted,
            "recent": [change.copy() for change in self.recent],
        }


class FileApproval(TypedDict):
    owner: FileState
    active: bool


# Child tasks inherit this token. The owner revokes it when approval returns.
approving_owner: ContextVar[FileApproval | None] = ContextVar("approving_file_owner", default=None)
_pending_decisions: set[asyncio.Task[object]] = set()
_Decision = TypeVar("_Decision")


def _finish_decision(task: asyncio.Task[object]) -> None:
    _pending_decisions.discard(task)
    if not task.cancelled():
        task.exception()


async def wait_for_decision(
    work: Callable[[], Awaitable[_Decision]], cancelled: Callable[[], bool] | None
) -> _Decision:
    if cancelled is None:
        return await work()
    if cancelled():
        raise ValueError("File decision interrupted.")

    async def decide() -> _Decision:
        if cancelled():
            raise ValueError("File decision interrupted.")
        return await work()

    pending = asyncio.create_task(decide())
    # Only this result is abandoned on cancellation; retain and observe the caller's read or approval.
    _pending_decisions.add(pending)
    pending.add_done_callback(_finish_decision)
    while not pending.done():
        if cancelled():
            raise ValueError("File decision interrupted.")
        await asyncio.wait({pending}, timeout=0.05)
    if cancelled():
        raise ValueError("File decision interrupted.")
    return pending.result()
