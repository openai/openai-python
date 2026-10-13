from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, cast

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.responses import Response
from openai.lib.responses_tool_runner import (
    ToolRunnerError,
    RegisteredFunction,
    ResponsesToolLedger,
    ResponsesToolRunner,
    AsyncRegisteredFunction,
    ResponsesToolCheckpoint,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)
from openai.resources.responses.responses import Responses, AsyncResponses
from openai.types.responses.response_output_item import McpApprovalRequest
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

from .test_responses_tool_runner import TOOL, FINAL, PARAMS, fn, run, sse, resp, iteration, next_turn


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "fields,valid",
    [
        ({}, True),
        ({"description": None}, True),
        ({"description": "Read a local fixture"}, True),
        ({"description": 3}, False),
        ({"description": False}, False),
        ({"description": {"text": "read"}}, False),
    ],
)
async def test_native_mcp_list_metadata_before_sibling(
    lane: str, fields: dict[str, object], valid: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    listed: dict[str, object] = {
        "type": "mcp_list_tools",
        "id": "listed",
        "server_label": "desk",
        "tools": [{"name": "read", "input_schema": {}, "annotations": ["free", 1, None], **fields}],
    }
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "tools": [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}],
            "tool_choice": {"type": "allowed_tools", "mode": "auto", "tools": [{"type": "function", "name": "record"}]},
        },
    )
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    approvals: list[str] = []

    def approve(item: McpApprovalRequest) -> bool:
        approvals.append(item.id)
        return True

    # Preserve an untyped custom client's native value across Pydantic versions.
    sync_create, async_create = Responses.create, AsyncResponses.create

    def preserve(response: Response) -> Response:
        for item in response.output:
            if item.type == "mcp_list_tools" and "description" in fields:
                object.__setattr__(item.tools[0], "description", fields["description"])
        return response

    def create(self: Responses, *args: Any, **kwargs: Any) -> Response:
        return preserve(sync_create(self, *args, **kwargs))

    async def acreate(self: AsyncResponses, *args: Any, **kwargs: Any) -> Response:
        return preserve(await async_create(self, *args, **kwargs))

    monkeypatch.setattr(Responses, "create", create)
    monkeypatch.setattr(AsyncResponses, "create", acreate)

    result = run(
        lane,
        None,
        [resp([fn("record", "local", text="permitted"), listed], "first"), FINAL],
        requests,
        params=params,
        effects=effects,
        approve_mcp=approve,
    )
    if valid:
        await result
        assert effects == ["permitted"] and len(requests) == 2
        assert any(item.get("type") == "mcp_list_tools" for item in requests[1]["input"])
        assert not any(item.get("type") == "mcp_call" for item in requests[1]["input"])
    else:
        with pytest.raises(ToolRunnerError):
            await result
        assert effects == [] and len(requests) == 1
    assert approvals == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream,eager", [(False, False), (True, False), (True, True)])
@pytest.mark.parametrize(
    "choice,allowed,allowed_tools",
    [
        ("none", False, None),
        ({"type": "mcp", "server_label": "other"}, False, None),
        ({"type": "mcp", "server_label": "desk", "name": "write"}, False, None),
        ({"type": "web_search_preview"}, False, None),
        ({"type": "mcp", "server_label": "desk", "name": "read"}, True, None),
        ({"type": "mcp", "server_label": "desk", "name": None}, True, None),
        ({"type": "mcp", "server_label": "desk"}, True, None),
        (
            {
                "type": "allowed_tools",
                "mode": "auto",
                "tools": [
                    {"type": "mcp", "server_label": "desk", "name": "write"},
                    {"type": "mcp", "server_label": "desk", "name": "read"},
                ],
            },
            True,
            None,
        ),
        ("auto", True, None),
        ("auto", False, []),
        ("auto", False, ["write"]),
        ("auto", True, ["read"]),
        ("auto", False, {"tool_names": []}),
        ("auto", False, {"tool_names": ["write"]}),
        ("auto", True, {"tool_names": ["read"]}),
        ("auto", True, {"read_only": True}),
    ],
)
async def test_mcp_approval_tool_choice(
    lane: str, stream: bool, eager: bool, choice: object, allowed: bool, allowed_tools: object
) -> None:
    approval: dict[str, object] = {
        "type": "mcp_approval_request",
        "id": "approval",
        "server_label": "desk",
        "name": "read",
        "arguments": "{}",
    }
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "tools": [
                {
                    "type": "mcp",
                    "server_label": "desk",
                    "server_url": "https://fixture.invalid/mcp",
                    "allowed_tools": allowed_tools,
                }
            ],
            "tool_choice": choice,
        },
    )
    requests: list[dict[str, Any]] = []
    approvals: list[str] = []

    def approve(item: McpApprovalRequest) -> bool:
        approvals.append(item.id)
        return True

    result = run(
        lane,
        None,
        [resp([approval], "first"), FINAL],
        requests,
        params=params,
        stream=stream,
        eager=eager,
        approve_mcp=approve,
    )
    if allowed:
        await result
        assert approvals == ["approval"]
        assert {"type": "mcp_approval_response", "approval_request_id": "approval", "approve": True} in requests[1][
            "input"
        ]
    else:
        with pytest.raises(ToolRunnerError):
            await result
        assert approvals == []
    assert len(requests) == (2 if allowed else 1)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream,eager", [(False, False), (True, False), (True, True)])
@pytest.mark.parametrize(
    "policy,is_request,allowed",
    [
        ("default", False, False),
        (None, False, False),
        ("always", False, False),
        ("never", True, False),
        ("never", False, True),
        (None, True, True),
        ("always", True, True),
        ({"always": {"tool_names": ["read"]}}, False, False),
        ({"never": {"tool_names": ["read"]}}, True, False),
        ({"never": {"tool_names": ["read"]}}, False, True),
        ({"never": {"tool_names": ["write"]}}, False, False),
        ({"always": {"tool_names": ["write"]}}, False, True),
        ({"always": {"tool_names": ["write"]}}, True, False),
        ({"always": {"read_only": True}}, False, True),
        ({"always": {}}, False, False),
        ({"always": {}}, True, True),
        ({"never": {}}, False, True),
        ({"never": {}}, True, False),
        ({"always": {"tool_names": ["read"]}, "never": {"tool_names": ["read"]}}, False, True),
    ],
)
async def test_declared_mcp_approval_rules(
    lane: str, stream: bool, eager: bool, policy: object, is_request: bool, allowed: bool
) -> None:
    remote: dict[str, object] = {
        "type": "mcp_approval_request" if is_request else "mcp_call",
        "id": "remote",
        "server_label": "desk",
        "name": "read",
        "arguments": "{}",
    }
    if not is_request:
        remote["status"] = "completed"
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "tools": [
                {
                    "type": "mcp",
                    "server_label": "desk",
                    "server_url": "https://fixture.invalid/mcp",
                    **({"require_approval": policy} if policy != "default" else {}),
                }
            ],
        },
    )
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    approvals: list[str] = []

    def approve(item: McpApprovalRequest) -> bool:
        approvals.append(item.id)
        return True

    result = run(
        lane,
        None,
        [resp([remote, fn("record", "record", text="saved")], "first"), FINAL],
        requests,
        params=params,
        effects=effects,
        stream=stream,
        eager=eager,
        approve_mcp=approve,
    )
    if allowed:
        await result
        assert effects == ["saved"]
        assert approvals == (["remote"] if is_request else [])
    else:
        with pytest.raises(ToolRunnerError):
            await result
        assert effects == [] and approvals == []
    assert len(requests) == (2 if allowed else 1)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream,eager", [(False, False), (True, False), (True, True)])
@pytest.mark.parametrize(
    "scenario",
    ["same-output", "previous-output", "saved-history", "repeated-history", "single-grant", "independent-grants"],
)
async def test_mcp_grant_used_once(lane: str, stream: bool, eager: bool, scenario: str) -> None:
    approval: dict[str, object] = {
        "type": "mcp_approval_request",
        "id": "approval",
        "server_label": "desk",
        "name": "read",
        "arguments": "{}",
    }
    receipt: dict[str, object] = {"type": "mcp_approval_response", "approval_request_id": "approval", "approve": True}
    remote: dict[str, object] = {
        "type": "mcp_call",
        "id": "remote",
        "server_label": "desk",
        "name": "read",
        "arguments": "{}",
        "approval_request_id": "approval",
        "status": "completed",
    }
    history: list[dict[str, object]] = [dict(approval), receipt]
    second = {**remote, "id": "remote_second"}
    output: list[dict[str, object]] = [second, fn("record", "record", text="saved")]
    if scenario == "same-output":
        output.insert(0, dict(remote))
    elif scenario == "previous-output":
        history.append(dict(remote))
    elif scenario == "saved-history":
        history.extend([dict(remote), second])
        output = [fn("record", "record", text="saved")]
    elif scenario == "repeated-history":
        history.extend([dict(remote), dict(approval), receipt])
    elif scenario == "independent-grants":
        next_approval = {**approval, "id": "approval_second"}
        history.extend([dict(next_approval), {**receipt, "approval_request_id": next_approval["id"]}])
        output = [
            dict(remote),
            {**second, "approval_request_id": next_approval["id"]},
            fn("record", "record", text="saved"),
        ]
    original = deepcopy(history)
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    approvals: list[str] = []
    writes: list[ResponsesToolCheckpoint] = []
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "input": history,
            "tools": [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}],
        },
    )

    def approve(item: McpApprovalRequest) -> bool:
        approvals.append(item.id)
        return True

    result = run(
        lane,
        None,
        [resp(output, "first"), FINAL],
        requests,
        params=params,
        effects=effects,
        stream=stream,
        eager=eager,
        approve_mcp=approve,
        save=writes.append if scenario == "saved-history" else None,
    )
    if scenario in ("single-grant", "independent-grants"):
        await result
        assert effects == ["saved"] and len(requests) == 2
    else:
        with pytest.raises((ToolRunnerError, ValueError)):
            await result
        assert effects == [] and writes == []
        assert len(requests) == (0 if scenario in ("saved-history", "repeated-history") else 1)
    expected = (
        ["approval", "approval_second"]
        if scenario == "independent-grants"
        else ["approval"]
        if scenario in ("single-grant", "same-output")
        else []
    )
    assert approvals == expected and history == original


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("mode", ["ordinary", "budget", "ledger"])
@pytest.mark.parametrize("decision", ["allow", "deny", "missing", "invalid"])
async def test_imported_mcp_grant_before_save_or_request(lane: str, mode: str, decision: str) -> None:
    history = [
        {"type": "mcp_approval_request", "id": "approval", "server_label": "desk", "name": "read", "arguments": "{}"},
        {"type": "mcp_approval_response", "approval_request_id": "approval", "approve": True},
        {"role": "user", "content": "continue"},
    ]
    original = deepcopy(history)
    requests: list[dict[str, Any]] = []
    writes: list[ResponsesToolCheckpoint] = []
    approvals: list[str] = []
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "input": history,
            "tools": [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}],
        },
    )

    def approve(item: McpApprovalRequest) -> bool:
        assert requests == [] and writes == []
        approvals.append(item.id)
        return cast(bool, "yes" if decision == "invalid" else decision == "allow")

    result = run(
        lane,
        None,
        [FINAL],
        requests,
        params=params,
        save=writes.append if mode == "ledger" else None,
        context_budget={"max_input_bytes": 8000, "max_input_images": 0} if mode == "budget" else None,
        approve_mcp=None if decision == "missing" else approve,
    )
    if decision in ("missing", "invalid"):
        with pytest.raises(ToolRunnerError):
            await result
        assert requests == [] and writes == []
    else:
        await result
        expected = {"type": "mcp_approval_response", "approval_request_id": "approval", "approve": decision == "allow"}
        assert expected in requests[0]["input"]
        if mode == "ledger":
            assert expected in writes[0]["history"]
    assert approvals == ([] if decision == "missing" else ["approval"])
    assert history == original


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("field", ["type", "server_label"])
async def test_mcp_declaration_fields_before_transport(lane: str, field: str) -> None:
    declaration = {"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}
    del declaration[field]
    requests: list[dict[str, Any]] = []
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "tools": [declaration]})
    with pytest.raises((ValueError, KeyError)):
        await run(lane, None, [FINAL], requests, params=params)
    assert requests == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream,eager", [(False, False), (True, False), (True, True)])
@pytest.mark.parametrize("allowed", [False, True])
async def test_mcp_call_obeys_declared_names(lane: str, stream: bool, eager: bool, allowed: bool) -> None:
    remote: dict[str, object] = {
        "type": "mcp_call",
        "id": "remote",
        "server_label": "desk",
        "name": "read",
        "arguments": "{}",
        "status": "completed",
    }
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "tools": [
                {
                    "type": "mcp",
                    "server_label": "desk",
                    "server_url": "https://fixture.invalid/mcp",
                    "require_approval": "never",
                    "allowed_tools": ["read"] if allowed else ["write"],
                }
            ],
        },
    )
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    result = run(
        lane,
        None,
        [resp([remote, fn("record", "record", text="saved")], "first"), FINAL],
        requests,
        params=params,
        effects=effects,
        stream=stream,
        eager=eager,
    )
    if allowed:
        await result
        assert effects == ["saved"]
    else:
        with pytest.raises(ToolRunnerError):
            await result
        assert effects == []
    assert len(requests) == (2 if allowed else 1)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("consumed", [False, True])
@pytest.mark.parametrize("restriction", ["choice", "declared"])
async def test_mcp_approval_tool_choice_on_resume(lane: str, consumed: bool, restriction: str) -> None:
    approval: dict[str, object] = {
        "type": "mcp_approval_request",
        "id": "approval",
        "server_label": "desk",
        "name": "read",
        "arguments": "{}",
    }
    remote = {**approval, "type": "mcp_call", "id": "remote", "approval_request_id": "approval", "status": "completed"}
    params: ResponseCreateParamsNonStreaming = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "tools": [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}],
        },
    )
    replies = [resp([approval, fn("record", "first", text="once")], "first")]
    if consumed:
        replies.append(resp([remote, fn("record", "second", text="twice")], "second"))
    replies.append(FINAL)
    saved: list[ResponsesToolCheckpoint] = []
    await run(lane, None, replies, [], params=params, save=saved.append, approve_mcp=lambda _: True)
    boundary = next(
        value
        for value in saved
        if value["phase"] == "boundary" and len(value["returned_call_ids"]) == (3 if consumed else 2)
    )
    if restriction == "declared":
        for declaration in boundary["tools"]:
            if declaration["type"] == "mcp":
                declaration["allowed_tools"] = ["write"]
        params = {
            **params,
            "tools": [
                {
                    "type": "mcp",
                    "server_label": "desk",
                    "server_url": "https://fixture.invalid/mcp",
                    "allowed_tools": ["write"],
                }
            ],
        }
    requests: list[dict[str, Any]] = []
    updated: list[ResponsesToolCheckpoint] = []
    approvals: list[str] = []

    def approve(item: McpApprovalRequest) -> bool:
        approvals.append(item.id)
        return True

    result = run(
        lane,
        None,
        [FINAL],
        requests,
        params={**params, "input": "new observation", "tool_choice": "auto" if restriction == "declared" else "none"},
        save=updated.append,
        resume=boundary,
        approve_mcp=approve,
    )
    if consumed:
        await result
        assert remote in requests[0]["input"]
    else:
        with pytest.raises(ToolRunnerError):
            await result
        assert updated == []
    assert approvals == []
    assert len(requests) == (1 if consumed else 0)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("kind", ["mcp_approval_request", "mcp_call", "mcp_list_tools"])
async def test_mcp_output_requires_server_label(lane: str, kind: str) -> None:
    item: dict[str, object] = {
        "type": kind,
        "id": "mcp",
        "name": "record",
        "arguments": "{}",
        "status": "completed",
        "tools": [],
    }
    params: ResponseCreateParamsNonStreaming = {
        **PARAMS,
        "tools": [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}],
    }
    async with iteration(lane, resp([item, fn("record", "one", text="never")], "first"), params=params) as rig:
        turns, _desktop, _computer, effects, requests, _closed = rig
        with pytest.raises(ToolRunnerError):
            await next_turn(turns)
        assert not effects and len(requests) == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("labels", [[""], ["desk", "desk"]])
async def test_mcp_declarations_require_nonempty_unique_labels(lane: str, labels: list[str]) -> None:
    params: ResponseCreateParamsNonStreaming = {
        **PARAMS,
        "tools": [
            {"type": "mcp", "server_label": label, "server_url": "https://fixture.invalid/mcp"} for label in labels
        ],
    }
    async with iteration(lane, FINAL, params=params) as rig:
        turns, _desktop, _computer, effects, requests, _closed = rig
        with pytest.raises(ValueError, match="labels"):
            await next_turn(turns)
        assert not effects and not requests


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_duplicate_mcp_request_id_cannot_replace_approved_action(lane: str) -> None:
    approval = {
        "type": "mcp_approval_request",
        "id": "approve",
        "server_label": "desk",
        "name": "record",
        "arguments": "{}",
    }
    changed = {**approval, "arguments": '{"changed":true}'}
    receipt = {"type": "mcp_approval_response", "approval_request_id": "approve", "approve": True}
    executed: dict[str, object] = {
        **changed,
        "type": "mcp_call",
        "id": "remote",
        "approval_request_id": "approve",
        "status": "completed",
    }
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "input": [approval, receipt, changed, receipt],
            "tools": [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}],
        },
    )
    async with iteration(lane, resp([executed, fn("record", "one", text="never")], "first"), params=params) as rig:
        turns, _desktop, _computer, effects, requests, _closed = rig
        with pytest.raises(ToolRunnerError):
            await next_turn(turns)
        assert effects == [] and requests == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("automatic", [False, True])
async def test_nonledger_mcp_requests_do_not_retry(lane: str, automatic: bool) -> None:
    requests: list[dict[str, Any]] = []
    params: ResponseCreateParamsNonStreaming = {
        **PARAMS,
        "tools": [{"type": "mcp", "server_label": "desk", "server_url": "https://fixture.invalid/mcp"}],
    }
    approval: dict[str, object] = {
        "type": "mcp_approval_request",
        "id": "approval_one",
        "server_label": "desk",
        "name": "record",
        "arguments": "{}",
    }

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        if len(requests) == 1 and not automatic:
            return httpx2.Response(200, json=resp([approval], "first"))
        return httpx2.Response(500, json={"error": {"message": "synthetic failure"}})

    if lane == "sync":
        with OpenAI(
            api_key="fixture", max_retries=1, http_client=httpx2.Client(transport=httpx2.MockTransport(handler))
        ) as client:
            with pytest.raises(ToolRunnerError):
                ResponsesToolRunner().run(client, params, approve_mcp=lambda _: True)
    else:

        async def approve(_item: McpApprovalRequest) -> bool:
            return True

        async with AsyncOpenAI(
            api_key="fixture", max_retries=1, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            with pytest.raises(ToolRunnerError):
                await AsyncResponsesToolRunner().run(client_async, params, approve_mcp=approve)
    assert len(requests) == (1 if automatic else 2)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("status", ["in_progress", "incomplete"])
async def test_unfinished_message_prevents_deferred_sibling_effects(lane: str, status: str) -> None:
    first = resp(
        [
            fn("record", "one", text="later"),
            {
                "id": "message_one",
                "type": "message",
                "role": "assistant",
                "status": status,
                "content": [{"type": "output_text", "text": "waiting", "annotations": []}],
            },
        ],
        "first",
    )
    async with iteration(lane, first) as rig:
        turns, _desktop, _computer, effects, requests, _closed = rig
        with pytest.raises(ToolRunnerError):
            await next_turn(turns)
        assert effects == [] and len(requests) == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("automatic", [False, True], ids=["approved-continuation", "automatic-first"])
async def test_lost_mcp_response_cannot_resume_admitted_transport(lane: str, automatic: bool) -> None:
    requests: list[dict[str, Any]] = []
    saved: list[ResponsesToolCheckpoint] = []
    approvals: list[str] = []
    params: ResponseCreateParamsNonStreaming = {
        **PARAMS,
        "tools": [
            {
                "type": "mcp",
                "server_label": "desk",
                "server_url": "https://fixture.invalid/mcp",
                "require_approval": "never" if automatic else "always",
            }
        ],
    }
    approval: dict[str, object] = {
        "type": "mcp_approval_request",
        "id": "approval_one",
        "server_label": "desk",
        "name": "record",
        "arguments": "{}",
    }

    def approve(item: McpApprovalRequest) -> bool:
        approvals.append(item.id)
        return True

    async def aapprove(item: McpApprovalRequest) -> bool:
        return approve(item)

    async def save(checkpoint: ResponsesToolCheckpoint) -> None:
        saved.append(checkpoint)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        if len(requests) == 1 and not automatic:
            return httpx2.Response(200, json=resp([approval], "first"))
        raise httpx2.ReadError("synthetic lost response")

    if lane == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            runner = ResponsesToolRunner()
            with pytest.raises(ToolRunnerError):
                runner.run(client, params, approve_mcp=approve, ledger=ResponsesToolLedger("mcp", saved.append))
            assert saved[-1]["phase"] == "pending"
            with pytest.raises(ValueError):
                runner.run(
                    client, params, approve_mcp=approve, ledger=ResponsesToolLedger("mcp", saved.append, saved[-1])
                )
    else:
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            runner_async = AsyncResponsesToolRunner()
            with pytest.raises(ToolRunnerError):
                await runner_async.run(
                    client_async, params, approve_mcp=aapprove, ledger=AsyncResponsesToolLedger("mcp", save)
                )
            assert saved[-1]["phase"] == "pending"
            with pytest.raises(ValueError):
                await runner_async.run(
                    client_async, params, approve_mcp=aapprove, ledger=AsyncResponsesToolLedger("mcp", save, saved[-1])
                )
    assert len(requests) == (1 if automatic else 2)
    assert approvals == ([] if automatic else ["approval_one"])


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_stateless_image_generation_stops_before_requests_or_effects(lane: str) -> None:
    params: ResponseCreateParamsNonStreaming = {**PARAMS, "tools": [{"type": "image_generation"}]}
    image: dict[str, object] = {"type": "image_generation_call", "id": "image", "status": "completed", "result": None}
    async with iteration(lane, resp([image, fn("record", "one", text="effect")], "first"), params=params) as rig:
        turns, _desktop, _computer, effects, requests, _closed = rig
        with pytest.raises(ValueError, match="stored responses"):
            await next_turn(turns)
        assert effects == [] and requests == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("server", ["code_interpreter", "image_generation", "web_search_preview"])
@pytest.mark.parametrize("status", ["completed", "failed", "in_progress"])
async def test_server_tools_replay_only_declared_completed_output(
    lane: str, stream: bool, server: str, status: str
) -> None:
    effects: list[str] = []
    requests: list[dict[str, Any]] = []
    saved: list[ResponsesToolCheckpoint] = []
    item: dict[str, object]
    if server == "code_interpreter":
        declaration: dict[str, object] = {"type": server, "container": "container-original"}
        item = {
            "type": "code_interpreter_call",
            "id": "ci-1",
            "container_id": "container-original",
            "status": status,
            "code": "synthetic",
            "outputs": [],
        }
    elif server == "image_generation":
        declaration = {"type": server}
        item = {"type": "image_generation_call", "id": "img-1", "status": status, "result": "synthetic-png"}
    else:
        declaration = {"type": server}
        item = {
            "type": "web_search_call",
            "id": "web-1",
            "status": status,
            "action": {"type": "search", "query": "synthetic"},
        }
    params = cast(
        ResponseCreateParamsNonStreaming, {**PARAMS, "store": server == "image_generation", "tools": [declaration]}
    )

    def record(_args: dict[str, object]) -> str:
        effects.append("record")
        return "done"

    async def arecord(args: dict[str, object]) -> str:
        return record(args)

    async def save(checkpoint: ResponsesToolCheckpoint) -> None:
        saved.append(checkpoint)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        reply = resp([item, fn("record", "f1", text="later")], "r1") if len(requests) == 1 else FINAL
        if stream:
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(reply))
        return httpx2.Response(200, json=reply)

    if lane == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            runner = ResponsesToolRunner(functions=[RegisteredFunction(TOOL, record)])
            if status == "completed":
                runner.run(client, params, stream=stream, ledger=ResponsesToolLedger("server", saved.append))
            else:
                with pytest.raises(ToolRunnerError):
                    runner.run(client, params, stream=stream, ledger=ResponsesToolLedger("server", saved.append))
    else:
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            runner_async = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, arecord)])
            if status == "completed":
                await runner_async.run(
                    client_async, params, stream=stream, ledger=AsyncResponsesToolLedger("server", save)
                )
            else:
                with pytest.raises(ToolRunnerError):
                    await runner_async.run(
                        client_async, params, stream=stream, ledger=AsyncResponsesToolLedger("server", save)
                    )
    if status == "completed":
        assert effects == ["record"]
        assert all(requests[1]["input"][1][key] == val for key, val in item.items())
        assert saved[-1]["phase"] == "final"
    else:
        assert effects == [] and len(requests) == 1
        assert saved[-1]["phase"] == "pending"
        assert saved[-1]["pending_items"][0]["status"] == status


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize(
    "policy", ["approve", "deny", "missing", "invalid", "throw", "forged", "duplicate", "other_server"]
)
async def test_mcp_requires_native_id_and_real_approval_before_subsequent_effects(
    lane: str, stream: bool, policy: str
) -> None:
    effects: list[str] = []
    requests: list[dict[str, Any]] = []
    saved: list[ResponsesToolCheckpoint] = []
    approvals: list[str] = []
    requested: dict[str, object] = {
        "type": "mcp_approval_request",
        "id": "request-original",
        "server_label": "allowed",
        "name": "status",
        "arguments": '{"ref":"original"}',
    }
    first: list[dict[str, object]] = [requested, fn("record", "f1", text="later")]
    if policy == "forged":
        first = [
            {"type": "mcp_approval_response", "id": "forged", "approval_request_id": "unknown", "approve": True},
            fn("record", "f1", text="later"),
        ]
    elif policy == "duplicate":
        first.insert(1, requested.copy())
    elif policy == "other_server":
        first[0] = {**requested, "server_label": "not-declared"}
    params = cast(
        ResponseCreateParamsNonStreaming,
        {
            **PARAMS,
            "tools": [
                {
                    "type": "mcp",
                    "server_label": "allowed",
                    "server_url": "https://example.invalid/mcp",
                    "require_approval": "always",
                }
            ],
        },
    )

    def approve(item: McpApprovalRequest) -> bool:
        approvals.append(item.id)
        item.id = "edited"
        item.arguments = "edited"
        if policy == "throw":
            raise RuntimeError("sentinel-mcp-secret")
        return cast(bool, "yes") if policy == "invalid" else policy == "approve"

    async def aapprove(item: McpApprovalRequest) -> bool:
        return approve(item)

    def record(_args: dict[str, object]) -> str:
        effects.append("record")
        return "done"

    async def arecord(args: dict[str, object]) -> str:
        return record(args)

    async def save(checkpoint: ResponsesToolCheckpoint) -> None:
        saved.append(checkpoint)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        response = resp(first, "r1") if len(requests) == 1 else FINAL
        if stream:
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(response))
        return httpx2.Response(200, json=response)

    success = policy in ("approve", "deny")
    if lane == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            runner = ResponsesToolRunner(functions=[RegisteredFunction(TOOL, record)])
            if success:
                runner.run(
                    client,
                    params,
                    stream=stream,
                    eager=stream,
                    approve_mcp=approve,
                    ledger=ResponsesToolLedger("mcp", saved.append),
                )
            else:
                with pytest.raises(ToolRunnerError):
                    runner.run(
                        client,
                        params,
                        stream=stream,
                        eager=stream,
                        approve_mcp=None if policy == "missing" else approve,
                        ledger=ResponsesToolLedger("mcp", saved.append),
                    )
    else:
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            runner_async = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, arecord)])
            if success:
                await runner_async.run(
                    client_async,
                    params,
                    stream=stream,
                    eager=stream,
                    approve_mcp=aapprove,
                    ledger=AsyncResponsesToolLedger("mcp", save),
                )
            else:
                with pytest.raises(ToolRunnerError):
                    await runner_async.run(
                        client_async,
                        params,
                        stream=stream,
                        eager=stream,
                        approve_mcp=None if policy == "missing" else aapprove,
                        ledger=AsyncResponsesToolLedger("mcp", save),
                    )
    if success:
        assert approvals == ["request-original"]
        assert effects == ["record"]
        assert requests[1]["input"][-2] == {
            "type": "mcp_approval_response",
            "approval_request_id": "request-original",
            "approve": policy == "approve",
        }
        assert requests[1]["input"][1]["arguments"] == '{"ref":"original"}'
        assert saved[-1]["phase"] == "final"
    else:
        assert effects == [] and len(requests) == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("durable", [False, True])
@pytest.mark.parametrize("status", ["completed", "failed"])
async def test_eager_local_action_waits_for_late_server_terminal_status(lane: str, durable: bool, status: str) -> None:
    effects: list[str] = []
    requests: list[dict[str, Any]] = []
    saved: list[ResponsesToolCheckpoint] = []
    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "store": True, "tools": [{"type": "image_generation"}]})
    server: dict[str, object] = {
        "type": "image_generation_call",
        "id": "img-late",
        "status": status,
        "result": "synthetic",
    }

    def record(_args: dict[str, object]) -> str:
        effects.append("record")
        return "done"

    async def arecord(args: dict[str, object]) -> str:
        return record(args)

    async def save(checkpoint: ResponsesToolCheckpoint) -> None:
        saved.append(checkpoint)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        first = resp([fn("record", "first", text="would mutate"), server], "r1")
        reply = first if len(requests) == 1 else FINAL
        return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(reply))

    async def exercise() -> None:
        if lane == "sync":
            with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                ResponsesToolRunner(functions=[RegisteredFunction(TOOL, record)]).run(
                    client,
                    params,
                    stream=True,
                    eager=True,
                    ledger=ResponsesToolLedger("late", saved.append) if durable else None,
                )
        else:
            async with AsyncOpenAI(
                api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
            ) as client_async:
                await AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, arecord)]).run(
                    client_async,
                    params,
                    stream=True,
                    eager=True,
                    ledger=AsyncResponsesToolLedger("late", save) if durable else None,
                )

    if status == "completed":
        await exercise()
        assert effects == ["record"]
        assert requests[1]["input"][-1]["call_id"] == "first"
    else:
        with pytest.raises(ToolRunnerError) as failure:
            await exercise()
        assert failure.value.attempted_call_ids == ()
        assert effects == [] and len(requests) == 1
        if durable:
            assert saved[-1]["phase"] == "pending"
            assert saved[-1]["pending_items"][-1]["status"] == "failed"


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_declared_server_does_not_allow_eager_without_stream(lane: str) -> None:
    requests: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request.url.path)
        return httpx2.Response(200, json=FINAL)

    params = cast(ResponseCreateParamsNonStreaming, {**PARAMS, "tools": [{"type": "web_search"}]})
    with pytest.raises(ValueError, match="requires streaming"):
        if lane == "sync":
            with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                ResponsesToolRunner().run(client, params, eager=True)
        else:
            async with AsyncOpenAI(
                api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
            ) as client_async:
                await AsyncResponsesToolRunner().run(client_async, params, eager=True)
    assert requests == []
