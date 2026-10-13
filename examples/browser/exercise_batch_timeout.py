"""A timed-out local trial must leave no running child process."""

from __future__ import annotations

import os
import sys
import json
import time
import signal
import hashlib
import tempfile
import subprocess
from pathlib import Path
from contextlib import suppress


def running(pid: int) -> bool:
    status = subprocess.run(
        ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, check=False
    ).stdout.strip()
    return bool(status) and not status.startswith("Z")


def main() -> None:
    batch = Path(__file__).with_name("long-workflow-batch.py")
    with tempfile.TemporaryDirectory(prefix="browser-batch-timeout-") as temporary:
        root = Path(temporary)
        entry = root / "trial.py"
        entry.write_text(
            "import subprocess, sys, time\nfrom pathlib import Path\n"
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
            "Path(__file__).with_suffix('.pid').write_text(str(child.pid))\n"
            "time.sleep(30)\n"
        )
        manifest = root / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "mode": "rehearsal",
                    "order": [{"sdk": "python", "variant": "A", "api": "responses", "scenario": "normal"}],
                    "python": sys.executable,
                    "python_entry": str(entry),
                    "limits": {"process_and_cleanup_seconds": 1},
                    "files_sha256": {str(entry): hashlib.sha256(entry.read_bytes()).hexdigest()},
                }
            )
        )
        (root / "manifest-sha256.json").write_text(
            json.dumps({"sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()})
        )
        pid: int | None = None
        try:
            result = subprocess.run(
                [sys.executable, "-B", str(batch), "run", "--directory", str(root)],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            pid = int(entry.with_suffix(".pid").read_text())
            assert result.returncode == 1
            assert json.loads((root / "summary.json").read_text())["trials"][0]["exit_code"] == 2
            end = time.monotonic() + 2
            while running(pid) and time.monotonic() < end:
                time.sleep(0.02)
            assert not running(pid), "Timed-out trial left its child running"
        finally:
            if pid is not None and running(pid):
                with suppress(ProcessLookupError):
                    os.kill(pid, signal.SIGKILL)
        print("PASS: timed-out trial terminates its whole process group")


if __name__ == "__main__":
    main()
