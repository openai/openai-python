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


def check_child_environment(batch: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="browser-batch-environment-") as temporary:
        root = Path(temporary)
        preload = root / "preload"
        preload.mkdir()
        marker = root / "preload-ran"
        (preload / "sitecustomize.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
        hook = preload / "hook.cjs"
        hook.write_text(f"require('node:fs').writeFileSync({json.dumps(str(marker))}, 'loaded');\n")
        receipt: dict[str, object] = {
            "cleanup": True,
            "oracle": {"correct": True, "explained": True, "lifecycle_valid": True},
            "requests": [],
            "wall_ms": 0,
            "phases": [],
            "escape_attempts": 0,
            "witness_arrivals": 0,
        }
        python = root / "trial.py"
        python.write_text(
            "import json, os, sys\nfrom pathlib import Path\n"
            f"receipt = json.loads({json.dumps(receipt)!r})\n"
            "receipt['inherited'] = [key for key in ('PYTHONPATH', 'NODE_OPTIONS', 'NODE_PATH') if key in os.environ]\n"
            "Path(sys.argv[sys.argv.index('--output') + 1]).write_text(json.dumps(receipt))\n"
        )
        node = root / "trial.cjs"
        node.write_text(
            f"const receipt = {json.dumps(receipt)};\n"
            "receipt.inherited = ['PYTHONPATH', 'NODE_OPTIONS', 'NODE_PATH'].filter(key => key in process.env);\n"
            "require('node:fs').writeFileSync(process.argv[process.argv.indexOf('--output') + 1], JSON.stringify(receipt));\n"
        )
        manifest = root / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "mode": "rehearsal",
                    "order": [
                        {"sdk": sdk, "variant": "A", "api": "responses", "scenario": "normal"}
                        for sdk in ("python", "node")
                    ],
                    "python": sys.executable,
                    "python_entry": str(python),
                    "node_entry": str(node),
                    "limits": {"process_and_cleanup_seconds": 10},
                    "files_sha256": {
                        str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (python, node)
                    },
                }
            )
        )
        (root / "manifest-sha256.json").write_text(
            json.dumps({"sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()})
        )
        env = {**os.environ, "PYTHONPATH": str(preload), "NODE_OPTIONS": f"--require={hook}", "NODE_PATH": str(preload)}
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(batch), "run", "--directory", str(root)],
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert not marker.exists(), "A child loaded code from the inherited interpreter environment"
        for index in (1, 2):
            assert json.loads((root / f"trial-{index:02d}.json").read_text())["inherited"] == []
        print("PASS: Python and Node trials ignore inherited preload and import paths")


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
    check_child_environment(batch)


if __name__ == "__main__":
    main()
