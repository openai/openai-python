"""Installed client contract probe. No Daytona client/sandbox/API credentials."""

import sys
import json
import zlib
import base64
import asyncio
import hashlib
import inspect
import importlib.metadata as md
from types import SimpleNamespace
from typing import Any, cast
from pathlib import Path

from adapter import DaytonaComputer
from daytona import AsyncMouse, AsyncKeyboard, AsyncComputerUse
from daytona.common.errors import DaytonaError
from daytona._sync.computer_use import Mouse
from daytona_toolbox_api_client_async.models.display_info import DisplayInfo
from daytona_toolbox_api_client_async.api.computer_use_api import ComputerUseApi
from daytona_toolbox_api_client_async.models.screenshot_response import ScreenshotResponse
from daytona_toolbox_api_client_async.models.display_info_response import DisplayInfoResponse

from openai.lib.computer import ComputerUseError, AsyncComputerToolset
from openai.types.responses import ResponseComputerToolCall, computer_action as modern

SMALL_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
PIXELS = (Path(__file__).parent / "matching.png").read_bytes()
PNG = base64.b64encode(PIXELS).decode()


class API:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.value = PNG
        self.failed_pointer: str | None = None
        self.cancel_on: str | None = None
        self.cancelled = False
        self.change_during_screenshot = False
        self.display_gate: tuple[asyncio.Event, asyncio.Event] | None = None
        self.change_after_effect: str | None = None
        self.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)

    async def get_display_info(self, **_kwargs: object) -> DisplayInfoResponse:
        if self.display_gate is not None:
            entered, finish = self.display_gate
            self.display_gate = None
            entered.set()
            await finish.wait()
        return DisplayInfoResponse(displays=[self.display])

    async def take_screenshot(self, **_kwargs: object) -> ScreenshotResponse:
        self.calls.append(("screenshot", {}))
        if self.cancel_on == "screenshot":
            self.cancelled = True
        if self.change_during_screenshot:
            self.display = self.display.model_copy(update={"id": 8})
        return ScreenshotResponse(screenshot=self.value)

    async def click(self, request: Any, **_kwargs: object) -> SimpleNamespace:
        self.calls.append(("click", request.to_dict()))
        if self.change_after_effect == "click":
            self.display = self.display.model_copy(update={"id": 8})
        if self.cancel_on == "click":
            self.cancelled = True
        if self.failed_pointer == "click":
            raise ValueError("Uncertain pointer effect in local fixture.")
        return SimpleNamespace()

    async def move_mouse(self, request: Any, **_kwargs: object) -> SimpleNamespace:
        self.calls.append(("move", request.to_dict()))
        if self.cancel_on == "move":
            self.cancelled = True
        if self.failed_pointer == "move":
            raise ValueError("Uncertain pointer effect in local fixture.")
        return SimpleNamespace()

    async def drag(self, request: Any, **_kwargs: object) -> SimpleNamespace:
        self.calls.append(("drag", request.to_dict()))
        if self.cancel_on == "drag":
            self.cancelled = True
        if self.failed_pointer == "drag":
            raise ValueError("Uncertain pointer effect in local fixture.")
        return SimpleNamespace()

    async def press_key(self, request: Any, **_kwargs: object) -> SimpleNamespace:
        self.calls.append(("keypress", request.to_dict()))
        if self.change_after_effect == "keypress":
            self.display = self.display.model_copy(update={"id": 8})
        if self.cancel_on == "keypress":
            self.cancelled = True
        if self.failed_pointer == "keypress":
            raise ValueError("Uncertain keyboard effect in local fixture.")
        return SimpleNamespace()

    async def type_text(self, request: Any, **_kwargs: object) -> SimpleNamespace:
        self.calls.append(("type", request.to_dict()))
        if self.change_after_effect == "type":
            self.display = self.display.model_copy(update={"id": 8})
        if self.cancel_on == "type":
            self.cancelled = True
        if self.failed_pointer == "type":
            raise ValueError("Uncertain keyboard effect in local fixture.")
        return SimpleNamespace()


def computer_call(action: object, pending: object = None) -> ResponseComputerToolCall:
    return ResponseComputerToolCall.model_validate(
        {
            "type": "computer_call",
            "status": "completed",
            "call_id": "fixture",
            "id": "cu_fixture",
            "actions": [action],
            "pending_safety_checks": pending or [],
        }
    )


async def main() -> None:
    api = API()
    cu = AsyncComputerUse(cast(ComputerUseApi, api))
    driver = await DaytonaComputer.from_started_desktop(cu)
    tool = AsyncComputerToolset(driver)
    passed: list[str] = []
    failed: list[str] = []

    async def yes(_: object) -> bool:
        return True

    async def no(_: object) -> bool:
        return False

    async def check_refusal(label: str, action: object) -> None:
        api.calls.clear()
        try:
            await tool.execute(computer_call(action), before_action=yes)
        except (ValueError, ComputerUseError, DaytonaError):
            denied = True
        else:
            denied = False
        # Reads of screenshot or display are harmless. No pointer/keyboard operation.
        observed = [entry for entry in api.calls if entry[0] != "screenshot"]
        (passed if denied and not observed else failed).append(label)

    if "--keys" in sys.argv:
        await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        for keys in (["Control"], ["Control", "CTRL", "A"], ["Shift", "Alt"], ["Ctrl", "ctrl"]):
            await check_refusal("invalid chord " + "+".join(keys), {"type": "keypress", "keys": keys})
        api.calls.clear()
        await tool.execute(computer_call({"type": "keypress", "keys": ["Control", "A"]}), before_action=yes)
        assert api.calls[0] == ("keypress", {"key": "A", "modifiers": ["ctrl"]})
        assert not failed, failed
        print(json.dumps({"checks": len(passed) + 1, "api_calls": 0, "vendor_calls": 0}))
        return

    pointer = {"type": "click", "x": 1023, "y": 767, "button": "left"}
    await check_refusal("display:initial-screenshot-required", pointer)
    await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
    cases = [
        ({"type": "click", "x": 20, "y": 25, "button": "right"}, "click"),
        ({"type": "double_click", "x": 20, "y": 25, "keys": None}, "click"),
        ({"type": "move", "x": 20, "y": 25}, "move"),
        ({"type": "drag", "path": [{"x": 1, "y": 2}, {"x": 5, "y": 8}]}, "drag"),
        ({"type": "keypress", "keys": ["Control", "ArrowDown"]}, "keypress"),
        ({"type": "type", "text": "synthetic fixture"}, "type"),
        ({"type": "screenshot"}, "screenshot"),
    ]
    for action, name in cases:
        api.calls.clear()
        result = await tool.execute(computer_call(action), before_action=yes)
        assert api.calls[0][0] == name
        assert result["output"] == {"type": "computer_screenshot", "image_url": "data:image/png;base64," + PNG}
        passed.append(f"supported:{action['type']}")
        if name == "keypress":
            assert api.calls[0][1] == {"key": "down", "modifiers": ["ctrl"]}, api.calls
    unsupported = [
        {"type": "click", "x": 20, "y": 25, "button": "back"},
        {"type": "click", "x": 20, "y": 25, "button": "wheel"},
        {"type": "click", "x": 20, "y": 25, "button": "left", "keys": ["CTRL"]},
        {"type": "move", "x": 20, "y": 25, "keys": ["Shift"]},
        {"type": "double_click", "x": 20, "y": 25, "keys": ["Alt"]},
        {"type": "drag", "path": [{"x": 1, "y": 2}, {"x": 5, "y": 8}, {"x": 20, "y": 30}]},
        {"type": "drag", "path": [{"x": 1, "y": 2}, {"x": 5, "y": 8}], "keys": ["Shift"]},
        {"type": "scroll", "x": 20, "y": 25, "scroll_x": 100, "scroll_y": 0},
        {"type": "scroll", "x": 20, "y": 25, "scroll_x": 0, "scroll_y": 100},
        {"type": "move", "x": 1024, "y": 2},
        {"type": "keypress", "keys": ["some-main-key", "Z"]},
    ]
    for index, action in enumerate(unsupported):
        api.calls.clear()
        try:
            await tool.execute(computer_call(action), before_action=yes)
        except (ValueError, ComputerUseError, DaytonaError):
            pass
        else:
            raise AssertionError(("unsupported action ran", action))
        assert api.calls == [], api.calls
        passed.append(f"unsupported:{index}:{action['type']}")
    for pending in (None, [{"id": "check1", "code": "fixture", "message": "synthetic"}]):
        api.calls.clear()
        try:
            await tool.execute(
                computer_call(cases[0][0], pending),
                before_action=no if pending is None else yes,
                approve_safety_checks=no,
            )
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Approval ignored")
        assert api.calls == []
        passed.append("refused:" + ("safety" if pending else "action"))
    for value in ("", "https://example.invalid/private", base64.b64encode(b"other pixels").decode()):
        api.value = value
        try:
            await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        except (ValueError, ComputerUseError, DaytonaError):
            pass
        else:
            raise AssertionError("Invalid image accepted")
        passed.append("screenshot:invalid")
    original_display = api.display
    api.display = api.display.model_copy(update={"width": 1, "height": 1})
    small = base64.b64decode(SMALL_PNG)
    for extra in range(3):
        text = b"Comment\0" + b"x" * (66000 + extra)
        chunk = b"tEXt" + text
        image = small[:-12] + len(text).to_bytes(4, "big") + chunk + zlib.crc32(chunk).to_bytes(4, "big") + small[-12:]
        api.value = SMALL_PNG
        driver = await DaytonaComputer.from_started_desktop(cu)
        tool = AsyncComputerToolset(driver)
        await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        api.value = base64.b64encode(image).decode()
        await check_refusal(f"screenshot:default-byte-budget:{extra}", {"type": "screenshot"})
        await check_refusal(
            f"screenshot:budget-invalidates-pointer:{extra}", {"type": "click", "x": 0, "y": 0, "button": "left"}
        )
        assert not failed, failed
        driver = await DaytonaComputer.from_started_desktop(cu, max_screenshot_bytes=len(image) - 1)
        tool = AsyncComputerToolset(driver)
        await check_refusal(f"screenshot:one-byte-over:{extra}", {"type": "screenshot"})
        driver = await DaytonaComputer.from_started_desktop(cu, max_screenshot_bytes=len(image))
        tool = AsyncComputerToolset(driver)
        result = await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        assert result["output"] == {"type": "computer_screenshot", "image_url": "data:image/png;base64," + api.value}
        await tool.execute(computer_call({"type": "click", "x": 0, "y": 0, "button": "left"}), before_action=yes)
        passed.append(f"screenshot:exact-byte-budget-and-pointer:{extra}")
    api.display = original_display
    api.value = PNG
    driver = await DaytonaComputer.from_started_desktop(cu)
    tool = AsyncComputerToolset(driver)
    headers = [
        ("one-pixel", base64.b64decode(SMALL_PNG)),
        ("signature-only", PIXELS[:8]),
        ("truncated-ihdr", PIXELS[:32]),
        ("ihdr-only", PIXELS[:33]),
        ("no-iend", PIXELS[:-12]),
        ("wrong-chunk", PIXELS[:12] + b"IDAT" + PIXELS[16:]),
        ("wrong-length", PIXELS[:8] + (12).to_bytes(4, "big") + PIXELS[12:]),
    ]
    for label, payload in headers:
        api.value = PNG
        await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        api.value = base64.b64encode(payload).decode()
        await check_refusal("screenshot:" + label, {"type": "screenshot"})
        await check_refusal("display:invalidated:" + label, pointer)
    api.value = PNG
    for action, name in cases[:4]:
        driver = await DaytonaComputer.from_started_desktop(cu)
        tool = AsyncComputerToolset(driver)
        await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        api.calls.clear()
        api.failed_pointer = name
        try:
            await tool.execute(computer_call(action), before_action=yes)
        except (ValueError, ComputerUseError, DaytonaError):
            pass
        else:
            raise AssertionError("Uncertain provider failure was ignored")
        assert api.calls[0][0] == name
        api.failed_pointer = None
        await check_refusal(f"display:failed-{action['type']}-invalidates-frame", pointer)
        await check_refusal(f"display:failed-{action['type']}-retires-capture", {"type": "screenshot"})
    driver = await DaytonaComputer.from_started_desktop(cu)
    tool = AsyncComputerToolset(driver)
    await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
    api.calls.clear()
    batch = computer_call(pointer)
    assert batch.actions
    batch.actions.append(batch.actions[0])
    await tool.execute(batch, before_action=yes)
    assert [kind for kind, _ in api.calls] == ["click", "click", "screenshot"]
    passed.append("display:successful-multi-pointer-batch")
    for moment in ("before", "during"):
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        driver = await DaytonaComputer.from_started_desktop(cu)
        tool = AsyncComputerToolset(driver)
        if moment == "before":
            api.display = api.display.model_copy(update={"id": 8})
        api.change_during_screenshot = moment == "during"
        await check_refusal("display:changed-" + moment + "-capture", {"type": "screenshot"})
        api.change_during_screenshot = False
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        await check_refusal("display:retired-after-" + moment + "-capture", pointer)
    for action, name in cases[4:6]:
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        driver = await DaytonaComputer.from_started_desktop(cu)
        tool = AsyncComputerToolset(driver)
        await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        api.failed_pointer = name
        try:
            await tool.execute(computer_call(action), before_action=yes)
        except (ValueError, ComputerUseError, DaytonaError):
            pass
        else:
            raise AssertionError("Uncertain keyboard failure ignored")
        api.failed_pointer = None
        await check_refusal("display:failed-" + name + "-retires-pointer", pointer)
        await check_refusal("display:failed-" + name + "-retires-capture", {"type": "screenshot"})
    for action in ({"type": "type", "text": "must not reach replacement"}, {"type": "keypress", "keys": ["Enter"]}):
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        driver = await DaytonaComputer.from_started_desktop(cu)
        tool = AsyncComputerToolset(driver)
        api.display = api.display.model_copy(update={"id": 8})
        await check_refusal(f"display:changed-before-first-{action['type']}", action)
    api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
    driver = await DaytonaComputer.from_started_desktop(cu)
    tool = AsyncComputerToolset(driver)
    await check_refusal("keypress:empty", {"type": "keypress", "keys": [""]})
    api.calls.clear()
    await tool.execute(computer_call({"type": "keypress", "keys": ["𐐀"]}), before_action=yes)
    (passed if api.calls[0][0] == "keypress" and api.calls[0][1]["key"] == "𐐀" else failed).append(
        "keypress:non-bmp-preserved"
    )
    for label, replacements in [
        ("resize", {"width": 640, "height": 480}),
        ("identity", {"id": 8}),
        ("missing-id", {"id": None}),
    ]:
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        driver = await DaytonaComputer.from_started_desktop(cu)
        tool = AsyncComputerToolset(driver)
        await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        api.display = api.display.model_copy(update=replacements)
        await check_refusal("display:" + label, pointer)
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        await check_refusal("display:retired:" + label, {"type": "screenshot"})
        if label == "identity":
            await check_refusal("display:retired:type", {"type": "type", "text": "unwanted after retirement"})
            await check_refusal("display:retired:keypress", {"type": "keypress", "keys": ["Enter"]})
    driver = await DaytonaComputer.from_started_desktop(cu)
    tool = AsyncComputerToolset(driver)
    api.calls.clear()
    await tool.execute(computer_call({"type": "type", "text": "fresh adapter"}), before_action=yes)
    assert api.calls[0][0] == "type" and api.calls[0][1]["text"] == "fresh adapter"
    passed.append("display:fresh-adapter:type")
    api.calls.clear()
    await tool.execute(computer_call({"type": "keypress", "keys": ["Enter"]}), before_action=yes)
    assert api.calls[0][0] == "keypress" and api.calls[0][1]["key"] == "enter"
    passed.append("display:fresh-adapter:keypress")
    await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
    api.calls.clear()
    await tool.execute(computer_call(pointer), before_action=yes)
    assert api.calls[0] == ("click", {"x": 1023, "y": 767, "button": "left", "double": False})
    passed.append("display:fresh-driver-visible-positive")
    for action, kind in (
        (pointer, "click"),
        ({"type": "move", "x": 12, "y": 12}, "move"),
        ({"type": "type", "text": "Synthetic input"}, "type"),
        ({"type": "keypress", "keys": ["Enter"]}, "keypress"),
        ({"type": "screenshot"}, "screenshot"),
    ):
        driver = await DaytonaComputer.from_started_desktop(cu)
        tool = AsyncComputerToolset(driver)
        await tool.execute(computer_call({"type": "screenshot"}), before_action=yes)
        api.cancel_on, api.cancelled = kind, False
        api.calls.clear()
        try:
            await tool.execute(computer_call(action), before_action=yes, cancelled=lambda: api.cancelled)
        except (ValueError, ComputerUseError):
            pass
        else:
            raise AssertionError(f"Cancelled {kind} was reported successful")
        assert sum(name == kind for name, _ in api.calls) == 1
        api.cancel_on, api.cancelled = None, False
        await check_refusal("cancel:" + kind + ":pointer-revoked", pointer)
        await check_refusal("cancel:" + kind + ":fresh-capture-cannot-revive", {"type": "screenshot"})

    for action, kind in (
        ({"type": "click", "x": 10, "y": 10, "button": "left"}, "click"),
        ({"type": "type", "text": "fixture"}, "type"),
        ({"type": "keypress", "keys": ["Enter"]}, "keypress"),
    ):
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        driver = await DaytonaComputer.from_started_desktop(cu)
        await driver.screenshot()
        parsed_call = computer_call(action)
        assert parsed_call.actions
        parsed = parsed_call.actions[0]
        api.change_after_effect = kind
        try:
            await getattr(driver, kind)(parsed)
        except (ValueError, ComputerUseError):
            pass
        else:
            raise AssertionError(f"Display switch during {kind} reported success")
        api.change_after_effect = None
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        try:
            await driver.screenshot()
        except ValueError:
            pass
        else:
            raise AssertionError("Display restoration revived retired adapter")
        passed.append(f"direct:display-switched-during-{kind}")

    api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
    driver = await DaytonaComputer.from_started_desktop(cu)
    await driver.screenshot()
    entered, finish = asyncio.Event(), asyncio.Event()
    api.display_gate = entered, finish
    api.calls.clear()
    click = modern.Click(type="click", x=10, y=10, button="left")
    writing = modern.Type(type="type", text="overlap")
    pending_click = asyncio.create_task(driver.click(click))
    await entered.wait()
    for work in (driver.screenshot, lambda: driver.type(writing), lambda: driver.click(click)):
        try:
            await work()
        except ValueError:
            pass
        else:
            raise AssertionError("An overlapping operation reached the borrowed desktop")
    assert api.calls == []
    finish.set()
    await pending_click
    assert [name for name, _body in api.calls] == ["click"]
    await driver.screenshot()
    passed.append("direct:overlap-refused-before-dispatch-and-capture")
    api.calls.clear()
    for work in (
        lambda: driver.type(writing, cancelled=lambda: True),
        lambda: driver.screenshot(cancelled=lambda: True),
    ):
        try:
            await work()
        except ValueError:
            pass
        else:
            raise AssertionError("Cancelled operation entered the provider")
    assert api.calls == []
    await driver.click(click)
    assert [name for name, _body in api.calls] == ["click"]
    passed.append("direct:cancelled-before-admission-preserves-frame")

    for original in (
        {"type": "click", "x": 20, "y": 25, "button": "left"},
        {"type": "double_click", "x": 20, "y": 25},
        {"type": "move", "x": 20, "y": 25},
        {"type": "drag", "path": [{"x": 1, "y": 2}, {"x": 5, "y": 8}]},
        {"type": "type", "text": "Original fixture text"},
    ):
        api.display = DisplayInfo(id=7, is_active=True, x=0, y=0, width=1024, height=768)
        driver = await DaytonaComputer.from_started_desktop(cu)
        await driver.screenshot()
        api.calls.clear()
        action_call = computer_call(original)
        assert action_call.actions
        action = action_call.actions[0]
        await getattr(driver, action.type)(action)
        expected = list(api.calls)
        await driver.screenshot()
        action_call = computer_call(original)
        assert action_call.actions
        action = action_call.actions[0]
        entered, finish = asyncio.Event(), asyncio.Event()
        api.display_gate = entered, finish
        api.calls.clear()
        task = asyncio.create_task(getattr(driver, action.type)(action))
        await entered.wait()
        if action.type == "drag":
            action.path[0].x = 2000
            action.path[1].y = 3000
        elif action.type == "type":
            action.text = "Changed fixture text"
        else:
            assert isinstance(action, (modern.Click, modern.DoubleClick, modern.Move))
            action.x, action.y = 2000, 3000
            if action.type == "click":
                action.button = "wheel"
        assert not api.calls
        finish.set()
        await task
        assert api.calls == expected
        await driver.screenshot()
        passed.append(f"direct:captured-before-display:{original['type']}")

    package = Path(inspect.getfile(AsyncComputerUse))
    assert "site-packages" in package.parts
    print(
        json.dumps(
            {
                "scope": "published Daytona SDK -> in-process fake toolbox transport; current OpenAI helper; no hosted API",
                "python": sys.version,
                "daytona": md.version("daytona"),
                "openai": md.version("openai"),
                "providerFileSha256": hashlib.sha256(package.read_bytes()).hexdigest(),
                "computerFileSha256": hashlib.sha256(
                    Path(inspect.getfile(AsyncComputerToolset)).read_bytes()
                ).hexdigest(),
                "signatures": {
                    "async_click": str(inspect.signature(AsyncMouse.click)),
                    "sync_click": str(inspect.signature(Mouse.click)),
                    "async_scroll": str(inspect.signature(AsyncMouse.scroll)),
                    "async_press": str(inspect.signature(AsyncKeyboard.press)),
                },
                "passed": passed,
                "count": len(passed),
                "failed": failed,
            },
            indent=2,
        )
    )
    if failed:
        raise SystemExit(1)


asyncio.run(main())
