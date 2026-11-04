"""Run the fixed disposable desktop task through the Responses API."""

from __future__ import annotations

import os
import json
import signal
import argparse
from pathlib import Path

from desktop import Desktop

from openai import OpenAI


def approve(prompt: str) -> bool:
    return input(prompt).strip().lower() == "yes"


def interrupt(_signal: int, _frame: object) -> None:
    raise KeyboardInterrupt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--runtime-dir", type=Path, required=True)
    args = parser.parse_args()
    model = os.environ.get("OPENAI_MODEL")
    if not args.live or not model or not os.environ.get("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY and OPENAI_MODEL and pass --live. Use exercise.py without API calls.")
    if not approve("Use only this disposable browser/editor and the fixed local receipt? Type yes to start: "):
        raise SystemExit("Desktop task declined.")

    previous = {name: signal.getsignal(name) for name in (signal.SIGINT, signal.SIGTERM)}
    signal.signal(signal.SIGTERM, interrupt)
    desktop: Desktop | None = None
    try:
        desktop = Desktop(args.runtime_dir)
        with OpenAI(max_retries=0) as client:
            desktop.operation(
                lambda computer: computer.run(
                    client,
                    {
                        "model": model,
                        "store": False,
                        "input": (
                            "This is an isolated Linux desktop with a local synthetic task. "
                            "In the browser on the left, route D-2201. In the editor on the right, "
                            "write exactly Desktop receipt D-2201 and save the open result.txt. Stop once done."
                        ),
                    },
                    max_steps=20,
                    before_action=lambda _action: True,
                    approve_safety_checks=lambda _call: approve(
                        "The API requests a safety decision for this local task. Approve the pending action? Type yes: "
                    ),
                )
            )
        proof = desktop.seal()
        verified = proof["file_matches"] is True and proof["browser_matches"] is True
        print(json.dumps({"verified": verified, "uncertainEffects": desktop.uncertain_effects}))
        if not verified:
            raise SystemExit(1)
    finally:
        try:
            for name in previous:
                signal.signal(name, signal.SIG_IGN)
            if desktop is not None:
                desktop.stop()
        finally:
            for name, handler in previous.items():
                signal.signal(name, handler)


if __name__ == "__main__":
    main()
