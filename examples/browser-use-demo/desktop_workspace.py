"""The fixed Linux guest for Fieldwork; Run remains the sole lifecycle owner."""

from __future__ import annotations

import os
import sys
import json
import uuid
import base64
import shutil
import asyncio
import tempfile
import threading
from typing import TYPE_CHECKING, Any
from pathlib import Path
from collections.abc import Callable

sys.path.insert(1, str(Path(__file__).resolve().parents[1] / "computer-desktop"))
from runner import now
from desktop import Desktop, DesktopStartupError
from file_state import wait_for_decision

from openai import AsyncOpenAI
from openai.lib.computer import Screenshot, ComputerActionInput, AsyncComputerToolset
from openai.types.responses import Response, ResponseComputerToolCall
from openai.lib.responses_tool_runner import ResponsesToolCheckpoint, AsyncResponsesToolLedger, AsyncResponsesToolRunner

if TYPE_CHECKING:
    from runner import Run

TASK = (
    "This is an isolated Linux desktop with a local synthetic task. In the browser on the left, route D-2201. "
    "In the editor on the right, write exactly Desktop receipt D-2201 and save the open result.txt. "
    "Inspect the current screen before acting: a human may have completed part of the task. "
    "Do not repeat completed work. Stop once both results are present."
)
KEYS = {
    "Enter": ["ENTER"],
    "Tab": ["TAB"],
    "Backspace": ["BACKSPACE"],
    "Delete": ["DELETE"],
    "Escape": ["ESC"],
    "ArrowUp": ["ARROWUP"],
    "ArrowDown": ["ARROWDOWN"],
    "ArrowLeft": ["ARROWLEFT"],
    "ArrowRight": ["ARROWRIGHT"],
    "Home": ["HOME"],
    "End": ["END"],
    "PageUp": ["PAGEUP"],
    "PageDown": ["PAGEDOWN"],
    "Space": ["SPACE"],
    "ControlOrMeta+A": ["CTRL", "A"],
    "ControlOrMeta+S": ["CTRL", "S"],
}


def input_action(body: dict[str, Any], point: dict[str, int] | None) -> dict[str, Any] | None:
    fields = {"click": {"x", "y"}, "type": {"text"}, "key": {"key"}, "scroll": {"direction", "amount"}}
    action = body.get("action")
    if action not in fields or set(body) - ({"runId", "ownerVersion", "desktopId", "action"} | fields[action]):
        return None
    if action == "click":
        if all(type(body.get(name)) is int and 0 <= body[name] < bound for name, bound in (("x", 1024), ("y", 768))):
            return {"type": "click", "button": "left", "x": body["x"], "y": body["y"]}
    if action == "type":
        if type(body.get("text")) is str and 0 < len(body["text"]) <= 2000:
            return {"type": "type", "text": body["text"]}
    if action == "key" and body.get("key") in KEYS:
        return {"type": "keypress", "keys": KEYS[body["key"]]}
    if (
        action == "scroll"
        and point
        and body.get("direction") in ("up", "down", "left", "right")
        and type(body.get("amount")) is int
        and 1 <= body["amount"] <= 2048
    ):
        amount = body["amount"]
        x, y = {"left": (-amount, 0), "right": (amount, 0), "up": (0, -amount), "down": (0, amount)}[body["direction"]]
        return {"type": "scroll", "x": point["x"], "y": point["y"], "scroll_x": x, "scroll_y": y}
    return None


class DesktopWorkspace:
    def __init__(self, run: Run) -> None:
        self.run = run
        self.startup_stop = threading.Event()
        self.guest: Desktop | None = None
        self.creation: asyncio.Task[Desktop] | None = None
        self.capturing: asyncio.Task[Screenshot] | None = None
        self.scroll_target: dict[str, int] | None = None

    async def initialize(self) -> None:
        runtime = self.run.app.desktop_runtime
        assert runtime is not None
        self.creation = asyncio.create_task(asyncio.to_thread(Desktop, runtime, cancelled=self.startup_stop.is_set))
        self.guest = guest = await self.creation
        if self.run.owner != "agent" or self.run.phase_cancel.is_set():
            await self.run.close_owned(lambda: asyncio.to_thread(guest.stop))
            raise RuntimeError("Desktop startup ended.")
        await self.run.capture()

    async def retire(self) -> None:
        self.startup_stop.set()
        if self.creation:
            await asyncio.wait({self.creation})
            try:
                self.guest = self.creation.result()
            except DesktopStartupError:
                return
        if self.guest:
            await asyncio.to_thread(self.guest.stop)
        if self.capturing:
            await asyncio.wait({self.capturing})

    def binding(self) -> dict[str, Any] | None:
        run = self.run
        if not self.guest or run.owner == "stopped" or run.closed:
            return None
        return {"desktopId": run.id, "ownerVersion": run.version}

    def matches(self, binding: dict[str, Any] | None) -> bool:
        point = self.binding()
        return bool(
            point
            and binding
            and binding.get("desktopId") == point["desktopId"]
            and binding.get("ownerVersion") == point["ownerVersion"]
        )

    async def frame(self, *, cancelled: Callable[[], bool] | None = None) -> None:
        while self.capturing:
            previous = self.capturing
            # Drain an older poll under this waiter's budget, then obtain this owner's own pixels.
            await wait_for_decision(lambda previous=previous: asyncio.wait({previous}), cancelled)
            if self.capturing is previous:
                self.capturing = None
        point = self.binding()
        if not point or not self.guest:
            return
        # Read-only capture never creates an input lease.
        phase = self.run.phase_cancel if self.run.owner == "agent" else None
        self.capturing = asyncio.create_task(
            asyncio.to_thread(self.guest.capture_frame, cancelled=cancelled or (phase.is_set if phase else None))
        )
        work = self.capturing
        try:
            image = await wait_for_decision(lambda: asyncio.shield(work), cancelled)
            if (cancelled and cancelled()) or not self.matches(point):
                return
            assert "image_url" in image
            pixels = base64.b64decode(image["image_url"].removeprefix("data:image/png;base64,"), validate=True)
            run = self.run
            run.frame = pixels
            run.view_binding = point
            run.view = {
                "status": "live",
                "sequence": run.view["sequence"] + 1,
                "at": now(),
                "width": 1024,
                "height": 768,
            }
        finally:
            if self.capturing is work and work.done():
                self.capturing = None

    async def proof(self, *, cancelled: Callable[[], bool] | None = None, finalize: bool = False) -> dict[str, Any]:
        assert self.guest is not None
        phase = self.run.phase_cancel if self.run.owner == "agent" else None
        read = self.guest.seal if finalize else self.guest.verify
        result = await asyncio.to_thread(read, cancelled=cancelled or (phase.is_set if phase else None))
        return {
            "revision": result["browser_effects"],
            "finished": finalize or (result["browser_matches"] and result["file_matches"]),
            "verified": result["browser_matches"] and result["file_matches"],
            "results": {"browser_matches": result["browser_matches"], "file_matches": result["file_matches"]},
        }

    async def human_input(self, body: dict[str, Any]) -> None:
        assert self.guest is not None
        action = input_action(body, self.scroll_target)
        if not action:
            raise ValueError("Choose a valid bounded desktop input.")
        run = self.run
        version = run.version

        async def execute(computer: AsyncComputerToolset) -> None:
            item = str(uuid.uuid4())
            call = ResponseComputerToolCall.model_validate(
                {
                    "type": "computer_call",
                    "id": item,
                    "call_id": item,
                    "status": "completed",
                    "actions": [action],
                    "pending_safety_checks": [],
                }
            )
            await computer.execute(
                call, before_action=lambda _action: accepted(), cancelled=lambda: run.owner == "stopped"
            )

        async def accepted() -> bool:
            return run.owner in ("human", "draining-to-agent") and run.version in (version, version + 1)

        await self.guest.operation_async(execute)
        if action["type"] == "click" and run.owner == "human" and run.version == version:
            self.scroll_target = {"x": action["x"], "y": action["y"]}
        await run.capture()

    async def execute(self, client: AsyncOpenAI) -> str:
        assert self.guest is not None
        run = self.run
        approved = False
        directory = Path(tempfile.mkdtemp(prefix="fieldwork-desktop-"))
        saved_revision = 0
        phase_id = f"{run.id}:{run.version}"
        run.phase_index += 1
        try:

            async def save(checkpoint: ResponsesToolCheckpoint) -> None:
                nonlocal saved_revision
                if checkpoint["run_id"] != phase_id or checkpoint["revision"] <= saved_revision:
                    raise RuntimeError("The desktop checkpoint is not the next owned write.")
                temporary = directory / (str(uuid.uuid4()) + ".tmp")
                with temporary.open("x") as out:
                    os.chmod(out.fileno(), 0o600)
                    json.dump(checkpoint, out)
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(temporary, directory / "checkpoint.json")
                saved_revision = checkpoint["revision"]
                run.add("tools", f"Desktop phase {checkpoint['phase']}")
                run.record(
                    "tools",
                    phaseIndex=run.phase_index,
                    phase=checkpoint["phase"],
                    attempted=len(checkpoint["attempted_call_ids"]),
                    returned=len(checkpoint["returned_call_ids"]),
                )

            async def before_action(action: ComputerActionInput) -> bool:
                nonlocal approved
                if run.phase_cancel.is_set() or run.owner != "agent":
                    return False
                if action.type == "screenshot":
                    return True
                if not approved:
                    approved = await run.ask(
                        "Let this agent phase route D-2201 and save the fixed receipt in the isolated desktop"
                    )
                return approved and not run.phase_cancel.is_set() and run.owner == "agent"

            async def safety(_call: ResponseComputerToolCall) -> bool:
                return await run.ask("Approve the pending desktop action flagged by the API safety check")

            initial = await self.proof()
            if initial["verified"]:
                run.result = "verified" if (await self.proof(finalize=True))["verified"] else "unverified"
                return run.result

            async def phase(computer: AsyncComputerToolset) -> Response:
                assert run.screenshot is not None
                model = run.app.models["responses"]
                assert model is not None
                runner = AsyncResponsesToolRunner(computer=computer)
                return await runner.run(
                    client,
                    {
                        "model": model,
                        "store": False,
                        "input": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "input_text", "text": TASK},
                                    {
                                        "type": "input_image",
                                        "image_url": "data:image/png;base64,"
                                        + base64.b64encode(run.screenshot).decode(),
                                        "detail": "auto",
                                    },
                                ],
                            }
                        ],
                    },
                    max_steps=run.step_limit - run.turns,
                    cancelled=run.phase_cancel.is_set,
                    on_diagnostic=run.diagnostics.event,
                    before_action=before_action,
                    approve_safety_checks=safety,
                    ledger=AsyncResponsesToolLedger(run_id=phase_id, save=save),
                )

            await self.guest.operation_async(phase)
            final = await self.proof()
            if final["verified"]:
                final = await self.proof(finalize=True)
            run.result = "verified" if final["verified"] else "unverified"
            return run.result
        finally:
            # Caller reaches here only after the admitted complete SDK work settles.
            async def close_ledger() -> None:
                shutil.rmtree(directory)

            await run.close_owned(close_ledger)
