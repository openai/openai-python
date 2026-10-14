"""No-key real desktop exercise. Run with an installed SDK and the local image."""

from __future__ import annotations

import json
import time
import base64
import signal
import struct
import asyncio
import argparse
import threading
import traceback
from io import BytesIO
from typing import Callable, cast
from pathlib import Path
from unittest.mock import patch
from typing_extensions import override
from concurrent.futures import TimeoutError as FutureTimeoutError, ThreadPoolExecutor

from desktop import Desktop

from openai.lib.computer import (
    ComputerToolset,
    ComputerUseError,
    ComputerActionInput,
    AsyncComputerToolset,
)
from openai.types.responses import ResponseComputerToolCall, computer_action as action
from openai.types.responses.response_input_param import ComputerCallOutput
from openai.types.responses.response_computer_tool_call import PendingSafetyCheck

EMPTY = {"browser_matches": False, "file_matches": False, "file_empty": True, "browser_effects": 0}
COMPLETE = {"browser_matches": True, "file_matches": True, "file_empty": False, "browser_effects": 1}


def call(*actions: action.ComputerAction, check: bool = False) -> ResponseComputerToolCall:
    return ResponseComputerToolCall(
        id="desktop-local",
        call_id="call-desktop-local",
        type="computer_call",
        status="completed",
        pending_safety_checks=(
            [PendingSafetyCheck(id="local-confirm", code="fixture", message="Confirm fixture input")] if check else []
        ),
        actions=list(actions),
    )


def screenshot(output: ComputerCallOutput) -> bytes:
    value = output["output"].get("image_url")
    assert isinstance(value, str) and value.startswith("data:image/png;base64,")
    png = base64.b64decode(value.removeprefix("data:image/png;base64,"), validate=True)
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1024, 768)
    return png


def route() -> action.Click:
    return action.Click(type="click", button="left", x=200, y=215)


def workflow(separator: str = "\n") -> ResponseComputerToolCall:
    # Exercise all nine native actions. Leave exactly one receipt via the editor UI.
    return call(
        action.Move(type="move", x=100, y=400),
        action.Move(type="move", x=100, y=400),
        action.Wait(type="wait"),
        action.Scroll(type="scroll", x=100, y=400, scroll_x=0, scroll_y=120),
        action.Scroll(type="scroll", x=140, y=400, scroll_x=0, scroll_y=-120),
        action.Click(type="click", button="left", x=700, y=180),
        action.Type(type="type", text="scratch"),
        action.DoubleClick(type="double_click", x=700, y=180),
        action.Drag(type="drag", path=[action.DragPath(x=700, y=180), action.DragPath(x=740, y=180)]),
        action.Keypress(type="keypress", keys=["CTRL", "A"]),
        action.Type(type="type", text=f"Desktop receipt{separator}D-2201"),
        action.Keypress(type="keypress", keys=["HOME"]),
        action.Keypress(type="keypress", keys=["BACKSPACE"]),
        action.Type(type="type", text=" "),
        action.Keypress(type="keypress", keys=["CTRL", "S"]),
        action.Wait(type="wait"),
        # Complete the browser ticket last, after all editor work.
        route(),
        action.Screenshot(type="screenshot"),
    )


def run_sync(runtime_dir: Path) -> None:
    desktop = Desktop(runtime_dir)
    try:
        assert desktop.verify() == EMPTY
        screenshot(desktop.operation(lambda tools: tools.execute(call(action.Screenshot(type="screenshot")))))
        try:
            desktop.operation(lambda tools: tools.execute(call(route(), check=True)))
        except ComputerUseError:
            pass
        else:
            raise AssertionError("SDK did not deny the unapproved safety check")
        assert desktop.verify() == EMPTY, "Denied input reached the fixture"
        assert not desktop.uncertain_effects

        try:
            desktop.operation(lambda tools: tools.execute(call(route()), before_action=lambda _: False))
        except ComputerUseError:
            pass
        else:
            raise AssertionError("SDK did not deny the before_action")
        assert desktop.verify() == EMPTY, "Denied input reached the fixture"
        assert not desktop.uncertain_effects

        desktop.operation(
            lambda tools: tools.execute(
                call(
                    action.Click(type="click", button="left", x=700, y=180),
                    action.Type(type="type", text="synthetic fixture " * 192 + "\nDesktop receipt D-2201"),
                    action.Keypress(type="keypress", keys=["CTRL", "S"]),
                )
            )
        )
        long_text = desktop.verify()
        for _ in range(5):
            if not long_text["file_empty"]:
                break
            # Wait for the actual local editor save receipt, within five normal GUI waits.
            desktop.operation(lambda tools: tools.execute(call(action.Wait(type="wait"))))
            long_text = desktop.verify()
        assert not long_text["file_empty"] and not long_text["file_matches"]
        assert not long_text["browser_matches"] and long_text["browser_effects"] == 0
        # Removing the prefix through the editor proves the exact suffix after character 2,000 reached the file.
        desktop.operation(
            lambda tools: tools.execute(
                call(
                    action.Keypress(type="keypress", keys=["HOME"]),
                    action.Keypress(type="keypress", keys=["CTRL", "SHIFT", "HOME"]),
                    action.Keypress(type="keypress", keys=["BACKSPACE"]),
                    action.Keypress(type="keypress", keys=["CTRL", "S"]),
                )
            )
        )
        assert desktop.verify()["file_matches"], "The suffix after character 2,000 was not saved in full"

        screenshot(desktop.operation(lambda tools: tools.execute(workflow(), before_action=lambda _: True)))
        assert desktop.verify() == COMPLETE, "Browser route or editor save did not reach the fixed fixture"
        try:
            desktop.operation(lambda tools: tools.execute(call(action.Type(type="type", text="Late edit"))))
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Input reached an already completed workspace")
        assert desktop.verify() == COMPLETE
        assert not desktop.uncertain_effects
        assert desktop.seal() == COMPLETE
        final_frame = screenshot(
            desktop.operation(lambda tools: tools.execute(call(action.Screenshot(type="screenshot"))))
        )
        for proposal in (
            call(route()),
            call(action.Type(type="type", text="Late edit"), action.Keypress(type="keypress", keys=["CTRL", "S"])),
        ):

            def execute(tools: ComputerToolset, proposal: ResponseComputerToolCall = proposal) -> ComputerCallOutput:
                return tools.execute(proposal, before_action=lambda _: True)

            try:
                desktop.operation(execute)
            except ComputerUseError:
                pass
            else:
                raise AssertionError("Sealed desktop admitted input that could change the proof")
        assert desktop.verify() == COMPLETE and desktop.seal() == COMPLETE
        assert (
            screenshot(desktop.operation(lambda tools: tools.execute(call(action.Screenshot(type="screenshot")))))
            == final_frame
        )
        assert not desktop.uncertain_effects
        print("PASS: terminal seal holds the file/browser proof and saved frame after refused late inputs")

        # Block a sentinel before action. Stop must complete even if approval never returns.
        entered = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []

        def approval(_: ComputerActionInput) -> bool:
            entered.set()
            assert release.wait(20), "Exercise approval timed out"
            return True

        def pending() -> None:
            try:
                desktop.operation(lambda tools: tools.execute(call(route()), before_action=approval))
            except BaseException as exc:
                errors.append(exc)

        thread = threading.Thread(target=pending)
        thread.start()
        assert entered.wait(5), "SDK never reached the approval"
        desktop.stop()
        release.set()
        thread.join(5)
        assert not thread.is_alive() and len(errors) == 1 and isinstance(errors[0], ComputerUseError)
        called = False

        def after_stop(tools: ComputerToolset) -> ComputerCallOutput:
            nonlocal called
            called = True
            return tools.execute(call(route()))

        try:
            desktop.operation(after_stop)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Stopped desktop admitted another operation")
        assert not called
        assert not desktop.uncertain_effects
    finally:
        desktop.stop()


async def run_async(runtime_dir: Path) -> None:
    desktop = await asyncio.to_thread(Desktop, runtime_dir)
    try:
        assert await asyncio.to_thread(desktop.verify) == EMPTY

        async def capture(tools: AsyncComputerToolset) -> ComputerCallOutput:
            return await tools.execute(call(action.Screenshot(type="screenshot")))

        screenshot(await desktop.operation_async(capture))

        async def needs_approval(tools: AsyncComputerToolset) -> ComputerCallOutput:
            return await tools.execute(call(route(), check=True))

        try:
            await desktop.operation_async(needs_approval)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("SDK did not deny the unapproved safety check")
        assert await asyncio.to_thread(desktop.verify) == EMPTY
        assert not desktop.uncertain_effects

        async def refuse(_: ComputerActionInput) -> bool:
            return False

        async def denied(tools: AsyncComputerToolset) -> ComputerCallOutput:
            return await tools.execute(call(route()), before_action=refuse)

        try:
            await desktop.operation_async(denied)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("SDK did not deny the before_action")
        assert await asyncio.to_thread(desktop.verify) == EMPTY
        assert not desktop.uncertain_effects

        async def approve(_: ComputerActionInput) -> bool:
            return True

        async def perform(tools: AsyncComputerToolset) -> ComputerCallOutput:
            return await tools.execute(workflow("\r\n"), before_action=approve)

        screenshot(await desktop.operation_async(perform))
        assert await asyncio.to_thread(desktop.verify) == COMPLETE
        assert not desktop.uncertain_effects
        assert await asyncio.to_thread(desktop.seal) == COMPLETE
        final_frame = screenshot(await desktop.operation_async(capture))

        async def late_input(tools: AsyncComputerToolset) -> ComputerCallOutput:
            return await tools.execute(call(route()), before_action=approve)

        try:
            await desktop.operation_async(late_input)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Sealed desktop admitted another input")
        assert await asyncio.to_thread(desktop.verify) == COMPLETE
        assert screenshot(await desktop.operation_async(capture)) == final_frame

        entered = asyncio.Event()
        release = asyncio.Event()

        async def pending_approval(_: ComputerActionInput) -> bool:
            entered.set()
            await release.wait()
            return True

        async def sentinel(tools: AsyncComputerToolset) -> ComputerCallOutput:
            return await tools.execute(call(route()), before_action=pending_approval)

        pending = asyncio.create_task(desktop.operation_async(sentinel))
        await asyncio.wait_for(entered.wait(), timeout=5)
        await asyncio.to_thread(desktop.stop)

        release.set()
        try:
            await asyncio.wait_for(pending, timeout=5)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Pending sentinel ran after Stop")
        called = False

        async def after_stop(tools: AsyncComputerToolset) -> ComputerCallOutput:
            nonlocal called
            called = True
            return await tools.execute(call(route()))

        try:
            await desktop.operation_async(after_stop)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Stopped desktop admitted another operation")
        assert not called
        assert not desktop.uncertain_effects
    finally:
        await asyncio.to_thread(desktop.stop)


def check_frames(*, phase_only: bool = False, startup_only: bool = False) -> None:
    from PIL import Image

    stream = BytesIO()
    Image.new("RGB", (1024, 768)).save(stream, format="PNG")
    png = stream.getvalue()

    class ControlledGuest:
        def __init__(self, _runtime_dir: Path, *, cancelled: Callable[[], bool] | None = None) -> None:
            if cancelled is not None and cancelled():
                raise ComputerUseError("Controlled startup was cancelled")
            self.id = "local-frame-fixture"
            self.frame = png
            self.removed = False
            self.requests: list[str] = []
            self.viewer_entered: threading.Event | None = None
            self.viewer_release: threading.Event | None = None
            self.held_kind: str | None = None
            self.input_entered = threading.Event()
            self.input_release = threading.Event()
            self.interruption: BaseException | None = None
            self.raw_reply: bytes | None = None

        def healthy(self, *, cancelled: Callable[[], bool] | None = None) -> bool:
            del cancelled
            return not self.removed

        def exchange(
            self, data: bytes, *, timeout: float, limit: int, cancelled: Callable[[], bool] | None = None
        ) -> bytes:
            assert timeout > 0 and limit > 0
            kind = json.loads(data)["type"]
            self.requests.append(kind)
            if kind != "ready" and self.raw_reply is not None:
                return self.raw_reply
            if kind == "type" and self.interruption is not None:
                raise self.interruption
            if kind == self.held_kind:
                self.input_entered.set()
                end = time.monotonic() + 2
                while not self.input_release.wait(0.01):
                    if cancelled is not None and cancelled():
                        raise ComputerUseError("Synthetic exchange interrupted")
                    if time.monotonic() >= end:
                        raise AssertionError("Controlled exchange was not released")
            result: dict[str, object] = {"ok": True}
            if kind in ("verify", "seal"):
                result.update(COMPLETE)
            if kind == "screenshot":
                if self.viewer_entered is not None and self.viewer_release is not None:
                    self.viewer_entered.set()
                    assert self.viewer_release.wait(timeout=2), "Controlled viewer was never released."
                result["image_url"] = "data:image/png;base64," + base64.b64encode(self.frame).decode()
            return json.dumps(result).encode()

        def remove(self) -> None:
            self.removed = True

    interrupted = threading.Event()
    guests: list[ControlledGuest] = []

    class StartingGuest(ControlledGuest):
        def __init__(self, runtime_dir: Path, *, cancelled: Callable[[], bool] | None = None) -> None:
            super().__init__(runtime_dir, cancelled=cancelled)
            self.held_kind = "ready"
            guests.append(self)

        @override
        def exchange(
            self, data: bytes, *, timeout: float, limit: int, cancelled: Callable[[], bool] | None = None
        ) -> bytes:
            interrupted.set()
            return super().exchange(data, timeout=timeout, limit=limit, cancelled=cancelled)

    with patch("desktop.Guest", StartingGuest):
        before = time.monotonic()
        try:
            Desktop(Path("controlled-fixture"), cancelled=interrupted.is_set)
        except ComputerUseError:
            pass
        else:
            raise AssertionError("Stopped startup returned a usable desktop")
        assert time.monotonic() - before < 1.5, "Stopped readiness waited for the exchange timeout"
        assert len(guests) == 1 and guests[0].removed
        assert guests[0].requests == ["ready"]
        print("PASS: cancelled readiness removes its one guest promptly without any input")

    import container_runtime
    from desktop import DesktopStartupError

    for error in (container_runtime.StartupCancelled("Cancelled after cleanup"), KeyboardInterrupt(), SystemExit()):
        with patch("desktop.Guest", side_effect=error):
            try:
                Desktop(Path("controlled-fixture"))
            except DesktopStartupError:
                assert isinstance(error, container_runtime.StartupCancelled)
            except BaseException as actual:
                assert not isinstance(error, container_runtime.StartupCancelled) and actual is error
            else:
                raise AssertionError("Interrupted construction returned a desktop")

    previous = {name: signal.getsignal(name) for name in (signal.SIGINT, signal.SIGTERM)}
    try:
        for first, second in ((signal.SIGINT, signal.SIGTERM), (signal.SIGTERM, signal.SIGINT)):
            stopped = KeyboardInterrupt(f"original {first.name}")
            started: list[ControlledGuest] = []

            def interrupt(_signum: int, _frame: object, *, stopped: KeyboardInterrupt = stopped) -> None:
                raise stopped

            signal.signal(signal.SIGINT, interrupt)
            signal.signal(signal.SIGTERM, interrupt)

            class RepeatedSignalGuest(ControlledGuest):
                instances = started
                startup_signal = first
                cleanup_signal = second

                @override
                def healthy(self, *, cancelled: Callable[[], bool] | None = None) -> bool:
                    self.instances.append(self)
                    signal.raise_signal(self.startup_signal)
                    raise AssertionError("Startup signal returned")

                @override
                def remove(self) -> None:
                    signal.raise_signal(self.cleanup_signal)
                    super().remove()

            with patch("desktop.Guest", RepeatedSignalGuest):
                try:
                    Desktop(Path("controlled-fixture"))
                except KeyboardInterrupt as error:
                    assert error is stopped, "Constructor cleanup replaced the original interruption"
                else:
                    raise AssertionError("Interrupted readiness returned a desktop")
                assert len(started) == 1 and started[0].removed
                assert signal.getsignal(signal.SIGINT) is interrupt
                assert signal.getsignal(signal.SIGTERM) is interrupt
        print(
            "PASS: repeated SIGINT/SIGTERM during failed constructor cleanup preserve the interruption and remove its guest"
        )
    finally:
        for name, handler in previous.items():
            signal.signal(name, handler)
    if startup_only:
        return

    with patch("desktop.Guest", ControlledGuest):
        for asynchronous in (False, True):
            for kind in ("verify", "seal", "operation"):
                desktop = Desktop(Path("controlled-fixture"))
                guest = cast(ControlledGuest, cast(object, desktop._guest))
                phase_call = call(action.Type(type="type", text="stale phase"))

                async def exercise_phase(
                    *,
                    asynchronous: bool = asynchronous,
                    kind: str = kind,
                    desktop: Desktop = desktop,
                    guest: ControlledGuest = guest,
                    selected: ResponseComputerToolCall = phase_call,
                ) -> None:
                    consent = asyncio.Event()
                    reached = asyncio.Event()
                    pending: asyncio.Task[ComputerCallOutput] | None = None
                    escaped: ComputerToolset | AsyncComputerToolset

                    async def hold(_action: ComputerActionInput) -> bool:
                        reached.set()
                        await consent.wait()
                        return True

                    if asynchronous:

                        async def start(tools: AsyncComputerToolset) -> AsyncComputerToolset:
                            nonlocal pending
                            pending = asyncio.create_task(tools.execute(selected, before_action=hold))
                            return tools

                        escaped = await desktop.operation_async(start)
                        await reached.wait()
                    else:
                        escaped = desktop.operation(lambda tools: tools)

                    with ThreadPoolExecutor(max_workers=1) as pool:
                        released = threading.Event()
                        entered = threading.Event()
                        if kind == "operation":

                            def later(tools: ComputerToolset) -> ComputerCallOutput:
                                entered.set()
                                assert released.wait(timeout=2)
                                return tools.execute(selected)

                            running = pool.submit(desktop.operation, later)
                            assert await asyncio.to_thread(entered.wait, 2)
                        else:
                            guest.held_kind = kind
                            running = pool.submit(getattr(desktop, kind))
                            assert await asyncio.to_thread(guest.input_entered.wait, 2)
                        try:
                            consent.set()
                            try:
                                if asynchronous:
                                    assert pending is not None
                                    await asyncio.wait_for(pending, timeout=0.6)
                                else:
                                    assert isinstance(escaped, ComputerToolset)
                                    escaped.execute(selected)
                            except ComputerUseError:
                                pass
                            else:
                                raise AssertionError("Stale computer dispatched during another operation")
                            assert guest.requests.count("type") == 0 and not guest.removed
                        finally:
                            consent.set()
                            released.set()
                            guest.input_release.set()
                            running.result(timeout=2)
                    assert guest.requests.count("type") == (1 if kind == "operation" else 0)
                    assert not desktop.uncertain_effects

                try:
                    asyncio.run(exercise_phase())
                finally:
                    desktop.stop()
                assert guest.removed
        print("PASS: old sync/async tools refuse verify, seal and later input phases; current operations remain usable")
        if phase_only:
            return
        for operation in ("verify", "seal"):
            for bad in (
                {"file_matches": "false", "browser_matches": "false"},
                {"file_empty": None},
                {"browser_effects": True},
                {"browser_effects": -1},
                {"browser_effects": 2**53},
            ):
                desktop = Desktop(Path("controlled-fixture"))
                guest = cast(ControlledGuest, cast(object, desktop._guest))
                guest.raw_reply = json.dumps({"ok": True, **COMPLETE, **bad}).encode()
                try:
                    getattr(desktop, operation)()
                except ComputerUseError:
                    pass
                else:
                    raise AssertionError("Invalid proof was exposed")
                assert guest.removed and not desktop.uncertain_effects
                try:
                    desktop.verify()
                except ComputerUseError:
                    pass
                else:
                    raise AssertionError("Malformed proof permitted reuse")
            desktop = Desktop(Path("controlled-fixture"))
            guest = cast(ControlledGuest, cast(object, desktop._guest))
            guest.raw_reply = json.dumps(
                {"ok": True, **COMPLETE, "browser_effects": None, "browser_matches": False}
            ).encode()
            try:
                result = getattr(desktop, operation)()
                assert result["browser_effects"] is None and result["browser_matches"] is False
            finally:
                desktop.stop()
        print("PASS: verify/seal reject malformed proof; null oversize count never verifies")
        for raw in (b'{"ok":invalid,"record":"SYNTHETIC_8738"}', b'{"ok":true,"record":"SYNTHETIC_8738\xff"}'):
            desktop = Desktop(Path("controlled-fixture"))
            guest = cast(ControlledGuest, cast(object, desktop._guest))
            guest.raw_reply = raw
            try:
                try:
                    desktop.verify()
                except ComputerUseError as error:
                    assert "Invalid desktop reply" in str(error)
                    assert "SYNTHETIC_8738" not in repr(error) + "".join(traceback.format_exception(error))
                    assert error.__cause__ is None and error.__context__ is None, (
                        "Invalid desktop reply retains a parser exception"
                    )
                else:
                    raise AssertionError("Malformed reply returned a proof")
                assert guest.removed
            finally:
                desktop.stop()
        print("PASS: malformed JSON and UTF-8 replies retain no exposed parser cause or result")
        for interruption in (KeyboardInterrupt(), SystemExit(), BaseException("Synthetic interruption")):
            desktop = Desktop(Path("controlled-fixture"))
            guest = cast(ControlledGuest, cast(object, desktop._guest))
            guest.interruption = interruption
            try:
                try:
                    desktop.operation(
                        lambda tools: tools.execute(call(action.Type(type="type", text="Synthetic note")))
                    )
                except BaseException as error:
                    assert error is interruption
                else:
                    raise AssertionError("Transport interruption was swallowed")
                assert desktop.uncertain_effects and guest.removed
                before = len(guest.requests)
                try:
                    desktop.verify()
                except ComputerUseError:
                    pass
                else:
                    raise AssertionError("Interrupted input left desktop reusable")
                assert len(guest.requests) == before
            finally:
                desktop.stop()
        print("PASS: three transport interruptions preserve the error and retire uncertain input")

        desktop = Desktop(Path("controlled-fixture"))
        try:
            assert desktop.verify() == COMPLETE
            assert desktop.seal() == COMPLETE
            assert desktop.verify() == COMPLETE
        finally:
            desktop.stop()
        print("PASS: verify and seal return the same public fixed-record proof for a confirmed guest reply")

        for mode, frame in [("complete", png), ("ihdr-only", png[:33]), ("no-iend", png[:-12]), ("invalid", b"Hi")]:
            for view in (True, False):
                desktop = Desktop(Path("controlled-fixture"))
                guest = cast(ControlledGuest, cast(object, desktop._guest))
                guest.frame = frame
                try:
                    if view:
                        desktop.capture_frame()
                    else:
                        desktop.operation(lambda tools: tools.execute(call(action.Screenshot(type="screenshot"))))
                except ComputerUseError:
                    assert mode != "complete"
                    assert guest.removed and not desktop.uncertain_effects
                    before = len(guest.requests)
                    try:
                        desktop.verify()
                    except ComputerUseError:
                        pass
                    else:
                        raise AssertionError("Malformed frame left desktop reusable")
                    assert len(guest.requests) == before
                else:
                    assert mode == "complete" and not guest.removed
                finally:
                    desktop.stop()
        print("PASS: valid and 3 invalid frames, viewer and SDK; invalid capture retires before further work")

        for kind in ("verify", "seal"):
            for before in (True, False):
                desktop = Desktop(Path("controlled-fixture"))
                guest = cast(ControlledGuest, cast(object, desktop._guest))

                def verify_cancelled(
                    *, before: bool = before, guest: ControlledGuest = guest, kind: str = kind
                ) -> bool:
                    return before or kind in guest.requests

                try:
                    try:
                        getattr(desktop, kind)(cancelled=verify_cancelled)
                    except ComputerUseError:
                        pass
                    else:
                        raise AssertionError("Verification published after cancellation")
                    assert guest.requests.count(kind) == (0 if before else 1)
                    assert not desktop.uncertain_effects
                    assert guest.removed is (kind == "seal" and not before)
                    if not guest.removed:
                        desktop.verify()
                finally:
                    desktop.stop()
        print("PASS: verify/seal cancellation publishes no result; only a dispatched seal retires the guest")

        desktop = Desktop(Path("controlled-fixture"))
        guest = cast(ControlledGuest, cast(object, desktop._guest))
        guest.viewer_entered = threading.Event()
        guest.viewer_release = threading.Event()
        with ThreadPoolExecutor(max_workers=2) as pool:
            viewing = pool.submit(desktop.capture_frame)
            assert guest.viewer_entered.wait(timeout=2)
            stopping = pool.submit(desktop.stop)
            try:
                try:
                    stopping.result(timeout=0.05)
                except FutureTimeoutError:
                    pass
                else:
                    raise AssertionError("Stop returned with a viewer still inside its exchange")
                assert not guest.removed and not desktop.uncertain_effects
            finally:
                guest.viewer_release.set()
            stopping.result(timeout=2)
            try:
                viewing.result(timeout=2)
            except ComputerUseError:
                pass
            else:
                raise AssertionError("An interrupted view returned a usable frame")
        observed = (guest.removed, desktop.uncertain_effects)
        assert observed == (True, False)
        print("PASS: Stop drains viewer transport before removal without marking read-only work uncertain")

        for asynchronous in (False, True):
            for kind in ("type", "screenshot"):
                for owner_stop in (False, True):
                    desktop = Desktop(Path("controlled-fixture"))
                    guest = cast(ControlledGuest, cast(object, desktop._guest))
                    guest.held_kind = kind
                    stopped = threading.Event()
                    selected: action.Type | action.Screenshot = (
                        action.Type(type="type", text="Synthetic note")
                        if kind == "type"
                        else action.Screenshot(type="screenshot")
                    )

                    def execute(
                        *,
                        asynchronous: bool = asynchronous,
                        desktop: Desktop = desktop,
                        selected: action.Type | action.Screenshot = selected,
                        stopped: threading.Event = stopped,
                    ) -> None:
                        if asynchronous:

                            async def work(tools: AsyncComputerToolset) -> ComputerCallOutput:
                                return await tools.execute(call(selected), cancelled=stopped.is_set)

                            asyncio.run(desktop.operation_async(work))
                        else:
                            desktop.operation(lambda tools: tools.execute(call(selected), cancelled=stopped.is_set))

                    with ThreadPoolExecutor(max_workers=2) as pool:
                        active = pool.submit(execute)
                        assert guest.input_entered.wait(timeout=2)
                        assert guest.requests == ["ready", kind], guest.requests
                        phase_stopping = pool.submit(desktop.stop) if owner_stop else None
                        if not owner_stop:
                            stopped.set()
                        try:
                            try:
                                active.result(timeout=0.8)
                            except ComputerUseError:
                                pass
                            else:
                                raise AssertionError("Cancelled interactive exchange returned a result")
                            if phase_stopping is not None:
                                phase_stopping.result(timeout=0.8)
                        finally:
                            guest.input_release.set()
                        phase_observed = (guest.removed, desktop.uncertain_effects)
                        assert phase_observed == (True, kind == "type"), phase_observed
                    desktop.stop()
        print("PASS: 8 sync/async active exchanges see phase or owner Stop, retain exact effect uncertainty")

        async def check_case(asynchronous: bool, before: bool) -> None:
            desktop = Desktop(Path("controlled-fixture"))
            guest = cast(ControlledGuest, cast(object, desktop._guest))
            cancelled = lambda: before or "type" in guest.requests
            try:
                if asynchronous:

                    async def work(tools: AsyncComputerToolset) -> ComputerCallOutput:
                        return await tools.execute(
                            call(action.Type(type="type", text="Synthetic note")), cancelled=cancelled
                        )

                    await desktop.operation_async(work)
                else:
                    desktop.operation(
                        lambda tools: tools.execute(
                            call(action.Type(type="type", text="Synthetic note")), cancelled=cancelled
                        )
                    )
            except ComputerUseError:
                pass
            else:
                raise AssertionError("Cancelled desktop operation returned a result")
            assert not desktop.uncertain_effects
            assert guest.requests.count("type") == (0 if before else 1)
            assert guest.removed is not before
            if before:
                desktop.verify()
            else:
                count = len(guest.requests)
                try:
                    desktop.verify()
                except ComputerUseError:
                    pass
                else:
                    raise AssertionError("Cancelled dispatched input left the desktop reusable")
                assert len(guest.requests) == count
            desktop.stop()

        async def check_cancellation() -> None:
            for asynchronous in (False, True):
                for before in (False, True):
                    await check_case(asynchronous, before)
            print("PASS: sync/async cancelled before dispatch permits reuse; after confirmed dispatch retires")

        asyncio.run(check_cancellation())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the fixed isolated desktop exercise without an API key.")
    parser.add_argument("--runtime-dir", type=Path)
    parser.add_argument("--check-frames", action="store_true", help="Check controlled local screenshot replies; no VM.")
    args = parser.parse_args()
    if args.check_frames:
        check_frames()
        raise SystemExit(0)
    if args.runtime_dir is None:
        parser.error("--runtime-dir is required for the real guest exercise")
    try:
        run_sync(args.runtime_dir)
        asyncio.run(run_async(args.runtime_dir))
    except ComputerUseError:
        raise SystemExit(
            "Desktop exercise failed: startup or an operation was refused or uncertain. "
            "Check the fixed guest's startup and the failing action. No success claim is available."
        ) from None
    print("PASS: sync and async; PNG; denied checks; browser and file; Stop and post-Stop sentinel")
