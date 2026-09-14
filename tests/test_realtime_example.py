from __future__ import annotations

import ast
import asyncio
import importlib
from types import SimpleNamespace
from typing import Any
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from openai.types.realtime.session_created_event import SessionCreatedEvent

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/realtime/push_to_talk_app.py"


def test_realtime_example_sdk_imports() -> None:
    for node in ast.parse(EXAMPLE.read_text()).body:
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("openai"):
            module = importlib.import_module(node.module)
            for alias in node.names:
                assert hasattr(module, alias.name)


@pytest.mark.parametrize(
    ("audio", "manual"),
    [
        (None, False),
        ({}, False),
        ({"input": {"turn_detection": {"type": "server_vad"}}}, False),
        ({"input": {"turn_detection": {"type": "semantic_vad"}}}, False),
        ({"input": {"turn_detection": None}}, True),
    ],
    ids=["no-audio", "no-input", "server-vad", "semantic-vad", "manual"],
)
async def test_realtime_example_recording_toggle(audio: object, manual: bool) -> None:
    # Exercise the real handler without requiring UI packages or audio hardware in SDK CI.
    tree = ast.parse(EXAMPLE.read_text())
    app = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RealtimeApp")
    handler = next(node for node in app.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "on_key")
    module = ast.Module(body=[handler], type_ignores=[])
    namespace: dict[str, Any] = {"AudioStatusIndicator": object()}
    exec(compile(module, str(EXAMPLE), "exec"), namespace)

    indicator = SimpleNamespace(is_recording=False)
    connection = SimpleNamespace(
        input_audio_buffer=SimpleNamespace(commit=AsyncMock()),
        response=SimpleNamespace(create=AsyncMock()),
    )
    session = SessionCreatedEvent.model_validate(
        {"type": "session.created", "event_id": "event-test", "session": {"type": "realtime", "audio": audio}}
    ).session
    controller = SimpleNamespace(
        session=session,
        should_send_audio=asyncio.Event(),
        query_one=lambda _: indicator,
        _get_connection=AsyncMock(return_value=connection),
    )
    event = SimpleNamespace(key="k")
    await namespace["on_key"](controller, event)
    assert indicator.is_recording
    assert controller.should_send_audio.is_set()
    connection.input_audio_buffer.commit.assert_not_awaited()
    connection.response.create.assert_not_awaited()

    await namespace["on_key"](controller, event)
    assert not indicator.is_recording
    assert not controller.should_send_audio.is_set()
    assert connection.input_audio_buffer.commit.await_count == int(manual)
    assert connection.response.create.await_count == int(manual)
