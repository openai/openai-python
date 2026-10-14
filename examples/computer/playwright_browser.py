"""A single-page, screenshot-based driver. Browser ownership stays with the caller."""

from __future__ import annotations

import re
import base64
import asyncio
from socket import inet_aton
from typing import Union, Literal
from ipaddress import IPv4Address, IPv6Address
from contextlib import asynccontextmanager
from urllib.parse import unquote, urlsplit
from collections.abc import AsyncGenerator

import idna
from playwright.async_api import Page, Error, Route

from openai.lib.computer import Screenshot, ComputerUseError
from openai.types.responses import computer_action as modern, response_computer_tool_call as legacy

WIDTH = 1024
HEIGHT = 768

_ALIASES = {
    "ALT": "Alt",
    "OPTION": "Alt",
    "CTRL": "Control",
    "CONTROL": "Control",
    "CMD": "Meta",
    "COMMAND": "Meta",
    "META": "Meta",
    "SUPER": "Meta",
    "SHIFT": "Shift",
    "ENTER": "Enter",
    "RETURN": "Enter",
    "ESC": "Escape",
    "ESCAPE": "Escape",
    "SPACE": "Space",
    "BACKSPACE": "Backspace",
    "DELETE": "Delete",
    "DEL": "Delete",
    "TAB": "Tab",
    "UP": "ArrowUp",
    "DOWN": "ArrowDown",
    "LEFT": "ArrowLeft",
    "RIGHT": "ArrowRight",
    "ARROWUP": "ArrowUp",
    "ARROWDOWN": "ArrowDown",
    "ARROWLEFT": "ArrowLeft",
    "ARROWRIGHT": "ArrowRight",
    "HOME": "Home",
    "END": "End",
    "PAGEUP": "PageUp",
    "PAGEDOWN": "PageDown",
}
_MODIFIERS = {"Alt", "Control", "Meta", "Shift"}


def origin(url: str) -> str:
    """Return a canonical HTTP origin, rejecting credentials and other schemes."""
    try:
        parsed = urlsplit(url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError
        host = parsed.hostname
        if parsed.netloc.startswith("["):
            if "%" in host:
                raise ValueError
            host = f"[{IPv6Address(host).compressed}]"
        else:
            host = idna.uts46_remap(unquote(host, errors="strict"), std3_rules=False, transitional=False)
            if not host or any(ord(c) <= 32 or c in "#%/:<>?@[\\]^|" or ord(c) == 127 for c in host):
                raise ValueError
            if not host.isascii():
                host = idna.encode(host).decode("ascii")
            last = host.removesuffix(".").rsplit(".", 1)[-1]
            if re.fullmatch(r"(?:[0-9]+|0[xX][0-9a-fA-F]*)", last):
                host = str(IPv4Address(inet_aton(host.removesuffix("."))))
        port = parsed.port if parsed.port is not None else (443 if parsed.scheme == "https" else 80)
        return f"{parsed.scheme}://{host}:{port}"
    except (ValueError, OSError):
        raise ValueError("Only http(s) URLs without credentials are supported.") from None


def key_name(value: str) -> str:
    key = _ALIASES.get(value.upper())
    if key is not None:
        return key
    if len(value) == 1 and value.isprintable():
        return value
    if value.upper().startswith("F") and value[1:].isdigit() and 1 <= int(value[1:]) <= 12:
        return value.upper()
    raise ComputerUseError("This driver does not support the requested key.")


class PlaywrightBrowser:
    """Drive one page while its caller context has at most 100 pages.

    This example stops admitting work at that budget. The caller remains
    responsible for popups and for closing its pages and browser.
    """

    def __init__(self, page: Page, allowed_origins: set[str]) -> None:
        self.page = page
        self.allowed_origins = frozenset(allowed_origins)
        self._unusable = False

    def _check(self) -> None:
        if self._unusable:
            raise ComputerUseError("This borrowed driver was retired and cannot be reused.")
        if len(self.page.context.pages) > 100:
            self._unusable = True
            raise ComputerUseError("Browser page limit reached; this borrowed driver cannot be reused.")

    async def guard(self, route: Route) -> None:
        # Only exact opted-in origins; even other localhost ports are blocked.
        try:
            try:
                allowed = origin(route.request.url) in self.allowed_origins
            except ValueError:
                allowed = False
            if not allowed:
                await route.abort("blockedbyclient")
                return
            response = await route.fetch(max_redirects=0)
            try:
                if response.status in (301, 302, 303, 307, 308):
                    await route.abort("failed")
                    return
                await route.fulfill(response=response)
            finally:
                await response.dispose()
        except Error:
            try:
                await route.abort("failed")
            except Error:
                pass

    @staticmethod
    def point(x: int, y: int) -> None:
        if not 0 <= x < WIDTH or not 0 <= y < HEIGHT:
            raise ComputerUseError("Point is outside the screenshot.")

    @asynccontextmanager
    async def held(self, keys: list[str] | None, *, modifiers_only: bool = True) -> AsyncGenerator[None]:
        self._check()
        names = [key_name(key) for key in (keys or [])]
        if modifiers_only and any(name not in _MODIFIERS for name in names):
            raise ComputerUseError("Pointer actions accept modifier keys only.")
        pressed: list[str] = []
        interrupted = False
        try:
            for name in names:
                pressed.append(name)
                await self.page.keyboard.down(name)
            yield
            self._check()
        except BaseException as error:
            interrupted = not isinstance(error, Exception)
            self._unusable = True
            if isinstance(error, Error):
                raise ComputerUseError("Browser input failed; this borrowed driver cannot be reused.") from None
            raise
        finally:
            failed = False
            release_interrupted: BaseException | None = None
            for name in reversed(pressed):
                try:
                    await self.page.keyboard.up(name)
                except BaseException as error:
                    if isinstance(error, Exception):
                        failed = True
                    elif release_interrupted is None:
                        release_interrupted = error
                    self._unusable = True
            if release_interrupted is not None and not interrupted:
                raise release_interrupted
            if failed and not interrupted:
                raise ComputerUseError("Input release was uncertain; this borrowed driver cannot be reused.")

    async def click(self, action: Union[modern.Click, legacy.ActionClick]) -> None:
        self.point(action.x, action.y)
        button: Literal["left", "right", "middle"]
        if action.button == "wheel":
            button = "middle"
        elif action.button == "left" or action.button == "right":
            button = action.button
        else:
            raise ComputerUseError("This driver does not support back/forward mouse buttons.")
        async with self.held(action.keys):
            await self.page.mouse.click(action.x, action.y, button=button)

    async def double_click(self, action: Union[modern.DoubleClick, legacy.ActionDoubleClick]) -> None:
        self.point(action.x, action.y)
        async with self.held(action.keys):
            await self.page.mouse.dblclick(action.x, action.y)

    async def drag(self, action: Union[modern.Drag, legacy.ActionDrag]) -> None:
        if len(action.path) < 2:
            raise ComputerUseError("A drag needs at least two points.")
        for point in action.path:
            self.point(point.x, point.y)
        async with self.held(action.keys):
            start, *rest = action.path
            await self.page.mouse.move(start.x, start.y)
            interrupted = False
            try:
                await self.page.mouse.down()
                for point in rest:
                    await self.page.mouse.move(point.x, point.y)
            except BaseException as error:
                interrupted = not isinstance(error, Exception)
                raise
            finally:
                try:
                    await self.page.mouse.up()
                except BaseException as error:
                    self._unusable = True
                    if not interrupted:
                        if not isinstance(error, Exception):
                            raise
                        raise ComputerUseError(
                            "Input release was uncertain; this borrowed driver cannot be reused."
                        ) from None

    async def keypress(self, action: Union[modern.Keypress, legacy.ActionKeypress]) -> None:
        async with self.held(action.keys, modifiers_only=False):
            pass

    async def move(self, action: Union[modern.Move, legacy.ActionMove]) -> None:
        self.point(action.x, action.y)
        async with self.held(action.keys):
            await self.page.mouse.move(action.x, action.y)

    async def scroll(self, action: Union[modern.Scroll, legacy.ActionScroll]) -> None:
        self.point(action.x, action.y)
        if abs(action.scroll_x) > WIDTH * 4 or abs(action.scroll_y) > HEIGHT * 4:
            raise ComputerUseError("Scroll exceeds the example's four-viewport limit.")
        async with self.held(action.keys):
            await self.page.mouse.move(action.x, action.y)
            await self.page.mouse.wheel(action.scroll_x, action.scroll_y)

    async def type(self, action: Union[modern.Type, legacy.ActionType]) -> None:
        async with self.held(None):
            await self.page.keyboard.insert_text(action.text)

    async def wait(self, action: Union[modern.Wait, legacy.ActionWait]) -> None:  # noqa: ARG002
        self._check()
        # The API wait action has no duration. Give the page at most one second.
        await asyncio.sleep(1)
        self._check()

    async def screenshot(self) -> Screenshot:
        self._check()
        try:
            png = await self.page.screenshot(type="png", full_page=False, timeout=5_000)
        except Error:
            raise ComputerUseError("Browser screenshot failed.") from None
        self._check()
        return {"type": "computer_screenshot", "image_url": "data:image/png;base64," + base64.b64encode(png).decode()}
