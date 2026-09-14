from __future__ import annotations

import json
import argparse
import datetime
from typing import Any, Callable

import pyperf
import pydantic

from openai._compat import model_dump
from openai._utils._json import openapi_dumps


class Message(pydantic.BaseModel):
    role: str
    content: str
    metadata: dict[str, Any]


class StdlibEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, pydantic.BaseModel):
            return model_dump(obj, exclude_unset=True, mode="json", by_alias=True)
        return super().default(obj)


def stdlib_openapi_dumps(obj: Any) -> bytes:
    """The pre-orjson openapi_dumps implementation used as the benchmark baseline."""
    return json.dumps(
        obj,
        cls=StdlibEncoder,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def payload(target_size_bytes: int) -> dict[str, Any]:
    content = "x" * 700
    messages: list[Message] = []

    while len(messages) * len(content) < target_size_bytes:
        messages.append(
            Message(
                role="user",
                content=content,
                metadata={"created_at": datetime.datetime(2026, 9, 14, 12, 0), "index": len(messages)},
            )
        )

    return {"model": "gpt-5", "messages": messages, "temperature": 0.7}


def serializer(value: str) -> Callable[[Any], bytes]:
    if value == "stdlib":
        return stdlib_openapi_dumps
    if value == "orjson":
        return openapi_dumps
    raise ValueError(f"Unknown serializer: {value}")


def add_cmdline_args(command: list[str], args: argparse.Namespace) -> None:
    """Pass the selected serializer to pyperf's isolated worker processes."""
    command.append(f"--serializer={args.serializer}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serializer", choices=("stdlib", "orjson"), required=True)
    runner = pyperf.Runner(_argparser=parser, add_cmdline_args=add_cmdline_args)
    selected_serializer = serializer(runner.parse_args().serializer)

    for name, target_size_bytes in (("18kb", 16_000), ("289kb", 256_000), ("1.13mb", 1_000_000)):
        runner.bench_func(f"openapi_dumps[{name}]", selected_serializer, payload(target_size_bytes))


if __name__ == "__main__":
    main()
