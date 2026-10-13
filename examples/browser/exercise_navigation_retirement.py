"""Failed/cancelled navigation ownership, using only local synthetic pages."""

from __future__ import annotations

import json
import asyncio
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import patch
from typing_extensions import override

from browser_driver import PlaywrightBrowser, origin
from playwright.async_api import Page, Browser, ElementHandle, async_playwright

from openai.lib.browser import BrowserError, BrowserCancelledError

EFFECTS: list[str] = []


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/commit":
            EFFECTS.append("commit")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b'<title>Fixture</title><p>Ready</p><button id="ready">Ready</button>')


async def check_new_tab(browser: Browser, url: str, owned: bool) -> str:
    context = await browser.new_context(service_workers="block")
    witness = None if owned else await context.new_page()
    urls = frozenset({url + "/a", url + "/commit"}) if owned else None
    driver = PlaywrightBrowser(context, {origin(url)}, owned_fixture_urls=urls)
    try:
        await driver.new_tab({"url": url + "/commit"}, cancelled=lambda: True)
    except BrowserCancelledError:
        pass
    else:
        raise AssertionError("new_tab admitted already cancelled navigation")
    assert not EFFECTS
    await driver.new_tab({"url": None})
    assert (await driver.state())["tabs"]
    start = context.new_page
    created: list[Page] = []

    async def broken_page() -> Page:
        page = await start()
        created.append(page)
        goto = page.goto

        async def broken_goto(target: str, **_kwargs: object) -> None:
            await goto(target, wait_until="domcontentloaded")
            raise RuntimeError("Synthetic failure after checked local GET")

        page.goto = broken_goto  # type: ignore[method-assign, assignment]
        return page

    with patch.object(context, "new_page", side_effect=broken_page):
        try:
            await driver.new_tab({"url": url + "/commit"})
        except (RuntimeError, BrowserError, BrowserCancelledError):
            pass
        else:
            raise AssertionError("new_tab did not report a failed local navigation")
    assert EFFECTS == ["commit"] and created[0].is_closed()
    try:
        await driver.new_tab({"url": url + "/commit"})
    except (RuntimeError, BrowserError, BrowserCancelledError):
        pass
    else:
        raise AssertionError("failed new_tab can duplicate its GET")
    assert EFFECTS == ["commit"]
    if witness:
        assert not witness.is_closed() and await witness.evaluate("() => 7") == 7
    else:
        assert not context.pages
    await context.close()
    EFFECTS.clear()
    return f"new_tab {owned}: stop and failed GET"


async def check_navigation(browser: Browser, url: str, operation: str) -> str:
    context = await browser.new_context(service_workers="block")
    driver = PlaywrightBrowser(context, {origin(url)}, owned_fixture_urls=frozenset({url + "/a", url + "/commit"}))
    await driver.new_tab({"url": url + "/a"})
    tab, page = driver.page(None)
    target = url + "/commit" if operation == "goto" else operation
    try:
        await driver.navigate({"tab_id": tab, "url": target}, cancelled=lambda: True)
    except BrowserCancelledError:
        pass
    else:
        raise AssertionError("owned navigation admitted already cancelled input")
    assert not page.is_closed() and not EFFECTS
    method = {"goto": "goto", "back": "go_back", "forward": "go_forward", "reload": "reload"}[operation]
    goto = page.goto
    stopped = False
    closed = asyncio.Event()

    def on_close(_page: Page) -> None:
        closed.set()

    page.on("close", on_close)

    async def commit_then_stop(*_args: object, **_kwargs: object) -> None:
        nonlocal stopped
        await goto(url + "/commit")
        stopped = True

    with patch.object(page, method, side_effect=commit_then_stop):
        try:
            await driver.navigate({"tab_id": tab, "url": target}, cancelled=lambda: stopped)
        except (RuntimeError, BrowserError, BrowserCancelledError):
            pass
        else:
            raise AssertionError("owned navigation did not retire after dispatched cancellation")
    assert EFFECTS == ["commit"]
    try:
        await driver.state()
    except (RuntimeError, BrowserError, BrowserCancelledError):
        pass
    else:
        raise AssertionError("owned driver survived uncertain navigation")
    await asyncio.wait_for(closed.wait(), 2)
    assert page.is_closed() and EFFECTS == ["commit"]
    await context.close()
    EFFECTS.clear()
    return f"owned {operation}: preabort reusable, effect then Stop retired"


async def check_preflight(browser: Browser, url: str, operation: str) -> str:
    context = await browser.new_context(service_workers="block")
    driver = PlaywrightBrowser(context, {origin(url)})
    await driver.new_tab({"url": url + "/a"})
    tab, page = driver.page(None)
    read = await driver.read_page({"tab_id": tab, "filter": "all"})
    assert not isinstance(read, str)
    assert any(element["label"] == "Ready" for element in read["elements"])
    handle = next(iter(driver._refs[tab].values()))[0]
    entered, released, stopped = asyncio.Event(), asyncio.Event(), asyncio.Event()
    dispose = handle.dispose

    async def held_dispose() -> None:
        entered.set()
        await released.wait()
        await dispose()

    target = url + "/commit" if operation == "goto" else operation
    with patch.object(handle, "dispose", side_effect=held_dispose):
        pending = asyncio.create_task(driver.navigate({"tab_id": tab, "url": target}, cancelled=stopped.is_set))
        try:
            await asyncio.wait_for(entered.wait(), 2)
            stopped.set()
            done, _ = await asyncio.wait({pending}, timeout=0.5)
            assert pending in done, "Stop must settle before held disposal is released"
            try:
                await pending
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError("navigation succeeded after Stop")
            assert not EFFECTS
            try:
                await driver.state()
            except (RuntimeError, BrowserError):
                pass
            else:
                raise AssertionError("driver admitted work after interrupted disposal")
        finally:
            released.set()
            await asyncio.gather(pending, return_exceptions=True)
    assert not EFFECTS and len(context.pages) == 1
    assert page.url == url + "/a" and await page.locator("#ready").text_content() == "Ready"
    await context.close()
    return f"borrowed {operation}: stopped before disposal, no late navigation"


async def check_scroll_cleanup(browser: Browser, url: str) -> str:
    context = await browser.new_context(service_workers="block")
    driver = PlaywrightBrowser(context, {origin(url)}, owned_fixture_urls=frozenset({url + "/a"}))
    await driver.new_tab({"url": url + "/a"})
    tab, _ = driver.page(None)
    entered, released, stopped = asyncio.Event(), asyncio.Event(), asyncio.Event()
    inputs: list[str] = []
    dispose = driver._dispose_refs

    async def owned_input(*_args: object, **_kwargs: object) -> None:
        inputs.append("scroll")

    async def held_dispose(previous: list[tuple[ElementHandle, object, int]]) -> None:
        entered.set()
        await released.wait()
        await dispose(previous)

    with (
        patch.object(driver, "_owned_action", side_effect=owned_input),
        patch.object(driver, "_dispose_refs", side_effect=held_dispose),
    ):
        assert driver.scroll_to is not None
        pending = asyncio.create_task(driver._scroll_to({"tab_id": tab, "target": "fixture"}, cancelled=stopped.is_set))
        try:
            await asyncio.wait_for(entered.wait(), 2)
            assert inputs == ["scroll"]
            stopped.set()
            done, _ = await asyncio.wait({pending}, timeout=0.65)
            assert pending in done, "Post-scroll Stop waited for reference disposal"
            try:
                await pending
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError("scroll_to returned success after Stop")
            try:
                await driver.state()
            except (RuntimeError, BrowserError):
                pass
            else:
                raise AssertionError("post-effect Stop reused the owned driver")
        finally:
            released.set()
            await asyncio.gather(pending, return_exceptions=True)
    assert driver._retirement
    await asyncio.wait_for(asyncio.shield(driver._retirement), 2)
    assert inputs == ["scroll"] and not context.pages and not EFFECTS
    return "owned scroll: admitted input once, Stop releases before dispose, owned retirement closes"


async def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"
    checks: list[str] = []
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            try:
                for operation in ("goto", "back"):
                    checks.append(await check_preflight(browser, url, operation))
                checks.append(await check_scroll_cleanup(browser, url))
                for owned in (False, True):
                    checks.append(await check_new_tab(browser, url, owned))
                for operation in ("goto", "back", "forward", "reload"):
                    checks.append(await check_navigation(browser, url, operation))
                print(json.dumps({"checks": checks, "api_calls": 0}))
            finally:
                await browser.close()
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


if __name__ == "__main__":
    asyncio.run(main())
