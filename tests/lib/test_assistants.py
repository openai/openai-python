from __future__ import annotations

from typing import Any

import pytest

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai._models import construct_type
from openai.types.beta import BaseTool
from openai.types.beta.threads import (
    Text,
    Message,
    TextDelta,
    MessageDelta,
    BaseAnnotation,
    BaseDeltaBlock,
    BaseContentBlock,
    BaseDeltaAnnotation,
)
from openai.types.beta.assistant import Assistant
from openai.types.beta.threads.runs import RunStep, BaseToolCall, RunStepDelta, BaseToolCallDelta


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,
        checking_client.beta.threads.create_and_run_poll,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,
        checking_client.beta.threads.create_and_run_stream,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,
        checking_client.beta.threads.runs.stream,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,
        checking_client.beta.threads.runs.create_and_poll,
        exclude_params={"stream"},
    )


def test_assistants_unknown_create_tool_response() -> None:
    response: dict[str, Any] = {
        "id": "asst_xxx",
        "created_at": 1722882650,
        "description": None,
        "instructions": "",
        "metadata": {},
        "model": "gpt-4",
        "name": "xxx",
        "object": "assistant",
        "tools": [{"type": "tool_unknown", "unknown": {}}],
        "response_format": "auto",
        "temperature": 1.0,
        "tool_resources": {},
        "top_p": 1.0,
    }
    assistant = construct_type(type_=Assistant, value=response)
    assert isinstance(assistant, Assistant)
    assert isinstance(assistant.tools[0], BaseTool)
    assert assistant.tools[0].type == "tool_unknown"  # type: ignore[comparison-overlap]
    a = assistant.model_dump()  # type: ignore[unreachable]
    assert a["tools"][0]["type"] == "tool_unknown"
    assert a["tools"][0]["unknown"] == {}


def test_assistants_unknown_annotation_response() -> None:
    response: dict[str, Any] = {
        "annotations": [
            {
                "text": "text",
                "type": "unknown_citation",
                "start_index": 150,
                "end_index": 162,
                "unknown_citation": {},
            },
            {
                "text": "text",
                "type": "unknown_citation",
                "start_index": 150,
                "end_index": 162,
                "unknown_citation": {},
            },
        ],
        "value": "",
    }
    text = construct_type(type_=Text, value=response)
    assert isinstance(text, Text)
    assert isinstance(text.annotations[0], BaseAnnotation)
    assert text.annotations[0].type == "unknown_citation"  # type: ignore[comparison-overlap]
    t = text.model_dump()  # type: ignore[unreachable]
    assert t["annotations"][0]["type"] == "unknown_citation"


def test_assistants_unknown_annotation_delta_response() -> None:
    response: dict[str, Any] = {
        "annotations": [
            {
                "index": 0,
                "type": "unknown_citation",
                "start_index": 150,
                "end_index": 162,
                "unknown_citation": {},
            },
            {
                "index": 1,
                "type": "unknown_citation",
                "start_index": 150,
                "end_index": 162,
                "unknown_citation": {},
            },
        ],
        "value": "",
    }
    text_delta = construct_type(type_=TextDelta, value=response)
    assert isinstance(text_delta, TextDelta)
    assert text_delta.annotations
    assert isinstance(text_delta.annotations[0], BaseDeltaAnnotation)
    assert text_delta.annotations[0].type == "unknown_citation"  # type: ignore[comparison-overlap]
    td = text_delta.model_dump()  # type: ignore[unreachable]
    assert td["annotations"][0]["type"] == "unknown_citation"


def test_assistants_unknown_message_content_response() -> None:
    response: dict[str, Any] = {
        "id": "msg_xxx",
        "assistant_id": None,
        "attachments": [],
        "content": [{"unknown_content": {}, "type": "unknown_content"}],
        "created_at": 1722885796,
        "metadata": {},
        "object": "thread.message",
        "role": "user",
        "run_id": None,
        "thread_id": "thread_xxx",
    }
    message = construct_type(type_=Message, value=response)
    assert isinstance(message, Message)
    assert isinstance(message.content[0], BaseContentBlock)
    assert message.content[0].type == "unknown_content"  # type: ignore[comparison-overlap]
    msg = message.model_dump()  # type: ignore[unreachable]
    assert msg["content"][0]["type"] == "unknown_content"


def test_assistants_unknown_message_content_delta_response() -> None:
    response: dict[str, Any] = {
        "content": [{"index": 1, "unknown_content": {}, "type": "unknown_content"}],
        "role": "user",
    }
    message_delta = construct_type(type_=MessageDelta, value=response)
    assert isinstance(message_delta, MessageDelta)
    assert message_delta.content
    assert isinstance(message_delta.content[0], BaseDeltaBlock)
    assert message_delta.content[0].type == "unknown_content"  # type: ignore[comparison-overlap]
    md = message_delta.model_dump()  # type: ignore[unreachable]
    assert md["content"][0]["type"] == "unknown_content"


def test_assistants_unknown_tool_call_response() -> None:
    response: dict[str, Any] = {
        "id": "step_xxx",
        "assistant_id": "asst_xxx",
        "cancelled_at": None,
        "completed_at": None,
        "created_at": 1722644003,
        "failed_at": None,
        "last_error": None,
        "object": "thread.run.step",
        "run_id": "run_xxx",
        "status": "in_progress",
        "step_details": {
            "tool_calls": [{"type": "tool_unknown", "id": "call_xxx", "unknown": {}}],
            "type": "tool_calls",
        },
        "thread_id": "thread_xxx",
        "type": "tool_calls",
        "usage": None,
        "expires_at": 1722644600,
    }
    run_step = construct_type(type_=RunStep, value=response)
    assert isinstance(run_step, RunStep)
    assert run_step.step_details
    assert run_step.step_details.type == "tool_calls"
    assert run_step.step_details.tool_calls
    assert isinstance(run_step.step_details.tool_calls[0], BaseToolCall)
    assert run_step.step_details.tool_calls[0].type == "tool_unknown"  # type: ignore[comparison-overlap]
    rs = run_step.model_dump()  # type: ignore[unreachable]
    assert rs["step_details"]["tool_calls"][0]["type"] == "tool_unknown"


def test_assistants_unknown_tool_call_delta_response() -> None:
    response: dict[str, Any] = {
        "step_details": {
            "tool_calls": [{"index": 0, "type": "tool_unknown", "id": "call_xxx", "unknown": {}}],
            "type": "tool_calls",
        },
    }
    run_step_delta = construct_type(type_=RunStepDelta, value=response)
    assert isinstance(run_step_delta, RunStepDelta)
    assert run_step_delta.step_details
    assert run_step_delta.step_details.type == "tool_calls"
    assert run_step_delta.step_details.tool_calls
    assert isinstance(run_step_delta.step_details.tool_calls[0], BaseToolCallDelta)
    assert run_step_delta.step_details.tool_calls[0].type == "tool_unknown"  # type: ignore[comparison-overlap]
    rsd = run_step_delta.model_dump()  # type: ignore[unreachable]
    assert rsd["step_details"]["tool_calls"][0]["type"] == "tool_unknown"
