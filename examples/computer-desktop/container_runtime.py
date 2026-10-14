"""Optional local Docker owner for the fixed offline desktop. No SDK dependency."""

from __future__ import annotations

import os
import sys
import json
import stat
import time
import select
import shutil
import signal
import hashlib
import secrets
import argparse
import platform
import tempfile
import selectors
import subprocess
from typing import Any, Callable, cast
from pathlib import Path

HERE = Path(__file__).resolve().parent / "guest"
DOCKER_SOCKET = "/var/run/docker.sock"
IMAGE = "mcr.microsoft.com/playwright/python@sha256:72bd171a9ffc2b4b59532aaa6210e21014d07093120dc25528870c0b840da1f0"
PROFILE = "bfa4a8eb1bcc25871ccbf720a7aab76c6f3d5eb31f097e7c42babe81a70f2d3a"
LABEL = "org.openai.desktop.example"
FILES = {
    "Dockerfile": HERE / "container/Dockerfile",
    "bridge.py": HERE / "container/bridge.py",
    "seccomp.json": HERE / "container/seccomp.json",
    "action.py": HERE / "action.py",
    "start.py": HERE / "start.py",
    "fixture.html": HERE / "fixture.html",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned(path: Path, mode: int, directory: bool = False) -> os.stat_result:
    info = path.lstat()
    check = stat.S_ISDIR if directory else stat.S_ISREG
    if not check(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != mode:
        raise ValueError(f"Expected private owned path: {path}")
    return info


def write_new(path: Path, value: object) -> None:
    with path.open("x") as output:
        os.fchmod(output.fileno(), 0o600)
        json.dump(value, output)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())


def identity(path: Path) -> dict[str, object]:
    info = owned(path, 0o700, True)
    return {"path": str(path.resolve(strict=True)), "device": info.st_dev, "inode": info.st_ino}


def recipe() -> dict[str, str]:
    return {name: digest(path) for name, path in FILES.items()}


def local_only() -> str:
    host_platform = sys.platform
    if host_platform != "linux" or platform.machine().lower() not in ("x86_64", "amd64"):
        raise ValueError("The container example requires a local x86-64 Linux host.")
    for name in (
        "DOCKER_CONTEXT",
        "DOCKER_CONFIG",
        "DOCKER_CERT_PATH",
        "DOCKER_TLS_VERIFY",
        "BUILDKIT_HOST",
        "BUILDX_BUILDER",
        "BUILDX_CONFIG",
    ):
        if os.environ.get(name):
            raise ValueError(f"Clear {name}; only a verified local Unix daemon is supported.")
    if os.environ.get("DOCKER_HOST") not in (None, "", "unix://" + DOCKER_SOCKET):
        raise ValueError("Remote Docker endpoints are not supported.")
    info = Path(DOCKER_SOCKET).stat()
    if not stat.S_ISSOCK(info.st_mode):
        raise ValueError("A local Docker Unix socket is required.")
    binary = shutil.which("docker", path="/usr/local/bin:/usr/bin:/bin")
    if binary is None:
        raise ValueError("Install Docker locally; no remote contexts or builders are supported.")
    return binary


class StartupCancelled(RuntimeError):
    """The caller stopped local startup; no SDK input was admitted."""


def check_cancelled(cancelled: Callable[[], bool] | None) -> None:
    if cancelled is not None and cancelled():
        raise StartupCancelled("Desktop container startup was cancelled.")


def docker(
    root: Path,
    args: list[str],
    *,
    data: bytes | None = None,
    timeout: float = 30,
    limit: int = 65536,
    cancelled: Callable[[], bool] | None = None,
    deadline: float | None = None,
    on_dispatch: Callable[[], None] | None = None,
) -> bytes:
    check_cancelled(cancelled)
    end = time.monotonic() + timeout
    if deadline is not None:
        end = min(end, deadline)
    if time.monotonic() >= end:
        raise subprocess.TimeoutExpired(args, timeout)
    binary = local_only()
    owned(root, 0o700, True)
    # A new empty config cannot inherit credentials, contexts or remote builders.
    with tempfile.TemporaryDirectory(prefix=".docker-", dir=root) as config:
        check_cancelled(cancelled)
        if time.monotonic() >= end:
            raise subprocess.TimeoutExpired(args, timeout)
        if on_dispatch is not None:
            on_dispatch()
        with subprocess.Popen(
            [binary, "--config", config, "--host", "unix://" + DOCKER_SOCKET, *args],
            cwd=config,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": config, "LANG": "C", "DOCKER_BUILDKIT": "0"},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as child:
            stdout = bytearray()
            stderr_size = 0
            pending = memoryview(data or b"")
            assert child.stdin is not None and child.stdout is not None and child.stderr is not None
            try:
                with selectors.DefaultSelector() as ready:
                    for pipe in (child.stdin, child.stdout, child.stderr):
                        os.set_blocking(pipe.fileno(), False)
                    ready.register(child.stdout, selectors.EVENT_READ, "stdout")
                    ready.register(child.stderr, selectors.EVENT_READ, "stderr")
                    if pending:
                        ready.register(child.stdin, selectors.EVENT_WRITE, "stdin")
                    else:
                        child.stdin.close()
                    while ready.get_map() or child.poll() is None:
                        check_cancelled(cancelled)
                        remaining = end - time.monotonic()
                        if remaining <= 0:
                            raise subprocess.TimeoutExpired(args, timeout)
                        for key, _ in ready.select(min(remaining, 0.1)):
                            if key.data == "stdin":
                                try:
                                    sent = os.write(key.fd, pending[: select.PIPE_BUF])
                                    pending = pending[sent:]
                                except BlockingIOError:
                                    continue
                                except BrokenPipeError:
                                    pending = pending[:0]
                                if not pending:
                                    ready.unregister(child.stdin)
                                    child.stdin.close()
                                continue
                            maximum = limit - len(stdout) if key.data == "stdout" else 1024 * 1024 - stderr_size
                            chunk = os.read(key.fd, min(65536, max(1, maximum + 1)))
                            if not chunk:
                                ready.unregister(key.fd)
                            elif len(chunk) > maximum:
                                raise RuntimeError("Local Docker reply exceeded the example's limit.")
                            elif key.data == "stdout":
                                stdout.extend(chunk)
                            else:
                                stderr_size += len(chunk)
                check_cancelled(cancelled)
            except BaseException:
                # Never drain unbounded output after failure. Reap before reconciling the CID.
                child.kill()
                child.stdin.close()
                child.stdout.close()
                child.stderr.close()
                child.wait()
                raise
    if child.returncode:
        raise RuntimeError("Local Docker command failed.")
    return bytes(stdout)


def check_image(root: Path, value: dict[str, Any], *, cancelled: Callable[[], bool] | None = None) -> None:
    image = value["image"]
    actual = docker(root, ["image", "inspect", "--format", "{{.Id}}", image], cancelled=cancelled)
    if actual.decode("ascii").strip() != image:
        raise RuntimeError("Recorded desktop image is absent or changed. Rebuild in a new runtime.")


def checked_root(root: Path) -> Path:
    if not root.is_absolute():
        raise ValueError("Use an absolute runtime directory outside the SDK checkout.")
    root = root.resolve()
    for parent in root.parents:
        info = parent.stat()
        if info.st_uid not in (0, os.getuid()) or (info.st_mode & 0o022 and not info.st_mode & stat.S_ISVTX):
            raise ValueError("Runtime ancestors must be trusted and not writable by other users.")
    return root


def runtime(root: Path) -> dict[str, Any]:
    root = checked_root(root)
    owned(root, 0o700, True)
    owned(root / "runs", 0o700, True)
    owned(root / "build", 0o700, True)
    context = root / "build/context"
    owned(context, 0o700, True)
    owned(root / "setup.json", 0o600)
    value: dict[str, Any] = json.loads((root / "setup.json").read_text())
    for name in FILES:
        owned(context / name, 0o600)
    current = recipe()
    image = value.get("image")
    if (
        value.get("backend") != "container"
        or value.get("owner") != identity(root)
        or value.get("base") != IMAGE
        or value.get("recipe") != current
        or {name: digest(context / name) for name in FILES} != current
        or current["seccomp.json"] != PROFILE
        or not isinstance(image, str)
        or len(image) != 71
        or not image.startswith("sha256:")
        or any(c not in "0123456789abcdef" for c in image[7:])
    ):
        raise ValueError("Container runtime does not match this recipe.")
    return value


def is_container(root: Path) -> bool:
    owned(root, 0o700, True)
    try:
        owned(root / "setup.json", 0o600)
    except FileNotFoundError:
        return False
    value = json.loads((root / "setup.json").read_text())
    if "backend" not in value:
        return False
    if value["backend"] != "container":
        raise ValueError("Unknown tagged desktop backend.")
    return True


def setup(root: Path) -> None:
    root = checked_root(root)
    try:
        root.lstat()
    except FileNotFoundError:
        pass
    else:
        check_image(root, runtime(root))
        print(f"Ready: {root} (existing local container recipe validated)")
        return
    local_only()
    initial_recipe = recipe()
    if initial_recipe["seccomp.json"] != PROFILE:
        raise ValueError("Desktop syscall profile has changed.")
    root.mkdir(mode=0o700)
    owned(root, 0o700, True)
    (root / "runs").mkdir(mode=0o700)
    build = root / "build"
    build.mkdir(mode=0o700)
    context = build / "context"
    context.mkdir(mode=0o700)
    # Never pass the caller's checkout, working tree or credentials to the builder.
    for name, path in FILES.items():
        shutil.copyfile(path, context / name)
        (context / name).chmod(0o600)
    if {name: digest(context / name) for name in FILES} != initial_recipe:
        raise ValueError("Container provisioning changed while copying the build context.")
    image_path = build / "image-id"
    docker(
        root, ["build", "--pull=false", "--iidfile", str(image_path), str(context)], timeout=900, limit=4 * 1024 * 1024
    )
    image = image_path.read_text().strip()
    if not image.startswith("sha256:") or len(image) != 71:
        raise RuntimeError("Docker did not return an immutable local image ID.")
    if recipe() != initial_recipe or {name: digest(context / name) for name in FILES} != initial_recipe:
        raise ValueError("Container provisioning changed during build; no receipt was published.")
    write_new(
        root / "setup.json",
        {"backend": "container", "owner": identity(root), "image": image, "recipe": initial_recipe, "base": IMAGE},
    )
    print(f"Ready: {root}. Run the SDK no-key exercise.")


def preflight(root: Path | None = None) -> None:
    local_only()
    if root is not None:
        root = checked_root(root)
        check_image(root, runtime(root))


def run_record(root: Path, id: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    if len(id) != 12 or any(c not in "0123456789abcdef" for c in id):
        raise ValueError("Invalid owned run ID.")
    setup_value = runtime(root)
    directory = root / "runs" / id
    owned(directory, 0o700, True)
    owned(directory / "intent.json", 0o600)
    intent: dict[str, Any] = json.loads((directory / "intent.json").read_text())
    if (
        intent.get("owner") != identity(directory)
        or intent.get("name") != "openai-desktop-" + id
        or intent.get("image") != setup_value["image"]
    ):
        raise ValueError("Run record no longer matches its runtime.")
    return directory, intent, setup_value


def lookup(
    root: Path, id: str, *, cancelled: Callable[[], bool] | None = None, deadline: float | None = None
) -> dict[str, Any] | None:
    directory, intent, setup_value = run_record(root, id)
    name = str(intent["name"])
    cidfile = directory / "container-id"
    try:
        info = cidfile.lstat()
    except FileNotFoundError:
        captured = None
    else:
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise RuntimeError("Invalid container ID receipt; retaining the run record.")
        captured = cidfile.read_text().strip()
        if len(captured) != 64 or any(c not in "0123456789abcdef" for c in captured):
            raise RuntimeError("Incomplete container ID receipt; retaining the run record.")
    # A completed cidfile binds lookup to that container even after a rename.
    # Before a CID was captured, absence by name cannot rule out a delayed create.
    selector = "id=" + captured if captured is not None else "name=^/" + name + "$"
    found = (
        docker(
            root,
            ["ps", "-a", "--no-trunc", "--filter", selector, "--format", "{{.ID}}"],
            cancelled=cancelled,
            deadline=deadline,
        )
        .decode()
        .splitlines()
    )
    if not found:
        if captured is not None:
            return None
        raise RuntimeError("Create outcome is still indeterminate; retaining the run record.")
    if len(found) != 1 or len(found[0]) != 64 or any(c not in "0123456789abcdef" for c in found[0]):
        raise RuntimeError("Owned name is ambiguous; retaining the run record.")
    current = found[0]
    if captured is not None and captured != current:
        raise RuntimeError("Container ID changed; retaining the run record.")
    raw_details: object = json.loads(docker(root, ["inspect", current], cancelled=cancelled, deadline=deadline))
    if not isinstance(raw_details, list):
        raise RuntimeError("Could not reconcile the owned container.")
    details = cast(list[object], raw_details)
    if len(details) != 1 or not isinstance(details[0], dict):
        raise RuntimeError("Could not reconcile the owned container.")
    item = cast(dict[str, Any], details[0])
    config, host = item["Config"], item["HostConfig"]
    labels: dict[str, Any] = config.get("Labels") or {}
    security: list[str] = host.get("SecurityOpt") or []
    profile = next((entry.removeprefix("seccomp=") for entry in security if entry.startswith("seccomp=")), "")
    try:
        valid_profile = json.loads(profile) == json.loads((root / "build/context/seccomp.json").read_text())
    except ValueError:
        valid_profile = False
    checks = (
        item["Id"] == current,
        item["Image"] == setup_value["image"],
        captured is not None or item["Name"] == "/" + name,
        labels.get(LABEL) == intent["nonce"],
        config["User"] == "0:0",
        host["NetworkMode"] == "none",
        host["IpcMode"] == "private",
        host["ReadonlyRootfs"] is True,
        host["Privileged"] is False,
        host.get("CapDrop") == ["ALL"],
        set(host.get("CapAdd") or []) == {"CAP_SETUID", "CAP_SETGID", "CAP_KILL"},
        not host.get("Binds"),
        not host.get("Mounts"),
        not item.get("Mounts"),
        not host.get("Devices"),
        not host.get("DeviceRequests"),
        not host.get("PidMode"),
        not host.get("UTSMode"),
        not host.get("PortBindings"),
        not host.get("PublishAllPorts"),
        host["NanoCpus"] == 2000000000,
        host["Memory"] == 2 * 1024**3,
        host["MemorySwap"] == 2 * 1024**3,
        host["ShmSize"] == 256 * 1024**2,
        host["PidsLimit"] == 512,
        host["Tmpfs"]
        == {
            "/tmp": "rw,nosuid,nodev,size=256m,mode=1777",
            "/run/desktop": "rw,nosuid,nodev,size=64m,uid=1000,gid=1000,mode=0755",
            "/run/desktop-owner": "rw,nosuid,nodev,size=8m,uid=0,gid=0,mode=0700",
            "/home/desktop": "rw,nosuid,nodev,size=768m,uid=1000,gid=1000,mode=0700",
        },
        len(security) == 2 and "no-new-privileges" in security and valid_profile,
        config["Cmd"] == ["python3", "-I", "/opt/desktop/start.py"],
        not config.get("Entrypoint"),
    )
    if not all(checks):
        raise RuntimeError("Container no longer has this owner's exact image, labels and isolation.")
    return item


def start(root: Path, *, cancelled: Callable[[], bool] | None = None) -> str:
    deadline = time.monotonic() + 60

    def stopped() -> bool:
        return (cancelled is not None and cancelled()) or time.monotonic() >= deadline

    value = runtime(root)
    root = Path(value["owner"]["path"])
    check_image(root, value, cancelled=stopped)
    check_cancelled(stopped)
    id = secrets.token_hex(6)
    directory = root / "runs" / id
    directory.mkdir(mode=0o700)
    intent: dict[str, Any] = {
        "owner": identity(directory),
        "name": "openai-desktop-" + id,
        "nonce": secrets.token_hex(24),
        "image": value["image"],
    }
    receipt = directory / "intent.json"
    created: os.stat_result | None = None
    dispatched = False

    def dispatch() -> None:
        nonlocal dispatched
        # From here, Popen may have reached Docker even if launch is interrupted.
        dispatched = True

    try:
        # Keep a stop pending only until the exclusively created file is identified.
        # Otherwise interruption between open and fstat strands an unclaimed receipt.
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            with receipt.open("x") as output:
                created = os.fstat(output.fileno())
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
                os.fchmod(output.fileno(), 0o600)
                json.dump(intent, output)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        # One create attempt. A cancelled caller cannot retry it.
        docker(
            root,
            [
                "create",
                "--pull=never",
                "--name",
                intent["name"],
                "--cidfile",
                str(directory / "container-id"),
                "--label",
                LABEL + "=" + intent["nonce"],
                "--user",
                "0:0",
                "--init",
                "--network",
                "none",
                "--ipc",
                "private",
                "--read-only",
                "--cap-drop=ALL",
                "--cap-add=SETUID",
                "--cap-add=SETGID",
                "--cap-add=KILL",
                "--security-opt",
                "no-new-privileges",
                "--security-opt",
                "seccomp=" + str(root / "build/context/seccomp.json"),
                "--pids-limit",
                "512",
                "--cpus",
                "2",
                "--memory",
                "2g",
                "--memory-swap",
                "2g",
                "--shm-size",
                "256m",
                "--tmpfs",
                "/tmp:rw,nosuid,nodev,size=256m,mode=1777",
                "--tmpfs",
                "/run/desktop:rw,nosuid,nodev,size=64m,uid=1000,gid=1000,mode=0755",
                "--tmpfs",
                "/run/desktop-owner:rw,nosuid,nodev,size=8m,uid=0,gid=0,mode=0700",
                "--tmpfs",
                "/home/desktop:rw,nosuid,nodev,size=768m,uid=1000,gid=1000,mode=0700",
                str(value["image"]),
            ],
            cancelled=stopped,
            on_dispatch=dispatch,
        )
        item = lookup(root, id, cancelled=stopped)
        if item is None:
            raise RuntimeError("New container could not be reconciled; run retained.")
    except BaseException:
        if dispatched:
            # Ignore the cancelled predicate. An uncertain create keeps its receipt.
            remove(root, id)
        else:
            # No create was dispatched; never infer ownership from a partial receipt.
            if identity(directory) != intent["owner"]:
                raise ValueError("Pre-create directory changed; run retained.") from None
            if created is not None:
                current = receipt.lstat()
                if not stat.S_ISREG(current.st_mode) or (current.st_dev, current.st_ino, current.st_uid) != (
                    created.st_dev,
                    created.st_ino,
                    created.st_uid,
                ):
                    raise ValueError("Pre-create receipt changed; run retained.") from None
                receipt.unlink()
            directory.rmdir()
        raise
    try:
        docker(root, ["start", str(item["Id"])], cancelled=stopped)
        check_cancelled(stopped)
    except BaseException:
        # The created container was reconciled; remove only that verified owner.
        remove(root, id)
        raise
    return id


def healthy(root: Path, id: str, *, cancelled: Callable[[], bool] | None = None, deadline: float | None = None) -> bool:
    if deadline is None:
        deadline = time.monotonic() + 30
    root = checked_root(root)
    current = lookup(root, id, cancelled=cancelled, deadline=deadline)
    return current is not None and current["State"]["Running"] is True


def exchange(
    root: Path,
    id: str,
    data: bytes,
    timeout: float,
    limit: int,
    *,
    cancelled: Callable[[], bool] | None = None,
) -> bytes:
    deadline = time.monotonic() + timeout
    root = checked_root(root)
    current = lookup(root, id, cancelled=cancelled, deadline=deadline)
    if current is None or not current["State"]["Running"]:
        raise RuntimeError("Private container has stopped.")
    # No retry: a failed exec can have delivered input and the Desktop owner will retire.
    return docker(
        root,
        ["exec", "-i", str(current["Id"]), "python3", "-I", "/opt/desktop/bridge.py"],
        data=data,
        timeout=timeout,
        limit=limit,
        cancelled=cancelled,
        deadline=deadline,
    )


def remove(root: Path, id: str, *, deadline: float | None = None) -> None:
    if deadline is None:
        deadline = time.monotonic() + 30
    root = checked_root(root)
    if len(id) != 12 or any(c not in "0123456789abcdef" for c in id):
        raise ValueError("Invalid owned run ID.")
    directory = root / "runs" / id
    cleanup = root / "runs" / (".cleanup-" + id)
    moved = cleanup / "run"
    marker = cleanup / "owner.json"
    try:
        owned(cleanup, 0o700, True)
    except FileNotFoundError:
        directory, intent, _ = run_record(root, id)
        current = lookup(root, id, deadline=deadline)
        if current is not None:
            # Persist a positively reconciled CID before mutation when the original
            # create reply never wrote one. Later absence can then be proven by ID.
            cidfile = directory / "container-id"
            try:
                with cidfile.open("x") as output:
                    os.fchmod(output.fileno(), 0o600)
                    output.write(str(current["Id"]))
                    output.flush()
                    os.fsync(output.fileno())
            except FileExistsError:
                recorded = lookup(root, id, deadline=deadline)
                if recorded is None or recorded["Id"] != current["Id"]:
                    raise RuntimeError("Container changed while recording ownership; run retained.") from None
            docker(root, ["rm", "-f", str(current["Id"])], deadline=deadline)
            if lookup(root, id, deadline=deadline) is not None:
                raise RuntimeError("Could not confirm stopped container; run retained.") from None
        cleanup.mkdir(mode=0o700)
        write_new(marker, intent["owner"])
    else:
        # Another CLI invocation may be finishing an interrupted recursive delete.
        runtime(root)
        try:
            owned(marker, 0o600)
        except FileNotFoundError:
            # Only an empty, owned cleanup directory can be an interrupted
            # marker creation or final removal. Never remove unexpected contents.
            cleanup.rmdir()
            try:
                owned(directory, 0o700, True)
            except FileNotFoundError:
                return
            remove(root, id, deadline=deadline)
            return
    owned(marker, 0o600)
    try:
        expected: dict[str, Any] = json.loads(marker.read_text())
    except json.JSONDecodeError:
        # An interrupted marker write is recoverable only before the run moved.
        # Revalidate its original receipt and preserve any unexpected cleanup data.
        run_record(root, id)
        if set(cleanup.iterdir()) != {marker}:
            raise
        marker.unlink()
        cleanup.rmdir()
        remove(root, id, deadline=deadline)
        return
    if expected.get("path") != str(root.resolve() / "runs" / id):
        raise RuntimeError("Run directory changed while reaping; cleanup record retained.")
    try:
        now = owned(moved, 0o700, True)
    except FileNotFoundError:
        try:
            now = owned(directory, 0o700, True)
        except FileNotFoundError:
            now = None
        if now is not None:
            if now.st_ino != expected.get("inode") or now.st_dev != expected.get("device"):
                raise RuntimeError("Run directory changed while reaping; cleanup record retained.") from None
            directory.rename(moved)
            now = owned(moved, 0o700, True)
    if now is not None:
        fd = os.open(moved, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            now = os.fstat(fd)
            if (
                now.st_ino != expected.get("inode")
                or now.st_dev != expected.get("device")
                or now.st_uid != os.getuid()
                or stat.S_IMODE(now.st_mode) != 0o700
            ):
                raise RuntimeError("Run directory changed while reaping; private cleanup directory retained.")
            for _, directories, files, here in os.fwalk(".", topdown=False, follow_symlinks=False, dir_fd=fd):
                for name in files:
                    os.unlink(name, dir_fd=here)
                for name in directories:
                    info = os.stat(name, dir_fd=here, follow_symlinks=False)
                    if stat.S_ISLNK(info.st_mode):
                        os.unlink(name, dir_fd=here)
                    else:
                        os.rmdir(name, dir_fd=here)
            current = owned(moved, 0o700, True)
            if current.st_ino != now.st_ino or current.st_dev != now.st_dev:
                raise RuntimeError("Run directory changed while reaping; private cleanup directory retained.")
            moved.rmdir()
        finally:
            os.close(fd)
    marker.unlink()
    cleanup.rmdir()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("preflight", "start", "health", "exchange", "remove"))
    parser.add_argument("--runtime-dir", type=Path)
    parser.add_argument("--id")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--limit", type=int, default=65536)
    args = parser.parse_args()
    if args.operation != "preflight" and args.runtime_dir is None:
        parser.error("--runtime-dir is required for this operation")
    startup_stopped = False

    def stop_startup(_signal: int, _frame: object) -> None:
        global startup_stopped
        startup_stopped = True

    if args.operation in ("start", "health", "exchange"):
        signal.signal(signal.SIGUSR1, stop_startup)
    try:
        if args.operation == "preflight":
            preflight(args.runtime_dir)
            print("ready")
        elif args.operation == "start":
            print(start(args.runtime_dir, cancelled=lambda: startup_stopped))
        elif args.operation == "health":
            print(
                "ready"
                if healthy(
                    args.runtime_dir,
                    args.id,
                    cancelled=lambda: startup_stopped,
                    deadline=time.monotonic() + args.timeout,
                )
                else "stopped"
            )
        elif args.operation == "exchange":
            sys.stdout.buffer.write(
                exchange(
                    args.runtime_dir,
                    args.id,
                    sys.stdin.buffer.readline(16385),
                    args.timeout,
                    args.limit,
                    cancelled=lambda: startup_stopped,
                )
            )
        else:
            remove(args.runtime_dir, args.id, deadline=time.monotonic() + args.timeout)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"{exc}\n")
