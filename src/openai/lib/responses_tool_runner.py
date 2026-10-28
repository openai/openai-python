"""A bounded Responses loop for browser, computer and registered function tools."""

from __future__ import annotations

import json
import math
import asyncio
import hashlib
from copy import copy, deepcopy
from time import monotonic
from typing import TypeVar, Callable, Awaitable, cast
from inspect import isawaitable, iscoroutine
from functools import partial
from contextvars import copy_context
from dataclasses import field, dataclass
from collections.abc import Mapping, Generator, AsyncGenerator
from typing_extensions import Literal, Required, TypeAlias, TypedDict
from concurrent.futures import Future, ThreadPoolExecutor

import pydantic

from .. import OpenAI, AsyncOpenAI
from ._tools import ResponsesPydanticFunctionTool
from .._types import Headers, omit
from .._utils import is_given, transform
from .browser import BrowserToolset, AsyncBrowserToolset, _legacy_state_url
from .._compat import model_copy
from .._models import validate_type, construct_type_unchecked
from .computer import (
    ComputerToolset,
    ComputerUseError,
    ComputerActionInput,
    AsyncComputerToolset,
    _actions as _computer_actions,
    _snapshot_call as _snapshot_computer_call,
    _snapshot_request,
    _snapshot_response as _snapshot_computer_response,
    _valid_native_message,
    _valid_native_reasoning,
)
from ._tool_lifecycle import CloseStatus, ToolLifecycle, invoke, rotated_idempotency_headers
from ..types.responses import (
    Response,
    ResponseComputerToolCall,
    ResponseFunctionToolCall,
)
from .tool_diagnostics import ToolDiagnosticObserver, emit_tool_diagnostic
from ._parsing._responses import parse_function_tool_arguments
from ..types.responses.tool_param import ToolParam, FunctionToolParam
from .streaming.responses._events import ResponseStreamEvent
from .streaming.responses._responses import ResponseStream, AsyncResponseStream
from ..types.responses.response_input_param import ComputerCallOutput, FunctionCallOutput, ResponseInputParam
from ..types.responses.response_output_item import McpCall, McpApprovalRequest, ResponseOutputItem
from ..types.responses.response_create_params import ResponseCreateParamsStreaming, ResponseCreateParamsNonStreaming
from ..types.responses.response_output_message import ResponseOutputMessage
from ..types.responses.response_input_item_param import McpApprovalResponse
from ..types.responses.response_function_call_output_item_list_param import ResponseFunctionCallOutputItemListParam

__all__ = [
    "RegisteredFunction",
    "AsyncRegisteredFunction",
    "ResponsesToolRunner",
    "AsyncResponsesToolRunner",
    "EarlyExecution",
    "ContextBudget",
    "AsyncContextBudget",
    "ContextBudgetSnapshot",
    "ContextBudgetDecision",
    "ResponsesRunnerTurn",
    "ResponsesToolCheckpoint",
    "ResponsesToolLedger",
    "AsyncResponsesToolLedger",
    "ToolRunnerError",
    "ToolRunnerCancelledError",
]

FunctionResult: TypeAlias = str | ResponseFunctionCallOutputItemListParam
ToolOutput: TypeAlias = FunctionCallOutput | ComputerCallOutput | McpApprovalResponse
_ModelT = TypeVar("_ModelT", bound=pydantic.BaseModel)


def _ledger_tools(tools: list[ToolParam]) -> list[ToolParam]:
    result: list[ToolParam] = []
    for tool in tools:
        if tool["type"] == "code_interpreter" and not isinstance(tool["container"], str):
            container = tool["container"]
            policy = container.get("network_policy")
            if (
                policy is not None
                and policy["type"] == "allowlist"
                and "domain_secrets" in policy
                and cast(object, policy["domain_secrets"]) is not None
            ):
                result.append(
                    {
                        **tool,
                        "container": {
                            **container,
                            "network_policy": {
                                **policy,
                                "domain_secrets": [{**secret, "value": ""} for secret in policy["domain_secrets"]],
                            },
                        },
                    }
                )
                continue
        if tool["type"] != "mcp":
            result.append(tool)
            continue
        registry = {key: value for key, value in tool.items() if key not in ("authorization", "headers")}
        url = registry.get("server_url")
        if isinstance(url, str):
            registry["server_url"] = "sha256:" + hashlib.sha256(_legacy_state_url(url).encode("utf-8")).hexdigest()
        result.append(cast(ToolParam, registry))
    return result


_SERVER_ITEMS: dict[str, frozenset[str]] = {
    "web_search_call": frozenset(
        {"web_search", "web_search_2025_08_26", "web_search_preview", "web_search_preview_2025_03_11"}
    ),
    "file_search_call": frozenset({"file_search"}),
    "code_interpreter_call": frozenset({"code_interpreter"}),
    "image_generation_call": frozenset({"image_generation"}),
    "mcp_call": frozenset({"mcp"}),
    "mcp_list_tools": frozenset({"mcp"}),
    "mcp_approval_request": frozenset({"mcp"}),
}
_SERVER_TOOLS = frozenset(kind for kinds in _SERVER_ITEMS.values() for kind in kinds)


def _validate_server_item(item: dict[str, object], tools: list[ToolParam]) -> None:
    kind = cast(str, item.get("type"))
    declared = _SERVER_ITEMS.get(kind, frozenset())
    matching = [tool for tool in tools if tool["type"] in declared]
    if not matching:
        raise ValueError("A server tool was not declared for this run.")
    if kind.startswith("mcp_"):
        label = item.get("server_label")
        if (
            type(label) is not str
            or not label
            or not any(tool["type"] == "mcp" and tool["server_label"] == label for tool in matching)
        ):
            raise ValueError("MCP item requires its declared server label.")
    if item.get("status") not in (None, "completed") or item.get("error") is not None:
        raise ValueError("A server tool did not complete; stop before dependent local effects.")
    if type(item.get("id")) is not str:
        raise ValueError("A server tool requires its native ID before replay.")
    valid = True
    if kind == "web_search_call":
        raw_action = item.get("action")
        action = cast(dict[str, object], raw_action) if isinstance(raw_action, dict) else None
        valid = item.get("status") == "completed" and action is not None
        if valid and action is not None:
            if action.get("type") == "search":
                queries = action.get("queries")
                sources = action.get("sources")
                valid = (
                    ("query" not in action or type(action["query"]) is str)
                    and (
                        "queries" not in action
                        or (
                            isinstance(queries, list)
                            and all(type(query) is str for query in cast(list[object], queries))
                        )
                    )
                    and ("sources" not in action or isinstance(sources, list))
                )
                if valid and isinstance(sources, list):
                    for source in cast(list[object], sources):
                        if not isinstance(source, dict):
                            valid = False
                            break
                        entry = cast(dict[str, object], source)
                        if entry.get("type") != "url" or type(entry.get("url")) is not str:
                            valid = False
                            break
            elif action.get("type") == "open_page":
                url = action.get("url")
                valid = url is None or type(url) is str
            else:
                valid = (
                    action.get("type") == "find_in_page"
                    and type(action.get("pattern")) is str
                    and type(action.get("url")) is str
                )
    elif kind == "file_search_call":
        queries = item.get("queries")
        results = item.get("results")
        valid = (
            item.get("status") == "completed"
            and isinstance(queries, list)
            and all(type(query) is str for query in cast(list[object], queries))
            and (results is None or isinstance(results, list))
        )
        if valid and isinstance(results, list):
            for result in cast(list[object], results):
                if not isinstance(result, dict):
                    valid = False
                    break
                entry = cast(dict[str, object], result)
                score = entry.get("score")
                attributes = entry.get("attributes")
                valid = (
                    all(key not in entry or type(entry[key]) is str for key in ("file_id", "filename", "text"))
                    and ("score" not in entry or type(score) is int or (type(score) is float and math.isfinite(score)))
                    and (
                        attributes is None
                        or (
                            isinstance(attributes, dict)
                            and all(
                                type(value) in (str, bool, int) or (type(value) is float and math.isfinite(value))
                                for value in cast(dict[str, object], attributes).values()
                            )
                        )
                    )
                )
                if not valid:
                    break
    elif kind == "code_interpreter_call":
        outputs = item.get("outputs")
        valid = (
            item.get("status") == "completed"
            and type(item.get("container_id")) is str
            and any(
                tool["type"] == "code_interpreter"
                and (
                    tool["container"] == item["container_id"]
                    or (isinstance(tool["container"], dict) and tool["container"].get("type") == "auto")
                )
                for tool in matching
            )
            and (
                "code" in item
                and (item["code"] is None or type(item["code"]) is str)
                and "outputs" in item
                and (outputs is None or isinstance(outputs, list))
            )
        )
        if valid and isinstance(outputs, list):
            for output in cast(list[object], outputs):
                if not isinstance(output, dict):
                    valid = False
                    break
                entry = cast(dict[str, object], output)
                if not (
                    (entry.get("type") == "logs" and type(entry.get("logs")) is str)
                    or (entry.get("type") == "image" and type(entry.get("url")) is str)
                ):
                    valid = False
                    break
    elif kind == "image_generation_call":
        image_action = item.get("action")
        background = item.get("background")
        output_format = item.get("output_format")
        quality = item.get("quality")
        prompt = item.get("revised_prompt")
        size = item.get("size")
        valid = (
            item.get("status") == "completed"
            and "result" in item
            and (item["result"] is None or type(item["result"]) is str)
            and image_action in (None, "generate", "edit", "auto")
            and background in (None, "transparent", "opaque", "auto")
            and output_format in (None, "png", "webp", "jpeg")
            and quality in (None, "low", "medium", "high", "xhigh", "max", "auto")
            and (prompt is None or type(prompt) is str)
            and (size is None or type(size) is str)
        )
    elif kind == "mcp_list_tools":
        listed = item.get("tools")
        valid = isinstance(listed, list)
        if isinstance(listed, list):
            for tool in cast(list[object], listed):
                if not isinstance(tool, dict):
                    valid = False
                    break
                entry = cast(dict[str, object], tool)
                description = entry.get("description")
                if (
                    type(entry.get("name")) is not str
                    or "input_schema" not in entry
                    or (description is not None and type(description) is not str)
                ):
                    valid = False
                    break
                _plain(entry)
    elif kind in ("mcp_call", "mcp_approval_request"):
        valid = type(item.get("name")) is str and type(item.get("arguments")) is str
        if kind == "mcp_call":
            output = item.get("output")
            valid = valid and (output is None or type(output) is str)
    if not valid:
        raise ValueError("A server tool requires its native fields before replay.")
    if kind == "mcp_approval_request" and (
        type(item.get("id")) is not str
        or not item["id"]
        or type(item.get("name")) is not str
        or type(item.get("arguments")) is not str
    ):
        raise ValueError("MCP approval requires its ID, name and arguments.")


def _mcp_approval_policy(declaration: Mapping[str, object], name: str) -> Literal["always", "never"] | None:
    policy = declaration.get("require_approval")
    if policy is None:
        return "always"
    if policy == "always":
        return "always"
    if policy == "never":
        return "never"
    if not isinstance(policy, dict):
        return None
    filters = cast(dict[str, object], policy)
    matched: Literal["always", "never"] | None = None
    for rule in ("always", "never"):
        if rule not in filters:
            continue
        raw_filter = filters[rule]
        if not isinstance(raw_filter, dict):
            return None
        tool_filter = cast(dict[str, object], raw_filter)
        names = tool_filter.get("tool_names")
        if "read_only" in tool_filter or ("tool_names" in tool_filter and not isinstance(names, list)):
            return None
        if "tool_names" not in tool_filter or (isinstance(names, list) and name in names):
            if matched is not None:
                return None
            matched = rule
    if matched is not None or ("always" in filters) == ("never" in filters):
        return matched
    return "never" if "always" in filters else "always"


def _validated_mcp_call(item: dict[str, object], approved: dict[str, dict[str, object]]) -> None:
    request_id = item.get("approval_request_id")
    if request_id is None:
        return
    request = approved.get(request_id) if type(request_id) is str else None
    if (
        request is None
        or request.get("server_label") != item.get("server_label")
        or request.get("name") != item.get("name")
        or request.get("arguments") != item.get("arguments")
    ):
        raise ValueError("MCP execution has no matching approved original request.")
    del approved[cast(str, request_id)]


def _approved_mcp_requests(history: ResponseInputParam) -> dict[str, dict[str, object]]:
    requests: dict[str, dict[str, object] | None] = {}
    approved: dict[str, dict[str, object]] = {}
    for item in cast(list[dict[str, object]], history):
        if item.get("type") == "mcp_approval_request" and type(item.get("id")) is str:
            requests.setdefault(cast(str, item["id"]), item)
        elif item.get("type") == "mcp_approval_response" and type(item.get("approve")) is bool:
            request_id = item.get("approval_request_id")
            request = requests.get(request_id) if type(request_id) is str else None
            if request is not None:
                requests[cast(str, request_id)] = None
                if item["approve"] is True:
                    approved[cast(str, request_id)] = request
        elif item.get("type") == "mcp_call":
            _validated_mcp_call(item, approved)
    return approved


class EarlyExecution(TypedDict, total=False):
    """Registered tools permitted to run before full streamed inspection.

    With stream=True and eager=True, the first unselected local tool defers
    every later item until iterator advance. None retains blanket eager mode.
    Timing can be chosen again when resuming a validated ledger boundary; it
    does not grant authority to replay pending effects or bypass approvals.
    """

    functions: list[str]
    computer: bool


class ContextBudgetSnapshot(TypedDict):
    """A detached full native input; eligibility belongs to this request only."""

    history: ResponseInputParam
    eligible_call_ids: list[str]
    input_bytes: int
    input_images: int


class ContextBudgetDecision(TypedDict, total=False):
    drop_call_ids: Required[list[str]]
    summary: str


class _ContextBudgetFields(TypedDict, total=False):
    max_input_bytes: Required[int]
    max_input_images: Required[int]
    keep_recent_screenshots: int


class ContextBudget(_ContextBudgetFields, total=False):
    """Invocation-scoped native input limits, separate from ledger storage."""

    compact: Callable[[ContextBudgetSnapshot], ContextBudgetDecision]


class AsyncContextBudget(_ContextBudgetFields, total=False):
    """Compaction may return immediately or be awaited before request admission."""

    compact: Callable[[ContextBudgetSnapshot], ContextBudgetDecision | Awaitable[ContextBudgetDecision]]


class ResponsesToolCheckpoint(TypedDict):
    """Private replay data. Returned IDs do not prove an external effect.

    Saved MCP tool declarations omit authorization and all custom headers and
    fingerprint server URLs. Resume supplies current credentials; the application must
    verify that these still address the intended remote tenant.
    """

    version: Literal[1]
    run_id: str
    revision: int
    phase: Literal["boundary", "pending", "final"]
    max_steps: int
    consumed_requests: int
    tools: list[ToolParam]
    output_override_names: list[str]
    history: ResponseInputParam
    attempted_call_ids: list[str]
    returned_call_ids: list[str]
    pending_items: list[dict[str, object]]
    returned_outputs: list[ToolOutput]
    final_response: dict[str, object] | None


@dataclass(frozen=True)
class ResponsesToolLedger:
    """save must durably commit the latest revision under exclusive ownership.

    Every save receives a detached, complete checkpoint, including saves before
    and after local effects. Copying and serializing snapshots can take quadratic
    total work as a batch grows. Size storage for the complete batch and history; context_budget does
    not limit it. After interruption, the saved prefix may omit later observations
    or unattempted proposals. Effect and completed inspection checkpoints include
    the full prefix.
    """

    run_id: str
    save: Callable[[ResponsesToolCheckpoint], None]
    resume_from: ResponsesToolCheckpoint | None = None


@dataclass(frozen=True)
class AsyncResponsesToolLedger:
    """An awaited recorder; pending checkpoints require external reconciliation.

    Like ResponsesToolLedger, each save receives a detached full checkpoint.
    Copying and serializing snapshots can take quadratic total work as a batch
    grows. context_budget does not limit ledger storage. After interruption, the
    saved prefix may omit later observations or unattempted proposals. Effect
    and completed inspection checkpoints include the full prefix.
    """

    run_id: str
    save: Callable[[ResponsesToolCheckpoint], Awaitable[None]]
    resume_from: ResponsesToolCheckpoint | None = None


def _plain(value: object, *, allow_omitted: bool = False) -> object:
    """Copy JSON values without serialization hooks or shared mutable objects."""
    if allow_omitted and not is_given(value):
        return value
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        return json.loads(json.dumps(value, allow_nan=False))
    if type(value) is list:
        return [_plain(item, allow_omitted=allow_omitted) for item in cast(list[object], value)]
    if type(value) is dict:
        entries = cast(dict[object, object], value)
        if any(type(key) is not str for key in entries):
            raise ValueError("Checkpoint object keys must be strings.")
        return {cast(str, key): _plain(item, allow_omitted=allow_omitted) for key, item in entries.items()}
    raise ValueError("Checkpoint data must be plain JSON values.")


def _history_native_ids(history: ResponseInputParam) -> set[str]:
    defined: set[str] = set()
    reserved: set[str] = set()
    for item in cast(list[dict[str, object]], history):
        item_id = item.get("id")
        if type(item_id) is str and item_id:
            if item.get("type") != "item_reference" and not (
                item.get("type") is None and "role" not in item and "content" not in item
            ):
                if item_id in defined:
                    raise ValueError("Replay history has a duplicate native output item ID.")
                defined.add(item_id)
            reserved.add(item_id)
    return reserved


def _history_calls(history: ResponseInputParam, tools: list[ToolParam], *, budget_only: bool = False) -> set[str]:
    # Modern computer calls can omit the legacy checklist; validate these with
    # the same action parser as dispatch, without changing the saved input.
    try:
        validate_type(
            type_=ResponseInputParam,
            value=[item for item in history if item.get("type") not in ("computer_call", "computer_call_output")],
        )
    except pydantic.ValidationError:
        raise ValueError("Replay history does not match the Responses input schema.") from None
    _history_native_ids(history)
    names = {tool["name"] for tool in tools if tool["type"] == "function"}
    computer = any(tool["type"] in ("computer", "computer_use_preview") for tool in tools)
    calls: dict[str, str] = {}
    returned: set[str] = set()
    approvals: dict[str, dict[str, object]] = {}
    approved: dict[str, dict[str, object]] = {}
    answered: set[str] = set()
    for index, item in enumerate(cast(list[dict[str, object]], history)):
        kind = item.get("type", "message")
        if budget_only:
            if kind == "compaction_trigger":
                if index != len(history) - 1:
                    raise ValueError("A compaction trigger must be the final input item.")
                continue
            if kind == "item_reference" or (
                item.get("type") is None and "id" in item and "role" not in item and "content" not in item
            ):
                if type(item.get("id")) is not str:
                    raise ValueError("Item references require a native string ID.")
                continue
        if kind in ("function_call", "computer_call"):
            call_id = item.get("call_id")
            if type(call_id) is not str or call_id in calls or call_id in approvals:
                raise ValueError("Replay history has a missing or duplicate call ID.")
            if item.get("status") not in (None, "completed"):
                raise ValueError("Replay history contains an incomplete call.")
            if kind == "function_call":
                name, arguments = item.get("name"), item.get("arguments")
                if (
                    type(name) is not str
                    or name not in names
                    or type(arguments) is not str
                    or not _valid_function_metadata(item)
                ):
                    raise ValueError("Replay history has an unregistered function.")
                if type(json.loads(arguments, parse_constant=_invalid_function_constant)) is not dict:
                    raise ValueError("Replay function arguments must be a JSON object.")
            else:
                if not computer:
                    raise ValueError("Replay history requires a registered computer.")
                if item.get("status") != "completed":
                    raise ValueError("Replay history contains an incomplete computer call.")
                if type(item.get("id")) is not str:
                    raise ValueError("Replay computer call requires its native item ID.")
                native = construct_type_unchecked(type_=ResponseComputerToolCall, value=item)
                try:
                    for action in _computer_actions(native):
                        validate_type(type_=type(action), value=action.to_dict())
                except (ComputerUseError, AttributeError, TypeError, ValueError):
                    raise ValueError("Replay computer actions are malformed.") from None
                if json.dumps(native.to_dict(), sort_keys=True) != json.dumps(item, sort_keys=True):
                    raise ValueError("Replay computer fields cannot be coerced.")
            calls[call_id] = cast(str, kind)
        elif kind in ("function_call_output", "computer_call_output"):
            call_id = item.get("call_id")
            if (
                type(call_id) is not str
                or call_id not in calls
                or call_id in returned
                or kind != calls[call_id] + "_output"
            ):
                raise ValueError("Replay output has no matching original call.")
            if kind == "function_call_output":
                if not _valid_function_metadata(item, output=True):
                    raise ValueError("Replay function output has invalid native fields.")
                _supplied_result(item.get("output"))
            else:
                checks = item.get("acknowledged_safety_checks")
                if (
                    (item.get("id") is not None and type(item["id"]) is not str)
                    or item.get("status") not in (None, "in_progress", "completed", "incomplete")
                    or (
                        checks is not None
                        and (
                            type(checks) is not list
                            or any(
                                type(check) is not dict
                                or type(check.get("id")) is not str
                                or any(
                                    check.get(key) is not None and type(check[key]) is not str
                                    for key in ("code", "message")
                                )
                                for check in cast(list[dict[str, object]], checks)
                            )
                        )
                    )
                ):
                    raise ValueError("Replay computer output has invalid native fields.")
                screenshot = item.get("output")
                if type(screenshot) is not dict:
                    raise ValueError("Replay computer output requires its native screenshot.")
                screenshot = cast(dict[str, object], screenshot)
                identifiers = [screenshot.get("image_url"), screenshot.get("file_id")]
                if (
                    screenshot.get("type") != "computer_screenshot"
                    or any(value is not None and type(value) is not str for value in identifiers)
                    or not any(type(value) is str and value.strip() for value in identifiers)
                ):
                    raise ValueError("Replay computer output requires a screenshot identifier.")
            returned.add(call_id)
        elif kind == "mcp_approval_response":
            request_id = item.get("approval_request_id")
            if (
                type(request_id) is not str
                or request_id not in approvals
                or request_id in answered
                or type(item.get("approve")) is not bool
                or any(item.get(key) is not None and type(item[key]) is not str for key in ("id", "reason"))
            ):
                raise ValueError("Replay MCP approval does not match one pending original request.")
            answered.add(request_id)
            if item.get("approve") is True:
                approved[request_id] = approvals[request_id]
        elif kind in _SERVER_ITEMS:
            _validate_server_item(item, tools)
            if kind == "mcp_approval_request":
                request_id = item.get("id")
                if type(request_id) is not str or not request_id or request_id in approvals or request_id in calls:
                    raise ValueError("Replay MCP approval request IDs must be unique.")
                approvals[request_id] = item
            elif kind == "mcp_call":
                _validated_mcp_call(item, approved)
        elif kind == "compaction":
            if type(item.get("encrypted_content")) is not str or (
                item.get("id") is not None and type(item["id"]) is not str
            ):
                raise ValueError("Replay compaction needs native encrypted content.")
        elif kind == "reasoning":
            if not _valid_reasoning_history(item):
                raise ValueError("Replay history requires native reasoning fields.")
        elif kind == "message":
            if not _valid_input_message_history(item):
                raise ValueError("Replay history requires native message input fields.")
        else:
            raise ValueError("Replay history contains an unsupported item.")
    if calls.keys() != returned or approvals.keys() != answered:
        raise ValueError("Replay history contains unresolved calls.")
    return set(calls) | set(approvals)


def _valid_input_message_history(item: dict[str, object]) -> bool:
    # Pydantic 1 can coerce an input into a different union member. Replay
    # sends the saved fields, so validate those rather than the parsed copy.
    if item.get("role") not in ("user", "assistant", "system", "developer"):
        return False
    content = item.get("content")
    if (type(content) is str or item.get("role") == "assistant") and item.get("phase") not in (
        None,
        "commentary",
        "final_answer",
    ):
        return False
    if type(content) is str:
        return True
    if type(content) is not list:
        return False
    if any(
        type(part) is dict and cast(dict[str, object], part).get("type") in ("output_text", "refusal")
        for part in cast(list[object], content)
    ):
        native = construct_type_unchecked(type_=ResponseOutputMessage, value=item)
        return _valid_native_message(native) and _same_message_fields(item, native.to_dict())
    for raw in cast(list[object], content):
        if type(raw) is not dict:
            return False
        part = cast(dict[str, object], raw)
        if not _valid_native_input_part_history(part):
            return False
    return True


def _same_message_fields(original: object, parsed: object) -> bool:
    # A native float score accepts an integer, but strings and booleans must
    # never be converted into native text, indices, bytes or scores on replay.
    if type(original) is int and type(parsed) is float:
        return original == parsed
    if type(original) is not type(parsed):
        return False
    if type(original) is dict:
        left, right = cast(dict[str, object], original), cast(dict[str, object], parsed)
        return left.keys() == right.keys() and all(
            _same_message_fields(value, right[key]) for key, value in left.items()
        )
    if type(original) is list:
        items, values = cast(list[object], original), cast(list[object], parsed)
        return len(items) == len(values) and all(
            _same_message_fields(item, value) for item, value in zip(items, values, strict=True)
        )
    return original == parsed


def _valid_native_input_part_history(part: dict[str, object]) -> bool:
    if "prompt_cache_breakpoint" in part:
        breakpoint = part["prompt_cache_breakpoint"]
        if type(breakpoint) is not dict or cast(dict[str, object], breakpoint).get("mode") != "explicit":
            return False
    kind = part.get("type")
    if kind == "input_text":
        return type(part.get("text")) is str
    if kind == "input_image":
        return part.get("detail") in ("auto", "low", "high", "original") and all(
            part.get(field) is None or type(part[field]) is str for field in ("image_url", "file_id")
        )
    if kind == "input_file":
        return (
            ("detail" not in part or part["detail"] in ("auto", "low", "high"))
            and (part.get("file_id") is None or type(part["file_id"]) is str)
            and all(field not in part or type(part[field]) is str for field in ("file_data", "file_url", "filename"))
        )
    return False


def _valid_reasoning_history(item: dict[str, object]) -> bool:
    def parts(value: object, kind: str) -> bool:
        if type(value) is not list:
            return False
        for part in cast(list[object], value):
            if type(part) is not dict:
                return False
            fields = cast(dict[str, object], part)
            if fields.get("type") != kind or type(fields.get("text")) is not str:
                return False
        return True

    return (
        type(item.get("id")) is str
        and parts(item.get("summary"), "summary_text")
        and ("content" not in item or parts(item["content"], "reasoning_text"))
        and (item.get("encrypted_content") is None or type(item["encrypted_content"]) is str)
        and ("status" not in item or item["status"] in ("completed", "incomplete", "in_progress"))
    )


def _has_observation(history: ResponseInputParam) -> bool:
    for item in cast(list[dict[str, object]], history):
        if item.get("type", "message") != "message" or item.get("role") != "user":
            continue
        content = item.get("content")
        if type(content) is str and content.strip():
            return True
        if type(content) is not list:
            continue
        try:
            blocks = _supplied_result(cast(list[object], content))
        except ValueError:
            continue
        if isinstance(blocks, list) and any(
            block["type"] != "input_text" or bool(block["text"].strip()) for block in blocks
        ):
            return True
    return False


def _save_sync(ledger: ResponsesToolLedger, checkpoint: ResponsesToolCheckpoint) -> None:
    result = cast(Callable[[ResponsesToolCheckpoint], object], ledger.save)(checkpoint)
    if isawaitable(result):
        if iscoroutine(result):
            result.close()
        raise ValueError("A sync recorder cannot return an awaitable; use the async runner.")


@dataclass(frozen=True)
class RegisteredFunction:
    tool: FunctionToolParam
    execute: Callable[[dict[str, object]], FunctionResult]
    allow_output_override: bool = False
    independent: bool = False
    _parsed_tool: FunctionToolParam | None = field(default=None, repr=False)

    @classmethod
    def from_tool(
        cls,
        tool: FunctionToolParam,
        *,
        execute: Callable[[_ModelT], FunctionResult],
        allow_output_override: bool = False,
        independent: bool = False,
    ) -> RegisteredFunction:
        """Register an existing Pydantic Responses tool and a typed executor."""
        if not isinstance(cast(object, tool), ResponsesPydanticFunctionTool) or not callable(execute):
            raise ValueError("from_tool requires a Pydantic Responses function tool and an executor.")
        return cls(
            tool,
            cast(Callable[[dict[str, object]], FunctionResult], execute),
            allow_output_override,
            independent,
            deepcopy(tool),
        )


@dataclass(frozen=True)
class AsyncRegisteredFunction:
    tool: FunctionToolParam
    execute: Callable[[dict[str, object]], Awaitable[FunctionResult]]
    allow_output_override: bool = False
    independent: bool = False
    _parsed_tool: FunctionToolParam | None = field(default=None, repr=False)

    @classmethod
    def from_tool(
        cls,
        tool: FunctionToolParam,
        *,
        execute: Callable[[_ModelT], Awaitable[FunctionResult]],
        allow_output_override: bool = False,
        independent: bool = False,
    ) -> AsyncRegisteredFunction:
        """Register an existing Pydantic Responses tool and a typed async executor."""
        if not isinstance(cast(object, tool), ResponsesPydanticFunctionTool) or not callable(execute):
            raise ValueError("from_tool requires a Pydantic Responses function tool and an executor.")
        return cls(
            tool,
            cast(Callable[[dict[str, object]], Awaitable[FunctionResult]], execute),
            allow_output_override,
            independent,
            deepcopy(tool),
        )


@dataclass(frozen=True)
class ResponsesRunnerTurn:
    """A paused turn. Receipts describe work already done, including eager tools.

    Supply only opted-in ordinary outputs before advancing/closing this turn.
    The original response is visible; changing it cannot change tool dispatch.
    """

    response: Response
    step: int
    final: bool
    tools_executed: bool
    attempted_call_ids: tuple[str, ...]
    completed_call_ids: tuple[str, ...]
    _supply: Callable[[list[FunctionCallOutput]], None] = field(repr=False, compare=False)
    _append: Callable[[str], None] = field(repr=False, compare=False)

    def supply_outputs(self, outputs: list[FunctionCallOutput]) -> None:
        self._supply(outputs)

    def append_user_text(self, text: str) -> None:
        """Append text after this turn's pending outputs, without changing its calls."""
        self._append(text)


class ToolRunnerError(RuntimeError):
    """A stopped run, with IDs only. Inspect these before deciding whether to retry.

    attempted_call_ids includes a call whose execution may have failed partway
    through. completed_call_ids means the SDK built its output, not that a
    browser action was approved.
    """

    def __init__(self, message: str, attempted_call_ids: list[str], completed_call_ids: list[str]) -> None:
        super().__init__(message)
        self.attempted_call_ids = tuple(attempted_call_ids)
        self.completed_call_ids = tuple(completed_call_ids)


class ToolRunnerCancelledError(asyncio.CancelledError):
    """Preserves task cancellation and records calls that may already have effects."""

    def __init__(self, attempted_call_ids: list[str], completed_call_ids: list[str]) -> None:
        super().__init__("Tool run was cancelled.")
        self.attempted_call_ids = tuple(attempted_call_ids)
        self.completed_call_ids = tuple(completed_call_ids)


def _wire(item: ResponseOutputItem) -> dict[str, object]:
    data = item.to_dict()
    data.pop("created_by", None)
    if item.type == "function_call":
        data.pop("parsed_arguments", None)
        if data.get("id") is None:
            # Response IDs are nullable; the replay-input field is optional but not nullable.
            data.pop("id", None)
    if item.type == "message":
        for part in cast(list[dict[str, object]], data.get("content", [])):
            if part.get("type") == "output_text":
                part.pop("parsed", None)
    return data


def _same_stream_output(observed: list[dict[str, object]], completed: list[dict[str, object]]) -> bool:
    if len(observed) != len(completed):
        return False
    for before, after in zip(observed, completed, strict=True):
        if (
            before.get("type") == after.get("type") == "reasoning"
            and type(before.get("encrypted_content")) is str
            and before.get("encrypted_content")
            and type(after.get("encrypted_content")) is str
            and after.get("encrypted_content")
        ):
            # Opaque reasoning ciphertext can change between done and completed events.
            before = {**before, "encrypted_content": after["encrypted_content"]}
        if (
            before.get("type") == after.get("type") == "function_call"
            and "id" not in before
            and type(after.get("id")) is str
        ):
            # A native optional platform ID may arrive after execution keyed by call_id.
            before = {**before, "id": after["id"]}
        if before != after:
            return False
    return True


def _invalid_function_constant(_constant: str) -> object:
    raise ValueError("Registered function arguments require valid JSON.")


def _function_args(call: ResponseFunctionToolCall) -> dict[str, object]:
    args: object = json.loads(call.arguments, parse_constant=_invalid_function_constant)
    if not isinstance(args, dict):
        raise ValueError("Registered functions require a JSON object.")
    return cast(dict[str, object], args)


def _valid_function_metadata(item: dict[str, object], *, output: bool = False) -> bool:
    caller = item.get("caller")
    if caller is not None:
        if not isinstance(caller, dict):
            return False
        source = cast(dict[str, object], caller)
        if source.get("type") != "direct" and (
            source.get("type") != "program" or type(source.get("caller_id")) is not str
        ):
            return False
    if output:
        return item.get("status") in (None, "in_progress", "completed", "incomplete") and all(
            item.get(key) is None or type(item[key]) is str for key in ("id", "name", "namespace")
        )
    return (
        ("id" not in item or type(item["id"]) is str)
        and ("async" not in item or type(item["async"]) is bool)
        and ("namespace" not in item or type(item["namespace"]) is str)
    )


def _supplied_result(value: object) -> FunctionResult:
    if type(value) is str:
        return value
    if type(value) is not list:
        raise ValueError("Supplied output must be text or a list of declared input blocks.")
    result: list[dict[str, object]] = []
    for raw in cast(list[object], value):
        if type(raw) is not dict:
            raise ValueError("Supplied input blocks must be ordinary dictionaries.")
        block = cast(dict[str, object], raw)
        if any(type(key) is not str for key in block):
            raise ValueError("Supplied input block keys must be strings.")
        kind = block.get("type")
        if type(kind) is not str or kind not in ("input_text", "input_image", "input_file"):
            raise ValueError("Supplied input block type is invalid.")
        allowed = {"type", "prompt_cache_breakpoint"}
        if kind == "input_text":
            allowed.add("text")
            if type(block.get("text")) is not str:
                raise ValueError("Supplied text requires a string.")
        elif kind == "input_image":
            allowed.update(("file_id", "image_url", "detail"))
        else:
            allowed.update(("file_data", "file_id", "file_url", "filename", "detail"))
        if block.keys() - allowed:
            raise ValueError("Supplied input block has unknown fields.")
        output: dict[str, object] = {"type": kind}
        for key in allowed - {"type", "prompt_cache_breakpoint"}:
            if key not in block:
                continue
            content = block[key]
            if key == "detail":
                allowed_details = (
                    (None, "auto", "low", "high", "original") if kind == "input_image" else ("auto", "low", "high")
                )
                if (content is not None and type(content) is not str) or content not in allowed_details:
                    raise ValueError("Supplied block detail is invalid.")
            elif content is not None and type(content) is not str:
                raise ValueError("Supplied block values must be strings or null.")
            output[key] = content
        if kind == "input_image" and not any(
            isinstance(output.get(key), str) and bool(cast(str, output[key]).strip())
            for key in ("image_url", "file_id")
        ):
            raise ValueError("Supplied image output requires image_url or file_id.")
        if kind == "input_file" and not any(
            isinstance(output.get(key), str) and bool(cast(str, output[key]).strip())
            for key in ("file_data", "file_id", "file_url")
        ):
            raise ValueError("Supplied file output requires file_data, file_id or file_url.")
        if "prompt_cache_breakpoint" in block:
            cache = block["prompt_cache_breakpoint"]
            if cache is None:
                output["prompt_cache_breakpoint"] = None
            else:
                if type(cache) is not dict:
                    raise ValueError("Supplied cache breakpoint is invalid.")
                entries = cast(dict[str, object], cache)
                if (
                    any(type(key) is not str for key in entries)
                    or entries.keys() != {"mode"}
                    or type(entries["mode"]) is not str
                    or entries["mode"] != "explicit"
                ):
                    raise ValueError("Supplied cache breakpoint is invalid.")
                output["prompt_cache_breakpoint"] = {"mode": "explicit"}
        result.append(output)
    return cast(ResponseFunctionCallOutputItemListParam, result)


class _Run:
    def __init__(
        self,
        params: ResponseCreateParamsNonStreaming,
        tools: list[ToolParam],
        functions: Mapping[str, RegisteredFunction | AsyncRegisteredFunction],
        max_steps: int | None,
        stream: bool,
        eager: bool,
        cancelled: Callable[[], bool] | None,
        ledger: ResponsesToolLedger | AsyncResponsesToolLedger | None = None,
        overrides: frozenset[str] = frozenset(),
        context_budget: ContextBudget | AsyncContextBudget | None = None,
        browser_names: frozenset[str] = frozenset(),
        on_diagnostic: ToolDiagnosticObserver | None = None,
    ) -> None:
        if context_budget is not None or ledger is not None:
            if type(cast(object, params)) is not dict:
                raise ValueError("Saved or budgeted requests require native body parameters.")
            if ledger is not None and params.keys() - ResponseCreateParamsNonStreaming.__annotations__.keys():
                raise ValueError("Ledger requests require native body parameters without request overrides.")
            # Only the native TypedDict transform decides where omission sentinels
            # disappear. Free-form schemas, metadata and array entries remain strict.
            params = cast(
                ResponseCreateParamsNonStreaming,
                _plain(transform(_plain(params, allow_omitted=True), ResponseCreateParamsNonStreaming)),
            )
        else:
            params = _snapshot_request(params)
        extra_body = cast(dict[str, object], params).get("extra_body")
        if isinstance(extra_body, Mapping):
            owned = {
                "stream",
                "store",
                "background",
                "conversation",
                "previous_response_id",
                "tools",
                "input",
                "include",
                "tool_choice",
            }
            if context_budget is not None:
                owned.update(("truncation", "context_management"))
            if owned.intersection(cast(Mapping[str, object], extra_body)):
                raise ValueError("ResponsesToolRunner extra_body cannot override runner-owned fields.")
        saved = None if ledger is None or ledger.resume_from is None else _plain(ledger.resume_from)
        if saved is not None and type(saved) is not dict:
            raise ValueError("Resume requires a complete checkpoint.")
        checkpoint = cast(ResponsesToolCheckpoint | None, saved)
        if max_steps is None:
            max_steps = 20 if checkpoint is None else checkpoint.get("max_steps")
        if type(max_steps) is not int or max_steps < 1:
            raise ValueError("max_steps must be a positive integer.")
        self.max_steps = max_steps
        self.ledger = ledger
        self.revision = 0
        self.consumed_requests = 0
        self.overrides = sorted(overrides)
        self.pending_items: list[dict[str, object]] | None = None
        if eager and not stream:
            raise ValueError("Eager execution requires streaming.")
        if (
            # Reject stream=True from untyped callers; select streaming through run(), not params.
            params.get("stream")  # ty: ignore[redundant-condition]
            or params.get("background")
            or params.get("conversation") is not None
            or params.get("previous_response_id") is not None
        ):
            raise ValueError("Use explicit input history and foreground responses. Select streaming on run().")
        has_computer = any(tool["type"] == "computer" for tool in tools)
        declared_computer = False
        for tool in params.get("tools") or []:
            if tool["type"] == "computer" or tool["type"] == "computer_use_preview":
                if not has_computer or declared_computer:
                    raise ValueError("A single declared computer requires a registered computer driver.")
                declared_computer = True
                tools = [current for current in tools if current["type"] != "computer"]
            elif tool["type"] not in _SERVER_TOOLS:
                raise ValueError(
                    "Only supported declared server tools and registered computer tools are accepted in params."
                )
            tools.append(deepcopy(tool))
        labels = [tool["server_label"] for tool in tools if tool["type"] == "mcp"]
        if any(type(label) is not str or not label for label in labels) or len(set(labels)) != len(labels):
            raise ValueError("MCP server labels must be nonempty and unique.")
        if params.get("store") is False and any(tool["type"] == "image_generation" for tool in tools):
            raise ValueError(
                "This runner requires stored responses to continue after image generation. "
                "Set store to true or use responses.create for a single request."
            )
        self.request = params.copy()
        if "tool_choice" in self.request:
            self.request["tool_choice"] = deepcopy(self.request["tool_choice"])
        choice = self.request.get("tool_choice")
        local_types = {"function", "computer", "computer_use", "computer_use_preview"}
        if (choice == "required" and bool(tools) and all(tool["type"] in local_types for tool in tools)) or (
            isinstance(choice, dict)
            and (
                choice["type"] in local_types
                or (
                    choice["type"] == "allowed_tools"
                    and choice["mode"] == "required"
                    and bool(choice["tools"])
                    and all(tool.get("type") in local_types for tool in choice["tools"])
                )
            )
        ):
            raise ValueError(
                "ResponsesToolRunner cannot finish when tool_choice always requires a local tool. "
                "Use auto or responses.create for a single forced request."
            )
        self.request["tools"] = tools
        self.tools = tools
        self.function_names = {tool["name"] for tool in tools if tool["type"] == "function"}
        self.selected_functions = self.function_names.copy()
        self.selected_computer = has_computer
        self.selected_mcp: list[tuple[str, str | None]] | None = None
        self.selected_server: set[str] | None = None
        if choice not in (None, "auto", "required"):
            choices = choice["tools"] if isinstance(choice, dict) and choice["type"] == "allowed_tools" else [choice]
            self.selected_functions = set[str]()
            self.selected_computer = False
            self.selected_mcp = []
            self.selected_server = set()
            for selected in choices:
                if not isinstance(selected, dict):
                    continue
                name = selected.get("name")
                if selected.get("type") == "function" and isinstance(name, str):
                    self.selected_functions.add(name)
                elif selected.get("type") in ("computer", "computer_use", "computer_use_preview"):
                    self.selected_computer = True
                elif selected.get("type") == "mcp":
                    server_label = selected.get("server_label")
                    if type(server_label) is str and (name is None or type(name) is str):
                        self.selected_mcp.append((server_label, name))
                else:
                    selected_type = selected.get("type")
                    if type(selected_type) is str and selected_type in _SERVER_TOOLS:
                        self.selected_server.add(selected_type)
        self.functions = functions
        self.has_computer = has_computer
        original = params.get("input", [])
        self.history: ResponseInputParam = (
            [{"role": "user", "content": original}] if isinstance(original, str) else list(original)
        )
        self.request["input"] = self.history
        self.request["include"] = list(dict.fromkeys([*(params.get("include") or []), "reasoning.encrypted_content"]))
        self.cancelled = cancelled
        self.on_diagnostic = on_diagnostic
        self.attempted: list[str] = []
        self.completed: list[str] = []
        self._seen = {
            cast(str, item["call_id"] if "call_id" in item else item["id"])
            for item in cast(list[dict[str, object]], self.history)
            if ("call_id" in item and type(item["call_id"]) is str)
            or (item.get("type") == "mcp_approval_request" and type(item.get("id")) is str)
        }
        self.last_error: ToolRunnerError | None = None
        self.items: list[dict[str, object]] = []
        self.outputs: list[ToolOutput] = []
        self.browser_failed = False
        self.last_step = False
        self.active_step: int | None = None
        self.supplied: dict[str, FunctionCallOutput] = {}
        self.user_text: list[str] = []
        self.browser_names = browser_names
        self.context_budget = context_budget
        if context_budget is not None:
            if type(cast(object, context_budget)) is not dict or context_budget.keys() - {
                "max_input_bytes",
                "max_input_images",
                "keep_recent_screenshots",
                "compact",
            }:
                raise ValueError("Unknown context_budget fields.")
            for name, minimum in (("max_input_bytes", 1), ("max_input_images", 0), ("keep_recent_screenshots", 1)):
                number = cast(dict[str, object], context_budget).get(
                    name, 1 if name == "keep_recent_screenshots" else None
                )
                if type(number) is not int or not minimum <= number <= 9007199254740991:
                    raise ValueError("Invalid context_budget limit.")
            if "compact" in context_budget and not callable(context_budget["compact"]):
                raise ValueError("context_budget.compact must be callable.")
            if params.get("truncation") == "auto" or params.get("context_management"):
                raise ValueError("context_budget cannot use server truncation or context management.")
            self.context_budget = context_budget.copy()
            if params.get("truncation") is None:
                self.request["truncation"] = "disabled"
        if ledger is not None:
            if type(ledger.run_id) is not str or not ledger.run_id or not callable(ledger.save):
                raise ValueError("A ledger requires a nonempty run ID and recorder.")
            self.request = cast(
                ResponseCreateParamsNonStreaming,
                _plain(transform(_plain(self.request, allow_omitted=True), ResponseCreateParamsNonStreaming)),
            )
            self.history = cast(ResponseInputParam, self.request.get("input"))
            self.tools = cast(list[ToolParam], self.request.get("tools"))
            if checkpoint is not None:
                self.restore(checkpoint)
            self.validate_boundary()

    def context_snapshot(self) -> tuple[ContextBudgetSnapshot, frozenset[str]] | None:
        """Measure full history at a safe boundary, before advancing admission."""
        budget = self.context_budget
        if budget is None:
            return None
        self.validate_boundary()
        size, images = self.context_size(self.history)
        if size <= budget["max_input_bytes"] and images <= budget["max_input_images"]:
            return None
        if "compact" not in budget:
            raise self.error("Native request input exceeds context_budget.")
        calls: dict[str, dict[str, object]] = {}
        protected: set[str] = set()
        screenshots: list[str] = []
        latest_browser = latest_computer = None
        for item in cast(list[dict[str, object]], self.history):
            kind = item.get("type")
            if kind in ("function_call", "computer_call"):
                call_id = cast(str, item["call_id"])
                calls[call_id] = item
                if kind == "computer_call":
                    latest_computer = call_id
                    if item.get("pending_safety_checks"):
                        protected.add(call_id)
                elif item.get("name") in self.browser_names:
                    latest_browser = call_id
            elif kind in ("function_call_output", "computer_call_output"):
                call_id = cast(str, item["call_id"])
                call = calls[call_id]
                if kind == "computer_call_output":
                    screenshots.append(call_id)
                    if item.get("acknowledged_safety_checks"):
                        protected.add(call_id)
                elif (
                    call.get("name") in ("browser_screenshot", "browser_zoom")
                    and call.get("name") in self.browser_names
                    and isinstance(item.get("output"), list)
                    and any(
                        block.get("type") == "input_image" for block in cast(list[dict[str, object]], item["output"])
                    )
                ):
                    screenshots.append(call_id)
        protected.update(screenshots[-budget.get("keep_recent_screenshots", 1) :])
        if latest_browser is not None:
            protected.add(latest_browser)
        if latest_computer is not None:
            protected.add(latest_computer)
        eligible = [call_id for call_id in calls if call_id not in protected]
        snapshot: ContextBudgetSnapshot = {
            "history": cast(ResponseInputParam, _plain(self.history)),
            "eligible_call_ids": eligible,
            "input_bytes": size,
            "input_images": images,
        }
        return snapshot, frozenset(eligible)

    @staticmethod
    def context_size(history: ResponseInputParam) -> tuple[int, int]:
        # History has already been validated/copied by the ledger. Compact JSON
        # measures native input, not total HTTP bytes or decoded remote data.
        encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        size = sum(
            len(chunk[offset : offset + 16_384].encode("utf-8"))
            for chunk in encoder.iterencode(history)
            for offset in range(0, len(chunk), 16_384)
        )
        images = 0
        for item in cast(list[dict[str, object]], history):
            kind = item.get("type", "message")
            if kind == "computer_call_output":
                images += 1
            elif kind in ("message", "function_call_output"):
                blocks = item.get("output" if kind == "function_call_output" else "content")
                if type(blocks) is list:
                    images += sum(
                        1
                        for block in cast(list[object], blocks)
                        if type(block) is dict and cast(dict[str, object], block).get("type") == "input_image"
                    )
        return size, images

    def context_input(self, decision: ContextBudgetDecision, eligible: frozenset[str]) -> ResponseInputParam:
        if type(cast(object, decision)) is not dict or decision.keys() - {"drop_call_ids", "summary"}:
            raise self.error("Invalid context_budget decision.")
        drop = decision.get("drop_call_ids")
        if (
            type(drop) is not list
            or any(type(call_id) is not str or call_id not in eligible for call_id in drop)
            or len(set(drop)) != len(drop)
            or ("summary" in decision and type(decision["summary"]) is not str)
        ):
            raise self.error("Invalid context_budget decision.")
        selected = frozenset(drop)
        retained: list[dict[str, object]] = []
        receipts: list[dict[str, str]] = []
        for item in cast(list[dict[str, object]], self.history):
            kind = item.get("type")
            if kind in ("function_call", "computer_call", "function_call_output", "computer_call_output") and (
                item.get("call_id") in selected
            ):
                if kind in ("function_call", "computer_call"):
                    receipt = {"call_id": cast(str, item["call_id"]), "kind": cast(str, kind)}
                    if kind == "function_call":
                        receipt["name"] = cast(str, item["name"])
                    receipts.append(receipt)
            else:
                retained.append(item)
        messages: ResponseInputParam = []
        if "summary" in decision:
            messages.append(
                {"role": "user", "content": "Caller summary of omitted completed tool results: " + decision["summary"]}
            )
        if receipts:
            messages.append(
                {
                    "role": "user",
                    "content": "Omitted completed tool receipts: "
                    + json.dumps(receipts, ensure_ascii=False, separators=(",", ":"))
                    + ". Output is present in the runner's full history; external success is unverified.",
                }
            )
        projected: ResponseInputParam = [*messages, *cast(ResponseInputParam, retained)]
        _history_calls(projected, self.tools, budget_only=self.ledger is None)
        size, images = self.context_size(projected)
        assert self.context_budget is not None
        if size > self.context_budget["max_input_bytes"] or images > self.context_budget["max_input_images"]:
            raise self.error("Native request input still exceeds context_budget.")
        return projected

    def validate_boundary(self) -> None:
        if (
            type(self.max_steps) is not int
            or not 1 <= self.max_steps <= 9007199254740991
            or type(self.consumed_requests) is not int
            or not 0 <= self.consumed_requests <= self.max_steps
            or type(self.revision) is not int
            or not 0 <= self.revision < 9007199254740991
        ):
            raise ValueError("Checkpoint revision or original request budget is invalid.")
        history = cast(ResponseInputParam, _plain(self.history))
        self._seen = _history_calls(
            history, self.tools, budget_only=self.ledger is None and self.context_budget is not None
        )
        if self.attempted != self.completed or any(call_id not in self._seen for call_id in self.completed):
            raise ValueError("A boundary cannot contain unresolved call receipts.")
        if any(type(call_id) is not str for call_id in self.attempted) or len(set(self.attempted)) != len(
            self.attempted
        ):
            raise ValueError("Checkpoint receipts are missing or duplicated.")

    def restore(self, checkpoint: ResponsesToolCheckpoint) -> None:
        assert self.ledger is not None
        if (
            checkpoint.keys() != ResponsesToolCheckpoint.__annotations__.keys()
            or type(checkpoint["version"]) is not int
            or checkpoint["version"] != 1
            or checkpoint["run_id"] != self.ledger.run_id
            or checkpoint["phase"] != "boundary"
            or type(checkpoint["max_steps"]) is not int
            or checkpoint["max_steps"] != self.max_steps
            or json.dumps(checkpoint["tools"], sort_keys=True, allow_nan=False)
            != json.dumps(_ledger_tools(self.tools), sort_keys=True, allow_nan=False)
            or checkpoint["output_override_names"] != self.overrides
            or checkpoint["pending_items"] != []
            or checkpoint["returned_outputs"] != []
            or checkpoint["final_response"] is not None
            or type(checkpoint["history"]) is not list
            or type(checkpoint["attempted_call_ids"]) is not list
            or type(checkpoint["returned_call_ids"]) is not list
            or type(checkpoint["revision"]) is not int
            or checkpoint["revision"] < 1
        ):
            raise ValueError("Only a matching completed boundary can resume; reconcile pending work externally.")
        fresh = self.history
        if not _has_observation(fresh):
            raise ValueError("Resume requires a nonempty current observation in params.input.")
        self.revision = checkpoint["revision"]
        self.consumed_requests = checkpoint["consumed_requests"]
        self.attempted = checkpoint["attempted_call_ids"]
        self.completed = checkpoint["returned_call_ids"]
        self.history = checkpoint["history"]
        self.validate_boundary()
        self.history = [*self.history, *fresh]
        self.request["input"] = self.history

    def checkpoint(
        self, phase: Literal["boundary", "pending", "final"], response: Response | None = None
    ) -> ResponsesToolCheckpoint:
        if self.ledger is None:
            raise AssertionError("No ledger was selected.")
        if phase == "boundary":
            self.validate_boundary()
        if self.revision >= 9007199254740991:
            raise ValueError("Checkpoint revision is exhausted.")
        self.revision += 1
        value: ResponsesToolCheckpoint = {
            "version": 1,
            "run_id": self.ledger.run_id,
            "revision": self.revision,
            "phase": phase,
            "max_steps": self.max_steps,
            "consumed_requests": self.consumed_requests,
            "tools": _ledger_tools(self.tools),
            "output_override_names": self.overrides,
            "history": self.history,
            "attempted_call_ids": self.attempted,
            "returned_call_ids": self.completed,
            "pending_items": (self.pending_items if self.pending_items is not None else self.items)
            if phase == "pending"
            else [],
            "returned_outputs": self.outputs if phase == "pending" else [],
            "final_response": response.to_dict() if phase == "final" and response is not None else None,
        }
        checkpoint = cast(ResponsesToolCheckpoint, _plain(value))
        final = checkpoint["final_response"]
        if final is not None and "tools" in final:
            final["tools"] = _ledger_tools(cast(list[ToolParam], final["tools"]))
        return checkpoint

    def approvals_to_refresh(self) -> Generator[tuple[dict[str, object], McpApprovalRequest], None, None]:
        if self.consumed_requests >= self.max_steps:
            return
        history = [
            item
            for item in cast(list[dict[str, object]], self.history)
            if item.get("type") in ("mcp_approval_request", "mcp_approval_response", "mcp_call")
        ]
        if not history:
            return
        if self.ledger is None:
            if self.context_budget is not None:
                self.validate_boundary()
            else:
                _history_calls(cast(ResponseInputParam, history), self.tools)
        # Only validated imported MCP history reaches here. Preserve consumed grants and all
        # receipts; a returned approval alone does not prove remote execution.
        approved = _approved_mcp_requests(cast(ResponseInputParam, history))
        for item in history:
            if item.get("type") == "mcp_approval_response" and item.get("approve") is True:
                request = approved.get(cast(str, item["approval_request_id"]))
                if request is not None:
                    approval = construct_type_unchecked(value=deepcopy(request), type_=McpApprovalRequest)
                    self.validate_mcp_selection(approval)
                    yield item, approval

    def error(self, message: str) -> ToolRunnerError:
        self.last_error = ToolRunnerError(message, self.attempted, self.completed)
        return self.last_error

    def check(self) -> None:
        if self.cancelled is not None and self.cancelled():
            raise self.error("Tool run was cancelled.")

    def begin(self, last_step: bool) -> None:
        self.items = []
        self.outputs = []
        self.browser_failed = False
        self.last_step = last_step
        self.supplied = {}
        self.pending_items = None
        self.turn_seen = self._seen.copy()
        self.stream_seen = self.turn_seen.copy()
        self.turn_native_ids = _history_native_ids(self.history)
        self.stream_native_ids = self.turn_native_ids.copy()
        self.stream_items: dict[int, dict[str, object]] = {}
        self.arguments: dict[str, object] = {}
        self.deferred = False
        self.approved_mcp = _approved_mcp_requests(self.history)

    def validate_mcp_selection(self, item: McpApprovalRequest | McpCall) -> None:
        declaration = next(
            (tool for tool in self.tools if tool["type"] == "mcp" and tool["server_label"] == item.server_label), None
        )
        policy = _mcp_approval_policy(declaration, item.name) if declaration is not None else None
        if item.type == "mcp_approval_request" and policy == "never":
            raise self.error("MCP approval request contradicts require_approval.")
        if item.type == "mcp_call" and policy == "always" and item.approval_request_id is None:
            raise self.error("MCP call requires a matching approval request.")
        allowed = declaration.get("allowed_tools") if declaration is not None else None
        names: object
        if isinstance(allowed, dict):
            tool_filter = cast(dict[str, object], allowed)
            filtered = "tool_names" in tool_filter
            names = tool_filter.get("tool_names")
        else:
            filtered = allowed is not None
            names = allowed
        if filtered and (not isinstance(names, (list, tuple)) or item.name not in names):
            raise self.error("MCP response names a tool excluded by allowed_tools.")
        if self.selected_mcp is not None and not any(
            server_label == item.server_label and (name is None or name == item.name)
            for server_label, name in self.selected_mcp
        ):
            raise self.error("Response contains a local tool excluded by tool_choice.")

    def validate(self, item: ResponseOutputItem, seen: set[str]) -> bool:
        try:
            wire = _wire(item)
            _plain(wire)
        except ValueError:
            raise self.error("Response contains replay data that is not plain JSON.") from None
        if item.type in _SERVER_ITEMS:
            try:
                _validate_server_item(wire, self.tools)
            except ValueError:
                raise self.error("Server tool did not complete or match its declaration and approval.") from None
            if item.type == "mcp_call" or item.type == "mcp_approval_request":
                self.validate_mcp_selection(item)
            if (
                self.selected_server is not None
                and "mcp" not in _SERVER_ITEMS[item.type]
                and _SERVER_ITEMS[item.type].isdisjoint(self.selected_server)
            ):
                raise self.error("Response contains a server tool excluded by tool_choice.")
            if item.type != "mcp_approval_request":
                return False
            if self.last_step:
                raise self.error("Tool run reached max_steps before completion.")
            if not item.id or item.id in seen:
                raise self.error("MCP approval request ID is missing or duplicate.")
            seen.add(item.id)
            return True
        if item.type not in ("function_call", "computer_call", "message", "reasoning", "compaction"):
            raise self.error("Response contains a tool the runner cannot execute.")
        if item.type == "message":
            if item.status != "completed":
                raise self.error("Response message did not complete.")
            if not _valid_native_message(item):
                raise self.error("Response message requires native assistant content before replay.")
        if item.type == "reasoning" and not _valid_native_reasoning(item):
            raise self.error("Response requires native reasoning content before replay.")
        if item.type == "compaction" and (
            type(getattr(item, "id", None)) is not str or type(getattr(item, "encrypted_content", None)) is not str
        ):
            raise self.error("Response requires native compaction content before replay.")
        if item.type != "function_call" and item.type != "computer_call":
            return False
        if item.type == "function_call":
            if item.name not in self.function_names or not _valid_function_metadata(wire):
                raise self.error("Function was not registered or lacks native metadata.")
            # The runner registers top-level functions; deferred calls may repeat their name as the namespace.
            if item.namespace not in (None, item.name):
                raise self.error("Function namespace does not match its registration.")
            declaration = next(tool for tool in self.tools if tool["type"] == "function" and tool["name"] == item.name)
            allowed = cast(object, declaration.get("allowed_callers"))
            caller = wire.get("caller")
            caller_type = (
                "programmatic"
                if isinstance(caller, dict) and cast(dict[str, object], caller).get("type") == "program"
                else "direct"
            )
            if allowed is not None and (not isinstance(allowed, (list, tuple)) or caller_type not in allowed):
                raise self.error("Function caller is excluded by allowed_callers.")
        if item.type == "computer_call":
            if not self.has_computer or wire.get("status") != "completed":
                raise self.error("Incomplete or unregistered computer call.")
            _computer_actions(item)
        if (item.type == "function_call" and item.name not in self.selected_functions) or (
            item.type == "computer_call" and not self.selected_computer
        ):
            raise self.error("Response contains a local tool excluded by tool_choice.")
        if item.status not in (None, "completed"):
            raise self.error("Tool call did not complete.")
        if self.last_step:
            raise self.error("Tool run reached max_steps before completion.")
        if not isinstance(cast(object, item.call_id), str) or item.call_id in seen:
            raise self.error("Tool call ID is missing or duplicate.")
        seen.add(item.call_id)
        if item.type == "function_call" and item.name in self.functions and item.call_id not in self.arguments:
            function = self.functions[item.name]
            started = monotonic()
            try:
                arguments = (
                    _function_args(item)
                    if function._parsed_tool is None
                    else parse_function_tool_arguments(input_tools=[function._parsed_tool], function_call=item)
                )
                if function._parsed_tool is not None and arguments is None:
                    raise self.error("Typed function arguments were not parsed.")
                self.arguments[item.call_id] = arguments
            except Exception:
                emit_tool_diagnostic(
                    self.on_diagnostic,
                    "responses",
                    "arguments",
                    "invalid_input",
                    started,
                    call_id=item.call_id,
                    member=item.name,
                )
                raise
        return True

    def receive(self, index: int, item: ResponseOutputItem, early: tuple[frozenset[str], bool] | None) -> bool:
        """Execute only the contiguous prefix. Defer any gap until final output is reconciled."""
        if type(index) is not int or index < 0 or index in self.stream_items:
            raise self.error("Tool stream output item index is invalid or duplicated.")
        self.validate_native_id(item, self.stream_native_ids)
        local = self.validate(item, self.stream_seen)
        if index != len(self.stream_items):
            self.deferred = True
        self.stream_items[index] = _wire(item)
        if (
            early is not None
            and local
            and (
                item.type == "mcp_approval_request"
                or (item.type == "function_call" and item.name not in early[0])
                or (item.type == "computer_call" and not early[1])
            )
        ):
            self.deferred = True
        return not self.deferred

    def validate_native_id(self, item: ResponseOutputItem, seen: set[str]) -> None:
        item_id = getattr(item, "id", None)
        if type(item_id) is str:
            if item_id in seen:
                raise self.error("Response output item IDs must be unique across the run.")
            seen.add(item_id)

    def preflight(self, response: Response, *, selective: bool = False) -> bool:
        if response.status != "completed":
            raise self.error("Response did not complete.")
        # Already executed prefix IDs belong to this turn, not to its baseline.
        seen = self.turn_seen.copy()
        native_ids = self.turn_native_ids.copy()
        tools = False
        for item in response.output:
            self.validate_native_id(item, native_ids)
            tools |= self.validate(item, seen)
            if item.type == "mcp_call":
                try:
                    _validated_mcp_call(_wire(item), self.approved_mcp)
                except ValueError:
                    raise self.error("Server tool did not match its approval.") from None
        if selective:
            if not _same_stream_output(
                [self.stream_items[index] for index in sorted(self.stream_items)],
                [_wire(item) for item in response.output],
            ):
                raise self.error("Completed response differs from collected stream output.")
            if len(self.items) == len(response.output):
                return self.finish(response)
        if tools:
            return False
        for index in range(len(self.items), len(response.output)):
            self.accept(index, response.output[index])
        return self.finish(response)

    def turn(
        self,
        response: Response,
        snapshot: Response,
        step: int,
        final: bool,
        reject_supplied: bool,
        names: frozenset[str],
    ) -> ResponsesRunnerTurn:
        self.active_step = step
        eligible = frozenset(
            item.call_id
            for item in snapshot.output[len(self.items) :]
            if item.type == "function_call" and item.name in names
        )
        return ResponsesRunnerTurn(
            response=response,
            step=step,
            final=final,
            tools_executed=bool(self.outputs),
            attempted_call_ids=tuple(self.attempted),
            completed_call_ids=tuple(self.completed),
            _supply=partial(self.supply, step, eligible, reject_supplied),
            _append=partial(self.append_user_text, step, final),
        )

    def append_user_text(self, step: int, final: bool, text: str) -> None:
        if self.active_step != step or final or type(text) is not str or not text.strip():
            raise ValueError("Only an active non-final turn can append user text.")
        self.user_text.append(text)

    def append_boundary_text(self) -> bool:
        if not self.user_text:
            return False
        self.history.extend({"role": "user", "content": text} for text in self.user_text)
        self.user_text = []
        return True

    def supply(self, step: int, eligible: frozenset[str], eager: bool, outputs: list[FunctionCallOutput]) -> None:
        if self.active_step != step or (eager and not eligible):
            raise ValueError("This turn cannot accept supplied outputs.")
        if type(outputs) is not list:
            raise ValueError("Supply an ordinary list of function outputs.")
        pending: dict[str, FunctionCallOutput] = {}
        for raw in cast(list[object], outputs):
            if type(raw) is not dict:
                raise ValueError("Supplied function outputs must be ordinary dictionaries.")
            output = cast(dict[str, object], raw)
            if (
                any(type(key) is not str for key in output)
                or output.keys() != {"type", "call_id", "output"}
                or type(output["type"]) is not str
                or output["type"] != "function_call_output"
                or type(output["call_id"]) is not str
            ):
                raise ValueError("Supplied function output fields are invalid.")
            call_id = output["call_id"]
            if call_id not in eligible or call_id in pending:
                raise ValueError("Supplied call ID is unknown, duplicated, or not permitted.")
            pending[call_id] = {
                "type": "function_call_output",
                "call_id": call_id,
                "output": _supplied_result(output["output"]),
            }
        self.supplied = pending

    def accept(self, index: int, item: ResponseOutputItem) -> bool:
        self.check()
        if index != len(self.items):
            raise self.error("Tool stream output items arrived out of order or twice.")
        if not self.validate(item, self._seen):
            self.items.append(_wire(item))
            return False
        self.items.append(_wire(item))
        if item.type == "mcp_approval_request":
            self.attempted.append(item.id)
        elif item.type == "function_call" or item.type == "computer_call":
            self.attempted.append(item.call_id)
        else:
            raise AssertionError("validated a non-tool")
        return True

    def add(
        self, item: ResponseFunctionToolCall | ResponseComputerToolCall | McpApprovalRequest, output: ToolOutput
    ) -> None:
        self.outputs.append(output)
        self.completed.append(item.id if item.type == "mcp_approval_request" else item.call_id)

    def finish(self, response: Response) -> bool:
        self.check()
        if response.status != "completed":
            raise self.error("Response did not complete.")
        completed = [_wire(item) for item in response.output]
        if not _same_stream_output(self.items, completed):
            raise self.error("Completed response differs from executed stream output.")
        self.items = completed
        if not self.outputs:
            if any(
                (item.type == "message" and item.status == "completed" and item.phase != "commentary")
                or (item.type in _SERVER_ITEMS and item.type != "mcp_approval_request")
                for item in response.output
            ):
                return True
            raise self.error("Response has no completed final message or tool call.")
        if (
            self.context_budget is not None
            and self.ledger is None
            and self.history
            and self.history[-1].get("type") == "compaction_trigger"
        ):
            self.history.pop()
        self.history.extend(cast(ResponseInputParam, deepcopy(self.items)))
        self.history.extend(self.outputs)
        return False


def _registry(
    browser: BrowserToolset | AsyncBrowserToolset | None,
    computer: ComputerToolset | AsyncComputerToolset | None,
    functions: list[RegisteredFunction] | list[AsyncRegisteredFunction],
) -> list[ToolParam]:
    tools: list[ToolParam] = list(browser.tools) if browser is not None else []
    names = {tool["name"] for tool in (browser.tools if browser is not None else [])}
    for function in functions:
        if not isinstance(cast(object, function), (RegisteredFunction, AsyncRegisteredFunction)) or not callable(
            function.execute
        ):
            raise ValueError("Every registered function requires an executor.")
        if type(function.allow_output_override) is not bool or type(function.independent) is not bool:
            raise ValueError("allow_output_override and independent must be booleans.")
        tool = cast(FunctionToolParam, deepcopy(dict(function.tool)))
        if tool["type"] != "function" or not tool["name"] or tool["name"] in names:
            raise ValueError("Function names must be unique and nonempty.")
        names.add(tool["name"])
        tools.append(tool)
    if computer is not None:
        tools.append({"type": "computer"})
    return tools


def _early_execution(early: EarlyExecution | None, tools: list[ToolParam]) -> tuple[frozenset[str], bool] | None:
    if early is None:
        return None
    if type(cast(object, early)) is not dict or early.keys() - {"functions", "computer"}:
        raise ValueError("early_execution must contain only functions and computer.")
    names = early.get("functions", [])
    computer = early.get("computer", False)
    registered = {tool["name"] for tool in tools if tool["type"] == "function"}
    if (
        type(names) is not list
        or any(type(name) is not str or name not in registered for name in names)
        or len(set(names)) != len(names)
    ):
        raise ValueError("Early functions must be unique registered function names.")
    if type(computer) is not bool or (computer and not any(tool["type"] == "computer" for tool in tools)):
        raise ValueError("Early computer execution requires a boolean and a registered dispatcher.")
    return frozenset(names), computer


class ResponsesToolRunner:
    def __init__(
        self,
        *,
        browser: BrowserToolset | None = None,
        computer: ComputerToolset | None = None,
        functions: list[RegisteredFunction] | None = None,
        early_execution: EarlyExecution | None = None,
    ) -> None:
        self._lifecycle = ToolLifecycle("Responses runner")
        selected = list(functions or [])
        self._tools = _registry(browser, computer, selected)
        self._early_execution = _early_execution(early_execution, self._tools)
        self._browser_names: frozenset[str] = (
            frozenset(tool["name"] for tool in browser.tools) if browser is not None else frozenset()
        )
        self.browser = browser
        self.computer = computer
        self._functions = {fn.tool["name"]: copy(fn) for fn in selected}
        self._overrides = frozenset(fn.tool["name"] for fn in selected if fn.allow_output_override)

    def close(self) -> CloseStatus:
        """Stop admission without taking ownership of the driver."""
        return self._lifecycle.close()

    def run(
        self,
        client: OpenAI,
        params: ResponseCreateParamsNonStreaming,
        *,
        max_steps: int | None = None,
        stream: bool = False,
        eager: bool = False,
        max_concurrent_calls: int = 2,
        on_event: Callable[[ResponseStreamEvent[None]], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
        approve_safety_checks: Callable[[ResponseComputerToolCall], bool] | None = None,
        before_action: Callable[[ComputerActionInput], bool] | None = None,
        ledger: ResponsesToolLedger | None = None,
        context_budget: ContextBudget | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
        approve_mcp: Callable[[McpApprovalRequest], bool] | None = None,
        before_early_call: Callable[[ResponseFunctionToolCall | ResponseComputerToolCall], Literal["execute", "defer"]]
        | None = None,
    ) -> Response:
        turns = self.iterate(
            client,
            params,
            max_steps=max_steps,
            stream=stream,
            eager=eager,
            max_concurrent_calls=max_concurrent_calls,
            on_event=on_event,
            cancelled=cancelled,
            approve_safety_checks=approve_safety_checks,
            before_action=before_action,
            ledger=ledger,
            context_budget=context_budget,
            on_diagnostic=on_diagnostic,
            approve_mcp=approve_mcp,
            before_early_call=before_early_call,
        )
        try:
            for turn in turns:
                if turn.final:
                    return turn.response
        finally:
            turns.close()
        raise AssertionError("unreachable")

    def iterate(
        self,
        client: OpenAI,
        params: ResponseCreateParamsNonStreaming,
        *,
        max_steps: int | None = None,
        stream: bool = False,
        eager: bool = False,
        max_concurrent_calls: int = 2,
        on_event: Callable[[ResponseStreamEvent[None]], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
        approve_safety_checks: Callable[[ResponseComputerToolCall], bool] | None = None,
        before_action: Callable[[ComputerActionInput], bool] | None = None,
        ledger: ResponsesToolLedger | None = None,
        context_budget: ContextBudget | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
        approve_mcp: Callable[[McpApprovalRequest], bool] | None = None,
        before_early_call: Callable[[ResponseFunctionToolCall | ResponseComputerToolCall], Literal["execute", "defer"]]
        | None = None,
    ) -> Generator[ResponsesRunnerTurn, None, None]:
        """Inspect complete turns before tools run; advance to execute them.

        supply_outputs replaces this turn's entire supplied-result set. A bare
        Python loop break does not close a retained generator. Use explicit
        close/aclose or contextlib.closing/aclosing for deterministic early exit.
        Eager execution may already have produced effects before yield.
        """
        self._lifecycle.enter()
        try:
            if type(max_concurrent_calls) is not int or max_concurrent_calls < 1:
                raise ValueError("max_concurrent_calls must be a positive integer.")
            stream, eager = bool(stream), bool(eager)
            browser, computer = self.browser, self.computer
            if ledger is not None and not isinstance(cast(object, ledger), ResponsesToolLedger):
                raise ValueError("A sync runner requires a sync ledger.")
            run = _Run(
                params,
                deepcopy(self._tools),
                self._functions,
                max_steps,
                stream,
                eager,
                cancelled,
                ledger,
                self._overrides,
                context_budget,
                self._browser_names,
                on_diagnostic,
            )
            collect = eager and ledger is not None
            has_server_tools = any(tool["type"] in _SERVER_TOOLS for tool in run.tools)
            # Record received evidence but defer effects until all server items pass preflight.
            eager = eager and not has_server_tools
            early = self._early_execution if eager else None
            if eager and early is None and before_early_call is not None:
                early = (
                    frozenset(tool["name"] for tool in self._tools if tool["type"] == "function"),
                    computer is not None,
                )
            selective = early is not None
            request_client = (
                client.with_options(max_retries=0)
                if ledger is not None or any(tool["type"] == "mcp" for tool in run.tools)
                else client
            )
        except BaseException:
            self._lifecycle.exit()
            raise
        jobs: list[tuple[ResponseFunctionToolCall, Future[FunctionCallOutput]]] = []
        pool: ThreadPoolExecutor | None = None

        def settle() -> None:
            pending, jobs[:] = jobs[:], []
            first: BaseException | None = None
            for item, job in pending:
                try:
                    run.add(item, job.result())
                except BaseException as exc:
                    if first is None:
                        first = exc
            if first is not None:
                raise first

        try:
            for answer, approval_request in run.approvals_to_refresh():
                answer["approve"] = self._approve_mcp(run, approval_request, approve_mcp)
            for step in range(run.consumed_requests, run.max_steps):
                run.begin(step == run.max_steps - 1)
                run.check()
                request = run.request.copy()
                if step > 0:
                    headers = rotated_idempotency_headers(
                        request_client, cast(Headers | None, request.get("extra_headers"))
                    )
                    if headers is not None:
                        cast(dict[str, object], request)["extra_headers"] = headers
                compact = run.context_snapshot()
                if compact is not None:
                    assert run.context_budget is not None and "compact" in run.context_budget
                    context, eligible = compact
                    decision = run.context_budget["compact"](context)
                    if isawaitable(decision):
                        if iscoroutine(decision):
                            decision.close()
                        raise run.error("A sync context_budget requires a synchronous compact callback.")
                    run.check()
                    request["input"] = run.context_input(decision, eligible)
                if ledger is not None:
                    run.consumed_requests = step + 1
                    phase: Literal["pending", "boundary"] = "pending" if has_server_tools else "boundary"
                    _save_sync(ledger, run.checkpoint(phase))
                    run.check()
                request_started = monotonic()
                try:
                    if stream:
                        raw = request_client.responses.create(
                            **cast(ResponseCreateParamsStreaming, {**request, "stream": True})
                        )
                        with ResponseStream[None](
                            raw_stream=raw, text_format=omit, input_tools=run.tools, starting_after=None
                        ) as events:
                            for event in events:
                                run.check()
                                # The consumer never receives the object used for dispatch.
                                if on_event is not None:
                                    on_event(model_copy(event, deep=True))
                                run.check()
                                if (eager or collect) and event.type == "response.output_item.done":
                                    item = (
                                        _snapshot_computer_call(event.item)
                                        if event.item.type == "computer_call"
                                        else event.item
                                    )
                                    if ledger is not None:
                                        if run.pending_items is None:
                                            run.pending_items = []
                                        run.pending_items.append(_wire(item))
                                        if len(run.pending_items) == 1 or item.type in _SERVER_ITEMS:
                                            _save_sync(ledger, run.checkpoint("pending"))
                                        run.check()
                                    if not eager:
                                        continue
                                    permitted = run.receive(event.output_index, item, early)
                                    if (
                                        permitted
                                        and before_early_call is not None
                                        and (item.type == "function_call" or item.type == "computer_call")
                                    ):
                                        early_decision: object = before_early_call(model_copy(item, deep=True))
                                        run.check()
                                        if type(early_decision) is not str or early_decision not in (
                                            "execute",
                                            "defer",
                                        ):
                                            raise run.error("before_early_call must return execute or defer.")
                                        if early_decision == "defer":
                                            run.deferred = True
                                            permitted = False
                                    if not permitted:
                                        settle()
                                    elif (
                                        ledger is None
                                        and item.type == "function_call"
                                        and item.name in self._functions
                                        and self._functions[item.name].independent
                                    ):
                                        run.accept(event.output_index, item)
                                        if pool is None:
                                            pool = ThreadPoolExecutor(max_workers=max_concurrent_calls)
                                        jobs.append(
                                            # Context.run forwards the callable result, which is FunctionCallOutput here.
                                            (item, pool.submit(copy_context().run, self._execute_function, run, item))  # ty: ignore[invalid-argument-type]
                                        )
                                        if len(jobs) == max_concurrent_calls:
                                            settle()
                                    else:
                                        settle()
                                        self._dispatch(
                                            run,
                                            browser,
                                            computer,
                                            event.output_index,
                                            item,
                                            approve_safety_checks,
                                            before_action,
                                            approve_mcp,
                                        )
                            settle()
                            response: Response = events.get_final_response()
                    else:
                        response = request_client.responses.create(**request)
                except (Exception, asyncio.CancelledError) as exc:
                    emit_tool_diagnostic(
                        on_diagnostic,
                        "responses",
                        "request",
                        "cancelled"
                        if isinstance(exc, (asyncio.CancelledError, ToolRunnerCancelledError))
                        else "api_failed",
                        request_started,
                    )
                    raise
                snapshot = _snapshot_computer_response(response)
                emit_tool_diagnostic(
                    on_diagnostic, "responses", "request", "completed", request_started, usage=snapshot.usage
                )
                run.check()
                if ledger is not None and any(
                    item.type in _SERVER_ITEMS
                    and (
                        getattr(item, "status", None) not in (None, "completed")
                        or getattr(item, "error", None) is not None
                    )
                    for item in snapshot.output
                ):
                    run.pending_items = [_wire(item) for item in snapshot.output]
                    _save_sync(ledger, run.checkpoint("pending"))
                final = run.preflight(snapshot, selective=eager)
                pending = not final and (not eager or len(run.items) < len(snapshot.output))
                if ledger is not None:
                    if not pending:
                        _save_sync(
                            ledger, run.checkpoint("final" if final else "boundary", snapshot if final else None)
                        )
                    else:
                        run.pending_items = [_wire(item) for item in snapshot.output]
                        _save_sync(ledger, run.checkpoint("pending"))
                    run.check()
                try:
                    yield run.turn(response, snapshot, step + 1, final, eager and not selective, self._overrides)
                finally:
                    run.active_step = None
                if final:
                    return
                if pending:
                    for index in range(len(run.items), len(snapshot.output)):
                        item = snapshot.output[index]
                        self._dispatch(
                            run,
                            browser,
                            computer,
                            index,
                            item,
                            approve_safety_checks,
                            before_action,
                            approve_mcp,
                        )
                    run.finish(snapshot)
                appended = run.append_boundary_text()
                if pending or appended:
                    if ledger is not None:
                        _save_sync(ledger, run.checkpoint("boundary"))
                        run.check()
        except ToolRunnerError as exc:
            try:
                settle()
            except BaseException:
                pass
            raise run.error(str(exc) if exc is run.last_error else "Tool run stopped before completion.") from None
        except asyncio.CancelledError:
            try:
                settle()
            except BaseException:
                pass
            raise ToolRunnerCancelledError(run.attempted, run.completed) from None
        except Exception:
            try:
                settle()
            except BaseException:
                pass
            raise run.error("Tool run stopped before completion.") from None
        finally:
            if pool is not None:
                pool.shutdown(wait=True)
            self._lifecycle.exit()
        raise run.error("Tool run reached max_steps before completion.")

    def _dispatch(
        self,
        run: _Run,
        browser: BrowserToolset | None,
        computer: ComputerToolset | None,
        index: int,
        item: ResponseOutputItem,
        approve_safety_checks: Callable[[ResponseComputerToolCall], bool] | None,
        before_action: Callable[[ComputerActionInput], bool] | None,
        approve_mcp: Callable[[McpApprovalRequest], bool] | None,
    ) -> None:
        if not run.accept(index, item):
            return
        if run.ledger is not None:
            if not isinstance(run.ledger, ResponsesToolLedger):
                raise AssertionError("A sync runner requires a sync ledger.")
            _save_sync(run.ledger, run.checkpoint("pending"))
            run.check()
        output: ToolOutput
        if item.type == "mcp_approval_request":
            approved = self._approve_mcp(run, item, approve_mcp)
            output = {"type": "mcp_approval_response", "approval_request_id": item.id, "approve": approved}
        elif item.type == "computer_call":
            if computer is None:
                raise run.error("No computer driver was registered.")
            output = computer.execute(
                item,
                approve_safety_checks=approve_safety_checks,
                before_action=before_action,
                cancelled=run.cancelled,
                on_diagnostic=run.on_diagnostic,
            )
        elif item.type == "function_call":
            if item.name in run.browser_names and browser is not None:
                output, ok = browser._execute(
                    item, skip=run.browser_failed, cancelled=run.cancelled, on_diagnostic=run.on_diagnostic
                )
                run.browser_failed |= not ok
            elif item.name in self._functions:
                if item.call_id in run.supplied:
                    output = run.supplied[item.call_id]
                else:
                    output = self._execute_function(run, item)
            else:
                raise run.error("Function was not registered.")
        else:
            raise AssertionError("accept allowed a non-tool")
        run.add(item, output)
        if run.ledger is not None:
            _save_sync(run.ledger, run.checkpoint("pending"))
            if run.browser_failed:
                raise run.error("Browser result requires reconciliation before another call.")
        run.check()

    @staticmethod
    def _approve_mcp(
        run: _Run, item: McpApprovalRequest, approve_mcp: Callable[[McpApprovalRequest], bool] | None
    ) -> bool:
        run.check()
        if approve_mcp is None:
            raise run.error("MCP approval requires an application callback.")
        started = monotonic()
        approved = approve_mcp(model_copy(item, deep=True))
        if type(approved) is not bool:
            raise run.error("MCP approval must return True or False.")
        run.check()
        emit_tool_diagnostic(
            run.on_diagnostic,
            "responses",
            "approval",
            "completed" if approved else "refused",
            started,
            call_id=item.id,
            member=item.name,
        )
        run.check()
        return approved

    def _execute_function(self, run: _Run, item: ResponseFunctionToolCall) -> FunctionCallOutput:
        function = self._functions[item.name]
        arguments = run.arguments[item.call_id]
        started = monotonic()
        try:
            raw_result = invoke(function.execute, arguments, cancelled=run.cancelled)
            if isawaitable(raw_result):
                if iscoroutine(raw_result):
                    raw_result.close()
                raise run.error(
                    "A synchronous function returned an awaitable; use AsyncRegisteredFunction with AsyncResponsesToolRunner."
                )
        except (Exception, asyncio.CancelledError):
            emit_tool_diagnostic(
                run.on_diagnostic,
                "responses",
                "action",
                "driver_failed",
                started,
                call_id=item.call_id,
                member=item.name,
            )
            raise
        output_started = monotonic()
        try:
            try:
                result = _supplied_result(raw_result)
            finally:
                emit_tool_diagnostic(
                    run.on_diagnostic,
                    "responses",
                    "action",
                    "completed",
                    started,
                    call_id=item.call_id,
                    member=item.name,
                )
        except Exception:
            emit_tool_diagnostic(
                run.on_diagnostic,
                "responses",
                "output",
                "invalid_output",
                output_started,
                call_id=item.call_id,
                member=item.name,
            )
            raise
        return {"type": "function_call_output", "call_id": item.call_id, "output": result}


class AsyncResponsesToolRunner:
    def __init__(
        self,
        *,
        browser: AsyncBrowserToolset | None = None,
        computer: AsyncComputerToolset | None = None,
        functions: list[AsyncRegisteredFunction] | None = None,
        early_execution: EarlyExecution | None = None,
    ) -> None:
        self._lifecycle = ToolLifecycle("Responses runner")
        selected = list(functions or [])
        self._tools = _registry(browser, computer, selected)
        self._early_execution = _early_execution(early_execution, self._tools)
        self._browser_names: frozenset[str] = (
            frozenset(tool["name"] for tool in browser.tools) if browser is not None else frozenset()
        )
        self.browser = browser
        self.computer = computer
        self._functions = {fn.tool["name"]: copy(fn) for fn in selected}
        self._overrides = frozenset(fn.tool["name"] for fn in selected if fn.allow_output_override)

    def close(self) -> CloseStatus:
        """Stop admission without taking ownership of the driver."""
        return self._lifecycle.close()

    async def run(
        self,
        client: AsyncOpenAI,
        params: ResponseCreateParamsNonStreaming,
        *,
        max_steps: int | None = None,
        stream: bool = False,
        eager: bool = False,
        max_concurrent_calls: int = 2,
        on_event: Callable[[ResponseStreamEvent[None]], Awaitable[None]] | None = None,
        cancelled: Callable[[], bool] | None = None,
        approve_safety_checks: Callable[[ResponseComputerToolCall], Awaitable[bool]] | None = None,
        before_action: Callable[[ComputerActionInput], Awaitable[bool]] | None = None,
        ledger: AsyncResponsesToolLedger | None = None,
        context_budget: AsyncContextBudget | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
        approve_mcp: Callable[[McpApprovalRequest], Awaitable[bool]] | None = None,
        before_early_call: Callable[
            [ResponseFunctionToolCall | ResponseComputerToolCall], Awaitable[Literal["execute", "defer"]]
        ]
        | None = None,
    ) -> Response:
        turns = self.iterate(
            client,
            params,
            max_steps=max_steps,
            stream=stream,
            eager=eager,
            max_concurrent_calls=max_concurrent_calls,
            on_event=on_event,
            cancelled=cancelled,
            approve_safety_checks=approve_safety_checks,
            before_action=before_action,
            ledger=ledger,
            context_budget=context_budget,
            on_diagnostic=on_diagnostic,
            approve_mcp=approve_mcp,
            before_early_call=before_early_call,
        )
        try:
            async for turn in turns:
                if turn.final:
                    return turn.response
        finally:
            await turns.aclose()
        raise AssertionError("unreachable")

    async def iterate(
        self,
        client: AsyncOpenAI,
        params: ResponseCreateParamsNonStreaming,
        *,
        max_steps: int | None = None,
        stream: bool = False,
        eager: bool = False,
        max_concurrent_calls: int = 2,
        on_event: Callable[[ResponseStreamEvent[None]], Awaitable[None]] | None = None,
        cancelled: Callable[[], bool] | None = None,
        approve_safety_checks: Callable[[ResponseComputerToolCall], Awaitable[bool]] | None = None,
        before_action: Callable[[ComputerActionInput], Awaitable[bool]] | None = None,
        ledger: AsyncResponsesToolLedger | None = None,
        context_budget: AsyncContextBudget | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
        approve_mcp: Callable[[McpApprovalRequest], Awaitable[bool]] | None = None,
        before_early_call: Callable[
            [ResponseFunctionToolCall | ResponseComputerToolCall], Awaitable[Literal["execute", "defer"]]
        ]
        | None = None,
    ) -> AsyncGenerator[ResponsesRunnerTurn, None]:
        """Inspect complete turns before tools run; advance to execute them.

        supply_outputs replaces this turn's entire supplied-result set. A bare
        Python loop break does not close a retained generator. Use explicit
        close/aclose or contextlib.closing/aclosing for deterministic early exit.
        Eager execution may already have produced effects before yield.
        """
        self._lifecycle.enter()
        try:
            if type(max_concurrent_calls) is not int or max_concurrent_calls < 1:
                raise ValueError("max_concurrent_calls must be a positive integer.")
            stream, eager = bool(stream), bool(eager)
            browser, computer = self.browser, self.computer
            if ledger is not None and not isinstance(cast(object, ledger), AsyncResponsesToolLedger):
                raise ValueError("An async runner requires an async ledger.")
            run = _Run(
                params,
                deepcopy(self._tools),
                self._functions,
                max_steps,
                stream,
                eager,
                cancelled,
                ledger,
                self._overrides,
                context_budget,
                self._browser_names,
                on_diagnostic,
            )
            collect = eager and ledger is not None
            has_server_tools = any(tool["type"] in _SERVER_TOOLS for tool in run.tools)
            # Record received evidence but defer effects until all server items pass preflight.
            eager = eager and not has_server_tools
            early = self._early_execution if eager else None
            if eager and early is None and before_early_call is not None:
                early = (
                    frozenset(tool["name"] for tool in self._tools if tool["type"] == "function"),
                    computer is not None,
                )
            selective = early is not None
            request_client = (
                client.with_options(max_retries=0)
                if ledger is not None or any(tool["type"] == "mcp" for tool in run.tools)
                else client
            )
        except BaseException:
            self._lifecycle.exit()
            raise
        jobs: list[tuple[ResponseFunctionToolCall, asyncio.Task[FunctionCallOutput]]] = []

        async def settle() -> None:
            first: BaseException | None = None
            while jobs:
                item, job = jobs[0]
                while not job.done():
                    try:
                        await asyncio.shield(job)
                    except asyncio.CancelledError as exc:
                        if first is None:
                            first = exc
                    except Exception:
                        # Retrieve the callback failure below, after the task is settled.
                        break
                try:
                    run.add(item, job.result())
                except BaseException as exc:
                    if first is None:
                        first = exc
                jobs.pop(0)
            if first is not None:
                raise first

        try:
            for answer, approval_request in run.approvals_to_refresh():
                answer["approve"] = await self._approve_mcp(run, approval_request, approve_mcp)
            for step in range(run.consumed_requests, run.max_steps):
                run.begin(step == run.max_steps - 1)
                run.check()
                request = run.request.copy()
                if step > 0:
                    headers = rotated_idempotency_headers(
                        request_client, cast(Headers | None, request.get("extra_headers"))
                    )
                    if headers is not None:
                        cast(dict[str, object], request)["extra_headers"] = headers
                compact = run.context_snapshot()
                if compact is not None:
                    assert run.context_budget is not None and "compact" in run.context_budget
                    context, eligible = compact
                    decision = run.context_budget["compact"](context)
                    if isawaitable(decision):
                        decision = await decision
                    run.check()
                    request["input"] = run.context_input(decision, eligible)
                if ledger is not None:
                    run.consumed_requests = step + 1
                    phase: Literal["pending", "boundary"] = "pending" if has_server_tools else "boundary"
                    await ledger.save(run.checkpoint(phase))
                    run.check()
                request_started = monotonic()
                try:
                    if stream:
                        raw = await request_client.responses.create(
                            **cast(ResponseCreateParamsStreaming, {**request, "stream": True})
                        )
                        async with AsyncResponseStream[None](
                            raw_stream=raw, text_format=omit, input_tools=run.tools, starting_after=None
                        ) as events:
                            async for event in events:
                                run.check()
                                if on_event is not None:
                                    await on_event(model_copy(event, deep=True))
                                run.check()
                                if (eager or collect) and event.type == "response.output_item.done":
                                    item = (
                                        _snapshot_computer_call(event.item)
                                        if event.item.type == "computer_call"
                                        else event.item
                                    )
                                    if ledger is not None:
                                        if run.pending_items is None:
                                            run.pending_items = []
                                        run.pending_items.append(_wire(item))
                                        if len(run.pending_items) == 1 or item.type in _SERVER_ITEMS:
                                            await ledger.save(run.checkpoint("pending"))
                                        run.check()
                                    if not eager:
                                        continue
                                    permitted = run.receive(event.output_index, item, early)
                                    if (
                                        permitted
                                        and before_early_call is not None
                                        and (item.type == "function_call" or item.type == "computer_call")
                                    ):
                                        early_decision: object = await before_early_call(model_copy(item, deep=True))
                                        run.check()
                                        if type(early_decision) is not str or early_decision not in (
                                            "execute",
                                            "defer",
                                        ):
                                            raise run.error("before_early_call must return execute or defer.")
                                        if early_decision == "defer":
                                            run.deferred = True
                                            permitted = False
                                    if not permitted:
                                        await settle()
                                    elif (
                                        ledger is None
                                        and item.type == "function_call"
                                        and item.name in self._functions
                                        and self._functions[item.name].independent
                                    ):
                                        run.accept(event.output_index, item)
                                        jobs.append((item, asyncio.create_task(self._execute_function(run, item))))
                                        if len(jobs) == max_concurrent_calls:
                                            await settle()
                                    else:
                                        await settle()
                                        await self._dispatch(
                                            run,
                                            browser,
                                            computer,
                                            event.output_index,
                                            item,
                                            approve_safety_checks,
                                            before_action,
                                            approve_mcp,
                                        )
                            await settle()
                            response: Response = await events.get_final_response()
                    else:
                        response = await request_client.responses.create(**request)
                except (Exception, asyncio.CancelledError) as exc:
                    emit_tool_diagnostic(
                        on_diagnostic,
                        "responses",
                        "request",
                        "cancelled"
                        if isinstance(exc, (asyncio.CancelledError, ToolRunnerCancelledError))
                        else "api_failed",
                        request_started,
                    )
                    raise
                snapshot = _snapshot_computer_response(response)
                emit_tool_diagnostic(
                    on_diagnostic, "responses", "request", "completed", request_started, usage=snapshot.usage
                )
                run.check()
                if ledger is not None and any(
                    item.type in _SERVER_ITEMS
                    and (
                        getattr(item, "status", None) not in (None, "completed")
                        or getattr(item, "error", None) is not None
                    )
                    for item in snapshot.output
                ):
                    run.pending_items = [_wire(item) for item in snapshot.output]
                    await ledger.save(run.checkpoint("pending"))
                final = run.preflight(snapshot, selective=eager)
                pending = not final and (not eager or len(run.items) < len(snapshot.output))
                if ledger is not None:
                    if not pending:
                        await ledger.save(run.checkpoint("final" if final else "boundary", snapshot if final else None))
                    else:
                        run.pending_items = [_wire(item) for item in snapshot.output]
                        await ledger.save(run.checkpoint("pending"))
                    run.check()
                try:
                    yield run.turn(response, snapshot, step + 1, final, eager and not selective, self._overrides)
                finally:
                    run.active_step = None
                if final:
                    return
                if pending:
                    for index in range(len(run.items), len(snapshot.output)):
                        item = snapshot.output[index]
                        await self._dispatch(
                            run,
                            browser,
                            computer,
                            index,
                            item,
                            approve_safety_checks,
                            before_action,
                            approve_mcp,
                        )
                    run.finish(snapshot)
                appended = run.append_boundary_text()
                if pending or appended:
                    if ledger is not None:
                        await ledger.save(run.checkpoint("boundary"))
                        run.check()
        except ToolRunnerError as exc:
            try:
                await settle()
            except BaseException:
                pass
            raise run.error(str(exc) if exc is run.last_error else "Tool run stopped before completion.") from None
        except asyncio.CancelledError:
            try:
                await settle()
            except BaseException:
                pass
            raise ToolRunnerCancelledError(run.attempted, run.completed) from None
        except Exception:
            try:
                await settle()
            except BaseException:
                pass
            raise run.error("Tool run stopped before completion.") from None
        finally:
            self._lifecycle.exit()
        raise run.error("Tool run reached max_steps before completion.")

    async def _dispatch(
        self,
        run: _Run,
        browser: AsyncBrowserToolset | None,
        computer: AsyncComputerToolset | None,
        index: int,
        item: ResponseOutputItem,
        approve_safety_checks: Callable[[ResponseComputerToolCall], Awaitable[bool]] | None,
        before_action: Callable[[ComputerActionInput], Awaitable[bool]] | None,
        approve_mcp: Callable[[McpApprovalRequest], Awaitable[bool]] | None,
    ) -> None:
        if not run.accept(index, item):
            return
        if run.ledger is not None:
            if not isinstance(run.ledger, AsyncResponsesToolLedger):
                raise AssertionError("An async runner requires an async ledger.")
            await run.ledger.save(run.checkpoint("pending"))
            run.check()
        output: ToolOutput
        if item.type == "mcp_approval_request":
            approved = await self._approve_mcp(run, item, approve_mcp)
            output = {"type": "mcp_approval_response", "approval_request_id": item.id, "approve": approved}
        elif item.type == "computer_call":
            if computer is None:
                raise run.error("No computer driver was registered.")
            output = await computer.execute(
                item,
                approve_safety_checks=approve_safety_checks,
                before_action=before_action,
                cancelled=run.cancelled,
                on_diagnostic=run.on_diagnostic,
            )
        elif item.type == "function_call":
            if item.name in run.browser_names and browser is not None:
                output, ok = await browser._execute(
                    item, skip=run.browser_failed, cancelled=run.cancelled, on_diagnostic=run.on_diagnostic
                )
                run.browser_failed |= not ok
            elif item.name in self._functions:
                if item.call_id in run.supplied:
                    output = run.supplied[item.call_id]
                else:
                    output = await self._execute_function(run, item)
            else:
                raise run.error("Function was not registered.")
        else:
            raise AssertionError("accept allowed a non-tool")
        run.add(item, output)
        if run.ledger is not None:
            await run.ledger.save(run.checkpoint("pending"))
            if run.browser_failed:
                raise run.error("Browser result requires reconciliation before another call.")
        run.check()

    @staticmethod
    async def _approve_mcp(
        run: _Run, item: McpApprovalRequest, approve_mcp: Callable[[McpApprovalRequest], Awaitable[bool]] | None
    ) -> bool:
        run.check()
        if approve_mcp is None:
            raise run.error("MCP approval requires an application callback.")
        started = monotonic()
        approved = await approve_mcp(model_copy(item, deep=True))
        if type(approved) is not bool:
            raise run.error("MCP approval must return True or False.")
        run.check()
        emit_tool_diagnostic(
            run.on_diagnostic,
            "responses",
            "approval",
            "completed" if approved else "refused",
            started,
            call_id=item.id,
            member=item.name,
        )
        run.check()
        return approved

    async def _execute_function(self, run: _Run, item: ResponseFunctionToolCall) -> FunctionCallOutput:
        function = self._functions[item.name]
        arguments = run.arguments[item.call_id]
        started = monotonic()
        try:
            result = await cast(Awaitable[FunctionResult], invoke(function.execute, arguments, cancelled=run.cancelled))
        except (Exception, asyncio.CancelledError):
            emit_tool_diagnostic(
                run.on_diagnostic,
                "responses",
                "action",
                "driver_failed",
                started,
                call_id=item.call_id,
                member=item.name,
            )
            raise
        output_started = monotonic()
        try:
            try:
                result = _supplied_result(result)
            finally:
                emit_tool_diagnostic(
                    run.on_diagnostic,
                    "responses",
                    "action",
                    "completed",
                    started,
                    call_id=item.call_id,
                    member=item.name,
                )
        except Exception:
            emit_tool_diagnostic(
                run.on_diagnostic,
                "responses",
                "output",
                "invalid_output",
                output_started,
                call_id=item.call_id,
                member=item.name,
            )
            raise
        return {"type": "function_call_output", "call_id": item.call_id, "output": result}
