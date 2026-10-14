from __future__ import annotations

import os
import sys
import stat
import time
import shutil
import socket
import secrets
import tempfile
import threading
import subprocess
from typing import BinaryIO, Callable
from pathlib import Path

import container_runtime

from openai.lib.computer import ComputerUseError


class Guest:
    def __init__(self, runtime_dir: Path, *, cancelled: Callable[[], bool] | None = None) -> None:
        if cancelled is not None and cancelled():
            raise ComputerUseError("Desktop startup was stopped.")
        if not runtime_dir.is_absolute():
            raise ComputerUseError("Use an absolute owned runtime path.")
        root = runtime_dir.resolve(strict=True)
        info = root.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise ComputerUseError("Invalid owned runtime root.")
        runs = (root / "runs").lstat()
        if not stat.S_ISDIR(runs.st_mode) or runs.st_uid != os.getuid() or stat.S_IMODE(runs.st_mode) != 0o700:
            raise ComputerUseError("Invalid owned runs directory.")
        self.container_root = root if container_runtime.is_container(root) else None
        if self.container_root is not None:
            self.id = container_runtime.start(root, cancelled=cancelled)
            self.directory = root / "runs" / self.id
            return
        self.id = secrets.token_hex(6)
        self.directory = root / "runs" / self.id
        self.socket = self.directory / "a.sock"
        path = str(self.socket)
        if len(path.encode()) >= 104 or any(c in path for c in "% ,"):
            raise ComputerUseError("Invalid owned socket path.")
        try:
            with subprocess.Popen(
                [
                    sys.executable,
                    "-I",
                    "-S",
                    str(Path(__file__).parent / "guest/setup.py"),
                    "--runtime-dir",
                    str(root),
                    "--verify-only",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={
                    "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
                    "LANG": "C",
                    "TMPDIR": str(root),
                },
            ) as verifier:
                deadline = time.monotonic() + 30
                try:
                    while True:
                        if cancelled is not None and cancelled():
                            raise ComputerUseError("Desktop startup was stopped.")
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise subprocess.TimeoutExpired(verifier.args, 30)
                        try:
                            status = verifier.wait(timeout=min(0.1, remaining))
                        except subprocess.TimeoutExpired:
                            continue
                        if status:
                            raise subprocess.CalledProcessError(status, verifier.args)
                        break
                finally:
                    if verifier.poll() is None:
                        verifier.kill()
                    verifier.wait()
        except (OSError, subprocess.SubprocessError):
            raise ComputerUseError("Existing VM runtime failed setup receipt validation.") from None
        if cancelled is not None and cancelled():
            raise ComputerUseError("Desktop startup was stopped.")
        self.directory.mkdir(mode=0o700)
        self.original = self.directory.lstat()
        if (
            not stat.S_ISDIR(self.original.st_mode)
            or self.original.st_uid != os.getuid()
            or stat.S_IMODE(self.original.st_mode) != 0o700
        ):
            raise ComputerUseError("Invalid run root.")
        args = [
            str(root / "bin/vfkit"),
            "--cpus",
            "4",
            "--memory",
            "4096",
            "--restful-uri",
            "none://",
            "--bootloader",
            f"efi,variable-store={self.directory / 'efi.vars'},create",
            "--device",
            f"virtio-blk,path={root / 'build/desktop.raw'},readonly,deviceId=bp22-root",
            "--device",
            f"virtio-vsock,port=4050,socketURL={self.socket},connect",
        ]
        self.failure: str | None = None
        self.output = {"stdout": 0, "stderr": 0}
        try:
            self.process = subprocess.Popen(
                [sys.executable, "-I", "-S", str(Path(__file__).parent / "guest/vm_owner.py"), "--", *args],
                cwd=self.directory,
                env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "C", "TMPDIR": str(self.directory)},
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except BaseException:
            try:
                if self._same_run_root(self.directory.lstat()):
                    self.directory.rmdir()
            except OSError:
                pass
            raise
        self.readers: list[threading.Thread] = []
        try:
            for pipe, name in ((self.process.stdout, "stdout"), (self.process.stderr, "stderr")):
                assert pipe is not None
                thread = threading.Thread(target=self.read_output, args=(pipe, name), daemon=True)
                thread.start()
                self.readers.append(thread)
        except BaseException:
            try:
                self.remove()
            except BaseException:
                # Reaping failure retains the run root. Preserve the original construction error.
                pass
            raise

    def read_output(self, pipe: BinaryIO, name: str) -> None:
        try:
            while chunk := os.read(pipe.fileno(), 4096):
                self.output[name] += len(chunk)
                if self.output[name] > 65536:
                    self.failure = "bounded vfkit output exceeded"
                    if self.process.poll() is None:
                        self.process.terminate()
                    break
        finally:
            pipe.close()

    def exchange(
        self, data: bytes, timeout: float, limit: int, *, cancelled: Callable[[], bool] | None = None
    ) -> bytes:
        if cancelled is not None and cancelled():
            raise ComputerUseError("Desktop verification was cancelled.")
        if self.container_root is not None:
            try:
                return container_runtime.exchange(
                    self.container_root, self.id, data, timeout, limit, cancelled=cancelled
                )
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
                raise ComputerUseError("Private guest request failed.") from None
        if not self.healthy():
            raise ComputerUseError("Private guest stopped.")
        deadline = time.monotonic() + timeout
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as stream:
                stream.settimeout(max(0.01, deadline - time.monotonic()))
                stream.connect(str(self.socket))
                stream.sendall(data)
                stream.shutdown(socket.SHUT_WR)
                parts = bytearray()
                while True:
                    if cancelled is not None and cancelled():
                        raise ComputerUseError("Desktop verification was cancelled.")
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError()
                    stream.settimeout(min(remaining, 0.05) if cancelled is not None else remaining)
                    try:
                        chunk = stream.recv(min(4096, limit + 1 - len(parts)))
                    except socket.timeout:
                        if cancelled is None:
                            raise
                        continue
                    if not chunk:
                        return bytes(parts)
                    parts.extend(chunk)
                    if len(parts) > limit:
                        raise ComputerUseError("Private guest reply exceeded limit.")
        except (OSError, TimeoutError):
            raise ComputerUseError("Private guest request failed.") from None

    def healthy(self, *, cancelled: Callable[[], bool] | None = None) -> bool:
        if self.container_root is not None:
            return container_runtime.healthy(self.container_root, self.id, cancelled=cancelled)
        return self.failure is None and self.process.poll() is None

    def _same_run_root(self, current: os.stat_result) -> bool:
        return (
            stat.S_ISDIR(current.st_mode)
            and current.st_dev == self.original.st_dev
            and current.st_ino == self.original.st_ino
            and current.st_uid == os.getuid()
            and stat.S_IMODE(current.st_mode) == 0o700
        )

    def remove(self) -> None:
        if self.container_root is not None:
            container_runtime.remove(self.container_root, self.id)
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.process.stdin is not None:
            self.process.stdin.close()
        for thread in self.readers:
            thread.join(timeout=1)
        if not hasattr(self, "_cleanup_root"):
            if not self._same_run_root(self.directory.lstat()):
                raise ComputerUseError("Run root ownership changed.")
            # Record where rename will put the run before rename or lstat can fail.
            self._cleanup_root = Path(tempfile.mkdtemp(prefix=".cleanup-", dir=self.directory.parent))
        moved = self._cleanup_root / "run"
        try:
            current = moved.lstat()
        except FileNotFoundError:
            if self.directory == moved:
                # Removal finished; only the private parent still needs cleanup.
                self._cleanup_root.rmdir()
                return
            current = None
        if current is None:
            if not self._same_run_root(self.directory.lstat()):
                raise ComputerUseError("Run root ownership changed.")
            self.directory.rename(moved)
            current = moved.lstat()
        if not self._same_run_root(current):
            # Never delete or restore a replacement onto the public path.
            raise ComputerUseError("Run root ownership changed; cleanup incomplete in private .cleanup- directory.")
        self.directory = moved
        shutil.rmtree(moved)
        self._cleanup_root.rmdir()
