"""Fieldwork: a local operator dashboard backed by the Python SDK."""

from __future__ import annotations

import os
import sys
import json
import asyncio
import secrets
import argparse
import threading
from typing import Any, cast
from pathlib import Path
from contextlib import asynccontextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit
from email.message import Message
from collections.abc import Mapping, AsyncGenerator
from typing_extensions import override

import httpx2 as httpx
from playwright.async_api import Page, Browser, Playwright, BrowserContext, async_playwright

sys.path.insert(1, str(Path(__file__).resolve().parents[1] / "browser"))
from runner import TASKS, Run, Reply, MixedHostInputRefusedError, now, as_json, failure
from diagnostics import DiagnosticCapture
from browser_driver import example_browser_channel

ROOT = Path(__file__).resolve().parent
TEMPLATES = {name: (ROOT / name).read_text() for name in ("index.html", "fixture.html", "notes.html", "traces.html")}


class Fieldwork:
    def __init__(
        self,
        browser: WorkspaceBrowser,
        origin: str,
        api_key: str | None = None,
        models: Mapping[str, str | None] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        desktop_runtime: Path | None = None,
        diagnostic_capture: DiagnosticCapture | None = None,
    ) -> None:
        self.browser = browser
        self.origin = origin
        self.api_key = api_key
        self.models = models or {}
        self.transport = transport
        self.desktop_runtime = desktop_runtime
        self.diagnostic_capture = diagnostic_capture
        self.token = secrets.token_hex(24)
        self.current: Run | None = None

    @property
    def launch_url(self) -> str:
        return f"{self.origin}/#token={self.token}"

    async def handle(
        self, method: str, raw_url: str, headers: Message[str, str] | Mapping[str, str], data: bytes
    ) -> Reply:
        host = urlsplit(self.origin).netloc
        if headers.get("Host") != host or headers.get("Origin") not in (None, self.origin):
            return failure(403, "This demo accepts only its bound loopback origin.")
        url = urlsplit(raw_url)
        path = url.path
        query = {name: values[-1] for name, values in parse_qs(url.query).items()}
        if method == "GET" and path in ("/", "/traces"):
            nonce = secrets.token_hex(18)
            return Reply(
                200,
                TEMPLATES["index.html" if path == "/" else "traces.html"].replace("__NONCE__", nonce).encode(),
                {
                    "Content-Type": "text/html; charset=utf-8",
                    "Referrer-Policy": "no-referrer",
                    "Content-Security-Policy": f"default-src 'self'; script-src 'nonce-{nonce}'; style-src 'unsafe-inline'; img-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'",
                },
            )
        run = self.current
        fixture_task = path.split("/")[2] if path.startswith("/fixture/") else None
        if fixture_task in ("stock", "service", "files") and (
            not run
            or not run.business
            or run.task_id != fixture_task
            or not any(
                cookie.strip() == f"fieldwork_workspace={run.workspace_token}"
                for cookie in headers.get("Cookie", "").split(";")
            )
        ):
            return failure(403, "An active workspace capability is required.")
        if path in ("/dispatch", "/route", "/result") or path.startswith("/result/"):
            from mixed_workspace import MixedWorkspace

            if not run or not isinstance(run.workspace, MixedWorkspace) or run.owner == "stopped":
                return failure(403, "No active mixed workspace.")
            if path in ("/dispatch", "/route") and not any(
                cookie.strip() == f"fieldwork_workspace={run.workspace_token}"
                for cookie in headers.get("Cookie", "").split(";")
            ):
                return failure(403, "An active workspace capability is required.")
            return await run.workspace.fixture(method, path, headers, data)
        if method == "GET" and path.startswith("/fixture/"):
            parts = path.removeprefix("/fixture/").split("/")
            task_id = parts[0]
            if (
                task_id not in TASKS
                or len(parts) not in (1, 3)
                or (len(parts) == 3 and (parts[1] != "notes" or parts[2] not in ("brief", "rules")))
                or (
                    task_id in ("stock", "service", "files")
                    and (not run or run.task_id != task_id or run.owner == "stopped")
                )
            ):
                return failure(404, "Unknown task.")
            task = TASKS[task_id]
            if len(parts) == 3:
                visible = {
                    "title": task["title"],
                    "section": "Brief" if parts[2] == "brief" else "Rules",
                    "text": task["summary"] if parts[2] == "brief" else task["instruction"],
                }
                page = TEMPLATES["notes.html"].replace("__NOTES__", json.dumps(visible))
            else:
                visible = {key: value for key, value in task.items() if key != "items"}
                visible["kind"] = task_id
                if "items" in task:
                    visible["items"] = [
                        {key: value for key, value in item.items() if key != "expected"} for item in task["items"]
                    ]
                if task_id in ("stock", "service", "files"):
                    assert run is not None
                    visible["effectURL"] = f"/fixture/{task_id}/effect?run={run.id}" + (
                        "&case=INTAKE-501" if task_id == "files" else ""
                    )
                page = TEMPLATES["fixture.html"].replace("__TASK__", json.dumps(visible))
            connection = "connect-src 'self'; " if task_id in ("stock", "service", "files") else ""
            return Reply(
                200,
                page.encode(),
                {
                    "Content-Type": "text/html; charset=utf-8",
                    "Content-Security-Policy": f"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; {connection}form-action 'none'; frame-ancestors 'none'",
                },
            )
        if method == "POST" and path in ("/fixture/stock/effect", "/fixture/service/effect", "/fixture/files/effect"):
            if (
                headers.get("Origin") != self.origin
                or not run
                or not run.business
                or path != f"/fixture/{run.task_id}/effect"
                or query.get("run") != run.id
                or (run.task_id == "files" and url.query != f"run={run.id}&case=INTAKE-501")
            ):
                return failure(403, "No active business workspace.")
            return await run.business.receive(headers, data)
        if headers.get("X-Demo-Token") != self.token:
            return failure(403, "A dashboard token is required.")
        if method == "GET" and path in ("/api/traces", "/api/trace", "/api/trace-frame"):
            capture = self.diagnostic_capture
            if not capture:
                return failure(404, "No capture selected. Start with --diagnostics or --diagnostics-reopen ID.")
            try:
                if path == "/api/traces":
                    return as_json({"capture": capture.id, "traces": capture.traces()})
                if path == "/api/trace":
                    return as_json(capture.trace(query.get("trace", "")))
                pixels, mime = capture.frame(query.get("trace", ""), query.get("frame", ""))
                return Reply(200, pixels, {"Content-Type": mime})
            except (ValueError, OSError, KeyError, TypeError):
                return failure(404, "Saved trace or frame unavailable.")
        if method == "GET" and path == "/api/state":
            if run and run.owner != "stopped" and not run.view_task:
                run.view_task = asyncio.create_task(run.refresh_view())
                run.view_task.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            return as_json(
                {
                    "liveAvailable": bool(
                        self.api_key and (self.models.get("responses") or self.models.get("decisions"))
                    ),
                    "desktopAvailable": bool(self.desktop_runtime and self.api_key and self.models.get("responses")),
                    "mixedAvailable": bool(self.desktop_runtime and self.api_key and self.models.get("responses")),
                    "run": await run.snapshot() if run else None,
                }
            )
        if method == "GET":
            if not run or query.get("run") != run.id:
                return failure(404, "This run is no longer current.")
            if path == "/api/inspector":
                if run.environment != "browser" or run.task_id == "files" or run.owner != "human" or not run.driver:
                    return failure(409, "Take control of a browser task to inspect its tools.")
                helper = run.toolset("human")
                tools = helper.tools
                helper.close()
                return as_json({"tools": tools})
            if path == "/api/export":
                return as_json(run.receipt())
            if path == "/api/checkpoint":
                point = next(
                    (item for item in run.checkpoints if str(item["sequence"]) == query.get("checkpoint")), None
                )
                if not point:
                    return failure(404, "Saved checkpoint unavailable.")
                return Reply(
                    200,
                    point["pixels"],
                    {"Content-Type": "image/jpeg" if run.environment == "browser" else "image/png"},
                )
            if path in ("/api/view", "/api/screenshot"):
                live = path == "/api/view"
                if live and (run.owner == "stopped" or run.closed):
                    return failure(410, "The browser view has ended.")
                binding = run.view_binding if live else run.screenshot_binding
                if (
                    not binding
                    or (
                        run.environment == "browser"
                        and (
                            query.get("tabId") != binding["tabId"] or query.get("sequence") != str(binding["sequence"])
                        )
                    )
                    or (
                        run.environment != "browser"
                        and (
                            query.get("desktopId") != binding["desktopId"]
                            or query.get("ownerVersion") != str(binding["ownerVersion"])
                        )
                    )
                    or (
                        run.environment == "mixed"
                        and (
                            query.get("view") != binding["view"]
                            or query.get("tabId") != binding["tabId"]
                            or query.get("sequence") != str(binding["sequence"])
                        )
                    )
                    or (run.owner != "stopped" and not await run.matches(binding))
                ):
                    return failure(409, "This page view is no longer current.")
                pixels = run.frame if live else run.screenshot
                if not pixels:
                    return failure(409, "The browser view is starting.")
                return Reply(
                    200, pixels, {"Content-Type": "image/jpeg" if run.environment == "browser" else "image/png"}
                )
            return failure(404, "Unknown route.")
        if method != "POST":
            return failure(404, "Unknown route.")
        try:
            parsed: object = json.loads(data or b"{}")
        except (ValueError, UnicodeDecodeError):
            return failure(400, "Invalid demo request.")
        if type(parsed) is not dict:
            return failure(400, "Invalid demo request.")
        body = cast(dict[str, Any], parsed)
        if path == "/api/start":
            if run and run.busy():
                return failure(409, "Stop the current run before starting another.")
            environment = body.get("environment", "browser")
            if (
                environment not in ("browser", "desktop", "mixed")
                or (body.get("taskId") not in TASKS if environment == "browser" else body.get("taskId") != environment)
                or body.get("api") not in ("responses", "decisions")
                or body.get("mode") not in ("live", "rehearsal")
            ):
                return failure(400, "Choose an available task, API, and run mode.")
            if environment != "browser" and (
                not self.desktop_runtime or body["api"] != "responses" or body["mode"] != "live"
            ):
                return failure(400, "The isolated desktop needs a configured runtime and live Responses.")
            if body["taskId"] == "files" and body.get("allowFileUpload") is not True:
                return failure(400, "Opt in to the synthetic file upload before starting file intake.")
            if body["mode"] == "rehearsal" and body["api"] != "decisions":
                return failure(400, "Rehearsal uses Decisions. Choose Live API for Responses.")
            if body["mode"] == "live" and (not self.api_key or not self.models.get(body["api"])):
                return failure(400, "Configure a server API key and a model for the selected API.")
            run = self.current = Run(self, body)
            run.agent = asyncio.create_task(run.execute())
            return as_json(await run.snapshot())
        if not run or body.get("runId") != run.id:
            return failure(409, "This run is no longer current.")
        if path == "/api/stop":
            run.stop()
            return as_json({"stopped": True})
        if path == "/api/approval":
            if (
                (run.owner != "agent" and not (run.owner == "human" and run.human and not run.human.done()))
                or body.get("ownerVersion") != run.version
                or not await run.matches(body)
                or not run.approval
                or body.get("approvalId") != run.approval["id"]
                or type(body.get("approved")) is not bool
                or now() >= run.approval["expiresAt"]
            ):
                return failure(409, "This approval is no longer pending.")
            if not body["approved"]:
                run.stop("refused")
            else:
                run.settle(True)
            return as_json({"accepted": True})
        if path in ("/api/take-control", "/api/return-control", "/api/input", "/api/mixed-view", "/api/inspect"):
            if run.task_id == "files":
                return failure(
                    403, "View and Stop are available. File selection is controlled by the approved fixture task."
                )
            initial = (
                path == "/api/take-control"
                and run.environment == "browser"
                and not run.task_page
                and body.get("tabId") is None
                and body.get("sequence") is None
            )
            if (
                (run.transfer and not run.transfer.done())
                or body.get("ownerVersion") != run.version
                or run.owner == "stopped"
                or (not initial and not await run.matches(body))
            ):
                return failure(409, "This control phase is no longer current.")
            if path == "/api/mixed-view" and run.environment == "mixed":
                from mixed_workspace import MixedWorkspace

                assert isinstance(run.workspace, MixedWorkspace)
                if (
                    run.owner not in ("agent", "human")
                    or (run.human and not run.human.done())
                    or body.get("selected") not in ("host", "guest")
                ):
                    return failure(409, "Wait until this mixed workspace can change views.")
                await run.workspace.select(body["selected"])
                return as_json({"accepted": True})
            if path == "/api/take-control" and run.owner == "agent":
                run.set_owner("draining-to-human")
                run.phase_cancel.set()
                run.settle(False)
                run.transfer = asyncio.create_task(run.take(run.version))
                return as_json({"accepted": True})
            if path == "/api/return-control" and run.owner == "human":
                if run.human and not run.human.done():
                    return failure(409, "Finish or stop your current action before returning control.")
                run.set_owner("draining-to-agent")
                run.transfer = asyncio.create_task(run.give_back(run.version))
                return as_json({"accepted": True})
            if path == "/api/inspect":
                if (
                    run.environment != "browser"
                    or run.owner != "human"
                    or (run.human and not run.human.done())
                    or not run.driver
                    or run.uncertain
                    or body.get("consent") is not True
                    or type(body.get("name")) is not str
                    or type(body.get("args")) is not dict
                ):
                    return failure(409, "Take control and consent to one manual browser call.")
                from openai.types.responses import ResponseFunctionToolCall

                helper = run.toolset("human")
                call_id = secrets.token_hex(18)
                call = ResponseFunctionToolCall(
                    type="function_call",
                    status="completed",
                    id=call_id,
                    call_id=call_id,
                    name=body["name"],
                    arguments=json.dumps(body["args"]),
                )

                async def invoke() -> None:
                    output = await helper.execute(call, cancelled=lambda: run.owner != "human")
                    result.update(output=output)

                result: dict[str, Any] = {}
                run.human = asyncio.create_task(invoke())
                try:
                    await run.human
                    return as_json(result)
                except Exception:
                    return failure(409, "The tool did not finish. Read the current page and check its outcome.")
                finally:
                    helper.close()
            if path == "/api/input" and run.owner == "human" and not (run.human and not run.human.done()):
                if not run.valid_input(body):
                    return failure(400, "Choose a valid bounded browser input.")
                input_task = asyncio.create_task(run.human_input(body))
                run.human = input_task
                try:
                    await input_task
                    return as_json({"accepted": True})
                except MixedHostInputRefusedError as error:
                    if run.human is input_task:
                        run.human = None
                    return failure(400, str(error))
                except Exception:
                    return failure(409, "The input outcome is uncertain. No automatic resume.")
            return failure(409, "The browser is not accepting this control action.")
        return failure(404, "Unknown route.")

    async def close(self) -> None:
        if self.current:
            self.current.stop()
            assert self.current.cleanup is not None
            _, pending = await asyncio.wait({self.current.cleanup}, timeout=35)
            if pending or self.current.cleanup_status != "completed":
                raise RuntimeError("Workspace cleanup did not finish.")


class WorkspaceBrowser:
    def __init__(self, playwright: Playwright) -> None:
        self.playwright = playwright
        self.launch: asyncio.Task[Browser] | None = None
        self.closing: asyncio.Task[None] | None = None

    async def opened(self) -> Browser:
        if self.closing:
            raise RuntimeError("The workspace browser is closing.")
        if self.launch is None:
            channel = example_browser_channel()

            async def start() -> Browser:
                opened = await self.playwright.chromium.launch(
                    headless=True,
                    channel=channel,
                    chromium_sandbox=True,
                    handle_sigint=False,
                    env={
                        name: value
                        for name in ("PATH", "HOME", "TMPDIR")
                        if (value := os.environ.get(name)) is not None
                    },
                )
                current = asyncio.current_task()

                def disconnected(_browser: Browser) -> None:
                    if self.launch is current:
                        self.launch = None

                opened.once("disconnected", disconnected)
                return opened

            self.launch = asyncio.create_task(start())
        starting = self.launch
        try:
            browser = await asyncio.shield(starting)
        except Exception:
            if self.launch is starting:
                self.launch = None
            raise
        if self.closing:
            raise RuntimeError("The workspace browser is closing.")
        return browser

    async def new_context(self, *, run: Run | None = None, **options: Any) -> BrowserContext:
        if run is None:
            browser = await self.opened()
            return await browser.new_context(**options)
        if run.phase_cancel.is_set():
            raise RuntimeError("Browser setup was stopped.")
        opening = asyncio.create_task(self.opened())
        stopped = asyncio.create_task(run.phase_cancel.wait())
        try:
            await asyncio.wait({opening, stopped}, return_when=asyncio.FIRST_COMPLETED)
            if run.phase_cancel.is_set():
                starting = self.launch
                if starting:
                    self.launch = None

                    async def retire_launch() -> None:
                        try:
                            late = await starting
                        except Exception:
                            # A rejected launch created no owned browser.
                            return
                        await run.close_owned(late.close)

                    run.launch_retirement = asyncio.create_task(retire_launch())
                raise RuntimeError("Browser setup was stopped.")
            browser = opening.result()
        finally:
            stopped.cancel()
            if not opening.done():
                opening.cancel()
            await asyncio.gather(opening, stopped, return_exceptions=True)
        creating = asyncio.create_task(browser.new_context(**options))
        stopped = asyncio.create_task(run.phase_cancel.wait())
        try:
            await asyncio.wait({creating, stopped}, return_when=asyncio.FIRST_COMPLETED)
            if run.phase_cancel.is_set():
                # Only this private run owns the captured generation. Reap it before
                # admitting a replacement, even if context creation has not replied.
                await run.close_owned(browser.close)
                raise RuntimeError("Browser setup was stopped.")
            return creating.result()
        finally:
            stopped.cancel()
            if not creating.done():
                creating.cancel()
            creating.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            await asyncio.gather(stopped, return_exceptions=True)

    async def new_page(self, **options: Any) -> Page:
        browser = await self.opened()
        return await browser.new_page(**options)

    @property
    def contexts(self) -> list[BrowserContext]:
        if self.launch is None or not self.launch.done() or self.launch.cancelled() or self.launch.exception():
            return []
        return self.launch.result().contexts

    async def close(self) -> None:
        if self.closing is None:
            self.closing = asyncio.create_task(self.finish_close())
        cancelled = False
        while not self.closing.done():
            try:
                await asyncio.shield(self.closing)
            except asyncio.CancelledError:
                cancelled = True
        self.closing.result()
        if cancelled:
            raise asyncio.CancelledError()

    async def finish_close(self) -> None:
        if self.launch is None:
            return
        try:
            browser = await self.launch
        except Exception:
            # No browser exists after a launch failure. Closing an opened one must still propagate errors.
            return
        await browser.close()


@asynccontextmanager
async def serve(
    port: int = 0,
    api_key: str | None = None,
    models: Mapping[str, str | None] | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    desktop_runtime: Path | None = None,
    diagnostic_capture: DiagnosticCapture | None = None,
) -> AsyncGenerator[Fieldwork, None]:
    """Launch with one loop-owned Fieldwork and no mutable run state on HTTP threads."""
    loop = asyncio.get_running_loop()
    app = None

    class Handler(BaseHTTPRequestHandler):
        def respond(self) -> None:
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 0 or size > 65536:
                    answer = failure(400, "The demo control request is too large.")
                else:
                    data = self.rfile.read(size)
                    assert app is not None
                    answer = asyncio.run_coroutine_threadsafe(
                        app.handle(self.command, self.path, self.headers, data), loop
                    ).result()
            except Exception:
                answer = failure(400, "Invalid demo request.")
            self.send_response(answer.status)
            for name, value in answer.headers.items():
                self.send_header(name, value)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(answer.body)))
            self.end_headers()
            try:
                self.wfile.write(answer.body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        do_GET = respond
        do_POST = respond

        @override
        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    thread = None
    try:
        async with async_playwright() as playwright:
            browser = WorkspaceBrowser(playwright)
            app = Fieldwork(
                browser,
                f"http://127.0.0.1:{server.server_port}",
                api_key,
                models,
                transport,
                desktop_runtime,
                diagnostic_capture,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                yield app
            finally:

                async def cleanup() -> None:
                    try:
                        await app.close()
                    finally:
                        try:
                            await browser.close()
                        finally:
                            await asyncio.to_thread(server.shutdown)
                            await asyncio.to_thread(thread.join)
                            server.server_close()

                finishing = asyncio.create_task(cleanup())
                # Retrieve a late failure even when the deadline ends our wait.
                finishing.add_done_callback(lambda task: task.exception() if not task.cancelled() else None)
                _, pending = await asyncio.wait({finishing}, timeout=35)
                if pending:
                    if app.current:
                        app.current.cleanup_status = "failed"
                        app.current.record("cleanup", outcome="failed")
                    raise RuntimeError("Workspace cleanup did not finish. Private evidence retained.")
                finishing.result()
    finally:
        if thread is None:
            server.server_close()


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.environ.get("DEMO_PORT", 0)))
    parser.add_argument("--desktop-runtime", type=Path, help="Existing local guest runtime")
    diagnostic = parser.add_mutually_exclusive_group()
    diagnostic.add_argument("--diagnostics", action="store_true", help="Save bounded private local diagnostic files")
    diagnostic.add_argument("--diagnostics-reopen", metavar="ID", help="Reopen a demo-owned capture by its printed ID")
    args = parser.parse_args()
    models = {
        name: os.environ.get(f"OPENAI_{name.upper()}_MODEL", os.environ.get("OPENAI_MODEL"))
        for name in ("responses", "decisions")
    }
    api_key = os.environ.get("OPENAI_API_KEY")
    diagnostic_capture = (
        DiagnosticCapture((api_key, *models.values()), args.diagnostics_reopen)
        if args.diagnostics or args.diagnostics_reopen
        else None
    )
    async with serve(
        args.port,
        api_key,
        models,
        desktop_runtime=args.desktop_runtime,
        diagnostic_capture=diagnostic_capture,
    ) as app:
        print(
            f"Browser-use example (private link): {app.launch_url}"
            if sys.stdout.isatty()
            else f"Browser-use example: {app.origin}\nPrivate link unavailable in redirected output; relaunch in a terminal.",
            flush=True,
        )
        if diagnostic_capture:
            print(
                f"Private diagnostic files: {diagnostic_capture.directory}. Reopen ID: {diagnostic_capture.id}. Inspect them before sharing.",
                flush=True,
            )
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
