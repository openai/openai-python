"""Finite local mixed Stop and task capability checks. No API or VM."""

from __future__ import annotations

import sys
import json
import asyncio
import threading
from typing import cast
from pathlib import Path
from collections.abc import Callable, Awaitable

sys.path[:0] = [
    str(Path(__file__).resolve().parents[1] / "browser"),
    str(Path(__file__).resolve().parents[1] / "computer-desktop"),
]
import httpx2
from runner import Run
from desktop import Desktop
from mixed_session import Dispatch, MixedSession
from browser_driver import PlaywrightBrowser
from playwright.async_api import ElementHandle

from openai import AsyncOpenAI
from openai.lib.browser import BrowserReadV1, ReadPageInput, BrowserCancelledError
from openai.lib.computer import ComputerUseError, AsyncComputerDriver, AsyncComputerToolset
from openai.lib.responses_tool_runner import ResponsesToolCheckpoint, AsyncResponsesToolLedger

checks: list[str] = []
failures: list[dict[str, str]] = []


async def check(name: str, body: Callable[[], Awaitable[None]]) -> None:
    try:
        await body()
        checks.append(name)
    except Exception as error:
        failures.append({"name": name, "error": str(error), "type": type(error).__name__})


async def capability(task_id: str) -> None:
    run = object.__new__(Run)
    run.task_id, run.version, run.owner = task_id, 0, "agent"
    run.phase_cancel = asyncio.Event()
    names = sorted(tool["name"] for tool in run.toolset("agent").tools)
    required = [
        "browser_list_tabs",
        "browser_read_page",
        "browser_get_page_text",
        "browser_switch_tab",
        "browser_click",
        "browser_type",
        "browser_select_option",
    ]
    if task_id in ("support", "stock"):
        required.append("browser_screenshot")
    assert names == sorted(required), (task_id, names)


class Host:
    routes = 0
    results = 0
    browser_routed = False


class Driver:
    active = "tab"


async def approval(_label: str) -> bool:
    return True


async def initial_read() -> None:
    entered, release = asyncio.Event(), asyncio.Event()
    requests: list[httpx2.Request] = []

    class HeldDriver(Driver):
        async def read_page(
            self, _args: ReadPageInput, *, cancelled: Callable[[], bool] | None = None
        ) -> BrowserReadV1:
            entered.set()
            while not release.is_set():
                if cancelled is not None and cancelled():
                    raise BrowserCancelledError("Controlled read interrupted")
                try:
                    await asyncio.wait_for(release.wait(), 0.02)
                except asyncio.TimeoutError:
                    # Check cancellation again after the bounded wait.
                    pass
            return {"version": 1, "text": "local", "elements": [], "omitted": []}

    class Guest:
        async def screenshot(self) -> dict[str, str]:
            return {"type": "computer_screenshot", "image_url": "data:image/png;base64,AA=="}

        async def effect(self, _action: object) -> None:
            raise AssertionError("Historical observation must not act")

        click = double_click = drag = keypress = move = scroll = type = wait = effect

    async def transport(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        raise AssertionError("Stopped initial observation sent a model request")

    async def save(_record: ResponsesToolCheckpoint) -> None:
        raise AssertionError("Stopped initial observation wrote a ledger")

    current = MixedSession(
        cast(Dispatch, Host()), cast(PlaywrightBrowser, HeldDriver()), cast(ElementHandle, None), approval
    )
    current.ledger = AsyncResponsesToolLedger("fixture", save)
    async with AsyncOpenAI(
        api_key="synthetic", max_retries=0, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport))
    ) as client:
        pending = asyncio.create_task(
            current._run(AsyncComputerToolset(cast(AsyncComputerDriver, Guest())), client, "")
        )
        try:
            await asyncio.wait_for(entered.wait(), 1)
            current.stop()
            try:
                await asyncio.wait_for(asyncio.shield(pending), 0.5)
            except BrowserCancelledError:
                # Stopping initial inspection may interrupt this read.
                pass
            assert requests == []
        finally:
            release.set()
            await asyncio.gather(pending, return_exceptions=True)


async def verifying(change: str, cooperative: bool = True) -> None:
    current = MixedSession(
        cast(Dispatch, Host()), cast(PlaywrightBrowser, Driver()), cast(ElementHandle, None), approval
    )
    entered, release = threading.Event(), threading.Event()

    class Guest:
        def verify(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, object]:
            entered.set()
            while not release.wait(0.01):
                if cooperative and cancelled is not None and cancelled():
                    raise ComputerUseError("Controlled read interrupted")
            return {"file_matches": True, "file_empty": False, "browser_matches": False, "browser_effects": 0}

    pending = asyncio.create_task(current.verify(cast(Desktop, Guest())))
    try:
        assert await asyncio.to_thread(entered.wait, 1)
        if change == "stop":
            current.stop()
        else:
            current.owner = "draining"
            current.phase_cancel.set()
        if not cooperative:
            release.set()
        result = await asyncio.wait_for(asyncio.shield(pending), 0.5)
        assert result["status"] == ("stopped" if change == "stop" else "unverified"), result
        assert result["guest_editor"] is (not cooperative), result
        assert current.settled.is_set()
    finally:
        release.set()
        await asyncio.gather(pending, return_exceptions=True)


async def main() -> bool:
    for task in ("support", "stock", "reservation", "service", "files"):
        await check("form capability " + task, lambda task=task: capability(task))
    await check("initial phase read Stop", initial_read)
    for change in ("stop", "handoff"):
        for cooperative in (True, False):
            await check(
                f"verification {change} cooperative={cooperative}",
                lambda change=change, cooperative=cooperative: verifying(change, cooperative),
            )
    print(json.dumps({"count": len(checks) + len(failures), "checks": checks, "failures": failures}, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
