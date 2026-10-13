"""Freeze and execute exactly the prospective 14 local release-workflow trials."""

from __future__ import annotations

import os
import json
import stat
import hashlib
import tarfile
import zipfile
import argparse
import subprocess
from typing import Any, cast
from pathlib import Path
from urllib.parse import unquote, urlparse


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_settings(path: Path) -> dict[str, Any]:
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise RuntimeError("Live config must be an owner-only regular file.")
    settings: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return settings


def save(path: Path, data: object) -> None:
    with path.open("x", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def resolved_sdk_files(node: Path, python: Path, node_package: Path, python_package: Path) -> list[Path]:
    # Resolve exactly as the entry points do; importing these SDK modules performs no request.
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("OPENAI_") and key != "LONG_WORKFLOW_MODEL"
    }
    resolved_node = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            'const names = ["openai", "openai/helpers/browser", "openai/helpers/responses-tool-runner", "openai/helpers/decisions-tool-runner"];'
            "process.stdout.write(JSON.stringify(names.map(name => import.meta.resolve(name))));",
        ],
        cwd=node.parent,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    node_paths = [Path(unquote(urlparse(value).path)) for value in cast(list[str], json.loads(resolved_node.stdout))]
    node_root = node_paths[0].parent
    with tarfile.open(node_package) as archive:
        for path in node_paths:
            item = archive.extractfile("package/" + path.relative_to(node_root).as_posix())
            if item is None or item.read() != path.read_bytes():
                raise RuntimeError(f"Resolved Node SDK file does not match archive: {path}")
    resolved_python = subprocess.run(
        [
            str(python),
            "-c",
            "import json,openai,openai.lib.browser as b,openai.lib.responses_tool_runner as r,openai.lib.decisions_tool_runner as d;"
            "print(json.dumps([module.__file__ for module in (openai,b,r,d)]))",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    python_paths = [Path(path) for path in json.loads(resolved_python.stdout)]
    python_root = python_paths[0].parent.parent
    with zipfile.ZipFile(python_package) as archive:
        for path in python_paths:
            if archive.read(path.relative_to(python_root).as_posix()) != path.read_bytes():
                raise RuntimeError(f"Resolved Python SDK file does not match archive: {path}")
    return [*node_paths, *python_paths]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--directory", type=Path, required=True)
    freeze.add_argument("--node-entry", type=Path, required=True)
    freeze.add_argument("--python-entry", type=Path, required=True)
    freeze.add_argument("--python", type=Path, required=True)
    freeze.add_argument("--node-package", type=Path, required=True)
    freeze.add_argument("--python-package", type=Path, required=True)
    freeze.add_argument("--mode", choices=("rehearsal", "live"), required=True)
    for command in (freeze, sub.add_parser("run")):
        if command is not freeze:
            command.add_argument("--directory", type=Path, required=True)
        command.add_argument("--private-config", type=Path)
    args = parser.parse_args()
    directory = args.directory.absolute()
    manifest_path = directory / "manifest.json"
    if args.command == "freeze":
        if (args.mode == "live") != (args.private_config is not None):
            raise RuntimeError("Only live freeze requires --private-config.")
        if args.mode == "live":
            private_settings(args.private_config)
        directory.mkdir(parents=False, exist_ok=False)
        node = args.node_entry.absolute()
        python = args.python_entry.absolute()
        # Hash the exact examples and driver modules consumed, not only the source checkout.
        sources = [
            node,
            node.parent / "driver.mjs",
            node.parent / "owned-pointer.mjs",
            node.parent / "long-workflow-fixture.html",
            node.parent / "long-workflow-oracle.json",
            node.parent / "package.json",
            python,
            python.parent / "browser_driver.py",
            python.parent / "owned_pointer.py",
            python.parent / "long-workflow-fixture.html",
            python.parent / "long-workflow-oracle.json",
            Path(__file__).absolute(),
            args.node_package.absolute(),
            args.python_package.absolute(),
        ]
        sources.extend(resolved_sdk_files(node, args.python.absolute(), args.node_package, args.python_package))
        order = [
            {"sdk": sdk, "variant": variant, "api": api, "scenario": "normal"}
            for variant in ("A", "B")
            for sdk in ("node", "python")
            for api in ("responses", "decisions")
        ] + [
            {"sdk": sdk, "variant": "A", "api": "responses", "scenario": scenario}
            for sdk in ("node", "python")
            for scenario in ("refuse", "stop", "resume")
        ]
        manifest = {
            "version": 1,
            "mode": args.mode,
            "order": order,
            "limits": {"requests_per_trial": 64, "trial_ms": 180000, "process_and_cleanup_seconds": 210},
            "controller": "normal; refuse first Save; Stop third Save; resume only from explained correct partial state",
            "config_sha256": digest(args.private_config)
            if args.mode == "live"
            else hashlib.sha256(b"rehearsal-local").hexdigest(),
            "node_entry": str(node),
            "python_entry": str(python),
            "python": str(args.python.absolute()),
            "files_sha256": {str(path): digest(path) for path in sources},
        }
        save(manifest_path, manifest)
        manifest_path.chmod(0o444)
        save(directory / "manifest-sha256.json", {"sha256": digest(manifest_path)})
        return 0

    manifest_hash = json.loads((directory / "manifest-sha256.json").read_text())["sha256"]
    if digest(manifest_path) != manifest_hash:
        raise RuntimeError("Prospective manifest changed.")
    manifest = json.loads(manifest_path.read_text())
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("OPENAI_") and key != "LONG_WORKFLOW_MODEL"
    }
    models = {"responses": "local", "decisions": "local"}
    if manifest["mode"] == "live":
        if args.private_config is None or digest(args.private_config) != manifest["config_sha256"]:
            raise RuntimeError("Private config differs from prospective manifest.")
        settings = private_settings(args.private_config)
        models = settings["models"]
        key_file = Path(settings["keyFile"])
        info = key_file.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise RuntimeError("Key file must be an owner-only regular file.")
        environment["OPENAI_API_KEY"] = key_file.read_text(encoding="utf-8").strip()
    elif args.private_config is not None:
        raise RuntimeError("Rehearsal must not receive a credential config.")
    summary: list[dict[str, object]] = []
    halted = False
    for index, trial in enumerate(manifest["order"], 1):
        if halted:
            summary.append(
                {"index": index, **trial, "status": "not_started", "reason": "previous safety/cleanup failure"}
            )
            continue
        if any(digest(Path(path)) != expected for path, expected in manifest["files_sha256"].items()):
            summary.append({"index": index, **trial, "status": "not_started", "reason": "frozen input changed"})
            halted = True
            continue
        result = directory / f"trial-{index:02d}.json"
        log = directory / f"trial-{index:02d}.log"
        entry = manifest["node_entry" if trial["sdk"] == "node" else "python_entry"]
        executable = "node" if trial["sdk"] == "node" else manifest["python"]
        child_command = [
            executable,
            entry,
            "--variant",
            trial["variant"],
            "--api",
            trial["api"],
            "--scenario",
            trial["scenario"],
            "--mode",
            manifest["mode"],
            "--output",
            str(result),
        ]
        child_environment = {**environment, "LONG_WORKFLOW_MODEL": models[trial["api"]]}
        with log.open("xb") as stream:
            try:
                completed = subprocess.run(
                    child_command,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    check=False,
                    timeout=manifest["limits"]["process_and_cleanup_seconds"],
                    env=child_environment,
                )
                code = completed.returncode
            except subprocess.TimeoutExpired:
                code = 2
        try:
            receipt = json.loads(result.read_text())
            halted = code == 2 or not receipt["cleanup"] or not receipt.get("oracle", {}).get("explained", False)
            halted = halted or receipt.get("witness_arrivals", 0) != 0
            summary.append(
                {
                    "index": index,
                    **trial,
                    "status": "pass"
                    if code == 0
                    and receipt.get("oracle", {}).get("correct")
                    and receipt.get("oracle", {}).get("lifecycle_valid")
                    else "failed",
                    "exit_code": code,
                    "requests": len(receipt["requests"]),
                    "wall_ms": receipt["wall_ms"],
                    "oracle": receipt.get("oracle"),
                    "phases": receipt["phases"],
                    "escape_attempts": receipt["escape_attempts"],
                    "witness_arrivals": receipt["witness_arrivals"],
                    "cleanup": receipt["cleanup"],
                }
            )
        except (OSError, ValueError, KeyError):
            halted = True
            summary.append(
                {"index": index, **trial, "status": "failed", "exit_code": code, "reason": "missing or invalid receipt"}
            )
    save(directory / "summary.json", {"manifest_sha256": manifest_hash, "trials": summary})
    return 0 if all(trial["status"] == "pass" for trial in summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
