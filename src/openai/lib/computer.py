"""Run the Responses computer tool with a caller-owned browser or desktop driver."""

from __future__ import annotations

import json
from abc import abstractmethod
from copy import deepcopy
from math import isfinite
from time import monotonic
from typing import Union, Callable, Iterable, Protocol, Awaitable, cast
from inspect import isawaitable, iscoroutine
from collections.abc import Mapping
from typing_extensions import TypeAlias

from .. import OpenAI, AsyncOpenAI
from .._types import Headers
from .._utils import transform
from .._compat import PYDANTIC_V1, model_copy, get_model_fields
from .._utils._json import openapi_dumps
from ._tool_lifecycle import CloseStatus, ToolLifecycle, invoke, callable_flavor, rotated_idempotency_headers
from ..types.responses import (
    Response,
    ResponseOutputItem,
    ResponseOutputText,
    ResponseOutputMessage,
    ResponseOutputRefusal,
    ResponseComputerToolCall,
    computer_action as modern,
    response_computer_tool_call as legacy,
)
from .tool_diagnostics import ToolDiagnosticObserver, emit_tool_diagnostic
from ..types.responses.tool_param import ToolParam
from ..types.responses.computer_action import ComputerAction
from ..types.responses.response_input_param import ComputerCallOutput, ResponseInputParam
from ..types.responses.response_output_text import (
    Logprob,
    LogprobTopLogprob,
    AnnotationFilePath,
    AnnotationURLCitation,
    AnnotationFileCitation,
    AnnotationContainerFileCitation,
)
from ..types.responses.response_create_params import ResponseCreateParamsNonStreaming
from ..types.responses.response_reasoning_item import Content, Summary, ResponseReasoningItem
from ..types.responses.tool_choice_allowed_param import ToolChoiceAllowedParam
from ..types.responses.response_computer_tool_call import Action
from ..types.responses.response_computer_tool_call_output_screenshot_param import (
    ResponseComputerToolCallOutputScreenshotParam,
)

ComputerActionInput: TypeAlias = Union[Action, ComputerAction]
Screenshot: TypeAlias = ResponseComputerToolCallOutputScreenshotParam

__all__ = [
    "ComputerActionInput",
    "Screenshot",
    "ComputerDriver",
    "AsyncComputerDriver",
    "ComputerToolset",
    "AsyncComputerToolset",
    "ComputerUseError",
]


class ComputerDriver(Protocol):
    """Implement each action used by your environment. Screenshots use native pixels.

    Drivers own permissions, bounds checks, waits, and cleanup. A method must raise
    if it cannot execute an action; do not silently ignore unsupported input.
    Approval covers action arguments, not a frozen screen. For target-specific
    consent, bind the target or reject the action after a state change.
    """

    @abstractmethod
    def click(self, action: Union[modern.Click, legacy.ActionClick]) -> None: ...
    @abstractmethod
    def double_click(self, action: Union[modern.DoubleClick, legacy.ActionDoubleClick]) -> None: ...
    @abstractmethod
    def drag(self, action: Union[modern.Drag, legacy.ActionDrag]) -> None: ...
    @abstractmethod
    def keypress(self, action: Union[modern.Keypress, legacy.ActionKeypress]) -> None: ...
    @abstractmethod
    def move(self, action: Union[modern.Move, legacy.ActionMove]) -> None: ...
    @abstractmethod
    def scroll(self, action: Union[modern.Scroll, legacy.ActionScroll]) -> None: ...
    @abstractmethod
    def type(self, action: Union[modern.Type, legacy.ActionType]) -> None: ...
    @abstractmethod
    def wait(self, action: Union[modern.Wait, legacy.ActionWait]) -> None: ...
    @abstractmethod
    def screenshot(self) -> Screenshot: ...


class AsyncComputerDriver(Protocol):
    """Asynchronous version of ComputerDriver, with caller-owned cleanup."""

    @abstractmethod
    async def click(self, action: Union[modern.Click, legacy.ActionClick]) -> None: ...
    @abstractmethod
    async def double_click(self, action: Union[modern.DoubleClick, legacy.ActionDoubleClick]) -> None: ...
    @abstractmethod
    async def drag(self, action: Union[modern.Drag, legacy.ActionDrag]) -> None: ...
    @abstractmethod
    async def keypress(self, action: Union[modern.Keypress, legacy.ActionKeypress]) -> None: ...
    @abstractmethod
    async def move(self, action: Union[modern.Move, legacy.ActionMove]) -> None: ...
    @abstractmethod
    async def scroll(self, action: Union[modern.Scroll, legacy.ActionScroll]) -> None: ...
    @abstractmethod
    async def type(self, action: Union[modern.Type, legacy.ActionType]) -> None: ...
    @abstractmethod
    async def wait(self, action: Union[modern.Wait, legacy.ActionWait]) -> None: ...
    @abstractmethod
    async def screenshot(self) -> Screenshot: ...


class ComputerUseError(RuntimeError):
    """A run stopped before completion. The last response is available for inspection."""

    def __init__(self, message: str, response: Response | None = None) -> None:
        super().__init__(message)
        self.response = response


def _prepare(params: ResponseCreateParamsNonStreaming, max_steps: object) -> ResponseCreateParamsNonStreaming:
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 1:
        raise ValueError("max_steps must be a positive integer")
    request = _snapshot_request(params)
    extra_body = cast(dict[str, object], request).get("extra_body")
    if isinstance(extra_body, Mapping) and {
        "stream",
        "background",
        "conversation",
        "previous_response_id",
        "tools",
        "input",
        "include",
        "tool_choice",
    }.intersection(cast(Mapping[str, object], extra_body)):
        raise ValueError("ComputerToolset extra_body cannot override runner-owned fields")
    if request.get("stream") or request.get("background"):
        raise ValueError("ComputerToolset requires non-streaming, foreground responses")
    if request.get("previous_response_id") or request.get("conversation"):
        raise ValueError("Pass complete input history; conversation and previous_response_id are not supported")
    configured_tools = request.get("tools")
    if configured_tools is None and "tools" in request:
        raise ValueError("ComputerToolset requires exactly one computer tool")
    tools: list[ToolParam] = [{"type": "computer"}] if configured_tools is None else list(configured_tools)
    if len(tools) != 1 or tools[0]["type"] not in {"computer", "computer_use_preview"}:
        raise ValueError("ComputerToolset requires exactly one computer tool")
    request["tools"] = tools
    request["stream"] = False
    original_input = request.get("input", [])
    request["input"] = (
        [{"role": "user", "content": original_input}] if isinstance(original_input, str) else list(original_input)
    )
    # Replay full history so the same loop works when response storage is disabled.
    request["include"] = list(dict.fromkeys([*(request.get("include") or []), "reasoning.encrypted_content"]))
    return request


def _rotate_computer_key(client: OpenAI | AsyncOpenAI, request: ResponseCreateParamsNonStreaming) -> None:
    headers = rotated_idempotency_headers(client, cast(Headers | None, request.get("extra_headers")))
    if headers is not None:
        # extra_headers is a native create option outside the generated body fields.
        cast(dict[str, object], request)["extra_headers"] = headers


def _snapshot_request(params: ResponseCreateParamsNonStreaming) -> ResponseCreateParamsNonStreaming:
    request = params.copy()
    original = request.get("input")
    if original is not None and not isinstance(original, str):
        request["input"] = list(original)
    tools = request.get("tools")
    if tools is not None:
        request["tools"] = list(tools)
    include = request.get("include")
    if include is not None:
        request["include"] = list(include)
    management = request.get("context_management")
    if management is not None:
        request["context_management"] = list(management)
    return deepcopy(transform(request, ResponseCreateParamsNonStreaming))


def _snapshot_call(call: ResponseComputerToolCall) -> ResponseComputerToolCall:
    # Construct no nested values: replay must preserve already parsed native
    # actions, including malformed custom-client values that validation rejects.
    if isinstance(cast(object, call), list):
        raise ComputerUseError("Invalid computer call")
    owned = ResponseComputerToolCall.construct()
    fields = get_model_fields(ResponseComputerToolCall)
    values = {name: getattr(call, name) for name in fields}
    checks = values["pending_safety_checks"]
    if isinstance(checks, list):
        source = cast(list[object], checks)
        projected: list[object] = []
        for index in range(len(source)):
            check = source[index]
            if isinstance(check, legacy.PendingSafetyCheck):
                canonical = legacy.PendingSafetyCheck.construct()
                check_values = {"id": check.id, "code": check.code, "message": check.message}
                object.__setattr__(canonical, "__dict__", {**check.__dict__, **check_values})
                canonical.model_fields_set.update(check.model_fields_set)
                if not PYDANTIC_V1:
                    object.__setattr__(canonical, "__pydantic_extra__", check.__pydantic_extra__)
                projected.append(canonical)
            else:
                # Keep malformed supplied values for _actions to reject, not coerce.
                projected.append(check)
        values["pending_safety_checks"] = projected
    # Preserve unknown wire fields as well as the canonical native fields.
    object.__setattr__(owned, "__dict__", deepcopy({**call.__dict__, **values}))
    owned.model_fields_set.update(call.model_fields_set)
    if not PYDANTIC_V1:
        object.__setattr__(owned, "__pydantic_extra__", deepcopy(call.__pydantic_extra__))
    return owned


def _snapshot_response(response: Response) -> Response:
    # Own declared native fields without re-running parsing. Subclass getters
    # or serialization hooks must not change the response after inspection.
    owned = Response.construct()
    status = response.status
    output = [
        _snapshot_call(item) if isinstance(item, ResponseComputerToolCall) else model_copy(item, deep=True)
        for item in response.output
    ]
    values = {name: getattr(response, name) for name in get_model_fields(Response) if name not in ("status", "output")}
    values.update(status=status, output=output)
    object.__setattr__(owned, "__dict__", deepcopy({**response.__dict__, **values}))
    owned.model_fields_set.update(response.model_fields_set)
    if not PYDANTIC_V1:
        object.__setattr__(owned, "__pydantic_extra__", deepcopy(response.__pydantic_extra__))
    return owned


def _valid_annotation(value: object) -> bool:
    kind = getattr(value, "type", None)
    strings: tuple[str, ...]
    integers: tuple[str, ...]
    if isinstance(value, AnnotationFileCitation) and kind == "file_citation":
        strings, integers = ("file_id", "filename"), ("index",)
    elif isinstance(value, AnnotationURLCitation) and kind == "url_citation":
        strings, integers = ("title", "url"), ("start_index", "end_index")
    elif isinstance(value, AnnotationContainerFileCitation) and kind == "container_file_citation":
        strings, integers = ("container_id", "file_id", "filename"), ("start_index", "end_index")
    elif isinstance(value, AnnotationFilePath) and kind == "file_path":
        strings, integers = ("file_id",), ("index",)
    else:
        return False
    return all(isinstance(getattr(value, name, None), str) for name in strings) and all(
        type(getattr(value, name, None)) is int for name in integers
    )


def _valid_logprob(value: object) -> bool:
    if not isinstance(value, (Logprob, LogprobTopLogprob)):
        return False
    token = getattr(value, "token", None)
    octets = getattr(value, "bytes", None)
    score = getattr(value, "logprob", None)
    return (
        isinstance(token, str)
        and isinstance(octets, list)
        and all(type(byte) is int for byte in cast(list[object], octets))
        and (type(score) is int or (type(score) is float and isfinite(score)))
    )


def _valid_native_message(item: ResponseOutputMessage) -> bool:
    if (
        not isinstance(getattr(item, "id", None), str)
        or getattr(item, "role", None) != "assistant"
        or getattr(item, "status", None) not in ("completed", "incomplete", "in_progress")
        or getattr(item, "phase", None) not in (None, "commentary", "final_answer")
        or not isinstance(getattr(item, "content", None), list)
    ):
        return False
    for part in item.content:
        if isinstance(part, ResponseOutputRefusal) and getattr(part, "type", None) == "refusal":
            if not isinstance(getattr(part, "refusal", None), str):
                return False
        elif isinstance(part, ResponseOutputText) and getattr(part, "type", None) == "output_text":
            annotations = getattr(part, "annotations", None)
            logprobs = getattr(part, "logprobs", None)
            if (
                not isinstance(getattr(part, "text", None), str)
                or not isinstance(annotations, list)
                or not all(_valid_annotation(annotation) for annotation in cast(list[object], annotations))
            ):
                return False
            if logprobs is not None:
                if not isinstance(logprobs, list):
                    return False
                for logprob in cast(list[object], logprobs):
                    top = getattr(logprob, "top_logprobs", None)
                    if (
                        not isinstance(logprob, Logprob)
                        or not _valid_logprob(logprob)
                        or not isinstance(top, list)
                        or not all(
                            isinstance(candidate, LogprobTopLogprob) and _valid_logprob(candidate)
                            for candidate in cast(list[object], top)
                        )
                    ):
                        return False
        else:
            return False
    return True


def _valid_native_reasoning(item: ResponseReasoningItem) -> bool:
    if (
        not isinstance(getattr(item, "id", None), str)
        or not isinstance(getattr(item, "summary", None), list)
        or any(
            not isinstance(cast(object, part), Summary)
            or getattr(part, "type", None) != "summary_text"
            or not isinstance(getattr(part, "text", None), str)
            for part in item.summary
        )
    ):
        return False
    if "content" in item.model_fields_set and (
        not isinstance(item.content, list)
        or any(
            not isinstance(cast(object, part), Content)
            or getattr(part, "type", None) != "reasoning_text"
            or not isinstance(getattr(part, "text", None), str)
            for part in item.content
        )
    ):
        return False
    return (item.encrypted_content is None or isinstance(cast(object, item.encrypted_content), str)) and (
        "status" not in item.model_fields_set or item.status in ("completed", "incomplete", "in_progress")
    )


def _calls(
    response: Response, last_step: bool, earlier_identities: set[str], earlier_call_ids: set[str]
) -> list[ResponseComputerToolCall]:
    if response.status != "completed":
        raise ComputerUseError("Response did not complete", response)
    calls: list[ResponseComputerToolCall] = []
    identities: set[str] = set()
    call_ids: set[str] = set()
    for item in response.output:
        if item.type == "computer_call":
            if item.status != "completed":
                raise ComputerUseError("Computer call did not complete", response)
            try:
                _actions(item)
            except ComputerUseError as exc:
                exc.response = response
                raise
            if item.call_id in call_ids or item.call_id in earlier_call_ids:
                raise ComputerUseError("Response has a duplicate computer call identity", response)
            call_ids.add(item.call_id)
            calls.append(item)
        elif item.type == "message":
            if not _valid_native_message(item):
                raise ComputerUseError("Response requires native assistant content before replay", response)
        elif item.type == "reasoning":
            if not _valid_native_reasoning(item):
                raise ComputerUseError("Response requires native reasoning content before replay", response)
        elif item.type == "compaction":
            if not isinstance(getattr(item, "id", None), str) or not isinstance(
                getattr(item, "encrypted_content", None), str
            ):
                raise ComputerUseError("Response requires native compaction content before replay", response)
        else:
            raise ComputerUseError("Response requires a tool this helper does not handle", response)
        if item.id in identities or (item.id != "" and item.id in earlier_identities):
            raise ComputerUseError("Response has a duplicate output item identity", response)
        identities.add(item.id)
    earlier_identities.update(identity for identity in identities if identity != "")
    earlier_call_ids.update(call_ids)
    if calls and last_step:
        raise ComputerUseError("Computer run reached max_steps before completion", response)
    if not calls and not any(
        item.type == "message" and item.status == "completed" and item.phase != "commentary" for item in response.output
    ):
        raise ComputerUseError("Response has no final message or computer call", response)
    return calls


def _initial_identities(request: ResponseCreateParamsNonStreaming) -> tuple[set[str], set[str]]:
    assert "input" in request  # _prepare captures and initializes replay history.
    identities: set[str] = set()
    call_ids: set[str] = set()
    for item in request["input"]:
        if isinstance(item, dict):
            identity = item.get("id")
            call_id = item.get("call_id")
            if isinstance(identity, str) and identity != "":
                identities.add(identity)
            if isinstance(call_id, str):
                call_ids.add(call_id)
    return identities, call_ids


def _actions(call: ResponseComputerToolCall) -> list[ComputerActionInput]:
    if not isinstance(cast(object, call.id), str):
        raise ComputerUseError("Computer call needs a string id")
    if not isinstance(cast(object, call.call_id), str):
        raise ComputerUseError("Computer call needs a string call_id")
    if (
        ("actions" in call.model_fields_set and call.actions is None)
        or ("action" in call.model_fields_set and call.action is None)
        or (call.actions is not None and call.action is not None)
    ):
        raise ComputerUseError("Computer call requires exactly one of action or actions")
    if call.actions is not None:
        actions: list[ComputerActionInput] = list(call.actions)
    elif call.action is not None:
        actions = [call.action]
    else:
        raise ComputerUseError("Computer call has no actions")
    if not actions:
        raise ComputerUseError("Computer call has no actions")
    # Modern responses can omit this legacy field entirely, but a supplied
    # field must be valid before any approvals or driver effects.
    if "pending_safety_checks" not in call.model_fields_set:
        if call.action is not None:
            raise ComputerUseError("Legacy computer call is missing safety checks")
    else:
        checks = cast(object, call.pending_safety_checks)
        if not isinstance(checks, list):
            raise ComputerUseError("Computer safety checks are malformed")
        for check in cast(list[object], checks):
            if (
                not isinstance(check, legacy.PendingSafetyCheck)
                or not isinstance(cast(object, check.id), str)
                or (check.code is not None and not isinstance(cast(object, check.code), str))
                or (check.message is not None and not isinstance(cast(object, check.message), str))
            ):
                raise ComputerUseError("Computer safety checks are malformed")
    for action in actions:
        if isinstance(action, list) or not _valid_action(action):
            raise ComputerUseError("Invalid computer action")
    return actions


def _integer_coordinate(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_point(point: object) -> bool:
    return (
        not isinstance(point, list)
        and _integer_coordinate(getattr(point, "x", None))
        and _integer_coordinate(getattr(point, "y", None))
    )


def _valid_action(action: ComputerActionInput) -> bool:
    keys: object = getattr(action, "keys", None)
    if keys is not None and (
        not isinstance(keys, list) or any(not isinstance(key, str) for key in cast(list[object], keys))
    ):
        return False
    if action.type == "click":
        return _valid_point(action) and action.button in {"left", "right", "wheel", "back", "forward"}
    if action.type in {"double_click", "move"}:
        return _valid_point(action)
    if action.type == "scroll":
        return _valid_point(action) and _integer_coordinate(action.scroll_x) and _integer_coordinate(action.scroll_y)
    if action.type == "drag":
        path = cast(object, action.path)
        return isinstance(path, list) and all(_valid_point(point) for point in cast(list[object], path))
    if action.type == "keypress":
        return isinstance(keys, list) and all(isinstance(key, str) for key in cast(list[object], keys))
    if action.type == "type":
        return isinstance(cast(object, action.text), str)
    return action.type in {"screenshot", "wait"}


def _reject_sync_awaitable(value: object) -> None:
    if isawaitable(value):
        if iscoroutine(value):
            value.close()
        raise ComputerUseError("Synchronous computer driver returned an awaitable; use AsyncComputerToolset.")


def _output(call: ResponseComputerToolCall, screenshot: object) -> ComputerCallOutput:
    if not isinstance(screenshot, dict):
        raise ComputerUseError("Driver must return a computer_screenshot with image_url or file_id")
    source = cast(dict[str, object], screenshot)
    image_url, file_id = source.get("image_url"), source.get("file_id")
    if (
        source.get("type") != "computer_screenshot"
        or (image_url is not None and (not isinstance(image_url, str) or not image_url.strip()))
        or (file_id is not None and (not isinstance(file_id, str) or not file_id.strip()))
        or (image_url is None and file_id is None)
    ):
        raise ComputerUseError("Driver must return a computer_screenshot with image_url or file_id")
    image: Screenshot = {"type": "computer_screenshot"}
    if image_url is not None:
        image["image_url"] = image_url
    if file_id is not None:
        image["file_id"] = file_id
    return {
        "type": "computer_call_output",
        "call_id": call.call_id,
        "output": image,
        "acknowledged_safety_checks": [
            {"id": check.id, "code": check.code, "message": check.message} for check in call.pending_safety_checks or []
        ],
    }


def _capture_replay(items: Iterable[ResponseOutputItem]) -> ResponseInputParam:
    replay: list[dict[str, object]] = []
    for item in items:
        data = item.to_dict(mode="python")
        data.pop("created_by", None)
        if item.type == "function_call":
            data.pop("parsed_arguments", None)
        replay.append(data)
    # Match the native transform and JSON encoder, keeping original callback models intact.
    native = transform(replay, ResponseInputParam)
    return cast(ResponseInputParam, json.loads(openapi_dumps(native)))


def _continue(request: ResponseCreateParamsNonStreaming, response: Response) -> ResponseInputParam:
    assert "input" in request  # _prepare always initializes the replay history.
    history = cast(ResponseInputParam, request["input"])
    # Only serialize this response, not all prior history.
    history.extend(_capture_replay(response.output))
    choice = request.get("tool_choice")
    if choice == "required" or (
        isinstance(choice, dict) and choice.get("type") in {"computer", "computer_use_preview", "computer_use"}
    ):
        request["tool_choice"] = "auto"
    elif isinstance(choice, dict) and choice.get("type") == "allowed_tools" and choice.get("mode") == "required":
        allowed = cast(ToolChoiceAllowedParam, choice)
        request["tool_choice"] = {"type": "allowed_tools", "tools": allowed["tools"], "mode": "auto"}
    return history


def _check_cancelled(cancelled: Callable[[], bool] | None, response: Response | None) -> None:
    if cancelled is not None and cancelled():
        raise ComputerUseError("Computer run was cancelled", response)


def _computer_handlers(
    driver: ComputerDriver | AsyncComputerDriver, *, asynchronous: bool
) -> dict[str, Callable[..., object]]:
    handlers: dict[str, Callable[..., object]] = {}
    for member in ("click", "double_click", "drag", "keypress", "move", "screenshot", "scroll", "type", "wait"):
        handler = getattr(driver, member, None)
        if not callable(handler):
            raise ValueError("Computer toolset requires callable computer driver methods.")
        returns_awaitable = callable_flavor(handler)
        if returns_awaitable is not None and returns_awaitable != asynchronous:
            correct = "AsyncComputerToolset" if returns_awaitable else "ComputerToolset"
            raise ValueError(f"Computer member {member!r} has the wrong method flavor; use {correct}.")
        handlers[member] = handler
    return handlers


class ComputerToolset:
    """Dispatch computer actions and run the non-streaming Responses loop.

    No browser is opened by this helper. Supply an isolated driver and call its
    cleanup method yourself. Use client.with_options() for HTTP request settings.
    """

    def __init__(self, driver: ComputerDriver) -> None:
        self.driver = driver
        self._handlers = _computer_handlers(driver, asynchronous=False)
        self._lifecycle = ToolLifecycle("Computer toolset")

    def close(self) -> CloseStatus:
        return self._lifecycle.close()

    def run(
        self,
        client: OpenAI,
        params: ResponseCreateParamsNonStreaming,
        *,
        max_steps: int = 20,
        approve_safety_checks: Callable[[ResponseComputerToolCall], bool] | None = None,
        before_action: Callable[[ComputerActionInput], bool] | None = None,
        cancelled: Callable[[], bool] | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
    ) -> Response:
        """Run until a final message. Policy callbacks must return exactly True.

        max_steps limits responses.create calls, including the final response.
        Client HTTP retry settings still apply to each call.

        Safety checks stop execution unless explicitly approved. before_action
        runs before every requested action and the final screenshot. It is
        the application's place to confirm consequential actions. Cancellation is
        cooperative between requests and driver calls; drivers must bound I/O.
        """
        self._lifecycle.enter()
        try:
            request = _prepare(params, max_steps)
            earlier_identities, earlier_call_ids = _initial_identities(request)
            response: Response | None = None
            for step in range(max_steps):
                _check_cancelled(cancelled, response)
                if step:
                    _rotate_computer_key(client, request)
                response = _snapshot_response(client.responses.create(**request))
                _check_cancelled(cancelled, response)
                calls = _calls(response, step == max_steps - 1, earlier_identities, earlier_call_ids)
                if not calls:
                    return response
                history = _continue(request, response)
                outputs: list[ComputerCallOutput] = []
                for call in calls:
                    try:
                        outputs.append(
                            self._dispatch(
                                call,
                                approve_safety_checks=approve_safety_checks,
                                before_action=before_action,
                                cancelled=cancelled,
                                on_diagnostic=on_diagnostic,
                            )
                        )
                    except ComputerUseError as exc:
                        exc.response = response
                        raise
                history.extend(outputs)
            raise AssertionError("unreachable")
        finally:
            self._lifecycle.exit()

    def execute(
        self,
        call: ResponseComputerToolCall,
        *,
        approve_safety_checks: Callable[[ResponseComputerToolCall], bool] | None = None,
        before_action: Callable[[ComputerActionInput], bool] | None = None,
        cancelled: Callable[[], bool] | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
    ) -> ComputerCallOutput:
        """Execute one complete call for applications that manage their own loop."""
        self._lifecycle.enter()
        try:
            return self._dispatch(
                _snapshot_call(call),
                approve_safety_checks=approve_safety_checks,
                before_action=before_action,
                cancelled=cancelled,
                on_diagnostic=on_diagnostic,
            )
        finally:
            self._lifecycle.exit()

    def _dispatch(
        self,
        call: ResponseComputerToolCall,
        *,
        approve_safety_checks: Callable[[ResponseComputerToolCall], bool] | None,
        before_action: Callable[[ComputerActionInput], bool] | None,
        cancelled: Callable[[], bool] | None,
        on_diagnostic: ToolDiagnosticObserver | None,
    ) -> ComputerCallOutput:
        call = model_copy(call, deep=True)
        if call.type != "computer_call" or call.status != "completed":
            raise ComputerUseError("Computer call did not complete")
        actions = _actions(call)
        _capture_replay([call])
        if actions[-1].type != "screenshot":
            actions.append(modern.Screenshot(type="screenshot"))
        _check_cancelled(cancelled, None)
        started = monotonic()
        if call.pending_safety_checks:
            try:
                approved = (
                    invoke(approve_safety_checks, model_copy(call, deep=True), cancelled=cancelled)
                    if approve_safety_checks is not None
                    else False
                )
                _check_cancelled(cancelled, None)
            except Exception:
                if cancelled is not None and cancelled():
                    emit_tool_diagnostic(
                        on_diagnostic, "computer", "approval", "cancelled", started, call_id=call.call_id
                    )
                    raise ComputerUseError("Computer run was cancelled") from None
                raise
            if approved is not True:
                emit_tool_diagnostic(on_diagnostic, "computer", "approval", "refused", started, call_id=call.call_id)
                raise ComputerUseError("Computer safety checks require explicit approval")
            emit_tool_diagnostic(on_diagnostic, "computer", "approval", "completed", started, call_id=call.call_id)
        for action in actions:
            _check_cancelled(cancelled, None)
            started = monotonic()
            if before_action is not None:
                try:
                    approved = invoke(before_action, model_copy(action, deep=True), cancelled=cancelled)
                    _check_cancelled(cancelled, None)
                except Exception:
                    if cancelled is not None and cancelled():
                        emit_tool_diagnostic(
                            on_diagnostic,
                            "computer",
                            "approval",
                            "cancelled",
                            started,
                            call_id=call.call_id,
                            member=action.type,
                        )
                        raise ComputerUseError("Computer run was cancelled") from None
                    raise
                if approved is not True:
                    emit_tool_diagnostic(
                        on_diagnostic,
                        "computer",
                        "approval",
                        "refused",
                        started,
                        call_id=call.call_id,
                        member=action.type,
                    )
                    raise ComputerUseError("Computer action was not approved")
                emit_tool_diagnostic(
                    on_diagnostic,
                    "computer",
                    "approval",
                    "completed",
                    started,
                    call_id=call.call_id,
                    member=action.type,
                )
            _check_cancelled(cancelled, None)
            if action.type == "screenshot":
                continue  # Capture the resulting screen once, after the whole batch.
            handler = self._handlers[action.type]
            started = monotonic()
            try:
                result = invoke(handler, model_copy(action, deep=True), cancelled=cancelled)
                _reject_sync_awaitable(result)
                _check_cancelled(cancelled, None)
            except Exception:
                stopped = cancelled is not None and cancelled()
                emit_tool_diagnostic(
                    on_diagnostic,
                    "computer",
                    "action",
                    "cancelled" if stopped else "driver_failed",
                    started,
                    call_id=call.call_id,
                    member=action.type,
                )
                if stopped:
                    raise ComputerUseError("Computer run was cancelled") from None
                raise
            emit_tool_diagnostic(
                on_diagnostic, "computer", "action", "completed", started, call_id=call.call_id, member=action.type
            )
        _check_cancelled(cancelled, None)
        started = monotonic()
        try:
            screenshot = invoke(self._handlers["screenshot"], cancelled=cancelled)
            _reject_sync_awaitable(screenshot)
            output = _output(call, screenshot)
            _check_cancelled(cancelled, None)
        except Exception:
            stopped = cancelled is not None and cancelled()
            emit_tool_diagnostic(
                on_diagnostic,
                "computer",
                "action",
                "cancelled" if stopped else "driver_failed",
                started,
                call_id=call.call_id,
                member="screenshot",
            )
            if stopped:
                raise ComputerUseError("Computer run was cancelled") from None
            raise
        emit_tool_diagnostic(
            on_diagnostic, "computer", "action", "completed", started, call_id=call.call_id, member="screenshot"
        )
        _check_cancelled(cancelled, None)
        return output


class AsyncComputerToolset:
    """Asynchronous ComputerToolset with the same approval and history behavior."""

    def __init__(self, driver: AsyncComputerDriver) -> None:
        self.driver = driver
        self._handlers = _computer_handlers(driver, asynchronous=True)
        self._lifecycle = ToolLifecycle("Computer toolset")

    def close(self) -> CloseStatus:
        return self._lifecycle.close()

    async def run(
        self,
        client: AsyncOpenAI,
        params: ResponseCreateParamsNonStreaming,
        *,
        max_steps: int = 20,
        approve_safety_checks: Callable[[ResponseComputerToolCall], Awaitable[bool]] | None = None,
        before_action: Callable[[ComputerActionInput], Awaitable[bool]] | None = None,
        cancelled: Callable[[], bool] | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
    ) -> Response:
        self._lifecycle.enter()
        try:
            request = _prepare(params, max_steps)
            earlier_identities, earlier_call_ids = _initial_identities(request)
            response: Response | None = None
            for step in range(max_steps):
                _check_cancelled(cancelled, response)
                if step:
                    _rotate_computer_key(client, request)
                response = _snapshot_response(await client.responses.create(**request))
                _check_cancelled(cancelled, response)
                calls = _calls(response, step == max_steps - 1, earlier_identities, earlier_call_ids)
                if not calls:
                    return response
                history = _continue(request, response)
                outputs: list[ComputerCallOutput] = []
                for call in calls:
                    try:
                        outputs.append(
                            await self._dispatch(
                                call,
                                approve_safety_checks=approve_safety_checks,
                                before_action=before_action,
                                cancelled=cancelled,
                                on_diagnostic=on_diagnostic,
                            )
                        )
                    except ComputerUseError as exc:
                        exc.response = response
                        raise
                history.extend(outputs)
            raise AssertionError("unreachable")
        finally:
            self._lifecycle.exit()

    async def execute(
        self,
        call: ResponseComputerToolCall,
        *,
        approve_safety_checks: Callable[[ResponseComputerToolCall], Awaitable[bool]] | None = None,
        before_action: Callable[[ComputerActionInput], Awaitable[bool]] | None = None,
        cancelled: Callable[[], bool] | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
    ) -> ComputerCallOutput:
        """Execute one complete call for applications that manage their own loop."""
        self._lifecycle.enter()
        try:
            return await self._dispatch(
                _snapshot_call(call),
                approve_safety_checks=approve_safety_checks,
                before_action=before_action,
                cancelled=cancelled,
                on_diagnostic=on_diagnostic,
            )
        finally:
            self._lifecycle.exit()

    async def _dispatch(
        self,
        call: ResponseComputerToolCall,
        *,
        approve_safety_checks: Callable[[ResponseComputerToolCall], Awaitable[bool]] | None,
        before_action: Callable[[ComputerActionInput], Awaitable[bool]] | None,
        cancelled: Callable[[], bool] | None,
        on_diagnostic: ToolDiagnosticObserver | None,
    ) -> ComputerCallOutput:
        call = model_copy(call, deep=True)
        if call.type != "computer_call" or call.status != "completed":
            raise ComputerUseError("Computer call did not complete")
        actions = _actions(call)
        _capture_replay([call])
        if actions[-1].type != "screenshot":
            actions.append(modern.Screenshot(type="screenshot"))
        _check_cancelled(cancelled, None)
        started = monotonic()
        if call.pending_safety_checks:
            try:
                approved = (
                    await cast(
                        Awaitable[bool], invoke(approve_safety_checks, model_copy(call, deep=True), cancelled=cancelled)
                    )
                    if approve_safety_checks is not None
                    else False
                )
                _check_cancelled(cancelled, None)
            except Exception:
                if cancelled is not None and cancelled():
                    emit_tool_diagnostic(
                        on_diagnostic, "computer", "approval", "cancelled", started, call_id=call.call_id
                    )
                    raise ComputerUseError("Computer run was cancelled") from None
                raise
            if approved is not True:
                emit_tool_diagnostic(on_diagnostic, "computer", "approval", "refused", started, call_id=call.call_id)
                raise ComputerUseError("Computer safety checks require explicit approval")
            emit_tool_diagnostic(on_diagnostic, "computer", "approval", "completed", started, call_id=call.call_id)
        for action in actions:
            _check_cancelled(cancelled, None)
            started = monotonic()
            if before_action is not None:
                try:
                    approved = await cast(
                        Awaitable[bool], invoke(before_action, model_copy(action, deep=True), cancelled=cancelled)
                    )
                    _check_cancelled(cancelled, None)
                except Exception:
                    if cancelled is not None and cancelled():
                        emit_tool_diagnostic(
                            on_diagnostic,
                            "computer",
                            "approval",
                            "cancelled",
                            started,
                            call_id=call.call_id,
                            member=action.type,
                        )
                        raise ComputerUseError("Computer run was cancelled") from None
                    raise
                if approved is not True:
                    emit_tool_diagnostic(
                        on_diagnostic,
                        "computer",
                        "approval",
                        "refused",
                        started,
                        call_id=call.call_id,
                        member=action.type,
                    )
                    raise ComputerUseError("Computer action was not approved")
                emit_tool_diagnostic(
                    on_diagnostic,
                    "computer",
                    "approval",
                    "completed",
                    started,
                    call_id=call.call_id,
                    member=action.type,
                )
            _check_cancelled(cancelled, None)
            if action.type == "screenshot":
                continue  # Capture the resulting screen once, after the whole batch.
            handler = self._handlers[action.type]
            started = monotonic()
            try:
                await cast(Awaitable[None], invoke(handler, model_copy(action, deep=True), cancelled=cancelled))
                _check_cancelled(cancelled, None)
            except Exception:
                stopped = cancelled is not None and cancelled()
                emit_tool_diagnostic(
                    on_diagnostic,
                    "computer",
                    "action",
                    "cancelled" if stopped else "driver_failed",
                    started,
                    call_id=call.call_id,
                    member=action.type,
                )
                if stopped:
                    raise ComputerUseError("Computer run was cancelled") from None
                raise
            emit_tool_diagnostic(
                on_diagnostic, "computer", "action", "completed", started, call_id=call.call_id, member=action.type
            )
        _check_cancelled(cancelled, None)
        started = monotonic()
        try:
            screenshot = await cast(Awaitable[Screenshot], invoke(self._handlers["screenshot"], cancelled=cancelled))
            output = _output(call, screenshot)
            _check_cancelled(cancelled, None)
        except Exception:
            stopped = cancelled is not None and cancelled()
            emit_tool_diagnostic(
                on_diagnostic,
                "computer",
                "action",
                "cancelled" if stopped else "driver_failed",
                started,
                call_id=call.call_id,
                member="screenshot",
            )
            if stopped:
                raise ComputerUseError("Computer run was cancelled") from None
            raise
        emit_tool_diagnostic(
            on_diagnostic, "computer", "action", "completed", started, call_id=call.call_id, member="screenshot"
        )
        _check_cancelled(cancelled, None)
        return output
