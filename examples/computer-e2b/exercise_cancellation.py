from __future__ import annotations

import re
import json
import base64
import threading
from io import BytesIO
from typing import TYPE_CHECKING, cast
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

from adapter import E2BComputer, E2BComputerError

from openai.lib.computer import ComputerToolset, ComputerUseError
from openai.types.responses import ResponseComputerToolCall

if TYPE_CHECKING:
    from e2b_desktop import Sandbox  # pyright: ignore[reportMissingTypeStubs]

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAMCAIAAADkharWAAAAE0lEQVR4nGP4TyJgGNUwqgE7AAATaT3feQFNJQAAAABJRU5ErkJggg=="
)


def call(action: dict[str, object]) -> ResponseComputerToolCall:
    return ResponseComputerToolCall.model_validate(
        {
            "type": "computer_call",
            "id": "fixture",
            "call_id": "fixture",
            "status": "completed",
            "actions": [action],
            "pending_safety_checks": [],
        }
    )


class LocalDesktop:
    sandbox_id = "local-fixture"

    def __init__(self) -> None:
        self.entered = threading.Event()
        self.gate = threading.Event()
        self.effects: list[str] = []
        self.paths: set[str] = set()
        self.held: str | None = None
        self.commands = self
        self.files = self

    def get_screen_size(self) -> tuple[int, int]:
        return 16, 12

    def work(self, operation: str) -> None:
        self.effects.append(operation)
        if self.held == operation:
            self.entered.set()
            assert self.gate.wait(5), "Fixture input must be released."

    def move_mouse(self, x: int, y: int) -> None:
        del x, y
        self.work("move")

    def left_click(self) -> None:
        self.work("left")

    def right_click(self) -> None:
        self.work("right")

    def double_click(self) -> None:
        self.work("double")

    def press(self, keys: list[str]) -> None:
        del keys
        self.work("key")

    def write(self, text: str, **options: object) -> None:
        del text, options
        self.work("text")

    def run(self, command: str, **options: object) -> None:
        del options
        matched = re.fullmatch(r"scrot --pointer (/tmp/openai-computer-[0-9a-f-]+\.png)", command)
        assert matched
        self.paths.add(matched[1])

    def read(self, path: str, **options: object) -> BytesIO:
        del options
        assert path in self.paths
        return BytesIO(PNG)

    def remove(self, path: str) -> None:
        self.paths.remove(path)


class ChunkStream(BytesIO):
    def __init__(self, stop: threading.Event, cancel: bool) -> None:
        super().__init__(PNG)
        self.stop, self.cancel = stop, cancel
        self.consumed = 0

    @override
    def __next__(self) -> bytes:
        part = self.read(24)
        if not part:
            raise StopIteration
        self.consumed += 1
        if self.cancel and self.consumed == 2:
            self.stop.set()
        return part


class StreamingDesktop(LocalDesktop):
    def __init__(self, stop: threading.Event, cancel: bool) -> None:
        super().__init__()
        self.stream = ChunkStream(stop, cancel)

    @override
    def read(self, path: str, **options: object) -> BytesIO:
        assert path in self.paths and options == {"format": "stream", "request_timeout": 2.5}
        return self.stream


checks = 0
cases: list[tuple[str, dict[str, object], list[str]]] = [
    ("move", {"type": "click", "x": 1, "y": 2, "button": "left"}, ["move"]),
    ("move", {"type": "double_click", "x": 1, "y": 2}, ["move"]),
    ("move", {"type": "move", "x": 1, "y": 2}, ["move"]),
    ("left", {"type": "click", "x": 1, "y": 2, "button": "left"}, ["move", "left"]),
    ("right", {"type": "click", "x": 1, "y": 2, "button": "right"}, ["move", "right"]),
    ("double", {"type": "double_click", "x": 1, "y": 2}, ["move", "double"]),
    ("key", {"type": "keypress", "keys": ["ENTER"]}, ["key"]),
    ("text", {"type": "type", "text": "local fixture"}, ["text"]),
]
for held, action, expected in cases:
    desktop = LocalDesktop()
    adapter = E2BComputer.from_started_desktop(cast("Sandbox", desktop))
    adapter.screenshot()
    desktop.held = held
    stop = threading.Event()
    toolset = ComputerToolset(adapter)
    with ThreadPoolExecutor(max_workers=1) as executor:
        active = executor.submit(toolset.execute, call(action), before_action=lambda _: True, cancelled=stop.is_set)
        try:
            assert desktop.entered.wait(5), "The fixture never reached the admitted input."
            stop.set()
            try:
                adapter.screenshot()
            except E2BComputerError as exc:
                assert "already running" in str(exc)
            else:
                raise AssertionError("An active provider input must hold the operation")
            assert not active.done(), "Stop must drain the admitted blocking input."
        finally:
            desktop.gate.set()
        try:
            active.result(timeout=5)
        except ComputerUseError as exc:
            assert "cancel" in str(exc).lower()
        else:
            raise AssertionError("Stop must cancel the toolset execution.")
    assert desktop.effects == expected, "Do not issue a later input after Stop."
    try:
        toolset.execute(call({"type": "click", "x": 1, "y": 2, "button": "left"}), before_action=lambda _: True)
    except E2BComputerError:
        pass
    else:
        raise AssertionError("A post-Stop pointer must not reuse the pre-effect frame.")
    try:
        adapter.screenshot()
    except E2BComputerError:
        pass
    else:
        raise AssertionError("The retired adapter must not publish a new screenshot.")
    assert desktop.effects == expected
    adapter.close()
    assert not desktop.paths
    checks += 1

desktop = LocalDesktop()
adapter = E2BComputer.from_started_desktop(cast("Sandbox", desktop))
adapter.screenshot()
toolset = ComputerToolset(adapter)
pointer = call({"type": "click", "x": 1, "y": 2, "button": "left"})
try:
    toolset.execute(pointer, before_action=lambda _: True, cancelled=lambda: True)
except ComputerUseError:
    pass
else:
    raise AssertionError("Pre-admission Stop must cancel")
assert not desktop.effects
toolset.execute(pointer, before_action=lambda _: True)
assert desktop.effects == ["move", "left"]
adapter.close()
checks += 1

for cancel in (False, True):
    stop = threading.Event()
    streaming = StreamingDesktop(stop, cancel)
    adapter = E2BComputer.from_started_desktop(cast("Sandbox", streaming))
    try:
        image = adapter.screenshot(cancelled=stop.is_set)
        assert not cancel
        assert image.get("image_url") == "data:image/png;base64," + base64.b64encode(PNG).decode("ascii")
        assert streaming.stream.consumed == (len(PNG) + 23) // 24
    except E2BComputerError as exc:
        assert cancel and "cancel" in str(exc).lower()
        assert streaming.stream.consumed == 2, "Stop must not read a subsequent chunk."
        try:
            adapter.screenshot()
        except E2BComputerError:
            pass
        else:
            raise AssertionError("The cancelled frame must not permit a new screenshot.")
    assert streaming.stream.closed and not streaming.paths
    adapter.close()
    checks += 1
print(json.dumps({"checks": checks, "api_calls": 0, "vendor_calls": 0}))
