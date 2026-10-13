from __future__ import annotations

import os
import sys
import time
import signal
import subprocess
import importlib.util
from pathlib import Path
from contextlib import suppress

import pytest


def running(pid: int) -> bool:
    state = subprocess.run(
        ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, check=False
    ).stdout.strip()
    return bool(state) and not state.startswith("Z")


@pytest.mark.skipif(os.name != "posix", reason="Example CI uses POSIX process groups")
@pytest.mark.parametrize("interrupt", [False, True])
def test_interrupted_example_stops_descendants(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, interrupt: bool
) -> None:
    spec = importlib.util.spec_from_file_location(
        "example_security", Path(__file__).resolve().parents[1] / "scripts/check-example-security.py"
    )
    assert spec is not None and spec.loader is not None
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    worker = tmp_path / "worker.py"
    worker.write_text(
        "import subprocess, sys, time\nfrom pathlib import Path\n"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        "Path(__file__).with_suffix('.pid').write_text(str(child.pid))\n"
        "time.sleep(60)\n"
    )
    command = [sys.executable, str(worker)]
    original_wait = subprocess.Popen[bytes].wait
    interrupted = False
    spawned: list[subprocess.Popen[bytes]] = []

    def wait(process: subprocess.Popen[bytes], timeout: float | None = None) -> int:
        nonlocal interrupted
        if process.args == command and process not in spawned:
            spawned.append(process)
        if interrupt and process.args == command and not interrupted:
            deadline = time.monotonic() + 5
            while not worker.with_suffix(".pid").exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            interrupted = True
            raise KeyboardInterrupt()
        return original_wait(process, timeout=timeout)

    monkeypatch.setattr(subprocess.Popen, "wait", wait)
    descendant: int | None = None
    try:
        with pytest.raises(KeyboardInterrupt if interrupt else subprocess.TimeoutExpired):
            launcher.run_case(command, dict(os.environ), timeout=1)
        descendant = int(worker.with_suffix(".pid").read_text())
        deadline = time.monotonic() + 2
        while running(descendant) and time.monotonic() < deadline:
            time.sleep(0.01)
        assert not running(descendant), "Interrupted example left a descendant running"
    finally:
        for process in spawned:
            if process.poll() is None:
                process.kill()
            original_wait(process, timeout=5)
        if descendant is not None:
            with suppress(ProcessLookupError):
                os.kill(descendant, signal.SIGKILL)
