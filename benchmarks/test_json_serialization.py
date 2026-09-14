from __future__ import annotations

import json
import datetime
from typing import Any, Callable

import pytest
import pydantic

from openai._compat import model_dump
from openai._utils._json import openapi_dumps


class _Message(pydantic.BaseModel):
    role: str
    content: str
    metadata: dict[str, Any]


class _StdlibEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, pydantic.BaseModel):
            return model_dump(obj, exclude_unset=True, mode="json", by_alias=True)
        return super().default(obj)


def _stdlib_openapi_dumps(obj: Any) -> bytes:
    """The pre-orjson openapi_dumps implementation used as the benchmark baseline."""
    return json.dumps(
        obj,
        cls=_StdlibEncoder,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def _payload(target_size_bytes: int) -> dict[str, Any]:
    content = "x" * 700
    messages: list[_Message] = []

    while len(messages) * len(content) < target_size_bytes:
        messages.append(
            _Message(
                role="user",
                content=content,
                metadata={"created_at": datetime.datetime(2026, 9, 14, 12, 0), "index": len(messages)},
            )
        )

    return {"model": "gpt-5", "messages": messages, "temperature": 0.7}


_PAYLOADS = (
    pytest.param(16_000, 500, id="18kb"),
    pytest.param(256_000, 50, id="289kb"),
    pytest.param(1_000_000, 10, id="1.13mb"),
)

_SERIALIZERS = (
    pytest.param("stdlib", _stdlib_openapi_dumps, id="stdlib"),
    pytest.param("orjson", openapi_dumps, id="orjson"),
)


@pytest.mark.parametrize(("target_size_bytes", "iterations"), _PAYLOADS)
@pytest.mark.parametrize(("serializer_name", "serializer"), _SERIALIZERS)
def test_openapi_dumps(
    benchmark: Any,
    target_size_bytes: int,
    iterations: int,
    serializer_name: str,
    serializer: Callable[[Any], bytes],
) -> None:
    """Measure identical payloads with the prior stdlib and proposed serializers."""
    payload = _payload(target_size_bytes)
    expected = _stdlib_openapi_dumps(payload)

    result = benchmark.pedantic(serializer, args=(payload,), rounds=30, iterations=iterations, warmup_rounds=5)

    assert result == expected, serializer_name
