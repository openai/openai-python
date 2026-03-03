from __future__ import annotations

from typing_extensions import TypeVar

import httpx2
import pytest
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai._types import omit
from openai._utils import assert_signatures_in_sync
from openai._models import construct_type_unchecked
from openai.types.responses import Response
from openai.lib._parsing._responses import parse_response

from ...conftest import base_url
from ..snapshots import make_snapshot_request

_T = TypeVar("_T")

# all the snapshots in this file are auto-generated from the live API
#
# you can update them with
#
# `OPENAI_LIVE=1 pytest --inline-snapshot=fix -p no:xdist -o addopts=""`


def _response_payload(output: list[dict[str, object]]) -> dict[str, object]:
    return {
        "id": "resp_test",
        "created_at": 1754925900,
        "model": "gpt-4o-mini",
        "object": "response",
        "output": output,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
    }


def _tool_output_items() -> list[dict[str, object]]:
    return [
        {
            "id": "ci_001",
            "type": "code_interpreter_call",
            "code": "print('calculated')",
            "container_id": "cntr_001",
            "outputs": [{"type": "logs", "logs": "calculated\n"}],
            "status": "completed",
        },
        {
            "id": "shell_001",
            "type": "shell_call_output",
            "call_id": "call_001",
            "output": [
                {
                    "stdout": "file1.txt\nfile2.txt\n",
                    "stderr": "",
                    "outcome": {"type": "exit", "exit_code": 0},
                }
            ],
            "status": "completed",
        },
        {
            "id": "msg_001",
            "type": "message",
            "status": "completed",
            "content": [
                {
                    "type": "output_text",
                    "annotations": [],
                    "logprobs": [],
                    "text": "Done.",
                }
            ],
            "role": "assistant",
        },
    ]


@pytest.mark.respx2(base_url=base_url)
def test_output_text(client: OpenAI, respx2_mock: MockRouter) -> None:
    response = make_snapshot_request(
        lambda c: c.responses.create(
            model="gpt-4o-mini",
            input="What's the weather like in SF?",
        ),
        content_snapshot=snapshot(
            '{"id": "resp_689a0b2545288193953c892439b42e2800b2e36c65a1fd4b", "object": "response", "created_at": 1754925861, "status": "completed", "background": false, "error": null, "incomplete_details": null, "instructions": null, "max_output_tokens": null, "max_tool_calls": null, "model": "gpt-4o-mini-2024-07-18", "output": [{"id": "msg_689a0b2637b08193ac478e568f49e3f900b2e36c65a1fd4b", "type": "message", "status": "completed", "content": [{"type": "output_text", "annotations": [], "logprobs": [], "text": "I can\'t provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it\'s good to be prepared for variable weather!"}], "role": "assistant"}], "parallel_tool_calls": true, "previous_response_id": null, "prompt_cache_key": null, "reasoning": {"effort": null, "summary": null}, "safety_identifier": null, "service_tier": "default", "store": true, "temperature": 1.0, "text": {"format": {"type": "text"}, "verbosity": "medium"}, "tool_choice": "auto", "tools": [], "top_logprobs": 0, "top_p": 1.0, "truncation": "disabled", "usage": {"input_tokens": 14, "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}, "output_tokens": 50, "output_tokens_details": {"reasoning_tokens": 0}, "total_tokens": 64}, "user": null, "metadata": {}}'
        ),
        path="/responses",
        mock_client=client,
        respx2_mock=respx2_mock,
    )

    assert response.output_text == snapshot(
        "I can't provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it's good to be prepared for variable weather!"
    )


@pytest.mark.respx2(base_url=base_url)
def test_output_text_includes_tool_results_sync(client: OpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.post("/responses").mock(return_value=httpx2.Response(200, json=_response_payload(_tool_output_items())))

    response = client.responses.create(model="gpt-4o-mini", input="Run the tools")

    assert response.output_text == "calculated\nfile1.txt\nfile2.txt\nDone."


@pytest.mark.respx2(base_url=base_url)
async def test_output_text_includes_tool_results_async(async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.post("/responses").mock(return_value=httpx2.Response(200, json=_response_payload(_tool_output_items())))

    response = await async_client.responses.create(model="gpt-4o-mini", input="Run the tools")

    assert response.output_text == "calculated\nfile1.txt\nfile2.txt\nDone."


@pytest.mark.parametrize(
    "output",
    [
        [
            {
                "id": "ci_none",
                "type": "code_interpreter_call",
                "code": None,
                "container_id": "cntr_none",
                "outputs": None,
                "status": "completed",
            }
        ],
        [
            {
                "id": "ci_empty",
                "type": "code_interpreter_call",
                "code": None,
                "container_id": "cntr_empty",
                "outputs": [],
                "status": "completed",
            }
        ],
        [
            {
                "id": "ci_image",
                "type": "code_interpreter_call",
                "code": None,
                "container_id": "cntr_image",
                "outputs": [{"type": "image", "url": "https://example.com/plot.png"}],
                "status": "completed",
            }
        ],
        [
            {
                "id": "ci_empty_logs",
                "type": "code_interpreter_call",
                "code": None,
                "container_id": "cntr_empty_logs",
                "outputs": [{"type": "logs", "logs": ""}],
                "status": "completed",
            }
        ],
        [
            {
                "id": "shell_empty",
                "type": "shell_call_output",
                "call_id": "call_empty",
                "output": [],
                "status": "completed",
            }
        ],
        [
            {
                "id": "shell_empty_stdout",
                "type": "shell_call_output",
                "call_id": "call_empty_stdout",
                "output": [
                    {
                        "stdout": "",
                        "stderr": "warning",
                        "outcome": {"type": "exit", "exit_code": 0},
                    }
                ],
                "status": "completed",
            }
        ],
    ],
    ids=["null", "empty", "non-text", "empty-logs", "empty-shell", "empty-stdout"],
)
def test_output_text_ignores_outputs_without_text(output: list[dict[str, object]]) -> None:
    response = construct_type_unchecked(type_=Response, value=_response_payload(output))

    assert response.output_text == ""


@pytest.mark.parametrize(
    "item",
    [
        {
            "id": "prog_123",
            "call_id": "call_123",
            "code": "return 42",
            "fingerprint": "fp_123",
            "type": "program",
        },
        {
            "id": "prog_out_123",
            "call_id": "call_123",
            "result": "42",
            "status": "completed",
            "type": "program_output",
        },
    ],
)
def test_parse_response_preserves_program_items(item: dict[str, object]) -> None:
    response = construct_type_unchecked(type_=Response, value={"output": [item]})

    parsed = parse_response(text_format=omit, input_tools=omit, response=response)

    assert parsed.output[0].to_dict() == item


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.stream,
        exclude_params={"stream", "tools"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_parse_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.parse,
        exclude_params={"tools"},
    )
