from __future__ import annotations

from copy import deepcopy
from typing import Any, cast

import pytest

from openai.lib.responses_tool_runner import ResponsesToolCheckpoint
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

from .test_responses_tool_runner import FINAL, PARAMS, Driver, fn, run, resp


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


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("restoring", [False, True], ids=["input", "resume"])
@pytest.mark.parametrize(
    "case",
    [
        "duplicate-id",
        "missing-status",
        "null-status",
        "output-id",
        "output-status",
        "output-checks",
        "output-check-id",
        "output-check-code",
        "output-check-message",
        "numeric-text",
        "numeric-refusal",
        "citation-index",
        "citation-boolean",
        "logprob-bytes",
        "logprob-boolean",
    ],
)
async def test_replay_original_native_fields_before_save_or_request(lane: str, restoring: bool, case: str) -> None:
    call: dict[str, object] = {
        "id": "cu_prior",
        "type": "computer_call",
        "call_id": "before",
        "status": "completed",
        "actions": [{"type": "wait"}],
    }
    output: dict[str, object] = {
        "type": "computer_call_output",
        "call_id": "before",
        "output": {"type": "computer_screenshot", "file_id": "file_fixture"},
    }
    history: list[dict[str, object]] = [call, output]
    if case == "duplicate-id":
        history = [
            fn("record", "a", text="past"),
            {"type": "function_call_output", "call_id": "a", "output": "past"},
            {**fn("record", "b", text="past"), "id": "fc_a"},
            {"type": "function_call_output", "call_id": "b", "output": "past"},
        ]
    elif case == "missing-status":
        del call["status"]
    elif case == "null-status":
        call["status"] = None
    elif case.startswith("output-"):
        if case == "output-id":
            output["id"] = 42
        elif case == "output-status":
            output["status"] = "failed"
        elif case == "output-checks":
            output["acknowledged_safety_checks"] = "not a list"
        else:
            key = case.removeprefix("output-check-")
            output["acknowledged_safety_checks"] = [{**{"id": "check", "code": None, "message": None}, key: 42}]
    else:
        part: dict[str, object] = {"type": "output_text", "text": "Earlier", "annotations": []}
        if case == "numeric-text":
            part["text"] = 42
        elif case == "numeric-refusal":
            part = {"type": "refusal", "refusal": 42}
        elif case in ("citation-index", "citation-boolean"):
            part["annotations"] = [
                {
                    "type": "url_citation",
                    "title": "Source",
                    "url": "https://example.com/",
                    "start_index": "0" if case == "citation-index" else False,
                    "end_index": 3,
                }
            ]
        else:
            part["logprobs"] = [
                {
                    "token": "e",
                    "bytes": ["101" if case == "logprob-bytes" else True],
                    "logprob": -1.0,
                    "top_logprobs": [],
                }
            ]
        history = [
            {"id": "msg_earlier", "type": "message", "role": "assistant", "status": "completed", "content": [part]}
        ]
    records: list[ResponsesToolCheckpoint] = []
    requests: list[dict[str, Any]] = []
    driver = Driver()
    effects: list[str] = []
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "input": history})
    checkpoint = None
    if restoring:
        await run(lane, None, [FINAL], [], computer=Driver(), save=records.append)
        checkpoint = deepcopy(next(item for item in records if item["phase"] == "boundary"))
        checkpoint["history"] = cast(Any, history)
        records.clear()
        params = PARAMS
    with pytest.raises(ValueError):
        await run(
            lane,
            None,
            [FINAL],
            requests,
            computer=driver,
            save=records.append,
            resume=checkpoint,
            max_steps=None if restoring else 20,
            params=params,
            effects=effects,
        )
    assert records == requests == driver.actions == effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("output_status", [None, "in_progress", "completed", "incomplete"])
async def test_native_replay_keeps_nullable_output_and_integer_logprobs(lane: str, output_status: str | None) -> None:
    history: list[dict[str, object]] = [
        {"id": "cu", "type": "computer_call", "call_id": "prior", "status": "completed", "actions": [{"type": "wait"}]},
        {
            "id": None,
            "type": "computer_call_output",
            "call_id": "prior",
            "status": output_status,
            "acknowledged_safety_checks": [{"id": "s", "code": None, "message": None}],
            "output": {"type": "computer_screenshot", "file_id": "file_fixture"},
            "future": {"opaque": True},
        },
        {
            "id": "earlier",
            "role": "assistant",
            "type": "message",
            "status": "completed",
            "future": ["kept", True],
            "content": [
                {"type": "refusal", "refusal": "Earlier refusal"},
                {"type": "output_text", "text": "read", "annotations": [], "logprobs": None},
                {
                    "type": "output_text",
                    "text": "again",
                    "annotations": [],
                    "logprobs": [
                        {
                            "token": "a",
                            "bytes": [97],
                            "logprob": 0,
                            "top_logprobs": [{"token": "a", "bytes": [97], "logprob": -1}],
                        }
                    ],
                },
            ],
        },
    ]
    records: list[ResponsesToolCheckpoint] = []
    requests: list[dict[str, Any]] = []
    driver = Driver()
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "input": history})
    await run(lane, None, [FINAL], requests, params=params, computer=driver, save=records.append)
    assert requests[0]["input"] == history and driver.actions == []
    boundary = next(record for record in records if record["phase"] == "boundary")
    requests.clear()
    await run(lane, None, [FINAL], requests, computer=driver, save=records.append, resume=boundary, max_steps=None)
    assert requests[0]["input"] == [*history, {"role": "user", "content": PARAMS.get("input")}] and driver.actions == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("restoring", [False, True], ids=["input", "resume"])
@pytest.mark.parametrize(
    ("where", "fields", "valid"),
    [
        ("call", {"call_id": "approval"}, False),
        ("output", {"id": 42}, False),
        ("output", {"name": 42}, False),
        ("output", {"namespace": 42}, False),
        ("output", {"caller": {"type": "program", "caller_id": 42}}, False),
        ("output", {"status": "failed"}, False),
        ("approval", {"id": 42}, False),
        ("approval", {"reason": 42}, False),
        ("output", {"id": None, "name": None, "namespace": None, "caller": None, "status": None}, True),
        (
            "output",
            {"id": "fo", "name": "record", "namespace": "ns", "caller": {"type": "direct"}, "status": "incomplete"},
            True,
        ),
        ("output", {"caller": {"type": "program", "caller_id": "pg"}, "status": "in_progress"}, True),
        ("approval", {"id": None, "reason": None}, True),
        ("approval", {"id": "answer", "reason": "Declined"}, True),
    ],
)
async def test_history_original_output_and_approval_metadata(
    lane: str, restoring: bool, where: str, fields: dict[str, object], valid: bool
) -> None:
    history: list[dict[str, object]] = [
        {"type": "mcp_approval_request", "id": "approval", "server_label": "desk", "name": "read", "arguments": "{}"},
        {"type": "mcp_approval_response", "approval_request_id": "approval", "approve": False},
        fn("record", "prior", text="past"),
        {"type": "function_call_output", "call_id": "prior", "output": "past", "future": {"keep": True}},
    ]
    tools: list[dict[str, object]] = [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid"}]
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "tools": tools, "input": history})
    records: list[ResponsesToolCheckpoint] = []
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    checkpoint = None
    if restoring:
        await run(
            lane,
            None,
            [resp([fn("record", "fresh", text="fixture")], "first"), FINAL],
            [],
            params=params,
            save=records.append,
        )
        checkpoint = deepcopy(next(item for item in records if item["phase"] == "boundary"))
        history = cast(list[dict[str, object]], checkpoint["history"])
        params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "tools": tools})
        records.clear()
    item = history[{"approval": 1, "call": 2, "output": 3}[where]]
    item.update(fields)
    if where == "call":
        history[3]["call_id"] = "approval"
        if checkpoint is not None:
            checkpoint["returned_call_ids"] = ["approval", "fresh"]
    original = deepcopy(history)
    if valid:
        await run(
            lane,
            None,
            [FINAL],
            requests,
            params=params,
            effects=effects,
            save=records.append,
            resume=checkpoint,
            max_steps=None if restoring else 20,
        )
        assert requests[0]["input"][: len(history)] == original
        assert records[0]["history"][: len(history)] == original and effects == []
    else:
        with pytest.raises(ValueError):
            await run(
                lane,
                None,
                [FINAL],
                requests,
                params=params,
                effects=effects,
                save=records.append,
                resume=checkpoint,
                max_steps=None if restoring else 20,
            )
        assert requests == [] and records == [] and effects == []
