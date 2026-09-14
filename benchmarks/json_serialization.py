from __future__ import annotations

import json
import argparse
import datetime
from typing import Any, Callable

import pyperf
import pydantic

import openai._base_client as base_client
from openai import OpenAI
from openai._compat import model_dump
from openai._models import FinalRequestOptions
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
    ).encode("utf-8")


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
    command.append(f"--scope={args.scope}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serializer", choices=("stdlib", "orjson"), required=True)
    parser.add_argument("--scope", choices=("request-preparation", "serialization"), default="serialization")
    runner = pyperf.Runner(_argparser=parser, add_cmdline_args=add_cmdline_args)
    args = runner.parse_args()
    selected_serializer = serializer(args.serializer)

    payloads = (
        (835, 500),
        (3_983, 3_000),
        (18_162, 16_000),
        (63_078, 56_000),
        (288_712, 256_000),
        (1_127_848, 1_000_000),
    )
    if args.scope == "serialization":
        for encoded_payload_bytes, target_content_bytes in payloads:
            benchmark_payload = payload(target_content_bytes)
            assert len(stdlib_openapi_dumps(benchmark_payload)) == encoded_payload_bytes
            runner.bench_func(f"openapi_dumps[{encoded_payload_bytes}b]", selected_serializer, benchmark_payload)
        return

    client = OpenAI(api_key="benchmark", base_url="https://example.invalid/v1")
    base_client.openapi_dumps = selected_serializer
    try:
        for encoded_payload_bytes, target_content_bytes in payloads:
            benchmark_payload = payload(target_content_bytes)
            assert len(stdlib_openapi_dumps(benchmark_payload)) == encoded_payload_bytes
            options = FinalRequestOptions(method="post", url="/responses", json_data=benchmark_payload)
            runner.bench_func(f"build_request[{encoded_payload_bytes}b]", client._build_request, options)
    finally:
        client.close()


if __name__ == "__main__":
    main()
