"""Opt-in Vertex acceptance from this checkout or an installed wheel."""

from __future__ import annotations

import os
import json
import asyncio
import logging
import subprocess
from typing import Callable, cast
from datetime import datetime, timezone
from urllib.parse import urlsplit

import pytest

from openai import OpenAI, AsyncOpenAI, APIStatusError, __version__
from openai.providers import vertex
from openai.types.responses import ResponseInputParam


@pytest.mark.skipif(os.environ.get("OPENAI_VERTEX_LIVE") != "1", reason="Vertex live acceptance is opt-in")
def test_vertex_live_acceptance() -> None:
    model = os.environ["OPENAI_VERTEX_MODEL"]
    result_path = os.environ["OPENAI_VERTEX_REPORT"]
    mode = os.environ.get("OPENAI_VERTEX_BUILD_MODE", "source")
    revision = os.environ.get("OPENAI_VERTEX_REVISION")
    if mode == "installed" and not revision:
        raise ValueError("Installed mode requires OPENAI_VERTEX_REVISION from the checkout used to build the wheel.")
    revision = revision or subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    provider = vertex(
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
        base_url=os.environ.get("OPENAI_VERTEX_BASE_URL"),
    )
    results: dict[str, dict[str, str | int]] = {}

    def record(name: str, operation: Callable[[], None]) -> None:
        try:
            operation()
            results[name] = {"status": "pass"}
        except APIStatusError as exc:
            # HTTP status distinguishes access/service failures. Never write the body or message.
            results[name] = {"status": "fail", "exception": type(exc).__name__, "http_status": exc.status_code}
        except Exception as exc:
            results[name] = {"status": "fail", "exception": type(exc).__name__}

    # Test runs must not inherit developer debug settings. Restore the logger for other tests.
    sdk_log = logging.getLogger("openai")
    prior_level = sdk_log.level
    sdk_log.setLevel(logging.CRITICAL)
    try:
        with OpenAI(provider=provider, timeout=60.0, max_retries=0) as client:
            root = urlsplit(str(client.base_url))

            def create() -> None:
                response = client.responses.create(model=model, input="Say hello.", store=False)
                assert response.id and response.status == "completed" and response.output_text

            def stream() -> None:
                completed = False
                with client.responses.create(model=model, input="Say hello.", stream=True, store=False) as events:
                    for event in events:
                        assert event.type not in ("response.failed", "response.incomplete", "error")
                        if event.type == "response.completed":
                            completed = bool(event.response.id and event.response.status == "completed")
                assert completed

            def tools() -> None:
                response = client.responses.create(
                    model=model,
                    input="Use the test tool.",
                    tools=[
                        {
                            "type": "function",
                            "name": "test_tool",
                            "parameters": {"type": "object", "properties": {}},
                            "strict": None,
                        }
                    ],
                    tool_choice={"type": "function", "name": "test_tool"},
                    store=False,
                )
                assert response.status == "completed"
                call = next(item for item in response.output if item.type == "function_call")
                result = client.responses.create(
                    model=model,
                    input=cast(
                        ResponseInputParam,
                        [
                            *[item.to_dict() for item in response.output],
                            {"type": "function_call_output", "call_id": call.call_id, "output": "ok"},
                        ],
                    ),
                    store=False,
                )
                assert result.id and result.status == "completed" and result.output

            def stateful() -> None:
                response = client.responses.create(model=model, input="Remember 42.", store=True)
                try:
                    assert response.id and response.status == "completed"
                    assert client.responses.retrieve(response.id).id == response.id
                    followup = client.responses.create(
                        model=model, previous_response_id=response.id, input="What number did I give you?", store=False
                    )
                    assert followup.id and followup.status == "completed" and followup.output
                finally:
                    client.responses.delete(response.id)

            def compact() -> None:
                compacted = client.responses.compact(model=model, input="Say hello.")
                assert compacted.id and compacted.output

            async def async_calls() -> None:
                async with AsyncOpenAI(provider=provider, timeout=60.0, max_retries=0) as async_client:
                    response = await async_client.responses.create(model=model, input="Say hello.", store=False)
                    assert response.id and response.status == "completed" and response.output_text
                    completed = False
                    events = await async_client.responses.create(
                        model=model, input="Say hello.", store=False, stream=True
                    )
                    async with events:
                        async for event in events:
                            assert event.type not in ("response.failed", "response.incomplete", "error")
                            if event.type == "response.completed":
                                completed = bool(event.response.id and event.response.status == "completed")
                    assert completed

            record("create_nonstored", create)
            record("stream_completion", stream)
            record("function_tools_roundtrip", tools)
            record("create_retrieve_previous_delete", stateful)
            record("compact", compact)
            record("async_create_and_stream", lambda: asyncio.run(async_calls()))
    finally:
        sdk_log.setLevel(prior_level)

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "revision": revision,
        "build_mode": mode,
        "package_version": __version__,
        "endpoint_origin": f"{root.scheme}://{root.netloc}",
        "model": model,
        "results": results,
    }
    with open(result_path, "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
    assert all(result["status"] == "pass" for result in results.values()), results


if __name__ == "__main__":
    if os.environ.get("OPENAI_VERTEX_LIVE") == "1":
        try:
            test_vertex_live_acceptance()
        except Exception as exc:
            # No traceback or exception message: either could contain request/credential data.
            print(f"Vertex acceptance failed: {type(exc).__name__}; consult the report.")
            raise SystemExit(1) from None
    else:
        print("Vertex live acceptance skipped (OPENAI_VERTEX_LIVE is not 1).")
