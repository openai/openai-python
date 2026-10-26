"""One loop-owned browser run, from initial observation through retirement."""

from __future__ import annotations

import re
import json
import time
import uuid
import base64
import asyncio
from typing import TYPE_CHECKING, Any, TypeVar, cast
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Mapping, Callable, Awaitable, AsyncIterator
from typing_extensions import override

import httpx2 as httpx
from booking import BookingBrowser
from playwright.async_api import Page, BrowserContext, WebSocketRoute, ScreencastFrame
from playwright._impl._errors import TargetClosedError

from openai import AsyncOpenAI
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
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner

if TYPE_CHECKING:
    from server import Fieldwork

ROOT = Path(__file__).resolve().parent
TASKS: dict[str, dict[str, Any]] = json.loads((ROOT / "tasks.json").read_text())
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


_Decision = TypeVar("_Decision")
_pending_decisions: set[asyncio.Task[object]] = set()


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
        raise ValueError("Browser operation interrupted.")

    async def decide() -> _Decision:
        if cancelled():
            raise ValueError("Browser operation interrupted.")
        return await work()

    pending = asyncio.create_task(decide())
    # Only this result is abandoned on cancellation; retain and observe the caller's read or approval.
    _pending_decisions.add(pending)
    pending.add_done_callback(_finish_decision)
    while not pending.done():
        if cancelled():
            raise ValueError("Browser operation interrupted.")
        await asyncio.wait({pending}, timeout=0.05)
    if cancelled():
        raise ValueError("Browser operation interrupted.")
    return pending.result()


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


class Run:
    def __init__(self, app: Fieldwork, body: dict[str, Any]) -> None:
        self.app = app
        self.id = str(uuid.uuid4())
        self.task_id = body["taskId"]
        self.task = TASKS[self.task_id]
        self.api, self.mode = body["api"], body["mode"]
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
        self.driver: BookingBrowser | None = None
        self.task_page: Page | None = None
        self.task_tab: str | None = None
        self.view_binding: dict[str, Any] | None = None
        self.screenshot_binding: dict[str, Any] | None = None
        self.frame: bytes | None = None
        self.screenshot: bytes | None = None
        self.cast_page: Page | None = None
        self.view: dict[str, Any] = {"status": "starting", "sequence": 0, "at": 0, "width": 0, "height": 0}
        self.screenshot_at: int | None = None
        self.events: list[dict[str, Any]] = []
        self.events_dropped = 0
        self.receipts: list[dict[str, Any]] = []
        self.receipts_dropped = 0
        self.cleanup_status = "not_started"
        self.approval: dict[str, Any] | None = None
        self.pending_approval: asyncio.Future[bool] | None = None
        self.expiry: asyncio.TimerHandle | None = None
        self.approval_timer: asyncio.TimerHandle | None = None
        self.expires_at: int | None = None
        self.closed, self.uncertain = False, False
        self.turns = self.requests = self.headers_ms = 0
        self.step_limit = 20 if self.api == "decisions" else 24
        self.final_text: str | None = None
        self.api_failure: dict[str, Any] | None = None
        self.fixture: dict[str, Any] | None = None
        self.observation: dict[str, Any] | None = None
        self.observed_binding: dict[str, Any] | None = None
        self.observed_revision = 0
        self.rehearsal_choice: str | None = None
        self.fixture_url = f"{app.origin}/fixture/{self.task_id}"
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
            if self.owner == "human":
                if self.expiry:
                    self.expiry.cancel()
                    self.expiry = None
                self.expires_at = None
            self.owner = owner
            self.version += 1
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
        return await self.pending_approval

    def stop(self, reason: str = "stopped") -> None:
        if self.owner != "stopped":
            self.set_owner("stopped")
            self.status = reason
            self.result = "verified" if self.result == "verified" else "unverified"
            self.add("control", f"Session ended: {reason}")
            self.elapsed = (time.monotonic() - self.started) * 1000
        self.phase_cancel.set()
        if self.transfer_cancel:
            self.transfer_cancel.set()
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
        if self.context:
            try:
                await self.close_owned(self.context.close)
            except Exception:
                # Failed cleanup remains visible and blocks reuse.
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

    async def binding(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, Any] | None:
        if not self.driver or not self.task_page or self.closed or self.owner == "stopped" or self.uncertain:
            return None
        state = await self.driver.state(cancelled=cancelled)
        active = next((tab["id"] for tab in state["tabs"] if tab["active"]), None)
        tabs = [{"id": self.task_tab, "role": "Task"}]
        role = next((item["role"] for item in tabs if item["id"] == active), None)
        if not role:
            return None
        observation = state.get("observation")
        assert observation is not None
        return {"tabId": active, "sequence": observation["sequence"], "role": role, "tabs": tabs}

    async def matches(self, value: dict[str, Any] | None, *, cancelled: Callable[[], bool] | None = None) -> bool:
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
        version = self.version
        try:
            point = await self.binding()
            view = (
                self.view
                if self.owner == "stopped" or await self.matches(self.view_binding)
                else {"status": "starting"}
            )
        except (BrowserError, TargetClosedError):
            if self.version == version:
                raise
            point, view = None, {"status": "starting"}
        if self.version != version or self.owner == "stopped":
            point = None
            view = {**self.view, "status": "closed"} if self.owner == "stopped" else {"status": "starting"}
        return {
            "id": self.id,
            "taskId": self.task_id,
            "api": self.api,
            "mode": self.mode,
            "status": self.status,
            "owner": self.owner,
            "ownerVersion": self.version,
            "browser": point,
            "screenshotBinding": self.screenshot_binding,
            "humanInputBusy": bool(
                (self.human and not self.human.done()) or (self.transfer and not self.transfer.done())
            ),
            "uncertainEffects": self.uncertain,
            "closing": self.owner == "stopped" and self.busy(),
            "sessionExpiresAt": self.expires_at,
            "turns": self.turns,
            "stepLimit": self.step_limit,
            "result": self.result,
            "requests": self.requests,
            "requestHeadersMs": round(self.headers_ms),
            "elapsedMs": round(
                self.elapsed
                if self.owner == "stopped" and (self.agent is None or self.agent.done())
                else (time.monotonic() - self.started) * 1000
            ),
            "screenshotAt": self.screenshot_at,
            "view": view,
            "events": self.events,
            "eventsDropped": self.events_dropped,
            "approval": self.approval,
            "fixture": self.fixture,
            "finalText": self.final_text,
            "apiFailure": self.api_failure,
        }

    async def refresh_view(self, *, cancelled: Callable[[], bool] | None = None) -> None:
        phase = self.phase_cancel if self.owner == "agent" else None
        transfer = self.transfer_cancel
        version = self.version

        def interrupted() -> bool:
            return (
                self.owner == "stopped"
                or self.version != version
                or bool(phase and phase.is_set())
                or bool(transfer and transfer.is_set())
                or bool(cancelled and cancelled())
            )

        try:
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
            if self.version == version:
                self.view_binding = self.frame = None
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

                async def stop_stale_cast() -> None:
                    try:
                        await page.screencast.stop()
                    except TargetClosedError:
                        if not page.is_closed():
                            raise

                await self.close_owned(stop_stale_cast)
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
        assert self.driver is not None
        _, page = self.driver.page(None)
        pixels = await wait_for_decision(lambda: page.screenshot(type="jpeg", quality=80), cancelled)
        fixture = await self.inspect(cancelled=cancelled)
        if not await self.matches(point, cancelled=cancelled):
            return
        self.screenshot, self.screenshot_at = pixels, now()
        self.screenshot_binding, self.fixture = point, fixture

    async def inspect(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, Any]:
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
        results: dict[str, Any] = cast(dict[str, Any], state["results"]) if isinstance(state["results"], dict) else {}
        submitted: dict[str, Any] = results.get("fields", {})
        state["verified"] = results.get("confirmation") == "TABLE-204" and all(
            submitted.get(name) == value and state["fields"].get(name) == value
            for name, value in self.task["fields"].items()
        )
        return state

    def toolset(self, owner: str) -> AsyncBrowserToolset:
        version = self.version

        async def confirm(_context: BrowserConfirmContext) -> bool:
            return (
                self.owner == owner and self.version == version and (owner != "agent" or not self.phase_cancel.is_set())
            )

        return AsyncBrowserToolset(
            cast(AsyncBrowserDriver, BrowserActions(self, owner, version)),
            members=("list_tabs", "read_page", "get_page_text", "click", "type", "select_option"),
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
        if member == "click" and label == "Reserve table":
            if not await self.ask(label, owner=owner):
                raise BrowserError("The operator refused the action.")
            await self.ensure_current(owner, version, cancelled=cancelled)
        self.add("action", label or member)
        try:
            await getattr(self.driver, member)(args, cancelled=cancelled)
        except (Exception, asyncio.CancelledError):
            if cancelled and cancelled():
                self.uncertain = True
            raise
        state = await self.inspect(cancelled=cancelled)
        self.observed_revision = state["revision"]
        if before["results"] != state["results"]:
            self.observed_binding = None
        await self.capture(cancelled=cancelled)

    async def observe(self) -> DecisionObservation:
        await self.read_page({"tab_id": None, "filter": "all"}, cancelled=self.phase_cancel.is_set)
        assert self.screenshot is not None
        return [
            {"type": "input_text", "text": json.dumps(self.observation)},
            {
                "type": "input_image",
                "image_url": "data:image/jpeg;base64," + base64.b64encode(self.screenshot).decode(),
            },
        ]

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
        fields = state["fields"]
        actions: list[AsyncDecisionActionCandidate] = []
        for element in self.observation["elements"]:
            args: dict[str, Any] = {"tab_id": None, "target": element["ref"]}
            label = element["label"]
            if element["role"] == "button":
                if not all(fields.get(name) == value for name, value in self.task["fields"].items()):
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
            choice = next(iter(actions), None)
            if not choice:
                raise BrowserError("No current fixture action is eligible.")
            self.rehearsal_choice = choice["id"]
        return [*actions, done]

    async def verify(self, _observation: DecisionObservation) -> bool:
        phase = self.phase_cancel
        state = await self.inspect(cancelled=phase.is_set)
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
        context = await self.app.browser.new_context(
            run=self, viewport={"width": 1024, "height": 720}, service_workers="block", accept_downloads=False
        )
        if self.owner != "agent" or self.phase_cancel.is_set():
            await self.close_owned(context.close)
            return
        self.context = context
        self.driver = BookingBrowser(context, self.fixture_url)
        await context.route("**/*", self.driver.guard)

        async def refuse_socket(route: WebSocketRoute) -> None:
            await route.close()

        await context.route_web_socket("**/*", refuse_socket)

        def closed(*_args: object) -> None:
            if self.owner != "stopped":
                self.stop("browser_closed")

        context.once("close", closed)
        await self.driver.open()
        self.task_tab, self.task_page = self.driver.page(None)
        self.task_page.once("close", closed)
        await self.refresh_view()

    async def execute(self) -> None:
        phase = self.phase_cancel
        try:
            if not self.context:
                await self.initialize()
            if self.phase_cancel.is_set() or self.owner != "agent":
                return
            await self.capture(cancelled=phase.is_set)
            if self.phase_cancel.is_set() or self.owner != "agent":
                return
            state = await self.inspect(cancelled=phase.is_set)
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
                        if self.api == "decisions":
                            runner = AsyncDecisionsToolRunner(
                                observe=self.observe, candidates=self.candidates, verify=self.verify
                            )
                            result = await runner.run(
                                client,
                                {"model": self.app.models.get(self.api) or "", "input": instruction},
                                max_steps=remaining,
                                cancelled=self.phase_cancel.is_set,
                            )
                            self.result = "verified" if result["status"] == "verified" else "unverified"
                            if result["status"] == "refused":
                                self.status = "refused"
                        else:
                            runner = AsyncResponsesToolRunner(browser=self.toolset("agent"))
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
                self.result = "verified" if self.result == "verified" else "unverified"
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
            if self.uncertain or self.closed or not self.task_page or self.task_page.is_closed():
                self.stop("handoff_unavailable")
                return
            if self.driver:
                await wait_for_decision(self.driver.invalidate_references, transfer.is_set)
            if self.owner != "draining-to-human" or self.version != version:
                return
            if self.uncertain or self.closed or not self.task_page or self.task_page.is_closed():
                self.stop("handoff_unavailable")
                return
            self.status, self.result = "paused", None
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
        action = body.get("action")
        fields: dict[str, set[str]] = {
            "click": {"x", "y"},
            "type": {"text"},
            "key": {"key"},
            "scroll": {"direction", "amount"},
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
        return False

    async def human_input(self, body: dict[str, Any]) -> None:
        try:
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
            await self.driver.invalidate_references()
            await self.refresh_view()
            await self.capture()
            self.add("human", f"Human {action} completed; browser state captured.")
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

    async def click(self, args: ClickInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        if self.run.observation is None:
            raise BrowserError("Read the current page before selecting a control.")
        label = next((item["label"] for item in self.run.observation["elements"] if item["ref"] == args["target"]), "")
        await self.run.act("click", args, label, self.owner, self.version, cancelled=cancelled)

    async def type(self, args: TypeInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        await self.run.act("type", args, "Fill field", self.owner, self.version, cancelled=cancelled)

    async def select_option(self, args: SelectOptionInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        await self.run.act("select_option", args, "Select field", self.owner, self.version, cancelled=cancelled)
