"""Responses runner, real Chromium and one literal-loopback result fixture."""

from __future__ import annotations

import os
import re
import sys
import json
import socket
import asyncio
import tempfile
from types import SimpleNamespace
from pathlib import Path
from threading import Event, Thread
from contextlib import asynccontextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import patch
from collections.abc import Mapping, Callable, Awaitable, AsyncGenerator
from typing_extensions import TypedDict, override

import httpx2
from file_download import PARENT, DownloadOwner, digest, refusal, unknown, milliseconds
from playwright.async_api import Page, Browser, Download, JSHandle, async_playwright

from openai import AsyncOpenAI
from openai.types.responses import Response, FunctionToolParam
from openai.lib.responses_tool_runner import (
    AsyncRegisteredFunction,
    AsyncResponsesToolRunner,
)
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

CONTENT = b"PRIVATE_RESULT_ONLY_FOR_QUARANTINE\n" * 600
CHECKS: list[dict[str, object]] = []
RULE: FunctionToolParam = {
    "type": "function",
    "name": "download",
    "description": "Receive the prepared fixture result.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {"grant_id": {"type": "string"}},
        "required": ["grant_id"],
        "additionalProperties": False,
    },
}


async def approve(_: Mapping[str, object]) -> bool:
    return True


async def wait_for(predicate: Callable[[], bool]) -> None:
    expiry = asyncio.get_running_loop().time() + 4
    while not predicate():
        assert asyncio.get_running_loop().time() < expiry, "local observable failed to settle"
        await asyncio.sleep(0.01)


def denied_issue(entry: Entry) -> None:
    try:
        entry.issue()
    except ValueError as exc:
        assert str(exc) == "Result grant refused."
    else:
        raise AssertionError("exhausted grant was issued")


class FixtureRequest(TypedDict, total=False):
    path: str
    method: str
    headers: dict[str, str]


class Entry(SimpleNamespace):
    name: str
    mode: str
    requests: list[FixtureRequest]
    deliveries: list[int]
    entered: Event
    release: Event
    blocked: int
    page: Page
    url: str
    config: dict[str, object]
    owner: DownloadOwner

    def issue(self, expiry: int | None = None) -> dict[str, str]:
        return self.owner.issue(
            {"url": self.url.removesuffix("/fixture") + "/result", "count": len(CONTENT), "sha256": digest(CONTENT)},
            milliseconds() + 15000 if expiry is None else expiry,
        )


class ResultServer(ThreadingHTTPServer):
    entry: Entry


class Fixture(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        assert isinstance(self.server, ResultServer)
        e = self.server.entry
        try:
            if self.path == "/fixture":
                body = PARENT.joinpath("file-download.html").read_bytes()
                self.send_response(200)
                self.send_header("content-type", "text/html")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path == "/unsolicited":
                self.send_response(200)
                self.send_header("content-type", "application/octet-stream")
                self.send_header("content-disposition", 'attachment; filename="../../UNTRUSTED_NAME"')
                self.send_header("content-length", str(len(CONTENT)))
                self.end_headers()
                self.wfile.write(CONTENT)
                return
            if self.path != "/result":
                if self.path == "/trap":
                    e.requests.append({"path": "TRAP"})
                self.send_response(404)
                self.send_header("content-length", "0")
                self.end_headers()
                return
            e.requests.append(
                {
                    "path": self.path,
                    "method": self.command,
                    "headers": {k.lower(): v for k, v in self.headers.items()},
                }
            )
            e.entered.set()
            mode = e.mode
            if mode in ("held-headers", "slow-headers"):
                e.release.wait(5)
            if mode == "redirect":
                self.send_response(302)
                self.send_header("location", "/trap")
                self.send_header("content-type", "application/octet-stream")
                self.send_header("content-length", "0")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header(
                "content-type",
                "text/html" if mode == "html" else "application/octet-stream",
            )
            self.send_header(
                "content-disposition",
                "attachment; filename=\"../../UNTRUSTED_NAME\"; filename*=utf-8''/tmp/PRIVATE_RESULT",
            )
            self.send_header("x-untrusted-path", "/tmp/PRIVATE_RESULT")
            self.send_header("content-encoding", "gzip" if mode == "encoded" else "identity")
            if mode == "huge-headers":
                self.send_header("x-oversize", "x" * 12000)
            chunked = mode not in (
                "positive",
                "held-headers",
                "slow-headers",
                "short-length",
                "long-length",
                "wrong-digest",
            )
            if chunked:
                self.send_header("transfer-encoding", "chunked")
            else:
                n = len(CONTENT) + (-5 if mode == "short-length" else 5 if mode == "long-length" else 0)
                self.send_header("content-length", str(n))
            self.end_headers()
            self.wfile.flush()

            def deliver(chunk: bytes) -> None:
                e.deliveries.append(len(chunk))
                if chunked:
                    self.wfile.write(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n")
                else:
                    self.wfile.write(chunk)
                self.wfile.flush()

            if mode == "oversized":
                for _ in range(12):
                    deliver(b"X" * 8192)
            elif mode in ("truncate", "lost-final-chunk"):
                deliver(CONTENT[:9000] if mode == "truncate" else CONTENT)
                e.release.wait(5)
                self.close_connection = True
                self.connection.shutdown(socket.SHUT_RDWR)
                return
            elif mode in ("held-body", "slow-body"):
                deliver(CONTENT[:12000])
                e.release.wait(5)
                deliver(CONTENT[12000:])
            else:
                deliver(b"Z" * len(CONTENT) if mode == "wrong-digest" else CONTENT)
            if chunked:
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            self.close_connection = True


class Call:
    def __init__(
        self,
        owner: DownloadOwner,
        grant: Mapping[str, str],
        args: dict[str, object] | None = None,
        *,
        read_state: bool = False,
    ) -> None:
        self.bodies: list[ResponseCreateParamsNonStreaming] = []
        self.args = {"grant_id": grant["grant_id"]} if args is None else args

        async def transport(request: httpx2.Request) -> httpx2.Response:
            self.bodies.append(json.loads(request.content))
            assert len(self.bodies) <= 2, "no automatic replay"
            if len(self.bodies) == 1:
                output: list[dict[str, object]] = [
                    {
                        "id": "fc_fixture",
                        "type": "function_call",
                        "name": "file_status" if read_state else "download",
                        "call_id": "download_once",
                        "status": "completed",
                        "arguments": json.dumps({} if read_state else self.args),
                    }
                ]
            else:
                output = [
                    {
                        "type": "message",
                        "id": "msg_fixture",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "Finished",
                                "annotations": [],
                            }
                        ],
                    }
                ]
            return httpx2.Response(
                200,
                json={
                    "id": "resp_" + str(len(self.bodies)),
                    "object": "response",
                    "created_at": 0,
                    "model": "",
                    "status": "completed",
                    "output": output,
                },
                request=request,
            )

        self.client = AsyncOpenAI(
            api_key="synthetic-unused",
            base_url="http://fixture.invalid/v1",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
        )

        async def status(_: dict[str, object]) -> str:
            return json.dumps(owner.state())

        runner = AsyncResponsesToolRunner(
            functions=[
                AsyncRegisteredFunction(RULE, owner.download),
                AsyncRegisteredFunction(
                    {
                        "type": "function",
                        "name": "file_status",
                        "description": "Read bounded transfer and cleanup outcomes.",
                        "strict": True,
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                            "additionalProperties": False,
                        },
                    },
                    status,
                ),
            ]
        )

        async def execute() -> Response:
            try:
                return await runner.run(
                    self.client,
                    {
                        "model": "",
                        "input": "Receive the prepared result.",
                        "store": False,
                    },
                    max_steps=3,
                    # This status read is a separate, explicitly authorized run after Stop.
                    cancelled=None if read_state else lambda: owner.stopped,
                )
            finally:
                await self.client.close()

        self.task = asyncio.create_task(execute())

    async def done(self, owner: DownloadOwner, status: str) -> None:
        await self.task
        assert len(self.bodies) == 2
        history = self.bodies[1].get("input")
        assert history is not None and not isinstance(history, str)
        item = next(v for v in history if v.get("type") == "function_call_output")
        assert item.get("type") == "function_call_output"
        output = item.get("output")
        assert isinstance(output, str)
        assert json.loads(output) == owner.receipt()
        assert owner.receipt()["status"] == status, owner.receipt()

    async def cancelled(self, *, original: bool = False) -> None:
        try:
            await self.task
        except asyncio.CancelledError:
            assert len(self.bodies) == 1, self.bodies
        except Exception:
            assert not original, "original task cancellation must propagate"
            assert len(self.bodies) == 1, self.bodies
        else:
            raise AssertionError("runner must halt before another request")


def files(e: Entry) -> list[Path]:
    return list(e.owner.quarantine.iterdir()) if e.owner.quarantine.exists() else []


def nothing(e: Entry) -> None:
    assert e.owner.stats["requests"] == 0
    assert not e.requests
    assert files(e) == []


async def refused(e: Entry, grant: Mapping[str, str], args: dict[str, object] | None = None) -> None:
    await Call(e.owner, grant, args).done(e.owner, "refused")
    nothing(e)


async def completed(e: Entry, grant: Mapping[str, str]) -> None:
    await Call(e.owner, grant).done(e.owner, "completed")
    paths = files(e)
    assert len(paths) == 1 and re.fullmatch(r"q_[a-f0-9]{24}", paths[0].name)
    assert paths[0].stat().st_mode & 0o777 == 0o600
    assert paths[0].read_bytes() == CONTENT
    assert e.owner.receipt() == {
        "status": "completed",
        "attempted": True,
        "completed": True,
        "count": len(CONTENT),
        "sha256": digest(CONTENT),
    }
    assert len(e.requests) == 1
    assert e.owner.state()["current"] == {"status": "completed", "effect": "completed"}
    assert e.owner.state()["cleanup"] == "not_started"


async def retired(e: Entry, grant: Mapping[str, str]) -> None:
    assert e.owner.receipt() == unknown(), e.owner.receipt()
    assert files(e) == []
    assert json.loads(await e.owner.download({"grant_id": grant["grant_id"]})) == refusal()
    denied_issue(e)
    assert e.owner.stats["requests"] == 1


@asynccontextmanager
async def scenario(
    browser: Browser,
    name: str,
    mode: str,
    *,
    enabled: bool = True,
    no_config: bool = False,
    approval: Callable[[Mapping[str, object]], Awaitable[object]] = approve,
) -> AsyncGenerator[Entry, None]:
    print(json.dumps({"phase": "begin", "name": name}), flush=True)
    e = Entry(
        name=name,
        mode=mode,
        requests=[],
        deliveries=[],
        entered=Event(),
        release=Event(),
        blocked=0,
    )
    server = ResultServer(("127.0.0.1", 0), Fixture)
    server.daemon_threads = True
    server.entry = e
    thread = Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()
    context = await browser.new_context(service_workers="block", accept_downloads=False)
    e.page = await context.new_page()

    async def cancelled_download(download: Download) -> None:
        await download.cancel()
        e.blocked += 1

    e.page.on("download", cancelled_download)
    e.url = f"http://127.0.0.1:{server.server_port}/fixture"
    await context.add_cookies([{"name": "fixture_private", "value": "NO_HTTP_AMBIENT_COOKIE", "url": e.url}])
    await e.page.goto(e.url)
    e.config = {
        "allow_download": enabled if not no_config else False,
        "record": await e.page.locator('[data-record-id="result-case"]').element_handle(),
        "control": await e.page.locator("button[data-result]").element_handle(),
        "record_id": "result-case",
    }
    e.owner = await DownloadOwner.create(e.page, e.config, approval)
    try:
        yield e
        last = e.owner.receipt()
        rendered = json.dumps([last, e.owner.state()])
        for marker in (
            str(e.owner.area),
            str(e.owner.quarantine),
            CONTENT.decode(),
            "UNTRUSTED_NAME",
            "PRIVATE_RESULT",
            "http:",
            e.url,
            "/result",
            "<html",
            "Error:",
            "q_",
        ):
            assert marker not in rendered, (name, marker)
        stats = e.owner.stats
        assert stats["readBytes"] <= 65537
        assert stats["writtenBytes"] <= 65536
        assert stats["peakFileBytes"] <= 65536
        assert len(e.requests) <= 1
        for req in e.requests:
            assert "path" in req and "method" in req and "headers" in req
            assert req["path"] == "/result" and req["method"] == "GET", req
            assert not {"cookie", "authorization", "proxy-authorization"}.intersection(req["headers"]), req
        CHECKS.append(
            {
                "name": name,
                "mode": mode,
                "stats": stats,
                "fixtureRequests": len(e.requests),
                "fixtureBytesWritten": sum(e.deliveries),
                "quarantineFiles": len(files(e)),
                "lastCallReceipt": last,
                "blocked": e.blocked,
            }
        )
    finally:
        e.release.set()
        await e.owner.stop()
        assert e.owner.state()["cleanup"] == "completed"
        await context.close()
        await asyncio.to_thread(server.shutdown)
        server.server_close()
        thread.join(timeout=1)
        assert not e.owner.area.exists()


async def cleanup_retry_exercise(browser: Browser) -> None:
    async with scenario(browser, "unlink-failure-settles-Stop-without-claiming-cleanup", "wrong-digest") as e:
        permitted = e.issue()
        original_unlink = Path.unlink

        def refuse_partial(path: Path, missing_ok: bool = False) -> None:
            if path.parent == e.owner.quarantine:
                raise PermissionError("PRIVATE_PARTIAL_PATH")
            original_unlink(path, missing_ok=missing_ok)

        with (
            patch.object(Path, "unlink", refuse_partial),
            patch("file_download.shutil.rmtree", side_effect=OSError("PRIVATE_REMOVAL_PATH")),
        ):
            call = Call(e.owner, permitted)
            await call.cancelled()
            assert e.owner.work is None and len(files(e)) == 1
            assert e.owner.state()["current"] == {"status": "unknown", "effect": "unknown"}
            assert e.owner.state()["cleanup"] == "pending"
            assert "PRIVATE_PARTIAL_PATH" not in json.dumps(e.owner.state())
            try:
                await asyncio.wait_for(e.owner.stop(), 2)
            except OSError:
                pass
            else:
                raise AssertionError("failed removal must not report successful Stop")
        assert e.owner.state()["cleanup"] == "pending" and e.owner.area.exists()
        assert json.loads(await e.owner.download({"grant_id": permitted["grant_id"]})) == refusal()
        await asyncio.wait_for(e.owner.stop(), 2)
        assert e.owner.state()["cleanup"] == "completed" and not e.owner.area.exists()
        assert e.owner.stats["requests"] == 1


async def exercise(browser: Browser) -> None:
    async with scenario(browser, "positive+tampered filenames+copied config", "positive") as e:
        expected: dict[str, object] = {
            "url": e.url.removesuffix("/fixture") + "/result",
            "count": len(CONTENT),
            "sha256": digest(CONTENT),
        }
        grant = e.owner.issue(expected, milliseconds() + 15000)
        expected.update(url="http://127.0.0.1:1/changed", count=0, sha256="0" * 64)
        grant["label"] = "../../UNTRUSTED_NAME"
        e.config.update(allow_download=False, port=1)
        await completed(e, grant)
        first = e.owner.receipt()
        assert json.loads(await e.owner.download({"grant_id": grant["grant_id"]})) == refusal()
        assert first["completed"]
        denied_issue(e)
        assert e.owner.stats["requests"] == 1

    async with scenario(browser, "absent config denies", "positive", no_config=True) as e:
        denied_issue(e)
        nothing(e)
    async with scenario(browser, "denied config cannot be enabled later", "positive", enabled=False) as e:
        e.config["allow_download"] = True
        denied_issue(e)
        nothing(e)

    responses: tuple[tuple[object, str], ...] = (
        (False, "false"),
        (None, "null"),
        (0, "0"),
        (1, "1"),
        ("true", "true"),
        ({}, "[object Object]"),
        ([], ""),
    )
    for value, js in responses:

        async def approval(_: Mapping[str, object], response: object = value) -> object:
            return response

        async with scenario(browser, "strict-approval-" + js, "positive", approval=approval) as e:
            await refused(e, e.issue())

    arguments: tuple[dict[str, object], ...] = (
        {"grant_id": "other"},
        {"grant_id": "other", "path": "/tmp/PRIVATE_RESULT"},
        {"grant_id": "other", "url": "http://127.0.0.1/result"},
        {"grant_id": "other", "headers": {"authorization": "PRIVATE"}},
        {"grant_id": "other", "name": "UNTRUSTED_NAME"},
    )
    for original in arguments:
        async with scenario(browser, "model-args-" + "-".join(original), "positive") as e:
            grant = e.issue()
            args = original if len(original) == 1 else {**original, "grant_id": grant["grant_id"]}
            await refused(e, grant, args)

    for mode in (
        "positive",
        "chunked",
        "redirect",
        "huge-headers",
        "html",
        "encoded",
        "short-length",
        "long-length",
        "oversized",
        "wrong-digest",
    ):
        async with scenario(browser, "native-" + mode, mode) as e:
            grant = e.issue()
            if mode in ("positive", "chunked"):
                await completed(e, grant)
            else:
                await Call(e.owner, grant).done(e.owner, "unknown")
                await retired(e, grant)

    for mutation in (
        "control",
        "disabled",
        "record",
        "document",
        "session",
        "expired",
        "stop",
    ):
        seen, pending = asyncio.Event(), asyncio.Event()

        async def held(
            metadata: Mapping[str, object],
            seen: asyncio.Event = seen,
            pending: asyncio.Event = pending,
        ) -> bool:
            assert sorted(metadata) == ["count", "label", "sha256"]
            seen.set()
            await pending.wait()
            return True

        async with scenario(browser, "held-approval-" + mutation, "positive", approval=held) as e:
            expires = milliseconds() + (500 if mutation == "expired" else 15000)
            grant = e.issue(expires)
            call = Call(e.owner, grant)
            await seen.wait()
            nothing(e)
            stopping = None
            if mutation == "control":
                await e.page.locator("button").evaluate("el=>el.replaceWith(el.cloneNode(true))")
            if mutation == "disabled":
                await e.owner.control.evaluate("el=>{el.disabled=true}")
            if mutation == "record":
                await e.page.locator("section").evaluate("el=>el.replaceWith(el.cloneNode(true))")
            if mutation == "document":
                await e.page.reload()
            if mutation == "session":
                e.owner.change_session()
            if mutation == "expired":
                await asyncio.sleep(max(0, expires - milliseconds() + 5) / 1000)
            if mutation == "stop":
                stopping = asyncio.create_task(e.owner.stop())
                try:
                    await asyncio.wait_for(asyncio.shield(stopping), 2)
                    assert e.owner.state()["cleanup"] == "completed"
                finally:
                    pending.set()
            pending.set()
            if stopping:
                await call.cancelled()
                await stopping
                assert e.owner.state()["current"] == {"status": "interrupted", "effect": "none"}
            else:
                await call.done(e.owner, "refused")
            nothing(e)

    for mode in (
        "truncate",
        "lost-final-chunk",
        "held-body",
        "held-headers",
        "slow-body",
        "slow-headers",
    ):
        for mutation in ("stop", "control", "document", "session", "expired") if mode.startswith("held") else ("end",):
            async with scenario(browser, mode + "-" + mutation, mode) as e:
                expires = milliseconds() + (
                    650 if mutation == "expired" else 1500 if mode.startswith("slow") else 15000
                )
                grant = e.issue(expires)
                call = Call(e.owner, grant)
                await wait_for(e.entered.is_set)
                if "body" in mode or mode in ("truncate", "lost-final-chunk"):
                    await wait_for(lambda: e.owner.stats["peakFileBytes"] >= 8192)
                    paths = files(e)
                    assert len(paths) == 1 and 8192 <= paths[0].stat().st_size <= 65536
                if mutation == "stop":
                    stopping = asyncio.create_task(e.owner.stop())
                    await asyncio.sleep(0)
                    assert json.loads(await e.owner.download({"grant_id": grant["grant_id"]})) == refusal()
                    await asyncio.wait_for(stopping, 3)
                    e.release.set()
                    await call.cancelled()
                    assert e.owner.state()["current"] == {"status": "interrupted", "effect": "unknown"}
                    exposed = e.owner.state()
                    current = exposed["current"]
                    assert current is not None
                    current["effect"] = "completed"
                    exposed["recent"].clear()
                    read = Call(e.owner, grant, read_state=True)
                    await read.task
                    history = read.bodies[1].get("input")
                    assert history is not None and not isinstance(history, str)
                    pair = next(item for item in history if item.get("type") == "function_call_output")
                    assert pair.get("type") == "function_call_output"
                    output = pair.get("output")
                    assert isinstance(output, str)
                    assert json.loads(output) == e.owner.state()
                    assert e.owner.state()["current"] == {"status": "interrupted", "effect": "unknown"}
                    assert e.owner.state()["cleanup"] == "completed"
                else:
                    if mutation == "control":
                        await e.owner.control.evaluate("el=>{el.disabled=true}")
                    if mutation == "document":
                        await e.page.reload()
                    if mutation == "session":
                        e.owner.change_session()
                    if mutation == "expired":
                        await asyncio.sleep(max(0, expires - milliseconds() + 5) / 1000)
                    if not mode.startswith("slow") and mutation != "expired":
                        e.release.set()
                    await call.done(e.owner, "unknown")
                await retired(e, grant)

    async with scenario(browser, "browser-download-remains-blocked", "positive", enabled=False) as e:
        await e.page.evaluate("""()=>{
          const a=document.createElement('a');a.href='/unsolicited';a.download='UNTRUSTED_NAME';
          document.body.append(a);a.click();
        }""")
        await wait_for(lambda: e.blocked == 1)
        await refused(e, {"grant_id": "browser-download-is-not-a-grant"})

    # Independent Node getter finding: detached diagnostics cannot grant a second GET.
    async with scenario(
        browser,
        "reading/resetting diagnostic count cannot reauthorize an exhausted owner",
        "positive",
    ) as e:
        grant = e.issue()
        await completed(e, grant)
        exposed = e.owner.stats
        exposed.update(requests=0, readBytes=0, writtenBytes=0, peakFileBytes=0)
        denied_issue(e)
        assert e.owner.stats["requests"] == len(e.requests) == len(files(e)) == 1

    # Python Task ownership: Stop completes before the caller's unrelated continuation.
    async with scenario(browser, "python-operation-drain-not-entire-caller", "positive") as e:
        grant = e.issue()
        proceeded, release_caller = asyncio.Event(), asyncio.Event()

        async def longer_caller() -> None:
            try:
                result = await e.owner.download({"grant_id": grant["grant_id"]})
                assert json.loads(result)["status"] == "completed"
            finally:
                await e.owner.stop()
            proceeded.set()
            await release_caller.wait()

        task = asyncio.create_task(longer_caller())
        await asyncio.wait_for(proceeded.wait(), 3)
        assert not task.done() and not e.owner.area.exists()
        release_caller.set()
        await task

    seen = asyncio.Event()

    async def cancelled_approval(_: Mapping[str, object]) -> bool:
        seen.set()
        await asyncio.Event().wait()
        return False

    async with scenario(
        browser,
        "python-cancel-before-admission",
        "positive",
        approval=cancelled_approval,
    ) as e:
        grant = e.issue()
        call = Call(e.owner, grant)
        await asyncio.wait_for(seen.wait(), 2)
        call.task.cancel()
        await call.cancelled(original=True)
        assert e.owner.receipt() == refusal()
        nothing(e)
        denied_issue(e)

    async with scenario(browser, "python-cancel-after-admission", "held-body") as e:
        grant = e.issue()
        call = Call(e.owner, grant)
        await wait_for(lambda: e.owner.stats["peakFileBytes"] >= 8192)
        call.task.cancel()
        await call.cancelled(original=True)
        await retired(e, grant)

    await cleanup_retry_exercise(browser)

    # Setup cancellation cannot retain its just-created private directory.
    async with scenario(browser, "python-setup-cancelled", "positive") as e:
        before = set(Path(tempfile.gettempdir()).glob("openai-file-download-*"))
        original = e.page.evaluate_handle
        started = asyncio.Event()

        async def pause(expression: str, arg: object = None) -> JSHandle:
            started.set()
            await asyncio.Event().wait()
            return await original(expression, arg=arg)

        e.page.evaluate_handle = pause
        task = asyncio.create_task(DownloadOwner.create(e.page, e.config, approve))
        await started.wait()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        else:
            raise AssertionError("setup swallowed cancellation")
        finally:
            e.page.evaluate_handle = original
        assert set(Path(tempfile.gettempdir()).glob("openai-file-download-*")) == before
        nothing(e)


async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            chromium_sandbox=True,
            env={
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
                "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
            },
        )
        try:
            if "--cleanup-retry" in sys.argv:
                await cleanup_retry_exercise(browser)
            else:
                await exercise(browser)
            print(
                json.dumps(
                    {
                        "phase": "result",
                        "checks": CHECKS,
                        "apiRequests": 0,
                        "chromium": browser.version,
                        "limits": "Application raw bytes <=65537, owned-file writes <=65536. "
                        "HTTPX parser/socket/kernel buffering is excluded; no browser/OS hard-cap proof.",
                    }
                ),
                flush=True,
            )
        finally:
            await browser.close()


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
