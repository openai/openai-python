from __future__ import annotations

import re
import sys
import json
import shlex
import base64
import threading
from types import SimpleNamespace
from typing import Any, Callable, cast
from pathlib import Path
from typing_extensions import override

import httpx2 as httpx
from e2b_desktop import Sandbox  # pyright: ignore[reportMissingTypeStubs]
from e2b.sandbox_sync.commands.command import Commands as SandboxCommands  # pyright: ignore[reportMissingTypeStubs]
from e2b.sandbox_sync.filesystem.filesystem import Filesystem  # pyright: ignore[reportMissingTypeStubs]

from openai import OpenAI
from openai.lib.computer import ComputerToolset
from openai.types.responses import ResponseComputerToolCall, computer_action as modern
from openai.lib.responses_tool_runner import RegisteredFunction, ResponsesToolRunner

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapter import E2BComputer

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAMCAIAAADkharWAAAAE0lEQVR4nGP4TyJgGNUwqgE7AAATaT3feQFNJQAAAABJRU5ErkJggg=="
)
PASSED: list[str] = []


def call(action: object) -> ResponseComputerToolCall:
    return ResponseComputerToolCall.model_validate(
        {
            "type": "computer_call",
            "id": "computer_fixture",
            "call_id": "computer_fixture",
            "status": "completed",
            "actions": [action],
            "pending_safety_checks": [],
        }
    )


def rejected(function: Callable[[], object]) -> None:
    try:
        function()
    except Exception:
        return
    raise AssertionError("Expected refusal")


class Stream:
    def __init__(self, state: SimpleNamespace, data: bytes) -> None:
        self.state, self.data, self.sent = state, data, False

    def __enter__(self) -> Stream:
        return self

    def __exit__(self, *args: object) -> None:
        self.state.closed_streams += 1

    def __iter__(self) -> Stream:
        return self

    def __next__(self) -> bytes:
        if self.sent:
            if self.state.after_read:
                self.state.after_read()
            raise StopIteration
        self.sent = True
        return self.data


class Commands:
    def __init__(self, state: SimpleNamespace) -> None:
        self.state = state

    def run(self, command: str, **_kwargs: object) -> SimpleNamespace:
        state = self.state
        state.calls.append(command)
        if command == "xrandr":
            if state.after_size:
                state.after_size()
            return SimpleNamespace(stdout=f"screen connected {state.width}x{state.height}+0+0")
        capture = re.fullmatch(r"scrot --pointer (/tmp/openai-computer-[0-9a-f-]+\.png)", command)
        if capture:
            state.files[capture[1]] = state.image
            return SimpleNamespace(stdout="")
        parts = shlex.split(command)
        if parts[:3] == ["xdotool", "mousemove", "--sync"]:
            if state.hold_move:
                state.move_entered.set()
                assert state.hold_move.wait(5), "Fixture move was not released"
            if state.fail_move:
                raise RuntimeError("fixture move failure")
            state.x, state.y = map(int, parts[3:])
            if state.after_move:
                state.after_move()
        elif parts[:2] == ["xdotool", "click"]:
            count = int(parts[3]) if parts[2] == "--repeat" else 1
            state.clicks.append((state.x, state.y, int(parts[-1]), count))
        elif parts[:2] == ["xdotool", "key"]:
            state.keys.append(parts[2])
            if state.after_key:
                state.after_key()
        elif parts[:5] == ["xdotool", "type", "--delay", "0", "--"]:
            assert len(parts) == 6
            state.text += parts[5]
            state.writes += 1
            if state.after_write:
                state.after_write()
        else:
            raise AssertionError("Unexpected fixture command")
        return SimpleNamespace(stdout="")


class Files:
    def __init__(self, state: SimpleNamespace) -> None:
        self.state = state

    def read(self, path: str, *, format: str, **_kwargs: object) -> Stream:
        assert format == "stream"
        if self.state.fail_read:
            raise RuntimeError("fixture read failure")
        return Stream(self.state, self.state.files[path])

    def remove(self, path: str) -> None:
        if self.state.fail_remove:
            raise RuntimeError("fixture removal failure")
        self.state.files.pop(path, None)


class LocalSandbox(Sandbox):
    def __init__(self, state: SimpleNamespace) -> None:
        self.fixture = state
        self.fixture_commands = Commands(state)
        self.fixture_files = Files(state)

    @property
    @override
    def sandbox_id(self) -> str:
        return self.fixture.identity

    @property
    @override
    def commands(self) -> SandboxCommands:
        return cast(SandboxCommands, self.fixture_commands)

    @property
    @override
    def files(self) -> Filesystem:
        return cast(Filesystem, self.fixture_files)


def fixture(frame: bool = True) -> tuple[SimpleNamespace, LocalSandbox, E2BComputer, ComputerToolset]:
    state = SimpleNamespace(
        identity="local-fixture",
        width=16,
        height=12,
        x=7,
        y=7,
        calls=[],
        clicks=[],
        keys=[],
        text="",
        writes=0,
        files={},
        image=PNG,
        fail_move=False,
        fail_read=False,
        fail_remove=False,
        after_read=None,
        after_size=None,
        hold_move=None,
        after_move=None,
        after_key=None,
        after_write=None,
        move_entered=threading.Event(),
        closed_streams=0,
    )
    sandbox = LocalSandbox(state)
    driver = E2BComputer.from_started_desktop(sandbox)
    tool = ComputerToolset(driver)
    if frame:
        tool.execute(call({"type": "screenshot"}), before_action=lambda _: True)
    return state, sandbox, driver, tool


for name, action, expected in [
    ("left at x zero", {"type": "click", "x": 0, "y": 5, "button": "left"}, (0, 5, 1, 1)),
    ("right at y zero", {"type": "click", "x": 5, "y": 0, "button": "right"}, (5, 0, 3, 1)),
    ("double at origin", {"type": "double_click", "x": 0, "y": 0}, (0, 0, 1, 2)),
]:
    state, _, driver, tool = fixture()
    tool.execute(call(action), before_action=lambda _: True)
    assert state.clicks == [expected] and not state.files
    driver.close()
    PASSED.append(name)

state, sandbox, driver, _ = fixture()
sandbox.left_click(0, 5)
assert state.clicks == [(7, 7, 1, 1)]
driver.close()
PASSED.append("real provider edge bug control")

state, _, driver, tool = fixture()
result = tool.execute(call({"type": "move", "x": 15, "y": 11}), before_action=lambda _: True)
assert (state.x, state.y) == (15, 11)
assert result["output"].get("image_url") == "data:image/png;base64," + base64.b64encode(PNG).decode()
driver.close()
PASSED.append("matching image and edge move")

state, _, driver, _ = fixture(False)
before = len(state.calls)
rejected(lambda: driver.click(modern.Click.model_construct(type="click", x=1, y=1, button="left")))
assert len(state.calls) == before
driver.screenshot()
driver.close()
PASSED.append("first screenshot required")

state, _, driver, _ = fixture()
before = len(state.calls)
for keys in [1, 0, False, "", {}, {"length": 0, "ctrl": True}]:
    rejected(
        lambda keys=keys: driver.click(modern.Click.model_construct(type="click", x=0, y=0, button="left", keys=keys))
    )
assert len(state.calls) == before
driver.click(modern.Click.model_construct(type="click", x=0, y=0, button="left", keys=[]))
assert state.clicks == [(0, 0, 1, 1)]
driver.close()
PASSED.append("malformed pointer modifiers never reach the provider")

for action in [
    {"type": "move", "x": -1, "y": 0},
    {"type": "move", "x": 16, "y": 0},
    {"type": "move", "x": 0, "y": 12},
    {"type": "click", "x": 0, "y": 0, "button": "wheel"},
    {"type": "click", "x": 0, "y": 0, "button": "back"},
    {"type": "click", "x": 0, "y": 0, "button": "left", "keys": ["CTRL"]},
    {"type": "drag", "path": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]},
    {"type": "scroll", "x": 0, "y": 0, "scroll_x": 0, "scroll_y": 100},
    {"type": "keypress", "keys": ["a;printf injected"]},
    {"type": "keypress", "keys": ["constructor"]},
    {"type": "keypress", "keys": ["__proto__"]},
    {"type": "keypress", "keys": ["CTRL", "CTRL", "a"]},
    {"type": "type", "text": "\0"},
    {"type": "type", "text": "\ud800"},
    {"type": "type", "text": "a" * 4097},
]:
    state, _, driver, tool = fixture()
    before = len(state.calls)
    rejected(lambda tool=tool, action=action: tool.execute(call(action), before_action=lambda _: True))
    assert len(state.calls) == before
    driver.close()
    PASSED.append(f"refusal {len(PASSED)}")

for coordinate in [0.5, True]:
    state, _, driver, _ = fixture()
    before = len(state.calls)
    rejected(
        lambda driver=driver, coordinate=coordinate: driver.move(
            modern.Move.model_construct(type="move", x=coordinate, y=0)
        )
    )
    assert len(state.calls) == before
    driver.close()
    PASSED.append("direct noninteger coordinate refused")

state, _, driver, tool = fixture()
tool.execute(call({"type": "keypress", "keys": ["CTRL", "a"]}), before_action=lambda _: True)
tool.execute(call({"type": "keypress", "keys": ["ENTER"]}), before_action=lambda _: True)
tool.execute(call({"type": "keypress", "keys": ["PAGEUP"]}), before_action=lambda _: True)
assert state.keys == ["Control_L+a", "Return", "Page_Up"]
driver.close()
PASSED.append("safe chord")

state, _, driver, _ = fixture()
mutable_click = modern.Click.model_construct(type="click", x=0, y=0, button="left")


def change_pointer() -> None:
    mutable_click.x, mutable_click.y, mutable_click.button = 999, 999, "right"


state.after_size = change_pointer
driver.click(mutable_click)
assert state.clicks == [(0, 0, 1, 1)]
driver.close()
PASSED.append("validated pointer values survive caller mutation")

state, _, driver, _ = fixture()
action = modern.Type.model_construct(type="type", text="approved")
state.after_size = lambda: setattr(action, "text", "changed")
driver.type(action)
assert state.text == "approved"
driver.close()
PASSED.append("validated text survives caller mutation")

state, _, driver, _ = fixture()
state.after_size = lambda: setattr(state, "identity", "different")
rejected(lambda: driver.type(modern.Type.model_construct(type="type", text="refused")))
assert state.writes == 0
driver.close()
PASSED.append("identity change during size query prevents input")

for mode in ("left", "right", "double_click", "move", "type", "keypress"):
    state, _, driver, _ = fixture()
    if mode == "type":
        state.after_write = lambda state=state: setattr(state, "width", state.width + 1)
        rejected(lambda driver=driver: driver.type(modern.Type.model_construct(type="type", text="one local note")))
        assert state.writes == 1
    elif mode == "keypress":
        state.after_key = lambda state=state: setattr(state, "identity", "different")
        rejected(
            lambda driver=driver: driver.keypress(modern.Keypress.model_construct(type="keypress", keys=["Enter"]))
        )
        assert len(state.keys) == 1
    else:
        state.after_move = lambda state=state: setattr(state, "identity", "different")
        action = modern.Click.model_construct(type="click", x=0, y=0, keys=None, button=mode)
        if mode in ("left", "right"):
            rejected(lambda driver=driver, action=action: driver.click(action))
        else:
            rejected(lambda driver=driver, mode=mode, action=action: getattr(driver, mode)(action))
        assert state.clicks == []
    count = len(state.calls)
    rejected(lambda driver=driver: driver.type(modern.Type.model_construct(type="type", text="refused")))
    rejected(driver.screenshot)
    assert len(state.calls) == count
    driver.close()
    PASSED.append(f"changed identity or dimensions after {mode} retires before further input")

state, _, driver, tool = fixture()
text = "a" * 24 + "😀 ' \" $SDK_FIXTURE_WORD $(printf injected); end"
tool.execute(call({"type": "type", "text": text}), before_action=lambda _: True)
assert state.text == text and state.writes == 1
driver.close()
PASSED.append("Unicode and quoted text preserved in one command")

state, _, driver, tool = fixture()
before = len(state.calls)
rejected(
    lambda: tool.execute(
        call({"type": "click", "x": 0, "y": 0, "button": "left"}),
        before_action=lambda _: cast(bool, {"approved": True}),
    )
)
assert len(state.calls) == before
rejected(
    lambda: tool.execute(
        call({"type": "click", "x": 0, "y": 0, "button": "left"}), before_action=lambda _: True, cancelled=lambda: True
    )
)
assert len(state.calls) == before
driver.close()
PASSED.append("strict approval and Stop")

state, _, driver, tool = fixture()
state.fail_move = True
rejected(lambda: tool.execute(call({"type": "click", "x": 0, "y": 0, "button": "left"}), before_action=lambda _: True))
assert not state.clicks
before = len(state.calls)
rejected(lambda: driver.type(modern.Type.model_construct(type="type", text="refused")))
rejected(lambda: driver.keypress(modern.Keypress.model_construct(type="keypress", keys=["a"])))
assert len(state.calls) == before
driver.close()
PASSED.append("failed move never clicks and retires keyboard")

for kind in ["read", "invalid PNG", "ihdr-only", "no-iend", "oversize", "changed size", "changed identity", "remove"]:
    state, _, driver, _ = fixture()
    if kind == "read":
        state.fail_read = True
    if kind == "invalid PNG":
        state.image = b"invalid"
    if kind == "ihdr-only":
        state.image = PNG[:33]
    if kind == "no-iend":
        state.image = PNG[:-12]
    if kind == "oversize":
        state.image = b"x" * (8 * 1024 * 1024 + 1)
    if kind == "changed size":
        state.after_read = lambda state=state: setattr(state, "width", 17)
    if kind == "changed identity":
        state.after_read = lambda state=state: setattr(state, "identity", "different")
    if kind == "remove":
        state.fail_remove = True
    rejected(driver.screenshot)
    before = len(state.calls)
    rejected(lambda driver=driver: driver.type(modern.Type.model_construct(type="type", text="refused")))
    assert len(state.calls) == before
    assert len(state.files) == (1 if kind in ["remove", "changed identity"] else 0)
    state.identity, state.fail_remove = "local-fixture", False
    driver.close()
    assert not state.files
    PASSED.append("capture " + kind)

state, _, driver, _ = fixture()
state.hold_move = threading.Event()
errors: list[BaseException] = []


def pending_click() -> None:
    try:
        driver.click(modern.Click.model_construct(type="click", x=0, y=0, button="left"))
    except BaseException as error:
        errors.append(error)


worker = threading.Thread(target=pending_click, daemon=True)
worker.start()
try:
    assert state.move_entered.wait(2)
    rejected(lambda: driver.type(modern.Type.model_construct(type="type", text="refused")))
    rejected(driver.close)
finally:
    state.hold_move.set()
    worker.join(2)
assert not worker.is_alive() and not errors and len(state.clicks) == 1 and not state.text
driver.close()
PASSED.append("concurrent input and early close refused until drain")

state, _, driver, tool = fixture()
bodies: list[dict[str, Any]] = []


def respond(request: httpx.Request) -> httpx.Response:
    bodies.append(json.loads(request.content))
    output: list[dict[str, Any]] = (
        [
            call({"type": "click", "x": 0, "y": 0, "button": "left"}).model_dump(exclude_unset=True),
            {
                "type": "function_call",
                "id": "oracle",
                "call_id": "oracle",
                "name": "oracle",
                "arguments": "{}",
                "status": "completed",
            },
        ]
        if len(bodies) == 1
        else [
            {
                "type": "message",
                "id": "done",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": "done", "annotations": []}],
            }
        ]
    )
    return httpx.Response(
        200,
        json={
            "id": f"response_{len(bodies)}",
            "object": "response",
            "created_at": 0,
            "status": "completed",
            "model": "",
            "output": output,
        },
    )


with OpenAI(
    api_key="fixture",
    base_url="http://127.0.0.1:1",
    max_retries=0,
    http_client=httpx.Client(transport=httpx.MockTransport(respond)),
) as client:
    runner = ResponsesToolRunner(
        computer=tool,
        functions=[
            RegisteredFunction(
                tool={
                    "type": "function",
                    "name": "oracle",
                    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
                    "strict": True,
                },
                execute=lambda _: str(len(state.clicks)),
            )
        ],
    )
    runner.run(client, {"model": "", "input": "fixture"}, max_steps=3, before_action=lambda _: True)
assert len(bodies) == 2 and len(state.clicks) == 1
assert any(
    item.get("type") == "function_call_output" and item["call_id"] == "oracle" and item["output"] == "1"
    for item in bodies[1]["input"]
)
assert any(
    item.get("type") == "computer_call_output" and item["call_id"] == "computer_fixture" for item in bodies[1]["input"]
)
driver.close()
PASSED.append("mixed Responses preserves tool results")

print(
    json.dumps(
        {
            "passed": len(PASSED),
            "cases": PASSED,
            "provider": "installed E2B methods with controlled command/file facades",
            "realProviderRequests": 0,
            "realModelRequests": 0,
        }
    )
)
