"""Bounded guest socket checks; no display, container or VM is needed."""

from __future__ import annotations

import os
import sys
import json
import time
import socket
import tempfile
import unittest
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def wait_for(path: Path, timeout: float = 3) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if path.exists():
            return True
        time.sleep(0.01)
    return False


def guest_process(root: Path, name: str, descriptor: int) -> None:
    sys.path.insert(0, str(HERE))
    import action

    os.dup2(descriptor, 3, inheritable=True)
    os.environ["LISTEN_PID"] = str(os.getpid())
    os.environ["LISTEN_FDS"] = "1"
    action.ROOT = root
    validate = action.validate

    def recorded_validate(raw: object) -> tuple[dict[str, object], list[str]]:
        result = validate(raw)
        (root / f"{name}-validated").touch()
        return result

    def controlled_reply(request: object) -> dict[str, object]:
        (root / f"{name}-request.json").write_text(json.dumps(request), encoding="utf-8")
        (root / f"{name}-entered").touch()
        if name == "read" and not wait_for(root / "release", 3):
            raise TimeoutError("Fixture read was not released.")
        return {"ok": True}

    action.validate = recorded_validate
    action.reply = controlled_reply
    action.main()


class ActionAdmissionTests(unittest.TestCase):
    def check_release(self, crash: bool) -> None:
        with tempfile.TemporaryDirectory(prefix="guest-admission-") as directory:
            root = Path(directory)
            clients: list[socket.socket] = []
            children: list[subprocess.Popen[bytes]] = []

            def send(name: str, request: dict[str, object]) -> socket.socket:
                client, peer = socket.socketpair()
                client.settimeout(2)
                clients.append(client)
                try:
                    child = subprocess.Popen(
                        [
                            sys.executable,
                            "-B",
                            str(HERE / "test_action_admission.py"),
                            "--guest",
                            str(root),
                            name,
                            str(peer.fileno()),
                        ],
                        pass_fds=(peer.fileno(),),
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                    )
                    children.append(child)
                finally:
                    peer.close()
                client.sendall(json.dumps(request).encode("ascii") + b"\n")
                client.shutdown(socket.SHUT_WR)
                return client

            try:
                read = send("read", {"type": "verify"})
                if not wait_for(root / "read-entered"):
                    self.fail(f"The read was never admitted: {children[0].communicate(timeout=2)[1]!r}")
                read.close()
                invalid = send("invalid", {"type": "unsupported"})
                self.assertEqual(
                    json.loads(invalid.recv(4096)),
                    {"ok": False, "uncertain": False, "error": "Unsupported or invalid action."},
                )
                self.assertFalse((root / "invalid-entered").exists())
                too_large = send("oversized", {"type": "type", "text": "x" * 16384})
                self.assertEqual(
                    json.loads(too_large.recv(4096)),
                    {"ok": False, "uncertain": False, "error": "Unsupported or invalid action."},
                )
                self.assertFalse((root / "oversized-entered").exists())
                requested: dict[str, object] = {
                    "type": "type",
                    "text": "synthetic fixture " * 192 + "\nDesktop receipt D-2201",
                }
                effect = send("input", requested)
                self.assertTrue(wait_for(root / "input-validated"), "The next action never reached admission.")
                self.assertFalse(wait_for(root / "input-entered", 0.2), "Input overlapped an abandoned read.")
                if crash:
                    children[0].kill()
                    children[0].wait(timeout=2)
                else:
                    (root / "release").touch()
                self.assertEqual(json.loads(effect.recv(4096)), {"ok": True})
                self.assertTrue((root / "input-entered").exists(), "The queued action never ran after release.")
                self.assertEqual(json.loads((root / "input-request.json").read_text(encoding="utf-8")), requested)
                children[-1].wait(timeout=2)
                self.assertEqual(children[-1].returncode, 0)
            finally:
                (root / "release").touch()
                for client in clients:
                    client.close()
                for child in children:
                    try:
                        child.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=2)
                    if child.stderr is not None:
                        child.stderr.close()

    def test_abandoned_read_drains_before_input(self) -> None:
        self.check_release(crash=False)

    def test_crashed_read_releases_input(self) -> None:
        self.check_release(crash=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--guest":
        guest_process(Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
    else:
        unittest.main()
