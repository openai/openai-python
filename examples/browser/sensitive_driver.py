"""Sensitive tools for an explicitly enabled, fresh, secret-free owned local fixture."""

from __future__ import annotations

import time
import asyncio
from typing import Callable, Awaitable
from collections import deque
from urllib.parse import urlsplit
from typing_extensions import override

from browser_driver import PlaywrightBrowser, origin
from playwright.async_api import Page, BrowserContext, WebSocketRoute

from openai.lib.browser import (
    NewTabInput,
    BrowserError,
    BrowserReadV1,
    NavigateInput,
    RunScriptInput,
    ReadDiagnosticsInput,
)


class SensitiveDriver(PlaywrightBrowser):
    def __init__(self, context: BrowserContext, url: str, *, diagnostics: bool = False, scripts: bool = False) -> None:
        fixture = urlsplit(url)
        if (
            fixture.scheme != "http"
            or fixture.hostname != "127.0.0.1"
            or fixture.username
            or fixture.password
            or fixture.query
            or fixture.fragment
        ):
            raise ValueError("Sensitive tools require an exact secret-free local fixture URL.")
        port = fixture.port
        canonical = "http://127.0.0.1" + (f":{port}" if port is not None and port != 80 else "") + (fixture.path or "/")
        super().__init__(context, {origin(canonical)}, owned_fixture_urls=frozenset({canonical}))
        self.installed_url = url
        self.fixture = canonical
        self.diagnostics_enabled = diagnostics is True
        self.scripts_enabled = scripts is True
        self.history: dict[Page, dict[str, deque[str]]] = {}
        self.dropped: dict[Page, set[str]] = {}
        if self.diagnostics_enabled:
            context.on("page", self._diagnostic_page)

    @override
    async def new_tab(self, action: NewTabInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        if action["url"] == self.installed_url:
            action = {**action, "url": self.fixture}
        await super().new_tab(action, cancelled=cancelled)

    @override
    async def navigate(self, action: NavigateInput, *, cancelled: Callable[[], bool] | None = None) -> str:
        if action["url"] == self.installed_url:
            action = {**action, "url": self.fixture}
        return await super().navigate(action, cancelled=cancelled)

    def _diagnostic_page(self, page: Page) -> None:
        records: dict[str, deque[str]] = {"console": deque(maxlen=100), "network": deque(maxlen=100)}
        self.history[page] = records
        self.dropped[page] = set()

        def add(source: str, text: str) -> None:
            if len(records[source]) == 100:
                self.dropped[page].add(source)
            records[source].append(text)

        def remove() -> None:
            self.history.pop(page, None)
            self.dropped.pop(page, None)

        page.on("close", lambda _page: remove())
        page.on(
            "console",
            lambda message: add(
                "console",
                "console:"
                + (message.type if message.type in ("warning", "error", "info", "debug", "log") else "other"),
            ),
        )
        page.on("response", lambda response: add("network", "status:" + str(response.status)))
        page.on("requestfailed", lambda _request: add("network", "failed"))

    def _current(self, tab_id: str | None) -> Page:
        selected, page = self.page(tab_id)
        if selected != self.active or page.url != self.fixture:
            raise BrowserError("Sensitive tools require the active installed fixture.")
        return page

    @property
    def read_diagnostics(self) -> Callable[[ReadDiagnosticsInput], Awaitable[BrowserReadV1]] | None:
        return self._read_diagnostics if self.diagnostics_enabled else None

    async def _read_diagnostics(self, action: ReadDiagnosticsInput) -> BrowserReadV1:
        page = self._current(action["tab_id"])
        records = self.history[page][action["source"]]
        return {
            "version": 1,
            "text": "\n".join(list(records)[-action["limit"] :]),
            "elements": [],
            "omitted": ["work_limit"]
            if action["source"] in self.dropped[page] or len(records) > action["limit"]
            else [],
        }

    @property
    def run_script(self) -> Callable[..., Awaitable[str]] | None:
        return self._run_script if self.scripts_enabled else None

    async def _run_script(self, action: RunScriptInput, *, cancelled: Callable[[], bool] | None) -> str:
        page = self._current(action["tab_id"])
        deadline = time.monotonic() + action["timeout_ms"] / 1000

        async def work() -> str:
            if cancelled and cancelled():
                raise BrowserError("Script interrupted.")
            root = await page.locator("html").element_handle()
            try:
                if cancelled and cancelled():
                    raise BrowserError("Script interrupted.")
                await self.invalidate_references()
                generation = self._generation
                if cancelled and cancelled():
                    raise BrowserError("Script interrupted.")
                result = await root.evaluate(
                    """async (element, body) => {
                      if (!element.isConnected || element.ownerDocument !== document) throw new Error('Fixture changed.');
                      const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor;
                      return await new AsyncFunction(body)();
                    }""",
                    action["source"],
                )
                if (
                    type(result) is not str
                    or len(result) > 16_384
                    or len(result.encode("utf-8")) > 16_384
                    or (cancelled and cancelled())
                    or self._current(action["tab_id"]) != page
                    or self._generation != generation
                    or not await root.evaluate("(e) => e.isConnected && e.ownerDocument === document")
                ):
                    raise BrowserError("Fixture changed.")
                return result
            finally:
                await root.dispose()

        pending = asyncio.create_task(work())
        try:
            while not pending.done():
                remaining = deadline - time.monotonic()
                if remaining <= 0 or (cancelled and cancelled()):
                    raise BrowserError("Script interrupted.")
                await asyncio.wait({pending}, timeout=min(0.025, remaining))
            return pending.result()
        except BaseException as error:
            self._retired()
            # Cancelling the waiter is not proof that Chromium stopped the script.
            if self._retirement is None:
                self._retirement = asyncio.create_task(self.context.close())
            pending.cancel()
            pending.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            if isinstance(error, asyncio.CancelledError):
                self._retirement.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
                raise
            await self._join_retirement(lambda: time.monotonic() >= deadline or bool(cancelled and cancelled()))
            raise


async def create_sensitive_driver(
    context: BrowserContext, url: str, *, diagnostics: bool = False, scripts: bool = False
) -> SensitiveDriver:
    driver = SensitiveDriver(context, url, diagnostics=diagnostics, scripts=scripts)
    await context.route("**/*", driver.guard)

    async def refuse_socket(route: WebSocketRoute) -> None:
        await route.close()

    await context.route_web_socket("**/*", refuse_socket)
    return driver
