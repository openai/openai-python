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
from runner import TASKS, Run, Reply, now, as_json, failure
from read_only import example_browser_channel

ROOT = Path(__file__).resolve().parent
TEMPLATES = {name: (ROOT / name).read_text(encoding="utf-8") for name in ("index.html", "fixture.html")}


class Fieldwork:
    def __init__(
        self,
        browser: WorkspaceBrowser,
        origin: str,
        api_key: str | None = None,
        models: Mapping[str, str | None] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.browser = browser
        self.origin = origin
        self.api_key = api_key
        self.models = models or {}
        self.transport = transport
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
        if method == "GET" and path == "/":
            nonce = secrets.token_hex(18)
            return Reply(
                200,
                TEMPLATES["index.html"].replace("__NONCE__", nonce).encode(),
                {
                    "Content-Type": "text/html; charset=utf-8",
                    "Referrer-Policy": "no-referrer",
                    "Content-Security-Policy": f"default-src 'self'; script-src 'nonce-{nonce}'; style-src 'unsafe-inline'; img-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'",
                },
            )
        run = self.current
        if method == "GET" and path == "/fixture/reservation":
            page = TEMPLATES["fixture.html"].replace(
                "__TASK__", json.dumps({**TASKS["reservation"], "kind": "reservation"})
            )
            return Reply(
                200,
                page.encode(),
                {
                    "Content-Type": "text/html; charset=utf-8",
                    "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; form-action 'none'; frame-ancestors 'none'",
                },
            )
        if headers.get("X-Demo-Token") != self.token:
            return failure(403, "A dashboard token is required.")
        if method == "GET" and path == "/api/state":
            if run and run.owner != "stopped" and not run.view_task:
                run.view_task = asyncio.create_task(run.refresh_view())
                run.view_task.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            return as_json(
                {
                    "liveAvailable": {
                        api: bool(self.api_key and self.models.get(api)) for api in ("responses", "decisions")
                    },
                    "run": await run.snapshot() if run else None,
                }
            )
        if method == "GET":
            if not run or query.get("run") != run.id:
                return failure(404, "This run is no longer current.")
            if path in ("/api/view", "/api/screenshot"):
                live = path == "/api/view"
                if live and (run.owner == "stopped" or run.closed):
                    return failure(410, "The browser view has ended.")
                binding = run.view_binding if live else run.screenshot_binding
                if (
                    not binding
                    or query.get("tabId") != binding["tabId"]
                    or query.get("sequence") != str(binding["sequence"])
                    or (run.owner != "stopped" and not await run.matches(binding))
                ):
                    return failure(409, "This page view is no longer current.")
                pixels = run.frame if live else run.screenshot
                if not pixels:
                    return failure(409, "The browser view is starting.")
                return Reply(200, pixels, {"Content-Type": "image/jpeg"})
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
            if (
                body.get("taskId") != "reservation"
                or body.get("api") not in ("responses", "decisions")
                or body.get("mode") not in ("live", "rehearsal")
                or set(body) - {"taskId", "api", "mode"}
            ):
                return failure(400, "Choose Book a table, an API, and a run mode.")
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
        if path in ("/api/take-control", "/api/return-control", "/api/input"):
            initial = (
                path == "/api/take-control"
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
            if path == "/api/input" and run.owner == "human" and not (run.human and not run.human.done()):
                if not run.valid_input(body):
                    return failure(400, "Choose a valid bounded browser input.")
                input_task = asyncio.create_task(run.human_input(body))
                run.human = input_task
                try:
                    await input_task
                    return as_json({"accepted": True})
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
                # The client disconnected after the request completed; there is no response left to send.
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
    args = parser.parse_args()
    models = {
        name: os.environ.get(f"OPENAI_{name.upper()}_MODEL", os.environ.get("OPENAI_MODEL"))
        for name in ("responses", "decisions")
    }
    api_key = os.environ.get("OPENAI_API_KEY")
    async with serve(args.port, api_key, models) as app:
        print(
            f"Browser-use example (private link): {app.launch_url}"
            if sys.stdout.isatty()
            else f"Browser-use example: {app.origin}\nPrivate link unavailable in redirected output; relaunch in a terminal.",
            flush=True,
        )
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Ctrl-C ends the CLI after main's context manager performs its normal shutdown.
        pass
