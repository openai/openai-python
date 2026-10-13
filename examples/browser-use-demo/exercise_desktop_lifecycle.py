"""Prove only read-only pixels may be obtained during a desktop input lease."""

from __future__ import annotations

import io
import sys
import json
import base64
import asyncio
import threading
from typing import Literal, ClassVar, cast
from pathlib import Path
from unittest.mock import patch
from collections.abc import Mapping, Callable, Awaitable
from typing_extensions import override

import httpx2 as httpx
from PIL import Image
from server import Fieldwork, WorkspaceBrowser, serve
from exercise import JSONMap
from playwright.async_api import Page, BrowserContext

sys.path.insert(1, str(Path(__file__).resolve().parents[1] / "computer-desktop"))
from runner import Run, UploadOwner
from desktop import Desktop
from mixed_workspace import DownloadOwner, MixedWorkspace
from desktop_workspace import DesktopWorkspace

from openai.lib.computer import ComputerUseError


class GuestProbe:
    instances: ClassVar[list[GuestProbe]] = []
    cancel_on_ready: ClassVar[threading.Event | None] = None

    @staticmethod
    def screenshot() -> str:
        buffer = io.BytesIO()
        Image.new("RGB", (1024, 768)).save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    def __init__(self, _runtime_dir: Path, *, cancelled: Callable[[], bool] | None = None) -> None:
        del cancelled
        self.id = "isolated-guest-probe"
        self.failure = False
        self.process = self
        self.removed = False
        self.requests: list[JSONMap] = []
        self.__class__.instances.append(self)

    def poll(self) -> None:
        return None

    def healthy(self, *, cancelled: Callable[[], bool] | None = None) -> bool:
        del cancelled
        return not self.failure and self.poll() is None

    def exchange(self, data: bytes, *, timeout: float, limit: int, cancelled: Callable[[], bool] | None) -> bytes:
        del timeout, limit, cancelled
        request = json.loads(data)
        self.requests.append(request)
        if request["type"] == "ready":
            if self.cancel_on_ready:
                self.cancel_on_ready.set()
            return b'{"ok":true}'
        if request["type"] == "screenshot":
            return json.dumps({"ok": True, "image_url": self.screenshot()}).encode()
        raise AssertionError(request)

    def remove(self) -> None:
        self.removed = True


def main() -> None:
    with patch("desktop.Guest", GuestProbe):
        stopped = threading.Event()
        stopped.set()
        try:
            Desktop(Path("/synthetic/unused"), cancelled=stopped.is_set)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Cancelled startup returned a desktop")
        assert GuestProbe.instances == []
        stopped.clear()
        GuestProbe.cancel_on_ready = stopped
        try:
            Desktop(Path("/synthetic/unused"), cancelled=stopped.is_set)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Startup cancelled during ready returned a desktop")
        created = GuestProbe.instances[-1]
        assert created.removed and created.requests == [{"type": "ready"}]
        GuestProbe.cancel_on_ready = None

        guest = Desktop(Path("/synthetic/unused"))
        entered, release = threading.Event(), threading.Event()
        errors: list[BaseException] = []

        def lease() -> None:
            try:
                guest.operation(lambda _computer: (entered.set(), release.wait(5)))
            except BaseException as exc:
                errors.append(exc)

        thread = threading.Thread(target=lease)
        thread.start()
        assert entered.wait(5)
        image = guest.capture_frame()
        assert image.get("image_url") == GuestProbe.screenshot()
        try:
            guest.operation(lambda _computer: None)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("A second mutation lease was admitted")
        release.set()
        thread.join(5)
        assert not thread.is_alive() and not errors
        guest.stop()
        assert GuestProbe.instances[-1].removed
        try:
            guest.capture_frame()
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Stopped desktop exposed a frame")
    print("PASS startup cancellation reaps its guest; frame read during lease grants no input; Stop revokes view")


async def startup_cleanup(environment: str, fail_removal: bool) -> None:
    class StartupGuest(GuestProbe):
        @override
        def healthy(self, *, cancelled: Callable[[], bool] | None = None) -> bool:
            del cancelled
            return False

        @override
        def remove(self) -> None:
            if fail_removal:
                raise RuntimeError("Controlled guest removal failure")
            super().remove()

    app = Fieldwork(
        cast(WorkspaceBrowser, None),
        "http://127.0.0.1:1",
        desktop_runtime=Path("/synthetic/unused"),
    )
    run = Run(app, {"environment": environment, "taskId": environment, "api": "responses", "mode": "live"})
    app.current = run
    workspace = run.workspace
    assert workspace is not None
    with patch("desktop.Guest", StartupGuest):
        try:
            await DesktopWorkspace.initialize(workspace)
        except Exception:
            pass
        else:
            raise AssertionError("Unhealthy guest completed startup")
        run.stop()
        assert run.cleanup is not None
        await run.cleanup
        created = StartupGuest.instances[-1]
        expected = "failed" if fail_removal else "completed"
        assert run.cleanup_status == expected, (environment, run.cleanup_status, run.receipts)
        assert created.removed is not fail_removal
        assert run.busy() is fail_removal, "Restart must remain blocked if the owned guest was not reaped"
        assert await run.binding() is None
        assert run.requests == 0
        outcomes = [entry["outcome"] for entry in run.receipts if entry["kind"] == "cleanup"]
        assert outcomes == ["pending", expected], outcomes
    print(f"PASS {environment} startup removal {expected}: correct receipt, input closed, restart status accurate")


async def late_download(fail_stop: bool = False) -> None:
    """Stop after actual host/download setup, before the owner reaches Run."""
    created, released = asyncio.Event(), asyncio.Event()
    original_create = DownloadOwner.create
    download: DownloadOwner | None = None
    original_stop: Callable[[], Awaitable[None]] | None = None
    seen = False

    async def held_create(
        page: Page,
        configuration: dict[str, object] | None,
        approve: Callable[[Mapping[str, object]], Awaitable[object]],
    ) -> DownloadOwner:
        nonlocal download, original_stop
        download = await original_create(page, configuration, approve)
        original_stop = download.stop
        if fail_stop:

            async def failed_stop() -> None:
                raise RuntimeError("Injected download stop failure")

            download.stop = failed_stop
        created.set()
        await released.wait()
        return download

    def forbidden_guest(_runtime_dir: Path) -> None:
        raise AssertionError("A stopped mixed startup launched a guest")

    try:
        with patch.object(DownloadOwner, "create", held_create), patch("desktop.Guest", forbidden_guest):
            async with serve(
                0, "synthetic-no-request", {"responses": "synthetic-no-request"}, desktop_runtime=Path("/unused")
            ) as app:
                async with httpx.AsyncClient(base_url=app.origin, timeout=10) as client:
                    client.headers["X-Demo-Token"] = app.token
                    start = await client.post(
                        "/api/start",
                        json={
                            "environment": "mixed",
                            "taskId": "mixed",
                            "api": "responses",
                            "mode": "live",
                        },
                    )
                    assert start.status_code == 200, start.text
                    await asyncio.wait_for(created.wait(), 5)
                    assert isinstance(download, DownloadOwner)
                    assert app.current is not None and isinstance(app.current.workspace, MixedWorkspace)
                    assert app.current.task_page is not None
                    assert download.area.is_dir() and app.current.workspace.download is None
                    stopped = await client.post("/api/stop", json={"runId": app.current.id})
                    assert stopped.status_code == 200
                    for _ in range(100):
                        if app.current.task_page.is_closed():
                            break
                        await asyncio.sleep(0.01)
                    assert app.current.task_page.is_closed()
                    export = await client.get("/api/export", params={"run": app.current.id})
                    assert export.json()["cleanup"] == "pending" and download.area.is_dir(), export.text
                    released.set()
                    assert app.current.cleanup is not None
                    _, pending = await asyncio.wait({app.current.cleanup}, timeout=5)
                    assert not pending, "Late initialization did not settle"
                    export = await client.get("/api/export", params={"run": app.current.id})
                    if fail_stop:
                        assert download.area.exists(), "Failed cleanup incorrectly erased retained area"
                        assert export.json()["cleanup"] == "failed", export.text
                        assert export.json()["status"] == "cleanup_failed", export.text
                        seen = True
                    else:
                        assert not download.area.exists(), "Late mixed download area leaked after Stop"
                        assert download.state()["cleanup"] == "completed"
                        assert export.json()["cleanup"] == "completed", export.text
                    assert app.current.requests == 0 and app.current.workspace.creation is None
    except RuntimeError as error:
        assert fail_stop and seen and str(error) == "Workspace cleanup did not finish.", error
    else:
        assert not fail_stop, "Server hid the late download cleanup failure"
    finally:
        released.set()
        if download and download.area.exists():
            assert original_stop is not None
            await original_stop()
    print(
        f"PASS Stop during real mixed download creation (fail_stop={fail_stop}): no guest/request and truthful cleanup"
    )


async def late_cleanup(kind: Literal["upload", "browser_context", "mixed_context"]) -> None:
    """A real late resource closes, then reports an error that Stop must preserve."""
    arrived, release = asyncio.Event(), asyncio.Event()
    resource: BrowserContext | UploadOwner | None = None
    seen = False
    mixed = kind == "mixed_context"
    try:
        async with (
            serve(
                0, "synthetic-no-request", {"responses": "synthetic-no-request"}, desktop_runtime=Path("/unused")
            ) as app,
            httpx.AsyncClient(base_url=app.origin, timeout=10) as client,
        ):
            client.headers["X-Demo-Token"] = app.token
            target = UploadOwner if kind == "upload" else app.browser
            method = "create" if kind == "upload" else "new_context"
            original = getattr(target, method)

            async def held_create(*args: object, **kwargs: object) -> BrowserContext | UploadOwner:
                nonlocal resource
                resource = await original(*args, **kwargs)
                close_name = "stop" if kind == "upload" else "close"
                original_close = getattr(resource, close_name)

                async def close_then_fail() -> None:
                    await original_close()
                    raise RuntimeError("Injected late resource close failure")

                setattr(resource, close_name, close_then_fail)
                arrived.set()
                await release.wait()
                assert isinstance(resource, (BrowserContext, UploadOwner))
                return resource

            with patch.object(target, method, held_create):
                start = await client.post(
                    "/api/start",
                    json={
                        "environment": "mixed" if mixed else "browser",
                        "taskId": "mixed" if mixed else "files" if kind == "upload" else "support",
                        "api": "responses" if mixed else "decisions",
                        "mode": "live" if mixed else "rehearsal",
                        "allowFileUpload": kind == "upload",
                    },
                )
                assert start.status_code == 200, start.text
                await asyncio.wait_for(arrived.wait(), 5)
                assert app.current is not None
                assert app.current.file_owner is None if kind == "upload" else app.current.context is None
                assert (await client.post("/api/stop", json={"runId": app.current.id})).status_code == 200
                export = await client.get("/api/export", params={"run": app.current.id})
                assert export.json()["cleanup"] == "pending", export.text
                assert app.current.cleanup is not None
                assert not app.current.cleanup.done()
                release.set()
                _, pending = await asyncio.wait({app.current.cleanup}, timeout=5)
                assert not pending
                if kind == "upload":
                    assert isinstance(resource, UploadOwner)
                    assert not resource.area.exists() and resource.state()["cleanup"] == "completed"
                else:
                    assert resource not in app.browser.contexts, "Actual late Chromium context remained open"
                export = await client.get("/api/export", params={"run": app.current.id})
                assert export.json()["cleanup"] == "failed" and export.json()["status"] == "cleanup_failed", export.text
                outcomes = [item["outcome"] for item in export.json()["events"] if item["kind"] == "cleanup"]
                assert outcomes == ["pending", "failed"], outcomes
                restart = await client.post(
                    "/api/start", json={"taskId": "support", "api": "decisions", "mode": "rehearsal"}
                )
                assert restart.status_code == 409
                if mixed:
                    assert isinstance(app.current.workspace, MixedWorkspace) and app.current.workspace.creation is None
                assert app.current.requests == 0
                seen = True
    except RuntimeError as error:
        assert seen and str(error) == "Workspace cleanup did not finish.", error
    else:
        raise AssertionError("Server close hid the late owned-resource failure")
    finally:
        release.set()
    print(f"PASS late {kind} closes then throws: real resource removed, receipt failed, restart refused")


async def cleanup_drains_admitted_tasks(fail_removal: bool) -> None:
    app = Fieldwork(
        cast(WorkspaceBrowser, None),
        "http://127.0.0.1:1",
        desktop_runtime=Path("/synthetic/unused"),
    )
    run = Run(app, {"environment": "desktop", "taskId": "desktop", "api": "responses", "mode": "live"})
    app.current = run
    workspace = run.workspace
    assert workspace is not None
    released, retired = asyncio.Event(), asyncio.Event()

    async def admitted() -> None:
        await released.wait()

    async def close_workspace() -> None:
        retired.set()
        if fail_removal:
            raise RuntimeError("Controlled removal failure")

    run.transfer = asyncio.create_task(admitted())
    run.view_task = asyncio.create_task(admitted())
    with patch.object(workspace, "retire", close_workspace):
        try:
            run.stop()
            await retired.wait()
            assert run.cleanup is not None and not run.cleanup.done()
            assert run.cleanup_status == ("failed" if fail_removal else "pending")
            assert run.busy()
        finally:
            released.set()
            assert run.cleanup is not None
            await run.cleanup
    assert run.transfer.done() and run.view_task.done()
    assert run.cleanup_status == ("failed" if fail_removal else "completed")
    assert run.requests == 0
    print("PASS cleanup drains admitted transfer and frame work, including after removal failure")


if __name__ == "__main__":
    main()
    for environment in ("desktop", "mixed"):
        for fail_removal in (False, True):
            asyncio.run(startup_cleanup(environment, fail_removal))
    asyncio.run(late_download())
    asyncio.run(late_download(fail_stop=True))
    for resource_kind in ("upload", "browser_context", "mixed_context"):
        asyncio.run(late_cleanup(resource_kind))
    for removal_failed in (False, True):
        asyncio.run(cleanup_drains_admitted_tasks(removal_failed))
