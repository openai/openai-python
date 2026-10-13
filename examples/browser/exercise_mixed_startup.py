"""Mixed CLI setup cancellation with a finite owned launcher and no native input."""

from __future__ import annotations

import os
import sys
import json
import asyncio
import threading
from typing import Any, cast
from pathlib import Path
from unittest.mock import patch

import run_mixed
import browser_driver
from desktop import DesktopStartupError


async def exercise(failure: str) -> None:
    entered, release, retired = asyncio.Event(), asyncio.Event(), asyncio.Event()
    terminal = run_mixed.Terminal()
    loop = asyncio.get_running_loop()
    counts = {"desktop": 0, "browser": 0, "context": 0}
    printed: list[str] = []

    class Guest:
        uncertain_effects = False

        def __init__(self, _runtime: Path, **_options: Any) -> None:
            pass

        def stop(self) -> None:
            counts["desktop"] += 1
            loop.call_soon_threadsafe(retired.set)
            if failure == "desktop":
                raise RuntimeError("Controlled guest cleanup failure")

    class Browser:
        async def close(self) -> None:
            counts["browser"] += 1
            if failure == "browser":
                raise RuntimeError("Controlled browser cleanup failure")

        async def new_context(self, **_options: Any) -> None:
            counts["context"] += 1
            raise AssertionError("Stopped setup must not start a context")

    class Chromium:
        async def launch(self, **_options: Any) -> Browser:
            entered.set()
            await release.wait()
            return Browser()

    class Local:
        chromium = Chromium()

        async def __aenter__(self) -> Local:
            return self

        async def __aexit__(self, *_args: object) -> None:
            pass

    async def approve(_description: str) -> bool:
        return True

    def output(*args: object, **_options: object) -> None:
        printed.append(" ".join(map(str, args)))

    async def invoked() -> BaseException | None:
        try:
            await run_mixed.main()
        except (Exception, SystemExit) as error:
            return error
        return None

    with (
        patch.object(run_mixed, "Terminal", return_value=terminal),
        patch.object(run_mixed, "Desktop", Guest),
        patch.object(browser_driver, "async_playwright", Local),
        patch.object(terminal, "start", lambda: None),
        patch.object(terminal, "ask", approve),
        patch.object(run_mixed, "print", output, create=True),
        patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic", "OPENAI_MODEL": "synthetic"}),
        patch.object(sys, "argv", ["run_mixed.py", "--live", "--runtime-dir", "/unused"]),
    ):
        work = asyncio.create_task(invoked())
        try:
            await asyncio.wait_for(entered.wait(), 2)
            terminal.stop()
            terminal.stop()
            await asyncio.wait_for(retired.wait(), 0.7)
            assert counts == {"desktop": 1, "browser": 0, "context": 0}, counts
            assert not work.done(), "Final proof must wait for the launched browser to be reaped"
            assert not any(line.startswith("{") for line in printed)
            release.set()
            result = await asyncio.wait_for(work, 2)
            assert counts == {"desktop": 1, "browser": 1, "context": 0}, counts
            reports = [json.loads(line) for line in printed if line.startswith("{")]
            if failure == "none":
                assert isinstance(result, SystemExit) and result.code == 1, result
                assert len(reports) == 1, reports
                assert reports[0] == {
                    "status": "stopped",
                    "host_browser": False,
                    "approved_document": False,
                    "guest_editor": False,
                    "download": None,
                    "requests": 0,
                    "attempted_call_ids": [],
                    "completed_call_ids": [],
                }
            else:
                assert isinstance(result, RuntimeError) and "cleanup failure" in str(result), result
                assert reports == [], reports
        finally:
            release.set()
            await asyncio.gather(work, return_exceptions=True)


async def desktop_startup(stopped: bool) -> None:
    terminal = run_mixed.Terminal()
    entered, release = asyncio.Event(), threading.Event()
    loop = asyncio.get_running_loop()
    printed: list[str] = []

    class Guest:
        def __init__(self, _runtime: Path, **_options: Any) -> None:
            loop.call_soon_threadsafe(entered.set)
            assert release.wait(2), "The startup fixture was not released"
            raise DesktopStartupError("Controlled startup failure")

    async def approve(_description: str) -> bool:
        return True

    def output(value: object) -> None:
        printed.append(str(value))

    async def invoked() -> BaseException | None:
        try:
            await run_mixed.main()
        except (Exception, SystemExit) as error:
            return error
        return None

    with (
        patch.object(run_mixed, "Terminal", return_value=terminal),
        patch.object(run_mixed, "Desktop", Guest),
        patch.object(terminal, "start", lambda: None),
        patch.object(terminal, "ask", approve),
        patch.object(run_mixed, "print", output, create=True),
        patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic", "OPENAI_MODEL": "synthetic"}),
        patch.object(sys, "argv", ["run_mixed.py", "--live", "--runtime-dir", "/unused"]),
    ):
        work = asyncio.create_task(invoked())
        try:
            await asyncio.wait_for(entered.wait(), 2)
            if stopped:
                terminal.stop()
            release.set()
            result = await asyncio.wait_for(work, 2)
            reports = [json.loads(line) for line in printed if line.startswith("{")]
            if stopped:
                assert isinstance(result, SystemExit) and result.code == 1, result
                assert len(reports) == 1 and reports[0]["status"] == "stopped", reports
                assert reports[0]["requests"] == 0 and reports[0]["guest_editor"] is False
            else:
                assert isinstance(result, DesktopStartupError), result
                assert reports == [], reports
        finally:
            release.set()
            await asyncio.gather(work, return_exceptions=True)


async def active_control() -> None:
    terminal = run_mixed.Terminal()
    stopped: list[str] = []

    class Guest:
        def stop(self) -> None:
            stopped.append("guest")

    class Session:
        def stop(self) -> None:
            stopped.append("session")

    terminal.desktop = cast(Any, Guest())
    terminal.session = cast(Any, Session())
    terminal.stop()
    terminal.stop()
    await asyncio.sleep(0)
    assert stopped == ["session", "session"], stopped


async def main() -> None:
    results: list[dict[str, object]] = []
    for kind in ("none", "desktop", "browser"):
        try:
            await exercise(kind)
            results.append({"case": kind, "pass": True})
        except Exception as error:
            results.append({"case": kind, "pass": False, "error": f"{type(error).__name__}: {error}"})
    await active_control()
    results.append({"case": "active-session-drain", "pass": True})
    for stopped in (False, True):
        await desktop_startup(stopped)
        results.append({"case": f"desktop-startup-stopped-{stopped}", "pass": True})
    print(json.dumps({"results": results, "api_calls": 0, "vm_calls": 0}))
    assert all(item["pass"] for item in results), results


if __name__ == "__main__":
    asyncio.run(main())
