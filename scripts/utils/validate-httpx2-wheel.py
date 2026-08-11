from __future__ import annotations

import os
import re
import sys
import email
import zipfile
import tempfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_TEST = ROOT / "tests/test_httpx2_base.py"
HTTPX2_TEST = ROOT / "tests/test_httpx2.py"
LEGACY_TEST = ROOT / "tests/test_httpx_compat.py"


def venv_python(environment_path: Path) -> Path:
    return environment_path / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def requirement_name(requirement: str) -> str:
    match = re.match(r"[A-Za-z0-9_.-]+", requirement)
    if match is None:
        raise RuntimeError(f"Cannot determine the package name for {requirement!r}")
    return match.group().replace("_", "-").lower()


def validate_metadata(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise RuntimeError(f"Expected exactly one METADATA file in {wheel}, found: {metadata_names}")
        metadata = email.message_from_bytes(archive.read(metadata_names[0]))

        for name in ("LICENSE", "README.md", "FORK.md"):
            if f"openai/_vendor/httpx_aiohttp/{name}" not in archive.namelist():
                raise RuntimeError(f"The wheel omitted the vendored aiohttp adapter's {name}")

    requirements = metadata.get_all("Requires-Dist", [])
    base = [value for value in requirements if "extra ==" not in value]
    aiohttp = [value for value in requirements if "extra == 'aiohttp'" in value]
    extras = set(metadata.get_all("Provides-Extra", []))

    if metadata["Requires-Python"] != ">=3.10":
        raise RuntimeError(f"Expected Python >=3.10, found: {metadata['Requires-Python']}")
    for expected in ("httpx2<3,>=2.7.0", "anyio<5,>=4.10.0"):
        if not any(value.startswith(expected) for value in base):
            raise RuntimeError(f"Expected the base wheel to require {expected}: {base}")
    if any(requirement_name(value) == "httpx" for value in requirements):
        raise RuntimeError(f"Legacy HTTPX must not be installed by any SDK extra: {requirements}")
    if any(requirement_name(value) == "httpx-aiohttp" for value in requirements):
        raise RuntimeError(f"The aiohttp extra must not install the legacy adapter package: {requirements}")
    if {"httpx", "httpx2"} & extras:
        raise RuntimeError(f"HTTP client selection must not require or expose an SDK extra: {extras}")
    if not any(value.startswith("aiohttp>=3.14.1") for value in aiohttp):
        raise RuntimeError(f"Expected the aiohttp extra to require a patched aiohttp release: {aiohttp}")


def run_case(
    wheel: Path, *, extra: str | None, tests: list[Path], dependencies: list[str], legacy: bool = False
) -> None:
    with tempfile.TemporaryDirectory(prefix="openai-httpx2-wheel-") as directory:
        environment_path = Path(directory) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(environment_path)], check=True)
        python = venv_python(environment_path)
        requirement = str(wheel.resolve()) if extra is None else f"{wheel.resolve()}[{extra}]"
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment.setdefault("PIP_DISABLE_CLIENT_CERTIFICATE", "1")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--quiet", requirement, *dependencies],
            cwd=directory,
            env=environment,
            check=True,
        )

        if not legacy:
            subprocess.run(
                [str(python), "-c", "import importlib.util; assert importlib.util.find_spec('httpx') is None"],
                cwd=directory,
                env=environment,
                check=True,
            )

        test_environment = environment.copy()
        for name in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "all_proxy", "https_proxy", "http_proxy"):
            test_environment.pop(name, None)
        if legacy:
            test_environment["OPENAI_TEST_LEGACY_HTTPX"] = "1"
        subprocess.run(
            [str(python), "-m", "pytest", "-o", "addopts=", *(str(test) for test in tests)],
            cwd=directory,
            env=test_environment,
            check=True,
        )


def main() -> None:
    wheels = list((ROOT / "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one wheel in dist/, found: {wheels}")
    wheel = wheels[0]
    validate_metadata(wheel)

    common = ["pytest==8.4.1", "pytest-asyncio==1.1.0"]
    run_case(wheel, extra=None, tests=[BASE_TEST, HTTPX2_TEST], dependencies=common)
    run_case(wheel, extra="aiohttp", tests=[BASE_TEST], dependencies=common)
    run_case(
        wheel,
        extra=None,
        tests=[LEGACY_TEST],
        dependencies=[*common, "httpx-aiohttp>=0.2.0,<0.3"],
        legacy=True,
    )
    print("Validated HTTPX2-only base and aiohttp installs plus isolated legacy HTTPX/aiohttp compatibility")


if __name__ == "__main__":
    main()
