"""Adapt a borrowed, already-started Daytona desktop to async ComputerToolset actions."""

from __future__ import annotations

import base64
import struct
import asyncio
from io import BytesIO
from typing import TYPE_CHECKING, TypeVar, Callable, Awaitable

from PIL import Image

from openai.lib.computer import Screenshot
from openai.types.responses import computer_action as modern, response_computer_tool_call as legacy

if TYPE_CHECKING:
    from daytona import AsyncComputerUse

    from openai.lib.computer import AsyncComputerToolset

DEFAULT_MAX_SCREENSHOT_PIXELS = 7680 * 4320


def _screenshot_limit(value: int, name: str = "max_screenshot_pixels") -> int:
    if type(value) is not int or not 1 <= value <= 2**53 - 1:
        raise ValueError(f"{name} must be a positive safe integer.")
    return value


_KEYS = {
    "arrowdown": "down",
    "arrowleft": "left",
    "arrowright": "right",
    "arrowup": "up",
    "option": "alt",
    "super": "cmd",
    "win": "cmd",
    "control": "ctrl",
}
T = TypeVar("T")
_MODIFIERS = {"ctrl", "shift", "alt", "cmd"}


class DaytonaComputer:
    def __init__(
        self,
        computer_use: AsyncComputerUse,
        display_id: int,
        width: int,
        height: int,
        *,
        max_screenshot_pixels: int = DEFAULT_MAX_SCREENSHOT_PIXELS,
        max_screenshot_bytes: int | None = None,
    ) -> None:
        self._pixel_limit = _screenshot_limit(max_screenshot_pixels)
        if (
            type(width) is not int
            or type(height) is not int
            or width < 1
            or height < 1
            or width > self._pixel_limit // height
        ):
            raise ValueError("Unsupported display geometry or screenshot pixel budget.")
        encoded_budget = min(2**53 - 1, 2 * (8 * width + 1) * height + 65_536)
        self._byte_limit = _screenshot_limit(
            encoded_budget if max_screenshot_bytes is None else max_screenshot_bytes, "max_screenshot_bytes"
        )
        self.cu, self.display_id, self.width, self.height = computer_use, display_id, width, height
        self._has_screenshot = False
        self._retired = False
        self._busy = False

    @classmethod
    async def from_started_desktop(
        cls,
        computer_use: AsyncComputerUse,
        *,
        max_screenshot_pixels: int = DEFAULT_MAX_SCREENSHOT_PIXELS,
        max_screenshot_bytes: int | None = None,
    ) -> DaytonaComputer:
        pixel_limit = _screenshot_limit(max_screenshot_pixels)
        if max_screenshot_bytes is not None:
            _screenshot_limit(max_screenshot_bytes, "max_screenshot_bytes")
        info = await computer_use.display.get_info()
        displays = info.displays
        if not displays or len(displays) != 1:
            raise ValueError("Exactly one active display is required.")
        display = displays[0]
        if (
            display.is_active is not True
            or display.x != 0
            or display.y != 0
            or type(display.id) is not int
            or type(display.width) is not int
            or type(display.height) is not int
            or display.width < 1
            or display.height < 1
        ):
            raise ValueError("Unsupported display geometry.")
        return cls(
            computer_use,
            display.id,
            display.width,
            display.height,
            max_screenshot_pixels=pixel_limit,
            max_screenshot_bytes=max_screenshot_bytes,
        )

    def _check_cancelled(self, cancelled: Callable[[], bool] | None) -> None:
        if cancelled is not None and cancelled():
            self._retired = True
            self._has_screenshot = False
            raise ValueError("Daytona operation was cancelled; create a new adapter.")

    async def _check_display(self, cancelled: Callable[[], bool] | None) -> None:
        self._check_cancelled(cancelled)
        if self._retired:
            raise ValueError("The display changed. Create a new adapter and take a fresh screenshot.")
        try:
            info = await self.cu.display.get_info()
        except asyncio.CancelledError:
            self._retired = True
            self._has_screenshot = False
            raise
        self._check_cancelled(cancelled)
        displays = info.displays
        if (
            not displays
            or len(displays) != 1
            or displays[0].is_active is not True
            or displays[0].id != self.display_id
            or displays[0].x != 0
            or displays[0].y != 0
            or displays[0].width != self.width
            or displays[0].height != self.height
        ):
            self._retired = True
            self._has_screenshot = False
            raise ValueError("The display changed. Create a new adapter and take a fresh screenshot.")

    async def _effect(self, work: Callable[[], Awaitable[T]], cancelled: Callable[[], bool] | None) -> T:
        if cancelled is not None and cancelled():
            raise ValueError("Daytona operation was cancelled before admission.")
        if self._busy:
            raise ValueError("Another Daytona operation is still active.")
        self._busy = True
        had_screenshot = self._has_screenshot
        self._has_screenshot = False
        dispatched = False
        try:
            await self._check_display(cancelled)
            dispatched = True
            result = await work()
            try:
                await self._check_display(cancelled)
            except BaseException:
                self._retired = True
                raise
            self._has_screenshot = had_screenshot
            return result
        except BaseException as error:
            if dispatched or isinstance(error, asyncio.CancelledError) or (cancelled is not None and cancelled()):
                self._retired = True
            self._has_screenshot = False
            raise
        finally:
            self._busy = False

    def _point(
        self,
        point: modern.Click
        | legacy.ActionClick
        | modern.DoubleClick
        | legacy.ActionDoubleClick
        | modern.Move
        | legacy.ActionMove
        | modern.DragPath
        | legacy.ActionDragPath,
    ) -> tuple[int, int]:
        x, y = point.x, point.y
        if type(x) is not int or type(y) is not int or not 0 <= x < self.width or not 0 <= y < self.height:
            raise ValueError("Point is outside the selected display.")
        if not self._has_screenshot:
            raise ValueError("A matching screenshot from an active adapter is required.")
        return x, y

    def _no_held_keys(
        self,
        action: modern.Click
        | legacy.ActionClick
        | modern.DoubleClick
        | legacy.ActionDoubleClick
        | modern.Move
        | legacy.ActionMove
        | modern.Drag
        | legacy.ActionDrag,
    ) -> None:
        if getattr(action, "keys", None):
            raise ValueError("Daytona 0.220.0 cannot preserve held keys for pointer actions.")

    async def click(
        self, action: modern.Click | legacy.ActionClick, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._no_held_keys(action)
        x, y = self._point(action)
        button = action.button
        if button not in ("left", "right"):
            raise ValueError("This adapter supports only left and right clicks.")
        await self._effect(lambda: self.cu.mouse.click(x, y, button), cancelled)

    async def double_click(
        self, action: modern.DoubleClick | legacy.ActionDoubleClick, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._no_held_keys(action)
        x, y = self._point(action)
        await self._effect(lambda: self.cu.mouse.click(x, y, "left", True), cancelled)

    async def drag(
        self, action: modern.Drag | legacy.ActionDrag, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._no_held_keys(action)
        if len(action.path) != 2:
            raise ValueError("Only a two-point drag is supported.")
        start, end = action.path
        start_x, start_y = self._point(start)
        end_x, end_y = self._point(end)
        await self._effect(lambda: self.cu.mouse.drag(start_x, start_y, end_x, end_y), cancelled)

    async def move(
        self, action: modern.Move | legacy.ActionMove, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._no_held_keys(action)
        x, y = self._point(action)
        await self._effect(lambda: self.cu.mouse.move(x, y), cancelled)

    async def scroll(self, action: modern.Scroll | legacy.ActionScroll) -> None:  # noqa: ARG002
        raise ValueError("Pixel scroll distance has no verified Daytona wheel-step mapping.")

    async def keypress(
        self, action: modern.Keypress | legacy.ActionKeypress, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        if not action.keys or any(not key for key in action.keys):
            raise ValueError("A keypress needs a key.")
        keys = [k if len(k) == 1 else _KEYS.get(k.lower(), k.lower()) for k in action.keys]
        if keys[-1] in _MODIFIERS or len(set(keys)) != len(keys) or any(key not in _MODIFIERS for key in keys[:-1]):
            raise ValueError("Unsupported key chord modifiers.")
        await self._effect(lambda: self.cu.keyboard.press(keys[-1], keys[:-1] or None), cancelled)

    async def type(
        self, action: modern.Type | legacy.ActionType, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        text = action.text
        await self._effect(lambda: self.cu.keyboard.type(text), cancelled)

    async def wait(
        self, action: modern.Wait | legacy.ActionWait, *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        del action
        await self._effect(lambda: asyncio.sleep(1), cancelled)

    async def screenshot(self, *, cancelled: Callable[[], bool] | None = None) -> Screenshot:
        if cancelled is not None and cancelled():
            raise ValueError("Daytona operation was cancelled before admission.")
        if self._busy:
            raise ValueError("Another Daytona operation is still active.")
        self._busy = True
        try:
            self._has_screenshot = False
            await self._check_display(cancelled)
            shot = await self.cu.screenshot.take_full_screen()
            value = shot.screenshot
            if type(value) is not str:
                raise ValueError("Daytona returned no screenshot.")
            padding = 2 if value.endswith("==") else 1 if value.endswith("=") else 0
            if ((len(value) + 3) // 4) * 3 - padding > self._byte_limit:
                raise ValueError("Image exceeds the encoded screenshot byte budget.")
            try:
                data = base64.b64decode(value, validate=True)
            except ValueError:
                raise ValueError("Daytona returned an invalid screenshot.") from None
            if (
                len(data) < 33
                or data[:8] != b"\x89PNG\r\n\x1a\n"
                or data[8:16] != b"\x00\x00\x00\rIHDR"
                or struct.unpack(">II", data[16:24]) != (self.width, self.height)
                or self.width > self._pixel_limit // self.height
                or data[28] != 0
            ):
                raise ValueError("Expected a non-interlaced full-screen PNG within the pixel budget.")
            try:
                with Image.open(BytesIO(data)) as image:
                    image.verify()
                with Image.open(BytesIO(data)) as image:
                    image.load()
            except (OSError, SyntaxError):
                raise ValueError("Expected a complete full-screen PNG.") from None
            await self._check_display(cancelled)
            self._has_screenshot = True
            return {"type": "computer_screenshot", "image_url": "data:image/png;base64," + value}
        finally:
            self._busy = False


if TYPE_CHECKING:

    def check_toolset_types(driver: DaytonaComputer) -> None:
        AsyncComputerToolset(driver)
