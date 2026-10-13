"""Exercise optional pointer tools with the real SDK and a fixed local canvas."""

from __future__ import annotations

import json
import asyncio
from typing import Any, Callable, AsyncGenerator
from pathlib import Path
from threading import Thread
from contextlib import asynccontextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import patch
from typing_extensions import override

from browser_driver import PlaywrightBrowser, open_browser
from exercise_owned import approve, function
from playwright.async_api import Page

from openai.lib.browser import AsyncBrowserToolset, BrowserCancelledError


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_GET(self) -> None:
        if self.path != "/canvas":
            self.send_error(404)
            return
        body = Path(__file__).with_name("capabilities-fixture.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@asynccontextmanager
async def session(url: str) -> AsyncGenerator[tuple[PlaywrightBrowser, Page, AsyncBrowserToolset], None]:
    async with open_browser(url, owned_fixture_urls=frozenset({url}), public_viewports=frozenset({url})) as driver:
        _, page = driver.page(None)
        record = await page.query_selector("#workspace")
        canvas = await page.query_selector("#board")
        assert record is not None and canvas is not None
        canvases = [canvas]
        pointer = await driver.owned_browser(record, cancelled=lambda: False, canvases=canvases)
        canvases.clear()
        tool = AsyncBrowserToolset(
            pointer, members=["screenshot", "click_at", "drag_path", "hold_keys"], confirm=approve
        )
        yield driver, page, tool


async def execute(
    tool: AsyncBrowserToolset, member: str, args: dict[str, Any], cancelled: Callable[[], bool] | None = None
) -> dict[str, Any]:
    response = await tool.execute(function(member, args), cancelled=cancelled)
    content = response["output"]
    assert isinstance(content, list) and content[0]["type"] == "input_text"
    result: dict[str, Any] = json.loads(content[0]["text"])
    return result


async def tests(url: str) -> None:
    async with session(url) as (driver, page, tool):
        screenshot = page.screenshot
        entered, release, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
        closed = asyncio.Event()
        driver.context.on("close", lambda _context: closed.set())

        async def held(*args: Any, **kwargs: Any) -> bytes:
            image = await screenshot(*args, **kwargs)
            entered.set()
            await release.wait()
            return image

        with patch.object(page, "screenshot", held):
            pending = asyncio.create_task(execute(tool, "screenshot", {"tab_id": None}, cancelled.is_set))
            await entered.wait()
            cancelled.set()
            release.set()
            try:
                await pending
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError("A cancelled capture succeeded.")
        action: dict[str, Any] = {"tab_id": None, "x": 20, "y": 20, "button": "left", "click_count": 1, "keys": []}
        assert driver._unusable
        for member, args in (("click_at", action), ("screenshot", {"tab_id": None})):
            try:
                await execute(tool, member, args)
            except RuntimeError:
                pass
            else:
                raise AssertionError("A cancelled capture revived a retired owned context.")
        await asyncio.wait_for(closed.wait(), timeout=2)
        assert driver.context.pages == []
        print("PASS cancelled owned capture retires its context; neither input nor another capture revives it")
    async with session(url) as (_, page, tool):
        for button, count in [("right", 1), ("left", 2), ("middle", 1), ("left", 3)]:
            assert (await execute(tool, "screenshot", {"tab_id": None}))["ok"]
            assert (
                await execute(
                    tool,
                    "click_at",
                    {"tab_id": None, "x": 20, "y": 20, "button": button, "click_count": count, "keys": []},
                )
            )["ok"]
        assert (await execute(tool, "screenshot", {"tab_id": None}))["ok"]
        assert (
            await execute(
                tool,
                "drag_path",
                {
                    "tab_id": None,
                    "path": [{"x": 20, "y": 20}, {"x": 100, "y": 40}, {"x": 150, "y": 80}],
                    "keys": ["Shift", "Alt"],
                },
            )
        )["ok"]
        await page.locator("#board").focus()
        assert (await execute(tool, "screenshot", {"tab_id": None}))["ok"]
        assert (
            await execute(tool, "hold_keys", {"tab_id": None, "keys": ["Shift", "ArrowRight"], "duration_ms": 120})
        )["ok"]
        result = await page.evaluate("() => window.readCanvasResult()")
        assert result["buttons"] == [2, 0, 0, 1, 0, 0, 0, 0]
        assert result["clickDetails"] == [1, 1, 2, 1, 1, 2, 3, 1]
        assert result["doubleClicks"] == 2
        assert result["dragPoints"] == [[100, 40], [150, 80]]
        assert result["modifierDrag"] is True and result["trusted"] is True
        assert result["pressed"] == [] and result["held"] >= 100
        await execute(tool, "screenshot", {"tab_id": None})
        await page.locator("#board").evaluate("node => node.replaceWith(node.cloneNode(true))")
        assert not (
            await execute(
                tool, "click_at", {"tab_id": None, "x": 20, "y": 20, "button": "left", "click_count": 1, "keys": []}
            )
        )["ok"]
        assert (await page.evaluate("() => window.readCanvasResult()"))["buttons"] == result["buttons"]
        print(
            "PASS trusted right/middle/double/triple clicks, modifier drag, timed hold, released keys and replaced-canvas refusal"
        )

    async with session(url) as (changed, page, tool):
        delivered: list[dict[str, Any]] = []

        def record_gesture(event: dict[str, Any]) -> None:
            delivered.append(event)

        await page.expose_function("recordGesture", record_gesture)  # pyright: ignore[reportUnknownMemberType] -- Playwright leaves the callback result untyped.
        await page.evaluate("""() => {
          document.addEventListener('mousedown', event => {
            void window.recordGesture({type:'down',detail:event.detail,target:event.target.id,trusted:event.isTrusted});
          });
          document.addEventListener('keyup', event => { void window.recordGesture({type:'up',key:event.key}); });
          document.querySelector('#board').addEventListener('mouseup', event => {
            if(event.detail===2) { const replacement=event.target.cloneNode(true); replacement.id='replacement'; event.target.replaceWith(replacement); }
          });
        }""")
        assert (await execute(tool, "screenshot", {"tab_id": None}))["ok"]
        try:
            await execute(
                tool,
                "click_at",
                {
                    "tab_id": None,
                    "x": 20,
                    "y": 20,
                    "button": "left",
                    "click_count": 3,
                    "keys": ["Shift"],
                },
            )
        except RuntimeError:
            pass
        else:
            raise AssertionError("Replaced target accepted a third click")
        assert [event for event in delivered if event["type"] == "down"] == [
            {"type": "down", "detail": 1, "target": "board", "trusted": True},
            {"type": "down", "detail": 2, "target": "board", "trusted": True},
        ]
        assert {"type": "up", "key": "Shift"} in delivered
        assert changed.context.pages == []
        print("PASS replaced target receives no third click; held modifier released and context retired")

    async with session(url) as (driver, page, tool), session(url) as (_, other_page, other_tool):
        closed = asyncio.Event()
        driver.context.on("close", lambda _context: closed.set())
        await page.locator("#board").focus()
        await execute(tool, "screenshot", {"tab_id": None})
        cancelled = asyncio.Event()
        work = asyncio.create_task(
            execute(
                tool,
                "hold_keys",
                {"tab_id": None, "keys": ["Shift", "ArrowRight"], "duration_ms": 3000},
                cancelled.is_set,
            )
        )
        await page.wait_for_function("() => window.readCanvasResult().pressed.includes('ArrowRight')")
        cancelled.set()
        try:
            await work
        except BrowserCancelledError:
            pass
        else:
            raise AssertionError("Expected cancelled held keys")
        assert driver._unusable
        await asyncio.wait_for(closed.wait(), timeout=2)
        assert driver.context.pages == []
        assert (await execute(other_tool, "screenshot", {"tab_id": None}))["ok"]
        assert (await other_page.evaluate("() => window.readCanvasResult()"))["pressed"] == []
        print("PASS cancelled hold retires only its own context; second owner remains usable")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        asyncio.run(tests(f"http://127.0.0.1:{server.server_port}/canvas"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
