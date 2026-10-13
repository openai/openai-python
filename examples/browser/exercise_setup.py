"""Exercise Stop during browser setup admission with local Playwright substitutes."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from typing_extensions import Literal, override

import browser_driver

from openai.lib.browser import BrowserCancelledError


class StopAtJoin(asyncio.Event):
    @override
    async def wait(self) -> Literal[True]:
        try:
            return await super().wait()
        except asyncio.CancelledError:
            # Model Stop arriving on the event loop turn used to join the
            # retired setup watcher, after the last setup check.
            self.set()
            raise


async def main() -> None:
    stopped = StopAtJoin()
    context = SimpleNamespace(route=AsyncMock(), route_web_socket=AsyncMock())
    browser = SimpleNamespace(new_context=AsyncMock(return_value=context), close=AsyncMock())
    playwright = SimpleNamespace(chromium=SimpleNamespace(launch=AsyncMock(return_value=browser)))
    manager = AsyncMock()
    manager.__aenter__.return_value = playwright
    driver = SimpleNamespace(guard=AsyncMock(), new_tab=AsyncMock())

    async def opened(_arguments: object) -> None:
        # The watcher must be waiting before the last setup admission check.
        await asyncio.sleep(0)

    driver.new_tab.side_effect = opened
    with (
        patch.object(browser_driver, "async_playwright", return_value=manager),
        patch.object(browser_driver, "PlaywrightBrowser", return_value=driver),
    ):
        try:
            async with browser_driver.open_browser("http://fixture.invalid", setup_stopped=stopped):
                raise AssertionError("Stop during setup retirement must never yield a driver.")
        except BrowserCancelledError:
            pass
    assert stopped.is_set()
    browser.close.assert_awaited()
    print("PASS setup Stop at the admission join: no driver returned, owned browser closed.")


if __name__ == "__main__":
    asyncio.run(main())
