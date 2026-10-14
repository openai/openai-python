"""Run the local-only example regressions supported by one locked provider group."""

from __future__ import annotations

import os
import sys
import signal
import argparse
import subprocess
from pathlib import Path
from contextlib import suppress

import openai

ROOT = Path(__file__).resolve().parent.parent
CASES: dict[str, list[tuple[str, ...]]] = {
    "browser": [("examples/browser/exercise_read_only.py",)],
    "computer": [
        ("examples/computer-desktop/exercise.py", "--check-frames"),
        ("examples/computer-desktop/exercise_helper_env.py",),
        ("examples/computer-desktop/exercise_container.py",),
        ("examples/computer-desktop/guest/test_action_admission.py",),
        ("examples/computer-desktop/guest/test_receipt.py",),
    ],
    "demo": [
        ("examples/browser-use-demo/exercise.py",),
        ("examples/browser-use-demo/exercise_ui.py",),
    ],
}


def run_case(command: list[str], env: dict[str, str], *, timeout: float = 120) -> None:
    with subprocess.Popen(command, cwd=ROOT, env=env, start_new_session=True) as process:
        try:
            code = process.wait(timeout=timeout)
        except BaseException:
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise
        if code:
            raise subprocess.CalledProcessError(code, command)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=CASES)
    args = parser.parse_args()
    if Path(openai.__file__).resolve() != ROOT / "src/openai/__init__.py":
        raise RuntimeError("Example checks replaced this OpenAI checkout.")
    env = {
        key: value
        for key, value in os.environ.items()
        if key.lower() not in ("http_proxy", "https_proxy", "all_proxy", "no_proxy")
        and not key.startswith(("OPENAI_", "BROWSERBASE_", "BROWSER_USE_", "E2B_", "DAYTONA_"))
    }
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for command in CASES[args.group]:
        script = ROOT / command[0]
        # Exercises import neighboring example modules and the exact checkout.
        env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(script.parent)))
        print(f"Running {script.relative_to(ROOT)} {' '.join(command[1:])}", flush=True)
        run_case([sys.executable, "-B", str(script), *command[1:]], env)


if __name__ == "__main__":
    main()
