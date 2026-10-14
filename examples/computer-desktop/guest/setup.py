"""Build the fixed Mac desktop guest, or validate one this script already built."""

from __future__ import annotations

import os
import sys
import gzip
import json
import stat
import shutil
import signal
import hashlib
import inspect
import argparse
import platform
import subprocess
import urllib.parse
import urllib.request
from typing import NamedTuple
from pathlib import Path

HERE = Path(__file__).resolve().parent
# This trusted checkout path also works when the verifier is started with python -I -S.
sys.path.insert(0, str(HERE.parent))
from container_runtime import setup as container_setup, checked_root  # noqa: E402

GUEST_FILES = (
    "preseed.cfg",
    "finish-guest.sh",
    "init-media.sh",
    "desktop.service",
    "desktop-action.socket",
    "desktop-action@.service",
    "action.py",
    "start.py",
    "fixture.html",
)
STAGED_INPUTS = {
    "bp22/preseed.cfg": "preseed.cfg",
    "bp22/finish-guest.sh": "finish-guest.sh",
    "bp22/desktop.service": "desktop.service",
    "bp22/desktop-action.socket": "desktop-action.socket",
    "bp22/desktop-action@.service": "desktop-action@.service",
    "bp22/fixed/action.py": "action.py",
    "bp22/fixed/start.py": "start.py",
    "bp22/fixed/fixture.html": "fixture.html",
    "initrd/preseed.cfg": "preseed.cfg",
    "initrd/bp22-media-init": "init-media.sh",
}
DVD_NAME = "debian-12.13.0-arm64-DVD-1.iso"
CD = "https://cdimage.debian.org/cdimage/archive/12.13.0/arm64/iso-dvd/"
DEBIAN = "https://snapshot.debian.org/archive/debian/20260111T000000Z/"
ALLOWED_DOWNLOAD_HOSTS = frozenset({"cdimage.debian.org", "chuangtzu.ftp.acc.umu.se", "snapshot.debian.org"})


class Media(NamedTuple):
    path: str
    url: str
    size: int
    digest: str
    algorithm: str


# The DVD digest comes from Debian's signed CD manifest. The two package
# digests come from the matching signed Bookworm ARM64 Packages index.
MEDIA = (
    Media(
        DVD_NAME,
        CD + DVD_NAME,
        3989385216,
        "381716dd4e85795854f65277556bdfb1bf4f45e71f62faa53cbfdd657201d0744"
        "afc5d44b9fd184d3360ec6b510b3e00194c6cb554b92d033d1c5a7d9d0ce8cd",
        "sha512",
    ),
    Media(
        "extra/xdotool_3.20160805.1-5_arm64.deb",
        DEBIAN + "pool/main/x/xdotool/xdotool_3.20160805.1-5_arm64.deb",
        53884,
        "7c7ba0b27f05947c9f9aa61f633696719ba578a53d54e90c9b8f7992610c917a",
        "sha256",
    ),
    Media(
        "extra/xvfb_21.1.7-3+deb12u11_arm64.deb",
        DEBIAN + "pool/main/x/xorg-server/xvfb_21.1.7-3%2Bdeb12u11_arm64.deb",
        3083120,
        "03802df143b8b0814d51ebfbe98e6bc746536139cad579d82582783a7a5a2283",
        "sha256",
    ),
)


class OfficialRedirects(urllib.request.HTTPRedirectHandler):
    # This Python 3.10 bootstrap uses only the standard library, which has no override decorator.
    def redirect_request(  # pyright: ignore[reportImplicitOverride]
        self, req: urllib.request.Request, fp: object, code: int, msg: str, headers: object, newurl: str
    ) -> urllib.request.Request | None:
        url = urllib.parse.urlsplit(newurl)
        if (
            url.scheme != "https"
            or url.hostname not in ALLOWED_DOWNLOAD_HOSTS
            or url.port not in (None, 443)
            or url.username is not None
            or url.password is not None
        ):
            raise ValueError("Debian redirected outside the fixed official download hosts.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)  # type: ignore[arg-type]


def digest(path: Path, algorithm: str = "sha256") -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def owned(path: Path, mode: int, *, directory: bool = False) -> os.stat_result:
    info = path.lstat()
    kind = stat.S_ISDIR if directory else stat.S_ISREG
    if not kind(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != mode:
        raise ValueError(f"Expected owned mode-{mode:04o} {'directory' if directory else 'file'}: {path}")
    return info


def disk_identity(root: Path) -> list[int]:
    disk = owned(root / "build" / "desktop.raw", 0o400)
    if disk.st_size != 16 * 1024**3:
        raise ValueError("Guest image has the wrong size.")
    return [disk.st_dev, disk.st_ino, disk.st_size, disk.st_mtime_ns]


def recipe() -> dict[str, str]:
    # Hash provisioning independently of this host-side receipt verifier. In
    # particular, editing launch validation must not change the guest identity.
    provisioning = "".join(
        inspect.getsource(part)
        for part in (OfficialRedirects, digest, check_media, command, executable, download, run_staged_installer, build)
    )
    return {
        **{name: digest(HERE / name) for name in (*GUEST_FILES, "install.py")},
        "media": hashlib.sha256(json.dumps(MEDIA).encode()).hexdigest(),
        "build": hashlib.sha256((provisioning + json.dumps(STAGED_INPUTS, sort_keys=True)).encode()).hexdigest(),
    }


def verify_staged(build: Path, expected: dict[str, str]) -> None:
    for name in (*GUEST_FILES, "install.py"):
        if digest(build / "inputs" / name) != expected[name]:
            raise ValueError("Guest provisioning snapshot changed.")
    for destination, name in STAGED_INPUTS.items():
        if digest(build / destination) != expected[name]:
            raise ValueError("Staged guest provisioning differs from the captured recipe.")


def verify(root: Path) -> None:
    root = checked_root(root)
    owned(root, 0o700, directory=True)
    owned(root / "runs", 0o700, directory=True)
    owned(root / "bin", 0o700, directory=True)
    owned(root / "build", 0o700, directory=True)
    owned(root / "bin" / "vfkit", 0o700)
    owned(root / "setup.json", 0o600)
    receipt: object = json.loads((root / "setup.json").read_text())
    current = recipe()
    expected: dict[str, object] = {
        "recipe": current,
        "disk": disk_identity(root),
        "vfkit": digest(root / "bin" / "vfkit"),
    }
    accepted = [expected]
    # Legacy v1 stored a whole setup.py hash. Its three previously verified
    # launchers may only be reused with these original provisioning inputs.
    # New receipts separate build and media, so this list must never grow.
    image_fingerprint = hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest()
    if image_fingerprint == "8910ffd7272147adffaaf60b81e9e19c0d5723fb0b2b32e2bc3724e7880e1527":
        guest_recipe = {name: current[name] for name in (*GUEST_FILES, "install.py")}
        for launcher in (
            "83aca5abddda1de4c378f039bbf8d03919e7b8fa040eea3f7b73f74165f5371b",
            "e7dd9dca9752560369f1ea9d8e2eb6a515a52c7f03f95868a00e046f1b8279f2",
            "d7ea5a8ba6b12769814cd9e49c087b62253d86bd449d6b0d8d52b7c4ddbd7767",
        ):
            accepted.append({**expected, "recipe": {**guest_recipe, "setup.py": launcher}})
    if receipt not in accepted:
        raise ValueError("Existing runtime does not match this finished setup. Use a new runtime directory.")


def check_media(directory: Path) -> None:
    for item in MEDIA:
        source = directory / item.path
        if source.stat().st_size != item.size or digest(source, item.algorithm) != item.digest:
            raise ValueError(f"Wrong Debian media bytes: {source}")


def command(args: list[str], *, output: Path | None = None) -> None:
    if output is None:
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, timeout=300)
    else:
        with output.open("xb") as stream:
            subprocess.run(args, check=True, stdout=stream, timeout=300)


def executable(name: str, supplied: Path | None) -> Path:
    found = str(supplied) if supplied is not None else shutil.which(name)
    if found is None:
        raise ValueError(
            f"Missing {name}. Install the tested upstream tool described in guest/README.md, "
            f"or pass --{name} /absolute/path/to/{name}."
        )
    result = Path(found).absolute()
    if not result.is_file() or not os.access(result, os.X_OK):
        raise ValueError(f"Not an executable: {result}")
    return result


def download(directory: Path) -> None:
    (directory / "extra").mkdir(parents=True, mode=0o700)
    opener = urllib.request.build_opener(OfficialRedirects())
    for item in MEDIA:
        print(f"Fetching fixed Debian input: {item.path}", flush=True)
        # Never send credentials or caller data. Only this pinned fixed URL is requested.
        with opener.open(item.url, timeout=60) as response, (directory / item.path).open("xb") as output:
            remaining = item.size
            while remaining:
                chunk = response.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ValueError(f"Incomplete Debian download: {item.path}")
                output.write(chunk)
                remaining -= len(chunk)
            if response.read(1):
                raise ValueError(f"Unexpected Debian download size: {item.path}")
    check_media(directory)


def run_staged_installer(root: Path) -> None:
    args = [sys.executable, "-I", "-S", str(root / "build" / "inputs" / "install.py"), "--runtime-dir", str(root)]
    with subprocess.Popen(args) as process:
        try:
            result = process.wait()
        except BaseException:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                process.wait()
            raise
        if result:
            raise subprocess.CalledProcessError(result, args)


def setup(root: Path, media_dir: Path | None, vfkit_path: Path | None, xorriso_path: Path | None) -> None:
    root = checked_root(root)
    socket = str(root / "runs" / "0123456789ab" / "a.sock")
    if len(socket.encode()) >= 104 or any(c in socket for c in "% ,"):
        raise ValueError("Runtime path must fit a 104-byte Unix socket and contain no spaces, commas or percent signs.")
    try:
        root.lstat()
    except FileNotFoundError:
        pass
    else:
        verify(root)
        print(f"Ready: {root} (existing guest validated; no build or download)", flush=True)
        return
    build(root, media_dir, vfkit_path, xorriso_path)


def build(root: Path, media_dir: Path | None, vfkit_path: Path | None, xorriso_path: Path | None) -> None:
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise ValueError("This fixed guest setup requires an Apple-silicon Mac.")
    vfkit = executable("vfkit", vfkit_path)
    xorriso = executable("xorriso", xorriso_path)
    for tool in ("/usr/bin/bsdtar", "/usr/bin/codesign"):
        if not os.access(tool, os.X_OK):
            raise ValueError(f"Required macOS tool is missing: {tool}")
    if shutil.disk_usage(root.parent).free < 12 * 1024**3:
        raise ValueError("Allow at least 12 GiB free for downloaded media, remastered DVD and guest disk.")
    initial_recipe = recipe()
    # mkdir is exclusive: never retry into someone else's runtime or a failed build.
    root.mkdir(mode=0o700)
    owned(root, 0o700, directory=True)
    for name in ("bin", "build", "runs"):
        (root / name).mkdir(mode=0o700)
    build = root / "build"
    inputs = build / "inputs"
    inputs.mkdir(mode=0o700)
    for name in (*GUEST_FILES, "install.py"):
        target = inputs / name
        shutil.copyfile(HERE / name, target)
        target.chmod(0o600)
        if digest(target) != initial_recipe[name]:
            raise ValueError("Guest provisioning changed while taking its snapshot.")
    copied_vfkit = root / "bin" / "vfkit"
    shutil.copyfile(vfkit, copied_vfkit)
    copied_vfkit.chmod(0o700)
    command(["/usr/bin/codesign", "--verify", "--strict", str(copied_vfkit)])
    source_media = media_dir
    media_dir = build / "downloads"
    if source_media is None:
        download(media_dir)
    else:
        (media_dir / "extra").mkdir(parents=True, mode=0o700)
        for item in MEDIA:
            shutil.copyfile(source_media / item.path, media_dir / item.path)
        check_media(media_dir)
    for name in ("bp22", "bp22/fixed", "bp22/extra", "initrd"):
        (build / name).mkdir(mode=0o755 if name.startswith("bp22") else 0o700)
    for destination, name in STAGED_INPUTS.items():
        target = build / destination
        shutil.copyfile(inputs / name, target)
        target.chmod(0o644 if destination.startswith("bp22/") else 0o600)
    (build / "initrd" / "bp22-media-init").chmod(0o755)
    verify_staged(build, initial_recipe)
    for item in MEDIA[1:]:
        target = build / "bp22" / item.path
        shutil.copyfile(media_dir / item.path, target)
        target.chmod(0o644)

    dvd = media_dir / DVD_NAME
    command(["/usr/bin/bsdtar", "-xOf", str(dvd), "install.a64/vmlinuz"], output=build / "vmlinuz")
    command(["/usr/bin/bsdtar", "-xOf", str(dvd), "install.a64/initrd.gz"], output=build / "initrd.gz")
    command(
        [
            "/usr/bin/bsdtar",
            "--format=newc",
            "--uid",
            "0",
            "--gid",
            "0",
            "-cf",
            str(build / "local.cpio"),
            "-C",
            str(build / "initrd"),
            "preseed.cfg",
            "bp22-media-init",
        ]
    )
    with gzip.open(build / "initrd.gz", "rb") as original, (build / "local.cpio").open("rb") as extra:
        with gzip.open(build / "initrd-local.gz", "xb") as combined:
            shutil.copyfileobj(original, combined)
            shutil.copyfileobj(extra, combined)
    print("Verified media. Preparing and installing the fixed no-network guest.", flush=True)
    command(
        [
            str(xorriso),
            "-no_rc",
            "-indev",
            str(dvd),
            "-outdev",
            str(build / "installer.iso"),
            "-map",
            str(build / "bp22"),
            "/bp22",
            "-boot_image",
            "any",
            "replay",
            "-compliance",
            "no_emul_toc",
            "-padding",
            "included",
        ]
    )
    with (build / "desktop.raw").open("xb") as disk:
        disk.truncate(16 * 1024**3)
    verify_staged(build, initial_recipe)
    # Run the exact captured host installer, which owns its own deadlines and
    # reaps its vfkit child on failure. It is never copied into the guest.
    run_staged_installer(root)
    verify_staged(build, initial_recipe)
    if recipe() != initial_recipe:
        raise ValueError("Guest provisioning changed during installation; no receipt was published.")
    receipt = {"recipe": initial_recipe, "disk": disk_identity(root), "vfkit": digest(root / "bin" / "vfkit")}
    with (root / "setup.json").open("x") as output:
        json.dump(receipt, output)
        output.write("\n")
    (root / "setup.json").chmod(0o600)
    print(f"Ready: {root}. Run the SDK's no-key exercise to check native desktop actions.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--backend", choices=("vm", "container"), default="vm")
    parser.add_argument(
        "--verify-only", action="store_true", help="Validate an existing VM without installing anything."
    )
    parser.add_argument("--media-dir", type=Path, help="Offline: directory containing the fixed DVD and extra/*.deb.")
    parser.add_argument("--vfkit", type=Path, help="Trusted vfkit executable, if it is not on PATH.")
    parser.add_argument("--xorriso", type=Path, help="Trusted xorriso executable, if it is not on PATH.")
    options = parser.parse_args()

    def stop(_signal: int, _frame: object) -> None:
        # Let the owned installer reap its VM before another signal can interrupt cleanup.
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        raise KeyboardInterrupt

    previous_term = signal.signal(signal.SIGTERM, stop)
    previous_int = signal.signal(signal.SIGINT, stop)
    try:
        if options.verify_only:
            if options.backend != "vm" or options.media_dir or options.vfkit or options.xorriso:
                raise ValueError("VM verify-only cannot be combined with provisioning or container options.")
            verify(options.runtime_dir)
        elif options.backend == "container":
            if options.media_dir or options.vfkit or options.xorriso:
                raise ValueError("VM options cannot be used with the container backend.")
            container_setup(options.runtime_dir)
        else:
            setup(options.runtime_dir, options.media_dir, options.vfkit, options.xorriso)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Setup failed: {exc}\nExisting files were preserved; use a new path for an incomplete build.\n")
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        signal.signal(signal.SIGINT, previous_int)


if __name__ == "__main__":
    main()
