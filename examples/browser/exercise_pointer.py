"""Run against the local, fixed owned fixture. No model, account, or network provider."""

from __future__ import annotations

import os
import sys
import json
import base64
import asyncio
from typing import Any, Callable, Awaitable
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

from browser_driver import PlaywrightBrowser, BrowserCancelledError, origin, open_browser
from exercise_owned import approve, function
from playwright.async_api import Page, ElementHandle, async_playwright

from openai.lib.browser import BrowserError, AsyncBrowserToolset
from openai.lib.computer import ComputerUseError, AsyncComputerToolset
from openai.types.responses import ResponseComputerToolCall

CHECKS: list[str] = []


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_GET(self) -> None:
        if self.path not in {"/pointer", "/next"}:
            self.send_error(404)
            return
        body = Path(__file__).with_name("pointer-fixture.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


async def computer(
    tool: AsyncComputerToolset, *actions: dict[str, Any], cancelled: Callable[[], bool] | None = None
) -> Any:
    payload: dict[str, Any] = {
        "type": "computer_call",
        "id": "call_owned",
        "call_id": "fixture",
        "status": "completed",
        "pending_safety_checks": [],
        "actions": list(actions),
    }
    call = ResponseComputerToolCall(**payload)
    return await tool.execute(call, cancelled=cancelled)


async def denied(operation: Callable[[], Awaitable[object]]) -> None:
    try:
        await operation()
    except (BrowserError, RuntimeError):
        return
    raise AssertionError("Expected a scoped pointer refusal.")


async def read(page: Page) -> dict[str, Any]:
    return await page.evaluate("() => structuredClone(proof)")


def png(data: str) -> bytes:
    assert data.startswith("data:image/png;base64,")
    return base64.b64decode(data.split(",", 1)[1], validate=True)


async def record(page: Page) -> ElementHandle:
    handle = await page.query_selector("#record")
    assert handle is not None
    return handle


async def tests(url: str) -> None:
    urls = frozenset({url, url.rsplit("/", 1)[0] + "/next"})
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        assert driver.zoom is None
        original = await record(page)
        await denied(lambda: driver.owned_computer(original, cancelled=lambda: False))
        await denied(lambda: driver.screenshot({"tab_id": None}))
        CHECKS.append("no-pixel-permission-no-factory-no-capture")

    async with open_browser(url, owned_fixture_urls=urls, public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        original = await record(page)
        native = await driver.owned_computer(original, cancelled=lambda: False)
        second = await driver.owned_computer(original, cancelled=lambda: False)
        tool = AsyncComputerToolset(native)
        browser = AsyncBrowserToolset(driver, members=["zoom", "screenshot"])
        click = {"type": "click", "button": "left", "x": 114, "y": 102}
        await denied(lambda: computer(tool, click))
        image_calls: list[tuple[str, dict[str, object]]] = [
            ("screenshot", {"tab_id": None}),
            ("zoom", {"tab_id": None, "region": [50, 50, 260, 220]}),
        ]
        for member, args in image_calls:
            output = await browser.execute(function(member, args))
            blocks = output["output"]
            assert isinstance(blocks, list) and blocks[1]["type"] == "input_image"
            await denied(lambda: computer(tool, click))
        CHECKS.append("readonly-pixels-do-not-mint-native-permit")
        await computer(tool, {"type": "screenshot"})
        before = await read(page)
        await denied(lambda: computer(AsyncComputerToolset(second), click))
        assert await read(page) == before
        CHECKS.append("captures-only-arm-originating-adapter")
        for action in [
            {"type": "double_click", "x": 100, "y": 100},
            {"type": "click", "button": "wheel", "x": 100, "y": 100},
            {"type": "drag", "path": [{"x": 100, "y": 250}, {"x": 9000, "y": 260}]},
            {"type": "keypress", "keys": ["Control", "A"]},
            {"type": "type", "text": "no"},
            {"type": "scroll", "x": 100, "y": 100, "scroll_x": 0, "scroll_y": 1},
            {"type": "wait"},
            {"type": "click", "button": "left", "x": 110, "y": 100, "count": 2},
            {"type": "click", "button": "left", "x": 110, "y": 100, "click_count": 3},
            {"type": "move", "x": 110, "y": 100, "extra": True},
            {"type": "drag", "path": [{"x": 118, "y": 255}, {"x": 555, "y": 255, "count": 2}]},
        ]:
            await computer(tool, {"type": "screenshot"})
            before = await read(page)
            await denied(lambda action=action: computer(tool, action))
            assert await read(page) == before, action
        CHECKS.append("unsupported-and-extra-action-or-last-point-fields-refuse-before-any-input")
        await computer(tool, {"type": "screenshot"})
        await computer(tool, {"type": "move", "x": 110, "y": 100})
        assert await page.locator("#action").is_visible()
        await computer(tool, {"type": "click", "button": "left", "x": 110, "y": 100})
        before = await read(page)
        await denied(lambda: computer(tool, {"type": "keypress", "keys": ["Enter"], "count": 2}))
        assert await read(page) == before
        await computer(tool, {"type": "screenshot"})
        await computer(tool, {"type": "keypress", "keys": ["Enter"]})
        assert (await read(page))["result"] == ["menu"]
        await computer(tool, {"type": "keypress", "keys": ["Escape"]})
        assert not await page.locator("#action").is_visible()
        CHECKS.append("native-hover-click-focused-menu-enter-escape-with-new-screenshot")
        await computer(tool, {"type": "click", "button": "right", "x": 620, "y": 125})
        await computer(tool, {"type": "click", "button": "left", "x": 410, "y": 165})
        assert (await read(page))["result"] == ["menu", "context"]
        CHECKS.append("native-context-menu-and-pointer-selection")
        await computer(
            tool,
            {
                "type": "drag",
                "keys": ["Shift"],
                "path": [{"x": 118, "y": 255}, {"x": 140, "y": 255}, {"x": 555, "y": 255}, {"x": 565, "y": 256}],
            },
        )
        assert (await read(page))["result"][-1] == "dropped:card-A"
        CHECKS.append("native-shift-drag-real-drop-fixture-oracle")
        await computer(tool, {"type": "screenshot"})
        await page.evaluate("receipt.textContent='page changed'")
        before = await read(page)
        await denied(lambda: computer(tool, click))
        assert await read(page) == before
        CHECKS.append("stale-png-pre-effect-denial")
        await computer(tool, {"type": "screenshot"})
        await driver.invalidate_references()
        await denied(lambda: computer(tool, click))
        CHECKS.append("structured-handoff-generation-revokes-native-permit")

    # Full-page scan must fail even where rich reads would omit secret/unknown nodes.
    for content in [
        "<input value=PRIVATE>",
        "<input type=password value=PRIVATE>",
        "<input type=file>",
        "<textarea>PRIVATE</textarea>",
        "<select><option>PRIVATE</option></select>",
        "<span data-browser-private>PRIVATE</span>",
        "<iframe src=/next></iframe>",
        "<canvas></canvas>",
        "<video></video>",
        "<x-unknown></x-unknown>",
    ]:
        await capture_race(url, urls, content)
    async with open_browser(url, owned_fixture_urls=urls, public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        native = await driver.owned_computer(await record(page), cancelled=lambda: False)
        await page.evaluate("""() => {
          const fragment=document.createDocumentFragment();
          for(let i=0;i<2050;i++){const el=document.createElement('i');el.hidden=true;fragment.append(el)}
          document.body.append(fragment);
        }""")
        await denied(native.screenshot)
        CHECKS.append("hidden-inclusive-admission-budget-no-partial-image")

    for change in ("record", "resize", "scroll", "overlay", "cancel"):
        await preaction_change(url, urls, change)
    for change in ("replace", "cover", "lost", "cancel", "up-fails", "private"):
        await interrupted(url, urls, change)
    # Capture the already-transparent state, so PNG freshness alone cannot
    # refuse input on an invisible hit, its original record or its parent.
    for selector in ("#menuTrigger", "#record", "body"):
        async with open_browser(url, owned_fixture_urls=urls, public_viewports=frozenset({url})) as driver:
            _, page = driver.page(None)
            native = await driver.owned_computer(await record(page), cancelled=lambda: False)
            tool = AsyncComputerToolset(native)
            await page.locator(selector).evaluate("(el)=>el.style.opacity='0'")
            await computer(tool, {"type": "screenshot"})
            before = await read(page)
            await denied(lambda tool=tool: computer(tool, {"type": "click", "button": "left", "x": 110, "y": 100}))
            assert await read(page) == before
        CHECKS.append("already-transparent-before-capture-denied:" + selector)


async def capture_race(url: str, urls: frozenset[str], content: str) -> None:
    async with open_browser(url, owned_fixture_urls=urls, public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        native = await driver.owned_computer(await record(page), cancelled=lambda: False)
        original_capture = page.screenshot
        injected = False

        async def capture(**kwargs: Any) -> bytes:
            nonlocal injected
            result = await original_capture(**kwargs)
            if not injected:
                injected = True
                await page.evaluate("(html)=>document.body.insertAdjacentHTML('beforeend',html)", content)
            return result

        page.screenshot = capture
        await denied(native.screenshot)
        page.screenshot = original_capture
        await denied(lambda native=native: computer(AsyncComputerToolset(native), {"type": "move", "x": 100, "y": 100}))
    CHECKS.append("post-capture-denial:" + content.split(">")[0])


async def preaction_change(url: str, urls: frozenset[str], change: str) -> None:
    cancelled = False
    async with open_browser(url, owned_fixture_urls=urls, public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        native = await driver.owned_computer(await record(page), cancelled=lambda: cancelled)
        tool = AsyncComputerToolset(native)
        await computer(tool, {"type": "screenshot"})
        if change == "record":
            await page.evaluate(
                "document.querySelector('#record').replaceWith(document.querySelector('#record').cloneNode(true))"
            )
        elif change == "resize":
            await page.set_viewport_size({"width": 900, "height": 650})
        elif change == "scroll":
            await page.evaluate("window.scrollTo(0,100)")
        elif change == "overlay":
            await page.evaluate("""() => {
              const el=document.createElement('div');Object.assign(el.style,{position:'fixed',inset:0,background:'white',zIndex:9});document.body.append(el);
            }""")
        else:
            cancelled = True
        before = await read(page)
        await denied(lambda: computer(tool, {"type": "click", "button": "left", "x": 110, "y": 100}))
        assert await read(page) == before, change
    CHECKS.append("revoked-before-effects:" + change)


async def interrupted(url: str, urls: frozenset[str], change: str) -> None:
    cancelled = False
    async with open_browser(url, owned_fixture_urls=urls, public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        native = await driver.owned_computer(await record(page), cancelled=lambda: cancelled)
        tool = AsyncComputerToolset(native)
        await page.evaluate("(kind)=>proof.inject=kind", change)
        await computer(tool, {"type": "screenshot"})
        original_down, original_up, original_close = page.mouse.down, page.mouse.up, driver.context.close
        observed: list[dict[str, Any]] = []

        async def down(**kwargs: Any) -> None:
            nonlocal cancelled
            await original_down(**kwargs)
            observed.append(await read(page))
            if change == "private":
                await page.evaluate("zone.dataset.browserPrivate=''")
            if change == "lost":
                raise RuntimeError("Synthetic lost down reply")
            if change == "cancel":
                cancelled = True

        async def up(**kwargs: Any) -> None:
            if change == "up-fails":
                raise RuntimeError("Synthetic unknown up")
            await original_up(**kwargs)

        async def close(**kwargs: Any) -> None:
            assert driver._unusable
            if change != "up-fails":
                await page.mouse.move(850, 600)
                state = await read(page)
                assert state["events"][-1]["buttons"] == 0 and not state["events"][-1]["shift"]
                assert state["result"] == []
            await original_close(**kwargs)

        page.mouse.down = down
        page.mouse.up = up
        driver.context.close = close
        await denied(
            lambda: computer(
                tool,
                {
                    "type": "drag",
                    "keys": ["Shift"],
                    "path": [{"x": 118, "y": 255}, {"x": 140, "y": 255}, {"x": 555, "y": 255}],
                },
            )
        )
        assert observed and any(e["kind"] == "pointerdown" for e in observed[0]["events"])
        await denied(driver.state)
        await denied(native.screenshot)
    CHECKS.append("observed-down-retirement-release:" + change)


async def crops(url: str) -> None:
    for dpr in (1, 2):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True, timeout=15000)
            context = await browser.new_context(
                viewport={"width": 900, "height": 620},
                device_scale_factor=dpr,
                service_workers="block",
                accept_downloads=False,
            )
            driver = PlaywrightBrowser(
                context, {origin(url)}, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})
            )
            await context.route("**/*", driver.guard)
            await driver.new_tab({"url": url})
            _, page = driver.page(None)
            await page.evaluate("window.scrollTo(79,700)")
            view = await page.evaluate("() => [innerWidth,innerHeight,scrollX,scrollY,devicePixelRatio]")
            assert view == [900, 620, 79, 700, dpr], view
            native = await driver.owned_computer(await record(page), cancelled=lambda: False)
            tool = AsyncBrowserToolset(driver, members=["zoom"])
            result = await tool.execute(function("zoom", {"tab_id": None, "region": [58, 245, 261, 354]}))
            blocks = result["output"]
            assert isinstance(blocks, list) and len(blocks) == 2, blocks
            assert blocks[1]["type"] == "input_image"
            raw_url = blocks[1].get("image_url")
            assert isinstance(raw_url, str)
            data = png(raw_url)
            assert data[:8] == b"\x89PNG\r\n\x1a\n"
            assert [int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")] == [203, 109]
            assert await page.evaluate("() => [innerWidth,innerHeight,scrollX,scrollY,devicePixelRatio]") == view
            await denied(
                lambda native=native: computer(AsyncComputerToolset(native), {"type": "move", "x": 100, "y": 100})
            )
            # Test-only blank page decodes image pixels, outside the captured viewport.
            oracle = await driver.context.new_page()
            pixels = await oracle.evaluate(
                """async url => {
              const img=new Image(); img.src=url;await img.decode();
              const c=document.createElement('canvas');c.width=203;c.height=109;
              const ctx=c.getContext('2d');ctx.drawImage(img,0,0);
              return [[2,2],[201,2],[2,107],[201,107]].map(([x,y])=>Array.from(ctx.getImageData(x,y,1,1).data));
            }""",
                raw_url,
            )
            assert pixels == [[215, 21, 42, 255], [11, 97, 203, 255], [41, 163, 57, 255], [251, 181, 13, 255]]
            await oracle.close()
            await browser.close()
        CHECKS.append("scrolled-DPR-native-crop-dimensions-unchanged-full-view-and-asymmetric-colors:" + str(dpr))


async def busy_and_repeated_cancel(url: str) -> None:
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        original = await record(page)
        native = await driver.owned_computer(original, cancelled=lambda: False)
        other = await driver.owned_computer(original, cancelled=lambda: False)
        tool = AsyncComputerToolset(native)
        browser = AsyncBrowserToolset(driver, members=["read_page", "click"], confirm=approve)
        await page.evaluate("document.getElementById('record').dataset.recordId='fixture'")
        observed = await browser.execute(function("read_page", {"tab_id": None, "filter": "interactive"}))
        blocks = observed["output"]
        assert isinstance(blocks, list) and blocks[0]["type"] == "input_text"
        fields = json.loads(blocks[0]["text"])["result"]["elements"]
        old_ref = next(element["ref"] for element in fields if element["label"] == "Open menu")
        await computer(tool, {"type": "screenshot"})
        down_started, release_started, finish_release = asyncio.Event(), asyncio.Event(), asyncio.Event()
        real_down, real_up, real_close = page.mouse.down, page.mouse.up, driver.context.close

        async def down(**kwargs: Any) -> None:
            await real_down(**kwargs)
            assert any(e["kind"] == "pointerdown" for e in (await read(page))["events"])
            down_started.set()
            await asyncio.Event().wait()

        async def up(**kwargs: Any) -> None:
            release_started.set()
            await finish_release.wait()
            await real_up(**kwargs)

        async def close(**kwargs: Any) -> None:
            await page.mouse.move(850, 600)
            actual = await read(page)
            assert actual["events"][-1]["buttons"] == 0 and not actual["events"][-1]["shift"]
            assert actual["result"] == []
            await real_close(**kwargs)

        page.mouse.down, page.mouse.up, driver.context.close = down, up, close
        closed = asyncio.Event()
        page.on("close", lambda _page: closed.set())
        active = asyncio.create_task(
            computer(
                tool,
                {
                    "type": "drag",
                    "keys": ["Shift"],
                    "path": [{"x": 118, "y": 255}, {"x": 140, "y": 255}, {"x": 555, "y": 255}],
                },
            )
        )
        await asyncio.wait_for(down_started.wait(), 3)
        await denied(other.screenshot)
        await denied(lambda: driver.screenshot({"tab_id": None}))
        active.cancel()
        await asyncio.wait_for(release_started.wait(), 3)
        for _ in range(3):
            active.cancel()
            await asyncio.sleep(0)
        before = await read(page)
        await denied(lambda: browser.execute(function("read_page", {"tab_id": None, "filter": "interactive"})))
        await denied(lambda: browser.execute(function("click", {"tab_id": None, "target": old_ref})))
        assert await read(page) == before
        finish_release.set()
        try:
            await asyncio.wait_for(asyncio.shield(active), 1)
        except asyncio.CancelledError:
            pass
        else:
            raise AssertionError("Repeated task cancellation must survive pointer cleanup.")
        await denied(other.screenshot)
        await asyncio.wait_for(closed.wait(), 2)
        CHECKS.append("public-browser-refuses-during-held-release-after-repeated-cancel-other-adapter-cannot-capture")


async def cancelled_input(url: str, kind: str) -> None:
    stopped = asyncio.Event()
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        native = await driver.owned_computer(await record(page), cancelled=stopped.is_set)
        tool = AsyncComputerToolset(native)
        await computer(tool, {"type": "screenshot"})
        entered, release, drained = asyncio.Event(), asyncio.Event(), asyncio.Event()
        owner = page.keyboard if kind == "key" else page.mouse
        member = "down" if kind == "key" else kind
        original = getattr(owner, member)
        calls = 0

        async def held(*args: Any, **kwargs: Any) -> None:
            nonlocal calls
            calls += 1
            await original(*args, **kwargs)
            entered.set()
            await release.wait()
            drained.set()

        setattr(owner, member, held)

        async def run() -> str:
            try:
                await computer(
                    tool,
                    {
                        "type": "drag",
                        "keys": ["Shift"],
                        "path": [
                            {"x": 118, "y": 255},
                            {"x": 555, "y": 255},
                        ],
                    },
                )
                return "completed"
            except RuntimeError as error:
                return str(error)

        closed = asyncio.Event()
        page.on("close", lambda _page: closed.set())
        outcome = asyncio.create_task(run())
        try:
            await asyncio.wait_for(entered.wait(), 3)
            result = None
            stopped.set()
            try:
                result = await asyncio.wait_for(asyncio.shield(outcome), 7 if kind == "up" else 1)
            except asyncio.TimeoutError:
                result = "timeout"
            assert "outcome is unknown" in result
            expected = 2 if kind == "up" else 1
            assert calls == expected
            await denied(lambda: driver.state())
            await asyncio.wait_for(closed.wait(), 2)
            assert driver.context.pages == []
            release.set()
            await drained.wait()
            await asyncio.sleep(0.03)
            assert calls == expected, "Stopped gesture must not dispatch later input"
            CHECKS.append("native-stopped-unknown-no-later-input:" + kind)
        finally:
            release.set()
            await outcome


async def cancelled_second_click(url: str) -> None:
    stopped = asyncio.Event()
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        pointer = await driver.owned_browser(await record(page), cancelled=stopped.is_set)
        await pointer.screenshot({"tab_id": None})
        checked, allow_check, check_finished = asyncio.Event(), asyncio.Event(), asyncio.Event()
        releasing, allow_release = asyncio.Event(), asyncio.Event()
        downs = 0
        down = page.mouse.down

        async def mouse_down(*args: Any, **kwargs: Any) -> None:
            nonlocal downs
            downs += 1
            await down(*args, **kwargs)

        page.mouse.down = mouse_down
        key_up = page.keyboard.up

        async def keyboard_up(*args: Any, **kwargs: Any) -> None:
            releasing.set()
            await allow_release.wait()
            await key_up(*args, **kwargs)

        page.keyboard.up = keyboard_up
        make_handle = page.evaluate_handle

        async def evaluate_handle(*args: Any, **kwargs: Any) -> Any:
            handle = await make_handle(*args, **kwargs)
            evaluate = handle.evaluate

            async def recheck(*check_args: Any, **check_kwargs: Any) -> Any:
                result = await evaluate(*check_args, **check_kwargs)
                checked.set()
                await allow_check.wait()
                check_finished.set()
                return result

            handle.evaluate = recheck
            return handle

        page.evaluate_handle = evaluate_handle

        async def run() -> str:
            try:
                await pointer.click_at(
                    {"tab_id": None, "x": 118, "y": 255, "button": "left", "click_count": 2, "keys": ["Shift"]}
                )
                return "completed"
            except RuntimeError as error:
                return str(error)

        closed = asyncio.Event()
        page.on("close", lambda _page: closed.set())
        outcome = asyncio.create_task(run())
        try:
            await asyncio.wait_for(checked.wait(), 3)
            stopped.set()
            await asyncio.wait_for(releasing.wait(), 3)
            assert downs == 1
            allow_check.set()
            await check_finished.wait()
            await asyncio.sleep(0.03)
            assert downs == 1, "Stop during double-click revalidation must not dispatch a second down"
            assert len(driver.context.pages) == 1
            allow_release.set()
            assert "outcome is unknown" in await outcome
            await denied(lambda: driver.state())
            await asyncio.wait_for(closed.wait(), 2)
            assert driver.context.pages == []
            CHECKS.append("second-click-check-cannot-dispatch-during-stop-cleanup")
        finally:
            allow_check.set()
            allow_release.set()
            await outcome


async def cancelled_capture(url: str, kind: str) -> None:
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        stopped = asyncio.Event()
        native = (
            await driver.owned_computer(await record(page), cancelled=stopped.is_set)
            if kind in ("computer", "gesture")
            else None
        )
        point: dict[str, Any] = {}
        if kind == "gesture":
            assert native is not None
            point = await page.locator("#source").evaluate(
                """element => {
                  const r = element.getBoundingClientRect();
                  return {x: Math.floor(r.left + r.width / 2), y: Math.floor(r.top + r.height / 2)};
                }"""
            )
            await native.screenshot()
        moves = 0
        original_move = page.mouse.move

        async def move(*args: Any, **kwargs: Any) -> None:
            nonlocal moves
            moves += 1
            await original_move(*args, **kwargs)

        page.mouse.move = move
        entered, release, drained = asyncio.Event(), asyncio.Event(), asyncio.Event()
        original = page.screenshot

        async def capture(*args: Any, **kwargs: Any) -> bytes:
            entered.set()
            await release.wait()
            try:
                return await original(*args, **kwargs)
            finally:
                drained.set()

        page.screenshot = capture

        async def run() -> str:
            try:
                if kind == "gesture":
                    assert native is not None
                    await computer(AsyncComputerToolset(native), {"type": "move", **point})
                elif native is not None:
                    await native.screenshot()
                elif kind == "zoom":
                    assert driver.zoom is not None
                    tool = AsyncBrowserToolset(driver, members=["zoom"])
                    await tool.execute(
                        function("zoom", {"tab_id": None, "region": [0, 0, 100, 100]}), cancelled=stopped.is_set
                    )
                else:
                    await driver.screenshot({"tab_id": None}, cancelled=stopped.is_set)
                return "completed"
            except BrowserCancelledError:
                return "cancelled"
            except Exception as error:
                return type(error).__name__

        closed = asyncio.Event()
        page.on("close", lambda _page: closed.set())
        outcome = asyncio.create_task(run())
        try:
            await entered.wait()
            stopped.set()
            assert await asyncio.wait_for(asyncio.shield(outcome), 0.5) == "cancelled"
            assert moves == 0
            await denied(driver.state)
            await asyncio.wait_for(closed.wait(), 2)
            assert not driver.context.pages
            CHECKS.append(kind + "-capture-stops-and-closes-owned-context")
        finally:
            release.set()
            await drained.wait()
            await outcome
            page.screenshot = original
            page.mouse.move = original_move


async def fixture_url_admission() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            env={name: os.environ[name] for name in ("PATH", "HOME", "TMPDIR") if name in os.environ},
        )
        try:
            for url in (
                "https://fixture.invalid",
                "https://FIXTURE.invalid/",
                "https://fixture.invalid:443/",
                "https://fixture.invalid/page#section",
                "https://fixture.invalid/page#",
                "https://fixture.invalid/one/../page",
                "https://fixture.invalid/one/%2e%2e/page",
                "http://127.1/fixture",
            ):
                context = await browser.new_context(service_workers="block")
                try:
                    try:
                        PlaywrightBrowser(context, {origin(url)}, owned_fixture_urls=frozenset({url}))
                    except ValueError as error:
                        assert "exact installed HTTP(S) URLs" in str(error)
                    else:
                        raise AssertionError("Expected a noncanonical fixture URL to be refused.")
                    assert not context.pages
                finally:
                    await context.close()
            for url in (
                "https://fixture.invalid/",
                "https://fixture.invalid/page",
                "https://fixture.invalid/page?q=one%20two",
            ):
                context = await browser.new_context(service_workers="block")
                try:
                    PlaywrightBrowser(
                        context,
                        {origin(url)},
                        owned_fixture_urls=frozenset({url}),
                        public_values=frozenset({(url, "record", "field")}),
                        public_viewports=frozenset({url}),
                    )
                    assert not context.pages
                finally:
                    await context.close()
            CHECKS.append("fixture-url-admission-preserves-url-field-and-viewport-keys")
        finally:
            await browser.close()


async def bounded_pointer_stop(url: str) -> None:
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        original = await record(page)
        native = await driver.owned_computer(original, cancelled=lambda: False)
        other = await driver.owned_computer(original, cancelled=lambda: False)
        tool = AsyncComputerToolset(native)
        await native.screenshot()
        entered, release = asyncio.Event(), asyncio.Event()
        child: asyncio.Task[Any] | None = None
        real_evaluate, real_move = original.evaluate, page.mouse.move
        checks = 0
        moves: list[tuple[object, ...]] = []

        async def hold_child_check(*args: Any, **kwargs: Any) -> Any:
            nonlocal checks, child
            result = await real_evaluate(*args, **kwargs)
            checks += 1
            if checks == 2:
                child = asyncio.current_task()
                entered.set()
                await release.wait()
            return result

        async def move(*args: Any, **kwargs: Any) -> None:
            moves.append(args)
            await real_move(*args, **kwargs)

        original.evaluate, page.mouse.move = hold_child_check, move
        active = asyncio.create_task(computer(tool, {"type": "move", "x": 110, "y": 100}))
        try:
            await asyncio.wait_for(entered.wait(), 3)
            active.cancel()
            try:
                await asyncio.wait_for(asyncio.shield(active), 1)
            except asyncio.CancelledError:
                pass
            else:
                raise AssertionError("Pre-effect task cancellation was lost")
            assert moves == [] and not page.is_closed()
            await other.screenshot()
            release.set()
            assert child is not None
            await asyncio.wait_for(asyncio.gather(child, return_exceptions=True), 1)
            assert moves == [], "The cancelled child dispatched native input after admission reopened"
            assert not page.is_closed()
            CHECKS.append("pre-effect-child-revoked-before-reuse")
        finally:
            release.set()
            await asyncio.gather(active, return_exceptions=True)
            original.evaluate, page.mouse.move = real_evaluate, real_move

    stopped = asyncio.Event()
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        native = await driver.owned_computer(await record(page), cancelled=lambda: False)
        tool = AsyncComputerToolset(native)
        await native.screenshot()
        real_move, real_down = page.mouse.move, page.mouse.down
        moves = []

        async def track_move(*args: Any, **kwargs: Any) -> None:
            moves.append(args)
            await real_move(*args, **kwargs)

        async def stop_after_down(*args: Any, **kwargs: Any) -> None:
            await real_down(*args, **kwargs)
            stopped.set()

        page.mouse.move, page.mouse.down = track_move, stop_after_down
        closed = asyncio.Event()
        page.on("close", lambda _page: closed.set())
        await denied(
            lambda: computer(
                tool,
                {"type": "drag", "path": [{"x": 118, "y": 255}, {"x": 140, "y": 255}, {"x": 555, "y": 255}]},
                cancelled=stopped.is_set,
            )
        )
        assert stopped.is_set()
        assert moves == [(118, 255)], "Per-call Stop must prevent later drag steps"
        await denied(native.screenshot)
        await asyncio.wait_for(closed.wait(), 2)
        assert page.is_closed()
        CHECKS.append("per-call-drag-stop-retired-before-next-step")


async def pre_input_stop(url: str, boundary: str, cancellation: str) -> None:
    owner_stop, caller_stop = asyncio.Event(), asyncio.Event()
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        owned_record = await record(page)
        native = await driver.owned_computer(owned_record, cancelled=owner_stop.is_set)
        point = await page.locator("#source").evaluate(
            "(el) => { const r=el.getBoundingClientRect(); return {x:Math.floor(r.x+r.width/2), y:Math.floor(r.y+r.height/2)}; }"
        )
        await native.screenshot()
        entered, release = asyncio.Event(), asyncio.Event()
        moves = 0
        closes = 0
        real_move, real_close = page.mouse.move, driver.context.close

        async def move(*args: Any, **kwargs: Any) -> None:
            nonlocal moves
            moves += 1
            await real_move(*args, **kwargs)

        async def close(*args: Any, **kwargs: Any) -> None:
            nonlocal closes
            closes += 1
            await real_close(*args, **kwargs)

        page.mouse.move, driver.context.close = move, close
        if boundary == "record check":
            evaluate = owned_record.evaluate

            async def check(*args: Any, **kwargs: Any) -> Any:
                entered.set()
                await release.wait()
                return await evaluate(*args, **kwargs)

            owned_record.evaluate = check
        else:
            invalidate = driver.invalidate_references

            async def held_invalidation() -> None:
                await invalidate()
                entered.set()
                await release.wait()

            driver.invalidate_references = held_invalidation
        active = asyncio.create_task(
            computer(AsyncComputerToolset(native), {"type": "move", **point}, cancelled=caller_stop.is_set)
        )
        try:
            await asyncio.wait_for(entered.wait(), 2)
            (owner_stop if cancellation == "owner" else caller_stop).set()
            done, _ = await asyncio.wait({active}, timeout=0.85)
            assert active in done, f"Stop retained pre-input {boundary}"
            try:
                await active
            except (BrowserCancelledError, ComputerUseError) as error:
                if cancellation == "caller":
                    assert isinstance(error, ComputerUseError) and "cancelled" in str(error)
                else:
                    assert isinstance(error, BrowserCancelledError)
            else:
                raise AssertionError("Interrupted pointer preflight succeeded")
            assert moves == 0
            await denied(driver.state)
            await asyncio.sleep(0.07)
            assert closes == 1
            release.set()
            await asyncio.sleep(0.07)
            assert moves == 0
            CHECKS.append(f"pre-input:{boundary}:{cancellation}:no-input-retired")
        finally:
            release.set()
            await asyncio.gather(active, return_exceptions=True)
            driver.context.close = real_close


async def retirement_close(url: str, fail_close: bool, when: str) -> None:
    stopped = asyncio.Event()
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        native = await driver.owned_computer(await record(page), cancelled=lambda: False)
        tool = AsyncComputerToolset(native)
        await native.screenshot()
        real_down, real_up, real_close = page.mouse.down, page.keyboard.up, driver.context.close
        closing, release, settled = (asyncio.Event() for _ in range(3))
        calls = 0
        neutral: dict[str, Any] = {}

        async def down(*args: Any, **kwargs: Any) -> None:
            await real_down(*args, **kwargs)
            if when == "before":
                stopped.set()
            elif when == "task":
                active.cancel("synthetic pointer cancellation")
                await asyncio.sleep(0)
            else:
                raise RuntimeError("Synthetic lost input reply")

        async def up(*args: Any, **kwargs: Any) -> None:
            await real_up(*args, **kwargs)
            if when == "cleanup":
                active.cancel("synthetic release cancellation")

        async def close(*args: Any, **kwargs: Any) -> None:
            nonlocal calls, neutral
            calls += 1
            assert driver._unusable
            await page.mouse.move(850, 600)
            proof = await read(page)
            neutral = proof["events"][-1]
            closing.set()
            await release.wait()
            try:
                await real_close(*args, **kwargs)
                if fail_close:
                    raise RuntimeError("Synthetic close failure")
            finally:
                settled.set()

        page.mouse.down, page.keyboard.up, driver.context.close = down, up, close
        active = asyncio.create_task(
            computer(
                tool,
                {"type": "drag", "keys": ["Shift"], "path": [{"x": 118, "y": 255}, {"x": 555, "y": 255}]},
                cancelled=stopped.is_set,
            )
        )
        try:
            await asyncio.wait_for(closing.wait(), 3)
            assert neutral["buttons"] == 0 and not neutral["shift"]
            assert calls == 1
            if when in ("during", "none"):
                done, _ = await asyncio.wait({active}, timeout=0.15)
                assert active not in done, "Normal failures must join owned cleanup until Stop."
            if when == "during":
                stopped.set()
            if when == "none":
                release.set()
            done, _ = await asyncio.wait({active}, timeout=1)
            assert active in done, "Stop must return before held close."
            try:
                await active
            except asyncio.CancelledError:
                assert when in ("task", "cleanup")
                assert active.cancelled() and driver._unusable
            except ComputerUseError as error:
                assert when in ("before", "during")
                assert str(error) == "Computer run was cancelled"
                assert driver._unusable
            except RuntimeError as error:
                assert when == "none"
                assert str(error) == "Owned native input outcome is unknown; context retired."
                assert driver._unusable
            else:
                raise AssertionError("Expected SDK cancellation or uncertain native input")
            await denied(driver.state)
            CHECKS.append(f"pointer-retirement:{when}:{fail_close}")
        finally:
            release.set()
            await asyncio.gather(active, return_exceptions=True)
            await asyncio.wait_for(settled.wait(), 3)
            page.keyboard.up = real_up
            driver.context.close = real_close


async def multi_click_cleanup(url: str, boundary: str, cancellation: str) -> None:
    owner_stop, caller_stop = asyncio.Event(), asyncio.Event()
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        pointer = await driver.owned_browser(await record(page), cancelled=owner_stop.is_set)
        await pointer.screenshot({"tab_id": None})
        checking, allow_check, disposing, allow_dispose, disposed = (asyncio.Event() for _ in range(5))
        real_down, real_close, make_handle = page.mouse.down, driver.context.close, page.evaluate_handle
        downs = closes = disposals = 0

        async def close(*args: Any, **kwargs: Any) -> None:
            nonlocal closes
            closes += 1
            await real_close(*args, **kwargs)

        async def mouse_down(*args: Any, **kwargs: Any) -> None:
            nonlocal downs
            downs += 1
            await real_down(*args, **kwargs)

        async def evaluate_handle(*args: Any, **kwargs: Any) -> Any:
            handle = await make_handle(*args, **kwargs)
            real_evaluate, real_dispose = handle.evaluate, handle.dispose

            async def recheck(*check_args: Any, **check_kwargs: Any) -> Any:
                accepted = await real_evaluate(*check_args, **check_kwargs)
                checking.set()
                if boundary == "check":
                    await allow_check.wait()
                return accepted

            async def dispose() -> None:
                nonlocal disposals
                disposals += 1
                disposing.set()
                await allow_dispose.wait()
                try:
                    await real_dispose()
                finally:
                    disposed.set()

            handle.evaluate, handle.dispose = recheck, dispose
            return handle

        page.mouse.down, driver.context.close, page.evaluate_handle = mouse_down, close, evaluate_handle

        async def run() -> str:
            try:
                await pointer.click_at(
                    {"tab_id": None, "x": 118, "y": 255, "button": "left", "click_count": 2, "keys": ["Shift"]},
                    cancelled=caller_stop.is_set,
                )
                return "completed"
            except RuntimeError as error:
                return str(error)

        active = asyncio.create_task(run())
        try:
            await asyncio.wait_for((checking if boundary == "check" else disposing).wait(), 2)
            if cancellation == "none":
                done, _ = await asyncio.wait({active}, timeout=0.12)
                assert not done and downs == 2 and closes == 0, "Normal success still owns target disposal"
                allow_dispose.set()
                assert await active == "completed"
                await driver.state()
                assert not driver._unusable
            else:
                (owner_stop if cancellation == "owner" else caller_stop).set()
                done, _ = await asyncio.wait({active}, timeout=0.85)
                assert active in done, "Stop retained multi-click target cleanup"
                assert await active == "Owned native input outcome is unknown; context retired."
                assert downs == (1 if boundary == "check" else 2)
                assert driver._unusable
                await denied(driver.state)
                assert closes == 1
                allow_check.set()
                allow_dispose.set()
                await asyncio.wait_for(disposed.wait(), 2)
                assert downs == (1 if boundary == "check" else 2), "No late input after Stop"
            await asyncio.wait_for(disposed.wait(), 2)
            assert disposals == 1
            CHECKS.append(f"multi-click-cleanup:{boundary}:{cancellation}:{downs}:{closes}:{disposals}")
        finally:
            allow_check.set()
            allow_dispose.set()
            await asyncio.gather(active, return_exceptions=True)
            driver.context.close = real_close


async def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/pointer"
        if "--retirement-close" in sys.argv:
            for boundary, cancellation in (
                ("check", "owner"),
                ("check", "caller"),
                ("dispose", "owner"),
                ("dispose", "caller"),
                ("dispose", "none"),
            ):
                await multi_click_cleanup(url, boundary, cancellation)
            for boundary in ("record check", "reference invalidation"):
                for cancellation in ("owner", "caller"):
                    await pre_input_stop(url, boundary, cancellation)
            for when in ("before", "during", "none", "task", "cleanup"):
                for fail_close in (False, True):
                    await retirement_close(url, fail_close, when)
            print(json.dumps({"checks": CHECKS, "api_requests": 0}))
            return
        await bounded_pointer_stop(url)
        if "--bounded-pointer-stop" in sys.argv:
            print(json.dumps({"checks": CHECKS, "api_requests": 0}, indent=2))
            return
        await fixture_url_admission()
        await cancelled_second_click(url)
        for kind in ("move", "down", "key", "up"):
            await cancelled_input(url, kind)
        for kind in ("browser", "zoom", "computer", "gesture"):
            await cancelled_capture(url, kind)
        await tests(url)
        await crops(url)
        await busy_and_repeated_cancel(url)
        print(json.dumps({"checks": CHECKS, "api_requests": 0}, indent=2))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    asyncio.run(main())
