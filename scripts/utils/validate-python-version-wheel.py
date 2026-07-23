from __future__ import annotations

import sys
import email
import tarfile
import zipfile
import argparse
import platform
import tempfile
import subprocess
from pathlib import Path
from email.message import Message

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_REQUIRES_PYTHON = ">=3.10"


def wheel_metadata(wheel: Path) -> Message:
    with zipfile.ZipFile(wheel) as archive:
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise RuntimeError(f"Expected exactly one METADATA file in {wheel}, found: {names}")
        return email.message_from_bytes(archive.read(names[0]))


def sdist_metadata(sdist: Path) -> Message:
    with tarfile.open(sdist) as archive:
        members = [member for member in archive.getmembers() if member.name.endswith("/PKG-INFO")]
        if len(members) != 1:
            raise RuntimeError(f"Expected exactly one PKG-INFO file in {sdist}, found: {members}")
        extracted = archive.extractfile(members[0])
        if extracted is None:
            raise RuntimeError(f"Could not read {members[0].name} from {sdist}")
        return email.message_from_bytes(extracted.read())


def assert_python_39_rejected(wheel: Path) -> None:
    if platform.python_version_tuple()[:2] != ("3", "9"):
        raise RuntimeError(f"The resolver check must run on Python 3.9, found {sys.version.split()[0]}")

    with tempfile.TemporaryDirectory(prefix="openai-python-version-wheel-") as directory:
        environment_path = Path(directory) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(environment_path)], check=True)
        python = environment_path / "bin/python"
        result = subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--dry-run",
                "--ignore-installed",
                "--no-deps",
                str(wheel.resolve()),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode == 0:
        raise RuntimeError("Python 3.9 unexpectedly accepted the built wheel")

    output = result.stdout + result.stderr
    if "3.10" not in output or "Python" not in output:
        raise RuntimeError(f"Python 3.9 rejection failed for an unexpected reason:\n{output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-python-39",
        action="store_true",
        help="Also prove that pip on an actual Python 3.9 interpreter rejects the wheel",
    )
    args = parser.parse_args()

    wheels = list((ROOT / "dist").glob("*.whl"))
    sdists = list((ROOT / "dist").glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError(f"Expected one wheel and one sdist, found wheels={wheels}, sdists={sdists}")

    for artifact, metadata in (
        (wheels[0], wheel_metadata(wheels[0])),
        (sdists[0], sdist_metadata(sdists[0])),
    ):
        actual = metadata["Requires-Python"]
        if actual != EXPECTED_REQUIRES_PYTHON:
            raise RuntimeError(f"Expected {artifact.name} to require {EXPECTED_REQUIRES_PYTHON}, found {actual}")

    if args.check_python_39:
        assert_python_39_rejected(wheels[0])
        print("Validated wheel and sdist Python metadata and Python 3.9 rejection")
    else:
        print("Validated wheel and sdist Python metadata")


if __name__ == "__main__":
    main()
