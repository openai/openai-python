from __future__ import annotations

import json

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.types.beta.threads.runs import RunStep

from ..conftest import base_url


@pytest.fixture(params=[False, True], ids=["empty", "snapshot-without-index"])
def assistant_tool_stream(request: pytest.FixtureRequest, respx2_mock: MockRouter) -> None:
    tool = {"id": "call_files", "type": "function", "function": {"name": "list_files", "arguments": ""}}
    step = {
        "id": "step_test",
        "object": "thread.run.step",
        "assistant_id": "asst_test",
        "thread_id": "thread_test",
        "run_id": "run_test",
        "created_at": 0,
        "status": "in_progress",
        "type": "tool_calls",
        "step_details": {"type": "tool_calls", "tool_calls": [tool] if request.param else []},
    }
    fragments = [
        {"index": 0, "type": "function", "function": {"arguments": '{"'}},
        {"index": 0, "type": "function", "function": {"arguments": 'path"'}},
    ]
    if not request.param:
        fragments.insert(0, {"index": 0, **tool})
    events = [
        ("thread.run.step.created", step),
        (
            "thread.run.step.delta",
            {
                "id": "step_test",
                "object": "thread.run.step.delta",
                "delta": {
                    "step_details": {"type": "tool_calls", "tool_calls": fragments},
                },
            },
        ),
        (
            "thread.run.step.delta",
            {
                "id": "step_test",
                "object": "thread.run.step.delta",
                "delta": {
                    "step_details": {
                        "type": "tool_calls",
                        "tool_calls": [
                            {"index": 0, "type": "function", "function": {"arguments": ': "."}'}},
                        ],
                    },
                },
            },
        ),
    ]
    body = "".join(f"event: {name}\ndata: {json.dumps(data)}\n\n" for name, data in events) + "data: [DONE]\n\n"
    respx2_mock.post("/threads/thread_test/runs").mock(
        return_value=httpx2.Response(200, text=body, headers={"content-type": "text/event-stream"})
    )


def assert_tool_arguments(steps: list[RunStep]) -> None:
    assert len(steps) == 1
    details = steps[0].step_details
    assert details.type == "tool_calls"
    assert len(details.tool_calls) == 1
    tool = details.tool_calls[0]
    assert tool.type == "function"
    assert tool.id == "call_files"
    assert tool.function.name == "list_files"
    assert json.loads(tool.function.arguments) == {"path": "."}


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.usefixtures("assistant_tool_stream")
@pytest.mark.filterwarnings("ignore:The Assistants API is deprecated:DeprecationWarning")
def test_assistant_tool_call_deltas(client: OpenAI) -> None:
    with client.beta.threads.runs.stream(thread_id="thread_test", assistant_id="asst_test") as stream:  # pyright: ignore[reportDeprecated]
        assert_tool_arguments(stream.get_final_run_steps())


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.usefixtures("assistant_tool_stream")
@pytest.mark.filterwarnings("ignore:The Assistants API is deprecated:DeprecationWarning")
async def test_async_assistant_tool_call_deltas(async_client: AsyncOpenAI) -> None:
    async with async_client.beta.threads.runs.stream(thread_id="thread_test", assistant_id="asst_test") as stream:  # pyright: ignore[reportDeprecated]
        assert_tool_arguments(await stream.get_final_run_steps())
