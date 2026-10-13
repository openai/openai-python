"""Optional local desktop. Ownership spans the complete SDK call and its approvals."""

from __future__ import annotations

import json
import time
import base64
import struct
import asyncio
import threading
from io import BytesIO
from typing import Union, TypeVar, Callable, Awaitable, cast
from pathlib import Path

from guest import Guest

from openai.lib.computer import (
    Screenshot,
    ComputerToolset,
    ComputerUseError,
    ComputerActionInput,
    AsyncComputerToolset,
)
from openai.types.responses import computer_action as modern, response_computer_tool_call as legacy

T = TypeVar("T")
_REPLY_LIMIT = 4 * 1024
_SCREENSHOT_LIMIT = 6 * 1024 * 1024
_EFFECT_TYPES = {"click", "double_click", "drag", "keypress", "move", "scroll", "type", "wait"}


class DesktopStartupError(ComputerUseError):
    """Startup ended with no guest left to remove."""


def _validate_screenshot(value: object) -> None:
    prefix = "data:image/png;base64,"
    if not isinstance(value, str) or not value.startswith(prefix):
        raise ComputerUseError("Desktop returned no PNG.")
    try:
        data = base64.b64decode(value[len(prefix) :], validate=True)
        if (
            len(data) < 33
            or len(data) > 4 * 1024 * 1024
            or data[:8] != b"\x89PNG\r\n\x1a\n"
            or data[8:16] != b"\x00\x00\x00\rIHDR"
            or struct.unpack(">II", data[16:24]) != (1024, 768)
        ):
            raise ComputerUseError("Desktop returned an invalid bounded PNG.")
        # Load only for a desktop capture; browser-only examples do not need Pillow.
        from PIL import Image

        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            image.load()
    except (OSError, SyntaxError, ValueError) as error:
        raise ComputerUseError("Desktop returned an invalid bounded PNG.") from error


class Desktop:
    """Owns only a fresh guest made from the fixed reviewed local image."""

    def __init__(self, runtime_dir: Path, *, cancelled: Callable[[], bool] | None = None) -> None:
        if cancelled is not None and cancelled():
            raise DesktopStartupError("Desktop startup was stopped.")
        self._state = threading.Condition()
        self._removal = threading.Lock()
        self._active = False
        self._viewers = 0
        self._input_pending = False
        self._stopped = False
        self.uncertain_effects = False
        self._guest = Guest(runtime_dir, cancelled=cancelled)
        self._id: str | None = self._guest.id
        try:
            end = time.monotonic() + 90
            while time.monotonic() < end:
                if cancelled is not None and cancelled():
                    raise ComputerUseError("Desktop startup was stopped.")
                if not self._guest.healthy(cancelled=cancelled):
                    raise ComputerUseError("Guest stopped during startup.")
                try:
                    ready = self._exchange({"type": "ready"}, timeout=min(3, max(0.01, end - time.monotonic())))
                except ComputerUseError:
                    ready = {"ok": False}
                if ready.get("ok") is True:
                    if cancelled is not None and cancelled():
                        raise ComputerUseError("Desktop startup was stopped.")
                    break
                time.sleep(0.2)
            else:
                raise ComputerUseError("Desktop did not become ready within its restrictions.")
        except BaseException as error:
            self.stop()
            if isinstance(error, Exception):
                raise DesktopStartupError("Desktop did not become ready within its restrictions.") from error
            raise

    def _begin(self) -> None:
        with self._state:
            if self._stopped or self._id is None:
                raise ComputerUseError("Desktop is stopped.")
            if self._active:
                raise ComputerUseError("Desktop already has an active operation.")
            self._active = True

    def _end(self) -> None:
        with self._state:
            self._active = False
            self._state.notify_all()

    def _result(self, value: T) -> T:
        with self._state:
            if self._stopped:
                raise ComputerUseError("Desktop stopped before its result could be used.")
            return value

    def operation(self, work: Callable[[ComputerToolset], T]) -> T:
        """Keep approvals, driver actions and the final capture in one admitted unit."""
        self._begin()
        try:
            return self._result(work(ComputerToolset(self)))
        finally:
            self._end()

    async def operation_async(self, work: Callable[[AsyncComputerToolset], Awaitable[T]]) -> T:
        self._begin()
        try:
            return self._result(await work(AsyncComputerToolset(AsyncDesktop(self))))
        except asyncio.CancelledError:
            # A cancelled to_thread can still be sending input. Revoke now: this
            # operation cannot drain itself. Repeated cancellation cannot skip
            # removal or reopen admission.
            with self._state:
                self._stopped = True
                if self._input_pending:
                    self.uncertain_effects = True
            removal = asyncio.create_task(asyncio.to_thread(self._remove))
            while not removal.done():
                try:
                    await asyncio.shield(removal)
                except asyncio.CancelledError:
                    continue
            removal.result()
            raise
        finally:
            self._end()

    def stop(self) -> None:
        """Admit nothing new. Drain up to five seconds, then remove only our created ID."""
        with self._state:
            self._stopped = True
            self._state.wait_for(lambda: not self._active and self._viewers == 0, timeout=5)
            if self._input_pending:
                self.uncertain_effects = True
        self._remove()

    def _remove(self) -> None:
        with self._removal:
            if self._id is not None:
                self._guest.remove()
                self._id = None

    def _exchange(
        self, value: dict[str, object], *, timeout: float = 10, cancelled: Callable[[], bool] | None = None
    ) -> dict[str, object]:
        guest_id = self._id
        if guest_id is None:
            return {"ok": False, "uncertain": False}
        data = json.dumps(value, ensure_ascii=True).encode("ascii") + b"\n"
        if len(data) > 16384:
            return {"ok": False, "uncertain": False}
        is_input = value.get("type") in _EFFECT_TYPES
        if is_input:
            with self._state:
                # Cancellation before the transport starts must not become
                # an uncertain input merely because a worker thread was queued.
                if self._stopped or not self._active:
                    return {"ok": False, "uncertain": False}
                self._input_pending = True
        try:
            raw = self._guest.exchange(
                data,
                timeout=timeout,
                limit=_SCREENSHOT_LIMIT if value.get("type") == "screenshot" else _REPLY_LIMIT,
                cancelled=cancelled,
            )
            try:
                reply = json.loads(raw)
            except (UnicodeError, ValueError) as exc:
                raise ComputerUseError("Invalid desktop reply.") from exc
            if not isinstance(reply, dict):
                raise ComputerUseError("Invalid desktop reply.")
            fields = cast(dict[str, object], reply)
            if type(fields.get("ok")) is not bool:
                raise ComputerUseError("Invalid desktop reply.")
            if value.get("type") == "screenshot" and fields["ok"] is True:
                _validate_screenshot(fields.get("image_url"))
        except ComputerUseError:
            if is_input:
                with self._state:
                    self.uncertain_effects = True
                    self._input_pending = False
            if value.get("type") == "screenshot" and not (cancelled is not None and cancelled()):
                with self._state:
                    self._stopped = True
                self._remove()
            raise
        if is_input:
            with self._state:
                if fields["ok"] is False and fields.get("uncertain") is not False:
                    self.uncertain_effects = True
                self._input_pending = False
        return fields

    def _request(
        self, value: dict[str, object], *, timeout: float = 10, cancelled: Callable[[], bool] | None = None
    ) -> dict[str, object]:
        with self._state:
            if self._stopped or not self._active:
                raise ComputerUseError("Use desktop.operation() for the complete SDK call.")

        def stopped() -> bool:
            with self._state:
                return self._stopped or (cancelled is not None and cancelled())

        try:
            reply = self._exchange(value, timeout=timeout, cancelled=stopped)
        except ComputerUseError:
            if stopped():
                # An interrupted input has no confirmed receipt; do not reuse
                # its guest. Read-only verification can still be repeated.
                if value.get("type") in _EFFECT_TYPES or value.get("type") in ("screenshot", "seal"):
                    with self._state:
                        self._stopped = True
                    self._remove()
                raise
            # Timeouts and malformed replies cannot prove that no input was sent.
            with self._state:
                self._stopped = True
            self._remove()
            raise
        if reply["ok"] is not True:
            if reply.get("uncertain") is not False:
                with self._state:
                    self._stopped = True
                self._remove()
            raise ComputerUseError("Desktop refused the action or its result is uncertain.")
        # A confirmed receipt is still confirmed after Stop. Do not reuse the
        # stale result, and do not relabel the confirmed action as uncertain.
        return self._result(reply)

    def _action(self, action: ComputerActionInput, cancelled: Callable[[], bool] | None) -> None:
        self._request(action.to_dict(), cancelled=cancelled)
        if cancelled is not None and cancelled():
            # The input receipt is confirmed, but this phase was cancelled
            # after dispatch. Do not let a future run reuse its changed guest.
            with self._state:
                self._stopped = True
            self._remove()
            raise ComputerUseError("Desktop operation was cancelled after input.")

    def verify(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, object]:
        """Only check the fixed fixture effect and fixed output file; return no contents."""
        if cancelled is not None and cancelled():
            raise ComputerUseError("Desktop verification was cancelled.")
        self._begin()
        try:
            reply = self._request({"type": "verify"}, cancelled=cancelled)
            if cancelled is not None and cancelled():
                raise ComputerUseError("Desktop verification was cancelled.")
            return self._result(
                {name: reply.get(name) for name in ("browser_matches", "file_matches", "file_empty", "browser_effects")}
            )
        finally:
            self._end()

    def seal(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, object]:
        """Stop fixture writers before returning terminal, persisted-state proof."""
        if cancelled is not None and cancelled():
            raise ComputerUseError("Desktop sealing was cancelled.")
        self._begin()
        try:
            reply = self._request({"type": "seal"}, cancelled=cancelled)
            if cancelled is not None and cancelled():
                with self._state:
                    self._stopped = True
                self._remove()
                raise ComputerUseError("Desktop sealing was cancelled.")
            return self._result(
                {name: reply.get(name) for name in ("browser_matches", "file_matches", "file_empty", "browser_effects")}
            )
        finally:
            self._end()

    def capture_frame(self, *, cancelled: Callable[[], bool] | None = None) -> Screenshot:
        """Read current guest pixels without acquiring or granting an input lease."""
        with self._state:
            if self._stopped or self._id is None:
                raise ComputerUseError("Desktop is stopped.")
            self._viewers += 1
        try:
            reply = self._exchange({"type": "screenshot"}, cancelled=cancelled)
            if cancelled is not None and cancelled():
                raise ComputerUseError("Desktop capture was cancelled.")
            image = reply.get("image_url")
            if (
                reply.get("ok") is not True
                or not isinstance(image, str)
                or not image.startswith("data:image/png;base64,")
            ):
                raise ComputerUseError("Desktop returned no PNG.")
            frame: Screenshot = {"type": "computer_screenshot", "image_url": image}
            return self._result(frame)
        finally:
            with self._state:
                self._viewers -= 1
                self._state.notify_all()

    def click(
        self, action: Union[modern.Click, legacy.ActionClick], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._action(action, cancelled)

    def double_click(
        self,
        action: Union[modern.DoubleClick, legacy.ActionDoubleClick],
        *,
        cancelled: Callable[[], bool] | None = None,
    ) -> None:
        self._action(action, cancelled)

    def drag(
        self, action: Union[modern.Drag, legacy.ActionDrag], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._action(action, cancelled)

    def keypress(
        self, action: Union[modern.Keypress, legacy.ActionKeypress], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._action(action, cancelled)

    def move(
        self, action: Union[modern.Move, legacy.ActionMove], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._action(action, cancelled)

    def scroll(
        self, action: Union[modern.Scroll, legacy.ActionScroll], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._action(action, cancelled)

    def type(
        self, action: Union[modern.Type, legacy.ActionType], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._action(action, cancelled)

    def wait(
        self, action: Union[modern.Wait, legacy.ActionWait], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        self._action(action, cancelled)

    def screenshot(self, *, cancelled: Callable[[], bool] | None = None) -> Screenshot:
        reply = self._request({"type": "screenshot"}, cancelled=cancelled)
        image = reply.get("image_url")
        if not isinstance(image, str) or not image.startswith("data:image/png;base64,"):
            raise ComputerUseError("Desktop returned no PNG.")
        return {"type": "computer_screenshot", "image_url": image}


class AsyncDesktop:
    """Use the same fixed owner without blocking the event loop on guest I/O."""

    def __init__(self, owner: Desktop) -> None:
        self.owner = owner

    async def click(
        self, action: Union[modern.Click, legacy.ActionClick], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        await asyncio.to_thread(self.owner.click, action, cancelled=cancelled)

    async def double_click(
        self,
        action: Union[modern.DoubleClick, legacy.ActionDoubleClick],
        *,
        cancelled: Callable[[], bool] | None = None,
    ) -> None:
        await asyncio.to_thread(self.owner.double_click, action, cancelled=cancelled)

    async def drag(
        self, action: Union[modern.Drag, legacy.ActionDrag], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        await asyncio.to_thread(self.owner.drag, action, cancelled=cancelled)

    async def keypress(
        self, action: Union[modern.Keypress, legacy.ActionKeypress], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        await asyncio.to_thread(self.owner.keypress, action, cancelled=cancelled)

    async def move(
        self, action: Union[modern.Move, legacy.ActionMove], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        await asyncio.to_thread(self.owner.move, action, cancelled=cancelled)

    async def scroll(
        self, action: Union[modern.Scroll, legacy.ActionScroll], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        await asyncio.to_thread(self.owner.scroll, action, cancelled=cancelled)

    async def type(
        self, action: Union[modern.Type, legacy.ActionType], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        await asyncio.to_thread(self.owner.type, action, cancelled=cancelled)

    async def wait(
        self, action: Union[modern.Wait, legacy.ActionWait], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        await asyncio.to_thread(self.owner.wait, action, cancelled=cancelled)

    async def screenshot(self, *, cancelled: Callable[[], bool] | None = None) -> Screenshot:
        return await asyncio.to_thread(self.owner.screenshot, cancelled=cancelled)
