"""Only synthetic provider HTTP and task-owned local sandboxed Chromium."""

from __future__ import annotations

import json
import asyncio
import tempfile
from typing import Any, cast
from pathlib import Path
from importlib import util, metadata
from contextlib import asynccontextmanager
from unittest.mock import patch
from collections.abc import Callable, Awaitable
from typing_extensions import Unpack, TypedDict, NotRequired

from browser_driver import PlaywrightBrowser
from browser_use_session import (
    BrowserUseError,
    CleanupNotificationError,
    _Cleanup,
    with_standalone_browser,
)
from playwright.async_api import Browser, BrowserType, async_playwright

from openai.lib.browser import NewTabInput, AsyncBrowserToolset, BrowserConfirmContext
from openai.types.responses import ResponseFunctionToolCall
from openai.types.responses.response_input_param import FunctionCallOutput

TMP = Path(tempfile.gettempdir())
IDENTITY = "00000000-0000-4000-8000-000000000001"
FOREIGN = "00000000-0000-4000-8000-000000000002"
KEY = "SYNTHETIC_FIXTURE_KEY"
SECRET = "SYNTHETIC_PROVIDER_PRIVATE_VIEW"
PASSED: list[str] = []


class StartOptions(TypedDict):
    allowed_origins: NotRequired[list[str]]
    on_cleanup: NotRequired[Callable[[_Cleanup], object]]
    cancelled: NotRequired[Callable[[], bool]]


async def answer(
    writer: asyncio.StreamWriter, status: int, value: dict[str, object] | bytes, content_type: str = "application/json"
) -> None:
    data = json.dumps(value).encode() if content_type == "application/json" else cast(bytes, value)
    writer.write(
        f"HTTP/1.1 {status} Result\r\nContent-Type: {content_type}\r\n"
        f"Content-Length: {len(data)}\r\nConnection: close\r\n\r\n".encode()
        + data
    )
    await writer.drain()


class Gate:
    def __init__(self, phase: str = "") -> None:
        self.phase = phase
        self.entered = asyncio.Event()
        self.resume = asyncio.Event()

    async def at(self, phase: str) -> None:
        if phase == self.phase:
            self.entered.set()
            await self.resume.wait()


class Fixture:
    def __init__(self, endpoint: str, gate: Gate) -> None:
        self.endpoint, self.gate = endpoint, gate
        self.log: list[tuple[str, str, object]] = []
        self.mode = ""
        self.status = "active"
        self.page_hits = 0

    async def request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            head = await reader.readuntil(b"\r\n\r\n")
            lines = head.decode("ascii").split("\r\n")
            method, path, _ = lines[0].split()
            headers = dict(line.lower().split(": ", 1) for line in lines[1:] if ": " in line)
            body = await reader.readexactly(int(headers.get("content-length", "0")))
            if path == "/approved":
                self.page_hits += 1
                await answer(
                    writer,
                    200,
                    b"<title>Fixture</title><p>Approved fixture</p><button>Apply</button>",
                    "text/html",
                )
                return
            self.log.append((method, path, json.loads(body) if body else None))
            view: dict[str, object] = {
                "id": IDENTITY,
                "status": self.status,
                "cdpUrl": self.endpoint,
                "liveUrl": SECRET,
                "timeoutAt": "2026-10-10T10:00:00Z",
                "startedAt": "2026-10-10T09:00:00Z",
                "agentSessionId": None,
            }
            if method == "POST" and path == "/browsers":
                await self.gate.at("create")
                if self.mode in ("429", "uncertain"):
                    await answer(writer, 429 if self.mode == "429" else 500, {"detail": SECRET})
                    return
                await answer(writer, 200, view)
                return
            if path != "/browsers/" + IDENTITY:
                await answer(writer, 404, {"detail": SECRET})
                return
            if method == "GET":
                await self.gate.at("get")
                if self.mode == "wrong-id":
                    view["id"] = FOREIGN
                if self.mode == "attached":
                    view["agentSessionId"] = FOREIGN
                if self.mode == "missing-agent":
                    del view["agentSessionId"]
                if self.mode == "unavailable":
                    await answer(writer, 500, {"detail": SECRET})
                    return
                await answer(writer, 200, view)
                return
            if method == "PATCH":
                await self.gate.at("stop")
                if self.mode == "stop-failed":
                    await answer(writer, 500, {"detail": SECRET})
                    return
                assert json.loads(body) == {"action": "stop"}
                self.status = view["status"] = "stopped"
                await answer(writer, 200, view)
                return
            await answer(writer, 404, {"detail": SECRET})
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    def requests(self, method: str) -> list[tuple[str, str, object]]:
        return [r for r in self.log if r[0] == method]

    def paths(self) -> None:
        assert self.requests("POST") == [
            (
                "POST",
                "/browsers",
                {
                    "timeout": 1,
                    "proxyCountryCode": None,
                    "enableRecording": False,
                    "browserScreenWidth": 1024,
                    "browserScreenHeight": 768,
                    "allowResizing": False,
                },
            )
        ], self.log
        assert all(path == "/browsers/" + IDENTITY for method, path, _ in self.log if method != "POST")


def call(tools: AsyncBrowserToolset, member: str, args: dict[str, object]) -> ResponseFunctionToolCall:
    name = next(t["name"] for t in tools.tools if t["name"].endswith(member))
    return ResponseFunctionToolCall(
        type="function_call",
        id="fc1",
        call_id="call1",
        name=name,
        arguments=json.dumps(args),
        status="completed",
    )


async def cancelled(task: Awaitable[object]) -> None:
    try:
        await task
    except asyncio.CancelledError as error:
        assert SECRET not in str(error) and KEY not in str(error)
        return
    raise AssertionError("cancellation required")


async def failed(task: Awaitable[object], kind: type[BrowserUseError] = BrowserUseError) -> BrowserUseError:
    try:
        await task
    except kind as error:
        assert SECRET not in str(error) and KEY not in str(error)
        assert error.__cause__ is None and error.__suppress_context__
        return error
    raise AssertionError("failure required")


async def main() -> None:
    assert util.find_spec("browser_use") is None
    print(
        json.dumps(
            {
                "python": metadata.version("openai"),
                "provider": metadata.version("browser-use-sdk"),
                "playwright": metadata.version("playwright"),
                "engine_importable": False,
            }
        ),
        flush=True,
    )
    with tempfile.TemporaryDirectory(dir=TMP, prefix="chromium-") as profile:
        async with async_playwright() as pw:
            persistent = await pw.chromium.launch_persistent_context(
                profile,
                headless=True,
                chromium_sandbox=True,
                args=["--remote-debugging-port=0"],
                env={
                    "HOME": profile,
                    "TMPDIR": str(TMP),
                    "PATH": "/usr/bin:/bin",
                },
            )
            port = (Path(profile) / "DevToolsActivePort").read_text().splitlines()[0]
            endpoint = "http://127.0.0.1:" + port
            caller = await pw.chromium.connect_over_cdp(endpoint)
            sentinel = await caller.new_context()
            witness = await sentinel.new_page()
            await witness.set_content("<p>Caller must survive</p>")
            print(json.dumps({"browser": caller.version}), flush=True)

            @asynccontextmanager
            async def fixture(phase: str = ""):
                gate = Gate(phase)
                service = Fixture(endpoint, gate)
                server = await asyncio.start_server(service.request, "127.0.0.1", 0)
                origin = "http://127.0.0.1:" + str(server.sockets[0].getsockname()[1])
                receipts: list[_Cleanup] = []
                effects: list[str] = []

                class Chromium:
                    async def connect_over_cdp(self, endpoint_url: str, *, timeout: float) -> Browser:
                        browser = await pw.chromium.connect_over_cdp(endpoint_url, timeout=timeout)
                        effects.append("connect")
                        await gate.at("connect")
                        return browser

                def tools_for(
                    driver: PlaywrightBrowser, confirm: Callable[[BrowserConfirmContext], Awaitable[bool]] | None = None
                ) -> AsyncBrowserToolset:
                    async def yes(_: BrowserConfirmContext) -> bool:
                        return True

                    async def policy(_: BrowserConfirmContext, url: str) -> bool:
                        return url == origin + "/approved"

                    return AsyncBrowserToolset(driver, confirm=confirm or yes, url_policy=policy)

                async def real_work(driver: PlaywrightBrowser, is_stopped: Callable[[], bool]) -> str:
                    effects.append("work")
                    tools = tools_for(driver)
                    assert len(tools.tools) == 15
                    created = await tools.execute(
                        call(tools, "new_tab", {"url": origin + "/approved"}),
                        cancelled=is_stopped,
                    )
                    assert '"ok": false' not in json.dumps(created), created
                    tabs = (await driver.state())["tabs"]
                    assert len(tabs) == 1
                    text = await tools.execute(
                        call(tools, "get_page_text", {"tab_id": tabs[0]["id"]}),
                        cancelled=is_stopped,
                    )
                    assert "Approved fixture" in json.dumps(text), text
                    return "visited"

                def start(
                    work: Callable[[PlaywrightBrowser, Callable[[], bool]], Awaitable[object]] = real_work,
                    **options: Unpack[StartOptions],
                ):
                    return with_standalone_browser(
                        cast(BrowserType, Chromium()),
                        options.pop("allowed_origins", [origin]),
                        work,
                        api_key=KEY,
                        base_url=origin,
                        on_cleanup=options.pop("on_cleanup", receipts.append),
                        cancelled=options.get("cancelled", lambda: False),
                    )

                try:
                    yield service, gate, receipts, effects, origin, start, tools_for
                finally:
                    gate.resume.set()
                    server.close()
                    await server.wait_closed()

            async def run(label: str, test: Callable[[], Awaitable[None]]) -> None:
                await test()
                assert "Caller must survive" in await witness.locator("p").inner_text()
                PASSED.append(label)
                print(json.dumps({"name": label, "pass": True}), flush=True)

            try:

                async def happy() -> None:
                    async with fixture() as (
                        service,
                        _gate,
                        receipts,
                        effects,
                        _,
                        start,
                        _,
                    ):
                        result = await start()
                        assert result["result"] == "visited" and result["status"] == "complete"
                        assert receipts == [result["cleanup"]] and effects == [
                            "connect",
                            "work",
                        ]
                        assert service.page_hits == 1 and len(service.requests("PATCH")) == 1
                        service.paths()
                        old = list(service.log)
                        assert await receipts[0].retry() == {"status": "complete"} and service.log == old

                await run("real installed helper and standalone resource", happy)

                async def invalid_origins() -> None:
                    async with fixture() as (service, _gate, receipts, effects, origin, start, _):
                        for invalid in (
                            origin + "/",
                            origin + "/private",
                            origin + "?view=private",
                            origin + "#private",
                            "http://user:pass@127.0.0.1",
                            "file:///tmp/private",
                            "https://",
                        ):
                            error = await failed(start(allowed_origins=[origin, invalid]))
                            assert receipts[-1] is error.cleanup
                            assert await error.cleanup.retry() == {"status": "unverified"}
                            assert service.log == [] and effects == [] and service.page_hits == 0, invalid

                await run("invalid origins rejected before provider creation", invalid_origins)

                for mutate, initially_granted in (
                    (False, False),
                    (True, False),
                    (False, True),
                ):

                    async def origins(mutate: bool = mutate, initially_granted: bool = initially_granted) -> None:
                        async with fixture("create") as (
                            service,
                            gate,
                            receipts,
                            _,
                            origin,
                            start,
                            _,
                        ):
                            async with fixture() as (
                                target,
                                _,
                                _,
                                _,
                                target_origin,
                                _,
                                target_tools,
                            ):
                                allowed = [origin]
                                if initially_granted:
                                    allowed.append(target_origin)

                                async def work(driver: PlaywrightBrowser, is_stopped: Callable[[], bool]):
                                    tools = target_tools(driver)
                                    return await tools.execute(
                                        call(
                                            tools,
                                            "new_tab",
                                            {"url": target_origin + "/approved"},
                                        ),
                                        cancelled=is_stopped,
                                    )

                                task = asyncio.create_task(start(work, allowed_origins=allowed))
                                await asyncio.wait_for(gate.entered.wait(), 8)
                                if mutate:
                                    allowed.append(target_origin)
                                gate.resume.set()
                                result = await task
                                assert result["status"] == "complete" and len(receipts) == 1
                                tool_result = cast(FunctionCallOutput, result["result"])
                                content = tool_result["output"]
                                assert isinstance(content, list) and content[0]["type"] == "input_text"
                                output = json.loads(content[0]["text"])
                                assert output["ok"] is initially_granted, result["result"]
                                assert target.page_hits == int(initially_granted)
                                assert len(service.requests("PATCH")) == 1
                                service.paths()

                    await run(
                        f"origin grant at admission: later mutation={mutate}, initial grant={initially_granted}",
                        origins,
                    )

                for mode in ("429", "uncertain", "wrong-id", "attached", "missing-agent"):

                    async def denied(mode: str = mode) -> None:
                        async with fixture() as (
                            service,
                            _,
                            receipts,
                            effects,
                            _,
                            start,
                            _,
                        ):
                            service.mode = mode
                            error = await failed(start())
                            assert len(receipts) == 1 and receipts == [error.cleanup]
                            assert await receipts[0].retry() == {"status": "unverified"}
                            service.paths()
                            assert service.requests("PATCH") == [] and effects == []
                            if mode in ("429", "uncertain"):
                                assert service.requests("GET") == []

                    await run("deny or uncertain " + mode, denied)

                for phase in ("create", "get", "connect", "work", "stop"):

                    async def drain(phase: str = phase) -> None:
                        async with fixture(phase) as (
                            service,
                            gate,
                            receipts,
                            effects,
                            _,
                            start,
                            _,
                        ):

                            async def work(_driver: PlaywrightBrowser, is_stopped: Callable[[], bool]):
                                effects.append("work")
                                await gate.at("work")
                                assert not is_stopped() or phase == "work"
                                return "done"

                            task = asyncio.create_task(start(work))
                            await asyncio.wait_for(gate.entered.wait(), 8)
                            task.cancel()
                            await asyncio.sleep(0.02)
                            task.cancel()
                            await asyncio.sleep(0.02)
                            assert not task.done() and receipts == []
                            if phase != "stop":
                                assert service.requests("PATCH") == []
                            gate.resume.set()
                            await cancelled(task)
                            assert len(receipts) == 1 and await receipts[0].retry() == {"status": "complete"}
                            assert len(service.requests("PATCH")) == 1
                            if phase in ("create", "get", "connect"):
                                assert "work" not in effects
                            service.paths()

                    await run("repeat cancel drains " + phase, drain)

                for phase in ("consent", "native"):

                    async def held_tool(phase: str = phase) -> None:
                        async with fixture(phase) as (
                            service,
                            gate,
                            receipts,
                            effects,
                            origin,
                            start,
                            tools_for,
                        ):

                            async def work(driver: PlaywrightBrowser, is_stopped: Callable[[], bool]):
                                class Held:
                                    def __getattr__(self, name: str) -> object:
                                        return getattr(driver, name)

                                    async def new_tab(self, args: NewTabInput) -> None:
                                        await driver.new_tab(args)
                                        effects.append("native")
                                        await gate.at("native")

                                async def confirm(_: BrowserConfirmContext) -> bool:
                                    await gate.at("consent")
                                    return True

                                tools = tools_for(cast(PlaywrightBrowser, Held()), confirm)
                                try:
                                    await tools.execute(
                                        call(
                                            tools,
                                            "new_tab",
                                            {"url": origin + "/approved"},
                                        ),
                                        cancelled=is_stopped,
                                    )
                                finally:
                                    assert is_stopped()
                                    await cancelled(
                                        tools.execute(
                                            call(
                                                tools,
                                                "new_tab",
                                                {"url": origin + "/approved"},
                                            ),
                                            cancelled=is_stopped,
                                        )
                                    )

                            task = asyncio.create_task(start(work))
                            await asyncio.wait_for(gate.entered.wait(), 8)
                            task.cancel()
                            await asyncio.sleep(0.02)
                            task.cancel()
                            await asyncio.sleep(0.02)
                            assert not task.done() and receipts == [] and service.requests("PATCH") == []
                            assert effects.count("native") == int(phase == "native")
                            gate.resume.set()
                            await cancelled(task)
                            assert len(receipts) == 1 and await receipts[0].retry() == {"status": "complete"}
                            assert effects.count("native") == int(phase == "native")
                            assert service.page_hits == int(phase == "native")

                    await run("no late action after held " + phase, held_tool)

                async def predicate() -> None:
                    async with fixture() as (service, _, receipts, _, _, start, _):
                        pulse = False

                        def stopped() -> bool:
                            nonlocal pulse
                            current, pulse = pulse, False
                            return current

                        async def work(_driver: PlaywrightBrowser, is_stopped: Callable[[], bool]):
                            nonlocal pulse
                            pulse = True
                            assert is_stopped()
                            assert not stopped()
                            assert is_stopped()
                            return "ignored Stop"

                        await cancelled(start(work, cancelled=stopped))
                        assert len(receipts) == 1
                        assert await receipts[0].retry() == {"status": "complete"}
                        service.paths()

                await run(
                    "predicate latches cancellation even when callback returns",
                    predicate,
                )

                async def retry() -> None:
                    async with fixture() as (service, gate, receipts, _, _, start, _):
                        service.mode = "stop-failed"
                        result = await start()
                        assert result["status"] == "pending" and len(receipts) == 1
                        assert len(service.requests("PATCH")) == 1
                        service.mode = ""
                        gate.phase = "stop"
                        a = asyncio.create_task(receipts[0].retry())
                        b = asyncio.create_task(receipts[0].retry())
                        await asyncio.wait_for(gate.entered.wait(), 8)
                        assert len(service.requests("PATCH")) == 2
                        a.cancel()
                        await cancelled(a)
                        assert not b.done()
                        gate.resume.set()
                        assert await b == {"status": "complete"}
                        assert len(service.requests("PATCH")) == 2
                        service.paths()

                await run("failed Stop preserves saved id; concurrent retries coalesce", retry)

                async def stalled_close() -> None:
                    async with fixture() as (service, _, receipts, _, _, start, _):
                        release = asyncio.Event()
                        closes = 0
                        native_close = Browser.close

                        async def held(browser: Browser, **kwargs: Any) -> None:
                            nonlocal closes
                            closes += 1
                            await release.wait()
                            await native_close(browser, **kwargs)

                        try:
                            with patch.object(Browser, "close", held):
                                result = await start()
                                assert result["status"] == "pending" and closes == 1
                                assert len(service.requests("PATCH")) == 1
                                retrying = asyncio.create_task(receipts[0].retry())
                                release.set()
                                assert await retrying == {"status": "complete"}
                                assert closes == 1 and len(service.requests("PATCH")) == 1
                                service.paths()
                        finally:
                            release.set()

                await run(
                    "stalled CDP close still releases exact provider, retaining one close across retries", stalled_close
                )

                async def changed_owner() -> None:
                    async with fixture() as (service, _, receipts, _, _, start, _):

                        async def work(_driver: PlaywrightBrowser, _stopped: Callable[[], bool]) -> None:
                            service.mode = "attached"

                        result = await start(work)
                        assert result["status"] == "unverified" and service.requests("PATCH") == []
                        assert (await receipts[0].retry())["status"] == "unverified"
                        service.mode = ""
                        assert (await receipts[0].retry())["status"] == "complete"
                        assert len(service.requests("PATCH")) == 1
                        service.paths()

                await run("GET before Stop rechecks standalone ownership", changed_owner)

                async def shield_only() -> None:
                    async with fixture("work") as (
                        service,
                        gate,
                        receipts,
                        _,
                        _,
                        start,
                        _,
                    ):

                        async def work(_driver: PlaywrightBrowser, is_stopped: Callable[[], bool]):
                            await gate.at("work")
                            assert not is_stopped()
                            return "continue"

                        scope = asyncio.create_task(start(work))
                        wrapped = asyncio.shield(scope)
                        await asyncio.wait_for(gate.entered.wait(), 8)
                        wrapped.cancel()
                        await cancelled(wrapped)
                        assert not scope.done() and receipts == [] and service.requests("PATCH") == []
                        gate.resume.set()
                        assert (await scope)["result"] == "continue" and len(receipts) == 1

                await run("cancelling outer shield alone preserves live scope", shield_only)

                for wrapper in ("direct", "gather", "shield"):

                    async def retain_scope(wrapper: str = wrapper) -> None:
                        async with fixture("create") as (
                            service,
                            gate,
                            receipts,
                            effects,
                            _,
                            start,
                            _,
                        ):
                            scope = asyncio.create_task(start())
                            if wrapper == "gather":
                                joining = asyncio.gather(scope)
                            elif wrapper == "shield":
                                joining = asyncio.shield(scope)
                            else:
                                joining = scope
                            await asyncio.wait_for(gate.entered.wait(), 8)
                            scope.cancel()
                            await asyncio.sleep(0.02)
                            scope.cancel()
                            assert receipts == [] and not scope.done()
                            gate.resume.set()
                            await cancelled(joining)
                            assert len(receipts) == 1 and await receipts[0].retry() == {"status": "complete"}
                            assert effects == [] and len(service.requests("PATCH")) == 1

                    await run("retained owned Task receipt through " + wrapper, retain_scope)

                async def notifications() -> None:
                    async with fixture() as (_, _, _, _, _, start, _):

                        def throws(_: _Cleanup) -> None:
                            raise ValueError(SECRET)

                        await failed(start(on_cleanup=throws), CleanupNotificationError)
                    async with fixture() as (_, _, _, _, _, start, _):

                        async def wrong_async(_: _Cleanup) -> None:
                            raise AssertionError("never schedule a cleanup notifier")

                        await failed(start(on_cleanup=wrong_async), CleanupNotificationError)

                await run(
                    "private cleanup notifier failure and accidental coroutine",
                    notifications,
                )

                async def invalid() -> None:
                    async with fixture() as (service, _, _, effects, origin, _, _):
                        for key, base in (
                            ("", origin),
                            (KEY, ""),
                            (KEY, origin.replace("://", "://fixture@")),
                            (KEY, origin + "#fixture"),
                            (KEY, origin + "/?page=example#fixture"),
                        ):
                            receipt: list[_Cleanup] = []

                            async def never(_driver: PlaywrightBrowser, _stopped: Callable[[], bool]) -> None:
                                raise AssertionError("invalid config must not reach work")

                            await failed(
                                with_standalone_browser(
                                    pw.chromium,
                                    [origin],
                                    never,
                                    api_key=key,
                                    base_url=base,
                                    on_cleanup=receipt.append,
                                )
                            )
                            assert len(receipt) == 1 and (await receipt[0].retry())["status"] == "unverified"
                        assert service.log == [] and effects == []

                await run(
                    "required explicit config prevents provider env/default fallbacks",
                    invalid,
                )
            finally:
                await sentinel.close()
                await caller.close()
                await persistent.close()
    print(json.dumps({"passed": len(PASSED), "cases": PASSED}), flush=True)


asyncio.run(main())
