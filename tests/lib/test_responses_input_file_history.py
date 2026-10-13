from __future__ import annotations

from typing import Any, cast

import pytest

from openai.lib.responses_tool_runner import ResponsesToolCheckpoint
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

from .test_responses_tool_runner import FINAL, PARAMS, run


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("file_data", 42),
        ("file_url", 42),
        ("filename", 42),
        ("file_id", 42),
        ("file_data", None),
        ("file_url", None),
        ("filename", None),
        ("detail", None),
        ("detail", "original"),
        ("prompt_cache_breakpoint", None),
        ("prompt_cache_breakpoint", {}),
        ("prompt_cache_breakpoint", {"mode": "other"}),
    ],
)
async def test_file_replay_refuses_raw_invalid_native_fields_before_boundary(
    lane: str, field: str, value: object
) -> None:
    records: list[ResponsesToolCheckpoint] = []
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    file: dict[str, object] = {"type": "input_file", field: value}
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "input": [{"role": "user", "content": [file]}]})
    with pytest.raises(ValueError):
        await run(lane, None, [FINAL], requests, params=params, save=records.append, effects=effects)
    assert records == [] and requests == [] and effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "file",
    [
        {"type": "input_file"},
        {"type": "input_file", "file_id": None},
        {
            "type": "input_file",
            "file_data": "",
            "file_url": "fixture-source",
            "filename": "fixture.txt",
            "file_id": "f",
        },
        {
            "type": "input_file",
            "detail": "low",
            "file_id": "",
            "prompt_cache_breakpoint": {"mode": "explicit", "caller_extension": {"kept": True}},
            "extension": [1, "kept"],
        },
    ],
)
async def test_file_replay_retains_native_optional_fields_and_extensions(lane: str, file: dict[str, object]) -> None:
    records: list[ResponsesToolCheckpoint] = []
    requests: list[dict[str, Any]] = []
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "input": [{"role": "user", "content": [file]}]})
    final = await run(lane, None, [FINAL], requests, params=params, save=records.append)
    assert final.id == "resp_final"
    assert requests[0]["input"] == [{"role": "user", "content": [file]}]
    boundary = next(record for record in records if record["phase"] == "boundary")
    assert boundary["history"] == [{"role": "user", "content": [file]}]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "message",
    [
        {"role": "user", "content": 42},
        {"role": "user", "content": [42]},
        {"role": "user", "content": [None]},
        {"role": "user", "content": ["hello"]},
        {"role": "other", "content": "hello"},
        {"content": "hello"},
        {"role": "assistant", "content": "old output", "phase": "unsupported"},
        {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "input_text", "text": "old output"}],
            "phase": "unsupported",
        },
        {"type": "message", "role": "user", "content": "plain text", "phase": 42},
        {"role": "user", "content": "plain text", "phase": 42},
        {"role": "assistant", "content": [{"type": "input_text", "text": "old output"}], "phase": "unsupported"},
        {"role": "user", "content": [{"type": "input_text", "text": 42}]},
        {"role": "user", "content": [{"type": "input_text"}]},
        {"role": "user", "content": [{"type": "input_text", "text": "", "prompt_cache_breakpoint": None}]},
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "", "prompt_cache_breakpoint": dict[str, object]()}],
        },
        {"role": "user", "content": [{"type": "input_image"}]},
        {"role": "user", "content": [{"type": "input_image", "detail": 42}]},
        {"role": "user", "content": [{"type": "input_image", "detail": "auto", "image_url": 42}]},
        {"role": "user", "content": [{"type": "input_image", "detail": "original", "file_id": 42}]},
        {"role": "user", "content": [{"type": "input_image", "detail": "low", "prompt_cache_breakpoint": None}]},
        {
            "role": "user",
            "content": [{"type": "input_image", "detail": "high", "prompt_cache_breakpoint": {"mode": "later"}}],
        },
    ],
)
async def test_native_input_message_raw_fields_cannot_change_during_replay(
    lane: str, message: dict[str, object]
) -> None:
    records: list[ResponsesToolCheckpoint] = []
    requests: list[dict[str, Any]] = []
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "input": [message]})
    with pytest.raises(ValueError):
        await run(lane, None, [FINAL], requests, params=params, save=records.append)
    assert records == [] and requests == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "message",
    [
        {"role": "assistant", "content": "Earlier instruction"},
        {"role": "assistant", "content": "old output", "phase": None},
        {"type": "message", "role": "assistant", "content": "old output", "phase": "commentary"},
        {"role": "assistant", "content": [{"type": "input_text", "text": ""}], "phase": "final_answer"},
        {"role": "user", "content": "plain text", "phase": None},
        {"role": "system", "content": [{"type": "input_text", "text": "instruction"}], "phase": "extension"},
        {
            "type": "message",
            "role": "developer",
            "content": [{"type": "input_text", "text": "instruction"}],
            "phase": {"opaque": True},
        },
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "", "prompt_cache_breakpoint": {"mode": "explicit"}}],
        },
        {"role": "user", "content": [{"type": "input_image", "detail": "auto"}]},
        {
            "role": "user",
            "content": [{"type": "input_image", "detail": "original", "image_url": None, "file_id": None}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "detail": "high",
                    "image_url": "fixture-image",
                    "file_id": "fixture-file",
                    "prompt_cache_breakpoint": {"mode": "explicit", "extension": 2},
                    "extension": ["keep", True],
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "File and picture"},
                {"type": "input_image", "detail": "low", "file_id": "fixture-file"},
                {"type": "input_file", "detail": "high", "filename": "fixture.txt"},
            ],
        },
    ],
)
async def test_native_input_message_keeps_easy_strings_and_native_nullable_sources(
    lane: str, message: dict[str, object]
) -> None:
    records: list[ResponsesToolCheckpoint] = []
    requests: list[dict[str, Any]] = []
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "input": [message]})
    final = await run(lane, None, [FINAL], requests, params=params, save=records.append)
    assert final.id == "resp_final" and requests[0]["input"] == [message]
    boundary = next(record for record in records if record["phase"] == "boundary")
    assert boundary["history"] == [message]
