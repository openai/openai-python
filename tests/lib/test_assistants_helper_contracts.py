from __future__ import annotations

import json
import inspect
from typing import Any
from unittest import mock

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._types import omit
from openai.lib.streaming import AssistantEventHandler, AsyncAssistantEventHandler

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.mark.parametrize("async_", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("terminal", ["requires_action", "cancelled", "completed", "failed", "expired", "incomplete"])
@pytest.mark.parametrize(
    ("interval", "server_headers", "expected_sleep"),
    [(omit, {}, 1.0), (omit, {"openai-poll-after-ms": "125"}, 0.125), (275, {"openai-poll-after-ms": "125"}, 0.275)],
    ids=["fallback", "server", "explicit"],
)
async def test_run_poll_http_options_and_terminal_states(
    async_: bool, terminal: str, interval: Any, server_headers: dict[str, str], expected_sleep: float
) -> None:
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            200,
            headers=server_headers,
            json={
                "id": "run-synthetic",
                "object": "thread.run",
                "status": "in_progress" if len(requests) == 1 else terminal,
            },
        )

    transport = httpx2.MockTransport(respond)
    client: Any = (
        AsyncOpenAI(api_key="synthetic-key", http_client=httpx2.AsyncClient(transport=transport, trust_env=False))
        if async_
        else OpenAI(api_key="synthetic-key", http_client=httpx2.Client(transport=transport, trust_env=False))
    )
    runs = client.beta.threads.runs
    with mock.patch.object(runs, "_sleep") as sleep:
        result = runs.poll(
            "run-synthetic",
            "thread-synthetic",
            {"OpenAI-Beta": "caller-beta", "X-Stainless-Poll-Helper": "caller"},
            {"probe": "yes"},
            {"probe": "body"},
            4.5,
            interval,
        )
        if inspect.isawaitable(result):
            result = await result
        assert result.status == terminal
        sleep.assert_called_once_with(expected_sleep)
    assert len(requests) == 2
    for request in requests:
        assert request.url.path == "/v1/threads/thread-synthetic/runs/run-synthetic"
        assert request.url.params["probe"] == "yes"
        assert request.headers["OpenAI-Beta"] == "caller-beta"
        assert request.headers["X-Stainless-Poll-Helper"] == "caller"
        assert request.extensions["timeout"]["read"] == 4.5
        assert request.content == b""
        if interval is not omit:
            assert request.headers["X-Stainless-Custom-Poll-Interval"] == "275"
    closed = client.close()
    if inspect.isawaitable(closed):
        await closed


@pytest.mark.parametrize("async_", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("family", ["runs", "threads", "submit"])
async def test_assistant_stream_factory_preserves_request_and_cleanup(async_: bool, family: str) -> None:
    requests: list[httpx2.Request] = []
    responses: list[httpx2.Response] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        response = httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=b"data: [DONE]\n\n")
        responses.append(response)
        return response

    transport = httpx2.MockTransport(respond)
    client: Any = (
        AsyncOpenAI(api_key="synthetic-key", http_client=httpx2.AsyncClient(transport=transport, trust_env=False))
        if async_
        else OpenAI(api_key="synthetic-key", http_client=httpx2.Client(transport=transport, trust_env=False))
    )
    handler: Any = AsyncAssistantEventHandler() if async_ else AssistantEventHandler()
    kwargs: dict[str, Any] = {
        "event_handler": handler,
        "extra_headers": {"OpenAI-Beta": "caller-beta", "X-Stainless-Stream-Helper": "caller"},
        "extra_query": {"probe": "yes"},
        "extra_body": {"probe": "body"},
        "timeout": 3.5,
    }
    if family == "runs":
        manager = client.beta.threads.runs.stream(thread_id="thread-synthetic", assistant_id="asst-synthetic", **kwargs)
        expected_path = "/v1/threads/thread-synthetic/runs"
    elif family == "threads":
        manager = client.beta.threads.create_and_run_stream(assistant_id="asst-synthetic", **kwargs)
        expected_path = "/v1/threads/runs"
    else:
        manager = client.beta.threads.runs.submit_tool_outputs_stream(
            run_id="run-synthetic",
            thread_id="thread-synthetic",
            tool_outputs=[{"tool_call_id": "call-synthetic", "output": "ok"}],
            **kwargs,
        )
        expected_path = "/v1/threads/thread-synthetic/runs/run-synthetic/submit_tool_outputs"
    assert not inspect.isawaitable(manager)
    assert not requests
    if async_:
        async with manager as stream:
            assert stream is handler
            await stream.until_done()
    else:
        with manager as stream:
            assert stream is handler
            stream.until_done()
    assert len(requests) == 1
    request = requests[0]
    assert request.url.path == expected_path
    assert request.url.params["probe"] == "yes"
    assert request.headers["OpenAI-Beta"] == "caller-beta"
    assert request.headers["X-Stainless-Stream-Helper"] == "caller"
    assert request.headers["X-Stainless-Custom-Event-Handler"] == "true"
    assert request.extensions["timeout"]["read"] == 3.5
    body = json.loads(request.content)
    assert body["stream"] is True
    assert body["probe"] == "body"
    assert responses[0].is_closed
    closed = client.close()
    if inspect.isawaitable(closed):
        await closed


@pytest.mark.parametrize("async_", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("method", ["create", "submit_tool_outputs", "create_and_run"])
async def test_released_deprecation_wrapper_count(async_: bool, method: str) -> None:
    import warnings

    transport = httpx2.MockTransport(lambda _request: httpx2.Response(500))
    client: Any = (
        AsyncOpenAI(api_key="synthetic-key", http_client=httpx2.AsyncClient(transport=transport, trust_env=False))
        if async_
        else OpenAI(api_key="synthetic-key", http_client=httpx2.Client(transport=transport, trust_env=False))
    )
    resource = client.beta.threads if method == "create_and_run" else client.beta.threads.runs
    kwargs: dict[str, Any] = {"assistant_id": "asst-synthetic"}
    if method != "create_and_run":
        kwargs["thread_id"] = "thread-synthetic"
    if method == "submit_tool_outputs":
        kwargs = {"thread_id": "thread-synthetic", "run_id": "run-synthetic", "tool_outputs": []}
    with mock.patch.object(resource, "_post", return_value=None), warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", DeprecationWarning)
        result = getattr(resource, method)(**kwargs)
        if inspect.isawaitable(result):
            await result
    assert len(captured) == (1 if method == "create" and not async_ else 2)
    assert all(str(w.message) == "The Assistants API is deprecated in favor of the Responses API" for w in captured)
    closed = client.close()
    if inspect.isawaitable(closed):
        await closed
