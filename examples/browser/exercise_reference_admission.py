"""Finite shared-driver admission and new-tab cancellation checks; no API calls."""

from __future__ import annotations

import json
import asyncio
from typing import Any, Callable, Awaitable, cast
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import patch
from typing_extensions import override

from browser_driver import PlaywrightBrowser
from playwright.async_api import Page, Error, Browser, ElementHandle, async_playwright

from openai.lib.browser import BrowserError, AsyncBrowserToolset, BrowserCancelledError
from openai.types.responses import ResponseFunctionToolCall

HTML = '<main data-record-id="form"><input aria-label="Name" data-browser-field="name" value="initial"><select aria-label="Room" data-browser-field="room"><option value="a">A</option><option value="b">B</option></select><input aria-label="Password" type="password" data-browser-field="password" value="PRIVATE_PASSWORD"><input aria-label="Upload" type="file" data-browser-field="upload"><input aria-label="Token" type="hidden" data-browser-field="token" value="PRIVATE_TOKEN"></main>'


async def approve(_context: object) -> bool:
    return True


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        self.send_response(200)
        if self.path == "/vector":
            content_type = "image/svg+xml"
            content = '<svg xmlns="http://www.w3.org/2000/svg"><text>Outside HTML</text></svg>'
        elif self.path == "/data":
            content_type = "application/xml"
            content = '<?xml-stylesheet type="text/css" href="/xml.css"?><record><name>Outside HTML</name></record>'
        elif self.path == "/xml.css":
            content_type = "text/css"
            content = "record, name { display: block; }"
        else:
            content_type = "text/html"
            content = HTML
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(content.encode())


def call(member: str, tab: str, target: str, value: str) -> ResponseFunctionToolCall:
    args = {"tab_id": tab, "target": target, **({"text": value} if member == "type" else {"values": [value]})}
    return ResponseFunctionToolCall(
        id="item",
        call_id="call",
        name="browser_" + member,
        type="function_call",
        status="completed",
        arguments=json.dumps(args),
    )


async def form(browser: Browser, origin: str, url: str, owned: bool) -> int:
    context = await browser.new_context(service_workers="block")
    grants = frozenset((url, "form", name) for name in ("name", "room", "password", "upload", "token"))
    driver = PlaywrightBrowser(
        context,
        {origin},
        owned_fixture_urls=frozenset({url}) if owned else None,
        public_values=grants if owned else frozenset(),
    )
    checks = 0
    try:
        await driver.new_tab({"url": url})
        tab = (await driver.state())["tabs"][0]["id"]
        page = context.pages[0]
        report = await driver.read_page({"tab_id": tab, "filter": "all"})
        assert not isinstance(report, str)
        assert [item["label"] for item in report["elements"]] == ["Name", "Room"]
        assert all(
            secret not in json.dumps(report)
            for secret in ("PRIVATE_PASSWORD", "PRIVATE_TOKEN", "Password", "Upload", "Token")
        )
        checks += 2
        if owned:
            name = next(item["ref"] for item in report["elements"] if item["label"] == "Name")
            describe = driver.describe_target
            assert describe is not None
            try:
                await describe({"tab_id": tab, "target": name}, cancelled=lambda: True)
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError("Stopped describe_target was admitted")
            assert await describe({"tab_id": tab, "target": name}) == {"label": "Name", "role": "textbox"}
            await driver.type({"tab_id": tab, "target": name, "text": "first"})
            await driver.type({"tab_id": tab, "target": name, "text": "last"})
            assert await page.locator("input").first.input_value() == "last"
            return checks + 3
        for member, label, first, last in (("type", "Name", "first", "last"), ("select_option", "Room", "a", "b")):
            ref = next(item["ref"] for item in report["elements"] if item["label"] == label)
            a = AsyncBrowserToolset(driver, members=[member], confirm=approve)
            b = AsyncBrowserToolset(driver, members=[member], confirm=approve)
            entered, release = asyncio.Event(), asyncio.Event()
            evaluate = page.evaluate
            held = False

            async def checked(
                expression: str,
                arg: Any = None,
                *,
                started: asyncio.Event = entered,
                finish: asyncio.Event = release,
                read: Callable[..., Awaitable[Any]] = evaluate,
            ) -> Any:
                nonlocal held
                if isinstance(arg, dict) and cast(dict[str, object], arg).get("checkedNode") and not held:
                    held = True
                    started.set()
                    await finish.wait()
                return await read(expression, arg)

            with patch.object(page, "evaluate", checked):
                pending = asyncio.create_task(a.execute(call(member, tab, ref, first)))
                try:
                    await asyncio.wait_for(entered.wait(), 3)
                    output = await b.execute(call(member, tab, ref, last))
                    content = cast(list[dict[str, object]], output["output"])
                    assert json.loads(str(content[0]["text"]))["ok"] is False
                    checks += 1
                finally:
                    release.set()
                    await pending
                output = await pending
                content = cast(list[dict[str, object]], output["output"])
                assert json.loads(str(content[0]["text"]))["ok"] is True
                output = await b.execute(call(member, tab, ref, last))
                content = cast(list[dict[str, object]], output["output"])
                assert json.loads(str(content[0]["text"]))["ok"] is True
                checks += 2
        return checks
    finally:
        await context.close()


async def creation(browser: Browser, origin: str, url: str, owned: bool, boundary: str) -> int:
    context = await browser.new_context(service_workers="block")
    witness = None if owned else await context.new_page()
    driver = PlaywrightBrowser(context, {origin}, owned_fixture_urls=frozenset({url}) if owned else None)
    entered, release, arrived, stop = (asyncio.Event() for _ in range(4))
    close_started, close_release = asyncio.Event(), asyncio.Event()
    close_calls = 0
    start = context.new_page
    created: Page | None = None
    navigations = 0

    async def new_page() -> Page:
        nonlocal created, navigations
        if boundary == "new_page":
            entered.set()
            await release.wait()
        page = await start()
        created = page
        arrived.set()
        goto = page.goto
        original_close = page.close
        if boundary in ("close", "failed_close"):

            async def close(*args: Any, **kwargs: Any) -> None:
                nonlocal close_calls
                close_calls += 1
                close_started.set()
                await close_release.wait()
                await original_close(*args, **kwargs)
                if boundary == "failed_close":
                    raise Error("Synthetic page close failure.")

            page.close = close

        async def navigate(*args: Any, **kwargs: Any) -> Any:
            nonlocal navigations
            navigations += 1
            entered.set()
            await release.wait()
            return await goto(*args, **kwargs)

        page.goto = navigate
        return page

    checks = 0
    with patch.object(context, "new_page", new_page):
        pending = asyncio.create_task(driver.new_tab({"url": url}, cancelled=stop.is_set))
        try:
            await asyncio.wait_for(entered.wait(), 3)
            stop.set()
            try:
                done, _ = await asyncio.wait({pending}, timeout=1)
                assert pending in done, "Stop must settle before the held close."
                await pending
            except (BrowserCancelledError, BrowserError):
                pass
            else:
                raise AssertionError("Stop failed to retire pending new_tab")
            assert navigations == (0 if boundary == "new_page" else 1)
            if boundary in ("close", "failed_close"):
                await asyncio.wait_for(close_started.wait(), 1)
                assert close_calls == 1
                assert created is not None and not created.is_closed()
                checks += 2
            elif boundary == "goto":
                assert created is not None
                if not created.is_closed():
                    await created.wait_for_event("close", timeout=3000)
            if witness:
                assert await witness.evaluate("() => 7") == 7
            try:
                await driver.state()
            except (BrowserError, RuntimeError):
                pass
            else:
                raise AssertionError("Stopped driver was reusable")
            checks += 4
        finally:
            close_release.set()
            release.set()
            await asyncio.gather(pending, return_exceptions=True)
            if not owned and boundary == "new_page":
                await asyncio.wait_for(arrived.wait(), 3)
                assert created is not None
                if not created.is_closed():
                    await created.wait_for_event("close", timeout=3000)
                assert len(context.pages) == 1
                checks += 1
            await context.close()
    return checks


async def failing_navigation(browser: Browser, origin: str, url: str, when: str, fail_close: bool) -> int:
    context = await browser.new_context(service_workers="block")
    driver = PlaywrightBrowser(context, {origin}, owned_fixture_urls=frozenset({url}))
    stop, closing, release = (asyncio.Event() for _ in range(3))
    real_close, real_page = context.close, context.new_page
    close_calls = 0

    async def page() -> Page:
        new_page = await real_page()

        async def goto(*args: Any, **kwargs: Any) -> None:
            del args, kwargs
            raise Error("Synthetic lost navigation reply")

        new_page.goto = goto
        return new_page

    async def close(*args: Any, **kwargs: Any) -> None:
        nonlocal close_calls
        close_calls += 1
        closing.set()
        await release.wait()
        await real_close(*args, **kwargs)
        if fail_close:
            raise Error("Synthetic failed context close")

    with patch.object(context, "new_page", page), patch.object(context, "close", close):
        pending = asyncio.create_task(driver.new_tab({"url": url}, cancelled=stop.is_set))
        try:
            await asyncio.wait_for(closing.wait(), 3)
            done, _ = await asyncio.wait({pending}, timeout=0.15)
            assert pending not in done
            assert close_calls == 1
            if when == "during":
                stop.set()
            else:
                release.set()
            done, _ = await asyncio.wait({pending}, timeout=1)
            assert pending in done, "Navigation Stop waited for held close."
            try:
                await pending
            except (BrowserCancelledError, BrowserError):
                pass
            else:
                raise AssertionError("A navigation failure must not complete.")
            try:
                await driver.state()
            except (BrowserError, RuntimeError):
                pass
            else:
                raise AssertionError("Failed navigation driver remained usable")
            return 4
        finally:
            release.set()
            await asyncio.gather(pending, return_exceptions=True)
            await real_close()


async def unsupported_roots(browser: Browser, origin: str) -> int:
    context = await browser.new_context(service_workers="block")
    driver = PlaywrightBrowser(context, {origin})
    try:
        await driver.new_tab({"url": origin + "/fixture"})
        tab = (await driver.state())["tabs"][0]["id"]
        page = context.pages[0]
        for path in ("/vector", "/data", "/fixture"):
            await page.goto(origin + path)
            if path == "/fixture":
                await page.evaluate("() => document.body.remove()")
            assert await page.evaluate("() => document.body === null"), path
            empty = {"version": 1, "text": "", "elements": [], "omitted": ["unsupported_root"]}
            assert await driver.read_page({"tab_id": tab, "filter": "all"}) == empty
            assert await driver.find({"tab_id": tab, "query": "Name"}) == empty
            assert await driver.get_page_text({"tab_id": tab}) == ""
            await page.goto(origin + "/fixture")
            usable = await driver.read_page({"tab_id": tab, "filter": "all"})
            assert not isinstance(usable, str)
            assert [item["label"] for item in usable["elements"]] == ["Name", "Room"]
        return 15
    finally:
        await context.close()


async def consumed_click(browser: Browser, origin: str, boundary: str) -> int:
    context = await browser.new_context(service_workers="block")
    close = context.close
    closes = 0
    clicks = 0
    disposals = 0
    hooked = False
    entered, release, disposed, stop = (asyncio.Event() for _ in range(4))
    pending: asyncio.Task[None] | None = None

    async def context_close(*args: Any, **kwargs: Any) -> None:
        nonlocal closes
        closes += 1
        await close(*args, **kwargs)

    context.close = context_close
    driver = PlaywrightBrowser(context, {origin})
    try:
        await driver.new_tab({"url": origin + "/fixture"})
        tab = (await driver.state())["tabs"][0]["id"]
        page = context.pages[0]
        await page.set_content(
            '<button onclick="this.dataset.clicked=String(Number(this.dataset.clicked||0)+1)">Save</button>'
            '<input aria-label="Name">'
        )
        report = await driver.read_page({"tab_id": tab, "filter": "all"})
        assert not isinstance(report, str)
        save = next(item["ref"] for item in report["elements"] if item["label"] == "Save")
        name = next(item["ref"] for item in report["elements"] if item["label"] == "Name")
        evaluate = page.evaluate

        async def checked(expression: str, arg: Any = None) -> Any:
            nonlocal hooked
            if isinstance(arg, dict) and cast(dict[str, object], arg).get("checkedNode") and not hooked:
                hooked = True
                handle = cast(ElementHandle, cast(dict[str, object], arg)["checkedNode"])
                click, dispose = handle.click, handle.dispose

                async def held_click(*args: Any, **kwargs: Any) -> None:
                    nonlocal clicks
                    clicks += 1
                    await click(*args, **kwargs)
                    if boundary == "click":
                        entered.set()
                        await release.wait()

                async def held_dispose() -> None:
                    nonlocal disposals
                    disposals += 1
                    if boundary != "check":
                        if boundary != "click":
                            entered.set()
                        await release.wait()
                    await dispose()
                    disposed.set()

                handle.click = held_click
                handle.dispose = held_dispose
                if boundary == "check":
                    entered.set()
                    await release.wait()
            return await evaluate(expression, cast(Any, arg))

        page.evaluate = checked
        pending = asyncio.create_task(driver.click({"tab_id": tab, "target": save}, cancelled=stop.is_set))
        await asyncio.wait_for(entered.wait(), 3)
        done, _ = await asyncio.wait({pending}, timeout=0.08)
        assert not done
        if boundary == "none":
            release.set()
            await pending
            try:
                await driver.click({"tab_id": tab, "target": save})
            except BrowserError:
                pass
            else:
                raise AssertionError("Consumed ref was reusable")
            await driver.type({"tab_id": tab, "target": name, "text": "still usable"})
            assert await page.locator("input").input_value() == "still usable"
        else:
            stop.set()
            done, _ = await asyncio.wait({pending}, timeout=1)
            assert pending in done, "Stop blocked on consumed handle disposal"
            try:
                await pending
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError("Stopped click succeeded")
            try:
                await driver.state()
            except (BrowserError, RuntimeError):
                pass
            else:
                raise AssertionError("Retired driver remained usable")
        assert clicks == (0 if boundary == "check" else 1)
        assert closes == 0
        assert await page.locator("button").get_attribute("data-clicked") == (None if boundary == "check" else "1")
        return 7 if boundary == "none" else 6
    finally:
        release.set()
        if pending:
            await asyncio.gather(pending, return_exceptions=True)
            await asyncio.wait_for(disposed.wait(), 3)
            assert disposals == 1
        await close()


async def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            try:
                checks = await unsupported_roots(browser, origin)
                for boundary in ("check", "click", "dispose", "none"):
                    checks += await consumed_click(browser, origin, boundary)
                for when in ("during", "none"):
                    for fail_close in (False, True):
                        checks += await failing_navigation(browser, origin, origin + "/fixture", when, fail_close)
                for owned in (False, True):
                    checks += await form(browser, origin, origin + "/fixture", owned)
                    for boundary in ("new_page", "goto") if owned else ("new_page", "goto", "close", "failed_close"):
                        checks += await creation(browser, origin, origin + "/fixture", owned, boundary)
            finally:
                await browser.close()
        print(json.dumps({"checks": checks, "api_calls": 0, "vendor_calls": 0}))
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


if __name__ == "__main__":
    asyncio.run(main())
