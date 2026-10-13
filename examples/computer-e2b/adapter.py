from __future__ import annotations

import re
import time
import base64
import struct
import threading
from io import BytesIO
from uuid import uuid4
from typing import TYPE_CHECKING, Callable, Generator
from contextlib import contextmanager

from PIL import Image

from openai.lib.computer import Screenshot
from openai.types.responses import computer_action as modern, response_computer_tool_call as legacy

if TYPE_CHECKING:
    from e2b_desktop import Sandbox  # pyright: ignore[reportMissingTypeStubs]

DEFAULT_MAX_SCREENSHOT_PIXELS = 7680 * 4320


def _screenshot_limit(value: int, name: str = "max_screenshot_pixels") -> int:
    if type(value) is not int or not 1 <= value <= 2**53 - 1:
        raise ValueError(f"{name} must be a positive safe integer.")
    return value


MAX_TEXT_BYTES = 4096
MODIFIERS = {"ctrl", "alt", "shift", "super"}
KEYS = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "alt": "alt",
    "option": "alt",
    "shift": "shift",
    "super": "super",
    "cmd": "super",
    "meta": "super",
    "enter": "enter",
    "return": "enter",
    "escape": "escape",
    "esc": "escape",
    "tab": "tab",
    "space": "space",
    "backspace": "backspace",
    "delete": "delete",
    "left": "left",
    "arrowleft": "left",
    "right": "right",
    "arrowright": "right",
    "up": "up",
    "arrowup": "up",
    "down": "down",
    "arrowdown": "down",
    "home": "home",
    "end": "end",
    "pageup": "page_up",
    "pagedown": "page_down",
    **{f"f{i}": f"f{i}" for i in range(1, 13)},
}


class E2BComputerError(RuntimeError):
    pass


def _identity(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", value) is None:
        raise E2BComputerError("A known desktop identity is required.")
    return value


def _image_chunk(value: object) -> bytes:
    if not isinstance(value, bytes):
        raise E2BComputerError("Screenshot contains invalid data.")
    return value


def _dimensions(value: tuple[int, int], pixel_limit: int) -> tuple[int, int]:
    if len(value) != 2 or any(type(part) is not int or part < 1 for part in value):
        raise E2BComputerError("Invalid desktop dimensions.")
    if value[0] > pixel_limit // value[1]:
        raise E2BComputerError("Desktop dimensions exceed the screenshot pixel budget.")
    return value


def _key_chord(values: list[str]) -> list[str]:
    if not 1 <= len(values) <= 5:
        raise E2BComputerError("Unsupported key chord.")
    keys: list[str] = []
    for value in values:
        key = value.lower() if len(value) == 1 and value.isascii() and value.isalnum() else KEYS.get(value.lower())
        if key is None:
            raise E2BComputerError("Unsupported key.")
        keys.append(key)
    if keys[-1] in MODIFIERS or any(key not in MODIFIERS for key in keys[:-1]) or len(set(keys)) != len(keys):
        raise E2BComputerError("Unsupported key chord.")
    return keys


class E2BComputer:
    """Adapt a started desktop; close only screenshot files created here."""

    def __init__(
        self,
        sandbox: Sandbox,
        identity: str,
        size: tuple[int, int],
        *,
        max_screenshot_pixels: int = DEFAULT_MAX_SCREENSHOT_PIXELS,
        max_screenshot_bytes: int | None = None,
    ) -> None:
        self._sandbox = sandbox
        self._identity = identity
        self._pixel_limit = _screenshot_limit(max_screenshot_pixels)
        self._size = _dimensions(size, self._pixel_limit)
        encoded_budget = min(2**53 - 1, 2 * (8 * self._size[0] + 1) * self._size[1] + 65_536)
        self._byte_limit = _screenshot_limit(
            encoded_budget if max_screenshot_bytes is None else max_screenshot_bytes, "max_screenshot_bytes"
        )
        self._has_frame = False
        self._retired = False
        self._closed = False
        self._lock = threading.Lock()
        self._file: str | None = None

    @classmethod
    def from_started_desktop(
        cls,
        sandbox: Sandbox,
        *,
        max_screenshot_pixels: int = DEFAULT_MAX_SCREENSHOT_PIXELS,
        max_screenshot_bytes: int | None = None,
    ) -> E2BComputer:
        pixel_limit = _screenshot_limit(max_screenshot_pixels)
        if max_screenshot_bytes is not None:
            _screenshot_limit(max_screenshot_bytes, "max_screenshot_bytes")
        identity = _identity(sandbox.sandbox_id)
        try:
            return cls(
                sandbox,
                identity,
                sandbox.get_screen_size(),
                max_screenshot_pixels=pixel_limit,
                max_screenshot_bytes=max_screenshot_bytes,
            )
        except Exception:
            raise E2BComputerError("Cannot read desktop dimensions.") from None

    def _check(self, cancelled: Callable[[], bool] | None) -> None:
        if cancelled is not None and cancelled():
            raise E2BComputerError("The desktop operation was cancelled; the adapter is retired.")
        if self._sandbox.sandbox_id != self._identity:
            raise E2BComputerError("The desktop identity changed.")
        if _dimensions(self._sandbox.get_screen_size(), self._pixel_limit) != self._size:
            raise E2BComputerError("The desktop dimensions changed.")
        if self._sandbox.sandbox_id != self._identity:
            raise E2BComputerError("The desktop identity changed.")
        if cancelled is not None and cancelled():
            raise E2BComputerError("The desktop operation was cancelled; the adapter is retired.")

    @contextmanager
    def _operation(self, cancelled: Callable[[], bool] | None) -> Generator[None, None, None]:
        if not self._lock.acquire(blocking=False):
            raise E2BComputerError("A desktop operation is already running.")
        try:
            if self._closed or self._retired:
                raise E2BComputerError("The adapter is closed or retired.")
            self._check(cancelled)
            yield
            self._check(cancelled)
        except BaseException as error:
            self._retired = True
            self._has_frame = False
            if isinstance(error, E2BComputerError) or not isinstance(error, Exception):
                raise
            raise E2BComputerError("The desktop operation failed; the adapter is retired.") from None
        finally:
            self._lock.release()

    def _point(self, x: int, y: int, keys: object) -> None:
        if keys is not None and (type(keys) is not list or keys != []):
            raise E2BComputerError("Held pointer modifiers are unsupported.")
        if type(x) is not int or type(y) is not int or not 0 <= x < self._size[0] or not 0 <= y < self._size[1]:
            raise E2BComputerError("Point is outside the desktop.")
        if not self._has_frame:
            raise E2BComputerError("Take a matching screenshot before pointer input.")

    def click(self, action: modern.Click | legacy.ActionClick, *, cancelled: Callable[[], bool] | None = None) -> None:
        x, y, button = action.x, action.y, action.button
        self._point(x, y, getattr(action, "keys", None))
        if button not in ("left", "right"):
            raise E2BComputerError("Unsupported mouse button.")
        with self._operation(cancelled):
            self._sandbox.move_mouse(x, y)
            self._check(cancelled)
            if button == "left":
                self._sandbox.left_click()
            else:
                self._sandbox.right_click()

    def double_click(
        self, action: modern.DoubleClick | legacy.ActionDoubleClick, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        x, y = action.x, action.y
        self._point(x, y, getattr(action, "keys", None))
        with self._operation(cancelled):
            self._sandbox.move_mouse(x, y)
            self._check(cancelled)
            self._sandbox.double_click()

    def move(self, action: modern.Move | legacy.ActionMove, *, cancelled: Callable[[], bool] | None = None) -> None:
        x, y = action.x, action.y
        self._point(x, y, getattr(action, "keys", None))
        with self._operation(cancelled):
            self._sandbox.move_mouse(x, y)

    def drag(self, action: modern.Drag | legacy.ActionDrag) -> None:
        del action
        raise E2BComputerError("Drag is unsupported without guaranteed input release.")

    def scroll(self, action: modern.Scroll | legacy.ActionScroll) -> None:
        del action
        raise E2BComputerError("Pixel scrolling has no verified wheel-step mapping.")

    def keypress(
        self, action: modern.Keypress | legacy.ActionKeypress, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        keys = _key_chord(action.keys)
        with self._operation(cancelled):
            self._sandbox.press(keys)

    def type(self, action: modern.Type | legacy.ActionType, *, cancelled: Callable[[], bool] | None = None) -> None:
        text = action.text
        try:
            encoded = text.encode("utf-8")
        except UnicodeEncodeError:
            raise E2BComputerError("Text must contain valid Unicode.") from None
        if b"\0" in encoded or len(encoded) > MAX_TEXT_BYTES:
            raise E2BComputerError("Text must not contain NUL or exceed 4096 UTF-8 bytes.")
        with self._operation(cancelled):
            self._sandbox.write(text, chunk_size=max(1, len(text)), delay_in_ms=0)

    def wait(self, action: modern.Wait | legacy.ActionWait, *, cancelled: Callable[[], bool] | None = None) -> None:
        del action
        with self._operation(cancelled):
            time.sleep(1)

    def _remove(self, path: str) -> None:
        if self._sandbox.sandbox_id != self._identity:
            raise E2BComputerError("Cannot clean a changed desktop.")
        self._sandbox.files.remove(path)
        self._file = None

    def screenshot(self, *, cancelled: Callable[[], bool] | None = None) -> Screenshot:
        with self._operation(cancelled):
            self._has_frame = False
            path = f"/tmp/openai-computer-{uuid4()}.png"
            self._file = path
            try:
                self._sandbox.commands.run(f"scrot --pointer {path}", timeout=5, request_timeout=2.5)
                self._check(cancelled)
                data = bytearray()
                header = bytearray()
                with self._sandbox.files.read(path, format="stream", request_timeout=2.5) as stream:
                    self._check(cancelled)
                    for chunk in stream:
                        if cancelled is not None and cancelled():
                            raise E2BComputerError("The desktop operation was cancelled; the adapter is retired.")
                        chunk = _image_chunk(chunk)
                        if len(header) < 33:
                            header.extend(chunk[: 33 - len(header)])
                            if len(header) == 33 and (
                                bytes(header[:8]) != b"\x89PNG\r\n\x1a\n"
                                or bytes(header[8:16]) != b"\x00\x00\x00\rIHDR"
                                or struct.unpack(">II", header[16:24]) != self._size
                                or header[28] != 0
                            ):
                                raise E2BComputerError("Expected a matching non-interlaced full-desktop PNG.")
                        if len(chunk) > self._byte_limit - len(data):
                            raise E2BComputerError("Image exceeds the encoded screenshot byte budget.")
                        data.extend(chunk)
                if len(header) < 33:
                    raise E2BComputerError("Expected a matching non-interlaced full-desktop PNG.")
                with Image.open(BytesIO(data)) as image:
                    image.verify()
                with Image.open(BytesIO(data)) as image:
                    image.load()
                self._check(cancelled)
            finally:
                self._remove(path)
            self._has_frame = True
            return {
                "type": "computer_screenshot",
                "image_url": "data:image/png;base64," + base64.b64encode(data).decode("ascii"),
            }

    def close(self) -> None:
        self._closed = True
        self._has_frame = False
        if not self._lock.acquire(blocking=False):
            raise E2BComputerError("Drain the active operation before cleanup.")
        try:
            if self._file is not None:
                self._remove(self._file)
        except Exception:
            raise E2BComputerError("Screenshot cleanup remains unverified.") from None
        finally:
            self._lock.release()
