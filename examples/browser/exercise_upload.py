"""Local upload cases through AsyncResponsesToolRunner."""

from __future__ import annotations

import os
import sys
import json
import asyncio
import tempfile
from pathlib import Path
from datetime import timedelta
from threading import Thread
from contextlib import asynccontextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from collections.abc import Mapping, Callable, Sequence, Awaitable, AsyncGenerator
from typing_extensions import override

import httpx2
from file_upload import UploadOwner, digest, no_hook, refusal, unknown, milliseconds
from playwright.async_api import Page, Route, Browser, Download, FilePayload, BrowserContext, async_playwright

from openai import AsyncOpenAI
from openai.types.responses import Response, FunctionToolParam
from openai.lib.responses_tool_runner import (
    AsyncRegisteredFunction,
    AsyncResponsesToolRunner,
)
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

ORIGINAL = b"PRIVATE_SYNTHETIC_DOCUMENT_only_fixture_16\n"
REPLACED = b"REPLACED_DO_NOT_SUBSTITUTE\n"
ENDPOINTS: list[dict[str, object]] = []
CHECKS: list[dict[str, object]] = []
REQUESTS: list[Call] = []
RULE: FunctionToolParam = {
    "type": "function",
    "name": "upload",
    "description": "Upload the approved fixture document.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {"grant_id": {"type": "string"}},
        "required": ["grant_id"],
        "additionalProperties": False,
    },
}


def receipt(content: bytes | bytearray) -> dict[str, object]:
    return {"count": len(content), "sha256": digest(content)}


async def approve(_: Mapping[str, object]) -> bool:
    return True


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.path == "/fixture":
            body = Path(__file__).with_name("file-upload.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif self.path == "/unsolicited":
            body = ORIGINAL
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header(
                "Content-Disposition",
                'attachment; filename="../../SUGGESTED_PRIVATE_FILE"',
            )
        else:
            self.send_error(404)
            return
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/uploaded":
            self.send_error(404)
            return
        count = int(self.headers["Content-Length"])
        data = self.rfile.read(count)
        ENDPOINTS.append(receipt(data))
        body = b"Received"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def source(owner: UploadOwner, content: bytes = ORIGINAL) -> str:
    name = owner.generated_name()
    fd = os.open(owner.upload_root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, content)
    finally:
        os.close(fd)
    return name


async def grant(owner: UploadOwner, name: str, expires: int | None = None) -> dict[str, str]:
    return await owner.prepare(owner.upload_root, name, milliseconds() + 20000 if expires is None else expires)


async def failure(awaitable: Awaitable[object], expected: str = "File preparation refused.") -> None:
    try:
        await awaitable
    except ValueError as exc:
        assert str(exc) == expected
        assert exc.__context__ is None or exc.__suppress_context__
        return
    raise AssertionError("expected refusal")


async def endpoint(page: Page, expected: bytes = ORIGINAL) -> None:
    await page.wait_for_function("document.querySelector('#result')?.textContent === 'Received'", timeout=2500)
    assert ENDPOINTS[-1] == receipt(expected)


def no_transfer(check: Check) -> None:
    assert not check.deliveries, check.deliveries
    assert len(ENDPOINTS) == check.start, ENDPOINTS[check.start :]


class Call:
    def __init__(
        self,
        owner: UploadOwner,
        supplied: Mapping[str, str],
        args: dict[str, object] | None = None,
        *,
        read_state: bool = False,
    ) -> None:
        self.bodies: list[ResponseCreateParamsNonStreaming] = []
        self.args = {"grant_id": supplied["grant_id"]} if args is None else args

        async def transport(request: httpx2.Request) -> httpx2.Response:
            self.bodies.append(json.loads(request.content))
            assert len(self.bodies) <= 2, "ordinary function must not replay"
            if len(self.bodies) == 1:
                output: list[dict[str, object]] = [
                    {
                        "id": "fc_fixture",
                        "type": "function_call",
                        "name": "file_status" if read_state else "upload",
                        "call_id": "transfer-one",
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
                AsyncRegisteredFunction(RULE, owner.upload),
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

        async def execute() -> Response | BaseException:
            try:
                return await runner.run(
                    self.client,
                    {
                        "model": "",
                        "input": "Use the approved document.",
                        "store": False,
                    },
                    max_steps=3,
                    # This status read is a separate, explicitly authorized run after Stop.
                    cancelled=None if read_state else lambda: owner.stopped,
                )
            except BaseException as exc:
                return exc
            finally:
                await self.client.close()

        self.task = asyncio.create_task(execute())
        REQUESTS.append(self)

    async def result(self, error: bool = False) -> Response | BaseException:
        outcome = await self.task
        if error:
            assert isinstance(outcome, BaseException), outcome
        else:
            assert not isinstance(outcome, BaseException), outcome
        return outcome

    def output(self) -> dict[str, object]:
        history = self.bodies[1].get("input")
        assert history is not None and not isinstance(history, str)
        pair = next(item for item in history if item.get("type") == "function_call_output")
        assert pair.get("type") == "function_call_output"
        output = pair.get("output")
        assert isinstance(output, str)
        return json.loads(output)


class Check:
    context: BrowserContext
    page: Page
    owner: UploadOwner
    start: int
    blocked: int
    deliveries: list[dict[str, object]]
    first: dict[str, object] | None
    method: Callable[..., Awaitable[None]]
    fault: Callable[..., Awaitable[None]]


@asynccontextmanager
async def scenario(
    browser: Browser,
    url: str,
    name: str,
    config: dict[str, object] | None,
    confirm: Callable[[Mapping[str, object]], Awaitable[object]] = approve,
    after_stat: Callable[[], Awaitable[None]] = no_hook,
) -> AsyncGenerator[Check, None]:
    check = Check()
    check.context = await browser.new_context(
        viewport={"width": 1024, "height": 720},
        service_workers="block",
        accept_downloads=False,
    )
    allowed = {
        url,
        url.replace("/fixture", "/uploaded"),
        url.replace("/fixture", "/unsolicited"),
    }

    async def guard(route: Route) -> None:
        if route.request.url in allowed:
            await route.continue_()
        else:
            await route.abort()

    await check.context.route("**/*", guard)
    check.page = await check.context.new_page()
    check.blocked = 0

    async def cancel(download: Download) -> None:
        await download.cancel()
        check.blocked += 1

    check.page.on("download", cancel)
    await check.page.goto(url)
    check.owner = await UploadOwner.create(
        check.page,
        {
            **(config or {}),
            "record": await check.page.locator('[data-record-id="transfer-case"]').element_handle(),
            "control": await check.page.locator("input[type=file]").element_handle(),
            "record_id": "transfer-case",
        },
        confirm,
        after_stat,
    )
    check.start = len(ENDPOINTS)
    check.deliveries = []
    check.method = check.owner.control.set_input_files
    check.fault = check.method
    check.first = None

    async def intercept(
        files: str | Path | FilePayload | Sequence[str | Path] | Sequence[FilePayload],
        *,
        timeout: float | timedelta | None = None,
        no_wait_after: bool | None = None,
    ) -> None:
        assert isinstance(files, dict), "owner must dispatch a bounded native buffer"
        payload = files
        check.deliveries.append(receipt(payload["buffer"]))
        return await check.fault(payload, timeout=timeout, no_wait_after=no_wait_after)

    check.owner.control.set_input_files = intercept
    try:
        yield check
        rendered = json.dumps([check.owner.receipt(), check.owner.state()])
        for secret in (
            str(check.owner.area),
            "approved.bin",
            "f_",
            ORIGINAL.decode(),
            REPLACED.decode(),
            "SUGGESTED_PRIVATE_FILE",
            "file:",
            "http:",
            "Error",
            "input[type=file]",
        ):
            assert secret not in rendered, (name, secret)
        CHECKS.append(
            {
                "name": name,
                "first_delivery": list(check.deliveries),
                "endpoint": ENDPOINTS[check.start :],
                "earlier_receipt": check.first,
                "last_call_receipt": check.owner.receipt(),
                "blocked": check.blocked,
            }
        )
        print(json.dumps({"case": name, "passed": True}), flush=True)
    finally:
        await check.owner.stop()
        assert check.owner.state()["cleanup"] == "completed"
        await check.context.close()
        assert not check.owner.area.exists(), "owned staging must be removed"


async def accepted(check: Check, supplied: Mapping[str, str]) -> None:
    call = Call(check.owner, supplied)
    await call.result()
    await endpoint(check.page)
    assert len(call.bodies) == 2
    check.first = call.output()
    assert check.first == {
        "status": "completed",
        "attempted": True,
        "completed": True,
        **receipt(ORIGINAL),
    }
    assert check.deliveries == [receipt(ORIGINAL)]
    assert check.owner.state()["current"] == {"status": "completed", "effect": "completed"}
    assert check.owner.state()["cleanup"] == "not_started"


async def denied(check: Check, supplied: Mapping[str, str], args: dict[str, object] | None = None) -> None:
    call = Call(check.owner, supplied, args)
    await call.result()
    assert check.owner.receipt() == refusal()
    assert call.output() == refusal()
    no_transfer(check)


async def cancellation_poll_exercises(browser: Browser, url: str) -> None:
    allowed: dict[str, object] = {"allow_upload": True}
    for phase in ("before-admission", "after-admission"):
        async with scenario(browser, url, "throwing cancellation poll " + phase, allowed) as c:
            g = await grant(c.owner, source(c.owner))
            assert c.owner.grant is not None
            staging = c.owner.grant["buffer"]
            delivered = asyncio.Event()

            async def deliver(
                files: str | Path | FilePayload | Sequence[str | Path] | Sequence[FilePayload],
                *,
                timeout: float | timedelta | None = None,
                no_wait_after: bool | None = None,
                completed: asyncio.Event = delivered,
            ) -> None:
                await c.method(files, timeout=timeout, no_wait_after=no_wait_after)
                await endpoint(c.page)
                completed.set()

            c.fault = deliver

            def broken_poll(phase: str = phase, completed: asyncio.Event = delivered) -> bool:
                if phase == "before-admission" or completed.is_set():
                    raise RuntimeError("Synthetic cancellation poll failure.")
                return False

            if phase == "before-admission":
                try:
                    await c.owner.upload_file({"grant_id": g["grant_id"]}, cancelled=broken_poll)
                except RuntimeError as error:
                    assert str(error) == "Synthetic cancellation poll failure."
                else:
                    raise AssertionError("The failed cancellation predicate must propagate.")
                no_transfer(c)
            else:
                result = await c.owner.upload_file({"grant_id": g["grant_id"]}, cancelled=broken_poll)
                assert result["status"] == "interrupted" and result["effect"] == "unknown", result
                assert delivered.is_set()
                assert c.deliveries == [receipt(ORIGINAL)]
                assert staging == bytearray(len(staging))
            assert c.owner.state()["current"] == {
                "status": "interrupted",
                "effect": "none" if phase == "before-admission" else "unknown",
            }
            assert c.owner.work is None
            await asyncio.wait_for(c.owner.stop(), 2)
            assert not c.owner.area.exists() and staging == bytearray(len(staging))


async def exercises(browser: Browser, url: str) -> None:
    allowed: dict[str, object] = {"allow_upload": True}
    config: dict[str, object] = {"allow_upload": True}
    async with scenario(
        browser,
        url,
        "positive, detached label, copied allow and no grant reuse",
        config,
    ) as c:
        config["allow_upload"] = False
        g = await grant(c.owner, source(c.owner))
        g["label"] = "../../SUGGESTED_PRIVATE_FILE\0"
        await accepted(c, g)
        assert json.loads(await c.owner.upload({"grant_id": g["grant_id"]})) == refusal()
        assert len(c.deliveries) == 1
    config = {"allow_upload": False}
    async with scenario(browser, url, "copied denial cannot acquire permission later", config) as c:
        config["allow_upload"] = True
        await failure(grant(c.owner, source(c.owner)))
        no_transfer(c)
    await cancellation_poll_exercises(browser, url)
    async with scenario(browser, url, "default configuration denies all", None) as c:
        await failure(grant(c.owner, source(c.owner)))
        no_transfer(c)
    for name in [
        "../outside",
        "/tmp/PRIVATE",
        r"\\remote\share",
        "file:///tmp/P",
        "https://host/P",
        "..",
        "x/y",
        "f_" + "0" * 24 + "\0",
        "CON",
        "f_" + "0" * 3000,
        42,
    ]:
        async with scenario(browser, url, "lexical_" + str(len(CHECKS)), allowed) as c:
            await failure(c.owner.prepare(c.owner.upload_root, name, milliseconds() + 20000))
            no_transfer(c)
    for case in (
        "outside-root",
        "quarantine-root",
        "symlink-file",
        "symlink-root",
        "directory",
        "fifo",
        "oversized",
        "expiry-in-past",
    ):
        async with scenario(browser, url, case, allowed) as c:
            owner = c.owner
            name = owner.generated_name()
            root = owner.upload_root
            expiry = milliseconds() + 20000
            target = root / name
            if case == "outside-root":
                root = owner.area
            elif case == "quarantine-root":
                root = owner.quarantine
            elif case == "symlink-file":
                target.symlink_to(owner.upload_root / source(owner))
            elif case == "symlink-root":
                saved = owner.area / "saved"
                root.rename(saved)
                root.symlink_to(saved)
                target.write_bytes(ORIGINAL)
            elif case == "directory":
                target.mkdir()
            elif case == "fifo":
                os.mkfifo(target, 0o600)
            elif case == "oversized":
                target.write_bytes(b"\0" * 65537)
            elif case == "expiry-in-past":
                target.write_bytes(ORIGINAL)
                expiry = milliseconds() - 1
            await failure(owner.prepare(root, name, expiry))
            no_transfer(c)
    growing: Path | None = None

    async def grow() -> None:
        assert growing is not None
        with growing.open("ab") as f:
            f.write(b"\0" * 65536)

    async with scenario(
        browser,
        url,
        "file grows after fstat; bounded read detects overflow",
        allowed,
        after_stat=grow,
    ) as c:
        name = source(c.owner)
        growing = c.owner.upload_root / name
        await failure(grant(c.owner, name))
        no_transfer(c)
    decisions: tuple[object, ...] = (False, None, "true", 1, {}, [])
    for decision in decisions:

        async def decision_only(_: Mapping[str, object], decision: object = decision) -> object:
            return decision

        async with scenario(browser, url, "strict approval_" + str(len(CHECKS)), allowed, decision_only) as c:
            await denied(c, await grant(c.owner, source(c.owner)))

    for action in (
        "replace-source",
        "replace-control",
        "replace-record",
        "changed-record",
        "new-document",
        "new-session",
        "expiry-held",
        "cancel-held",
        "extra-model-args",
    ):
        seen, approval = asyncio.Event(), asyncio.Event()

        async def held(
            snapshot: Mapping[str, object],
            seen: asyncio.Event = seen,
            approval: asyncio.Event = approval,
        ) -> bool:
            assert set(snapshot) == {"count", "label", "sha256"}
            seen.set()
            await approval.wait()
            return True

        async with scenario(browser, url, action, allowed, held) as c:
            name = source(c.owner)
            expiry = milliseconds() + 1500 if action == "expiry-held" else milliseconds() + 20000
            g = await grant(c.owner, name, expiry)
            if action == "extra-model-args":
                await denied(c, g, {"grant_id": g["grant_id"], "path": "/tmp/PRIVATE"})
                continue
            call = Call(c.owner, g)
            await asyncio.wait_for(seen.wait(), 3)
            no_transfer(c)
            stopping = None
            if action == "replace-source":
                (c.owner.upload_root / name).rename(c.owner.area / "old")
                (c.owner.upload_root / name).write_bytes(REPLACED)
            elif action == "replace-control":
                await c.page.evaluate(
                    "() => {const el=document.querySelector('input');el.replaceWith(el.cloneNode(true))}"
                )
            elif action == "replace-record":
                await c.page.evaluate(
                    "() => {const el=document.querySelector('section');el.replaceWith(el.cloneNode(true))}"
                )
            elif action == "changed-record":
                await c.page.evaluate("document.querySelector('section').dataset.recordId='other'")
            elif action == "new-document":
                await c.page.reload()
            elif action == "new-session":
                c.owner.change_session()
            elif action == "expiry-held":
                await asyncio.sleep(max(0, (expiry - milliseconds() + 20) / 1000))
            elif action == "cancel-held":
                stopping = asyncio.create_task(c.owner.stop())
                try:
                    await asyncio.wait_for(asyncio.shield(stopping), 2)
                    assert not c.owner.area.exists()
                finally:
                    approval.set()
            approval.set()
            await call.result(error=stopping is not None)
            if stopping:
                await stopping
            if action == "replace-source":
                await endpoint(c.page)
                assert c.deliveries == [receipt(ORIGINAL)]
            else:
                no_transfer(c)
    for action in (
        "lost-before-native",
        "lost-after-native",
        "cancel-before-native",
        "cancel-after-native",
        "replace-control-before-native",
        "replace-control-after-native",
    ):
        async with scenario(browser, url, action, allowed) as c:
            entered, release = asyncio.Event(), asyncio.Event()

            async def fault(
                files: str | Path | FilePayload | Sequence[str | Path] | Sequence[FilePayload],
                *,
                timeout: float | timedelta | None = None,
                no_wait_after: bool | None = None,
                action: str = action,
                entered: asyncio.Event = entered,
                release: asyncio.Event = release,
            ) -> None:
                assert isinstance(files, dict), "owner must dispatch a bounded native buffer"
                payload = files
                if action.endswith("after-native"):
                    await c.method(payload, timeout=timeout, no_wait_after=no_wait_after)
                    await endpoint(c.page)
                entered.set()
                await release.wait()
                if action.startswith("lost"):
                    raise RuntimeError("PRIVATE_PLAYWRIGHT_PATH")
                if action.endswith("before-native"):
                    await c.method(payload, timeout=timeout, no_wait_after=no_wait_after)

            c.fault = fault
            g = await grant(c.owner, source(c.owner))
            call = Call(c.owner, g)
            await asyncio.wait_for(entered.wait(), 3)
            assert len(c.deliveries) == 1
            assert c.owner.state()["current"] == {"status": "in_progress", "effect": "unknown"}
            stopping = None
            if action.startswith("cancel"):
                stopping = asyncio.create_task(c.owner.stop())
                await asyncio.sleep(0)
                assert not stopping.done() and c.owner.area.exists()
                assert c.owner.state()["cleanup"] == "pending"
                for _ in range(35):
                    assert json.loads(await c.owner.upload({"grant_id": g["grant_id"]})) == refusal()
                assert c.owner.state()["current"] == {"status": "in_progress", "effect": "unknown"}
                assert c.owner.state()["earlier_omitted"] and len(c.owner.state()["recent"]) == 32
            if action.startswith("replace-control"):
                await c.page.evaluate(
                    "() => {const el=document.querySelector('input');el.replaceWith(el.cloneNode(true))}"
                )
            release.set()
            await call.result(error=stopping is not None)
            if stopping:
                await stopping
            assert c.owner.receipt() == unknown()
            assert c.owner.state()["current"] == {
                "status": "interrupted" if stopping else "unknown",
                "effect": "unknown",
            }
            if stopping:
                exposed = c.owner.state()
                current = exposed["current"]
                assert current is not None
                current["status"] = "completed"
                exposed["recent"].clear()
                read = Call(c.owner, g, read_state=True)
                await read.result()
                assert read.output() == c.owner.state()
                assert c.owner.state()["current"] == {"status": "interrupted", "effect": "unknown"}
                assert c.owner.state()["cleanup"] == "completed"
            assert json.loads(await c.owner.upload({"grant_id": g["grant_id"]})) == refusal()
            assert len(c.deliveries) == 1
            if action == "lost-before-native":
                assert len(ENDPOINTS) == c.start
            elif action == "replace-control-before-native":
                received = ENDPOINTS[c.start :]
                assert len(received) <= 1
                if received:
                    assert received[0] == receipt(ORIGINAL)
                assert await c.page.locator("input").evaluate("e=>e.files.length") == 0
            else:
                await endpoint(c.page)
                assert len(ENDPOINTS) == c.start + 1
    async with scenario(browser, url, "unsolicited download cancelled; no automatic grant", allowed) as c:
        await c.page.evaluate("""() => {
          const a=document.createElement('a');a.href='/unsolicited';a.download='SUGGESTED_PRIVATE_FILE';
          document.body.append(a);a.click()
        }""")
        for _ in range(100):
            if c.blocked:
                break
            await asyncio.sleep(0.02)
        assert c.blocked == 1
        await denied(c, {"grant_id": "untrusted-download"})
    assert len(CHECKS) == 47

    # Reproduce the original review's three additional failure boundaries.
    seen, release = asyncio.Event(), asyncio.Event()

    async def held_stat() -> None:
        seen.set()
        await release.wait()

    async with scenario(
        browser,
        url,
        "stop-during-prepare-drains-open-descriptor",
        allowed,
        after_stat=held_stat,
    ) as c:
        preparation = asyncio.create_task(grant(c.owner, source(c.owner)))
        await asyncio.wait_for(seen.wait(), 3)
        stopping = asyncio.create_task(c.owner.stop())
        await asyncio.sleep(0)
        assert not stopping.done() and c.owner.area.exists()
        # Both prepare and upload share the slot, so no later callback can enter.
        await failure(grant(c.owner, source(c.owner)))
        assert json.loads(await c.owner.upload({"grant_id": "never-issued"})) == refusal()
        no_transfer(c)
        release.set()
        await failure(preparation)
        await stopping
        call = Call(c.owner, {"grant_id": "never-issued"})
        await call.result(error=True)
        assert len(call.bodies) == 0
    async with scenario(browser, url, "native-assignment-then-type-change-is-unknown", allowed) as c:

        async def changed(
            files: str | Path | FilePayload | Sequence[str | Path] | Sequence[FilePayload],
            *,
            timeout: float | timedelta | None = None,
            no_wait_after: bool | None = None,
        ) -> None:
            assert isinstance(files, dict), "owner must dispatch a bounded native buffer"
            payload = files
            await c.method(payload, timeout=timeout, no_wait_after=no_wait_after)
            await endpoint(c.page)
            await c.page.locator("input").evaluate("el=>el.type='text'")

        c.fault = changed
        g = await grant(c.owner, source(c.owner))
        call = Call(c.owner, g)
        await call.result()
        assert c.owner.receipt() == unknown() == call.output()
        assert json.loads(await c.owner.upload({"grant_id": g["grant_id"]})) == refusal()
        assert c.deliveries == [receipt(ORIGINAL)] and ENDPOINTS[c.start :] == [receipt(ORIGINAL)]
    async with scenario(browser, url, "changed-type-before-approval-has-zero-transfer", allowed) as c:
        g = await grant(c.owner, source(c.owner))
        await c.page.locator("input").evaluate("el=>el.type='text'")
        await denied(c, g)
    original = set(Path(tempfile.gettempdir()).glob("openai-file-upload-*"))
    context = await browser.new_context()
    page = await context.new_page()
    await page.close()
    await failure(UploadOwner.create(page, allowed, approve), "File owner initialization refused.")
    assert set(Path(tempfile.gettempdir()).glob("openai-file-upload-*")) == original
    await context.close()
    CHECKS.append({"name": "closed-page-cleanup-after-area-creation", "passed": True})


async def main() -> None:
    fixture = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=fixture.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{fixture.server_port}/fixture"
    try:
        async with async_playwright() as engine:
            browser = await engine.chromium.launch(
                headless=True,
                chromium_sandbox=True,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "HOME": os.environ.get("HOME", ""),
                    "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
                },
            )
            try:
                if "--cancellation-polls" in sys.argv:
                    await cancellation_poll_exercises(browser, url)
                    assert len(CHECKS) == 2
                else:
                    await exercises(browser, url)
                    assert len(CHECKS) == 51
                assert all(len(call.bodies) <= 2 for call in REQUESTS)
                print(
                    json.dumps(
                        {
                            "checks": CHECKS,
                            "ordinary_sdk_requests": [len(call.bodies) for call in REQUESTS],
                            "api_requests": 0,
                            "runtime": {"chromium": browser.version},
                        }
                    ),
                    flush=True,
                )
            finally:
                await browser.close()
    finally:
        fixture.shutdown()
        fixture.server_close()
        thread.join()


def start() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    start()
