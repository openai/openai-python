"""Run only the fixed offline installer and reap its exact child."""

from __future__ import annotations

import os
import stat
import time
import argparse
import selectors
import subprocess
from pathlib import Path


def install(root: Path) -> None:
    root = root.absolute()
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError("Use a fresh owned mode-0700 runtime directory.")
    build = root / "build"
    disk = build / "desktop.raw"
    before = disk.lstat()
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_uid != os.getuid()
        or before.st_size != 16 * 1024**3
        or before.st_blocks != 0
    ):
        raise ValueError("The sole build disk must be a fresh blank 16 GiB sparse file.")
    if any((root / "runs").iterdir()):
        raise ValueError("Refusing to install into an active runtime.")
    args = [
        str(root / "bin" / "vfkit"),
        "--cpus",
        "4",
        "--memory",
        "4096",
        "--restful-uri",
        "none://",
        "--bootloader",
        f"linux,kernel={build / 'vmlinuz'},initrd={build / 'initrd-local.gz'},"
        'cmdline="auto=true priority=critical console=hvc0 rdinit=/bp22-media-init ---"',
        "--device",
        f"usb-mass-storage,path={build / 'installer.iso'},readonly",
        "--device",
        f"virtio-blk,path={disk},deviceId=bp22-root",
        "--device",
        "virtio-serial,stdio",
    ]
    master, slave = os.openpty()
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            args,
            cwd=build,
            env={
                "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
                "LANG": "C",
                "TMPDIR": str(build),
            },
            stdin=slave,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        os.close(slave)
        slave = -1
        assert process.stdout is not None and process.stderr is not None
        started = last_change = time.monotonic()
        modified = before.st_mtime_ns
        outputs = {"stdout": bytearray(), "stderr": bytearray()}
        reason: str | None = None
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ, "stdout")
            selector.register(process.stderr, selectors.EVENT_READ, "stderr")
            while selector.get_map():
                now = time.monotonic()
                current = disk.lstat()
                if current.st_ino != before.st_ino:
                    reason = "Owned build disk changed."
                    break
                if current.st_mtime_ns != modified:
                    last_change, modified = now, current.st_mtime_ns
                if now - started > 900 or (process.poll() is None and now - last_change > 180):
                    reason = "Installer exceeded its total or disk-progress deadline."
                    break
                for key, _ in selector.select(0.25):
                    chunk = os.read(key.fd, 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    label = str(key.data)
                    maximum = 1048576 if label == "stdout" else 65536
                    if len(outputs[label]) + len(chunk) > maximum:
                        reason = "Installer output exceeded its bound."
                        break
                    outputs[label].extend(chunk)
                if reason:
                    break
        if reason:
            raise RuntimeError(reason)
        process.wait(timeout=5)
        checks = (
            b"BP22-LATE-BEGIN",
            b"BP22-LATE-PACKAGES",
            b"BP22-LATE-ACCOUNT-CHECKS-PASSED",
            b"BP22-LATE-SERVICES",
            b"BP22-LATE-READONLY-MOUNTS",
            b"BP22-LATE-BLOCK-DRIVER",
            b"BP22-LATE-EFI-PASSED",
            b"BP22-LATE-COMPLETE",
        )
        if reason or process.returncode or not all(value in outputs["stdout"] for value in checks):
            raise RuntimeError(reason or "Installer did not complete its fixed guest checks.")
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
        if slave >= 0:
            os.close(slave)
        os.close(master)
    disk.chmod(0o400)
    print("Installed fixed read-only guest. Run the SDK exercise to test readiness and actions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the fixed isolated guest from staged verified inputs.")
    parser.add_argument("--runtime-dir", type=Path, required=True)
    options = parser.parse_args()
    install(options.runtime_dir)
