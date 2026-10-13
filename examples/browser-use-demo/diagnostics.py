"""Explicit, bounded local capture and an authenticated read-only viewer."""

from __future__ import annotations

import os
import re
import json
import math
import stat
import time
import argparse
import tempfile
from typing import Any, cast
from pathlib import Path
from collections.abc import Iterable

MAX_BYTES = 1024 * 1024
MAX_RUNS = 16


class RunDiagnostics:
    """Keep numeric public facts separate from explicitly enabled private capture."""

    def __init__(self, capture: DiagnosticCapture | None, mode: str) -> None:
        self.recorder = capture.start() if capture else None
        self.enabled = capture is not None
        self.live = mode == "live"
        self.recorded_requests = 0
        self.tokens = {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0}
        self.times: dict[str, float | None] = {"apiMs": None, "actionMs": None, "approvalMs": None}

    def record(self, kind: str, data: Any) -> None:
        if self.recorder:
            self.recorder.record(kind, data)

    def frame(self, metadata: dict[str, Any], pixels: bytes) -> None:
        if self.recorder:
            self.recorder.frame(metadata, pixels)

    def event(self, event: Any) -> None:
        self.record("runner", event)
        if event.get("stage") != "request" or event.get("reason") == "started" or not self.live:
            return
        self.measure("apiMs", event.get("duration_ms"))
        usage = event.get("usage")
        if not isinstance(usage, dict):
            return
        tokens = cast(dict[str, Any], usage)
        if all(
            type(tokens.get(key)) is int and tokens[key] >= 0
            for key in ("input_tokens", "output_tokens", "total_tokens")
        ):
            self.recorded_requests += 1
            for source, target in (
                ("input_tokens", "inputTokens"),
                ("output_tokens", "outputTokens"),
                ("total_tokens", "totalTokens"),
            ):
                self.tokens[target] += tokens[source]

    def measure(self, stage: str, duration: Any) -> None:
        if stage in self.times and type(duration) in (int, float) and math.isfinite(duration) and duration >= 0:
            self.times[stage] = (self.times[stage] or 0) + duration

    def summary(self, requests: int) -> dict[str, Any]:
        return {
            "usage": {
                "recordedRequests": self.recorded_requests,
                "missingRequests": max(0, requests - self.recorded_requests),
                "complete": requests > 0 and requests == self.recorded_requests,
                **{key: value if self.recorded_requests else None for key, value in self.tokens.items()},
            },
            "timing": {key: round(value) if value is not None else None for key, value in self.times.items()},
            "capture": {
                "enabled": self.enabled,
                "status": self.recorder.status if self.recorder else "limited" if self.enabled else "disabled",
                "omitted": self.recorder.omitted if self.recorder else 0,
            },
        }

    def close(self) -> None:
        if self.recorder:
            self.recorder.close()


class DiagnosticCapture:
    def __init__(self, secrets: Iterable[str | None] = (), capture_id: str | None = None) -> None:
        if os.name != "posix":
            raise RuntimeError("Private diagnostic capture requires POSIX owner-only filesystem permissions.")
        if capture_id is not None and not re.fullmatch(r"openai-browser-diagnostics-[A-Za-z0-9_-]{6,12}", capture_id):
            raise ValueError("Choose the capture ID printed by this demo, not a path or URL.")
        self.directory = (
            Path(tempfile.mkdtemp(prefix="openai-browser-diagnostics-"))
            if capture_id is None
            else Path(tempfile.gettempdir()) / capture_id
        )
        if capture_id is None:
            self.directory.chmod(0o700)
        info = self.directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError("The capture must be an owner-only directory created by this demo.")
        self.id = self.directory.name
        self.secrets = tuple(value for value in secrets if value)
        self.runs = max(
            (index for index in range(1, MAX_RUNS + 1) if (self.directory / f"run-{index}.jsonl").exists()), default=0
        )

    def owned_file(self, filename: Path, limit: int) -> bytes:
        with os.fdopen(os.open(filename, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW), "rb") as handle:
            info = os.fstat(handle.fileno())
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_size > limit
            ):
                raise ValueError("Capture file unavailable.")
            data = handle.read(limit + 1)
            if len(data) > limit:
                raise ValueError("Capture file exceeded its limit.")
            return data

    def trace(self, trace_id: str) -> dict[str, Any]:
        if trace_id not in (f"run-{index}" for index in range(1, MAX_RUNS + 1)):
            raise ValueError("Saved trace unavailable.")
        return parse_diagnostic_trace(self.owned_file(self.directory / f"{trace_id}.jsonl", MAX_BYTES))

    def traces(self) -> list[str]:
        found: list[str] = []
        for index in range(1, MAX_RUNS + 1):
            trace_id = f"run-{index}"
            try:
                self.trace(trace_id)
                found.append(trace_id)
            except (ValueError, OSError):
                # Skip captures that are invalid or no longer readable.
                continue
        return found

    def frame(self, trace_id: str, sequence: str) -> tuple[bytes, str]:
        if not re.fullmatch(r"[1-9][0-9]{0,8}", sequence):
            raise ValueError("Saved frame unavailable.")
        record = next(
            (
                item
                for item in self.trace(trace_id)["records"]
                if item["kind"] == "frame" and str(item["data"]["sequence"]) == sequence
            ),
            None,
        )
        if not record or record["data"]["mime"] not in ("image/jpeg", "image/png"):
            raise ValueError("Saved frame unavailable.")
        return self.owned_file(self.directory / f"{trace_id}-{sequence}.frame", MAX_BYTES), record["data"]["mime"]

    def start(self) -> DiagnosticRecorder | None:
        if self.runs >= MAX_RUNS:
            return None
        self.runs += 1
        return DiagnosticRecorder(self.directory / f"run-{self.runs}.jsonl", self.secrets)


class DiagnosticRecorder:
    def __init__(self, filename: Path, secrets: tuple[str, ...] = ()) -> None:
        self.filename = filename
        self.secrets = secrets
        self.status = "recording"
        self.omitted = 0
        self.bytes = 0
        self.frames = self.frame_bytes = self.omitted_frames = 0
        self.started = time.monotonic()
        self.descriptor: int | None = None
        try:
            self.descriptor = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.fchmod(self.descriptor, 0o600)
        except OSError:
            self.status = "failed"
            self.close()

    def frame(self, metadata: dict[str, Any], pixels: bytes) -> None:
        if self.descriptor is None or metadata["mime"] not in ("image/jpeg", "image/png"):
            return
        if self.frames >= 12 or len(pixels) > MAX_BYTES or self.frame_bytes + len(pixels) > 8 * MAX_BYTES:
            self.omitted_frames += 1
            return
        target = self.filename.with_name(f"{self.filename.stem}-{metadata['sequence']}.frame")
        try:
            with os.fdopen(os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as out:
                os.fchmod(out.fileno(), 0o600)
                out.write(pixels)
            if self.record("frame", metadata):
                self.frames += 1
                self.frame_bytes += len(pixels)
            else:
                target.unlink()
                self.omitted_frames += 1
        except OSError:
            self.omitted_frames += 1

    def record(self, kind: str, data: Any) -> bool:
        if self.descriptor is None:
            return False
        try:

            def redact(value: Any) -> Any:
                if isinstance(value, str):
                    for secret in self.secrets:
                        value = value.replace(secret, "[redacted]")
                    return re.sub(r"sk-[\w-]+", "[redacted]", value)
                if isinstance(value, list):
                    return [redact(item) for item in cast(list[object], value)]
                if isinstance(value, dict):
                    return {key: redact(item) for key, item in cast(dict[object, object], value).items()}
                return value

            serialized = json.dumps(
                redact(
                    {"version": 1, "kind": kind, "atMs": round((time.monotonic() - self.started) * 1000), "data": data}
                ),
                ensure_ascii=False,
                separators=(",", ":"),
            )
            line = (serialized + "\n").encode()
            if self.bytes + len(line) > (MAX_BYTES if kind == "capture" else MAX_BYTES - 512):
                self.omitted += 1
                self.status = "limited"
                return False
            offset = 0
            while offset < len(line):
                written = os.write(self.descriptor, line[offset:])
                if written == 0:
                    raise OSError("Diagnostic write did not advance.")
                offset += written
            self.bytes += len(line)
            return True
        except Exception:
            self.status = "failed"
            self.close()
            return False

    def close(self) -> None:
        if self.descriptor is not None and self.status != "failed":
            self.record(
                "capture",
                {
                    "status": "complete" if self.status == "recording" else self.status,
                    "omitted": self.omitted,
                    "frames": self.frames,
                    "omittedFrames": self.omitted_frames,
                },
            )
        if self.descriptor is not None:
            try:
                os.close(self.descriptor)
                if self.status == "recording":
                    self.status = "complete"
            except OSError:
                self.status = "failed"
            self.descriptor = None


def diagnostic_observation(observation: Any) -> str | list[str]:
    """Keep text observations only; never copy images or transport credentials."""
    if isinstance(observation, str):
        return observation
    return [part["text"] for part in observation if part.get("type") == "input_text"]


def read_diagnostic_trace(filename: Path) -> dict[str, Any]:
    """Read data only. A trace never supplies executable or replayable actions."""
    with os.fdopen(os.open(filename, os.O_RDONLY | os.O_NONBLOCK), "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise ValueError("Choose a diagnostic JSONL file no larger than 1 MiB.")
        text = handle.read(MAX_BYTES + 1)
        if len(text) > MAX_BYTES:
            raise ValueError("Diagnostic file grew beyond 1 MiB.")
    return parse_diagnostic_trace(text)


def valid_diagnostic_data(kind: object, value: object) -> bool:
    if kind == "observation":
        return isinstance(value, str) or (
            isinstance(value, list) and all(isinstance(part, str) for part in cast("list[object]", value))
        )
    if kind == "choices":
        if not isinstance(value, list):
            return False
        for item in cast("list[object]", value):
            if not isinstance(item, dict):
                return False
            choice = cast("dict[str, object]", item)
            if not (
                isinstance(choice.get("id"), str)
                and isinstance(choice.get("description"), str)
                and isinstance(choice.get("done"), bool)
            ):
                return False
        return True
    if not isinstance(value, dict):
        return False
    data = cast("dict[str, object]", value)

    def strings(*names: str) -> bool:
        return all(isinstance(data.get(name), str) for name in names)

    def counts(*names: str) -> bool:
        return all(type(data.get(name)) is int and cast(int, data[name]) >= 0 for name in names)

    if kind == "run":
        return strings("api", "mode", "taskId") or (
            strings("status", "cleanup")
            and "result" in data
            and (data["result"] is None or isinstance(data["result"], str))
        )
    if kind == "runner":
        return strings("api", "stage", "reason")
    if kind == "effect":
        return strings("member") and isinstance(data.get("state"), dict)
    if kind == "verification":
        return isinstance(data.get("verified"), bool)
    if kind == "frame":
        return (
            strings("owner", "role", "mime")
            and counts("sequence")
            and cast(int, data["sequence"]) > 0
            and data["mime"] in ("image/jpeg", "image/png")
        )
    if kind == "capture":
        return strings("status") and counts("omitted", "frames", "omittedFrames")
    return False


def parse_diagnostic_trace(text: bytes) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line:
            continue
        try:
            decoded: object = json.loads(line)
            if not isinstance(decoded, dict):
                raise ValueError("Invalid trace record.")
            record = cast(dict[str, Any], decoded)
            if (
                record.get("version") != 1
                or type(record.get("atMs")) not in (int, float)
                or not 0 <= record["atMs"] < float("inf")
                or "data" not in record
                or not valid_diagnostic_data(record.get("kind"), record["data"])
            ):
                raise ValueError("Invalid trace record.")
            records.append(record)
        except (ValueError, TypeError):
            return {"records": records, "incomplete": True}
    return {"records": records, "incomplete": not records or records[-1]["kind"] != "capture"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect private local evidence. This command never executes actions.")
    parser.add_argument("filename", type=Path)
    args = parser.parse_args()
    trace = read_diagnostic_trace(args.filename)
    print("Private local evidence: inspect page values before sharing.")
    print(json.dumps(trace, indent=2))
    raise SystemExit(2 if trace["incomplete"] else 0)
