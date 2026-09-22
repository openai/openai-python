from __future__ import annotations

import os
import sys
import subprocess
from typing import TYPE_CHECKING
from pathlib import Path

import pytest

import openai

if TYPE_CHECKING:
    from typing_extensions import assert_type

    from openai.resources import Chat, AsyncChat
    from openai.lib.streaming import AssistantEventHandler as StreamingHandler
    from openai.resources.chat import Chat as CanonicalChat, AsyncChat as CanonicalAsyncChat
    from openai.lib.streaming._assistants import (
        AssistantEventHandler as CanonicalHandler,
        AsyncAssistantEventHandler as CanonicalAsyncHandler,
    )

    assert_type(Chat, type[CanonicalChat])
    assert_type(AsyncChat, type[CanonicalAsyncChat])
    assert_type(openai.AssistantEventHandler, type[CanonicalHandler])
    assert_type(openai.AsyncAssistantEventHandler, type[CanonicalAsyncHandler])
    assert_type(StreamingHandler, type[CanonicalHandler])


def _run_python(source: str) -> None:
    # Each case needs an empty module cache, including when the suite has already
    # imported every API resource during collection.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(openai.__file__).parents[1])
    result = subprocess.run(
        [sys.executable, "-c", source],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "statement",
    [
        "import openai",
        "from openai import OpenAI, AsyncOpenAI",
        "from openai.resources import Chat",
        "from openai.lib.streaming.chat import ChatCompletionStream",
        "from openai.lib.streaming.responses import ResponseStream",
    ],
)
def test_import_does_not_load_assistants(statement: str) -> None:
    _run_python(
        statement
        + """
import sys
assert "openai.lib.streaming._assistants" not in sys.modules
assert not any(name == "openai.types.beta" or name.startswith("openai.types.beta.") for name in sys.modules)
"""
    )


def test_resource_packages_load_only_accessed_exports() -> None:
    _run_python(
        """
import importlib
import sys

resources = importlib.import_module("openai.resources")
chat = importlib.import_module("openai.resources.chat")
completions = importlib.import_module("openai.resources.chat.completions")
for module in (resources, chat, completions):
    assert set(module.__all__) <= set(dir(module))
assert "openai.resources.chat.chat" not in sys.modules
assert "openai.resources.chat.completions.completions" not in sys.modules

from openai.resources import Chat
from openai.resources.chat.chat import Chat as CanonicalChat
assert Chat is CanonicalChat
assert resources.Chat is Chat
assert "openai.resources.audio" not in sys.modules
assert "openai.resources.beta" not in sys.modules
"""
    )


def test_lazy_exports_preserve_public_import_contracts() -> None:
    _run_python(
        """
import importlib
import inspect
import pickle
import sys
import typing
import openai

resources = importlib.import_module("openai.resources")
streaming = importlib.import_module("openai.lib.streaming")
assert {"AssistantEventHandler", "AsyncAssistantEventHandler"} <= set(dir(openai))
assert set(streaming.__all__) <= set(dir(streaming))
assert set(resources.__all__) <= set(dir(resources))
assert {"chat", "beta"} <= set(dir(resources))
assert "openai.types.beta" not in sys.modules

from openai import AssistantEventHandler, AsyncAssistantEventHandler
from openai.lib.streaming._assistants import AssistantEventHandler as Canonical
assert AssistantEventHandler is Canonical
for cls in (AssistantEventHandler, AsyncAssistantEventHandler):
    assert dict(inspect.getmembers(openai))[cls.__name__] is cls
    assert pickle.loads(pickle.dumps(cls)) is cls
    for method in ("on_event", "on_run_step_delta", "on_tool_call_delta"):
        assert "return" in typing.get_type_hints(getattr(cls, method))

namespace = {}
exec("from openai.lib.streaming import *", namespace)
assert namespace["AssistantEventHandler"] is Canonical
exec("from openai.resources import *", namespace)
assert all(namespace[name] is getattr(resources, name) for name in resources.__all__)
exec("from openai import *", namespace)
assert all(namespace[name] is getattr(openai, name) for name in openai.__all__)

import openai.types as types
assert types is sys.modules["openai.types"]
assert importlib.reload(types) is types
assert importlib.reload(resources) is resources
assert resources.Chat is importlib.import_module("openai.resources.chat").Chat
assert resources.chat is importlib.import_module("openai.resources.chat")
for module in (openai, resources, streaming):
    try:
        module.definitely_not_an_export
    except AttributeError as exc:
        assert module.__name__ in str(exc)
    else:
        raise AssertionError("unknown names must raise AttributeError")
"""
    )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_first_requests_and_streams_do_not_load_assistants(asynchronous: bool) -> None:
    _run_python(
        f"asynchronous = {asynchronous!r}\n"
        + """
import asyncio
import json
import sys
import httpx2
from openai import OpenAI, AsyncOpenAI

response = {
    "id": "resp_test", "object": "response", "created_at": 0,
    "status": "completed", "model": "test-model", "output": [],
}
completion = {
    "id": "chat_test", "object": "chat.completion", "created": 0, "model": "test-model",
    "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "ok"}}],
}

def handle(request):
    body = json.loads(request.content)
    if request.url.path.endswith("/responses"):
        payload = response
        events = [
            {"type": "response.created", "sequence_number": 0, "response": dict(response, status="in_progress")},
            {"type": "response.completed", "sequence_number": 1, "response": response},
        ]
    else:
        payload = completion
        events = [{
            "id": "chat_test", "object": "chat.completion.chunk", "created": 0, "model": "test-model",
            "choices": [{"index": 0, "finish_reason": "stop", "delta": {"role": "assistant", "content": "ok"}}],
        }]
    if body.get("stream"):
        data = "".join("data: " + json.dumps(event) + "\\n\\n" for event in events) + "data: [DONE]\\n\\n"
        return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=data)
    return httpx2.Response(200, json=payload)

def assert_isolated():
    assert "openai.lib.streaming._assistants" not in sys.modules
    assert not any(name == "openai.types.beta" or name.startswith("openai.types.beta.") for name in sys.modules)

async def run_async():
    async with AsyncOpenAI(api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle))) as c:
        assert (await c.responses.create(model="test-model", input="hello")).id == "resp_test"
        assert_isolated()
        assert (await c.chat.completions.create(model="test-model", messages=[])).choices[0].message.content == "ok"
        async with c.responses.stream(model="test-model", input="hello") as stream:
            assert (await stream.get_final_response()).status == "completed"
        async with c.chat.completions.stream(model="test-model", messages=[]) as stream:
            assert (await stream.get_final_completion()).choices[0].message.content == "ok"
        assert_isolated()

if asynchronous:
    asyncio.run(run_async())
else:
    with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=httpx2.MockTransport(handle))) as c:
        assert c.responses.create(model="test-model", input="hello").id == "resp_test"
        assert_isolated()
        assert c.chat.completions.create(model="test-model", messages=[]).choices[0].message.content == "ok"
        with c.responses.stream(model="test-model", input="hello") as stream:
            assert stream.get_final_response().status == "completed"
        with c.chat.completions.stream(model="test-model", messages=[]) as stream:
            assert stream.get_final_completion().choices[0].message.content == "ok"
        assert_isolated()
"""
    )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_concurrent_first_access_preserves_class_identity(asynchronous: bool) -> None:
    _run_python(
        f"asynchronous = {asynchronous!r}\n"
        + """
import concurrent.futures
import importlib
import threading
import openai
resources = importlib.import_module("openai.resources")
responses = importlib.import_module("openai.resources.responses")
prefix = "Async" if asynchronous else ""
exports = [(resources, prefix + "Chat"), (responses, prefix + "Responses"), (openai, prefix + "AssistantEventHandler")]
barrier = threading.Barrier(2 * len(exports))

def resolve(module, name):
    barrier.wait(timeout=30)
    return getattr(module, name)

with concurrent.futures.ThreadPoolExecutor(max_workers=2 * len(exports)) as executor:
    futures = [executor.submit(resolve, module, name) for module, name in exports * 2]
    values = [future.result(timeout=45) for future in futures]
for index, (module, name) in enumerate(exports):
    assert values[index] is values[index + len(exports)], name
    assert values[index] is getattr(module, name)
"""
    )
