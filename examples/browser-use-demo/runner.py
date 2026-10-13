"""One loop-owned browser run, from initial observation through retirement."""

from __future__ import annotations

import os
import re
import json
import time
import uuid
import base64
import asyncio
import secrets
from typing import TYPE_CHECKING, Any, TypeVar, cast
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Mapping, Callable, Iterable, Awaitable, AsyncIterator
from typing_extensions import override

import httpx2 as httpx
from file_state import wait_for_decision
from diagnostics import RunDiagnostics, diagnostic_observation
from file_upload import UploadOwner
from browser_driver import PlaywrightBrowser, origin
from playwright.async_api import Page, BrowserContext, WebSocketRoute, ScreencastFrame

from openai import AsyncOpenAI
from openai.types import DecisionInputPartUnionParam
from openai.lib.browser import (
    TabInput,
    TypeInput,
    ClickInput,
    BrowserError,
    BrowserState,
    BrowserReadV1,
    ReadPageInput,
    SelectOptionInput,
    AsyncBrowserDriver,
    AsyncBrowserToolset,
    BrowserConfirmContext,
)
from openai.types.responses import ResponseInputImageContentParam
from openai.lib.decisions_tool_runner import (
    DecisionObservation,
    DecisionDoneCandidate,
    AsyncDecisionCandidate,
    AsyncDecisionsToolRunner,
    AsyncDecisionActionCandidate,
)
from openai.lib.responses_tool_runner import AsyncRegisteredFunction, AsyncResponsesToolRunner

if TYPE_CHECKING:
    from server import Fieldwork
    from business import Permit

ROOT = Path(__file__).resolve().parent
TASKS: dict[str, dict[str, Any]] = json.loads((ROOT / "tasks.json").read_text())
OWNERS = ("agent", "draining-to-human", "human", "draining-to-agent", "stopped")
CLEANUP = ("not_started", "pending", "completed", "failed")
FILE_STATUSES = ("ready", "in_progress", "completed", "refused", "interrupted", "unknown", "failed")
_NetworkResult = TypeVar("_NetworkResult")


async def network_read(work: Awaitable[_NetworkResult], phase: asyncio.Event) -> _NetworkResult:
    pending = asyncio.ensure_future(work)
    stopped = asyncio.create_task(phase.wait())
    try:
        await asyncio.wait({pending, stopped}, return_when=asyncio.FIRST_COMPLETED)
        if phase.is_set():
            if not pending.done():
                pending.cancel()
            result = (await asyncio.gather(pending, return_exceptions=True))[0]
            # Headers may arrive in the same event-loop turn as Stop or Take.
            if isinstance(result, httpx.Response):
                await result.aclose()
            raise BrowserError("Request interrupted.")
        return await pending
    finally:
        stopped.cancel()
        if not pending.done():
            pending.cancel()
        await asyncio.gather(pending, stopped, return_exceptions=True)


class PhaseStream(httpx.AsyncByteStream):
    def __init__(
        self, stream: httpx.AsyncByteStream, phase: asyncio.Event, receipt: dict[str, Any], started: float
    ) -> None:
        self.stream, self.phase, self.receipt = stream, phase, receipt
        self.started = started

    def finish(self, phase: str | None = None) -> None:
        if self.receipt["durationMs"] is None:
            if phase is not None:
                self.receipt["phase"] = phase
            self.receipt["durationMs"] = round((time.monotonic() - self.started) * 1000)

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        iterator = self.stream.__aiter__()
        while True:
            try:
                yield await network_read(anext(iterator), self.phase)
            except StopAsyncIteration:
                self.finish()
                return
            except asyncio.CancelledError:
                self.finish("cancelled")
                raise
            except Exception:
                self.finish("cancelled" if self.phase.is_set() else "failed")
                raise

    @override
    async def aclose(self) -> None:
        try:
            await self.stream.aclose()
        except asyncio.CancelledError:
            self.finish("cancelled")
            raise
        except Exception:
            self.finish("cancelled" if self.phase.is_set() else "failed")
            raise
        else:
            self.finish("cancelled")


def member(value: Any, choices: Iterable[str], fallback: str | None = None) -> str | None:
    return value if value in choices else fallback


def count(value: Any) -> int:
    return value if type(value) is int and 0 <= value <= 9007199254740991 else 0


def now() -> int:
    return int(time.time() * 1000)


@dataclass
class Reply:
    status: int
    body: bytes
    headers: dict[str, str]


def as_json(value: Any, status: int = 200) -> Reply:
    return Reply(status, json.dumps(value).encode(), {"Content-Type": "application/json"})


def failure(status: int, message: str) -> Reply:
    return as_json({"error": message}, status)


class MixedHostInputRefusedError(ValueError):
    def __init__(self) -> None:
        super().__init__("Choose Route D-2201 in the host view.")


class Run:
    def __init__(self, app: Fieldwork, body: dict[str, Any]) -> None:
        self.app = app
        self.id = str(uuid.uuid4())
        self.task_id = body["taskId"]
        self.environment = body.get("environment", "browser")
        self.workspace: DesktopWorkspace | MixedWorkspace | None = None
        self.task: dict[str, Any]
        if self.environment == "desktop":
            from desktop_workspace import TASK, DesktopWorkspace

            self.workspace = DesktopWorkspace(self)
            self.task = {"title": "Route and save a desktop receipt", "instruction": TASK}
        elif self.environment == "mixed":
            from mixed_workspace import INSTRUCTION, MixedWorkspace

            self.workspace = MixedWorkspace(self)
            self.task = {"title": "Route in Host, save receipt in Guest", "instruction": INSTRUCTION}
        else:
            self.task = TASKS[self.task_id]
        self.api, self.mode = body["api"], body["mode"]
        self.diagnostics = RunDiagnostics(app.diagnostic_capture, self.mode)
        self.diagnostics.record("run", {"api": self.api, "mode": self.mode, "taskId": self.task_id})
        self.owner, self.version, self.status = "agent", 0, "running"
        self.phase_cancel = asyncio.Event()
        self.transfer_cancel: asyncio.Event | None = None
        self.started = time.monotonic()
        self.elapsed = 0.0
        self.result: str | None = None
        self.agent: asyncio.Task[None] | None = None
        self.human: asyncio.Task[None] | None = None
        self.transfer: asyncio.Task[None] | None = None
        self.cleanup: asyncio.Task[None] | None = None
        self.launch_retirement: asyncio.Task[None] | None = None
        self.view_task: asyncio.Task[None] | None = None
        self.cast_task: asyncio.Task[None] | None = None
        self.context: BrowserContext | None = None
        self.driver: PlaywrightBrowser | None = None
        self.task_page: Page | None = None
        self.task_tab: str | None = None
        self.notes_tab: str | None = None
        self.view_binding: dict[str, Any] | None = None
        self.screenshot_binding: dict[str, Any] | None = None
        self.frame: bytes | None = None
        self.screenshot: bytes | None = None
        self.cast_page: Page | None = None
        self.view: dict[str, Any] = {"status": "starting", "sequence": 0, "at": 0, "width": 0, "height": 0}
        self.screenshot_at: int | None = None
        self.checkpoints: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.events_dropped = 0
        self.receipts: list[dict[str, Any]] = []
        self.receipts_dropped = self.phase_index = 0
        self.cleanup_status = "not_started"
        self.checkpoint_sequence = self.checkpoint_dropped = self.checkpoint_bytes = 0
        self.approval: dict[str, Any] | None = None
        self.pending_approval: asyncio.Future[bool] | None = None
        self.expiry: asyncio.TimerHandle | None = None
        self.approval_timer: asyncio.TimerHandle | None = None
        self.expires_at: int | None = None
        self.closed, self.uncertain = False, False
        self.turns = self.requests = self.headers_ms = 0
        self.step_limit = 20 if self.api == "decisions" or self.workspace else 24
        self.final_text: str | None = None
        self.api_failure: dict[str, Any] | None = None
        self.fixture: dict[str, Any] | None = None
        self.observation: dict[str, Any] | None = None
        self.observed_binding: dict[str, Any] | None = None
        self.observed_revision = 0
        self.rehearsal_choice: str | None = None
        self.fixture_url = f"{app.origin}/fixture/{self.task_id}"
        self.workspace_token = secrets.token_hex(24)
        self.notes_url = f"{self.fixture_url}/notes/"
        self.file_owner: UploadOwner | None = None
        self.file_grant: dict[str, str] | None = None
        self.file_permit: Permit | None = None
        self.file_expires_at: int | None = None
        self.business: Business | None
        if self.task_id in ("stock", "service", "files"):
            from business import Business

            self.business = Business(self)
        else:
            self.business = None
        self.add(
            "start", ("Scripted rehearsal" if self.mode == "rehearsal" else "Live API") + " · " + self.task["title"]
        )

    def add(self, kind: str, text: str) -> None:
        self.events.append({"kind": kind, "text": text, "atMs": round((time.monotonic() - self.started) * 1000)})
        if len(self.events) > 256:
            self.events.pop(0)
            self.events_dropped += 1

    def record(self, kind: str, **fields: Any) -> dict[str, Any]:
        entry = {"kind": kind, "atMs": round((time.monotonic() - self.started) * 1000), **fields}
        self.receipts.append(entry)
        if len(self.receipts) > 256:
            self.receipts.pop(0)
            self.receipts_dropped += 1
        return entry

    def busy(self) -> bool:
        return (
            self.owner != "stopped"
            or not self.closed
            or any(
                task and not task.done()
                for task in (self.agent, self.human, self.transfer, self.cleanup, self.view_task, self.cast_task)
            )
            or bool(self.cleanup and self.cleanup.done() and self.cleanup.exception())
        )

    def set_owner(self, owner: str) -> None:
        if owner != self.owner:
            if self.business:
                self.business.revoke(self.business.pending)
            self.owner = owner
            self.version += 1
            if self.workspace:
                self.workspace.scroll_target = None
            self.add("control", owner)
            self.record("control", owner=owner)

    def settle(self, value: bool, outcome: str = "cancelled") -> None:
        if self.pending_approval and not self.pending_approval.done():
            self.pending_approval.set_result(value)
            self.add("approval", "Operator approved the action." if value else "Approval cancelled.")
            self.record("approval", outcome="approved" if value else outcome)
        self.approval = None
        if self.approval_timer:
            self.approval_timer.cancel()
            self.approval_timer = None

    async def ask(self, label: str, expires_at: int | None = None, owner: str = "agent") -> bool:
        if self.owner != owner or (owner == "agent" and self.phase_cancel.is_set()):
            return False
        self.pending_approval = asyncio.get_running_loop().create_future()
        deadline = expires_at if expires_at is not None else now() + 120000
        self.approval = {"id": str(uuid.uuid4()), "label": label, "expiresAt": deadline}
        self.add("approval", f"Waiting for approval: {label}")
        self.record("approval", outcome="offered")
        self.approval_timer = asyncio.get_running_loop().call_later(
            max(0, (deadline - now()) / 1000), self.stop, "approval_expired"
        )
        started = time.monotonic()
        try:
            return await self.pending_approval
        finally:
            self.diagnostics.measure("approvalMs", (time.monotonic() - started) * 1000)

    def stop(self, reason: str = "stopped") -> None:
        if self.owner != "stopped":
            self.set_owner("stopped")
            self.status = reason
            self.result = (
                "verified"
                if self.result == "verified" or (self.business and self.business.snapshot()["verified"])
                else "unverified"
            )
            self.add("control", f"Session ended: {reason}")
            self.elapsed = (time.monotonic() - self.started) * 1000
        self.phase_cancel.set()
        if self.transfer_cancel:
            self.transfer_cancel.set()
        if self.workspace:
            self.workspace.startup_stop.set()
        self.settle(
            False, "refused" if reason == "refused" else "expired" if reason == "approval_expired" else "cancelled"
        )
        if self.expiry:
            self.expiry.cancel()
            self.expiry = None
        self.expires_at = None
        if not self.cleanup:
            if self.cleanup_status != "failed":
                self.cleanup_status = "pending"
                self.record("cleanup", outcome="pending")
            self.cleanup = asyncio.create_task(self.retire())

    async def close_owned(self, close: Callable[[], Awaitable[None]]) -> None:
        """Remember owned cleanup errors even if the resource arrived after Stop."""
        try:
            await close()
        except Exception:
            if self.cleanup_status != "failed":
                self.cleanup_status = "failed"
                self.record("cleanup", outcome="failed")
            self.status = "cleanup_failed"
            self.stop("cleanup_failed")
            raise

    async def retire(self) -> None:
        # Closing revokes input before any delayed request can dispatch more work.
        for close in (
            self.context.close if self.context else None,
            self.file_owner.stop if self.file_owner else None,
            self.workspace.retire if self.workspace else None,
        ):
            if close:
                try:
                    await self.close_owned(close)
                except Exception:
                    # The failed owner stays unavailable; still retire the other resources.
                    pass
        self.frame = None
        self.view = {**self.view, "status": "closed"}
        admitted = {task for task in (self.agent, self.human, self.transfer, self.view_task, self.cast_task) if task}
        if admitted:
            await asyncio.wait(admitted)
        if self.launch_retirement:
            try:
                await self.launch_retirement
            except Exception:
                # close_owned records the failed resource and prevents admission.
                pass
        if self.cleanup_status != "failed":
            self.closed = True
            self.cleanup_status = "completed"
            self.record("cleanup", outcome="completed")
        self.diagnostics.record("run", {"status": self.status, "result": self.result, "cleanup": self.cleanup_status})
        self.diagnostics.close()

    async def binding(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, Any] | None:
        if self.workspace:
            return self.workspace.binding()
        if not self.driver or not self.task_page or self.closed or self.owner == "stopped" or self.uncertain:
            return None
        state = await self.driver.state(cancelled=cancelled)
        active = next((tab["id"] for tab in state["tabs"] if tab["active"]), None)
        tabs = [{"id": self.task_tab, "role": "Task"}]
        if self.notes_tab:
            tabs.append({"id": self.notes_tab, "role": "Notes"})
        role = next((item["role"] for item in tabs if item["id"] == active), None)
        if not role:
            return None
        observation = state.get("observation")
        assert observation is not None
        return {"tabId": active, "sequence": observation["sequence"], "role": role, "tabs": tabs}

    async def matches(self, value: dict[str, Any] | None, *, cancelled: Callable[[], bool] | None = None) -> bool:
        if self.workspace:
            return self.workspace.matches(value)
        current = await self.binding(cancelled=cancelled)
        return bool(
            current
            and value
            and value.get("tabId") == current["tabId"]
            and value.get("sequence") == current["sequence"]
        )

    async def check_target(
        self, args: Mapping[str, object], switching: bool = False, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        point = await self.binding(cancelled=cancelled)
        tab = args.get("tab_id")
        if not point or (
            tab is not None
            and (not any(item["id"] == tab for item in point["tabs"]) if switching else tab != point["tabId"])
        ):
            raise BrowserError("Select the target tab and read its current page first.")

    async def snapshot(self) -> dict[str, Any]:
        point = await self.binding()
        view = self.view if self.owner == "stopped" or await self.matches(self.view_binding) else {"status": "starting"}
        disclosed = False
        if self.environment == "mixed":
            from mixed_workspace import MixedWorkspace

            assert isinstance(self.workspace, MixedWorkspace)
            disclosed = self.workspace.disclosed
        return {
            "id": self.id,
            "taskId": self.task_id,
            "api": self.api,
            "mode": self.mode,
            "environment": self.environment,
            "status": self.status,
            "owner": self.owner,
            "ownerVersion": self.version,
            "browser": None if self.workspace else point,
            "desktop": point if self.workspace else None,
            "mixedDisclosed": disclosed,
            "screenshotBinding": self.screenshot_binding,
            "humanInputBusy": bool(
                (self.human and not self.human.done()) or (self.transfer and not self.transfer.done())
            ),
            "scrollTarget": self.workspace.scroll_target if self.workspace else None,
            "uncertainEffects": self.uncertain
            or bool(self.workspace and self.workspace.guest and self.workspace.guest.uncertain_effects),
            "closing": self.owner == "stopped" and self.busy(),
            "sessionExpiresAt": self.expires_at,
            "turns": self.turns,
            "stepLimit": self.step_limit,
            "result": self.result,
            "requests": self.requests,
            "requestHeadersMs": round(self.headers_ms),
            "diagnostics": self.diagnostics.summary(self.requests),
            "elapsedMs": round(
                self.elapsed
                if self.owner == "stopped" and (self.agent is None or self.agent.done())
                else (time.monotonic() - self.started) * 1000
            ),
            "screenshotAt": self.screenshot_at,
            "history": {
                "dropped": self.checkpoint_dropped,
                "checkpoints": [
                    {key: value for key, value in item.items() if key != "pixels"} for item in self.checkpoints
                ],
            },
            "view": view,
            "events": self.events,
            "eventsDropped": self.events_dropped,
            "approval": self.approval,
            "fixture": self.business.snapshot() if self.business else self.fixture,
            "finalText": self.final_text,
            "apiFailure": self.api_failure,
        }

    def receipt(self) -> dict[str, Any]:
        file: dict[str, Any] | None = None
        owner = self.file_owner
        if self.environment == "mixed":
            from mixed_workspace import MixedWorkspace

            assert isinstance(self.workspace, MixedWorkspace)
            owner = self.workspace.download
        if owner:
            state = owner.state()
            effect = ("none", "completed", "unknown")
            current = state["current"]
            file = {
                "version": 1,
                "direction": member(state["direction"], ("upload", "download")),
                "current": {
                    "status": member(current["status"], FILE_STATUSES),
                    "effect": member(current["effect"], effect),
                }
                if current
                else None,
                "cleanup": member(state["cleanup"], CLEANUP),
                "earlier_omitted": state["earlier_omitted"] is True,
                "recent": [
                    {
                        "phase": member(change["phase"], ("prepare", "transfer", "cleanup")),
                        "status": member(change["status"], (*FILE_STATUSES, *CLEANUP)),
                        **({"effect": member(change["effect"], effect)} if "effect" in change else {}),
                    }
                    for change in state["recent"][-32:]
                ],
            }
        events: list[dict[str, Any]] = []
        for event in self.receipts:
            item: dict[str, Any] = {"kind": event["kind"], "atMs": count(event["atMs"])}
            if event["kind"] == "request":
                item.update(
                    attempt=count(event["attempt"]),
                    phase=member(event["phase"], ("pending", "headers", "failed", "cancelled")),
                    status=event["status"] if type(event["status"]) is int and 100 <= event["status"] <= 599 else None,
                    headersMs=count(event["headersMs"]) if event["headersMs"] is not None else None,
                    durationMs=count(event["durationMs"]) if event["durationMs"] is not None else None,
                )
            elif event["kind"] == "approval":
                item["outcome"] = member(event["outcome"], ("offered", "approved", "refused", "expired", "cancelled"))
            elif event["kind"] == "control":
                item["owner"] = member(event["owner"], OWNERS)
            elif event["kind"] == "cleanup":
                item["outcome"] = member(event["outcome"], CLEANUP)
            elif event["kind"] == "tools":
                item.update(
                    phaseIndex=count(event["phaseIndex"]),
                    phase=member(event["phase"], ("boundary", "pending", "final")),
                    attempted=count(event["attempted"]),
                    returned=count(event["returned"]),
                )
            else:
                continue
            events.append(item)
        return {
            "version": 1,
            "id": self.id if re.fullmatch(r"[a-f0-9-]{36}", self.id) else None,
            "environment": member(self.environment, ("desktop", "mixed"), "browser"),
            "taskId": member(self.task_id, (*TASKS, "desktop", "mixed")),
            "api": member(self.api, ("responses", "decisions")),
            "mode": member(self.mode, ("live", "rehearsal")),
            "status": member(
                self.status,
                (
                    "running",
                    "paused",
                    "complete",
                    "unverified",
                    "refused",
                    "approval_expired",
                    "stopped",
                    "failed",
                    "expired",
                    "view_failed",
                    "input_failed",
                    "handoff_failed",
                    "handoff_unavailable",
                    "uncertain",
                    "browser_closed",
                    "cleanup_failed",
                ),
                "unknown",
            ),
            "owner": member(self.owner, OWNERS),
            "result": member(self.result, ("verified", "unverified")),
            "uncertainEffects": self.uncertain
            or bool(self.workspace and self.workspace.guest and self.workspace.guest.uncertain_effects)
            or bool(file and file["current"] and file["current"]["effect"] == "unknown"),
            "cleanup": member(self.cleanup_status, CLEANUP, "not_started"),
            "requests": count(self.requests),
            "turns": count(self.turns),
            "stepLimit": count(self.step_limit),
            "elapsedMs": count(
                round(
                    self.elapsed
                    if self.owner == "stopped" and (self.agent is None or self.agent.done())
                    else (time.monotonic() - self.started) * 1000
                )
            ),
            "requestHeadersMs": count(round(self.headers_ms)),
            "diagnostics": self.diagnostics.summary(self.requests),
            "droppedEvents": count(self.receipts_dropped),
            "events": events,
            "file": file,
        }

    async def refresh_view(self, *, cancelled: Callable[[], bool] | None = None) -> None:
        phase = self.phase_cancel if self.owner == "agent" else None
        transfer = self.transfer_cancel
        version = self.version
        point = self.workspace.binding() if self.workspace else None

        def interrupted() -> bool:
            return (
                self.owner == "stopped"
                or self.version != version
                or bool(phase and phase.is_set())
                or bool(transfer and transfer.is_set())
                or bool(cancelled and cancelled())
            )

        try:
            if self.workspace:
                await self.workspace.frame(cancelled=interrupted)
                return
            while self.cast_task:
                previous_task = self.cast_task
                await wait_for_decision(lambda previous_task=previous_task: asyncio.shield(previous_task), interrupted)
            if interrupted():
                raise ValueError("Cancelled")
            task = asyncio.create_task(self._refresh_browser_view(version))
            self.cast_task = task
            # Every waiter may settle on Stop, while retire/busy still own setup and late cleanup.
            task.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            await wait_for_decision(lambda: asyncio.shield(task), interrupted)
        except Exception:
            if (
                self.workspace
                and point is not None
                and self.version == version
                and self.workspace.binding() is not None
                and not self.workspace.matches(point)
            ):
                return
            if self.version == version:
                self.view_binding = self.frame = None
            if self.workspace and not interrupted():
                self.stop("view_failed")
            if interrupted():
                raise
        finally:
            if self.view_task is asyncio.current_task():
                self.view_task = None

    async def _refresh_browser_view(self, version: int) -> None:
        try:
            if self.owner == "stopped" or self.version != version:
                return
            point = await self.binding()
            if not point or await self.matches(self.view_binding) or self.version != version:
                return
            previous = self.cast_page
            self.frame = None
            self.view_binding = None
            self.cast_page = None
            if previous and not previous.is_closed():
                await previous.screencast.stop()
            if not await self.matches(point) or self.version != version:
                return
            assert self.driver is not None
            _, page = self.driver.page(None)
            latest: ScreencastFrame | None = None

            def on_frame(value: ScreencastFrame) -> None:
                nonlocal latest
                latest = value
                if (
                    self.version == version
                    and self.cast_page is page
                    and self.view_binding == point
                    and self.owner != "stopped"
                ):
                    self.frame = value["data"]
                    self.view = {
                        "status": "live",
                        "sequence": self.view["sequence"] + 1,
                        "at": value["timestamp"],
                        "width": value["viewportWidth"],
                        "height": value["viewportHeight"],
                    }

            await page.screencast.start(size={"width": 1024, "height": 720}, quality=75, on_frame=on_frame)
            if not await self.matches(point) or self.version != version:
                await self.close_owned(page.screencast.stop)
                return
            self.cast_page = page
            self.view_binding = point
            if latest is not None:
                on_frame(latest)
        finally:
            if self.cast_task is asyncio.current_task():
                self.cast_task = None

    async def capture(self, *, cancelled: Callable[[], bool] | None = None) -> None:
        point = await self.binding(cancelled=cancelled)
        if not point:
            return
        if self.workspace:
            await self.refresh_view(cancelled=cancelled)
            if not self.frame or not await self.matches(self.view_binding, cancelled=cancelled):
                raise RuntimeError("No current desktop frame is available.")
            pixels = self.frame
            fixture = self.fixture
        else:
            assert self.driver is not None
            _, page = self.driver.page(None)
            pixels = await wait_for_decision(lambda: page.screenshot(type="jpeg", quality=80), cancelled)
            fixture = await self.inspect(cancelled=cancelled)
        if not await self.matches(point, cancelled=cancelled):
            return
        self.screenshot, self.screenshot_at = pixels, now()
        self.screenshot_binding, self.fixture = point, fixture
        self.checkpoint_sequence += 1
        role = (
            ("Host browser" if point["view"] == "host" else "Guest editor")
            if self.environment == "mixed"
            else ("Desktop" if self.workspace else point["role"])
        )
        self.diagnostics.frame(
            {
                "sequence": self.checkpoint_sequence,
                "owner": self.owner,
                "role": role,
                "mime": "image/jpeg" if self.environment == "browser" else "image/png",
            },
            pixels,
        )
        if len(pixels) > 1024 * 1024:
            self.checkpoint_dropped += 1
            return
        self.checkpoints.append(
            {
                "sequence": self.checkpoint_sequence,
                "at": self.screenshot_at,
                "atMs": round((time.monotonic() - self.started) * 1000),
                "owner": self.owner,
                "role": role,
                "pixels": pixels,
            }
        )
        self.checkpoint_bytes += len(pixels)
        while len(self.checkpoints) > 12 or self.checkpoint_bytes > 8 * 1024 * 1024:
            self.checkpoint_bytes -= len(self.checkpoints.pop(0)["pixels"])
            self.checkpoint_dropped += 1

    async def inspect(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, Any]:
        if self.workspace:
            return await self.workspace.proof(cancelled=cancelled)
        if self.business:
            return self.business.snapshot()
        assert self.task_page is not None
        body = self.task_page.locator("body")
        state: dict[str, Any] = await wait_for_decision(
            lambda: body.evaluate("""body => ({
                revision: Number(body.dataset.revision), finished: body.dataset.finished === 'true',
                results: JSON.parse(body.dataset.results),
                fields: Object.fromEntries([...body.querySelectorAll('input,select')]
                   .map(field => [field.getAttribute('aria-label'),field.value]))
            })"""),
            cancelled,
        )
        if self.task_id == "reservation":
            state["verified"] = (
                isinstance(state["results"], dict)
                and cast(dict[str, Any], state["results"]).get("confirmation") == "TABLE-204"
                and all(state["fields"].get(name) == value for name, value in self.task["fields"].items())
            )
        else:
            expected = [{"id": item["id"], "choice": item["expected"]} for item in self.task["items"]]
            state["verified"] = state["results"] == expected
        return state

    def toolset(self, owner: str) -> AsyncBrowserToolset:
        version = self.version

        async def confirm(_context: BrowserConfirmContext) -> bool:
            return (
                self.owner == owner and self.version == version and (owner != "agent" or not self.phase_cancel.is_set())
            )

        return AsyncBrowserToolset(
            cast(AsyncBrowserDriver, BrowserActions(self, owner, version)),
            members=(
                ("list_tabs", "read_page", "get_page_text", "switch_tab", "click", "type", "select_option")
                if self.task_id in ("reservation", "service", "files")
                else None
            ),
            confirm=confirm,
        )

    async def ensure_current(
        self, owner: str = "agent", version: int | None = None, *, cancelled: Callable[[], bool] | None = None
    ) -> dict[str, Any]:
        if (
            self.owner != owner
            or (version is not None and self.version != version)
            or (owner == "agent" and self.phase_cancel.is_set())
        ):
            raise BrowserError("The agent no longer controls this session.")
        state = await self.inspect(cancelled=cancelled)
        assert self.task_page is not None
        if (
            self.task_page.url != self.fixture_url
            or state["revision"] != self.observed_revision
            or not await self.matches(self.observed_binding, cancelled=cancelled)
        ):
            raise BrowserError("The workspace changed. Read the current page again.")
        return state

    async def read_page(self, args: ReadPageInput, *, cancelled: Callable[[], bool] | None = None) -> BrowserReadV1:
        await self.check_target(args, cancelled=cancelled)
        point = await self.binding(cancelled=cancelled)
        assert self.driver is not None
        result = await self.driver.read_page(args, cancelled=cancelled)
        assert not isinstance(result, str)
        if not point or not await self.matches(point, cancelled=cancelled):
            raise BrowserError("The page changed during observation.")
        if self.business:
            if point["tabId"] == self.task_tab:
                await self.business.bind_read(result["elements"], cancelled=cancelled)
            else:
                self.business.bindings = {}
        revision = (await self.inspect(cancelled=cancelled))["revision"]
        await self.capture(cancelled=cancelled)
        if not await self.matches(point, cancelled=cancelled) or not await self.matches(
            self.screenshot_binding, cancelled=cancelled
        ):
            raise BrowserError("The page changed during observation.")
        self.observation = {**result, "tabs": point["tabs"], "active_tab_id": point["tabId"]}
        self.observed_binding = point
        self.observed_revision = revision
        return result

    async def act(
        self,
        member: str,
        args: Mapping[str, Any],
        label: str,
        owner: str = "agent",
        version: int | None = None,
        *,
        cancelled: Callable[[], bool] | None = None,
    ) -> None:
        cancelled = cancelled or (self.phase_cancel.is_set if owner == "agent" else None)
        await self.check_target(args, member == "switch_tab", cancelled=cancelled)
        before = await self.ensure_current(owner, version, cancelled=cancelled)
        operation = self.business.bindings.get(args.get("target", "")) if self.business and member == "click" else None
        if self.business and member == "click" and not operation:
            raise BrowserError("Read an unambiguous business control and its current fields before approval.")
        if member == "click" and (operation or label in ("Reserve table", "Approve")):
            prompt = label
            if operation and operation["operation"] == "schedule":
                prompt = f"{label} · {operation['date']} · {operation['technician']} · {operation['note']}"
            if not await self.ask(prompt, owner=owner):
                raise BrowserError("The operator refused the action.")
            await self.ensure_current(owner, version, cancelled=cancelled)
        self.add("action", label or member)
        permit = self.business.authorize(operation) if operation and self.business else None
        started = time.monotonic()
        try:
            await getattr(self.driver, member)(args, cancelled=cancelled)
            if permit and self.business:
                await self.business.finish(permit)
        finally:
            self.diagnostics.measure("actionMs", (time.monotonic() - started) * 1000)
            if permit and self.business:
                self.business.revoke(permit)
        state = await self.inspect(cancelled=cancelled)
        self.diagnostics.record("effect", {"member": member, "state": state})
        self.observed_revision = state["revision"]
        if before["results"] != state["results"]:
            self.observed_binding = None
        await self.capture(cancelled=cancelled)

    async def observe(self) -> list[DecisionInputPartUnionParam]:
        await self.read_page({"tab_id": None, "filter": "all"}, cancelled=self.phase_cancel.is_set)
        assert self.screenshot is not None
        result: list[DecisionInputPartUnionParam] = [
            {"type": "input_text", "text": json.dumps(self.observation)},
            {
                "type": "input_image",
                "image_url": "data:image/jpeg;base64," + base64.b64encode(self.screenshot).decode(),
            },
        ]
        if self.api == "decisions":
            self.diagnostics.record("observation", diagnostic_observation(result))
        return result

    async def candidates(self, _observation: DecisionObservation) -> list[AsyncDecisionCandidate]:
        state = await self.inspect(cancelled=self.phase_cancel.is_set)
        done: DecisionDoneCandidate = {
            "id": "done",
            "description": "Finish only when the page shows all items complete.",
            "done": True,
        }
        if state["finished"]:
            return [done]
        assert self.observed_binding is not None and self.observation is not None
        if self.observed_binding["tabId"] != self.task_tab:

            async def switch() -> None:
                await self.act("switch_tab", {"tab_id": self.task_tab}, "Switch to Task")

            self.rehearsal_choice = "switch_to_task"
            return [{"id": "switch_to_task", "description": "Switch to the Task tab", "execute": switch}, done]
        if self.task_id == "files":
            self.rehearsal_choice = "attach_intake_note"
            return [
                {
                    "id": "attach_intake_note",
                    "description": "Attach approved fixture document; operator approval required",
                    "execute": self.attach_file,
                },
                done,
            ]
        if self.task_id == "service":
            fields: dict[str, Any] = {item["label"]: item.get("value") for item in self.observation["elements"]}
        else:
            fields = state.get("fields", {})
        actions: list[AsyncDecisionActionCandidate] = []
        for element in self.observation["elements"]:
            args: dict[str, Any] = {"tab_id": None, "target": element["ref"]}
            label = element["label"]
            if element["role"] == "button":
                if "fields" in self.task and (
                    (
                        self.task_id == "service"
                        and self.business is not None
                        and element["ref"] not in self.business.bindings
                    )
                    or (
                        self.task_id != "service"
                        and not all(fields.get(name) == value for name, value in self.task["fields"].items())
                    )
                ):
                    continue
                member = "click"
                description = f"Click {label}"
            elif label in self.task.get("fields", {}) and fields.get(label) != self.task["fields"][label]:
                value = self.task["fields"][label]
                if element["role"] == "combobox":
                    member = "select_option"
                    args["values"] = [value]
                else:
                    member = "type"
                    args["text"] = value
                description = f"Fill {label} with {value}"
            else:
                continue

            async def execute(member: str = member, args: Mapping[str, Any] = args, label: str = label) -> None:
                await self.act(member, args, label)

            actions.append({"id": element["ref"], "description": description, "execute": execute})
        if self.mode == "rehearsal":
            expected = (
                f"Click {self.task['items'][len(state['results'])]['expected']}" if "items" in self.task else None
            )
            if self.task_id == "stock":
                order = self.task["orders"][len(state["results"])]
                stock = next(item for item in self.task["stock"] if item["colour"] == order["colour"])
                expected = f"Click Ship {order['id']} with {stock['sku']}"
            choice = next((item for item in actions if expected is None or item["description"] == expected), None)
            if not choice:
                raise BrowserError("No current fixture action is eligible.")
            self.rehearsal_choice = choice["id"]
        return [*actions, done]

    async def traced_candidates(self, observation: DecisionObservation) -> list[AsyncDecisionCandidate]:
        choices = await self.candidates(observation)
        self.diagnostics.record(
            "choices",
            [
                {"id": item["id"], "description": item["description"], "done": item.get("done") is True}
                for item in choices
            ],
        )
        return choices

    async def verify(self, _observation: DecisionObservation) -> bool:
        phase = self.phase_cancel
        state = await self.inspect(cancelled=phase.is_set)
        self.diagnostics.record("verification", state)
        return state["verified"]

    def redact(self, text: str) -> str:
        value = re.sub(r"sk-[\w-]+", "[redacted]", str(text))
        for secret in (self.app.api_key, *self.app.models.values()):
            if secret:
                value = value.replace(secret, "[redacted]")
        return value[:400]

    async def dispatch(self, request: httpx.Request) -> httpx.Response:
        phase = self.phase_cancel
        if phase.is_set() or self.owner != "agent" or self.turns >= self.step_limit:
            raise BrowserError("No further request is admitted for this task.")
        self.turns += 1
        started = time.monotonic()
        if self.mode == "rehearsal":
            choice = self.rehearsal_choice
            response = httpx.Response(
                200,
                json={
                    "object": "decision",
                    "id": "rehearsal",
                    "model": "",
                    "answers": [
                        {
                            "name": "next_action",
                            "type": "choice",
                            "choice": choice,
                            "confidence": 1,
                            "probabilities": [{"value": choice, "probability": 1}],
                        }
                    ],
                    "usage": {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                        "output_tokens_details": {"reasoning_tokens": 0},
                    },
                },
            )
        else:
            self.requests += 1
            receipt = self.record(
                "request", attempt=self.requests, phase="pending", status=None, headersMs=None, durationMs=None
            )
            try:
                response = await network_read(self.http_transport.handle_async_request(request), phase)
                receipt["phase"] = "headers"
                receipt["status"] = response.status_code
                receipt["headersMs"] = round((time.monotonic() - started) * 1000)
                self.headers_ms += receipt["headersMs"]
                if response.is_stream_consumed and response.is_closed:
                    # A custom transport may return cached content whose stream
                    # has already completed; HTTPX will not iterate it again.
                    receipt["durationMs"] = round((time.monotonic() - started) * 1000)
                else:
                    response.stream = PhaseStream(cast(httpx.AsyncByteStream, response.stream), phase, receipt, started)
            except asyncio.CancelledError:
                receipt["phase"] = "cancelled"
                receipt["durationMs"] = round((time.monotonic() - started) * 1000)
                raise
            except Exception:
                receipt["phase"] = "cancelled" if phase.is_set() else "failed"
                receipt["durationMs"] = round((time.monotonic() - started) * 1000)
                raise
        self.add(
            "request",
            "Scripted local choice · No API request"
            if self.mode == "rehearsal"
            else f"{self.api.title()} · HTTP {response.status_code}",
        )
        if response.is_error:
            self.api_failure = {
                "status": response.status_code,
                "requestId": self.redact(response.headers.get("x-request-id", "")),
                "code": None,
                "message": "The API denied this request.",
            }
        return response

    async def initialize(self) -> None:
        if self.workspace:
            await self.workspace.initialize()
            return
        context = await self.app.browser.new_context(
            run=self, viewport={"width": 1024, "height": 720}, service_workers="block", accept_downloads=False
        )
        if self.owner != "agent" or self.phase_cancel.is_set():
            await self.close_owned(context.close)
            return
        self.context = context
        if self.business:
            adding = asyncio.create_task(
                context.add_cookies(
                    [
                        {
                            "name": "fieldwork_workspace",
                            "value": self.workspace_token,
                            "domain": "127.0.0.1",
                            "path": f"/fixture/{self.task_id}",
                            "httpOnly": True,
                            "sameSite": "Strict",
                        }
                    ]
                )
            )
            stopped = asyncio.create_task(self.phase_cancel.wait())
            try:
                await asyncio.wait({adding, stopped}, return_when=asyncio.FIRST_COMPLETED)
                if self.owner != "agent" or self.phase_cancel.is_set():
                    return
                adding.result()
            finally:
                stopped.cancel()
                if not adding.done():
                    adding.cancel()
                adding.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
                await asyncio.gather(stopped, return_exceptions=True)
        urls = {self.fixture_url, self.notes_url + "brief", self.notes_url + "rules"}
        public_viewports = frozenset(urls)
        public_values: frozenset[tuple[str, str, str]] = frozenset()
        if self.task_id == "reservation":
            public_values = frozenset(
                (self.fixture_url, "TABLE-204", name) for name in ("guest_name", "party_size", "time", "seating")
            )
        elif self.task_id == "service":
            public_values = frozenset(
                (self.fixture_url, "SERVICE-401", name) for name in ("visit_date", "technician", "note")
            )
        if self.business:
            urls.add(
                f"{self.fixture_url}/effect?run={self.id}" + ("&case=INTAKE-501" if self.task_id == "files" else "")
            )
        self.driver = PlaywrightBrowser(
            context,
            {origin(self.fixture_url)},
            owned_fixture_urls=frozenset(urls),
            public_values=public_values,
            public_viewports=public_viewports,
        )
        await context.route("**/*", self.driver.guard)

        async def refuse_socket(route: WebSocketRoute) -> None:
            await route.close()

        await context.route_web_socket("**/*", refuse_socket)

        def closed(*_args: object) -> None:
            if self.owner != "stopped":
                self.stop("browser_closed")

        context.once("close", closed)
        await self.driver.new_tab({"url": self.fixture_url})
        self.task_tab, self.task_page = self.driver.page(None)
        self.task_page.once("close", closed)
        if self.task_id == "files":

            async def approve_file(transfer: Mapping[str, object]) -> bool:
                assert self.business is not None and self.task_page is not None
                point = await self.binding()
                revision = self.business.snapshot()["revision"]
                if (
                    not point
                    or point["tabId"] != self.task_tab
                    or self.owner != "agent"
                    or not await self.ask("Attach Approved fixture document to INTAKE-501", self.file_expires_at)
                    or not await self.matches(point)
                    or self.task_page.url != self.fixture_url
                    or self.business.snapshot()["revision"] != revision
                    or self.phase_cancel.is_set()
                ):
                    return False
                self.file_permit = self.business.authorize(
                    {
                        "operation": "attach",
                        "job": self.task["job"],
                        "count": transfer["count"],
                        "sha256": transfer["sha256"],
                    }
                )
                return True

            created = await UploadOwner.create(
                self.task_page,
                {
                    "allow_upload": True,
                    "record": await self.task_page.locator('[data-record-id="transfer-case"]').element_handle(),
                    "control": await self.task_page.locator("input[type=file]").element_handle(),
                    "record_id": "transfer-case",
                },
                approve_file,
            )
            if self.closed or self.owner != "agent" or self.phase_cancel.is_set():
                await self.close_owned(created.stop)
                raise BrowserError("File task setup ended.")
            self.file_owner = created
        await self.refresh_view()

    async def attach_file(self, arguments: dict[str, Any] | None = None) -> str:
        from business import INTAKE

        await self.check_target({"tab_id": self.task_tab})
        if (
            arguments
            or not self.file_owner
            or not self.business
            or self.owner != "agent"
            or self.phase_cancel.is_set()
            or self.file_permit
        ):
            raise BrowserError("No active file task.")
        if not self.file_grant:
            name = self.file_owner.generated_name()
            with (self.file_owner.upload_root / name).open("xb") as stream:
                os.chmod(stream.fileno(), 0o600)
                stream.write(INTAKE)
            self.file_expires_at = now() + 30000
            self.file_grant = await self.file_owner.prepare(self.file_owner.upload_root, name, self.file_expires_at)
        try:
            result = json.loads(await self.file_owner.upload({"grant_id": self.file_grant["grant_id"]}))
            if not result.get("completed") or not self.file_permit:
                raise BrowserError("File selection was refused or its outcome is unknown.")
            await self.business.finish(self.file_permit)
            self.add("action", "Received by fixture · INTAKE-501")
            await self.capture()
            return json.dumps(self.file_owner.state())
        finally:
            if self.file_permit:
                self.business.revoke(self.file_permit)
                self.file_permit = None

    async def execute(self) -> None:
        phase = self.phase_cancel
        try:
            if not self.context and not (self.workspace and self.workspace.guest):
                await self.initialize()
            if self.phase_cancel.is_set() or self.owner != "agent":
                return
            await self.capture(cancelled=phase.is_set)
            if self.phase_cancel.is_set() or self.owner != "agent":
                return
            state = await self.inspect(cancelled=phase.is_set)
            if state["verified"] and self.workspace:
                state = await self.workspace.proof(cancelled=phase.is_set, finalize=True)
            if self.phase_cancel.is_set() or self.owner != "agent":
                return
            if state["finished"]:
                self.result = "verified" if state["verified"] else "unverified"
            else:
                self.http_transport = self.app.transport or httpx.AsyncHTTPTransport()
                try:
                    async with AsyncOpenAI(
                        api_key="local-rehearsal" if self.mode == "rehearsal" else self.app.api_key,
                        max_retries=0,
                        timeout=60,
                        http_client=httpx.AsyncClient(transport=httpx.MockTransport(self.dispatch)),
                    ) as client:
                        instruction = (
                            "This is an isolated synthetic browser demonstration. All records and actions are local fixtures. "
                            "To request a gated action, call its tool: the application asks the operator before execution. "
                            "Do not ask for approval in a final answer. " + self.task["instruction"]
                        )
                        remaining = self.step_limit - self.turns
                        if self.workspace:
                            self.result = await self.workspace.execute(client)
                            self.fixture = await self.inspect(cancelled=phase.is_set)
                        elif self.api == "decisions":
                            runner = AsyncDecisionsToolRunner(
                                observe=self.observe, candidates=self.traced_candidates, verify=self.verify
                            )
                            result = await runner.run(
                                client,
                                {"model": self.app.models.get(self.api) or "", "input": instruction},
                                max_steps=remaining,
                                cancelled=self.phase_cancel.is_set,
                                on_diagnostic=self.diagnostics.event,
                            )
                            self.result = (
                                "verified"
                                if result["status"] == "verified"
                                or (self.business and self.business.snapshot()["verified"])
                                else "unverified"
                            )
                            if result["status"] == "refused":
                                self.status = "refused"
                        else:
                            functions: list[AsyncRegisteredFunction] = []
                            if self.task_id == "files":
                                functions.append(
                                    AsyncRegisteredFunction(
                                        tool={
                                            "type": "function",
                                            "name": "attach_intake_note",
                                            "strict": True,
                                            "description": "Attach the approved fixture document to INTAKE-501. Requires operator approval.",
                                            "parameters": {
                                                "type": "object",
                                                "properties": {},
                                                "required": [],
                                                "additionalProperties": False,
                                            },
                                        },
                                        execute=self.attach_file,
                                    )
                                )
                            runner = AsyncResponsesToolRunner(
                                browser=self.toolset("agent"),
                                functions=functions,
                            )
                            await self.read_page({"tab_id": None, "filter": "all"}, cancelled=self.phase_cancel.is_set)
                            assert self.screenshot is not None
                            model = self.app.models[self.api]
                            assert model is not None
                            result = await runner.run(
                                client,
                                {
                                    "model": model,
                                    "store": False,
                                    "input": [
                                        {
                                            "role": "user",
                                            "content": [
                                                {"type": "input_text", "text": instruction},
                                                {"type": "input_text", "text": json.dumps(self.observation)},
                                                {
                                                    "type": "input_image",
                                                    "image_url": "data:image/jpeg;base64,"
                                                    + base64.b64encode(self.screenshot).decode(),
                                                    "detail": "auto",
                                                },
                                            ],
                                        }
                                    ],
                                },
                                max_steps=remaining,
                                stream=True,
                                cancelled=self.phase_cancel.is_set,
                                on_diagnostic=self.diagnostics.event,
                            )
                            self.final_text = self.redact(result.output_text)
                            self.result = (
                                "verified" if (await self.inspect(cancelled=phase.is_set))["verified"] else "unverified"
                            )
                finally:
                    if not self.app.transport:
                        await self.http_transport.aclose()
            if self.owner == "agent" and not self.phase_cancel.is_set():
                await self.capture(cancelled=phase.is_set)
                if self.owner != "agent" or self.phase_cancel.is_set():
                    return
                if self.status != "refused":
                    self.status = "complete" if self.result == "verified" else self.result
                self.add("result", f"{self.mode.title()} · {self.result}")
        except (Exception, asyncio.CancelledError):
            if self.owner == "agent":
                self.status = "failed"
                self.result = (
                    "verified"
                    if self.result == "verified" or (self.business and self.business.snapshot()["verified"])
                    else "unverified"
                )
                self.add("result", "Request or action failed. Inspect the browser before retrying.")
        finally:
            self.settle(False)
            self.elapsed = (time.monotonic() - self.started) * 1000
            if self.owner == "agent":
                self.stop(self.status)

    async def take(self, version: int) -> None:
        transfer = asyncio.Event()
        self.transfer_cancel = transfer
        timer = asyncio.get_running_loop().call_later(5, transfer.set)
        try:
            agent = self.agent
            assert agent is not None
            try:
                await wait_for_decision(lambda: asyncio.shield(agent), transfer.is_set)
            except Exception:
                if self.owner == "draining-to-human" and self.version == version:
                    self.stop("handoff_unavailable")
                return
            if self.owner != "draining-to-human" or self.version != version:
                return
            if not self.workspace and (self.closed or not self.task_page or self.task_page.is_closed()):
                self.stop("handoff_unavailable")
                return
            if self.driver:
                await wait_for_decision(self.driver.invalidate_references, transfer.is_set)
            if self.owner != "draining-to-human" or self.version != version:
                return
            if not self.workspace and (self.closed or not self.task_page or self.task_page.is_closed()):
                self.stop("handoff_unavailable")
                return
            self.status = "paused"
            self.set_owner("human")
            human_version = self.version
            self.view_binding = None
            await self.capture(cancelled=transfer.is_set)
            if self.version != human_version:
                return
            if not await self.matches(self.screenshot_binding, cancelled=transfer.is_set):
                self.stop("handoff_unavailable")
                return
            self.expires_at = now() + 300000
            self.expiry = asyncio.get_running_loop().call_later(300, self.stop, "expired")
            self.add("control", "Agent work drained. You control the browser.")
        except Exception:
            if self.owner != "stopped":
                self.stop("handoff_failed")
        finally:
            timer.cancel()
            if self.transfer_cancel is transfer:
                self.transfer_cancel = None

    async def give_back(self, version: int) -> None:
        transfer = asyncio.Event()
        self.transfer_cancel = transfer
        timer = asyncio.get_running_loop().call_later(5, transfer.set)
        try:
            human = self.human
            if human:
                try:
                    await wait_for_decision(lambda: asyncio.shield(human), transfer.is_set)
                except Exception:
                    self.stop("handoff_unavailable")
                    return
            if self.owner != "draining-to-agent" or self.version != version:
                return
            if self.driver:
                await wait_for_decision(self.driver.invalidate_references, transfer.is_set)
                await self.driver.read_page({"tab_id": None, "filter": "all"}, cancelled=transfer.is_set)
            await self.capture(cancelled=transfer.is_set)
            if self.owner != "draining-to-agent" or self.version != version:
                return
            if self.expiry:
                self.expiry.cancel()
            self.expires_at = None
            self.phase_cancel = asyncio.Event()
            self.status, self.result = "running", None
            self.view_binding = None
            self.set_owner("agent")
            self.add("control", "Fresh workspace state observed. Agent control resumed.")
            self.agent = asyncio.create_task(self.execute())
        except Exception:
            if self.owner != "stopped":
                self.stop("handoff_failed")
        finally:
            timer.cancel()
            if self.transfer_cancel is transfer:
                self.transfer_cancel = None

    def valid_input(self, body: dict[str, Any]) -> bool:
        if self.environment == "mixed":
            from mixed_workspace import MixedWorkspace

            assert isinstance(self.workspace, MixedWorkspace)
            return self.workspace.valid_input(body)
        if self.workspace:
            from desktop_workspace import input_action

            return input_action(body, self.workspace.scroll_target) is not None
        action = body.get("action")
        fields: dict[str, set[str]] = {
            "click": {"x", "y"},
            "type": {"text"},
            "key": {"key"},
            "scroll": {"direction", "amount"},
            "open_notes": set(),
            "close_notes": set(),
            "switch_tab": {"tab_id"},
        }
        if action not in fields or set(body) - (
            {"runId", "ownerVersion", "tabId", "sequence", "action"} | fields[action]
        ):
            return False
        if action == "click":
            return all(
                type(body.get(name)) in (int, float) and 0 <= body[name] < limit
                for name, limit in (("x", 1024), ("y", 720))
            )
        if action == "type":
            return (
                type(body.get("text")) is str
                and 0 < len(body["text"].encode("utf-16-le", errors="surrogatepass")) <= 4000
            )
        if action == "key":
            return body.get("key") in (
                "Enter",
                "Tab",
                "Backspace",
                "Delete",
                "Escape",
                "ArrowUp",
                "ArrowDown",
                "ArrowLeft",
                "ArrowRight",
                "Home",
                "End",
                "PageUp",
                "PageDown",
                "Space",
                "ControlOrMeta+A",
            )
        if action == "scroll":
            return (
                body.get("direction") in ("up", "down", "left", "right")
                and type(body.get("amount")) is int
                and 1 <= body["amount"] <= 2048
            )
        if action == "open_notes":
            return self.notes_tab is None
        if action == "close_notes":
            return self.notes_tab is not None
        return body.get("tab_id") in (self.task_tab, self.notes_tab) and body.get("tab_id") is not None

    async def human_input(self, body: dict[str, Any]) -> None:
        try:
            if self.workspace:
                await self.workspace.human_input(body)
                self.add("human", f"Human {body['action']} completed; desktop state captured.")
                return
            assert self.driver is not None
            _, page = self.driver.page(None)
            action = body["action"]
            if action == "click":
                await page.mouse.click(body["x"], body["y"])
            elif action == "type":
                await page.keyboard.insert_text(body["text"])
            elif action == "key":
                await page.keyboard.press(body["key"])
            elif action == "scroll":
                deltas = {
                    "up": (0, -body["amount"]),
                    "down": (0, body["amount"]),
                    "left": (-body["amount"], 0),
                    "right": (body["amount"], 0),
                }
                await page.mouse.wheel(*deltas[body["direction"]])
            elif action == "open_notes":
                await self.driver.new_tab({"url": self.notes_url + "brief"})
                self.notes_tab, _ = self.driver.page(None)
            elif action == "close_notes":
                await self.driver.close_tab({"tab_id": self.notes_tab})
                self.notes_tab = None
            elif action == "switch_tab":
                await self.driver.switch_tab({"tab_id": body["tab_id"]})
            await self.refresh_view()
            await self.capture()
            self.add("human", f"Human {action} completed; browser state captured.")
        except MixedHostInputRefusedError:
            raise
        except Exception:
            self.uncertain = True
            self.stop("uncertain")
            raise


class BrowserActions:
    def __init__(self, run: Run, owner: str, version: int) -> None:
        self.run = run
        self.owner = owner
        self.version = version

    async def state(self, *, cancelled: Callable[[], bool] | None = None) -> BrowserState:
        assert self.run.driver is not None
        return await self.run.driver.state(cancelled=cancelled)

    async def read_page(self, args: ReadPageInput, *, cancelled: Callable[[], bool] | None = None) -> BrowserReadV1:
        return await self.run.read_page(args, cancelled=cancelled)

    async def get_page_text(
        self, args: TabInput, *, cancelled: Callable[[], bool] | None = None
    ) -> str | BrowserReadV1:
        await self.run.check_target(args, cancelled=cancelled)
        assert self.run.driver is not None
        return await self.run.driver.get_page_text(args, cancelled=cancelled)

    async def screenshot(
        self, args: TabInput, *, cancelled: Callable[[], bool] | None = None
    ) -> ResponseInputImageContentParam:
        await self.run.check_target(args, cancelled=cancelled)
        assert self.run.driver is not None
        return await self.run.driver.screenshot(args, cancelled=cancelled)

    async def switch_tab(self, args: TabInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        await self.run.act("switch_tab", args, "Switch tab", self.owner, self.version, cancelled=cancelled)

    async def click(self, args: ClickInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        if self.run.observation is None:
            raise BrowserError("Read the current page before selecting a control.")
        label = next((item["label"] for item in self.run.observation["elements"] if item["ref"] == args["target"]), "")
        await self.run.act("click", args, label, self.owner, self.version, cancelled=cancelled)

    async def type(self, args: TypeInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        await self.run.act("type", args, "Fill field", self.owner, self.version, cancelled=cancelled)

    async def select_option(self, args: SelectOptionInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        await self.run.act("select_option", args, "Select field", self.owner, self.version, cancelled=cancelled)
