"""No provider network: published SDK MockTransport and a new owned sandboxed Chromium."""

from __future__ import annotations

import json
import shutil
import asyncio
import tempfile
from types import SimpleNamespace
from typing import Literal, TypedDict, cast
from pathlib import Path
from collections.abc import Callable, Awaitable
from typing_extensions import override

import httpx
from browserbase import AsyncBrowserbase
from browser_driver import PlaywrightBrowser
from browserbase_session import (
    SessionConfig,
    BrowserSessionError,
    BrowserCleanupNotificationError,
    _Cleanup,
    with_borrowed_browser,
    with_browserbase_session,
)
from playwright.async_api import (
    Route,
    Browser as PWBrowser,
    BrowserType,
    ViewportSize,
    BrowserContext,
    WebSocketRoute,
    async_playwright,
)

from openai.lib.browser import NewTabInput, AsyncBrowserToolset, BrowserConfirmContext
from openai.types.responses import ResponseFunctionToolCall

TMP = Path(tempfile.gettempdir())
PASSED: list[str] = []
HITS: list[bytes] = []


class ProviderMode(TypedDict, total=False):
    create_fail: bool
    release_fail: bool
    stay_live: bool
    created: dict[str, str]
    readback: dict[str, str]


class Request(TypedDict):
    method: str
    resource: str
    body: dict[str, object] | None


class Counts(TypedDict):
    context: int
    http: int
    ws: int
    context_close: int
    browser_close: int
    callback: int
    fail_close: bool


async def fixture(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        head = await reader.readuntil(b"\r\n\r\n")
        HITS.append(head.split(b"\r\n")[0])
        data = b"<title>Fixture</title><button>Apply</button><p>Approved fixture</p>"
        writer.write(
            b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: "
            + str(len(data)).encode()
            + b"\r\nConnection: close\r\n\r\n"
            + data
        )
        await writer.drain()
    except (ConnectionError, asyncio.IncompleteReadError):
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main() -> None:
    server = await asyncio.start_server(fixture, "127.0.0.1", 0)
    origin = "http://127.0.0.1:" + str(server.sockets[0].getsockname()[1])
    profile = tempfile.mkdtemp(dir=TMP, prefix="python-owner-")
    try:
        async with async_playwright() as pw:
            persistent = await pw.chromium.launch_persistent_context(
                profile,
                headless=True,
                chromium_sandbox=True,
                args=["--remote-debugging-port=0"],
                env={"PATH": "/usr/bin:/bin", "TMPDIR": str(TMP), "HOME": profile},
            )
            port = (Path(profile) / "DevToolsActivePort").read_text().splitlines()[0]
            endpoint = "http://127.0.0.1:" + port
            caller = await pw.chromium.connect_over_cdp(endpoint)
            sentinel = await caller.new_context()
            witness = await sentinel.new_page()
            await witness.set_content("<p>Caller must survive</p>")
            config: SessionConfig = {"project_id": "project-local", "allowed_origins": [origin]}

            async def no_gate(_: str) -> None:
                pass

            def provider(
                gate: Callable[[str], Awaitable[None]] = no_gate,
                mode: ProviderMode | None = None,
            ) -> tuple[AsyncBrowserbase, httpx.AsyncClient, list[Request]]:
                mode = {} if mode is None else mode
                log: list[Request] = []
                current = {
                    "id": "session-local",
                    "projectId": "project-local",
                    "status": "RUNNING",
                    "connectUrl": endpoint,
                    "signingKey": "PRIVATE_SIGNING_SENTINEL",
                    "seleniumRemoteUrl": "PRIVATE_SELENIUM_SENTINEL",
                }

                async def handle(request: httpx.Request) -> httpx.Response:
                    resource = request.url.path
                    method = request.method
                    body = cast("dict[str, object]", json.loads(request.content)) if request.content else None
                    log.append({"method": method, "resource": resource, "body": body})
                    if resource == "/v1/sessions":
                        assert (
                            body is not None
                            and method == "POST"
                            and body["timeout"] == 60
                            and body["keepAlive"] is False
                            and body["proxies"] is False
                            and body["browserSettings"]
                            == {
                                "recordSession": False,
                                "logSession": False,
                                "solveCaptchas": False,
                                "verified": False,
                                "advancedStealth": False,
                            }
                        )
                        await gate("create")
                        if mode.get("create_fail"):
                            return httpx.Response(504, json={"error": "PRIVATE_PROVIDER_ERROR"})
                        return httpx.Response(201, json={**current, **mode.get("created", {})})
                    assert resource == "/v1/sessions/session-local", resource
                    if method == "POST":
                        assert body == {"status": "REQUEST_RELEASE", "projectId": "project-local"}
                        await gate("release")
                        if mode.get("release_fail"):
                            return httpx.Response(503, json={"error": "PRIVATE_PROVIDER_ERROR"})
                        if not mode.get("stay_live"):
                            current["status"] = "COMPLETED"
                        return httpx.Response(200, json=current)
                    await gate("retrieve")
                    return httpx.Response(200, json={**current, **mode.get("readback", {})})

                pool = httpx.AsyncClient(transport=httpx.MockTransport(handle))
                return (
                    AsyncBrowserbase(
                        api_key="SYNTHETIC_UNUSED_KEY",
                        base_url="http://synthetic.invalid",
                        max_retries=2,
                        http_client=pool,
                    ),
                    pool,
                    log,
                )

            def releases(log: list[Request]) -> list[Request]:
                return [r for r in log if (r["body"] or {}).get("status") == "REQUEST_RELEASE"]

            class Context:
                def __init__(
                    self, context: BrowserContext, gate: Callable[[str], Awaitable[None]], counts: Counts
                ) -> None:
                    self.context, self.gate, self.counts = context, gate, counts

                def __getattr__(self, name: str) -> object:
                    return getattr(self.context, name)

                async def route(self, url: str, handler: Callable[[Route], Awaitable[None]]) -> None:
                    await self.context.route(url, handler)
                    self.counts["http"] += 1
                    await self.gate("http")

                async def route_web_socket(
                    self, url: str, handler: Callable[[WebSocketRoute], Awaitable[None]]
                ) -> None:
                    await self.context.route_web_socket(url, handler)
                    self.counts["ws"] += 1
                    await self.gate("ws")

                async def close(self) -> None:
                    self.counts["context_close"] += 1
                    if self.counts.get("fail_close"):
                        raise RuntimeError("PRIVATE_CONTEXT_ERROR")
                    await self.gate("close")
                    await self.context.close()

            class Browser:
                def __init__(
                    self, browser: PWBrowser, gate: Callable[[str], Awaitable[None]], counts: Counts, owned: bool
                ) -> None:
                    self.browser, self.gate, self.counts, self.owned = browser, gate, counts, owned

                async def new_context(
                    self, *, service_workers: Literal["block", "allow"], accept_downloads: bool, viewport: ViewportSize
                ) -> BrowserContext:
                    assert service_workers == "block" and accept_downloads is False
                    context = await self.browser.new_context(
                        service_workers=service_workers, accept_downloads=accept_downloads, viewport=viewport
                    )
                    self.counts["context"] += 1
                    await self.gate("context")
                    return cast("BrowserContext", Context(context, self.gate, self.counts))

                async def close(self) -> None:
                    self.counts["browser_close"] += 1
                    assert self.owned, "Borrowed browser must never be closed"
                    await self.browser.close()

            class Chromium:
                def __init__(self, gate: Callable[[str], Awaitable[None]], counts: Counts) -> None:
                    self.gate, self.counts = gate, counts

                async def connect_over_cdp(self, endpoint_url: str, *, timeout: float) -> PWBrowser:
                    browser = await pw.chromium.connect_over_cdp(endpoint_url, timeout=timeout)
                    await self.gate("connect")
                    return cast("PWBrowser", Browser(browser, self.gate, self.counts, True))

            def counts() -> Counts:
                return Counts(context=0, http=0, ws=0, context_close=0, browser_close=0, callback=0, fail_close=False)

            async def confirm(_: BrowserConfirmContext) -> bool:
                return True

            async def url_policy(_: BrowserConfirmContext, url: str) -> bool:
                return url.startswith(origin + "/") or url == origin

            def toolkit(
                driver: PlaywrightBrowser,
                confirm_callback: Callable[[BrowserConfirmContext], Awaitable[bool]] = confirm,
            ) -> AsyncBrowserToolset:
                return AsyncBrowserToolset(driver, confirm=confirm_callback, url_policy=url_policy)

            def new_tab(tools: AsyncBrowserToolset) -> ResponseFunctionToolCall:
                name = next(t["name"] for t in tools.tools if t["name"].endswith("new_tab"))
                return ResponseFunctionToolCall(
                    type="function_call",
                    call_id="a",
                    name=name,
                    id="f1",
                    status="completed",
                    arguments=json.dumps({"url": origin}),
                )

            async def work_check(driver: PlaywrightBrowser, cancelled: Callable[[], bool]) -> bool:
                tools = toolkit(driver)
                assert len(tools.tools) == 15
                names = [t["name"] for t in tools.tools]
                for member in ("scroll_to", "wait_for", "zoom"):
                    assert not any(n.endswith(member) for n in names)
                result = await tools.execute(new_tab(tools), cancelled=cancelled)
                assert '"ok": false' not in json.dumps(result), result
                state = await driver.state()
                assert len(state["tabs"]) == 1, state
                value = await driver.get_page_text({"tab_id": state["tabs"][0]["id"]})
                assert "Approved fixture" in value
                return True

            async def run(label: str, test: Callable[[], Awaitable[None]]) -> None:
                await test()
                assert "Caller must survive" in await witness.locator("p").inner_text()
                PASSED.append(label)
                print(json.dumps({"name": label, "pass": True}), flush=True)

            async def dispose(client: AsyncBrowserbase, pool: httpx.AsyncClient) -> None:
                assert not pool.is_closed, "supplied pool remains caller-owned"
                await client.close()

            try:

                async def happy() -> None:
                    client, pool, log = provider()
                    handles: list[_Cleanup] = []
                    try:
                        result = await with_browserbase_session(
                            client, pw.chromium, config, work_check, on_cleanup=handles.append
                        )
                        assert result["result"] and result["status"] == "complete"
                        assert handles == [result["cleanup"]]
                        assert len(releases(log)) == 1
                        assert len([r for r in log if r["resource"] == "/v1/sessions"]) == 1
                        before = len(log)
                        assert await result["cleanup"].retry() == {"status": "complete"}
                        assert len(log) == before
                    finally:
                        await dispose(client, pool)

                await run("owned real installed public helpers and 15 generic declarations", happy)

                async def borrowed_happy() -> None:
                    handles: list[_Cleanup] = []
                    result = await with_borrowed_browser(caller, config, work_check, on_cleanup=handles.append)
                    assert result["status"] == "complete" and handles == [result["cleanup"]]

                await run("borrowed happy keeps caller-owned real sentinel", borrowed_happy)

                for configured, equivalent, other in (
                    ("https://EXAMPLE.test", "https://example.test:443/page", "https://example.test:444/page"),
                    ("https://example.test:443", "https://example.test/page", "http://example.test/page"),
                    ("http://example.test", "http://example.test:80/page", "http://example.test:81/page"),
                    ("http://example.test:80", "http://example.test/page", "https://example.test/page"),
                    ("http://[::1]:8080", "http://[::1]:8080/page", "http://[::1]/page"),
                ):
                    for owned in (False, True):

                        async def canonical_origin(
                            configured: str = configured,
                            equivalent: str = equivalent,
                            other: str = other,
                            owned: bool = owned,
                        ) -> None:
                            handles: list[_Cleanup] = []
                            client, pool, log = provider()

                            class RequestRoute:
                                def __init__(self, url: str) -> None:
                                    self.request = SimpleNamespace(url=url)
                                    self.effects: list[str] = []

                                async def fetch(self, *, max_redirects: int, timeout: float) -> SimpleNamespace:
                                    assert max_redirects == 0 and timeout == 0
                                    self.effects.append("fetch")

                                    async def dispose() -> None:
                                        pass

                                    return SimpleNamespace(status=200, dispose=dispose)

                                async def fulfill(self, *, response: SimpleNamespace) -> None:
                                    assert response.status == 200
                                    self.effects.append("fulfill")

                                async def abort(self, reason: str) -> None:
                                    self.effects.append(reason)

                            async def work(driver: PlaywrightBrowser, _cancelled: Callable[[], bool]) -> bool:
                                for url, expected in (
                                    (equivalent, ["fetch", "fulfill"]),
                                    (other, ["blockedbyclient"]),
                                    ("https://unlisted.test/page", ["blockedbyclient"]),
                                ):
                                    assert driver.allows(url) is (expected[0] == "fetch")
                                    route = RequestRoute(url)
                                    await driver.guard(cast("Route", route))
                                    assert route.effects == expected
                                return True

                            case_config: SessionConfig = {
                                "project_id": "project-local",
                                "allowed_origins": [configured],
                            }
                            try:
                                if owned:
                                    result = await with_browserbase_session(
                                        client, pw.chromium, case_config, work, on_cleanup=handles.append
                                    )
                                    assert len(releases(log)) == 1
                                else:
                                    result = await with_borrowed_browser(
                                        caller, case_config, work, on_cleanup=handles.append
                                    )
                                    assert log == []
                                assert result["result"] is True and result["status"] == "complete"
                                assert handles == [result["cleanup"]]
                            finally:
                                await dispose(client, pool)

                        await run(f"canonical origin {configured}, owned={owned}", canonical_origin)

                for owned, phases in [
                    (True, ("create", "connect", "context", "http", "ws", "callback", "release")),
                    (False, ("context", "http", "ws", "callback")),
                ]:
                    for phase, rejects in [*((phase, False) for phase in phases), ("http", True), ("ws", True)]:

                        async def cancel_case(phase: str = phase, owned: bool = owned, rejects: bool = rejects) -> None:
                            entered, resume = asyncio.Event(), asyncio.Event()
                            c = counts()
                            handles: list[_Cleanup] = []

                            async def gate(at: str) -> None:
                                if at == phase:
                                    entered.set()
                                    await resume.wait()
                                    if rejects:
                                        raise RuntimeError("SYNTHETIC_GUARD_FAILURE")

                            client, pool, log = provider(gate)

                            async def work(_driver: PlaywrightBrowser, cancelled: Callable[[], bool]):
                                c["callback"] += 1
                                await gate("callback")
                                return not cancelled()

                            if owned:
                                task = asyncio.create_task(
                                    with_browserbase_session(
                                        client,
                                        cast("BrowserType", Chromium(gate, c)),
                                        config,
                                        work,
                                        on_cleanup=handles.append,
                                    )
                                )
                            else:
                                task = asyncio.create_task(
                                    with_borrowed_browser(
                                        cast("PWBrowser", Browser(caller, gate, c, False)),
                                        config,
                                        work,
                                        on_cleanup=handles.append,
                                    )
                                )
                            try:
                                await asyncio.wait_for(entered.wait(), 4)
                                task.cancel()
                                await asyncio.sleep(0.02)
                                task.cancel()
                                await asyncio.sleep(0.02)
                                if phase in ("context", "http", "ws"):
                                    _, pending = await asyncio.wait({task}, timeout=1)
                                    assert not pending, "Opening must stay owned without blocking Stop."
                                    assert len(handles) == 1
                                    assert await handles[0].retry() == {"status": "pending"}
                                    if phase != "context":
                                        assert c["context_close"] == 1 and c["callback"] == 0
                                else:
                                    assert not task.done(), "Scope must wait for admitted work and cleanup"
                                    assert handles == []
                                    if phase != "release":
                                        assert c["context_close"] == c["browser_close"] == 0
                                        assert len(releases(log)) == 0
                                resume.set()
                                try:
                                    await task
                                    raise AssertionError("expected cancellation")
                                except asyncio.CancelledError:
                                    assert len(handles) == 1
                                    if phase in ("context", "http", "ws"):
                                        opening = handles[0]._opening
                                        assert opening is not None
                                        try:
                                            await asyncio.wait_for(asyncio.shield(opening), 2)
                                        except asyncio.CancelledError:
                                            assert not rejects
                                        except RuntimeError as error:
                                            assert rejects and str(error) == "SYNTHETIC_GUARD_FAILURE"
                                    assert await handles[0].retry() == {"status": "complete"}
                                assert c["browser_close"] == int(owned and phase != "create")
                                if owned:
                                    assert len(releases(log)) == 1
                                    assert len([r for r in log if r["resource"] == "/v1/sessions"]) == 1
                                else:
                                    assert log == []
                                if phase not in ("callback", "release"):
                                    assert c["callback"] == 0
                                if phase == "http":
                                    assert c["ws"] == 0
                            finally:
                                resume.set()
                                if not task.done():
                                    try:
                                        await task
                                    except asyncio.CancelledError:
                                        pass
                                await dispose(client, pool)

                        await run(
                            ("owned" if owned else "borrowed")
                            + " twice cancelled at "
                            + phase
                            + (" rejecting" if rejects else ""),
                            cancel_case,
                        )

                for owned in (False, True):
                    for rejects in (False, True):
                        for explicit in (False, True):

                            async def opening_case(
                                owned: bool = owned, rejects: bool = rejects, explicit: bool = explicit
                            ) -> None:
                                entered, resume, stop = asyncio.Event(), asyncio.Event(), asyncio.Event()
                                c = counts()
                                handles: list[_Cleanup] = []
                                client, pool, log = provider()

                                class LateContext:
                                    async def close(self) -> None:
                                        c["context_close"] += 1

                                    async def route(self, *_args: object) -> None:
                                        c["http"] += 1

                                class OpeningBrowser(Browser):
                                    @override
                                    async def new_context(
                                        self,
                                        *,
                                        service_workers: Literal["block", "allow"],
                                        accept_downloads: bool,
                                        viewport: ViewportSize,
                                    ) -> BrowserContext:
                                        assert service_workers == "block" and not accept_downloads and viewport
                                        c["context"] += 1
                                        entered.set()
                                        await resume.wait()
                                        if rejects:
                                            raise RuntimeError("SYNTHETIC_OPEN_FAILURE")
                                        return cast("BrowserContext", LateContext())

                                class OpeningChromium:
                                    async def connect_over_cdp(self, endpoint_url: str, *, timeout: float) -> PWBrowser:
                                        connected = await pw.chromium.connect_over_cdp(endpoint_url, timeout=timeout)
                                        return cast("PWBrowser", OpeningBrowser(connected, no_gate, c, True))

                                async def no_work(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]) -> bool:
                                    c["callback"] += 1
                                    return True

                                if owned:
                                    task = asyncio.create_task(
                                        with_browserbase_session(
                                            client,
                                            cast("BrowserType", OpeningChromium()),
                                            config,
                                            no_work,
                                            on_cleanup=handles.append,
                                            cancelled=stop.is_set,
                                        )
                                    )
                                else:
                                    task = asyncio.create_task(
                                        with_borrowed_browser(
                                            cast("PWBrowser", OpeningBrowser(caller, no_gate, c, False)),
                                            config,
                                            no_work,
                                            on_cleanup=handles.append,
                                            cancelled=stop.is_set,
                                        )
                                    )
                                try:
                                    await asyncio.wait_for(entered.wait(), 2)
                                    if explicit:
                                        task.cancel()
                                    else:
                                        stop.set()
                                    _, pending = await asyncio.wait({task}, timeout=1)
                                    assert not pending, "Pending context creation must not keep the scope alive."
                                    try:
                                        await task
                                        raise AssertionError("Cancellation required")
                                    except asyncio.CancelledError:
                                        pass
                                    assert len(handles) == 1
                                    handle = handles[0]
                                    assert await handle.retry() == {"status": "pending"}
                                    assert c["context_close"] == c["http"] == c["ws"] == c["callback"] == 0
                                    assert c["browser_close"] == int(owned) and len(releases(log)) == int(owned)
                                    resume.set()
                                    opening = handle._opening
                                    assert opening is not None
                                    try:
                                        await asyncio.wait_for(asyncio.shield(opening), 2)
                                        assert not rejects
                                    except asyncio.CancelledError:
                                        assert not rejects
                                    except RuntimeError as error:
                                        assert rejects and str(error) == "SYNTHETIC_OPEN_FAILURE"
                                    # Automatic retry has completed before the opening owner settles.
                                    assert handle._complete and c["context_close"] == int(not rejects)
                                    assert c["context"] == 1 and c["http"] == c["ws"] == c["callback"] == 0
                                    old_log = list(log)
                                    assert await handle.retry() == {"status": "complete"}
                                    assert log == old_log and len(releases(log)) == int(owned)
                                    assert c["browser_close"] == int(owned)
                                finally:
                                    resume.set()
                                    if not task.done():
                                        try:
                                            await task
                                        except (BrowserSessionError, asyncio.CancelledError):
                                            pass
                                    await dispose(client, pool)

                            await run(f"late opening owned={owned} rejects={rejects} explicit={explicit}", opening_case)

                async def stopped_before_opening_starts() -> None:
                    c = counts()
                    handles: list[_Cleanup] = []
                    reads = 0

                    def cancelled() -> bool:
                        nonlocal reads
                        reads += 1
                        # The borrowed scope checks admission and configuration,
                        # then polls after it retains its context-creation task.
                        return reads >= 3

                    async def no_work(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]) -> bool:
                        c["callback"] += 1
                        return True

                    try:
                        await with_borrowed_browser(
                            cast("PWBrowser", Browser(caller, no_gate, c, False)),
                            config,
                            no_work,
                            on_cleanup=handles.append,
                            cancelled=cancelled,
                        )
                        raise AssertionError("Stop is required.")
                    except asyncio.CancelledError:
                        pass
                    assert len(handles) == 1
                    opening = handles[0]._opening
                    assert opening is not None
                    try:
                        await asyncio.wait_for(asyncio.shield(opening), 2)
                    except asyncio.CancelledError:
                        pass
                    assert c["context"] == c["context_close"] == c["browser_close"] == c["callback"] == 0
                    assert await handles[0].retry() == {"status": "complete"}

                await run(
                    "Stop after opening task retention prevents context invocation", stopped_before_opening_starts
                )

                for phase in ("consent", "native"):

                    async def held_tool(phase: str = phase) -> None:
                        entered, resume = asyncio.Event(), asyncio.Event()
                        c = counts()
                        effects = 0
                        handles: list[_Cleanup] = []
                        client, pool, log = provider()

                        async def work(driver: PlaywrightBrowser, cancelled: Callable[[], bool]):
                            class Held:
                                def __getattr__(self, name: str) -> object:
                                    return getattr(driver, name)

                                async def new_tab(self, args: NewTabInput) -> None:
                                    nonlocal effects
                                    result = await driver.new_tab(args)
                                    effects += 1
                                    if phase == "native":
                                        entered.set()
                                        await resume.wait()
                                    return result

                            async def held_consent(_: BrowserConfirmContext) -> bool:
                                if phase == "consent":
                                    entered.set()
                                    await resume.wait()
                                return True

                            tools = toolkit(cast("PlaywrightBrowser", Held()), held_consent)
                            return await tools.execute(new_tab(tools), cancelled=cancelled)

                        task = asyncio.create_task(
                            with_browserbase_session(
                                client,
                                cast("BrowserType", Chromium(no_gate, c)),
                                config,
                                work,
                                on_cleanup=handles.append,
                            )
                        )
                        try:
                            await asyncio.wait_for(entered.wait(), 4)
                            task.cancel()
                            await asyncio.sleep(0.02)
                            task.cancel()
                            await asyncio.sleep(0.02)
                            assert not task.done()
                            assert handles == []
                            assert c["context_close"] == c["browser_close"] == 0
                            assert len(releases(log)) == 0
                            assert effects == int(phase == "native")
                            resume.set()
                            try:
                                await task
                                raise AssertionError("cancel required")
                            except asyncio.CancelledError:
                                assert len(handles) == 1
                                assert await handles[0].retry() == {"status": "complete"}
                            assert effects == int(phase == "native") and len(releases(log)) == 1
                        finally:
                            resume.set()
                            await dispose(client, pool)

                    await run("twice cancelled during public helper " + phase, held_tool)

                for created in ({"id": "../other"}, {"id": ""}):

                    async def invalid_initial(created: dict[str, str] = created) -> None:
                        handles: list[_Cleanup] = []
                        client, pool, log = provider(mode={"created": created})
                        try:

                            async def forbidden(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                                raise AssertionError("no work expected")

                            try:
                                await with_browserbase_session(
                                    client, pw.chromium, config, forbidden, on_cleanup=handles.append
                                )
                                raise AssertionError("expected failed session")
                            except BrowserSessionError as error:
                                assert str(error) == "Browser session failed."
                                assert await error.cleanup.retry() == {"status": "unverified"}
                            assert len(log) == 1
                        finally:
                            await dispose(client, pool)

                    await run("initial invalid identity " + json.dumps(created), invalid_initial)

                for initially_verified in (True, False):

                    async def refused_project(initially_verified: bool = initially_verified) -> None:
                        mode: ProviderMode = {
                            "created": {"projectId": "other"},
                            "readback": {} if initially_verified else {"projectId": "other"},
                        }
                        client, pool, log = provider(mode=mode)
                        try:

                            async def forbidden(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]) -> None:
                                raise AssertionError("no work expected")

                            try:
                                await with_browserbase_session(
                                    client, pw.chromium, config, forbidden, on_cleanup=lambda _: None
                                )
                                raise AssertionError("expected failed session")
                            except BrowserSessionError as error:
                                assert len(releases(log)) == int(initially_verified)
                                assert await error.cleanup.retry() == {
                                    "status": "complete" if initially_verified else "pending"
                                }
                                assert len(releases(log)) == int(initially_verified)
                                mode["readback"] = {}
                                assert await error.cleanup.retry() == {"status": "complete"}
                                assert len(releases(log)) == 1
                        finally:
                            await dispose(client, pool)

                    await run(
                        "create-project mismatch then verified readback " + str(initially_verified), refused_project
                    )

                async def create_uncertain() -> None:
                    handles: list[_Cleanup] = []
                    client, pool, log = provider(mode={"create_fail": True})
                    try:

                        async def forbidden(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                            raise AssertionError("no callback")

                        try:
                            await with_browserbase_session(
                                client, pw.chromium, config, forbidden, on_cleanup=handles.append
                            )
                            raise AssertionError("failure required")
                        except BrowserSessionError as error:
                            assert await error.cleanup.retry() == {"status": "unverified"}
                        assert len(log) == 1
                    finally:
                        await dispose(client, pool)

                await run("504 uncertain create once despite shared-client retry defaults", create_uncertain)
                for readback in ({"id": "other"}, {"projectId": "other"}, {"status": "UNKNOWN"}):

                    async def invalid_readback(readback: dict[str, str] = readback) -> None:
                        handles: list[_Cleanup] = []
                        client, pool, log = provider(mode={"readback": readback})
                        try:

                            async def callback(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                                return True

                            result = await with_browserbase_session(
                                client, pw.chromium, config, callback, on_cleanup=handles.append
                            )
                            assert result["status"] == "pending" and len(releases(log)) == 0
                        finally:
                            await dispose(client, pool)

                    await run("readback identity/status " + json.dumps(readback), invalid_readback)

                async def retry_failure() -> None:
                    handles: list[_Cleanup] = []
                    mode: ProviderMode = {"release_fail": True}
                    client, pool, log = provider(mode=mode)
                    try:

                        async def callback(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                            raise RuntimeError("PRIVATE_CALLBACK_ERROR")

                        try:
                            await with_browserbase_session(
                                client, pw.chromium, config, callback, on_cleanup=handles.append
                            )
                            raise AssertionError("failure required")
                        except BrowserSessionError as error:
                            assert str(error) == "Browser session failed."
                            assert len(releases(log)) == 1
                            before = len(log)
                            mode["release_fail"] = False
                            a, b = await asyncio.gather(error.cleanup.retry(), error.cleanup.retry())
                            assert a == b == {"status": "complete"}
                        assert log[before]["method"] == "GET" and len(releases(log[before:])) == 1
                    finally:
                        await dispose(client, pool)

                await run("failure retains cleanup handle and concurrent retries read first", retry_failure)

                async def local_cleanup_failure() -> None:
                    handles: list[_Cleanup] = []
                    c = counts()
                    c["fail_close"] = True
                    client, pool, log = provider()
                    handles: list[_Cleanup] = []
                    try:

                        async def callback(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                            return True

                        result = await with_browserbase_session(
                            client,
                            cast("BrowserType", Chromium(no_gate, c)),
                            config,
                            callback,
                            on_cleanup=handles.append,
                        )
                        assert result["status"] == "pending" and len(releases(log)) == 1
                        c["fail_close"] = False
                        assert await result["cleanup"].retry() == {"status": "complete"}
                        assert len(releases(log)) == 1
                    finally:
                        await dispose(client, pool)

                await run("failed local close still requests release once", local_cleanup_failure)

                async def unsettled_local_close() -> None:
                    c = counts()
                    client, pool, log = provider()
                    handles: list[_Cleanup] = []
                    finish = asyncio.Event()

                    async def gate(at: str) -> None:
                        if at == "close":
                            await finish.wait()

                    async def callback(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]) -> bool:
                        return True

                    try:
                        start = asyncio.get_running_loop().time()
                        result = await with_browserbase_session(
                            client, cast("BrowserType", Chromium(gate, c)), config, callback, on_cleanup=handles.append
                        )
                        assert asyncio.get_running_loop().time() - start < 6
                        assert result["status"] == "pending" and len(releases(log)) == 1
                        assert c["context_close"] == 1
                        first = asyncio.create_task(result["cleanup"].retry())
                        second = asyncio.create_task(result["cleanup"].retry())
                        assert c["context_close"] == 1
                        finish.set()
                        assert await asyncio.gather(first, second) == [{"status": "complete"}, {"status": "complete"}]
                        assert len(releases(log)) == 1
                    finally:
                        finish.set()
                        await dispose(client, pool)

                await run("unsettled local close releases provider and is retained by retries", unsettled_local_close)

                for boundary in ("task", "shield", "gather"):

                    async def wrapped_cancel(boundary: str = boundary) -> None:
                        handles: list[_Cleanup] = []
                        entered, resume = asyncio.Event(), asyncio.Event()
                        mode: ProviderMode = {"release_fail": True}

                        async def gate(phase: str) -> None:
                            if phase == "create":
                                entered.set()
                                await resume.wait()

                        client, pool, log = provider(gate, mode)

                        async def forbidden(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                            raise AssertionError("stopped create must not admit work")

                        task = asyncio.create_task(
                            with_browserbase_session(client, pw.chromium, config, forbidden, on_cleanup=handles.append)
                        )
                        observed = (
                            asyncio.shield(task)
                            if boundary == "shield"
                            else (asyncio.gather(task) if boundary == "gather" else task)
                        )
                        try:
                            await asyncio.wait_for(entered.wait(), 4)
                            task.cancel()
                            await asyncio.sleep(0.015)
                            task.cancel()
                            await asyncio.sleep(0.015)
                            assert not task.done() and handles == [] and releases(log) == []
                            resume.set()
                            try:
                                await observed
                                raise AssertionError("cancel required")
                            except asyncio.CancelledError:
                                pass
                            assert len(handles) == 1 and len(releases(log)) == 1
                            mode["release_fail"] = False
                            before = len(log)
                            a, b = await asyncio.gather(handles[0].retry(), handles[0].retry())
                            assert a == b == {"status": "complete"} and log[before]["method"] == "GET"
                            assert len(releases(log[before:])) == 1 and len(handles) == 1
                        finally:
                            resume.set()
                            await dispose(client, pool)

                    await run(boundary + " keeps one post-cancel pending receipt for saved-id retry", wrapped_cancel)

                async def direct_cancel() -> None:
                    handles: list[_Cleanup] = []
                    entered = False
                    mode: ProviderMode = {"release_fail": True}
                    client, pool, log = provider(mode=mode)

                    async def work(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                        nonlocal entered
                        entered = True

                    try:
                        try:
                            await with_browserbase_session(
                                client, pw.chromium, config, work, on_cleanup=handles.append, cancelled=lambda: entered
                            )
                            raise AssertionError("cancel required")
                        except asyncio.CancelledError:
                            assert len(handles) == 1
                        assert len(releases(log)) == 1
                        mode["release_fail"] = False
                        assert await handles[0].retry() == {"status": "complete"}
                        assert len(releases(log)) == 2 and len(handles) == 1
                    finally:
                        await dispose(client, pool)

                await run("direct await cancellation keeps private pending receipt", direct_cancel)

                async def copy_failure() -> None:
                    # The published SDK copy() re-instantiates self.__class__ without the app argument.
                    # This supported subclass works when created but its inherited with_options cannot copy it.
                    class ScopedAppClient(AsyncBrowserbase):
                        def __init__(
                            self, app_scope: str, *, api_key: str, base_url: str, http_client: httpx.AsyncClient
                        ) -> None:
                            self.app_scope = app_scope
                            super().__init__(api_key=api_key, base_url=base_url, http_client=http_client)

                    handles: list[_Cleanup] = []
                    log: list[httpx.Request] = []

                    async def unexpected(req: httpx.Request) -> httpx.Response:
                        log.append(req)
                        raise AssertionError("copy fails before any request")

                    pool = httpx.AsyncClient(transport=httpx.MockTransport(unexpected))
                    client = ScopedAppClient(
                        "SYNTHETIC_APP_SCOPE",
                        api_key="SYNTHETIC_UNUSED_KEY",
                        base_url="http://synthetic.invalid",
                        http_client=pool,
                    )

                    async def forbidden(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                        raise AssertionError("no work")

                    try:
                        try:
                            await with_browserbase_session(
                                client, pw.chromium, config, forbidden, on_cleanup=handles.append
                            )
                            raise AssertionError("copy failure required")
                        except BrowserSessionError as error:
                            assert str(error) == "Browser session failed."
                            assert error.__context__ is None and error.__cause__ is None
                            assert handles == [error.cleanup]
                        assert await handles[0].retry() == {"status": "unverified"}
                        assert log == [] and not pool.is_closed
                    finally:
                        await dispose(client, pool)

                await run(
                    "real provider inherited with_options copy failure is sanitized before requests", copy_failure
                )

                async def callback_validation() -> None:
                    client, pool, log = provider()

                    async def forbidden(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                        raise AssertionError("work forbidden")

                    try:
                        for call in (
                            with_browserbase_session(
                                client,
                                pw.chromium,
                                config,
                                forbidden,
                                on_cleanup=cast("Callable[[_Cleanup], object]", None),
                            ),
                            with_borrowed_browser(
                                caller, config, forbidden, on_cleanup=cast("Callable[[_Cleanup], object]", None)
                            ),
                        ):
                            try:
                                await call
                                raise AssertionError("invalid callback required")
                            except TypeError as error:
                                assert str(error) == "on_cleanup must be callable."
                        assert log == []
                    finally:
                        await dispose(client, pool)

                await run("required receipt callback validated before owned or borrowed admission", callback_validation)

                for failure in ("throw", "coroutine", "custom_awaitable"):

                    async def notification_failure(failure: str = failure) -> None:
                        calls: list[_Cleanup] = []
                        started: list[bool] = []

                        async def later() -> None:
                            started.append(True)

                        class NotScheduled:
                            def __await__(self):
                                started.append(True)
                                yield

                        def notify(handle: _Cleanup) -> object:
                            calls.append(handle)
                            if failure == "throw":
                                raise ValueError("SYNTHETIC_PRIVATE_NOTIFICATION")
                            if failure == "coroutine":
                                return later()
                            return NotScheduled()

                        async def work(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                            return True

                        client, pool, log = provider()
                        try:
                            try:
                                await with_browserbase_session(client, pw.chromium, config, work, on_cleanup=notify)
                                raise AssertionError("notification failure expected")
                            except BrowserCleanupNotificationError as error:
                                assert str(error) == "Browser cleanup notification failed."
                                assert error.__context__ is None and error.__cause__ is None
                            assert len(calls) == 1 and started == [] and len(releases(log)) == 1
                        finally:
                            await dispose(client, pool)

                    await run(
                        "failed " + failure + " receipt notification is sanitized and never awaited",
                        notification_failure,
                    )

                for primary in ("failure", "cancel"):

                    async def priority(primary: str = primary) -> None:
                        handles: list[_Cleanup] = []
                        stop = False

                        def notify(handle: _Cleanup) -> object:
                            handles.append(handle)
                            raise ValueError("SYNTHETIC_PRIVATE_NOTIFICATION")

                        async def work(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]):
                            nonlocal stop
                            if primary == "failure":
                                raise ValueError("SYNTHETIC_PRIVATE_WORK")
                            stop = True

                        client, pool, log = provider()
                        try:
                            try:
                                await with_browserbase_session(
                                    client, pw.chromium, config, work, on_cleanup=notify, cancelled=lambda: stop
                                )
                                raise AssertionError("expected primary outcome")
                            except asyncio.CancelledError:
                                assert primary == "cancel"
                            except BrowserSessionError as error:
                                assert primary == "failure" and type(error) is BrowserSessionError
                                assert str(error) == "Browser session failed."
                                assert error.__context__ is None and error.__cause__ is None
                            assert len(handles) == 1 and len(releases(log)) == 1
                        finally:
                            await dispose(client, pool)

                    await run(primary + " takes precedence over notification failure", priority)

                for case in ("confirm_stop", "observed_then_cleared", "cleanup_error_after_stop"):

                    async def observed_stop(case: str = case) -> None:
                        requested = False
                        recorded: list[bool] = []
                        handles: list[_Cleanup] = []
                        before = len(HITS)

                        async def work(driver: PlaywrightBrowser, cancelled: Callable[[], bool]) -> None:
                            nonlocal requested

                            async def confirm_stop(_: BrowserConfirmContext) -> bool:
                                nonlocal requested
                                if case in ("confirm_stop", "cleanup_error_after_stop"):
                                    requested = True
                                return True

                            tools = toolkit(driver, confirm_stop)
                            if case == "observed_then_cleared":
                                requested = True
                                recorded.append(cancelled())
                                requested = False
                                recorded.append(cancelled())
                            await tools.execute(new_tab(tools), cancelled=cancelled)

                        def notify(handle: _Cleanup) -> None:
                            handles.append(handle)
                            if case == "cleanup_error_after_stop":
                                raise ValueError("SYNTHETIC_PRIVATE_NOTICE")

                        try:
                            await with_borrowed_browser(
                                caller, config, work, on_cleanup=notify, cancelled=lambda: requested
                            )
                            raise AssertionError("scope must remain cancelled")
                        except asyncio.CancelledError:
                            pass
                        assert len(HITS) == before and len(handles) == 1
                        assert await handles[0].retry() == {"status": "complete"}
                        if case == "observed_then_cleared":
                            assert recorded == [True, True]

                    await run("installed helper observed Stop: " + case, observed_stop)

                async def outer_shield_only() -> None:
                    entered, release = asyncio.Event(), asyncio.Event()
                    handles: list[_Cleanup] = []

                    async def held(_driver: PlaywrightBrowser, _cancelled: Callable[[], bool]) -> bool:
                        entered.set()
                        await release.wait()
                        return True

                    task = asyncio.create_task(with_borrowed_browser(caller, config, held, on_cleanup=handles.append))
                    shield = asyncio.shield(task)
                    await entered.wait()
                    shield.cancel()
                    try:
                        await shield
                        raise AssertionError("wrapper cancellation required")
                    except asyncio.CancelledError:
                        assert not task.done() and handles == []
                    release.set()
                    completed = await task
                    assert len(handles) == 1 and completed["result"] is True

                await run("outer shield alone cannot stop or finish its scope", outer_shield_only)
                print(
                    json.dumps(
                        {
                            "summary": True,
                            "passed": len(PASSED),
                            "provider": "httpx_mocktransport_only",
                            "apiRequests": 0,
                            "chromium": caller.version,
                            "sandbox": True,
                            "cancellation_handle_checked": True,
                        }
                    )
                )
            finally:
                await sentinel.close()
                await caller.close()
                await persistent.close()
    finally:
        server.close()
        await server.wait_closed()
        shutil.rmtree(profile)


asyncio.run(main())
