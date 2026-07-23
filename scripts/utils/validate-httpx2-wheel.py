from __future__ import annotations

import os
import sys
import email
import zipfile
import platform
import tempfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_TEST = ROOT / "tests/test_httpx2_base.py"
HTTPX2_TEST = ROOT / "tests/test_httpx2.py"


def validate_metadata(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise RuntimeError(f"Expected exactly one METADATA file in {wheel}, found: {metadata_names}")
        metadata = email.message_from_bytes(archive.read(metadata_names[0]))

    requirements = metadata.get_all("Requires-Dist", [])
    base = [value for value in requirements if "extra ==" not in value]
    httpx2 = [value for value in requirements if "extra == 'httpx2'" in value]
    aiohttp = [value for value in requirements if "extra == 'aiohttp'" in value]

    if metadata["Requires-Python"] != ">=3.10":
        raise RuntimeError(f"Expected Python >=3.10, found: {metadata['Requires-Python']}")
    if not any(value.startswith("httpx<1,>=0.23.0") for value in base):
        raise RuntimeError(f"Expected the base wheel to require HTTPX >=0.23.0,<1: {base}")
    if not any(value.startswith("anyio<5,>=3.5.0") for value in base):
        raise RuntimeError(f"Expected the base wheel to require AnyIO >=3.5.0,<5: {base}")
    if any(value.startswith("httpx2") for value in base):
        raise RuntimeError(f"HTTPX2 leaked into the base wheel requirements: {base}")

    for expected in ("httpx<1,>=0.25.1", "httpx2<3,>=2.7.0", "anyio<5,>=4.10.0"):
        if not any(value.startswith(expected) for value in httpx2):
            raise RuntimeError(f"Expected the HTTPX2 extra to require {expected}: {httpx2}")
    if any("python_version" in value for value in httpx2):
        raise RuntimeError(f"HTTPX2 requirements have redundant Python markers: {httpx2}")

    if not any(value.startswith("aiohttp>=3.14.1") for value in aiohttp):
        raise RuntimeError(f"Expected the unchanged aiohttp requirement: {aiohttp}")
    if not any(value.startswith("httpx-aiohttp>=0.1.9") for value in aiohttp):
        raise RuntimeError(f"Expected the unchanged httpx-aiohttp requirement: {aiohttp}")


def run_case(wheel: Path, *, extra: str | None, tests: list[Path], dependencies: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="openai-httpx2-wheel-") as directory:
        environment_path = Path(directory) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(environment_path)], check=True)
        python = environment_path / "bin/python"
        requirement = str(wheel.resolve()) if extra is None else f"{wheel.resolve()}[{extra}]"
        environment = os.environ.copy()
        environment.setdefault("PIP_DISABLE_CLIENT_CERTIFICATE", "1")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--quiet", requirement, *dependencies],
            cwd=directory,
            env=environment,
            check=True,
        )
        test_environment = environment.copy()
        for name in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "all_proxy", "https_proxy", "http_proxy"):
            test_environment.pop(name, None)
        subprocess.run(
            [str(python), "-m", "pytest", "-o", "addopts=", *(str(test) for test in tests)],
            cwd=directory,
            env=test_environment,
            check=True,
        )


def assert_incompatible_pin_fails(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="openai-httpx2-conflict-") as directory:
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
                f"{wheel.resolve()}[httpx2]",
                "httpx==0.25.0",
            ],
            cwd=directory,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            raise RuntimeError("Expected openai[httpx2] with httpx==0.25.0 to fail dependency resolution")
        output = result.stdout + result.stderr
        if "ResolutionImpossible" not in output and "conflicting dependencies" not in output:
            raise RuntimeError(f"The incompatible resolution failed for an unexpected reason:\n{output}")


def main() -> None:
    wheels = list((ROOT / "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one wheel in dist/, found: {wheels}")
    wheel = wheels[0]
    validate_metadata(wheel)

    common = ["pytest==8.4.1", "pytest-asyncio==1.1.0", "respx==0.22.0"]
    run_case(wheel, extra=None, tests=[BASE_TEST], dependencies=common)
    if platform.python_version_tuple()[:2] == ("3", "10"):
        run_case(
            wheel,
            extra=None,
            tests=[BASE_TEST],
            dependencies=[
                "pytest==8.4.1",
                "pytest-asyncio==1.1.0",
                "respx==0.20.2",
                "httpx==0.23.0",
                "anyio==3.5.0",
            ],
        )

    run_case(wheel, extra="aiohttp", tests=[BASE_TEST], dependencies=common)
    run_case(wheel, extra="httpx2", tests=[BASE_TEST, HTTPX2_TEST], dependencies=common)
    run_case(
        wheel,
        extra="httpx2",
        tests=[BASE_TEST, HTTPX2_TEST],
        dependencies=[*common, "httpx==0.25.1", "anyio==4.10.0", "pydantic<2", "botocore==1.42.97"],
    )
    assert_incompatible_pin_fails(wheel)
    print("Validated base, aiohttp, native HTTPX2, supported floors, Pydantic modes, and resolver conflicts")


if __name__ == "__main__":
    main()
