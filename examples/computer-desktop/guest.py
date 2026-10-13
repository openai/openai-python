from __future__ import annotations

import os
import sys
import stat
import time
import shutil
import socket
import secrets
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
        root = runtime_dir
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
                args,
                cwd=self.directory,
                env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "C", "TMPDIR": str(self.directory)},
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except BaseException:
            try:
                if self.directory.lstat().st_ino == self.original.st_ino:
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
        for thread in self.readers:
            thread.join(timeout=1)
        current = self.directory.lstat()
        if current.st_ino != self.original.st_ino or current.st_uid != os.getuid():
            raise ComputerUseError("Run root ownership changed.")
        shutil.rmtree(self.directory)
