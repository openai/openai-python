"""Optional live Responses task: host browser, approved document, guest editor."""

from __future__ import annotations

import os
import sys
import json
import signal
import asyncio
import argparse
from pathlib import Path

from mixed_session import MixedSession, open_mixed

from openai import AsyncOpenAI
from openai.lib.browser import BrowserCancelledError
from openai.lib.responses_tool_runner import ToolRunnerError

# The trusted sibling source directory is fixed by the repository, never by task input.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "computer-desktop"))
from desktop import Desktop, DesktopStartupError


class Terminal:
    def __init__(self) -> None:
        self.pending: asyncio.Future[bool] | None = None
        self.stopped = asyncio.Event()
        self.session: MixedSession | None = None
        self.desktop: Desktop | None = None
        self.desktop_cleanup: asyncio.Task[None] | None = None
        self.commands: set[asyncio.Task[None]] = set()

    def start(self) -> None:
        asyncio.get_running_loop().add_reader(sys.stdin.fileno(), self.read)

    def read(self) -> None:
        line = sys.stdin.readline()
        if not line:
            asyncio.get_running_loop().remove_reader(sys.stdin.fileno())
            self.stop()
            return
        command = line.strip().lower()
        if command == "stop":
            self.stop()
        elif command in {"yes", "no"}:
            if self.pending is None or self.pending.done():
                print("There is no current approval.")
            else:
                self.pending.set_result(command == "yes")
        elif command in {
            "take",
            "return",
            "view",
            "host route",
            "host receipt",
            "guest type",
            "guest select-all",
            "guest save",
        } or command.startswith("guest click "):
            task = asyncio.create_task(self.control(command))
            self.commands.add(task)
            task.add_done_callback(self.commands.discard)
        else:
            print(
                "Use take, return, view, host route, host receipt, guest click X Y, guest type, guest select-all, guest save or stop."
            )

    async def control(self, command: str) -> None:
        current, desktop = self.session, self.desktop
        if current is None or desktop is None or self.stopped.is_set():
            print("The workspaces are not available.")
            return
        try:
            if command == "take":
                print("Take requested. Waiting for the complete active lease...")
                await current.take(desktop)
                print("Human owns both workspaces. Type view for current private PNG snapshots.")
            elif command == "return":
                print("Return requested. Waiting for human work to settle...")
                await current.return_control(desktop)
                print("Agent may continue with fresh observations and approvals.")
            else:
                paths = await current.human(desktop, command)
                if paths and current.owner == "human":
                    print(f"Private current Host browser: {paths[0]}\nPrivate current Guest desktop: {paths[1]}")
                elif current.owner == "human":
                    print("Command completed. Type view for a fresh snapshot.")
        except Exception:
            # No browser, guest, ledger or credential details in terminal errors.
            print(f"Command unavailable; owner={current.owner}, outcome={current.reason or 'unchanged'}.")

    async def ask(self, description: str) -> bool:
        print(f"\n{description}. Type yes or no (take or stop also works): ", end="", flush=True)
        loop = asyncio.get_running_loop()
        answer: asyncio.Future[bool] = loop.create_future()
        if self.pending is not None:
            raise RuntimeError("A previous approval is still outstanding.")
        self.pending = answer
        try:
            return await answer
        finally:
            self.pending = None

    def stop(self) -> None:
        self.stopped.set()
        if self.session:
            self.session.stop()
        else:
            self.retire_desktop()
        if self.pending and not self.pending.done():
            self.pending.set_result(False)

    def retire_desktop(self) -> None:
        if self.desktop is not None and self.desktop_cleanup is None:
            self.desktop_cleanup = asyncio.create_task(asyncio.to_thread(self.desktop.stop))

    async def close(self) -> None:
        self.stop()
        asyncio.get_running_loop().remove_reader(sys.stdin.fileno())
        if self.commands:
            await asyncio.gather(*self.commands, return_exceptions=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--runtime-dir", type=Path, required=True)
    args = parser.parse_args()
    model = os.environ.get("OPENAI_MODEL")
    if not args.live or not model or not os.environ.get("OPENAI_API_KEY"):
        parser.error("Use --live with caller OPENAI_MODEL and OPENAI_API_KEY. The no-key exercise never uses the API.")
    terminal = Terminal()
    desktop: Desktop | None = None
    report: dict[str, object] | None = None
    loop = asyncio.get_running_loop()

    def stop() -> None:
        terminal.stop()

    loop.add_signal_handler(signal.SIGINT, stop)
    print(
        "Dispatch receipt · two workspaces\n"
        "1  Host browser — read and route the synthetic dispatch case.\n"
        "2  Isolated desktop — enter the approved receipt in the editor; leave its browser alone.\n"
        "One local function will ask to fetch AND disclose the fixed public document.\n"
        "Type take to request control, return to resume, or stop at any time.\n"
        "Ctrl+C also stops. Stop cannot undo earlier work."
    )
    terminal.start()
    try:
        if not await terminal.ask("Create only these disposable resources for this task") or terminal.stopped.is_set():
            print(json.dumps({"status": "stopped" if terminal.stopped.is_set() else "refused"}))
            return
        desktop = await asyncio.to_thread(Desktop, args.runtime_dir, cancelled=terminal.stopped.is_set)
        terminal.desktop = desktop
        async with (
            open_mixed(terminal.ask, setup_stopped=terminal.stopped) as current,
            AsyncOpenAI(max_retries=0, timeout=30) as client,
        ):
            terminal.session = current
            if terminal.stopped.is_set():
                current.stop()
            try:
                while not current.stopping.is_set():
                    if not current.agent_owns():
                        current.changed.clear()
                        await current.changed.wait()
                        continue
                    # A human may have completed the fixed task. Check real owners
                    # before admission, even when no model requests remain.
                    proof = await current.verify(desktop)
                    if not current.agent_owns():
                        if current.stopping.is_set():
                            report = proof
                            report["status"] = current.reason or "stopped"
                        continue
                    if proof["status"] == "verified":
                        report = proof
                        break
                    try:
                        await current.agent_phase(desktop, client, model)
                    except (ToolRunnerError, RuntimeError, ValueError):
                        if current.owner == "draining":
                            continue
                        break
                    if current.owner == "agent":
                        proof = await current.verify(desktop)
                        if not current.agent_owns():
                            if current.stopping.is_set():
                                report = proof
                                report["status"] = current.reason or "stopped"
                            continue
                        if desktop.uncertain_effects:
                            proof["status"] = "unknown"
                        report = proof
                        break
            finally:
                # Stop marks intent; only this outer lifetime can drain the human
                # lease before open_mixed closes its DownloadOwner and browser.
                current.stop()
                try:
                    await asyncio.wait_for(current.settled.wait(), 5)
                except asyncio.TimeoutError:
                    current.reason = "unknown"
                    report = None
                    terminal.retire_desktop()
                    assert terminal.desktop_cleanup is not None
                    await terminal.desktop_cleanup
    except (BrowserCancelledError, DesktopStartupError):
        if terminal.session is not None or not terminal.stopped.is_set():
            raise
        report = {
            "status": "stopped",
            "host_browser": False,
            "approved_document": False,
            "guest_editor": False,
            "download": None,
            "requests": 0,
            "attempted_call_ids": [],
            "completed_call_ids": [],
        }
    finally:
        try:
            terminal.retire_desktop()
            if terminal.desktop_cleanup is not None:
                await terminal.desktop_cleanup
        finally:
            await terminal.close()
            loop.remove_signal_handler(signal.SIGINT)
    session = terminal.session
    if report is None:
        assert session is not None
        report = session.proof({})
    elif session is not None and session.download is not None:
        # The earlier settled guest verification remains valid. Cleanup is
        # reported only after its owner and the desktop have both closed.
        report["download"] = session.download.state()
    if desktop is not None and desktop.uncertain_effects:
        report["status"] = "unknown"
    print(json.dumps(report))
    if report["status"] != "verified" or not all(
        report.get(key) is True for key in ("host_browser", "approved_document", "guest_editor")
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
