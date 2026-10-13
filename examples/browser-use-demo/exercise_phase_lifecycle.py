"""Finite controlled desktop and browser operations. No model or guest starts."""

from __future__ import annotations

import io
import sys
import json
import base64
import asyncio
import threading
from typing import Any, cast
from pathlib import Path
from unittest.mock import AsyncMock, patch
from collections.abc import Callable, AsyncIterator
from typing_extensions import override

import httpx2 as httpx
from PIL import Image
from server import Run, Fieldwork, WorkspaceBrowser, serve
from playwright.async_api import Playwright

from openai.lib.browser import BrowserError
from openai.lib.computer import ComputerUseError


async def network_duration_check(outcome: str) -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "browser", "taskId": "service", "api": "responses", "mode": "live"})
    app.current = run
    entered, release = asyncio.Event(), asyncio.Event()
    reads: list[str] = []
    closed: list[str] = []

    class Stream(httpx.AsyncByteStream):
        @override
        async def __aiter__(self) -> AsyncIterator[bytes]:
            reads.append("first")
            yield b"data: first\n\n"
            reads.append("last")
            entered.set()
            await release.wait()
            if outcome == "failed":
                raise RuntimeError("Controlled body read failed")
            yield b"data: last\n\n"

        @override
        async def aclose(self) -> None:
            closed.append("stream")
            if outcome == "close failure":
                raise RuntimeError("Controlled close failed")

    class Transport(httpx.AsyncBaseTransport):
        @override
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            del request
            return httpx.Response(
                201, headers={"content-type": "text/event-stream", "x-request-id": "fixture"}, stream=Stream()
            )

    run.http_transport = Transport()
    response = await run.dispatch(httpx.Request("POST", "http://127.0.0.1:1/responses"))
    (receipt,) = [entry for entry in run.receipts if entry["kind"] == "request"]
    assert response.status_code == 201 and response.headers["x-request-id"] == "fixture"
    assert receipt["phase"] == "headers" and receipt["durationMs"] is None, receipt
    assert not reads, "Timing must not consume or prefetch any response data"
    iterator = response.aiter_raw()
    assert await anext(iterator) == b"data: first\n\n"
    assert receipt["durationMs"] is None
    if outcome in ("closed", "close failure"):
        try:
            await response.aclose()
        except RuntimeError as exc:
            assert outcome == "close failure" and str(exc) == "Controlled close failed"
        else:
            assert outcome == "closed"
    else:
        last = asyncio.create_task(anext(iterator))
        await asyncio.wait_for(entered.wait(), 1)
        assert receipt["durationMs"] is None, "Headers and one chunk do not complete the request"
        if outcome == "cancelled":
            run.phase_cancel.set()
        else:
            release.set()
        if outcome in ("failed", "cancelled"):
            try:
                await asyncio.wait_for(last, 1)
            except (RuntimeError, BrowserError):
                pass
            else:
                raise AssertionError("Interrupted stream returned content")
        else:
            assert await last == b"data: last\n\n"
            try:
                await anext(iterator)
            except StopAsyncIteration:
                pass
            else:
                raise AssertionError("Extra data escaped")
    expected = "cancelled" if outcome in ("cancelled", "closed") else "headers" if outcome == "complete" else "failed"
    assert receipt["phase"] == expected and receipt["durationMs"] >= receipt["headersMs"], receipt
    duration = receipt["durationMs"]
    await asyncio.sleep(0.004)
    await response.aclose()
    assert receipt["durationMs"] == duration and closed == ["stream"], (receipt, closed)


async def network_buffered_duration_check(kind: str) -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "browser", "taskId": "service", "api": "responses", "mode": "live"})
    app.current = run
    body = b"event: done\ndata: [DONE]\n\n"
    response = (
        httpx.Response(200, json={"answer": "fixture"}, headers={"x-request-id": "local-json"})
        if kind == "json"
        else httpx.Response(
            200, content=body, headers={"content-type": "text/event-stream", "x-request-id": "local-sse"}
        )
    )
    # Custom transports can legally return a complete, buffered response. The SDK
    # then reads its cached bytes without iterating or closing its stream again.
    assert response.is_stream_consumed and response.is_closed
    original = response.stream

    class Transport(httpx.AsyncBaseTransport):
        @override
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            del request
            return response

    run.http_transport = Transport()
    returned = await run.dispatch(httpx.Request("POST", "http://127.0.0.1:1/responses"))
    (receipt,) = [entry for entry in run.receipts if entry["kind"] == "request"]
    assert receipt["phase"] == "headers" and receipt["durationMs"] >= receipt["headersMs"], receipt
    assert returned is response and returned.stream is original, "Already closed content needs no stream wrapper"
    if kind == "json":
        assert returned.headers["x-request-id"] == "local-json" and returned.json() == {"answer": "fixture"}
    else:
        assert returned.headers["x-request-id"] == "local-sse" and await returned.aread() == body
    duration = receipt["durationMs"]
    await asyncio.sleep(0.004)
    await returned.aclose()
    assert receipt["durationMs"] == duration


async def network_phase_check(where: str, transfer: bool) -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "browser", "taskId": "service", "api": "responses", "mode": "live"})
    app.current = run
    entered, release, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
    closed: list[str] = []

    class Stream(httpx.AsyncByteStream):
        @override
        async def __aiter__(self) -> AsyncIterator[bytes]:
            if where == "body":
                yield b'event: response.created\ndata: {"type":"response.created"}\n\n'
                entered.set()
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    cancelled.set()
                    raise
            yield b"data: [DONE]\n\n"

        @override
        async def aclose(self) -> None:
            closed.append("stream")

    class Transport(httpx.AsyncBaseTransport):
        @override
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            del request
            if where == "headers":
                entered.set()
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    cancelled.set()
                    raise
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=Stream())

    run.http_transport = Transport()

    async def request() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(run.dispatch)) as client:
            async with client.stream("POST", "http://127.0.0.1:1/responses") as response:
                async for _line in response.aiter_lines():
                    pass

    run.agent = asyncio.create_task(request())
    try:
        await asyncio.wait_for(entered.wait(), 1)
        if transfer:
            run.set_owner("draining-to-human")
            run.phase_cancel.set()
            # A Return starts a new phase. It cannot revive the request from the prior one.
            run.set_owner("agent")
            run.phase_cancel = asyncio.Event()
        else:
            run.stop()
        done, _ = await asyncio.wait({run.agent}, timeout=0.65)
        assert run.agent in done, f"{where}: pending network did not retire with its captured phase"
        assert cancelled.is_set(), "The outstanding network operation was left running"
        assert isinstance(run.agent.exception(), Exception), "Retired request reported successful completion"
        requests = [entry for entry in run.receipts if entry["kind"] == "request"]
        assert len(requests) == 1 and requests[0]["phase"] == "cancelled"
        if where == "body":
            assert closed == ["stream"], "The interrupted SSE response did not close exactly once"
        if transfer:
            release.set()
            # A new request after Return observes its own phase, not the prior cancellation.
            await asyncio.wait_for(request(), 1)
            requests = [entry for entry in run.receipts if entry["kind"] == "request"]
            assert [entry["phase"] for entry in requests] == ["cancelled", "headers"]
        else:
            assert run.cleanup is not None
            await asyncio.wait_for(asyncio.shield(run.cleanup), 1)
            assert run.cleanup_status == "completed"
    finally:
        release.set()
        await asyncio.gather(run.agent, *([run.cleanup] if run.cleanup else []), return_exceptions=True)
        if not run.cleanup:
            run.stop()
            cleanup = cast("asyncio.Task[None] | None", run.cleanup)
            assert cleanup
            await cleanup


async def network_simultaneous_stop_check() -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "browser", "taskId": "service", "api": "responses", "mode": "live"})
    app.current = run
    closed: list[str] = []

    class Stream(httpx.AsyncByteStream):
        @override
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"must not be returned"

        @override
        async def aclose(self) -> None:
            closed.append("stream")

    class Transport(httpx.AsyncBaseTransport):
        @override
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            del request
            run.stop()
            return httpx.Response(200, stream=Stream())

    run.http_transport = Transport()
    try:
        async with httpx.AsyncClient(transport=httpx.MockTransport(run.dispatch)) as client:
            try:
                await client.get("http://127.0.0.1:1/responses")
            except Exception:
                pass
            else:
                raise AssertionError("Response arriving with Stop was returned as success")
        assert closed == ["stream"]
        requests = [entry for entry in run.receipts if entry["kind"] == "request"]
        assert len(requests) == 1 and requests[0]["phase"] == "cancelled"
    finally:
        assert run.cleanup
        await run.cleanup


async def superseded_mixed_frame_check() -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "mixed", "taskId": "mixed", "api": "responses", "mode": "live"})
    app.current = run
    workspace = run.workspace
    assert workspace is not None
    entered, release = asyncio.Event(), asyncio.Event()

    class Guest:
        def stop(self) -> None:
            pass

    workspace.guest = cast(Any, Guest())
    run.task_tab = "host-tab"

    async def frame(*, cancelled: Callable[[], bool] | None = None) -> None:
        del cancelled
        point = workspace.binding()
        if point and point["view"] == "host":
            entered.set()
            await release.wait()
            raise RuntimeError("Controlled superseded Host failure")
        run.frame = b"current Guest"
        run.view_binding = point

    with patch.object(workspace, "frame", frame):
        old = asyncio.create_task(run.refresh_view())
        try:
            await asyncio.wait_for(entered.wait(), 1)
            await cast(Any, workspace).select("guest")
            assert run.frame == b"current Guest"
            release.set()
            await asyncio.wait_for(old, 1)
            assert run.owner == "agent", "obsolete capture stopped a healthy new view"
            assert run.frame == b"current Guest" and workspace.matches(run.view_binding)
        finally:
            release.set()
            await asyncio.gather(old, return_exceptions=True)
            run.stop()
            assert run.cleanup
            await run.cleanup


async def launch_check(fail_close: bool) -> None:
    entered, release = asyncio.Event(), asyncio.Event()

    class Browser:
        closes = 0
        contexts = 0

        def once(self, _event: str, _callback: object) -> None:
            pass

        async def new_context(self, **_options: Any) -> None:
            self.contexts += 1
            raise AssertionError("No context should be created after Stop")

        async def close(self) -> None:
            self.closes += 1
            if fail_close:
                raise RuntimeError("Controlled close failure")

    class Chromium:
        async def launch(self, **_options: Any) -> Browser:
            entered.set()
            await release.wait()
            return opened

    class Local:
        chromium = Chromium()

    opened = Browser()
    browser = WorkspaceBrowser(cast(Playwright, Local()))
    app = Fieldwork(browser, "http://127.0.0.1:41234", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "mixed", "taskId": "mixed", "api": "responses", "mode": "live"})
    app.current = run
    run.agent = asyncio.create_task(run.execute())
    try:
        await asyncio.wait_for(entered.wait(), 2)
        run.stop()
        done, _ = await asyncio.wait({run.agent}, timeout=0.65)
        assert run.agent in done, "Agent remained blocked on mixed launch after Stop"
        assert run.status == "stopped" and run.busy() and run.cleanup_status == "pending"
        assert opened.closes == 0
        release.set()
        assert run.cleanup is not None
        await asyncio.wait_for(asyncio.shield(run.cleanup), 2)
        assert opened.closes == 1 and opened.contexts == 0
        assert run.cleanup_status == ("failed" if fail_close else "completed")
        assert run.busy() is fail_close
        assert run.requests == 0
    finally:
        release.set()
        await asyncio.gather(run.agent, *([run.cleanup] if run.cleanup else []), return_exceptions=True)
        await browser.close()


async def proof_check(environment: str) -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": environment, "taskId": environment, "api": "responses", "mode": "live"})
    app.current = run
    workspace = run.workspace
    assert workspace is not None
    entered, release = threading.Event(), threading.Event()

    class Guest:
        stops = 0

        def verify(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, object]:
            entered.set()
            for _ in range(300):
                if cancelled and cancelled():
                    raise ComputerUseError("Controlled verification cancellation")
                if release.wait(0.01):
                    break
            return {"file_matches": False, "browser_matches": False, "browser_effects": 0}

        def stop(self) -> None:
            self.stops += 1

    guest = Guest()
    workspace.guest = cast(Any, guest)
    verifying = asyncio.create_task(run.inspect())
    try:
        assert await asyncio.to_thread(entered.wait, 1)
        run.set_owner("draining-to-human")
        run.phase_cancel.set()
        done, _ = await asyncio.wait({verifying}, timeout=0.65)
        assert verifying in done, "Agent verification blocked Take until the guest replied"
        try:
            verifying.result()
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Take did not revoke agent verification")
        assert guest.stops == 0
        # A human's later inspection must not reuse the agent's cancelled phase.
        run.set_owner("human")
        release.set()
        state = await run.inspect()
        assert state["verified"] is False
        assert run.requests == 0 and guest.stops == 0
    finally:
        release.set()
        await asyncio.gather(verifying, return_exceptions=True)
        run.stop()
        assert run.cleanup
        await run.cleanup


async def capture_check(poll: bool) -> None:
    from desktop import Desktop

    entered, release = threading.Event(), threading.Event()
    pixels = io.BytesIO()
    Image.new("RGB", (1024, 768)).save(pixels, format="PNG")
    png = pixels.getvalue()

    class Guest:
        frames = 0
        removals = 0

        def __init__(self, _runtime: Path, *, cancelled: Callable[[], bool] | None = None) -> None:
            del cancelled
            self.id = "controlled-capture"

        def healthy(self, *, cancelled: Callable[[], bool] | None = None) -> bool:
            del cancelled
            return True

        def exchange(self, data: bytes, *, timeout: float, limit: int, cancelled: Callable[[], bool] | None) -> bytes:
            del timeout, limit
            request = json.loads(data)
            if request["type"] == "ready":
                return b'{"ok":true}'
            assert request["type"] == "screenshot"
            self.frames += 1
            if self.frames == 1:
                entered.set()
                for _ in range(250):
                    if cancelled and cancelled():
                        raise ComputerUseError("Controlled capture cancellation")
                    if release.wait(0.01):
                        break
            return json.dumps(
                {"ok": True, "image_url": "data:image/png;base64," + base64.b64encode(png).decode()}
            ).encode()

        def remove(self) -> None:
            self.removals += 1

    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "desktop", "taskId": "desktop", "api": "responses", "mode": "live"})
    workspace = run.workspace
    assert workspace is not None
    with patch("desktop.Guest", Guest):
        owned = Desktop(Path("/synthetic/unused"))
        workspace.guest = owned
        work = asyncio.create_task(run.refresh_view() if poll else run.capture())
        try:
            assert await asyncio.to_thread(entered.wait, 1)
            run.set_owner("draining-to-human")
            run.phase_cancel.set()
            done, _ = await asyncio.wait({work}, timeout=0.65)
            assert work in done, "Take retained the owned screenshot transport"
            await asyncio.gather(work, return_exceptions=True)
            assert run.owner == "draining-to-human"
            assert owned._viewers == 0 and cast(Guest, owned._guest).removals == 0
            assert run.screenshot is None
            run.set_owner("human")
            release.set()
            await run.capture()
            assert run.screenshot == png and cast(Guest, owned._guest).removals == 0
            assert run.requests == 0
        finally:
            release.set()
            await asyncio.gather(work, return_exceptions=True)
            await asyncio.to_thread(owned.stop)


async def disconnect_check(owner: str) -> None:
    import desktop_workspace

    class Guest:
        id = "controlled-guest"
        stops = 0

        def __init__(self, _runtime: Path, *, cancelled: Callable[[], bool] | None = None) -> None:
            assert not cancelled or not cancelled()

        def stop(self) -> None:
            self.stops += 1

    with patch.object(desktop_workspace, "Desktop", Guest):
        async with serve(0, "synthetic", {"responses": "synthetic"}, desktop_runtime=Path("/unused")) as app:
            run = Run(app, {"environment": "mixed", "taskId": "mixed", "api": "responses", "mode": "live"})
            app.current = run
            assert run.workspace
            await run.workspace.initialize()
            context = run.context
            assert context and run.workspace.guest
            guest = run.workspace.guest
            if owner in ("stopped", "refused"):
                run.stop("view_failed" if owner == "stopped" else "refused")
            else:
                run.set_owner(owner)
                run.phase_cancel.set()
            await context.close()
            assert run.status == (
                "view_failed" if owner == "stopped" else "refused" if owner == "refused" else "browser_closed"
            )
            assert run.cleanup
            await run.cleanup
            assert run.cleanup_status == "completed" and not run.busy()
            assert cast(Any, guest).stops == 1
            assert run.requests == 0 and context not in app.browser.contexts


async def transfer_check(boundary: str) -> None:
    from file_state import wait_for_decision

    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": "support", "api": "decisions", "mode": "rehearsal"})
    app.current = run
    entered, release = asyncio.Event(), asyncio.Event()
    published: list[str] = []

    async def held() -> None:
        entered.set()
        await release.wait()

    class OwnedDriver:
        async def invalidate_references(self) -> None:
            pass

        async def read_page(self, _args: object, *, cancelled: Callable[[], bool] | None = None) -> dict[str, Any]:
            if boundary == "read":
                await wait_for_decision(held, cancelled)
            return {"version": 1, "elements": []}

    async def capture(*, cancelled: Callable[[], bool] | None = None) -> None:
        if boundary == "capture":
            await wait_for_decision(held, cancelled)
        published.append("capture")

    run.driver = cast(Any, OwnedDriver())
    run.phase_cancel.set()
    run.set_owner("draining-to-agent")
    with patch.object(run, "capture", capture):
        run.transfer = asyncio.create_task(run.give_back(run.version))
        try:
            await asyncio.wait_for(entered.wait(), 1)
            run.stop()
            done, _ = await asyncio.wait({run.transfer}, timeout=0.65)
            assert run.transfer in done, "Stop left Return waiting for its prior read/capture"
            assert run.owner == "stopped" and run.status == "stopped"
            release.set()
            assert run.cleanup
            await asyncio.wait_for(asyncio.shield(run.cleanup), 1)
            await asyncio.sleep(0)
            assert published == [] and run.requests == 0
        finally:
            release.set()
            await asyncio.gather(run.transfer, *([run.cleanup] if run.cleanup else []), return_exceptions=True)


async def fresh_take_check() -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "desktop", "taskId": "desktop", "api": "responses", "mode": "live"})
    app.current = run
    entered, release = threading.Event(), threading.Event()

    class Guest:
        frames = 0
        uncertain_effects = False

        def capture_frame(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, str]:
            del cancelled
            self.frames += 1
            frame = self.frames
            if frame == 1:
                entered.set()
                assert release.wait(3), "Bounded owned poll was not released"
            return {"image_url": "data:image/png;base64," + base64.b64encode(f"frame-{frame}".encode()).decode()}

        def stop(self) -> None:
            pass

    guest = Guest()
    assert run.workspace
    run.workspace.guest = cast(Any, guest)
    run.set_owner("human")
    poll = asyncio.create_task(run.refresh_view())
    run.view_task = poll
    try:
        assert await asyncio.to_thread(entered.wait, 1)
        run.set_owner("agent")
        run.agent = asyncio.create_task(asyncio.sleep(0))
        run.set_owner("draining-to-human")
        run.phase_cancel.set()
        run.transfer = asyncio.create_task(run.take(run.version))
        await asyncio.sleep(0.07)
        assert not run.transfer.done()
        assert poll.done() and run.view_task is None
        assert run.workspace and run.workspace.capturing and not run.workspace.capturing.done()
        assert run.screenshot is None, "Older pixels published before the held capture completed"
        release.set()
        await asyncio.wait_for(asyncio.shield(run.transfer), 2)
        assert run.owner == "human" and run.status == "paused"
        assert await run.matches(run.screenshot_binding)
        assert run.screenshot != b"frame-1" and guest.frames >= 2
        assert run.requests == 0
    finally:
        release.set()
        run.stop()
        await asyncio.gather(poll, *([run.transfer] if run.transfer else []), return_exceptions=True)
        assert run.cleanup
        await run.cleanup


async def human_poll_return_check(kind: str) -> None:
    from mixed_workspace import MixedWorkspace

    environment = "desktop" if kind == "desktop" else "mixed"
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": environment, "taskId": environment, "api": "responses", "mode": "live"})
    app.current = run
    workspace = run.workspace
    assert workspace is not None
    entered, released = threading.Event(), threading.Event()
    host_entered, host_release = asyncio.Event(), asyncio.Event()

    class Guest:
        frames = 0
        stops = 0
        uncertain_effects = False

        def capture_frame(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, str]:
            self.frames += 1
            if self.frames == 1:
                entered.set()
                for _ in range(200):
                    if cancelled and cancelled():
                        raise ComputerUseError("Old owned screenshot cancelled")
                    if released.wait(0.01):
                        break
            pixels = f"frame-{self.frames}".encode()
            return {"image_url": "data:image/png;base64," + base64.b64encode(pixels).decode()}

        def verify(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, object]:
            assert not cancelled or not cancelled()
            return {"browser_effects": 0, "file_matches": False, "browser_matches": False}

        def stop(self) -> None:
            self.stops += 1
            released.set()

    class Page:
        frames = 0

        async def screenshot(self, **_options: object) -> bytes:
            self.frames += 1
            number = self.frames
            if number == 1:
                host_entered.set()
                await asyncio.wait_for(host_release.wait(), 2)
            return f"host-{number}".encode()

    guest, page = Guest(), Page()
    workspace.guest = cast(Any, guest)
    if isinstance(workspace, MixedWorkspace):
        workspace.selected = "host" if kind == "mixed-host" else "guest"
        run.task_tab = "fixture-tab"
        run.task_page = cast(Any, page)
    run.phase_cancel.set()
    run.set_owner("human")
    resumed = asyncio.Event()

    async def agent() -> None:
        resumed.set()

    with patch.object(run, "execute", side_effect=agent):
        poll = asyncio.create_task(run.refresh_view())
        run.view_task = poll
        try:
            if kind == "mixed-host":
                await asyncio.wait_for(host_entered.wait(), 1)
            else:
                assert await asyncio.to_thread(entered.wait, 1)
            run.set_owner("draining-to-agent")
            run.transfer = asyncio.create_task(run.give_back(run.version))
            done, _ = await asyncio.wait({poll, run.transfer}, timeout=0.65)
            assert poll in done and run.transfer in done, "Return kept an old human screenshot"
            await asyncio.gather(poll, run.transfer, return_exceptions=True)
            assert run.owner == "agent" and run.status == "running" and guest.stops == 0
            await asyncio.wait_for(resumed.wait(), 1)
            screenshot = run.screenshot
            assert screenshot and screenshot not in (b"frame-1", b"host-1")
            released.set()
            host_release.set()
            await asyncio.sleep(0.06)
            assert run.screenshot == screenshot and guest.stops == 0 and run.requests == 0
        finally:
            released.set()
            host_release.set()
            run.stop()
            await asyncio.gather(poll, *([run.transfer] if run.transfer else []), return_exceptions=True)
            assert run.cleanup
            await run.cleanup


async def business_ack_check(task_id: str, operation: str) -> None:
    import hashlib

    from business import INTAKE, Business

    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": task_id, "api": "responses", "mode": "rehearsal"})
    business = Business(run)
    run.business = business
    entered, release = asyncio.Event(), asyncio.Event()

    class Page:
        async def wait_for_function(self, _source: str, *, arg: int, timeout: int) -> None:
            assert arg == 1 and timeout == 5000
            entered.set()
            await asyncio.wait_for(release.wait(), 2)

    run.task_page = cast(Any, Page())
    if task_id == "files":
        record = {
            "operation": "attach",
            "job": run.task["job"],
            "count": len(INTAKE),
            "sha256": hashlib.sha256(INTAKE).hexdigest(),
        }
    else:
        record = {
            "operation": "schedule",
            "job": run.task["job"],
            "date": run.task["fields"]["Visit date"],
            "technician": run.task["fields"]["Technician"],
            "note": run.task["fields"]["Service note"],
        }
    permit = business.authorize(record)
    permit["received"] = True
    permit["staged"].set_result(True)
    work = asyncio.create_task(business.finish(permit))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        assert business.snapshot()["verified"] and len(business.results) == 1 and permit["reply"].done()
        if operation == "take":
            run.set_owner("draining-to-human")
            run.phase_cancel.set()
        elif operation == "stop":
            run.stop()
        else:
            release.set()
        done, _ = await asyncio.wait({work}, timeout=0.65)
        assert work in done, "Committed business acknowledgement ignored the ended phase"
        result = await asyncio.gather(work, return_exceptions=True)
        assert isinstance(result[0], ValueError) if operation != "ordinary" else result[0] is None
        assert business.snapshot()["verified"] and business.results == [record]
        release.set()
        await asyncio.sleep(0.06)
        assert business.snapshot()["verified"] and business.results == [record] and run.requests == 0
    finally:
        release.set()
        business.revoke(permit)
        run.stop()
        await asyncio.gather(work, return_exceptions=True)
        assert run.cleanup
        await run.cleanup


async def final_verify_check() -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": "support", "api": "decisions", "mode": "rehearsal"})
    run.business = None
    entered, release = asyncio.Event(), asyncio.Event()

    class Body:
        async def evaluate(self, _source: str) -> dict[str, Any]:
            entered.set()
            await release.wait()
            return {"revision": 1, "finished": True, "results": {}, "fields": {}}

    class Page:
        def locator(self, _selector: str) -> Body:
            return Body()

    run.task_page = cast(Any, Page())
    work = asyncio.create_task(run.verify([]))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        run.set_owner("draining-to-human")
        run.phase_cancel.set()
        done, _ = await asyncio.wait({work}, timeout=0.65)
        assert work in done, "Final Decisions verification retained control"
        results = await asyncio.gather(work, return_exceptions=True)
        assert isinstance(results[0], ValueError)
        release.set()
        await asyncio.sleep(0.07)
        assert run.result is None and run.requests == 0
    finally:
        release.set()
        await asyncio.gather(work, return_exceptions=True)


async def browser_inspection_check(boundary: str) -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": "support", "api": "decisions", "mode": "rehearsal"})
    app.current = run
    entered, release = asyncio.Event(), asyncio.Event()
    inspections = 0
    effects: list[str] = []

    class Body:
        async def evaluate(self, _source: str) -> dict[str, Any]:
            nonlocal inspections
            inspections += 1
            if inspections == (2 if boundary == "after action" else 1):
                entered.set()
                await release.wait()
            return {"revision": 0, "finished": False, "results": [], "fields": {}}

    class Page:
        url = run.fixture_url

        def locator(self, _selector: str) -> Body:
            return Body()

    class Driver:
        async def click(self, _args: object, *, cancelled: Callable[[], bool] | None = None) -> None:
            if cancelled and cancelled():
                raise ValueError("Cancelled")
            effects.append("click")

    run.task_page = cast(Any, Page())
    run.driver = cast(Any, Driver())
    with patch.object(run, "matches", AsyncMock(return_value=True)), patch.object(run, "check_target", AsyncMock()):
        if boundary == "candidates":
            work = asyncio.create_task(run.candidates([]))
        else:
            work = asyncio.create_task(run.act("click", {"tab_id": None, "target": "billing"}, "Billing"))
        try:
            await asyncio.wait_for(entered.wait(), 1)
            run.set_owner("draining-to-human")
            run.phase_cancel.set()
            done, _ = await asyncio.wait({work}, timeout=0.65)
            assert work in done, f"Take retained {boundary}"
            outcome = await asyncio.gather(work, return_exceptions=True)
            assert isinstance(outcome[0], ValueError), outcome
            expected = ["click"] if boundary == "after action" else []
            assert effects == expected and run.requests == 0 and run.result is None
            release.set()
            await asyncio.sleep(0.07)
            assert effects == expected and run.result is None
            # Human inspection must not reuse the revoked agent phase.
            run.set_owner("human")
            state = await run.ensure_current("human", run.version)
            assert state["revision"] == 0
        finally:
            release.set()
            await asyncio.gather(work, return_exceptions=True)


async def browser_take_check(boundary: str) -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": "support", "api": "decisions", "mode": "rehearsal"})
    app.current = run
    page_closed = False

    class Page:
        def is_closed(self) -> bool:
            return page_closed

    class Driver:
        async def invalidate_references(self) -> None:
            nonlocal page_closed
            page_closed = True

    run.agent = asyncio.create_task(asyncio.sleep(0))
    run.set_owner("draining-to-human")
    run.phase_cancel.set()
    if boundary == "after invalidate":
        run.task_page = cast(Any, Page())
        run.driver = cast(Any, Driver())
    version = run.version - 1 if boundary == "stale transfer" else run.version
    with (
        patch.object(run, "capture", AsyncMock()) as capture,
        patch.object(run, "matches", AsyncMock(return_value=True)),
    ):
        run.transfer = asyncio.create_task(run.take(version))
        try:
            await asyncio.wait_for(asyncio.shield(run.transfer), 1)
            assert not any(event["kind"] == "control" and event["text"] == "human" for event in run.events)
            capture.assert_not_awaited()
            if boundary == "stale transfer":
                assert (run.owner, run.status, run.result) == ("draining-to-human", "running", None)
            else:
                assert (run.owner, run.status, run.result) == ("stopped", "handoff_unavailable", "unverified")
            assert run.requests == 0
        finally:
            run.stop()
            if run.cleanup:
                await asyncio.gather(run.cleanup, return_exceptions=True)


async def browser_action_view_check() -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": "support", "api": "decisions", "mode": "rehearsal"})
    entered, release = asyncio.Event(), asyncio.Event()
    effects: list[str] = []

    class Driver:
        async def click(self, _args: object, *, cancelled: Callable[[], bool] | None = None) -> None:
            if cancelled and cancelled():
                raise ValueError("Cancelled")
            effects.append("click")

    async def live_view(*, cancelled: Callable[[], bool] | None = None) -> None:
        del cancelled
        entered.set()
        await release.wait()

    run.driver = cast(Any, Driver())
    state: dict[str, Any] = {"revision": 0, "results": [], "finished": False}
    with (
        patch.object(run, "check_target", AsyncMock()),
        patch.object(run, "ensure_current", AsyncMock(return_value=state)),
        patch.object(run, "inspect", AsyncMock(return_value=state)),
        patch.object(run, "capture", AsyncMock()) as capture,
        patch.object(run, "refresh_view", live_view),
    ):
        work = asyncio.create_task(run.act("click", {"tab_id": None, "target": "billing"}, "Billing"))
        try:
            done, _ = await asyncio.wait({work}, timeout=0.65)
            assert work in done, "Action proof waits for separate live view startup"
            work.result()
            assert not entered.is_set() and effects == ["click"]
            capture.assert_awaited_once()
        finally:
            release.set()
            await asyncio.gather(work, return_exceptions=True)


async def browser_view_retirement_check(boundary: str, take: bool) -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": "support", "api": "decisions", "mode": "rehearsal"})
    app.current = run
    entered, release = asyncio.Event(), asyncio.Event()
    events: list[str] = []
    frame: Callable[[Any], None] | None = None
    point: dict[str, Any] = {"tabId": "t", "sequence": 1, "role": "Task", "tabs": []}

    class Screencast:
        def __init__(self, label: str) -> None:
            self.label = label

        async def start(self, *, on_frame: Callable[[Any], None], **_kwargs: object) -> None:
            nonlocal frame
            events.append(self.label + "-start")
            frame = on_frame
            if boundary == "start":
                entered.set()
                await release.wait()
            on_frame({"data": "late", "timestamp": 1, "viewportWidth": 20, "viewportHeight": 10})

        async def stop(self) -> None:
            events.append(self.label + "-stop")
            if self.label == "previous" and boundary == "previous":
                entered.set()
                await release.wait()

    class Page:
        def __init__(self, label: str) -> None:
            self.screencast = Screencast(label)

        def is_closed(self) -> bool:
            return False

    page = Page("current")

    class Driver:
        def page(self, _id: object) -> tuple[str, Page]:
            return "t", page

    async def binding(*, cancelled: Callable[[], bool] | None = None) -> dict[str, Any] | None:
        return None if run.owner == "stopped" or (cancelled and cancelled()) else point

    async def matches(value: dict[str, Any] | None, *, cancelled: Callable[[], bool] | None = None) -> bool:
        return run.owner != "stopped" and not (cancelled and cancelled()) and value == point

    run.driver = cast(Any, Driver())
    run.task_page = cast(Any, page)
    run.cast_page = cast(Any, Page("previous"))
    human: asyncio.Task[None] | None = None
    with patch.object(run, "binding", side_effect=binding), patch.object(run, "matches", side_effect=matches):
        work = asyncio.create_task(run.refresh_view())
        run.view_task = work
        try:
            await asyncio.wait_for(entered.wait(), 1)
            assert run.cast_page is None and run.frame is None
            if take:
                run.set_owner("draining-to-human")
                run.phase_cancel.set()
            else:
                run.stop()
            done, _ = await asyncio.wait({work}, timeout=0.65)
            assert work in done, "Live-view waiter retained its old phase"
            result = await asyncio.gather(work, return_exceptions=True)
            assert isinstance(result[0], ValueError) and run.cast_task and not run.cast_task.done()
            if take:
                # A subsequent human request must remain stoppable while the old producer drains.
                run.set_owner("human")
                human = asyncio.create_task(run.refresh_view())
                await asyncio.sleep(0)
                run.stop()
                done, _ = await asyncio.wait({human}, timeout=0.65)
                assert human in done, "Human waiter ignored Stop while joining old live-view work"
                result = await asyncio.gather(human, return_exceptions=True)
                assert isinstance(result[0], ValueError)
            assert run.busy() and run.cleanup_status == "pending" and run.status == "stopped"
            release.set()
            assert run.cleanup
            await asyncio.wait_for(asyncio.shield(run.cleanup), 2)
            assert not run.busy() and run.cleanup_status == "completed" and run.frame is None
            assert events == (
                ["previous-stop", "current-start", "current-stop"] if boundary == "start" else ["previous-stop"]
            )
            if frame:
                frame({"data": "late-again", "timestamp": 2, "viewportWidth": 20, "viewportHeight": 10})
                assert run.frame is None
            assert run.requests == 0
        finally:
            release.set()
            await asyncio.gather(
                work, *([human] if human else []), *([run.cleanup] if run.cleanup else []), return_exceptions=True
            )


async def browser_view_human_control() -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1")
    run = Run(app, {"environment": "browser", "taskId": "support", "api": "decisions", "mode": "rehearsal"})
    point: dict[str, Any] = {"tabId": "t", "sequence": 1, "role": "Task", "tabs": []}
    frame: Callable[[Any], None] | None = None

    class Page:
        screencast: Page

        def __init__(self) -> None:
            self.screencast = self

        async def start(self, *, on_frame: Callable[[Any], None], **_kwargs: object) -> None:
            nonlocal frame
            frame = on_frame
            on_frame({"data": "initial", "timestamp": 1, "viewportWidth": 20, "viewportHeight": 10})
            assert run.frame is None

        async def stop(self) -> None:
            pass

        def is_closed(self) -> bool:
            return False

    page = Page()

    class Driver:
        def page(self, _id: object) -> tuple[str, Page]:
            return "t", page

    async def matches(value: dict[str, Any] | None, *, cancelled: Callable[[], bool] | None = None) -> bool:
        return not (cancelled and cancelled()) and value == point

    run.driver = cast(Any, Driver())
    run.task_page = cast(Any, page)
    run.phase_cancel.set()
    run.set_owner("human")
    with (
        patch.object(run, "binding", AsyncMock(return_value=point)),
        patch.object(run, "matches", AsyncMock(side_effect=matches)),
    ):
        try:
            await run.refresh_view(cancelled=lambda: True)
        except ValueError as error:
            assert str(error) == "Cancelled"
        else:
            raise AssertionError("Already cancelled browser view caller was admitted")
        await asyncio.sleep(0)
        assert frame is None and run.cast_task is None and run.frame is None
        await asyncio.wait_for(run.refresh_view(), 1)
        assert run.cast_page is page and run.view_binding == point and frame is not None
        assert run.frame == "initial" and run.view["status"] == "live"
        frame({"data": "current", "timestamp": 2, "viewportWidth": 20, "viewportHeight": 10})
        assert run.frame == "current" and run.view["status"] == "live"
    run.stop()
    assert run.cleanup
    await asyncio.wait_for(asyncio.shield(run.cleanup), 1)


async def mixed_context_retirement_check() -> None:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/synthetic/unused"))
    run = Run(app, {"environment": "mixed", "taskId": "mixed", "api": "responses", "mode": "live"})
    app.current = run
    workspace = run.workspace
    assert workspace is not None
    context_closed, guest_entered, release = asyncio.Event(), asyncio.Event(), asyncio.Event()

    class Context:
        async def close(self) -> None:
            context_closed.set()

    async def retire_guest() -> None:
        guest_entered.set()
        await release.wait()

    async def host_work() -> None:
        await context_closed.wait()

    run.context = cast(Any, Context())
    run.set_owner("human")
    run.human = asyncio.create_task(host_work())
    with patch.object(workspace, "retire", retire_guest):
        try:
            run.stop()
            await asyncio.wait_for(guest_entered.wait(), 1)
            assert context_closed.is_set(), "Guest retirement delayed Host browser closure"
            done, _ = await asyncio.wait({run.human}, timeout=0.65)
            assert run.human in done, "Host work remained pending behind guest retirement"
            assert run.cleanup is not None and not run.cleanup.done()
            release.set()
            await asyncio.wait_for(run.cleanup, 1)
            assert run.cleanup_status == "completed"
        finally:
            release.set()
            await asyncio.gather(run.human, *([run.cleanup] if run.cleanup else []), return_exceptions=True)


async def main() -> None:
    results: list[dict[str, object]] = []
    for name, work in [
        *[
            (f"Network {where} {'Take/Return' if transfer else 'Stop'}", network_phase_check(where, transfer))
            for where in ("headers", "body")
            for transfer in (False, True)
        ],
        ("Response and Stop arrive together", network_simultaneous_stop_check()),
        *[
            (f"Network duration {outcome}", network_duration_check(outcome))
            for outcome in ("complete", "failed", "cancelled", "closed", "close failure")
        ],
        *[(f"Buffered {kind} request duration", network_buffered_duration_check(kind)) for kind in ("json", "sse")],
        ("Superseded mixed Host frame failure", superseded_mixed_frame_check()),
        ("mixed launch clean", launch_check(False)),
        ("mixed launch close failure", launch_check(True)),
        ("mixed Host closes before guest retirement", mixed_context_retirement_check()),
        ("desktop verify Take and human read", proof_check("desktop")),
        ("mixed verify Take and human read", proof_check("mixed")),
        ("desktop capture Take and human read", capture_check(False)),
        ("desktop poll Take and human read", capture_check(True)),
        ("Return Stop at read", transfer_check("read")),
        ("Return Stop at capture", transfer_check("capture")),
        ("Take obtains the current-owner frame after an older poll", fresh_take_check()),
        ("Decisions verification stops on captured phase", final_verify_check()),
        ("Browser candidates Take", browser_inspection_check("candidates")),
        ("Browser before action Take", browser_inspection_check("before action")),
        ("Browser after action Take", browser_inspection_check("after action")),
        ("Browser missing page on Take", browser_take_check("missing page")),
        ("Browser stale Take does not stop new owner version", browser_take_check("stale transfer")),
        ("Browser closed after invalidation on Take", browser_take_check("after invalidate")),
        ("Browser action proof does not wait for live view startup", browser_action_view_check()),
        ("Browser live frame after human approval", browser_view_human_control()),
        ("Browser previous view Stop", browser_view_retirement_check("previous", False)),
        ("Browser starting view Stop", browser_view_retirement_check("start", False)),
        ("Browser previous view Take then human Stop", browser_view_retirement_check("previous", True)),
        ("Browser starting view Take then human Stop", browser_view_retirement_check("start", True)),
        *[
            (f"{kind} human poll drains on Return", human_poll_return_check(kind))
            for kind in ("desktop", "mixed-guest", "mixed-host")
        ],
        *[
            (f"{task_id} committed acknowledgement {action}", business_ack_check(task_id, action))
            for task_id in ("service", "files")
            for action in ("take", "stop", "ordinary")
        ],
    ]:
        try:
            await work
            results.append({"name": name, "pass": True})
        except Exception as error:
            results.append({"name": name, "pass": False, "error": str(error)})
    if "--browser" in sys.argv:
        for owner in ("human", "draining-to-human", "draining-to-agent", "stopped", "refused"):
            try:
                await disconnect_check(owner)
                results.append({"name": f"mixed disconnect {owner}", "pass": True})
            except Exception as error:
                results.append({"name": f"mixed disconnect {owner}", "pass": False, "error": str(error)})
    print(json.dumps({"results": results, "api_calls": 0, "vm_calls": 0}))
    assert all(item["pass"] for item in results), results


if __name__ == "__main__":
    asyncio.run(main())
