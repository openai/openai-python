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
    "browser": [
        ("examples/browser/exercise.py",),
        ("examples/browser/exercise_borrowed_retirement.py",),
        ("examples/browser/exercise_wait_editable.py", "wait"),
        ("examples/browser/exercise_wait_editable.py", "editable"),
        ("examples/browser/exercise_scoped.py",),
        ("examples/browser/exercise_capabilities.py",),
        ("examples/browser/exercise_portable_files.py",),
        ("examples/browser/exercise_coordinates.py",),
        ("examples/browser/exercise_find_budget.py",),
        ("examples/browser/exercise_batch_timeout.py",),
        ("examples/browser/exercise_network.py",),
        ("examples/browser/exercise_navigation.py",),
        ("examples/browser/exercise_navigation_retirement.py",),
        ("examples/browser/exercise_pointer.py",),
        ("examples/browser/exercise_owned.py",),
        ("examples/browser/exercise_sensitive.py",),
        ("examples/browser/exercise_read_only.py",),
        ("examples/browser/exercise_setup.py",),
        ("examples/browser/exercise_read_integrity.py",),
        ("examples/browser/exercise_reference_admission.py",),
        ("examples/browser/exercise_borrowed_read_cancellation.py",),
        ("examples/browser/exercise_approval.py",),
        ("examples/browser/exercise_file_eligibility.py",),
        ("examples/browser/exercise_file_cleanup.py",),
        ("examples/browser/exercise_upload.py",),
        ("examples/browser/exercise_download.py",),
        ("examples/browser/exercise_browserbase.py",),
        ("examples/browser/exercise_browser_use.py",),
    ],
    "computer": [
        ("examples/computer/exercise.py",),
        ("examples/computer-desktop/exercise.py", "--check-frames"),
        ("examples/computer-desktop/exercise_helper_env.py",),
        ("examples/computer-desktop/exercise_container.py",),
        ("examples/computer-desktop/guest/test_action_admission.py",),
        ("examples/computer-desktop/guest/test_receipt.py",),
    ],
    "e2b": [
        ("examples/computer-e2b/exercise.py",),
        ("examples/computer-e2b/exercise_png.py",),
        ("examples/computer-e2b/exercise_cancellation.py",),
    ],
    "daytona": [("examples/computer-daytona/exercise.py",)],
    "demo": [
        ("examples/browser-use-demo/exercise_controls.py",),
        ("examples/browser-use-demo/exercise_diagnostics.py",),
        ("examples/browser-use-demo/exercise_wire.py",),
        ("examples/browser-use-demo/exercise_refusal_stop.py",),
        ("examples/browser-use-demo/exercise_mixed_boundaries.py",),
        ("examples/browser-use-demo/exercise_phase_lifecycle.py",),
        ("examples/browser-use-demo/exercise_desktop_lifecycle.py",),
        ("examples/browser-use-demo/exercise_ledger_classification.py",),
        ("examples/browser/exercise_mixed_startup.py",),
        ("examples/browser-workflow/exercise.py",),
        ("examples/browser-workflow/exercise_approval.py",),
        ("examples/browser-workflow/exercise_cancel.py",),
        ("examples/browser-workflow/exercise_origin.py",),
        ("examples/browser-workflow/exercise_outcomes.py", "pixels"),
        ("examples/browser-workflow/exercise_outcomes.py", "identifiers"),
        ("examples/browser-workflow/exercise_outcomes.py", "browser-loss"),
        ("examples/browser-workflow/exercise_outcomes.py", "operator-stop"),
        ("examples/browser-workflow/exercise_recovery.py", "storage"),
        ("examples/browser-workflow/exercise_recovery.py", "startup"),
        ("examples/browser-workflow/exercise_runners.py",),
        ("examples/browser-workflow/exercise_stop_boundaries.py",),
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
