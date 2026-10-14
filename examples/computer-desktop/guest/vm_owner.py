"""Stop and reap one VM when its SDK owner closes the parent-liveness pipe."""

from __future__ import annotations

import os
import sys
import signal
import threading
import subprocess


def main() -> int:
    command = sys.argv[1:]
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        raise SystemExit("Usage: vm_owner.py -- <vfkit executable> [arguments]")
    stopped = threading.Event()

    def stop(_signal: int, _frame: object) -> None:
        stopped.set()

    def watch_parent() -> None:
        try:
            while os.read(0, 4096):
                pass
        finally:
            stopped.set()

    previous = {name: signal.signal(name, stop) for name in (signal.SIGINT, signal.SIGTERM)}
    child: subprocess.Popen[bytes] | None = None
    try:
        threading.Thread(target=watch_parent, daemon=True).start()
        if stopped.is_set():
            return 0
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, close_fds=True)
        while not stopped.is_set():
            try:
                status = child.wait(timeout=0.1)
                return status if status >= 0 else 128 - status
            except subprocess.TimeoutExpired:
                # Poll again so a parent shutdown can stop the child.
                pass
        return 0
    finally:
        if child is not None and child.poll() is None:
            try:
                child.terminate()
            except ProcessLookupError:
                # The child exited between poll() and terminate().
                pass
            try:
                child.wait(timeout=4)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        for name, handler in previous.items():
            signal.signal(name, handler)


if __name__ == "__main__":
    raise SystemExit(main())
