from __future__ import annotations

from copy import deepcopy
from typing import Any, cast
from itertools import count

import pytest

from openai._compat import model_copy
from openai._models import BaseModel
from openai.types.responses import responses_server_event as events
from openai.lib.responses_websocket import ResponsesWebSocketAccumulator
from openai.types.responses.responses_server_event import ResponsesServerEvent

INDEX = 7
ITEM_ID = "rich_item"
LANE = "rich_lane"
_SEQUENCE = count()


def response(status: str = "in_progress", **fields: Any) -> dict[str, Any]:
    return {
        "id": "rich_response",
        "object": "response",
        "created_at": 1,
        "model": "synthetic-model",
        "output": [],
        "parallel_tool_calls": False,
        "tool_choice": "auto",
        "tools": [],
        "status": status,
        "metadata": {"stage": "created"},
        **fields,
    }


def typed(model: type[BaseModel], tag: str, **fields: Any) -> ResponsesServerEvent:
    # Construct real generated WS models with validation, not model_construct.
    return cast(
        ResponsesServerEvent,
        model(type=tag, sequence_number=next(_SEQUENCE), stream_id=LANE, **fields),
    )


def item(kind: str, **fields: Any) -> dict[str, Any]:
    return {"id": ITEM_ID, "type": kind, "future_item": {"nested": [1], "optional": None}, **fields}


def reasoning(**fields: Any) -> dict[str, Any]:
    return item("reasoning", summary=[{"type": "summary_text", "text": "seed"}], **fields)


def interpreter() -> dict[str, Any]:
    return item("code_interpreter_call", container_id="synthetic_container", status="in_progress", code="seed")


def shell(commands: list[str]) -> dict[str, Any]:
    return item(
        "shell_call",
        call_id="synthetic_call",
        status="in_progress",
        action={"commands": commands, "timeout_ms": 100, "future_action": None},
    )


def shell_output() -> dict[str, Any]:
    return item(
        "shell_call_output",
        call_id="synthetic_call",
        status="in_progress",
        output=[
            {
                "stdout": "seed-out",
                "stderr": "seed-err",
                "outcome": {"type": "exit", "exit_code": 0},
                "future_output": {"keep": True},
            }
        ],
    )


def seeded(source: dict[str, Any]) -> ResponsesWebSocketAccumulator:
    acc = ResponsesWebSocketAccumulator()
    acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response()))
    acc.add_event(
        typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=INDEX, item=source)
    )
    return acc


def row(acc: ResponsesWebSocketAccumulator, output_index: int = INDEX) -> dict[str, Any]:
    return next(
        cast("dict[str, Any]", item)
        for item in acc.detailed_snapshot()["output"]
        if item["output_index"] == output_index
    )


def value(data: Any, path: tuple[str | int, ...]) -> Any:
    try:
        for key in path:
            data = data[key]
    except (KeyError, IndexError, TypeError):
        return ("absent", path)
    return data


def rich_cases() -> list[Any]:
    cases = [
        (
            events.ResponseReasoningSummaryPartWsAdded,
            "response.reasoning_summary_part.added",
            item("reasoning", summary=[]),
            {"summary_index": 0, "part": {"type": "summary_text", "text": "added", "future_part": None}},
            ("item", "summary", 0, "text"),
            "added",
        ),
        (
            events.ResponseReasoningSummaryPartWsDone,
            "response.reasoning_summary_part.done",
            reasoning(),
            {"summary_index": 0, "part": {"type": "summary_text", "text": "done", "future_part": "done"}},
            ("item", "summary", 0, "text"),
            "done",
        ),
        (
            events.ResponseReasoningSummaryTextWsDelta,
            "response.reasoning_summary_text.delta",
            reasoning(),
            {"summary_index": 0, "delta": "+delta"},
            ("item", "summary", 0, "text"),
            "seed+delta",
        ),
        (
            events.ResponseReasoningSummaryTextWsDone,
            "response.reasoning_summary_text.done",
            reasoning(),
            {"summary_index": 0, "text": "done"},
            ("item", "summary", 0, "text"),
            "done",
        ),
        (
            events.ResponseReasoningTextWsDelta,
            "response.reasoning_text.delta",
            reasoning(content=[{"type": "reasoning_text", "text": "seed"}]),
            {"content_index": 0, "delta": "+delta"},
            ("content", 0, "part", "text"),
            "seed+delta",
        ),
        (
            events.ResponseReasoningTextWsDone,
            "response.reasoning_text.done",
            reasoning(content=[{"type": "reasoning_text", "text": "seed"}]),
            {"content_index": 0, "text": "done"},
            ("content", 0, "part", "text"),
            "done",
        ),
        (
            events.ResponseShellCallCommandWsAdded,
            "response.shell_call_command.added",
            shell([]),
            {"command_index": 0, "command": "added"},
            ("item", "action", "commands"),
            ["added"],
        ),
        (
            events.ResponseShellCallCommandWsDelta,
            "response.shell_call_command.delta",
            shell(["seed"]),
            {"command_index": 0, "delta": "+delta"},
            ("item", "action", "commands"),
            ["seed+delta"],
        ),
        (
            events.ResponseShellCallCommandWsDone,
            "response.shell_call_command.done",
            shell(["seed"]),
            {"command_index": 0, "command": "done"},
            ("item", "action", "commands"),
            ["done"],
        ),
        (
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            shell_output(),
            {"command_index": 0, "delta": {"stdout": "+out", "stderr": "+err"}},
            ("shell_output", 0, "data"),
            {"stdout": "+out", "stderr": "+err"},
        ),
        (
            events.ResponseShellCallOutputContentWsDone,
            "response.shell_call_output_content.done",
            shell_output(),
            {
                "command_index": 0,
                "output": [
                    {
                        "stdout": "done-out",
                        "stderr": "done-err",
                        "outcome": {"type": "timeout"},
                        "future_output": {"done": True},
                    }
                ],
            },
            ("shell_output", 0, "data", "output"),
            [
                {
                    "stdout": "done-out",
                    "stderr": "done-err",
                    "outcome": {"type": "timeout"},
                    "future_output": {"done": True},
                }
            ],
        ),
        (
            events.ResponseCodeInterpreterCallCodeWsDelta,
            "response.code_interpreter_call_code.delta",
            interpreter(),
            {"delta": "+delta"},
            ("item", "code"),
            "seed+delta",
        ),
        (
            events.ResponseCodeInterpreterCallCodeWsDone,
            "response.code_interpreter_call_code.done",
            interpreter(),
            {"code": "done"},
            ("item", "code"),
            "done",
        ),
    ]
    status_families = [
        (
            interpreter(),
            [
                (events.ResponseCodeInterpreterCallInWsProgress, "in_progress"),
                (events.ResponseCodeInterpreterCallWsInterpreting, "interpreting"),
                (events.ResponseCodeInterpreterCallWsCompleted, "completed"),
            ],
            "code_interpreter_call",
        ),
        (
            item("file_search_call", queries=["synthetic"], status="in_progress"),
            [
                (events.ResponseFileSearchCallInWsProgress, "in_progress"),
                (events.ResponseFileSearchCallWsSearching, "searching"),
                (events.ResponseFileSearchCallWsCompleted, "completed"),
            ],
            "file_search_call",
        ),
        (
            item("web_search_call", action={"type": "search", "query": "synthetic"}, status="in_progress"),
            [
                (events.ResponseWebSearchCallInWsProgress, "in_progress"),
                (events.ResponseWebSearchCallWsSearching, "searching"),
                (events.ResponseWebSearchCallWsCompleted, "completed"),
            ],
            "web_search_call",
        ),
        (
            item("image_generation_call", status="in_progress"),
            [
                (events.ResponseImageGenCallInWsProgress, "in_progress"),
                (events.ResponseImageGenCallWsGenerating, "generating"),
                (events.ResponseImageGenCallWsCompleted, "completed"),
            ],
            "image_generation_call",
        ),
        (
            item("mcp_call", name="synthetic", server_label="fixture", arguments="{}"),
            [
                (events.ResponseMcpCallInWsProgress, "in_progress"),
                (events.ResponseMcpCallWsCompleted, "completed"),
                (events.ResponseMcpCallWsFailed, "failed"),
            ],
            "mcp_call",
        ),
    ]
    for source, statuses, family in status_families:
        for model, status in statuses:
            cases.append((model, f"response.{family}.{status}", source, {}, ("item", "status"), status))
    return [pytest.param(*case, id=case[1]) for case in cases]


@pytest.mark.parametrize("model,tag,source,fields,path,expected", rich_cases())
def test_rich_progress_through_public_accumulator(
    model: type[BaseModel],
    tag: str,
    source: dict[str, Any],
    fields: dict[str, Any],
    path: tuple[str | int, ...],
    expected: Any,
) -> None:
    acc = seeded(source)
    old_details = acc.detailed_snapshot()
    old_compact = acc.snapshot()
    routing = {} if tag.startswith("response.shell_call_command.") else {"item_id": ITEM_ID}
    event = typed(model, tag, output_index=INDEX, **routing, **fields)
    original = event.to_dict()
    if tag.startswith("response.shell_call_command."):
        assert "item_id" not in original
    acc.add_event(event)
    current = row(acc)
    assert value(current, path) == expected
    assert current["output_index"] == INDEX
    assert current["item"]["future_item"] == {"nested": [1], "optional": None}
    assert acc.snapshot() == old_compact
    assert acc.snapshot().output_text == ""
    assert event.to_dict() == original
    current["item"]["future_item"]["nested"].append(2)
    assert row(acc)["item"]["future_item"]["nested"] == [1]
    assert old_details["output"][0]["item"]["future_item"]["nested"] == [1]


@pytest.mark.parametrize("phase", ["added", "done"])
def test_reasoning_content_parts_retain_other_indexed_parts(phase: str) -> None:
    parts = [{"type": "reasoning_text", "text": "keep", "future_part": {"keep": True}}]
    if phase == "done":
        parts.append({"type": "reasoning_text", "text": "draft"})
    acc = seeded(reasoning(content=parts))
    model = events.ResponseContentPartWsAdded if phase == "added" else events.ResponseContentPartWsDone
    event = typed(
        model,
        f"response.content_part.{phase}",
        output_index=INDEX,
        content_index=1,
        item_id=ITEM_ID,
        part={"type": "reasoning_text", "text": phase},
    )
    original = event.to_dict()
    acc.add_event(event)
    assert row(acc)["content"] == [
        {"content_index": 0, "part": parts[0]},
        {"content_index": 1, "part": {"type": "reasoning_text", "text": phase}},
    ]
    assert acc.snapshot().output_text == ""
    assert event.to_dict() == original


@pytest.mark.parametrize("initial_created", [False, True])
def test_queued_lifecycle_refreshes_observed_metadata(initial_created: bool) -> None:
    acc = ResponsesWebSocketAccumulator()
    if initial_created:
        acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response("queued")))
    event = typed(
        events.ResponseWsQueued,
        "response.queued",
        response=response("queued", metadata={"stage": "queued"}, future_response={"observed": None}),
    )
    original = event.to_dict()
    acc.add_event(event)
    details = acc.detailed_snapshot()
    assert details["response"] is not None
    assert details["response"]["metadata"] == {"stage": "queued"}
    assert details["response"]["future_response"] == {"observed": None}
    assert acc.snapshot().response_id == "rich_response"
    assert event.to_dict() == original
    with pytest.raises(RuntimeError, match="No terminal"):
        acc.get_final_response()


def test_normal_reasoning_parts_and_text_share_one_detached_projection() -> None:
    acc = seeded(reasoning(content=[]))
    summary_delta = typed(
        events.ResponseReasoningSummaryTextWsDelta,
        "response.reasoning_summary_text.delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        summary_index=0,
        delta="+keep",
    )
    added = typed(
        events.ResponseContentPartWsAdded,
        "response.content_part.added",
        output_index=INDEX,
        item_id=ITEM_ID,
        content_index=0,
        part={"type": "reasoning_text", "text": "part-seed", "future_part": {"keep": True}},
    )
    delta = typed(
        events.ResponseReasoningTextWsDelta,
        "response.reasoning_text.delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        content_index=0,
        delta="+delta",
    )
    done = typed(
        events.ResponseContentPartWsDone,
        "response.content_part.done",
        output_index=INDEX,
        item_id=ITEM_ID,
        content_index=0,
        part={"type": "reasoning_text", "text": "part-done", "future_part": {"done": True}},
    )
    originals = [event.to_dict() for event in (summary_delta, added, delta, done)]
    for event in (summary_delta, added, delta):
        acc.add_event(event)
    before_done = acc.detailed_snapshot()
    assert before_done["output"][0]["content"][0]["part"]["text"] == "part-seed+delta"
    assert before_done["output"][0]["item"]["content"][0]["text"] == "part-seed+delta"
    acc.add_event(done)
    current = row(acc)
    expected_part = {"type": "reasoning_text", "text": "part-done", "future_part": {"done": True}}
    assert current["content"] == [{"content_index": 0, "part": expected_part}]
    assert current["item"]["content"] == [expected_part]
    assert current["item"]["summary"][0]["text"] == "seed+keep"
    assert before_done["output"][0]["content"][0]["part"]["text"] == "part-seed+delta"
    assert acc.snapshot().output_text == ""
    assert [event.to_dict() for event in (summary_delta, added, delta, done)] == originals


def test_shell_output_can_start_empty_without_fabricating_an_outcome() -> None:
    source = shell_output()
    source["output"] = []
    acc = seeded(source)
    event = typed(
        events.ResponseShellCallOutputContentWsDelta,
        "response.shell_call_output_content.delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        command_index=0,
        delta={"stdout": "first"},
    )
    original = event.to_dict()
    acc.add_event(event)
    current = row(acc)
    assert current["item"]["output"] == []
    assert current["shell_output"] == [{"command_index": 0, "data": {"stdout": "first"}}]
    assert event.to_dict() == original


def test_shell_output_retains_a_later_command_first_as_sparse_progress() -> None:
    acc = seeded(shell(["first", "second", "third"]))
    source = shell_output()
    source["id"] = "shell_output"
    source["output"] = []
    output_index = INDEX + 1
    acc.add_event(
        typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=output_index, item=source)
    )
    for command_index, delta in [(2, {"stdout": "late"}), (0, {"stdout": "first"})]:
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=output_index,
                item_id="shell_output",
                command_index=command_index,
                delta=delta,
            )
        )
    before_done = acc.detailed_snapshot()
    current = row(acc, output_index)
    assert current["item"]["output"] == []
    assert current["shell_output"] == [
        {"command_index": 0, "data": {"stdout": "first"}},
        {"command_index": 2, "data": {"stdout": "late"}},
    ]
    final_output = {
        "stdout": "done",
        "stderr": "done-error",
        "outcome": {"type": "exit", "exit_code": 7},
        "future_output": None,
    }
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDone,
            "response.shell_call_output_content.done",
            output_index=output_index,
            item_id="shell_output",
            command_index=2,
            output=[final_output],
        )
    )
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            output_index=output_index,
            item_id="shell_output",
            command_index=1,
            delta={"stderr": "middle"},
        )
    )
    assert row(acc, output_index)["item"]["output"] == []
    assert row(acc, output_index)["shell_output"] == [
        {"command_index": 0, "data": {"stdout": "first"}},
        {"command_index": 1, "data": {"stderr": "middle"}},
        {"command_index": 2, "data": {"output": [final_output]}},
    ]
    assert before_done["output"][1]["shell_output"][1]["data"] == {"stdout": "late"}


def test_summary_done_full_item_and_terminal_have_separate_authority() -> None:
    acc = ResponsesWebSocketAccumulator()
    acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response()))
    scaffold = typed(
        events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=INDEX, item=reasoning()
    )
    original_scaffold = scaffold.to_dict()
    acc.add_event(scaffold)
    delta = typed(
        events.ResponseReasoningSummaryTextWsDelta,
        "response.reasoning_summary_text.delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        summary_index=0,
        delta="+delta",
    )
    acc.add_event(delta)
    after_delta = acc.detailed_snapshot()
    assert row(acc)["item"]["summary"][0]["text"] == "seed+delta"
    acc.add_event(
        typed(
            events.ResponseReasoningSummaryTextWsDone,
            "response.reasoning_summary_text.done",
            output_index=INDEX,
            item_id=ITEM_ID,
            summary_index=0,
            text="done",
        )
    )
    after_done = acc.detailed_snapshot()
    assert row(acc)["item"]["summary"][0]["text"] == "done"
    full = reasoning()
    full["summary"][0]["text"] = "full-item"
    full["future_item"] = {"authority": "full-item"}
    acc.add_event(typed(events.ResponseOutputItemWsDone, "response.output_item.done", output_index=INDEX, item=full))
    assert row(acc)["item"]["summary"][0]["text"] == "full-item"
    terminal_item = deepcopy(full)
    terminal_item["summary"][0]["text"] = "terminal"
    terminal = typed(
        events.ResponseWsCompleted, "response.completed", response=response("completed", output=[terminal_item])
    )
    original_terminal = terminal.to_dict()
    acc.add_event(terminal)
    final_item = acc.get_final_response().output[0]
    assert final_item.type == "reasoning"
    assert final_item.summary[0].text == "terminal"
    assert after_delta["output"][0]["item"]["summary"][0]["text"] == "seed+delta"
    assert after_done["output"][0]["item"]["summary"][0]["text"] == "done"
    assert terminal.to_dict() == original_terminal
    assert scaffold.to_dict() == original_scaffold
    returned = acc.get_final_response()
    returned.output.clear()
    assert len(acc.get_final_response().output) == 1


def test_status_and_other_part_replacements_preserve_text_fragments() -> None:
    acc = seeded(interpreter())
    acc.add_event(
        typed(
            events.ResponseCodeInterpreterCallCodeWsDelta,
            "response.code_interpreter_call_code.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            delta="+before",
        )
    )
    acc.add_event(
        typed(
            events.ResponseCodeInterpreterCallWsInterpreting,
            "response.code_interpreter_call.interpreting",
            output_index=INDEX,
            item_id=ITEM_ID,
        )
    )
    acc.add_event(
        typed(
            events.ResponseCodeInterpreterCallCodeWsDelta,
            "response.code_interpreter_call_code.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            delta="+after",
        )
    )
    assert row(acc)["item"]["code"] == "seed+before+after"
    assert row(acc)["item"]["status"] == "interpreting"

    source = reasoning()
    source["summary"].append({"type": "summary_text", "text": "other"})
    acc = seeded(source)
    acc.add_event(
        typed(
            events.ResponseReasoningSummaryTextWsDelta,
            "response.reasoning_summary_text.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            summary_index=0,
            delta="+keep",
        )
    )
    acc.add_event(
        typed(
            events.ResponseReasoningSummaryPartWsDone,
            "response.reasoning_summary_part.done",
            output_index=INDEX,
            item_id=ITEM_ID,
            summary_index=1,
            part={"type": "summary_text", "text": "replacement"},
        )
    )
    assert [part["text"] for part in row(acc)["item"]["summary"]] == ["seed+keep", "replacement"]


def test_shell_command_replacement_preserves_another_commands_fragments() -> None:
    acc = seeded(shell(["seed"]))
    acc.add_event(
        typed(
            events.ResponseShellCallCommandWsDelta,
            "response.shell_call_command.delta",
            output_index=INDEX,
            command_index=0,
            delta="+keep",
        )
    )
    acc.add_event(
        typed(
            events.ResponseShellCallCommandWsAdded,
            "response.shell_call_command.added",
            output_index=INDEX,
            command_index=1,
            command="second",
        )
    )
    before_done = acc.detailed_snapshot()
    acc.add_event(
        typed(
            events.ResponseShellCallCommandWsDelta,
            "response.shell_call_command.delta",
            output_index=INDEX,
            command_index=1,
            delta="+delta",
        )
    )
    acc.add_event(
        typed(
            events.ResponseShellCallCommandWsDone,
            "response.shell_call_command.done",
            output_index=INDEX,
            command_index=1,
            command="done",
        )
    )
    assert row(acc)["item"]["action"]["commands"] == ["seed+keep", "done"]
    assert before_done["output"][0]["item"]["action"]["commands"] == ["seed+keep", "second"]


@pytest.mark.parametrize("extra_item_id", [42, "unrelated_item"])
@pytest.mark.parametrize(
    "model,tag,fields,expected",
    [
        (
            events.ResponseShellCallCommandWsAdded,
            "response.shell_call_command.added",
            {"command_index": 1, "command": "added"},
            ["seed", "added"],
        ),
        (
            events.ResponseShellCallCommandWsDelta,
            "response.shell_call_command.delta",
            {"command_index": 0, "delta": "+delta"},
            ["seed+delta"],
        ),
        (
            events.ResponseShellCallCommandWsDone,
            "response.shell_call_command.done",
            {"command_index": 0, "command": "done"},
            ["done"],
        ),
    ],
)
def test_shell_commands_preserve_but_do_not_route_by_unmodeled_item_id(
    model: type[BaseModel], tag: str, fields: dict[str, Any], expected: list[str], extra_item_id: Any
) -> None:
    acc = seeded(shell(["seed"]))
    event = typed(model, tag, output_index=INDEX, item_id=extra_item_id, future_event={"keep": [1]}, **fields)
    original = event.to_dict()
    acc.add_event(event)
    assert row(acc)["item"]["action"]["commands"] == expected
    assert event.to_dict() == original
    assert original["item_id"] == extra_item_id


@pytest.mark.parametrize("target", ["absent", "wrong_kind"])
def test_shell_commands_require_an_observed_shell_call_at_their_index(target: str) -> None:
    acc = seeded(item("message", role="assistant", status="completed", content=[], action={"commands": ["owned"]}))
    before = acc.detailed_snapshot()
    event = typed(
        events.ResponseShellCallCommandWsDelta,
        "response.shell_call_command.delta",
        output_index=INDEX + 1 if target == "absent" else INDEX,
        command_index=0,
        delta="must-not-apply",
    )
    acc.add_event(event)
    assert acc.detailed_snapshot() == before


def test_shell_bounds_refresh_after_late_call_growth_and_replacement() -> None:
    source = shell_output()
    source["output"] = []
    acc = seeded(source)
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            command_index=0,
            delta={"stdout": "first"},
        )
    )
    call_index = INDEX + 1
    call = shell(["first", "second"])
    call["id"] = "call_item"
    acc.add_event(
        typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=call_index, item=call)
    )
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            command_index=1,
            delta={"stdout": "second"},
        )
    )
    acc.add_event(
        typed(
            events.ResponseShellCallCommandWsAdded,
            "response.shell_call_command.added",
            output_index=call_index,
            command_index=2,
            command="third",
        )
    )
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            command_index=2,
            delta={"stdout": "third"},
        )
    )
    assert [part["data"]["stdout"] for part in row(acc)["shell_output"]] == ["first", "second", "third"]

    call["action"]["commands"] = ["only"]
    acc.add_event(
        typed(events.ResponseOutputItemWsDone, "response.output_item.done", output_index=call_index, item=call)
    )
    before = acc.detailed_snapshot()
    with pytest.raises(ValueError):
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=INDEX,
                item_id=ITEM_ID,
                command_index=1,
                delta={"stdout": "must-not-apply"},
            )
        )
    assert acc.detailed_snapshot() == before

    replacement = item("message", role="assistant", status="completed", content=[])
    replacement["id"] = "message_item"
    acc.add_event(
        typed(events.ResponseOutputItemWsDone, "response.output_item.done", output_index=call_index, item=replacement)
    )
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            command_index=1,
            delta={"stdout": "+after-removal"},
        )
    )
    assert row(acc)["shell_output"][1]["data"]["stdout"] == "second+after-removal"


@pytest.mark.parametrize("with_call", [False, True])
def test_many_shell_fragments_keep_snapshots_and_new_lifecycle_bounds(with_call: bool) -> None:
    acc = ResponsesWebSocketAccumulator()
    acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response()))
    source = shell_output()
    source["id"] = "output_item"
    source["output"] = []
    output_index = INDEX + 1
    for index in range(64):
        unrelated = item("message", role="assistant", status="completed", content=[])
        unrelated["id"] = f"unrelated_{index}"
        acc.add_event(
            typed(
                events.ResponseOutputItemWsAdded,
                "response.output_item.added",
                output_index=INDEX + 2 + index,
                item=unrelated,
            )
        )
    if with_call:
        acc.add_event(
            typed(
                events.ResponseOutputItemWsAdded,
                "response.output_item.added",
                output_index=INDEX,
                item=shell(["first", "second"]),
            )
        )
    acc.add_event(
        typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=output_index, item=source)
    )
    command_index = 1 if with_call else 0
    for _ in range(2048):
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=output_index,
                item_id="output_item",
                command_index=command_index,
                delta={"stdout": "x"},
            )
        )
    prior = acc.detailed_snapshot()
    assert row(acc, output_index)["shell_output"] == [{"command_index": command_index, "data": {"stdout": "x" * 2048}}]
    new_call = shell(["only"])
    new_call["id"] = "new_call"
    acc.add_event(
        typed(events.ResponseInWsProgress, "response.in_progress", response=response(output=[new_call, source]))
    )
    before = acc.detailed_snapshot()
    with pytest.raises(ValueError):
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=1,
                item_id="output_item",
                command_index=1,
                delta={"stdout": "must-not-apply"},
            )
        )
    assert acc.detailed_snapshot() == before
    assert prior["output"][1 if with_call else 0]["shell_output"][0]["data"]["stdout"] == "x" * 2048


def test_many_distinct_shell_outputs_keep_their_bounds_across_unrelated_call_insertions() -> None:
    count = 64
    outputs: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for index in range(count):
        output = shell_output()
        output.update(id=f"output_{index}", call_id=f"call_{index}", output=[])
        outputs.append(output)
        call = shell(["command"] * (index % 3 + 1))
        call.update(id=f"call_item_{index}", call_id=f"call_{index}")
        calls.append(call)
    acc = ResponsesWebSocketAccumulator()
    acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response(parallel_tool_calls=True)))
    lifecycle = typed(
        events.ResponseInWsProgress,
        "response.in_progress",
        response=response(parallel_tool_calls=True, output=outputs + calls),
    )
    original = lifecycle.to_dict()
    acc.add_event(lifecycle)
    for index in range(count):
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=index,
                item_id=f"output_{index}",
                command_index=index % 3,
                delta={"stdout": f"first_{index}"},
            )
        )
    prior = acc.detailed_snapshot()
    for index in range(count):
        unrelated = shell(["unrelated"])
        unrelated.update(id=f"unrelated_item_{index}", call_id=f"unrelated_call_{index}")
        acc.add_event(
            typed(
                events.ResponseOutputItemWsAdded,
                "response.output_item.added",
                output_index=2 * count + index,
                item=unrelated,
            )
        )
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=index,
                item_id=f"output_{index}",
                command_index=index % 3,
                delta={"stdout": "+after-unrelated-call"},
            )
        )
    details = acc.detailed_snapshot()
    for index, output in enumerate(details["output"][:count]):
        assert output["item"]["output"] == []
        assert output["shell_output"] == [
            {"command_index": index % 3, "data": {"stdout": f"first_{index}+after-unrelated-call"}}
        ]
        assert prior["output"][index]["shell_output"][0]["data"] == {"stdout": f"first_{index}"}
    for index in range(3):
        with pytest.raises(ValueError, match="missing its command"):
            acc.add_event(
                typed(
                    events.ResponseShellCallOutputContentWsDelta,
                    "response.shell_call_output_content.delta",
                    output_index=index,
                    item_id=f"output_{index}",
                    command_index=index % 3 + 1,
                    delta={"stdout": "must-not-apply"},
                )
            )
    assert acc.detailed_snapshot() == details
    assert lifecycle.to_dict() == original


@pytest.mark.parametrize("clear", ["lifecycle", "reset"])
def test_shell_bounds_do_not_survive_removal_from_lifecycle_or_reset(clear: str) -> None:
    output = shell_output()
    output["output"] = []
    acc = seeded(output)
    call = shell([])
    call["id"] = "empty_call"
    acc.add_event(
        typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=INDEX + 1, item=call)
    )
    with pytest.raises(ValueError, match="missing its command"):
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=INDEX,
                item_id=ITEM_ID,
                command_index=0,
                delta={"stdout": "must-not-apply"},
            )
        )
    if clear == "reset":
        acc.reset()
        acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response(output=[output])))
    else:
        acc.add_event(typed(events.ResponseInWsProgress, "response.in_progress", response=response(output=[output])))
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            output_index=0,
            item_id=ITEM_ID,
            command_index=5,
            delta={"stdout": "unknown-bound"},
        )
    )
    assert row(acc, 0)["shell_output"] == [{"command_index": 5, "data": {"stdout": "unknown-bound"}}]


@pytest.mark.parametrize("presence", ["absent", "null", "present"])
@pytest.mark.parametrize("family", ["function_call", "custom_tool_call"])
def test_full_tool_item_id_presence_is_separate_from_observed_delta_identity(family: str, presence: str) -> None:
    field = "arguments" if family == "function_call" else "input"
    seed = "{" if family == "function_call" else "seed"
    fragment = '"observed":true}' if family == "function_call" else "+delta"
    completed = '{"replacement":true}' if family == "function_call" else "replacement"
    source = item(family, name="synthetic", call_id="synthetic_call", status="in_progress", **{field: seed})
    if presence == "absent":
        del source["id"]
    elif presence == "null":
        source["id"] = None
    acc = ResponsesWebSocketAccumulator()
    acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response()))
    scaffold = typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=INDEX, item=source)
    original_scaffold = scaffold.to_dict()
    acc.add_event(scaffold)
    before_delta = acc.detailed_snapshot()
    model = (
        events.ResponseFunctionCallArgumentsWsDelta
        if family == "function_call"
        else events.ResponseCustomToolCallInputWsDelta
    )
    tag = (
        "response.function_call_arguments.delta"
        if family == "function_call"
        else "response.custom_tool_call_input.delta"
    )
    delta = typed(model, tag, output_index=INDEX, item_id=ITEM_ID, delta=fragment)
    original_delta = delta.to_dict()
    acc.add_event(delta)
    current = row(acc)
    assert ("id" in current["item"]) == ("id" in source)
    if "id" in source:
        assert current["item"]["id"] == source["id"]
    assert current["item"][field] == seed + fragment
    assert acc.snapshot().output[0].item_id == ITEM_ID
    assert before_delta["output"][0]["item"] == source
    assert scaffold.to_dict() == original_scaffold
    assert delta.to_dict() == original_delta

    before_replacement = acc.detailed_snapshot()
    replacement = deepcopy(source)
    replacement.update(status="completed", future_item={"authority": "full-item"}, **{field: completed})
    full = typed(events.ResponseOutputItemWsDone, "response.output_item.done", output_index=INDEX, item=replacement)
    original_full = full.to_dict()
    acc.add_event(full)
    assert row(acc)["item"] == replacement
    assert before_replacement["output"][0]["item"] == current["item"]
    assert before_delta["output"][0]["item"] == source
    assert full.to_dict() == original_full
    assert scaffold.to_dict() == original_scaffold
    assert delta.to_dict() == original_delta


@pytest.mark.parametrize("scaffold", ["absent", "null", "present", "bootstrap"])
@pytest.mark.parametrize("phase", ["delta", "done"])
@pytest.mark.parametrize("family", ["function_call", "custom_tool_call"])
def test_omitted_id_full_tools_keep_bound_identity_and_legacy_replacement_cases(
    family: str, phase: str, scaffold: str
) -> None:
    field = "arguments" if family == "function_call" else "input"
    prefix = "response.function_call_arguments" if family == "function_call" else "response.custom_tool_call_input"
    delta_model = (
        events.ResponseFunctionCallArgumentsWsDelta
        if family == "function_call"
        else events.ResponseCustomToolCallInputWsDelta
    )
    done_model = (
        events.ResponseFunctionCallArgumentsWsDone
        if family == "function_call"
        else events.ResponseCustomToolCallInputWsDone
    )
    acc = ResponsesWebSocketAccumulator()
    acc.add_event(typed(events.ResponseWsCreated, "response.created", response=response()))
    if scaffold != "bootstrap":
        source = item(family, name="synthetic", call_id="synthetic_call", status="in_progress", **{field: ""})
        if scaffold == "absent":
            del source["id"]
        elif scaffold == "null":
            source["id"] = None
        acc.add_event(
            typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=INDEX, item=source)
        )
    first_text = '{"first":true}' if family == "function_call" else "first"
    first = typed(delta_model, prefix + ".delta", output_index=INDEX, item_id=ITEM_ID, delta=first_text)
    original_first = first.to_dict()
    acc.add_event(first)
    before = acc.detailed_snapshot()
    compact_before = acc.snapshot()
    assert compact_before.output[0].item_id == ITEM_ID
    second_text = '{"second":true}' if family == "function_call" else "second"
    fields = {"delta" if phase == "delta" else field: second_text}
    conflict = typed(
        delta_model if phase == "delta" else done_model,
        prefix + "." + phase,
        output_index=INDEX,
        item_id="other_item",
        **fields,
    )
    original_conflict = conflict.to_dict()
    acc.add_event(conflict)
    assert first.to_dict() == original_first
    assert conflict.to_dict() == original_conflict
    if scaffold == "absent":
        assert acc.detailed_snapshot() == before
        assert acc.snapshot() == compact_before
    else:
        # Explicit-null/present IDs and unscaffolded inputs retain replacement policy.
        assert acc.snapshot().output[0].item_id == "other_item"
        assert acc.snapshot().output[0].type is None
        assert getattr(acc.snapshot().output[0], field) == second_text
    assert before["output"][0]["item"][field] == first_text


@pytest.mark.parametrize("phase", ["delta", "done"])
@pytest.mark.parametrize("family", ["function_call", "custom_tool_call"])
def test_omitted_id_full_tool_ignores_other_progress_family_before_binding(family: str, phase: str) -> None:
    field = "arguments" if family == "function_call" else "input"
    source = item(family, name="synthetic", call_id="synthetic_call", status="in_progress", **{field: ""})
    del source["id"]
    acc = seeded(source)
    before = acc.detailed_snapshot()
    compact_before = acc.snapshot()
    if family == "function_call":
        wrong_prefix = "response.custom_tool_call_input"
        wrong_field = "input"
        wrong_model = (
            events.ResponseCustomToolCallInputWsDelta if phase == "delta" else events.ResponseCustomToolCallInputWsDone
        )
        matching_prefix = "response.function_call_arguments"
        matching_model = events.ResponseFunctionCallArgumentsWsDelta
    else:
        wrong_prefix = "response.function_call_arguments"
        wrong_field = "arguments"
        wrong_model = (
            events.ResponseFunctionCallArgumentsWsDelta
            if phase == "delta"
            else events.ResponseFunctionCallArgumentsWsDone
        )
        matching_prefix = "response.custom_tool_call_input"
        matching_model = events.ResponseCustomToolCallInputWsDelta
    wrong = typed(
        wrong_model,
        wrong_prefix + "." + phase,
        output_index=INDEX,
        item_id="wrong_family_item",
        **{"delta" if phase == "delta" else wrong_field: '{"wrong":true}'},
    )
    original_wrong = wrong.to_dict()
    acc.add_event(wrong)
    assert acc.snapshot() == compact_before
    assert acc.detailed_snapshot() == before
    correct_text = '{"correct":true}' if family == "function_call" else "correct"
    matching = typed(
        matching_model,
        matching_prefix + ".delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        delta=correct_text,
    )
    original_matching = matching.to_dict()
    acc.add_event(matching)
    assert acc.snapshot().output[0].item_id == ITEM_ID
    assert row(acc)["item"][field] == correct_text
    assert "id" not in row(acc)["item"]
    assert before["output"][0]["item"] == source
    assert wrong.to_dict() == original_wrong
    assert matching.to_dict() == original_matching


@pytest.mark.parametrize("code_presence", ["missing", "null"])
def test_optional_code_seed_stays_observed_until_progress(code_presence: str) -> None:
    source = interpreter()
    if code_presence == "missing":
        del source["code"]
    else:
        source["code"] = None
    acc = seeded(source)
    before = row(acc)
    assert ("code" in before["item"]) is (code_presence == "null")
    acc.add_event(
        typed(
            events.ResponseCodeInterpreterCallCodeWsDelta,
            "response.code_interpreter_call_code.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            delta="observed",
        )
    )
    assert row(acc)["item"]["code"] == "observed"
    acc.add_event(typed(events.ResponseOutputItemWsDone, "response.output_item.done", output_index=INDEX, item=source))
    assert row(acc)["item"].get("code") is None
    assert ("code" in row(acc)["item"]) is (code_presence == "null")


def test_invalid_shell_stream_cannot_partially_extend_the_other_stream() -> None:
    acc = seeded(shell_output())
    event = typed(
        events.ResponseShellCallOutputContentWsDelta,
        "response.shell_call_output_content.delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        command_index=0,
        delta={"stdout": "+valid", "stderr": "+valid"},
    )
    # The wire parser can retain known events without runtime validation.
    malformed = model_copy(event, deep=True)
    object.__setattr__(malformed, "delta", {"stdout": "+valid", "stderr": 42})
    before = acc.detailed_snapshot()
    with pytest.raises(ValueError, match="stderr must be a string"):
        acc.add_event(malformed)
    assert acc.detailed_snapshot() == before


def test_negative_shell_command_index_cannot_mutate() -> None:
    command_index = -1
    source = shell_output()
    source["output"] = []
    acc = seeded(source)
    before = acc.detailed_snapshot()
    event = typed(
        events.ResponseShellCallOutputContentWsDelta,
        "response.shell_call_output_content.delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        command_index=command_index,
        delta={"stdout": "must-not-apply"},
    )
    with pytest.raises(ValueError):
        acc.add_event(event)
    assert acc.detailed_snapshot() == before


@pytest.mark.parametrize("empty", [False, True], ids=["two-chunks", "empty"])
def test_shell_done_array_replaces_only_its_command_and_preserves_full_authority(empty: bool) -> None:
    acc = seeded(shell(["first", "second", "third"]))
    source = shell_output()
    source["id"] = "output_item"
    output_index = INDEX + 1
    acc.add_event(
        typed(events.ResponseOutputItemWsAdded, "response.output_item.added", output_index=output_index, item=source)
    )
    for command_index, text in [(2, "neighbor"), (0, "draft")]:
        acc.add_event(
            typed(
                events.ResponseShellCallOutputContentWsDelta,
                "response.shell_call_output_content.delta",
                output_index=output_index,
                item_id="output_item",
                command_index=command_index,
                delta={"stdout": text},
            )
        )
    before_done = acc.detailed_snapshot()
    chunks = (
        []
        if empty
        else [
            {
                "stdout": "first-output",
                "stderr": "first-error",
                "outcome": {"type": "exit", "exit_code": 3},
                "created_by": "first-actor",
                "future_output": {"keep": [False, None]},
            },
            {
                "stdout": "second-output",
                "stderr": "second-error",
                "outcome": {"type": "timeout"},
                "created_by": "second-actor",
                "future_output": None,
            },
        ]
    )
    done = typed(
        events.ResponseShellCallOutputContentWsDone,
        "response.shell_call_output_content.done",
        output_index=output_index,
        item_id="output_item",
        command_index=0,
        output=chunks,
    )
    original = done.to_dict()
    acc.add_event(done)
    current = row(acc, output_index)
    assert current["shell_output"] == [
        {"command_index": 0, "data": {"output": chunks}},
        {"command_index": 2, "data": {"stdout": "neighbor"}},
    ]
    assert current["item"]["output"] == source["output"]
    assert before_done["output"][1]["shell_output"][0]["data"] == {"stdout": "draft"}
    assert done.to_dict() == original
    current["shell_output"][0]["data"]["output"].append({"caller": "mutation"})
    assert row(acc, output_index)["shell_output"][0]["data"]["output"] == chunks

    full = deepcopy(source)
    full["output"][0]["stdout"] = "whole-item-output"
    acc.add_event(
        typed(events.ResponseOutputItemWsDone, "response.output_item.done", output_index=output_index, item=full)
    )
    assert row(acc, output_index)["item"]["output"] == full["output"]
    assert row(acc, output_index)["shell_output"] == []
    terminal_item = deepcopy(full)
    terminal_item["output"][0]["stdout"] = "terminal-output"
    terminal = typed(
        events.ResponseWsCompleted, "response.completed", response=response("completed", output=[terminal_item])
    )
    original_terminal = terminal.to_dict()
    acc.add_event(terminal)
    assert row(acc, 0)["item"]["output"] == terminal_item["output"]
    assert row(acc, 0)["shell_output"] == []
    final_item = acc.get_final_response().output[0]
    assert final_item.type == "shell_call_output"
    assert final_item.output[0].stdout == "terminal-output"
    assert terminal.to_dict() == original_terminal
    assert done.to_dict() == original
    assert before_done["output"][1]["shell_output"][0]["data"] == {"stdout": "draft"}


@pytest.mark.parametrize("command_index", [5, 2**65])
def test_shell_without_companion_retains_sparse_observed_command_without_holes(command_index: int) -> None:
    source = shell_output()
    source["output"] = []
    acc = seeded(source)
    event = typed(
        events.ResponseShellCallOutputContentWsDelta,
        "response.shell_call_output_content.delta",
        output_index=INDEX,
        item_id=ITEM_ID,
        command_index=command_index,
        delta={"stdout": "sparse"},
    )
    original = event.to_dict()
    acc.add_event(event)
    assert row(acc)["item"]["output"] == []
    assert row(acc)["shell_output"] == [{"command_index": command_index, "data": {"stdout": "sparse"}}]
    assert event.to_dict() == original


def test_shell_flat_array_does_not_establish_command_grouping_or_seed_progress() -> None:
    source = shell_output()
    source["output"].append(deepcopy(source["output"][0]))
    source["output"][1]["stdout"] = "another-whole-item-row"
    acc = seeded(source)
    acc.add_event(
        typed(
            events.ResponseShellCallOutputContentWsDelta,
            "response.shell_call_output_content.delta",
            output_index=INDEX,
            item_id=ITEM_ID,
            command_index=1,
            delta={"stdout": "observed"},
        )
    )
    assert row(acc)["item"]["output"] == source["output"]
    assert row(acc)["shell_output"] == [{"command_index": 1, "data": {"stdout": "observed"}}]


@pytest.mark.parametrize("target", ["absent", "wrong_id", "wrong_kind", "retired_id"])
def test_rich_progress_cannot_create_or_replace_an_unrelated_item(target: str) -> None:
    acc = seeded(reasoning())
    item_id = ITEM_ID
    if target == "absent":
        output_index = INDEX + 1
    else:
        output_index = INDEX
    if target == "wrong_id":
        item_id = "other_item"
    elif target == "wrong_kind":
        acc.add_event(
            typed(
                events.ResponseOutputItemWsDone,
                "response.output_item.done",
                output_index=INDEX,
                item=item("message", role="assistant", status="completed", content=[]),
            )
        )
    elif target == "retired_id":
        replacement = reasoning()
        replacement["id"] = "replacement_item"
        acc.add_event(
            typed(events.ResponseOutputItemWsDone, "response.output_item.done", output_index=INDEX, item=replacement)
        )
    before = acc.detailed_snapshot()
    acc.add_event(
        typed(
            events.ResponseReasoningSummaryTextWsDelta,
            "response.reasoning_summary_text.delta",
            output_index=output_index,
            item_id=item_id,
            summary_index=0,
            delta="must-not-apply",
        )
    )
    assert acc.detailed_snapshot() == before
