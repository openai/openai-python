"""Check local prerequisites before starting a browser or desktop example. No API key needed."""

from __future__ import annotations

import sys
import json
import shutil
import argparse
import platform
import subprocess
from pathlib import Path
from importlib import import_module

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--environment", choices=("browser", "desktop-vm", "desktop-container"), default="browser")
parser.add_argument("--runtime-dir", type=Path)
args = parser.parse_args()
checks: list[dict[str, object]] = []


def check(name: str, ready: bool, fix: str = "") -> None:
    checks.append({"name": name, "ready": ready, **({} if ready else {"fix": fix})})


supported_runtime = sys.version_info >= (3, 10)
check("Python runtime", supported_runtime, "Use Python 3.10 or later.")
if not supported_runtime:
    print(json.dumps({"environment": args.environment, "ready": False, "checks": checks}, indent=2))
    sys.exit(1)
if args.environment != "browser" and args.runtime_dir is not None and not args.runtime_dir.is_absolute():
    check("Runtime directory", False, "Use an absolute --runtime-dir path.")
    print(json.dumps({"environment": args.environment, "ready": False, "checks": checks}, indent=2))
    sys.exit(1)
try:
    helper = import_module("openai.lib.browser" if args.environment == "browser" else "openai.lib.computer")
    required = "AsyncBrowserToolset" if args.environment == "browser" else "AsyncComputerToolset"
    check(
        "SDK helper",
        callable(getattr(helper, required, None)),
        "Install the matching released SDK: python -m pip install -U openai",
    )
except (ImportError, AttributeError):
    check("SDK helper", False, "Install the matching released SDK: python -m pip install -U openai")

if args.environment != "browser":
    fix = "Run: python -m pip install Pillow==12.3.0"
    try:
        image = import_module("PIL.Image")
        check("Pillow package", callable(getattr(image, "open", None)), fix)
    except (ImportError, OSError):
        check("Pillow package", False, fix)

if args.environment == "browser":
    try:
        from playwright.sync_api import sync_playwright

        check("Playwright package", True)
        with sync_playwright() as playwright:
            if next(row for row in checks if row["name"] == "SDK helper")["ready"]:
                from browser_driver import example_browser_channel

                try:
                    channel = example_browser_channel()
                    if channel == "chrome":
                        check("Chrome channel selected; installation and sandbox will be checked at launch", True)
                    else:
                        check(
                            "Chromium",
                            Path(playwright.chromium.executable_path).is_file(),
                            "Run: python -m playwright install chromium",
                        )
                except ValueError as error:
                    check("Browser channel", False, str(error))
    except ImportError:
        check("Playwright package", False, "Run: python -m pip install playwright==1.63.0")
elif args.environment == "desktop-vm":
    check(
        "Apple silicon host",
        sys.platform == "darwin" and platform.machine() == "arm64",
        "Use an Apple silicon Mac, or choose desktop-container on local Linux.",
    )
    for name in () if args.runtime_dir else ("vfkit", "xorriso"):
        check(
            name,
            shutil.which(name) is not None,
            f"Install the trusted {name} prerequisite in computer-desktop/guest/README.md.",
        )
    if args.runtime_dir:
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-E",
                    "-S",
                    str(Path(__file__).resolve().parents[1] / "computer-desktop/guest/setup.py"),
                    "--runtime-dir",
                    str(args.runtime_dir),
                    "--verify-only",
                ],
                check=True,
                timeout=30,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            check("Completed guest runtime", True)
        except (OSError, subprocess.SubprocessError):
            check(
                "Completed guest runtime",
                False,
                "Build a matching guest with computer-desktop/guest/setup.py, or choose its completed runtime directory.",
            )
else:
    try:
        subprocess.run(
            [
                sys.executable,
                "-E",
                "-S",
                str(Path(__file__).resolve().parents[1] / "computer-desktop/container_runtime.py"),
                "preflight",
                *(["--runtime-dir", str(args.runtime_dir)] if args.runtime_dir else []),
            ],
            check=True,
            timeout=30,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        check("Local Docker runtime", True)
    except (OSError, subprocess.SubprocessError):
        check(
            "Local Docker runtime",
            False,
            "Run python computer-desktop/container_runtime.py preflight to check the local Docker setup. "
            "Add --runtime-dir to check an existing runtime.",
        )
ready = all(item["ready"] for item in checks)
print(json.dumps({"environment": args.environment, "ready": ready, "checks": checks}, indent=2))
sys.exit(0 if ready else 1)
