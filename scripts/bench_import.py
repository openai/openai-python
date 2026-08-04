#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path


def _pythonpath_for_repo() -> str | None:
    src = Path(__file__).resolve().parents[1] / "src"
    if not src.exists():
        return None

    existing = os.environ.get("PYTHONPATH")
    if existing:
        return f"{src}{os.pathsep}{existing}"
    return str(src)


def _cold_import_seconds(repeats: int, env: dict[str, str]) -> list[float]:
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        subprocess.run([sys.executable, "-c", "import openai"], check=True, env=env, stdout=subprocess.DEVNULL)
        samples.append(time.perf_counter() - start)
    return samples


def _importtime_output(env: dict[str, str]) -> str:
    proc = subprocess.run(
        [sys.executable, "-X", "importtime", "-c", "import openai"],
        check=True,
        env=env,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
    )
    return proc.stderr


def _parse_importtime(importtime_stderr: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for line in importtime_stderr.splitlines():
        if "| " not in line:
            continue
        if "import time:" not in line:
            continue
        _, _, payload = line.partition("import time:")
        parts = [p.strip() for p in payload.split("|")]
        if len(parts) != 3:
            continue
        cumulative_raw = parts[1]
        module = parts[2]
        if not module.startswith("openai"):
            continue
        try:
            cumulative = int(cumulative_raw)
        except ValueError:
            continue
        rows.append((cumulative, module))
    rows.sort(reverse=True)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark openai import time for this checkout.")
    parser.add_argument("--repeats", type=int, default=5, help="Number of cold imports to sample")
    parser.add_argument("--top", type=int, default=20, help="How many importtime rows to print")
    args = parser.parse_args()

    env = dict(os.environ)
    pythonpath = _pythonpath_for_repo()
    if pythonpath is not None:
        env["PYTHONPATH"] = pythonpath

    samples = _cold_import_seconds(repeats=args.repeats, env=env)
    avg = sum(samples) / len(samples)

    print(f"Python: {sys.executable}")
    print(f"Samples (s): {[round(s, 4) for s in samples]}")
    print(f"Average cold import (s): {avg:.4f}")
    print()

    rows = _parse_importtime(_importtime_output(env))
    print(f"Top {min(args.top, len(rows))} cumulative importtime rows (us):")
    for cumulative, module in rows[: args.top]:
        print(f"{cumulative:>8}  {module}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
