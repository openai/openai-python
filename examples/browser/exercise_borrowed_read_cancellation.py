"""Local controlled reads: Stop must not depend on a stalled renderer."""

from __future__ import annotations

import sys
import json
import asyncio
from typing import Any, Callable, Awaitable, cast
from threading import Thread
from contextlib import ExitStack
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from browser_driver import PlaywrightBrowser, origin
from exercise_owned import Fixture
from playwright.async_api import Error, Mouse, Dialog, Browser, Locator, Download, JSHandle, Keyboard, async_playwright

from openai.lib.browser import BrowserError, BrowserCancelledError


async def check_read(browser: Browser, operation: str, boundary: str) -> str:
    context = await browser.new_context()
    driver = PlaywrightBrowser(context, set())
    page = await context.new_page()
    await page.set_content("<title>Held read</title><p>Fixture text</p><button>Save</button>")
    tab, _ = driver.page(None)
    before = await driver.read_page({"tab_id": tab, "filter": "all"})
    assert not isinstance(before, str)
    assert any(item["label"] == "Save" for item in before["elements"])
    disposed, disposals = asyncio.Event(), 0
    entered, release = asyncio.Event(), asyncio.Event()
    stop = False
    evaluate, native_scan, capture = page.evaluate, page.evaluate_handle, page.screenshot
    with ExitStack() as mocks:
        if boundary == "title":
            ((handle, _, _),) = driver._refs[tab].values()
            native_dispose = handle.dispose

            async def dispose_ref() -> None:
                nonlocal disposals
                await native_dispose()
                disposals += 1
                disposed.set()

            mocks.enter_context(patch.object(handle, "dispose", side_effect=dispose_ref))

        async def held_title(expression: str, arg: Any = None) -> Any:
            entered.set()
            await release.wait()
            return await evaluate(expression, arg)

        async def held_capture(**kwargs: Any) -> bytes:
            entered.set()
            await release.wait()
            return await capture(**kwargs)

        async def held_scan(expression: str, arg: Any = None) -> JSHandle:
            scan = await native_scan(expression, arg)
            if boundary == "scanner":
                entered.set()
                await release.wait()
            elif boundary == "property":
                get_property = scan.get_property

                async def held_property(name: str) -> JSHandle:
                    if name == "report":
                        entered.set()
                        await release.wait()
                    return await get_property(name)

                mocks.enter_context(patch.object(scan, "get_property", side_effect=held_property))
            else:
                dispose = scan.dispose

                async def held_dispose() -> None:
                    entered.set()
                    await release.wait()
                    await dispose()

                mocks.enter_context(patch.object(scan, "dispose", side_effect=held_dispose))
            return scan

        if boundary == "title":
            mocks.enter_context(patch.object(page, "evaluate", side_effect=held_title))
        elif boundary == "capture":
            mocks.enter_context(patch.object(page, "screenshot", side_effect=held_capture))
        else:
            mocks.enter_context(patch.object(page, "evaluate_handle", side_effect=held_scan))

        async def act() -> None:
            if operation == "state":
                await driver.state(cancelled=lambda: stop)
            elif operation == "read_page":
                await driver.read_page({"tab_id": tab, "filter": "all"}, cancelled=lambda: stop)
            elif operation == "get_page_text":
                await driver.get_page_text({"tab_id": tab}, cancelled=lambda: stop)
            elif operation == "screenshot":
                await driver.screenshot({"tab_id": tab}, cancelled=lambda: stop)
            else:
                await driver.find({"tab_id": tab, "query": "Save"}, cancelled=lambda: stop)

        reading = asyncio.create_task(act())
        try:
            await asyncio.wait_for(entered.wait(), 3)
            stop = True
            try:
                await asyncio.wait_for(asyncio.shield(reading), 0.5)
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError(f"{boundary} read survived cancellation")
            try:
                await driver.state()
            except RuntimeError:
                pass
            else:
                raise AssertionError("cancelled driver can publish a new observation")
            assert not page.is_closed()
            if boundary == "title":
                await asyncio.wait_for(disposed.wait(), 0.5)
                assert disposals == 1
        finally:
            release.set()
            await asyncio.gather(reading, return_exceptions=True)
            # Let the held native promise settle before removing its patches.
            await asyncio.sleep(0.03)
    try:
        await driver.state()
    except RuntimeError:
        pass
    else:
        raise AssertionError("late result revived the retired driver")
    assert await page.evaluate("() => document.querySelector('button').textContent") == "Save"
    await context.close()
    return f"{operation} held at {boundary}: promptly retired, caller retains context"


async def owned_event(browser: Browser, event: str) -> str:
    context, caller = await browser.new_context(), await browser.new_context()
    caller_page = await caller.new_page()
    url = "https://fixture.invalid/"
    driver = PlaywrightBrowser(context, {origin(url)}, owned_fixture_urls=frozenset({url}))
    page = await context.new_page()
    tab, _ = driver.page(None)

    class Event:
        type = "confirm"
        fail = False

        async def dismiss(self) -> None:
            if self.fail:
                raise Error("Fixture event cleanup failed")

        async def cancel(self) -> None:
            await self.dismiss()

    observation = Event()

    async def handle() -> None:
        if event == "dialog":
            await driver._dismiss(cast(Dialog, observation), tab)
        else:
            await driver._download(cast(Download, observation), tab)

    try:
        await handle()
        result = await driver.state()
        assert "observation" in result
        assert any(
            change["type"] == ("dialog_dismissed" if event == "dialog" else "download")
            for change in result["observation"]["changes"]
        )
        observation.fail = True
        await handle()
        assert page.is_closed()
        assert not caller_page.is_closed()
        try:
            await driver.state()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Unconfirmed owned event cleanup left driver usable")
    finally:
        await caller.close()
        await context.close()
    return f"owned {event}: success reported, unconfirmed cleanup closes only owned context"


async def owned_read(browser: Browser, operation: str, url: str) -> str:
    context = await browser.new_context()
    driver = PlaywrightBrowser(context, {origin(url)}, owned_fixture_urls=frozenset({url}))
    await driver.new_tab({"url": url})
    tab, page = driver.page(None)
    before = await driver.read_page({"tab_id": tab, "filter": "all"})
    assert not isinstance(before, str)
    assert any(item["label"] == "Confirm" for item in before["elements"])
    try:
        await driver.state(cancelled=lambda: True)
    except BrowserCancelledError:
        pass
    else:
        raise AssertionError("Pre-aborted state was admitted")
    assert not page.is_closed()
    entered, release = asyncio.Event(), asyncio.Event()
    stop = False
    frame = page.main_frame
    native_locator = frame.locator
    with ExitStack() as mocks:

        def held_locator(*args: Any, **kwargs: Any) -> Locator:
            locator = native_locator(*args, **kwargs)
            native_scan = locator.evaluate_handle

            async def held_scan(expression: str, arg: Any = None, *, timeout: float | None = None) -> JSHandle:
                entered.set()
                await release.wait()
                return await native_scan(expression, arg, timeout=timeout)

            mocks.enter_context(patch.object(locator, "evaluate_handle", side_effect=held_scan))
            return locator

        mocks.enter_context(patch.object(frame, "locator", side_effect=held_locator))

        async def act() -> None:
            if operation == "read_page":
                await driver.read_page({"tab_id": tab, "filter": "all"}, cancelled=lambda: stop)
            elif operation == "get_page_text":
                await driver.get_page_text({"tab_id": tab}, cancelled=lambda: stop)
            elif operation == "find":
                await driver.find({"tab_id": tab, "query": "Confirm"}, cancelled=lambda: stop)
            else:
                scoped = driver.read_page_scoped
                assert scoped is not None
                await scoped({"tab_id": tab, "filter": "all", "root": None, "depth": 1}, cancelled=lambda: stop)

        closed = asyncio.Event()
        context.once("close", lambda _: closed.set())
        task = asyncio.create_task(act())
        try:
            await asyncio.wait_for(entered.wait(), 3)
            stop = True
            try:
                await asyncio.wait_for(asyncio.shield(task), 0.7)
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError("Owned read survived cancellation")
            try:
                await driver.state()
            except RuntimeError:
                pass
            else:
                raise AssertionError("Cancelled owner returned state")
            await asyncio.wait_for(closed.wait(), 3)
            assert page.is_closed()
        finally:
            release.set()
            await asyncio.gather(task, return_exceptions=True)
            await asyncio.sleep(0.03)
    try:
        await driver.state()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Late owned read revived refs")
    return f"owned {operation}: read cancellation closes delegated context, no late ref admission"


async def borrowed_budgets(browser: Browser) -> list[str]:
    checks: list[str] = []
    for title, expected in (("😺" * 400, "😺" * 256), ("x" * 1023 + "😺", "x" * 1023)):
        context = await browser.new_context()
        driver = PlaywrightBrowser(context, set())
        page = await context.new_page()
        await page.set_content("<p>Visible</p><button>Save</button>")
        await page.evaluate("(value) => { document.title=value; }", title)
        state = await driver.state()
        assert state["tabs"][0]["title"] == expected
        assert len(state["tabs"][0]["title"].encode()) <= 1024
        await context.close()
        checks.append("borrowed normal multibyte title bounded without splitting character")
    for kind in ("text", "report"):
        context = await browser.new_context()
        driver = PlaywrightBrowser(context, set())
        page = await context.new_page()
        await page.set_content("<p>Visible</p><button>Save</button>")
        tab, _ = driver.page(None)
        before = await driver.read_page({"tab_id": tab, "filter": "all"})
        assert not isinstance(before, str)
        ref = next(item["ref"] for item in before["elements"] if item["label"] == "Save")
        native_scan = page.evaluate_handle
        properties: list[str] = []
        with ExitStack() as mocks:

            async def oversized(
                _expression: str,
                _arg: Any = None,
                *,
                native_scan: Callable[..., Awaitable[JSHandle]] = native_scan,
                kind: str = kind,
                properties: list[str] = properties,
            ) -> JSHandle:
                handle = await native_scan(
                    """value => ({
                    report:{version:1, text:value==='text'?'z'.repeat(16385):'', elements:[], omitted:[],
                      ...(value==='report'?{extra:'z'.repeat(65537)}:{})},
                    targets:[],nextRef:1000
                })""",
                    kind,
                )
                native_property = handle.get_property

                async def counted(name: str) -> JSHandle:
                    properties.append(name)
                    return await native_property(name)

                mocks.enter_context(patch.object(handle, "get_property", side_effect=counted))
                return handle

            mocks.enter_context(patch.object(page, "evaluate_handle", side_effect=oversized))
            try:
                await driver.read_page({"tab_id": tab, "filter": "all"})
            except BrowserError as error:
                assert "report budget" in str(error)
            else:
                raise AssertionError("An oversized report passed host admission")
            assert properties == ["report"]
        try:
            await driver.click({"tab_id": tab, "target": ref})
        except BrowserError:
            pass
        else:
            raise AssertionError("Old ref survived a rejected fresh report")
        assert not page.is_closed()
        after = await driver.read_page({"tab_id": tab, "filter": "all"})
        assert not isinstance(after, str)
        assert any(item["label"] == "Save" for item in after["elements"])
        await context.close()
        checks.append(f"borrowed {kind} refused before target admission, fresh report usable")
    return checks


async def check_inputs(browser: Browser) -> list[str]:
    checks: list[str] = []
    for kind in ("type", "key", "scroll"):
        context = await browser.new_context()
        try:
            driver = PlaywrightBrowser(context, set())
            page = await context.new_page()
            await page.set_content("<title>Local input</title><label>Note<input></label>")
            tab, _ = driver.page(None)
            await page.locator("input").focus()
            stop, entered, release, settled = (asyncio.Event() for _ in range(4))
            dispatched = 0
            owner: Keyboard | Mouse
            if kind == "type":
                owner, member = page.keyboard, "insert_text"
            elif kind == "key":
                owner, member = page.keyboard, "press"
            else:
                owner, member = page.mouse, "wheel"
            native = getattr(owner, member)

            async def held(
                *args: Any,
                entered: asyncio.Event = entered,
                release: asyncio.Event = release,
                settled: asyncio.Event = settled,
                native: Any = native,
                **kwargs: Any,
            ) -> None:
                nonlocal dispatched
                dispatched += 1
                entered.set()
                try:
                    await release.wait()
                    await native(*args, **kwargs)
                    raise RuntimeError("Local late input result")
                finally:
                    settled.set()

            with patch.object(owner, member, side_effect=held):
                if kind == "type":
                    operation = driver.type({"tab_id": tab, "target": None, "text": "hello"}, cancelled=stop.is_set)
                elif kind == "key":
                    operation = driver._key({"tab_id": tab, "keys": ["A"]}, cancelled=stop.is_set)
                else:
                    operation = driver._scroll(
                        {"tab_id": tab, "direction": "down", "amount": 50}, cancelled=stop.is_set
                    )
                active = asyncio.create_task(operation)
                try:
                    await entered.wait()
                    stop.set()
                    try:
                        await asyncio.wait_for(asyncio.shield(active), timeout=0.7)
                    except BrowserCancelledError:
                        pass
                    except asyncio.TimeoutError:
                        raise AssertionError(f"{kind} Stop remained blocked on native input") from None
                    else:
                        raise AssertionError(f"{kind} did not report cancellation")
                    assert dispatched == 1
                    try:
                        await driver.state()
                    except RuntimeError as exc:
                        assert "retired" in str(exc)
                    else:
                        raise AssertionError(f"{kind} accepted work after Stop")
                    assert not page.is_closed()
                finally:
                    release.set()
                    await settled.wait()
                    await asyncio.gather(active, return_exceptions=True)
            assert await page.title() == "Local input"
            checks.append(f"{kind}: prompt Stop, observed late input, retained caller context")
        finally:
            await context.close()
    return checks


async def check_string_iteration(browser: Browser) -> str:
    context = await browser.new_context()
    try:
        driver = PlaywrightBrowser(context, set())
        page = await context.new_page()
        await page.set_content("<p>Iterator target é😀漢</p><button>Iterator target é😀漢</button>")
        tab, _ = driver.page(None)
        await page.evaluate(r"""() => {
            const original = String.prototype[Symbol.iterator];
            window.iteratorCalls = 0;
            const label = 'Iterator target é😀漢\uD800';
            for (const element of document.querySelectorAll('p, button')) {
                element.textContent = label;
            }
            Object.defineProperty(String.prototype, label.length, {
                get() {
                    window.iteratorCalls += 1;
                    throw new Error('Page-owned out-of-bounds string getter reached');
                },
            });
            String.prototype[Symbol.iterator] = function () {
                if (String(this).includes('Iterator target')) {
                    window.iteratorCalls += 1;
                    throw new Error('Page-owned string iteration reached');
                }
                return original.call(this);
            };
        }""")
        read = await driver.read_page({"tab_id": tab, "filter": "all"})
        found = await driver.find({"tab_id": tab, "query": "Iterator target"})
        text = await driver.get_page_text({"tab_id": tab})
        for value in (read, found, text):
            assert "Iterator target é😀漢" in json.dumps(value, ensure_ascii=False)
        assert await page.evaluate("() => window.iteratorCalls") == 0
        return "borrowed reads preserve Unicode without invoking page-owned string iterators"
    finally:
        await context.close()


async def main() -> None:
    checks: list[str] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            checks.extend(await check_inputs(browser))
            if "--input-only" in sys.argv:
                print(json.dumps({"checks": checks, "api_calls": 0}))
                return
            checks.append(await check_string_iteration(browser))
            for operation, boundary in (
                ("state", "title"),
                ("read_page", "scanner"),
                ("get_page_text", "property"),
                ("find", "disposal"),
                ("screenshot", "capture"),
            ):
                checks.append(await check_read(browser, operation, boundary))
            for event in ("dialog", "download"):
                checks.append(await owned_event(browser, event))
            server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for operation in ("read_page", "get_page_text", "find", "read_page_scoped"):
                    checks.append(
                        await owned_read(browser, operation, f"http://127.0.0.1:{server.server_port}/fixture")
                    )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
            checks.extend(await borrowed_budgets(browser))
            print(json.dumps({"checks": checks, "api_calls": 0}))
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
