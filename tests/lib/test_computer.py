from __future__ import annotations

import json
import asyncio
import inspect
from copy import deepcopy
from typing import Any, Callable, Awaitable, cast
from datetime import datetime, timezone
from collections.abc import Mapping, Iterator
from typing_extensions import override

import httpx2
import pytest

from openai import Omit, OpenAI, AsyncOpenAI
from openai._compat import PYDANTIC_V1, get_model_fields
from openai.lib.computer import (
    Screenshot,
    ComputerToolset,
    ComputerUseError,
    ComputerActionInput,
    AsyncComputerToolset,
)
from openai.types.responses import Response, ResponseComputerToolCall
from openai.lib.responses_tool_runner import ToolRunnerError, ResponsesToolRunner, AsyncResponsesToolRunner
from openai.types.responses.computer_action import Type, Wait, Click, Keypress, DoubleClick, ComputerAction
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

SCREENSHOT: Screenshot = {"type": "computer_screenshot", "image_url": "data:image/png;base64,c2NyZWVu"}


def approve_checks(_call: ResponseComputerToolCall) -> bool:
    return True


def deny_checks(_call: ResponseComputerToolCall) -> bool:
    return False


def invalid_approval(_call: ResponseComputerToolCall) -> int:
    return 1


def stop_before_typing(action: ComputerActionInput) -> bool:
    return action.type != "type"


def deny_screenshot(action: ComputerActionInput) -> bool:
    return action.type != "screenshot"


class Driver:
    def __init__(self, fail: bool = False) -> None:
        self.actions: list[str] = []
        self.fail = fail

    def record(self, action: ComputerActionInput) -> None:
        self.actions.append(action.type)
        if self.fail:
            raise RuntimeError("driver failed")

    click = double_click = drag = keypress = move = scroll = type = wait = record

    def screenshot(self) -> Screenshot:
        self.actions.append("screenshot")
        return SCREENSHOT.copy()


class AsyncDriver:
    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    async def record(self, action: ComputerActionInput) -> None:
        self.driver.record(action)

    click = double_click = drag = keypress = move = scroll = type = wait = record

    async def screenshot(self) -> Screenshot:
        return self.driver.screenshot()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("shape", ["native-empty", "list-call"])
async def test_direct_computer_native_call_shape_and_empty_id(mode: str, shape: str) -> None:
    driver = Driver()
    pending = ResponseComputerToolCall(**call(call_id="" if shape == "native-empty" else "list_fixture"))
    if shape == "list-call":

        class ListCall(list[object]):
            pass

        supplied = ListCall()
        for name in get_model_fields(ResponseComputerToolCall):
            setattr(supplied, name, getattr(pending, name))
        setattr(supplied, "model_fields_set", set(pending.model_fields_set))  # noqa: B010
        if not PYDANTIC_V1:
            setattr(supplied, "__pydantic_extra__", deepcopy(pending.__pydantic_extra__))  # noqa: B010
        pending = cast(ResponseComputerToolCall, supplied)
    approvals: list[str] = []

    def approve(action: ComputerActionInput) -> bool:
        approvals.append(action.type)
        return True

    async def async_approve(action: ComputerActionInput) -> bool:
        return approve(action)

    async def invoke() -> object:
        if mode == "sync":
            return ComputerToolset(driver).execute(pending, before_action=approve)
        return await AsyncComputerToolset(AsyncDriver(driver)).execute(pending, before_action=async_approve)

    if shape == "list-call":
        with pytest.raises(ComputerUseError, match="Invalid computer call"):
            await invoke()
        assert not approvals and not driver.actions
    else:
        returned = cast(dict[str, object], await invoke())
        assert returned["call_id"] == "" and approvals == driver.actions == ["click", "type", "screenshot"]


@pytest.mark.parametrize("member", ["wait", "screenshot"])
@pytest.mark.parametrize("kind", ["coroutine", "future"])
async def test_sync_driver_awaitable_refusal_releases_admission(member: str, kind: str) -> None:
    from openai.lib.tool_diagnostics import ToolDiagnostic

    driver = Driver()
    original = cast(Callable[..., object], getattr(driver, member))
    captured: list[Awaitable[object]] = []
    events: list[ToolDiagnostic] = []
    broken = True

    async def deferred() -> Screenshot:
        driver.actions.append("deferred")
        return SCREENSHOT.copy()

    def perform(*args: object) -> object:
        if broken:
            result: Awaitable[object] = (
                deferred() if kind == "coroutine" else asyncio.get_running_loop().create_future()
            )
            captured.append(result)
            return result
        return original(*args)

    setattr(driver, member, perform)
    tools = ComputerToolset(driver)
    pending = ResponseComputerToolCall(**call(actions=[{"type": member}]))
    with pytest.raises(ComputerUseError, match="use AsyncComputerToolset"):
        tools.execute(pending, on_diagnostic=events.append)
    assert driver.actions == []
    assert [(event["stage"], event.get("member"), event["reason"]) for event in events] == [
        ("action", member, "driver_failed")
    ]
    value = captured[0]
    if inspect.iscoroutine(value):
        assert inspect.getcoroutinestate(value) == inspect.CORO_CLOSED
    else:
        assert isinstance(value, asyncio.Future) and not value.done()
        value.set_result("caller completed")
        assert value.result() == "caller completed"
    broken = False
    assert tools.execute(pending)["output"] == SCREENSHOT
    assert tools.close() == {"status": "closed"}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("legacy", [False, True])
async def test_direct_replay_rejects_list_drag_points_before_effects(mode: str, legacy: bool) -> None:
    class ListPoint(list[object]):
        def __init__(self) -> None:
            super().__init__()
            self.x = -1
            self.y = 2

    driver = Driver()
    drag = {"type": "drag", "path": [{"x": -1, "y": 2}]}
    pending = ResponseComputerToolCall(**(call(legacy=True, action=drag) if legacy else call(actions=[drag])))
    if legacy:
        action: Any = pending.action
    else:
        assert pending.actions is not None
        action = pending.actions[0]
    action.path = [ListPoint()]
    if mode == "sync":
        with pytest.raises(ComputerUseError, match="Invalid computer action"):
            ComputerToolset(driver).execute(pending)
    else:
        with pytest.raises(ComputerUseError, match="Invalid computer action"):
            await AsyncComputerToolset(AsyncDriver(driver)).execute(pending)
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("where", ["first", "later", "call", "check"])
async def test_direct_replay_preflights_non_json_extensions(mode: str, where: str) -> None:
    driver = Driver()
    pending = ResponseComputerToolCall(
        **call(checks=where == "check", actions=[{"type": "wait"}, {"type": "click", "x": 1, "y": 2, "button": "left"}])
    )
    assert pending.actions is not None
    if where == "check":
        assert pending.pending_safety_checks
        target: Any = pending.pending_safety_checks[0]
    else:
        target = pending if where == "call" else pending.actions[0 if where == "first" else 1]
    setattr(target, "audit", object())  # noqa: B010
    approvals: list[str] = []

    def approve_safety(_call: ResponseComputerToolCall) -> bool:
        approvals.append("safety")
        return True

    async def approve_safety_async(value: ResponseComputerToolCall) -> bool:
        return approve_safety(value)

    def approve(action: ComputerActionInput) -> bool:
        approvals.append(action.type)
        return True

    async def approve_async(action: ComputerActionInput) -> bool:
        return approve(action)

    if mode == "sync":
        with pytest.raises((TypeError, ValueError)):
            ComputerToolset(driver).execute(pending, approve_safety_checks=approve_safety, before_action=approve)
    else:
        with pytest.raises((TypeError, ValueError)):
            await AsyncComputerToolset(AsyncDriver(driver)).execute(
                pending, approve_safety_checks=approve_safety_async, before_action=approve_async
            )
    assert approvals == []
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_direct_replay_preserves_native_date_and_output_metadata(mode: str) -> None:
    driver = Driver()
    pending = ResponseComputerToolCall(**call(actions=[{"type": "wait"}]))
    assert pending.actions is not None
    at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    setattr(pending.actions[0], "audit", {"at": at, "details": ["kept", None, 7]})  # noqa: B010
    setattr(pending, "created_by", object())  # noqa: B010
    values: list[object] = []

    def approve(action: ComputerActionInput) -> bool:
        if action.type == "wait":
            values.append(getattr(action, "audit"))  # noqa: B009
        return True

    async def approve_async(action: ComputerActionInput) -> bool:
        return approve(action)

    if mode == "sync":
        ComputerToolset(driver).execute(pending, before_action=approve)
    else:
        await AsyncComputerToolset(AsyncDriver(driver)).execute(pending, before_action=approve_async)
    assert values == [{"at": at, "details": ["kept", None, 7]}]
    assert driver.actions == ["wait", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("location", ["call", "message"])
async def test_custom_output_serialization_stops_before_computer_effects(
    mode: str, location: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []

    def transport(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        return httpx2.Response(200, json=response([call(actions=[{"type": "wait"}]), *FINAL["output"]]))

    if mode == "sync":
        with OpenAI(api_key="fixture", http_client=httpx2.Client(transport=httpx2.MockTransport(transport))) as client:
            original = cast(Callable[..., Response], client.responses.create)

            def reply(**kwargs: Any) -> Response:
                value = original(**kwargs)
                target = value.output[0 if location == "call" else 1]
                # Native models accept extensions; static model members do not declare this field.
                setattr(target, "database_revision", object())  # noqa: B010
                return value

            monkeypatch.setattr(client.responses, "create", reply)
            with pytest.raises((ComputerUseError, TypeError, ValueError)):
                ComputerToolset(driver).run(client, {"model": "", "input": "fixture"})
    else:
        async with AsyncOpenAI(
            api_key="fixture", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport))
        ) as client_async:
            original_async = cast(Callable[..., Awaitable[Response]], client_async.responses.create)

            async def reply_async(**kwargs: Any) -> Response:
                value = await original_async(**kwargs)
                target = value.output[0 if location == "call" else 1]
                setattr(target, "database_revision", object())  # noqa: B010
                return value

            monkeypatch.setattr(client_async.responses, "create", reply_async)
            with pytest.raises((ComputerUseError, TypeError, ValueError)):
                await AsyncComputerToolset(AsyncDriver(driver)).run(client_async, {"model": "", "input": "fixture"})
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_native_encoder_date_and_json_extras_survive_computer_replay(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []

    def transport(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        output = response([call(actions=[{"type": "wait"}])]) if len(requests) == 1 else FINAL
        return httpx2.Response(200, json=output)

    if mode == "sync":
        with OpenAI(api_key="fixture", http_client=httpx2.Client(transport=httpx2.MockTransport(transport))) as client:
            original = cast(Callable[..., Response], client.responses.create)

            def reply(**kwargs: Any) -> Response:
                value = original(**kwargs)
                if len(requests) == 1:
                    setattr(  # noqa: B010
                        value.output[0],
                        "audit",
                        {
                            "at": datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
                            "fields": ["kept", None, 7],
                        },
                    )
                return value

            monkeypatch.setattr(client.responses, "create", reply)
            ComputerToolset(driver).run(client, {"model": "", "input": "fixture"})
    else:
        async with AsyncOpenAI(
            api_key="fixture", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport))
        ) as client_async:
            original_async = cast(Callable[..., Awaitable[Response]], client_async.responses.create)

            async def reply_async(**kwargs: Any) -> Response:
                value = await original_async(**kwargs)
                if len(requests) == 1:
                    setattr(  # noqa: B010
                        value.output[0],
                        "audit",
                        {
                            "at": datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
                            "fields": ["kept", None, 7],
                        },
                    )
                return value

            monkeypatch.setattr(client_async.responses, "create", reply_async)
            await AsyncComputerToolset(AsyncDriver(driver)).run(client_async, {"model": "", "input": "fixture"})
    assert driver.actions == ["wait", "screenshot"]
    assert requests[1]["input"][1]["audit"] == {"at": "2026-01-02T03:04:05+00:00", "fields": ["kept", None, 7]}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("stage", ["safety", "action"])
async def test_computer_approval_receives_the_optional_cancellation_probe(mode: str, stage: str) -> None:
    from openai.lib.tool_diagnostics import ToolDiagnostic

    driver = Driver()
    stopped = False
    seen: list[Callable[[], bool] | None] = []
    diagnostics: list[ToolDiagnostic] = []
    pending = ResponseComputerToolCall.construct(
        **call(pending_safety_checks=[{"id": "review", "code": None, "message": None}])
    )

    def check() -> bool:
        return stopped

    def approve(_value: object, *, cancelled: Callable[[], bool] | None = None) -> bool:
        nonlocal stopped
        seen.append(cancelled)
        stopped = cancelled is check
        return True

    async def async_approve(_value: object, *, cancelled: Callable[[], bool] | None = None) -> bool:
        return approve(_value, cancelled=cancelled)

    with pytest.raises(ComputerUseError, match="cancelled"):
        if mode == "sync":
            ComputerToolset(driver).execute(
                pending,
                cancelled=check,
                approve_safety_checks=approve if stage == "safety" else approve_checks,
                before_action=approve if stage == "action" else None,
                on_diagnostic=diagnostics.append,
            )
        else:

            async def allow(_call: ResponseComputerToolCall) -> bool:
                return True

            await AsyncComputerToolset(AsyncDriver(driver)).execute(
                pending,
                cancelled=check,
                approve_safety_checks=async_approve if stage == "safety" else allow,
                before_action=async_approve if stage == "action" else None,
                on_diagnostic=diagnostics.append,
            )
    assert seen == [check]
    assert driver.actions == []
    assert diagnostics[-1]["stage"] == "approval" and diagnostics[-1]["reason"] == "cancelled"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("stage", ["safety", "action"])
async def test_legacy_callback_positional_parameter_may_be_named_cancelled(mode: str, stage: str) -> None:
    driver = Driver()
    received: list[ResponseComputerToolCall | ComputerActionInput] = []
    pending = ResponseComputerToolCall.construct(
        **call(pending_safety_checks=[{"id": "review", "code": None, "message": None}])
    )

    def approve(cancelled: ResponseComputerToolCall | ComputerActionInput) -> bool:
        received.append(cancelled)
        return True

    async def async_approve(cancelled: ResponseComputerToolCall | ComputerActionInput) -> bool:
        return approve(cancelled)

    async def allow(_call: ResponseComputerToolCall) -> bool:
        return True

    if mode == "sync":
        ComputerToolset(driver).execute(
            pending,
            cancelled=lambda: False,
            approve_safety_checks=approve if stage == "safety" else approve_checks,
            before_action=approve if stage == "action" else None,
        )
    else:
        await AsyncComputerToolset(AsyncDriver(driver)).execute(
            pending,
            cancelled=lambda: False,
            approve_safety_checks=async_approve if stage == "safety" else allow,
            before_action=async_approve if stage == "action" else None,
        )
    assert [item.type for item in received] == (["computer_call"] if stage == "safety" else driver.actions)
    assert driver.actions[-1] == "screenshot"


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_native_missing_id_blocks_the_entire_batch_before_driver_effects(mode: str) -> None:
    driver = Driver()
    with pytest.raises(ComputerUseError, match="string id"):
        await run(mode, driver, [response([call(), call(id=None, call_id="second")])], [])
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_empty_native_id_remains_a_valid_string(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    await run(mode, driver, [response([call(id="")]), FINAL], requests)
    assert len(requests) == 2
    assert driver.actions


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_am_repeated_nonempty_output_identity_stops_later_effects(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError, match="duplicate output item identity"):
        await run(
            mode,
            driver,
            [response([call(actions=[{"type": "wait"}])]), response([call(call_id="next")]), FINAL],
            requests,
        )
    assert len(requests) == 2
    assert driver.actions == ["wait", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_am_separately_returned_empty_native_ids_keep_compatibility(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    await run(
        mode, driver, [response([call(id="", call_id="one")]), response([call(id="", call_id="two")]), FINAL], requests
    )
    assert len(requests) == 3


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("where", ["same", "later"])
async def test_fr_repeated_call_id_refuses_batch_before_effects(mode: str, where: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    first = call(actions=[{"type": "wait"}])
    second = call(id="cu_second")
    replies = [response([first, second]), FINAL] if where == "same" else [response([first]), response([second]), FINAL]
    with pytest.raises(ComputerUseError, match="duplicate computer call identity"):
        await run(mode, driver, replies, requests)
    assert driver.actions == ([] if where == "same" else ["wait", "screenshot"])
    assert len(requests) == (1 if where == "same" else 2)


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "source",
    ["complete-pair", "complete-empty-call", "output-only", "output-id", "reference-id"],
)
async def test_initial_history_reserves_computer_identities_before_first_effect(mode: str, source: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    approvals: list[str] = []
    call_id = "" if source == "complete-empty-call" else "prior"
    history: list[dict[str, Any]] = [
        call(id="prior-item", call_id=call_id, actions=[{"type": "wait"}]),
        {"type": "computer_call_output", "call_id": call_id, "output": SCREENSHOT.copy()},
    ]
    incoming = call(id="new-item", call_id=call_id, checks=True)
    expected = "duplicate computer call identity"
    if source == "output-only":
        history = [history[1]]
    if source in ("output-id", "reference-id"):
        incoming = call(id="prior-item", call_id="new-call", checks=True)
        expected = "duplicate output item identity"
        if source == "reference-id":
            history = [{"type": "item_reference", "id": "prior-item"}]

    def approval(value: object) -> bool:
        approvals.append(type(value).__name__)
        return True

    with pytest.raises(ComputerUseError, match=expected) as error:
        await run(
            mode,
            driver,
            [response([incoming]), FINAL],
            requests,
            params={"input": history},
            approve_safety_checks=approval,
            before_action=approval,
        )
    assert error.value.response is not None
    assert len(requests) == 1 and requests[0]["input"] == history
    assert approvals == [] and driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("source", ["fresh", "empty-item", "identity-namespaces", "legacy-history"])
async def test_initial_history_keeps_fresh_computer_calls_and_empty_item_ids(mode: str, source: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = [
        call(
            legacy=source == "legacy-history", id="" if source == "empty-item" else "prior-item", call_id="prior-call"
        ),
        {"type": "computer_call_output", "call_id": "prior-call", "output": SCREENSHOT.copy()},
    ]
    incoming = call(id="new-item", call_id="new-call", actions=[{"type": "wait"}])
    if source == "empty-item":
        incoming = call(id="", call_id="", actions=[{"type": "wait"}])
    if source == "identity-namespaces":
        incoming = call(id="prior-call", call_id="prior-item", actions=[{"type": "wait"}])
    result = await run(mode, driver, [response([incoming]), FINAL], requests, params={"input": history})
    assert result.output_text == "Done"
    assert len(requests) == 2 and requests[0]["input"] == history
    assert requests[1]["input"][: len(history)] == history
    assert driver.actions == ["wait", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("operation", ["execute", "run"])
async def test_fr_empty_safety_id_and_native_output_projection(mode: str, operation: str) -> None:
    driver = Driver()
    checks = [{"id": "", "code": None, "message": None}]
    wire = call(actions=[{"type": "wait"}], pending_safety_checks=checks)
    if operation == "run":
        requests: list[dict[str, Any]] = []
        await run(mode, driver, [response([wire]), FINAL], requests, approve_safety_checks=approve_checks)
        out = next(item for item in requests[1]["input"] if item.get("type") == "computer_call_output")
    else:
        pending = ResponseComputerToolCall(**wire)
        assert pending.pending_safety_checks
        # Replay accepts JSON extras, but acknowledged checks expose only id/code/message.
        setattr(pending.pending_safety_checks[0], "opaque_extension", {"value": ["fixture", None, 1]})  # noqa: B010
        if mode == "sync":
            out = ComputerToolset(driver).execute(pending, approve_safety_checks=approve_checks)
        else:

            async def allow(value: ResponseComputerToolCall) -> bool:
                return approve_checks(value)

            out = await AsyncComputerToolset(AsyncDriver(driver)).execute(pending, approve_safety_checks=allow)
        json.dumps(out)
    assert out.get("acknowledged_safety_checks") == checks
    assert driver.actions == ["wait", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("source", ["default", "request", "remove", "none"])
async def test_continuation_idempotency_uses_effective_client_headers(mode: str, source: str) -> None:
    driver = Driver()
    sent: list[httpx2.Headers] = []
    reports: list[int] = []

    class FixtureClient(OpenAI):
        @property
        @override
        def default_headers(self) -> dict[str, str | Omit]:
            reports.append(len(reports) + 1)
            return {**super().default_headers, "x-prepared": str(reports[-1])}

    class AsyncFixtureClient(AsyncOpenAI):
        @property
        @override
        def default_headers(self) -> dict[str, str | Omit]:
            reports.append(len(reports) + 1)
            return {**super().default_headers, "x-prepared": str(reports[-1])}

    def transport(request: httpx2.Request) -> httpx2.Response:
        sent.append(request.headers)
        output = (
            [call(id=f"cu_{len(sent)}", call_id=f"call_{len(sent)}", actions=[{"type": "wait"}])]
            if len(sent) < 3
            else FINAL["output"]
        )
        return httpx2.Response(200, json=response(output))

    defaults = {"x-default": "remove-this", "x-kept": "client"}
    if source != "none":
        defaults["Idempotency-Key"] = "client-fixed"
    extra: dict[str, str | Omit] = {"x-default": Omit()}
    if source == "request":
        extra["IDEMPOTENCY-KEY"] = "request-first"
    elif source == "remove":
        extra["idempotency-key"] = Omit()
    params = cast(ResponseCreateParamsNonStreaming, {"model": "", "input": "fixture", "extra_headers": extra})
    if mode == "sync":
        with FixtureClient(
            api_key="fixture",
            max_retries=0,
            default_headers=defaults,
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:
            ComputerToolset(driver).run(client, params)
    else:
        async with AsyncFixtureClient(
            api_key="fixture",
            max_retries=0,
            default_headers=defaults,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
        ) as async_client:
            await AsyncComputerToolset(AsyncDriver(driver)).run(async_client, params)
    keys = [headers.get("idempotency-key") for headers in sent]
    if source in ("remove", "none"):
        assert keys == [None, None, None]
    else:
        assert keys[0] == ("request-first" if source == "request" else "client-fixed")
        assert all(keys) and len(set(keys)) == 3
    assert reports == [1, 2, 3]
    assert [headers.get("x-prepared") for headers in sent] == ["1", "2", "3"]
    assert [headers.get("x-default") for headers in sent] == [None, None, None]
    assert [headers.get("x-kept") for headers in sent] == ["client", "client", "client"]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_continuation_dispatch_uses_the_inspected_header_values(mode: str) -> None:
    driver = Driver()
    sent: list[httpx2.Headers] = []

    class ChangingHeaders(Mapping[str, str | Omit]):
        continuation_reads = 0

        @override
        def __len__(self) -> int:
            return 2

        @override
        def __iter__(self) -> Iterator[str]:
            return iter(("Idempotency-Key", "x-kept"))

        @override
        def __getitem__(self, key: str) -> str | Omit:
            if key == "x-kept":
                return "request"
            if key != "Idempotency-Key":
                raise KeyError(key)
            if driver.actions:
                self.continuation_reads += 1
                if self.continuation_reads == 1:
                    return Omit()
            return "original-request"

    extra = ChangingHeaders()

    def transport(request: httpx2.Request) -> httpx2.Response:
        sent.append(request.headers)
        output = [call(actions=[{"type": "wait"}])] if len(sent) == 1 else FINAL["output"]
        return httpx2.Response(200, json=response(output))

    params = cast(ResponseCreateParamsNonStreaming, {"model": "", "input": "fixture", "extra_headers": extra})
    if mode == "sync":
        with OpenAI(
            api_key="fixture", max_retries=0, http_client=httpx2.Client(transport=httpx2.MockTransport(transport))
        ) as client:
            ComputerToolset(driver).run(client, params)
    else:
        async with AsyncOpenAI(
            api_key="fixture", max_retries=0, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport))
        ) as async_client:
            await AsyncComputerToolset(AsyncDriver(driver)).run(async_client, params)
    assert driver.actions == ["wait", "screenshot"]
    assert [headers.get("idempotency-key") for headers in sent] == ["original-request", None]
    assert [headers.get("x-kept") for headers in sent] == ["request", "request"]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_native_compaction_preserves_opaque_replay(mode: str) -> None:
    compact = {"type": "compaction", "id": "cmp_1", "encrypted_content": "opaque fixture", "extra": "preserve"}
    driver = Driver()
    requests: list[dict[str, Any]] = []
    await run(
        mode,
        driver,
        [response([compact, call()]), FINAL],
        requests,
        params={"context_management": [{"type": "compaction", "compact_threshold": 1000}]},
    )
    assert compact in requests[1]["input"]
    assert driver.actions[-1] == "screenshot"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "compact",
    [
        {"type": "compaction", "encrypted_content": "opaque"},
        {"type": "compaction", "id": "cmp_1"},
        {"type": "compaction", "id": "cmp_1", "encrypted_content": None},
        {"type": "compaction", "id": "cu_fixture", "encrypted_content": ""},
    ],
)
async def test_invalid_compaction_stops_computer_effects(mode: str, compact: dict[str, Any]) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    if compact.get("id") == "cu_fixture":
        compact = {**compact, "id": call()["id"]}
    with pytest.raises(ComputerUseError):
        await run(mode, driver, [response([call(), compact]), FINAL], requests)
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("choice", ["required", {"type": "computer"}])
async def test_run_releases_forced_choice_and_retains_each_reused_screenshot(mode: str, choice: object) -> None:
    class ReusingDriver(Driver):
        def __init__(self) -> None:
            super().__init__()
            self.image: Screenshot = {"type": "computer_screenshot", "file_id": "file_initial"}
            self.captures = 0

        @override
        def screenshot(self) -> Screenshot:
            self.captures += 1
            self.image["file_id"] = f"file_{self.captures}"
            return self.image

    requests: list[dict[str, Any]] = []
    await run(
        mode,
        ReusingDriver(),
        [response([call()]), response([call(id="cu_2", call_id="call_2")]), FINAL],
        requests,
        params={"tool_choice": choice},
    )
    assert [request.get("tool_choice") for request in requests] == [choice, "auto", "auto"]
    screenshots = [item["output"] for item in requests[2]["input"] if item.get("type") == "computer_call_output"]
    assert screenshots == [
        {"type": "computer_screenshot", "file_id": "file_1"},
        {"type": "computer_screenshot", "file_id": "file_2"},
    ]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "choice, continuation",
    [
        ({"type": "computer"}, "auto"),
        (
            {"type": "allowed_tools", "mode": "required", "tools": [{"type": "computer"}]},
            {"type": "allowed_tools", "mode": "auto", "tools": [{"type": "computer"}]},
        ),
    ],
)
async def test_caller_choice_mutation_during_approval_cannot_change_continuation(
    mode: str, choice: dict[str, Any], continuation: object
) -> None:
    requests: list[dict[str, Any]] = []
    choice = deepcopy(choice)

    def confirm(_action: ComputerActionInput) -> bool:
        nested = choice.get("tools")
        if isinstance(nested, list):
            nested.clear()
        choice.clear()
        choice.update({"type": "function", "name": "unadmitted"})
        return True

    await run(
        mode, Driver(), [response([call()]), FINAL], requests, params={"tool_choice": choice}, before_action=confirm
    )
    assert requests[1]["tool_choice"] == continuation
    assert requests[1]["tools"] == [{"type": "computer"}]


def call(*, legacy: bool = False, checks: bool = False, **extra: Any) -> dict[str, Any]:
    return {
        "id": "cu_1",
        "call_id": "call_1",
        "type": "computer_call",
        "status": "completed",
        "pending_safety_checks": [{"id": "safe_1", "code": "sensitive_domain", "message": "Confirm"}] if checks else [],
        **(
            {"action": {"type": "click", "button": "left", "x": 0, "y": 2}}
            if legacy
            else {"actions": [{"type": "click", "button": "left", "x": 0, "y": 2}, {"type": "type", "text": "penguin"}]}
        ),
        **extra,
    }


def response(output: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    return {
        "id": "resp_1",
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "model": "",
        "output": output,
        **extra,
    }


FINAL = response(
    [
        {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "phase": "final_answer",
            "content": [{"type": "output_text", "text": "Done", "annotations": []}],
        }
    ]
)


async def run(
    mode: str,
    driver: Driver,
    replies: list[dict[str, Any]],
    requests: list[dict[str, Any]],
    *,
    params: dict[str, Any] | None = None,
    mixed: bool = False,
    **options: Any,
) -> Any:
    def transport(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/v1/responses"
        assert request.headers["X-Test-Setting"] == "preserved"
        requests.append(json.loads(request.content))
        return httpx2.Response(200, json=replies[len(requests) - 1])

    body = cast(
        ResponseCreateParamsNonStreaming,
        {"model": "", "input": "Find penguin", "store": False, **(params or {})},
    )
    if mode == "sync":
        with OpenAI(
            api_key="test",
            base_url="http://test/v1",
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:
            toolset = ComputerToolset(driver)
            runner = ResponsesToolRunner(computer=toolset) if mixed else toolset
            return runner.run(client.with_options(default_headers={"X-Test-Setting": "preserved"}), body, **options)

    def async_callback(callback: Callable[..., bool]) -> Callable[..., Any]:
        async def wrapped(*args: Any) -> bool:
            return callback(*args)

        return wrapped

    for key in ("approve_safety_checks", "before_action"):
        if key in options:
            options[key] = async_callback(options[key])
    async with AsyncOpenAI(
        api_key="test",
        base_url="http://test/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
    ) as async_client:
        async_toolset = AsyncComputerToolset(AsyncDriver(driver))
        async_runner = AsyncResponsesToolRunner(computer=async_toolset) if mixed else async_toolset
        return await async_runner.run(
            async_client.with_options(default_headers={"X-Test-Setting": "preserved"}), body, **options
        )


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "field",
    ["stream", "background", "conversation", "previous_response_id", "tools", "input", "include", "tool_choice"],
)
async def test_native_computer_extra_body_cannot_replace_owned_fields(mode: str, field: str) -> None:
    requests: list[dict[str, Any]] = []
    driver = Driver()
    with pytest.raises(ValueError, match="extra_body"):
        await run(mode, driver, [FINAL], requests, params={"extra_body": {field: None}})
    assert not requests and not driver.actions


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_native_computer_extra_body_preserves_unowned_fields(mode: str) -> None:
    requests: list[dict[str, Any]] = []
    driver = Driver()
    params = {"extra_body": {"metadata": {"fixture": "kept"}}}
    await run(mode, driver, [response([call()]), FINAL], requests, params=params)
    assert len(requests) == 2
    assert all(request["metadata"] == {"fixture": "kept"} for request in requests)
    assert any(item["type"] == "computer_call_output" for item in requests[1]["input"] if "type" in item)
    assert params == {"extra_body": {"metadata": {"fixture": "kept"}}}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("legacy", [False, True])
async def test_driver_edits_do_not_rewrite_diagnostic_members(mode: str, legacy: bool) -> None:
    from openai.lib.tool_diagnostics import ToolDiagnostic

    class NormalizingDriver(Driver):
        @override
        def record(self, action: ComputerActionInput) -> None:
            super().record(action)
            assert action.type == "keypress"
            action.keys[:] = ["shift", "a"]
            vars(action).update(adapter={"normalized": True}, type="wait")

        keypress = record

    requests: list[dict[str, Any]] = []
    diagnostics: list[ToolDiagnostic] = []
    action = {"type": "keypress", "keys": ["SHIFT", "A"]}
    pending = call(legacy=True, action=action) if legacy else call(actions=[action])
    await run(mode, NormalizingDriver(), [response([pending]), FINAL], requests, on_diagnostic=diagnostics.append)
    assert len(requests) == 2
    replay = next(item for item in requests[1]["input"] if item.get("type") == "computer_call")
    assert (replay["action"] if legacy else replay["actions"][0]) == action
    assert [event["member"] for event in diagnostics if event["stage"] == "action"] == ["keypress", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("legacy", [False, True])
async def test_loop_preserves_stateless_history_and_request_options(mode: str, legacy: bool) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    first = response(
        [
            {
                "id": "rs_1",
                "type": "reasoning",
                "summary": [],
                "encrypted_content": "encrypted",
                "created_by": "output-only",
            },
            call(legacy=legacy, checks=True),
        ]
    )
    result = await run(mode, driver, [first, FINAL], requests, approve_safety_checks=approve_checks)
    assert result.output_text == "Done"
    assert driver.actions == (["click", "screenshot"] if legacy else ["click", "type", "screenshot"])
    assert requests[1]["store"] is False
    assert "reasoning.encrypted_content" in requests[1]["include"]
    assert requests[1]["input"][0] == {"role": "user", "content": "Find penguin"}
    assert requests[1]["input"][1] == {
        "id": "rs_1",
        "type": "reasoning",
        "summary": [],
        "encrypted_content": "encrypted",
    }
    assert requests[1]["input"][-1] == {
        "type": "computer_call_output",
        "call_id": "call_1",
        "output": SCREENSHOT,
        "acknowledged_safety_checks": [{"id": "safe_1", "code": "sensitive_domain", "message": "Confirm"}],
    }


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "sibling",
    [
        {**FINAL["output"][0], "id": None},
        {"type": "message", "role": "assistant", "status": "completed", "content": []},
        {**FINAL["output"][0], "role": "user"},
        {**FINAL["output"][0], "content": None},
        {**FINAL["output"][0], "content": [{"type": "output_text", "text": None}]},
        {**FINAL["output"][0], "content": [{"type": "output_text"}]},
        {**FINAL["output"][0], "content": [{"type": "refusal"}]},
        {**FINAL["output"][0], "content": [{"type": "other", "text": "fixture"}]},
        {**FINAL["output"][0], "status": "unknown"},
        {"type": "reasoning", "summary": []},
        {"type": "reasoning", "id": None, "summary": []},
        {"type": "reasoning", "id": "rs", "summary": None},
        {"type": "reasoning", "id": "rs", "summary": [{"type": "summary_text", "text": None}]},
    ],
)
async def test_invalid_replay_sibling_stops_computer_batch_before_effects(
    mode: str, sibling: dict[str, object]
) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError):
        await run(mode, driver, [response([call(), sibling]), FINAL], requests)
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("kind", ["computer_call", "message", "reasoning"])
async def test_duplicate_platform_identity_stops_computer_effects(mode: str, kind: str) -> None:
    first = call()
    sibling: dict[str, Any]
    if kind == "computer_call":
        sibling = {**call(), "id": first["id"], "call_id": "other_call"}
    elif kind == "message":
        sibling = {**FINAL["output"][0], "id": first["id"]}
    else:
        sibling = {"type": "reasoning", "id": first["id"], "summary": [], "encrypted_content": ""}
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError, match="identity"):
        await run(mode, driver, [response([first, sibling]), FINAL], requests)
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True])
@pytest.mark.parametrize(
    "changes",
    [
        {"content": [None]},
        {"content": "invalid"},
        {"content": [{"type": "reasoning_text"}]},
        {"content": [{"type": "summary_text", "text": ""}]},
        {"encrypted_content": {}},
        {"status": "other"},
        {"status": None},
        {"content": None},
    ],
)
async def test_invalid_reasoning_before_computer_effects(mode: str, mixed: bool, changes: dict[str, object]) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    sibling: dict[str, object] = {"type": "reasoning", "id": "rs", "summary": [], **changes}
    with pytest.raises((ComputerUseError, ToolRunnerError)):
        await run(mode, driver, [response([call(), sibling]), FINAL], requests, mixed=mixed)
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True])
@pytest.mark.parametrize("status", ["completed", "incomplete", "in_progress", None])
async def test_native_reasoning_fields_replay_without_inventing_omitted_content(
    mode: str, mixed: bool, status: str | None
) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    reasoning: dict[str, object] = {
        "type": "reasoning",
        "id": "rs",
        "summary": [{"type": "summary_text", "text": ""}],
        "encrypted_content": None if status is None else "opaque:%00/source",
    }
    if status is not None:
        reasoning.update(status=status, content=[{"type": "reasoning_text", "text": ""}])
    await run(mode, driver, [response([call(), reasoning]), FINAL], requests, mixed=mixed)
    assert driver.actions == ["click", "type", "screenshot"]
    replay = next(item for item in requests[1]["input"] if item.get("id") == "rs")
    assert replay == reasoning


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_null_safety_check_rejected_before_approval(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    approvals: list[str] = []

    def approve(pending: ResponseComputerToolCall) -> bool:
        approvals.append(pending.call_id)
        return True

    with pytest.raises(ComputerUseError):
        await run(
            mode,
            driver,
            [response([call(pending_safety_checks=[None])]), FINAL],
            requests,
            approve_safety_checks=approve,
        )
    assert approvals == []
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("status", ["completed", "incomplete", "in_progress"])
async def test_native_intermediate_commentary_with_computer_calls(mode: str, status: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    intermediate = {**FINAL["output"][0], "id": "msg_commentary", "phase": "commentary", "status": status}
    result = await run(mode, driver, [response([intermediate, call()]), FINAL], requests)
    assert result.output_text == "Done"
    assert driver.actions == ["click", "type", "screenshot"]
    assert any(
        item.get("type") == "message" and item.get("status") == status and item.get("phase") == "commentary"
        for item in requests[1]["input"]
    )


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True])
@pytest.mark.parametrize(
    "changes",
    cast(
        list[dict[str, object]],
        [
            {"content": [{"type": "output_text", "text": "Fixture"}]},
            {"content": [{"type": "output_text", "text": "Fixture", "annotations": None}]},
            {"content": [{"type": "output_text", "text": "Fixture", "annotations": [None]}]},
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [{"type": "file_citation", "file_id": "f"}],
                    }
                ]
            },
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [{"type": "file_path", "file_id": "f", "index": None}],
                    }
                ]
            },
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [
                            {"type": "url_citation", "title": "t", "url": "https://fixture.invalid", "start_index": 0}
                        ],
                    }
                ]
            },
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [
                            {
                                "type": "container_file_citation",
                                "file_id": "f",
                                "filename": "n",
                                "start_index": 0,
                                "end_index": 1,
                            }
                        ],
                    }
                ]
            },
            {"content": [{"type": "output_text", "text": "Fixture", "annotations": [{"type": "unknown"}]}]},
            {"content": [{"type": "output_text", "text": "Fixture", "annotations": [], "logprobs": [None]}]},
            {"content": [{"type": "output_text", "text": "Fixture", "annotations": [], "logprobs": "bad"}]},
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [],
                        "logprobs": [{"token": "t", "bytes": None, "logprob": -1, "top_logprobs": []}],
                    }
                ]
            },
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [],
                        "logprobs": [{"token": "t", "bytes": [0], "logprob": None, "top_logprobs": []}],
                    }
                ]
            },
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [],
                        "logprobs": [{"token": "t", "bytes": [0], "logprob": -1, "top_logprobs": [None]}],
                    }
                ]
            },
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "Fixture",
                        "annotations": [],
                        "logprobs": [
                            {
                                "token": "t",
                                "bytes": [0],
                                "logprob": -1,
                                "top_logprobs": [{"token": "x", "bytes": [1], "logprob": None}],
                            }
                        ],
                    }
                ]
            },
            {"phase": "unrecognized"},
        ],
    ),
)
async def test_native_message_metadata_preflights_before_computer_effects(
    mode: str, mixed: bool, changes: dict[str, object]
) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    sibling = {**FINAL["output"][0], **changes}
    with pytest.raises((ComputerUseError, ToolRunnerError)):
        await run(mode, driver, [response([call(), sibling]), FINAL], requests, mixed=mixed)
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True])
@pytest.mark.parametrize("logprobs", ["omit", "null", "native"])
async def test_native_message_citations_logprobs_and_extras_replay(mode: str, mixed: bool, logprobs: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    annotations = [
        {"type": "file_citation", "file_id": "f", "filename": "n", "index": 0, "extra": "keep"},
        {"type": "file_path", "file_id": "f", "index": 1},
        {"type": "url_citation", "title": "t", "url": "https://fixture.invalid/", "start_index": 0, "end_index": 1},
        {
            "type": "container_file_citation",
            "container_id": "c",
            "file_id": "f",
            "filename": "n",
            "start_index": 0,
            "end_index": 1,
        },
    ]
    part: dict[str, object] = {"type": "output_text", "text": "Fixture", "annotations": annotations, "extra": "keep"}
    if logprobs != "omit":
        part["logprobs"] = (
            None
            if logprobs == "null"
            else [
                {
                    "token": "F",
                    "bytes": [70],
                    "logprob": -1,
                    "top_logprobs": [{"token": "x", "bytes": [120], "logprob": -2, "extra": "keep"}],
                }
            ]
        )
    sibling = {**FINAL["output"][0], "id": "msg_citations", "phase": None, "content": [part], "extra": "keep"}
    result = await run(mode, driver, [response([call(), sibling]), FINAL], requests, mixed=mixed)
    assert result.output_text == "Done"
    assert driver.actions == ["click", "type", "screenshot"]
    replay = next(item for item in requests[1]["input"] if item.get("id") == sibling["id"])
    assert replay["extra"] == "keep" and replay["phase"] is None
    assert replay["content"][0]["extra"] == "keep"
    assert replay["content"][0]["annotations"] == annotations
    if logprobs != "omit":
        assert replay["content"][0]["logprobs"] == part["logprobs"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("field", ["index", "bytes", "logprob", "top_logprob"])
@pytest.mark.parametrize("bad", [True, "1"])
async def test_already_parsed_native_metadata_is_not_coerced_during_preflight(
    mode: str, field: str, bad: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    from openai.types.responses import Response, ResponseOutputText, ResponseOutputMessage
    from openai.types.responses.response_output_text import AnnotationFilePath

    part = {
        "type": "output_text",
        "text": "Fixture",
        "annotations": [{"type": "file_path", "file_id": "f", "index": 1}],
        "logprobs": [
            {
                "token": "F",
                "bytes": [70],
                "logprob": -1,
                "top_logprobs": [{"token": "x", "bytes": [120], "logprob": -2}],
            }
        ],
    }
    parsed = Response(
        **response(
            [call(), {**FINAL["output"][0], "content": [part]}],
            parallel_tool_calls=False,
            tool_choice="auto",
            tools=[],
        )
    )
    message = cast(ResponseOutputMessage, parsed.output[1])
    text = cast(ResponseOutputText, message.content[0])
    annotation = cast(AnnotationFilePath, text.annotations[0])
    assert text.logprobs is not None
    logprob = text.logprobs[0]
    if field == "index":
        object.__setattr__(annotation, "index", bad)
    elif field == "bytes":
        object.__setattr__(logprob, "bytes", [bad])
    elif field == "logprob":
        object.__setattr__(logprob, "logprob", bad)
    else:
        object.__setattr__(logprob.top_logprobs[0], "logprob", bad)

    driver = Driver()

    class ResponsesClient:
        def create(self, **_kwargs: object) -> Response:
            return parsed

    class AsyncResponsesClient:
        async def create(self, **_kwargs: object) -> Response:
            return parsed

    if mode == "sync":
        with OpenAI(api_key="fixture", http_client=httpx2.Client(trust_env=False)) as client:
            monkeypatch.setattr(client, "responses", ResponsesClient())
            with pytest.raises(ComputerUseError):
                ComputerToolset(driver).run(client, {"model": "", "input": "fixture"}, max_steps=2)
    else:
        async with AsyncOpenAI(api_key="fixture", http_client=httpx2.AsyncClient(trust_env=False)) as client_async:
            monkeypatch.setattr(client_async, "responses", AsyncResponsesClient())
            with pytest.raises(ComputerUseError):
                await AsyncComputerToolset(AsyncDriver(driver)).run(
                    client_async, {"model": "", "input": "fixture"}, max_steps=2
                )
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "options", [{}, {"approve_safety_checks": deny_checks}, {"approve_safety_checks": invalid_approval}]
)
async def test_safety_denial_executes_nothing(mode: str, options: dict[str, Any]) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError, match="safety checks") as error:
        await run(mode, driver, [response([call(checks=True)])], requests, **options)
    assert error.value.response is not None
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_action_denial_and_cancellation_stop_batch(mode: str) -> None:
    for cancellation in (False, True):
        driver = Driver()
        requests: list[dict[str, Any]] = []

        def was_cancelled(current_driver: Driver = driver) -> bool:
            return bool(current_driver.actions)

        options: dict[str, Any] = (
            {"cancelled": was_cancelled} if cancellation else {"before_action": stop_before_typing}
        )
        with pytest.raises(ComputerUseError):
            await run(mode, driver, [response([call()])], requests, **options)
        assert driver.actions == ["click"]
        assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_driver_error_does_not_retry_or_execute_remaining_actions(mode: str) -> None:
    driver = Driver(fail=True)
    requests: list[dict[str, Any]] = []
    with pytest.raises(RuntimeError, match="driver failed"):
        await run(mode, driver, [response([call()])], requests)
    assert driver.actions == ["click"]
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_max_steps_reserves_a_response_to_observe_actions(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError, match="max_steps"):
        await run(
            mode, driver, [response([call()]), response([call(id="cu_2", call_id="call_2")])], requests, max_steps=2
        )
    assert len(requests) == 2
    assert driver.actions == ["click", "type", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "bad_response",
    [
        response([call()], status="incomplete"),
        response([call(status="in_progress")]),
        response(
            [call(), {"id": "fn_1", "call_id": "fn_1", "type": "function_call", "name": "other", "arguments": "{}"}]
        ),
        response([call(actions=[{"type": "__getattribute__"}])]),
        response([call(action={"type": "screenshot"})]),
        response([]),
    ],
)
async def test_invalid_response_has_no_side_effects(mode: str, bad_response: dict[str, Any]) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError):
        await run(mode, driver, [bad_response], requests)
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "params",
    cast(
        list[dict[str, Any]],
        [
            {"stream": True},
            {"background": True},
            {"conversation": "conv_1"},
            {"previous_response_id": "resp_1"},
            {"tools": None},
            {"tools": [{"type": "function", "name": "exec", "parameters": {}}]},
        ],
    ),
)
async def test_unsupported_request_fails_before_api(mode: str, params: dict[str, Any]) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ValueError):
        await run(mode, driver, [], requests, params=params)
    assert not requests and not driver.actions


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True])
async def test_explicit_null_input_fails_before_api_or_effects(mode: str, mixed: bool) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises((TypeError, ValueError)):
        await run(mode, driver, [response([call()]), FINAL], requests, params={"input": None}, mixed=mixed)
    assert requests == [] and driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_approval_callback_cannot_change_dispatched_action(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []

    def approve(action: ComputerActionInput) -> bool:
        action.type = "__getattribute__"  # type: ignore[assignment]
        return True

    await run(mode, driver, [response([call()]), FINAL], requests, before_action=approve)
    assert driver.actions == ["click", "type", "screenshot"]


async def test_async_task_cancellation_does_not_capture_or_continue() -> None:
    driver = Driver()

    class CancellingDriver(AsyncDriver):
        @override
        async def click(self, action: ComputerActionInput) -> None:
            self.driver.actions.append(action.type)
            raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await AsyncComputerToolset(CancellingDriver(driver)).execute(ResponseComputerToolCall(**call()))
    assert driver.actions == ["click"]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_policy_can_block_implicit_screenshot(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError, match="not approved"):
        await run(mode, driver, [response([call()])], requests, before_action=deny_screenshot)
    assert driver.actions == ["click", "type"]
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_screenshot_actions_capture_once_after_batch(mode: str) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    actions = [{"type": "screenshot"}, {"type": "click", "button": "left", "x": 0, "y": 0}, {"type": "screenshot"}]
    await run(mode, driver, [response([call(actions=actions)]), FINAL], requests)
    assert driver.actions == ["click", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True], ids=["native", "mixed"])
async def test_modern_live_screenshot_without_pending_checks(mode: str, mixed: bool) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    modern = {
        "id": "cu_fixture",
        "call_id": "call_fixture",
        "type": "computer_call",
        "status": "completed",
        "actions": [{"type": "screenshot"}],
    }
    result = await run(mode, driver, [response([modern]), FINAL], requests, mixed=mixed)
    assert result.output_text == "Done"
    assert driver.actions == ["screenshot"]
    assert requests[1]["input"][-1] == {
        "type": "computer_call_output",
        "call_id": "call_fixture",
        "output": SCREENSHOT,
        "acknowledged_safety_checks": [],
    }


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True], ids=["native", "mixed"])
@pytest.mark.parametrize("legacy", [False, True])
# A list ID stays invalid after either SDK parser; Pydantic 1 coerces integer IDs to strings.
@pytest.mark.parametrize("checks", [None, False, {}, [None], [{"id": []}], [{"id": "check", "code": ["invalid"]}]])
async def test_malformed_pending_checks_stop_before_approval_and_driver(
    mode: str, mixed: bool, legacy: bool, checks: object
) -> None:
    driver = Driver()
    decisions: list[str] = []

    def approve(_call: ResponseComputerToolCall) -> bool:
        decisions.append("checks")
        return True

    def before(_action: ComputerActionInput) -> bool:
        decisions.append("action")
        return True

    with pytest.raises((ComputerUseError, ToolRunnerError)):
        await run(
            mode,
            driver,
            [response([call(legacy=legacy, pending_safety_checks=checks)])],
            [],
            mixed=mixed,
            approve_safety_checks=approve,
            before_action=before,
        )
    assert decisions == []
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True], ids=["native", "mixed"])
async def test_legacy_missing_checks_remains_invalid(mode: str, mixed: bool) -> None:
    driver = Driver()
    legacy = call(legacy=True)
    del legacy["pending_safety_checks"]
    with pytest.raises((ComputerUseError, ToolRunnerError)):
        await run(mode, driver, [response([legacy])], [], mixed=mixed)
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("mixed", [False, True], ids=["native", "mixed"])
async def test_later_malformed_checks_preflight_before_earlier_effects(mode: str, mixed: bool) -> None:
    driver = Driver()
    first = call()
    second = call(id="cu_2", call_id="call_2", pending_safety_checks=None)
    with pytest.raises((ComputerUseError, ToolRunnerError)):
        await run(mode, driver, [response([first, second])], [], mixed=mixed, approve_safety_checks=approve_checks)
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("close_while_waiting", [False, True])
async def test_run_reserves_driver_until_response_and_drains_on_close(mode: str, close_while_waiting: bool) -> None:
    driver = Driver()
    pending = ResponseComputerToolCall(**call())
    params: ResponseCreateParamsNonStreaming = {"model": "", "input": "Find penguin"}
    requests: list[dict[str, Any]] = []

    if mode == "sync":
        tools = ComputerToolset(driver)

        def transport(request: httpx2.Request) -> httpx2.Response:
            requests.append(json.loads(request.content))
            if len(requests) == 1:
                with pytest.raises(RuntimeError, match="busy"):
                    tools.execute(pending)
                with pytest.raises(RuntimeError, match="busy"):
                    tools.run(client, params)
                assert driver.actions == []
                if close_while_waiting:
                    assert tools.close() == {"status": "draining"}
                    with pytest.raises(RuntimeError, match="closed"):
                        tools.execute(pending)
                return httpx2.Response(200, json=response([call()]))
            return httpx2.Response(200, json=FINAL)

        with OpenAI(
            api_key="test",
            base_url="http://test/v1",
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:
            result = tools.run(client, params)
            assert result.output_text == "Done"
            assert driver.actions == ["click", "type", "screenshot"]
            if close_while_waiting:
                with pytest.raises(RuntimeError, match="closed"):
                    tools.run(client, params)
            else:
                assert tools.execute(pending)["output"] == SCREENSHOT
                assert driver.actions == ["click", "type", "screenshot"] * 2
            assert tools.close() == {"status": "closed"}
    else:
        async_tools = AsyncComputerToolset(AsyncDriver(driver))

        async def async_transport(request: httpx2.Request) -> httpx2.Response:
            requests.append(json.loads(request.content))
            if len(requests) == 1:
                with pytest.raises(RuntimeError, match="busy"):
                    await async_tools.execute(pending)
                with pytest.raises(RuntimeError, match="busy"):
                    await async_tools.run(async_client, params)
                assert driver.actions == []
                if close_while_waiting:
                    assert async_tools.close() == {"status": "draining"}
                    with pytest.raises(RuntimeError, match="closed"):
                        await async_tools.execute(pending)
                return httpx2.Response(200, json=response([call()]))
            return httpx2.Response(200, json=FINAL)

        async with AsyncOpenAI(
            api_key="test",
            base_url="http://test/v1",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(async_transport)),
        ) as async_client:
            result = await async_tools.run(async_client, params)
            assert result.output_text == "Done"
            assert driver.actions == ["click", "type", "screenshot"]
            if close_while_waiting:
                with pytest.raises(RuntimeError, match="closed"):
                    await async_tools.run(async_client, params)
            else:
                assert (await async_tools.execute(pending))["output"] == SCREENSHOT
                assert driver.actions == ["click", "type", "screenshot"] * 2
            assert async_tools.close() == {"status": "closed"}
    assert len(requests) == 2
    assert requests[1]["input"][-1]["output"] == SCREENSHOT


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_execute_reserves_driver_and_releases_admission_after_failure(mode: str) -> None:
    driver = Driver()
    pending = ResponseComputerToolCall(**call())
    params: ResponseCreateParamsNonStreaming = {"model": "", "input": "Find penguin"}
    requests: list[httpx2.Request] = []

    def transport(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=FINAL)

    if mode == "sync":
        tools = ComputerToolset(driver)
        with OpenAI(
            api_key="test",
            base_url="http://test/v1",
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:

            def before(_action: ComputerActionInput) -> bool:
                with pytest.raises(RuntimeError, match="busy"):
                    tools.run(client, params)
                with pytest.raises(RuntimeError, match="busy"):
                    tools.execute(pending)
                assert requests == [] and driver.actions == []
                return False

            with pytest.raises(ComputerUseError, match="not approved"):
                tools.execute(pending, before_action=before)
            assert tools.run(client, params).output_text == "Done"
            assert tools.execute(pending)["output"] == SCREENSHOT
    else:
        async_tools = AsyncComputerToolset(AsyncDriver(driver))
        async with AsyncOpenAI(
            api_key="test",
            base_url="http://test/v1",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
        ) as async_client:

            async def async_before(_action: ComputerActionInput) -> bool:
                with pytest.raises(RuntimeError, match="busy"):
                    await async_tools.run(async_client, params)
                with pytest.raises(RuntimeError, match="busy"):
                    await async_tools.execute(pending)
                assert requests == [] and driver.actions == []
                return False

            with pytest.raises(ComputerUseError, match="not approved"):
                await async_tools.execute(pending, before_action=async_before)
            assert (await async_tools.run(async_client, params)).output_text == "Done"
            assert (await async_tools.execute(pending))["output"] == SCREENSHOT
    assert len(requests) == 1
    assert driver.actions == ["click", "type", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "bad",
    [
        {"type": "click", "x": "bad", "y": -1, "button": "left"},
        {"type": "click", "x": None, "y": 1, "button": "back"},
        {"type": "click", "x": 1, "y": 2, "button": "other"},
        {"type": "keypress", "keys": ["Shift", None]},
        {"type": "drag", "path": [{"x": 1, "y": None}]},
        {"type": "scroll", "x": 0, "y": 0, "scroll_x": 0, "scroll_y": "bad"},
        {"type": "type", "text": None},
    ],
)
async def test_all_native_actions_validated_before_any_effect(mode: str, bad: dict[str, object]) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError):
        await run(mode, driver, [response([call(actions=[{"type": "wait"}, bad])])], requests)
    assert driver.actions == []
    assert len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "bad",
    [
        Click.construct(type="click", x=-0.5, y=1, button="back"),
        Keypress.construct(type="keypress", keys=["Shift", 2]),
        DoubleClick.construct(type="double_click", x=1, y=2, keys=["Shift", 2]),
        DoubleClick.construct(type="double_click", x=1, y=2, keys="Shift"),
        Type.construct(type="type", text=2),
    ],
)
async def test_malformed_action_models_stop_before_any_effect(mode: str, bad: ComputerAction) -> None:
    driver = Driver()
    pending = ResponseComputerToolCall(**call())
    # Assign after parsing so native Pydantic coercion cannot normalize the malformed values.
    pending.actions = [Wait(type="wait"), bad]
    with pytest.raises(ComputerUseError, match="Invalid computer action"):
        if mode == "sync":
            ComputerToolset(driver).execute(pending)
        else:
            await AsyncComputerToolset(AsyncDriver(driver)).execute(pending)
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("array_shaped", [False, True])
async def test_computer_action_records_reject_array_shapes(mode: str, legacy: bool, array_shaped: bool) -> None:
    class ListAction(list[object]):
        def __init__(self) -> None:
            super().__init__()
            self.type = "click"
            self.x = 0
            self.y = 2
            self.button = "left"
            self.keys = None

    driver = Driver()
    pending = ResponseComputerToolCall(**call(legacy=legacy))
    action: Any = ListAction() if array_shaped else Click(type="click", x=0, y=2, button="left")
    if legacy:
        pending.action = action
    else:
        pending.actions = [action]

    async def execute() -> None:
        if mode == "sync":
            ComputerToolset(driver).execute(pending)
        else:
            await AsyncComputerToolset(AsyncDriver(driver)).execute(pending)

    if array_shaped:
        with pytest.raises(ComputerUseError, match="Invalid computer action"):
            await execute()
        assert driver.actions == []
    else:
        if legacy and not PYDANTIC_V1:
            # A current Click in the legacy union still replays, with Pydantic's native warning.
            with pytest.warns(UserWarning, match="Pydantic serializer warnings"):
                await execute()
        else:
            await execute()
        assert driver.actions == ["click", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_valid_signed_coordinates_and_both_native_image_sources(mode: str) -> None:
    class NativeDriver(Driver):
        @override
        def screenshot(self) -> Screenshot:
            self.actions.append("screenshot")
            return {**SCREENSHOT, "file_id": "file_fixture"}

    driver = NativeDriver()
    requests: list[dict[str, Any]] = []
    await run(
        mode,
        driver,
        [response([call(actions=[{"type": "click", "x": -5, "y": 125, "button": "back"}])]), FINAL],
        requests,
    )
    assert driver.actions == ["click", "screenshot"]
    output = next(item for item in requests[1]["input"] if item.get("type") == "computer_call_output")
    assert output["output"] == {**SCREENSHOT, "file_id": "file_fixture"}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("iterable", [False, True], ids=["list", "generator"])
async def test_admitted_nested_request_is_owned_during_computer_continuation(mode: str, iterable: bool) -> None:
    requests: list[dict[str, Any]] = []
    original = [{"role": "user", "content": [{"type": "input_text", "text": "admitted task"}]}]
    metadata = {"ticket": "admitted"}
    inputs = (item for item in original) if iterable else original

    def change(_action: ComputerActionInput) -> bool:
        original[0]["content"] = [{"type": "input_text", "text": "later task"}]
        metadata["ticket"] = "later"
        return True

    await run(
        mode,
        Driver(),
        [response([call()]), FINAL],
        requests,
        params={"input": inputs, "metadata": metadata},
        before_action=change,
    )
    assert len(requests) == 2
    assert requests[1]["input"][0] == {"role": "user", "content": [{"type": "input_text", "text": "admitted task"}]}
    assert requests[1]["metadata"] == {"ticket": "admitted"}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("field", ["allowed_tools", "input_content"])
async def test_nested_native_iterables_are_owned_before_computer_execution(mode: str, field: str) -> None:
    requests: list[dict[str, Any]] = []
    params: dict[str, Any]
    if field == "allowed_tools":
        values = [{"type": "computer"}]
        params = {"tool_choice": {"type": "allowed_tools", "mode": "auto", "tools": (item for item in values)}}
    else:
        values = [{"type": "input_text", "text": "original task"}]
        params = {"input": [{"role": "user", "content": (item for item in values)}]}

    def mutate(_action: ComputerActionInput) -> bool:
        values[0].clear()
        return True

    await run(mode, Driver(), [response([call()]), FINAL], requests, params=params, before_action=mutate)
    for request in requests:
        if field == "allowed_tools":
            assert request["tool_choice"] == {
                "type": "allowed_tools",
                "mode": "auto",
                "tools": [{"type": "computer"}],
            }
        else:
            assert request["input"][0] == {
                "role": "user",
                "content": [{"type": "input_text", "text": "original task"}],
            }


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("callback", ["diagnostic", "cancelled"])
async def test_screenshot_is_owned_before_post_capture_callbacks(mode: str, callback: str) -> None:
    from openai.lib.tool_diagnostics import ToolDiagnostic

    image: Screenshot = {"type": "computer_screenshot", "file_id": "file_captured"}
    captured = False

    class ReusingDriver(Driver):
        @override
        def screenshot(self) -> Screenshot:
            nonlocal captured
            captured = True
            return image

    def diagnostic(event: ToolDiagnostic) -> None:
        if callback == "diagnostic" and event.get("member") == "screenshot" and event["reason"] == "completed":
            image["file_id"] = "file_recycled"

    def cancelled() -> bool:
        if callback == "cancelled" and captured:
            image["file_id"] = "file_recycled"
        return False

    driver = ReusingDriver()
    pending = ResponseComputerToolCall(**call())
    if mode == "sync":
        result = ComputerToolset(driver).execute(pending, on_diagnostic=diagnostic, cancelled=cancelled)
    else:
        result = await AsyncComputerToolset(AsyncDriver(driver)).execute(
            pending, on_diagnostic=diagnostic, cancelled=cancelled
        )
    assert image["file_id"] == "file_recycled"
    assert result["output"] == {"type": "computer_screenshot", "file_id": "file_captured"}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("stage", ["click", "screenshot"])
@pytest.mark.parametrize("cancel", [False, True])
@pytest.mark.parametrize("throws", [False, True])
async def test_computer_driver_failure_prefers_observed_cancellation(
    mode: str,
    stage: str,
    cancel: bool,
    throws: bool,
) -> None:
    from openai.lib.tool_diagnostics import ToolDiagnostic

    stopped = False
    events: list[ToolDiagnostic] = []

    class FailingDriver(Driver):
        @override
        def record(self, action: ComputerActionInput) -> None:
            nonlocal stopped
            self.actions.append(action.type)
            if stage == action.type:
                stopped = cancel
                if throws:
                    raise RuntimeError("driver interrupted")

        click = record

        @override
        def screenshot(self) -> Screenshot:
            nonlocal stopped
            self.actions.append("screenshot")
            stopped = cancel
            if throws:
                raise RuntimeError("driver interrupted")
            return SCREENSHOT.copy()

    driver = FailingDriver()
    pending = ResponseComputerToolCall(**call(actions=[{"type": "click", "x": 1, "y": 2, "button": "left"}]))
    expected = ComputerUseError if cancel else RuntimeError
    if not cancel and not throws:
        if mode == "sync":
            ComputerToolset(driver).execute(pending, cancelled=lambda: stopped, on_diagnostic=events.append)
        else:
            await AsyncComputerToolset(AsyncDriver(driver)).execute(
                pending, cancelled=lambda: stopped, on_diagnostic=events.append
            )
        assert driver.actions == ["click", "screenshot"]
        assert all(event["reason"] == "completed" for event in events)
        return
    with pytest.raises(expected, match="cancelled" if cancel else "driver interrupted"):
        if mode == "sync":
            ComputerToolset(driver).execute(pending, cancelled=lambda: stopped, on_diagnostic=events.append)
        else:
            await AsyncComputerToolset(AsyncDriver(driver)).execute(
                pending, cancelled=lambda: stopped, on_diagnostic=events.append
            )
    assert driver.actions == (["click"] if stage == "click" else ["click", "screenshot"])
    assert (events[-1]["stage"], events[-1]["reason"], events[-1]["member"]) == (
        "action",
        "cancelled" if cancel else "driver_failed",
        stage,
    )


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("keys", [{}, {"keys": None}, {"keys": []}, {"keys": ["Shift"]}])
async def test_python_native_double_click_optional_keys(mode: str, keys: dict[str, object]) -> None:
    driver = Driver()
    await run(mode, driver, [response([call(actions=[{"type": "double_click", "x": 1, "y": 2, **keys}])]), FINAL], [])
    assert driver.actions == ["double_click", "screenshot"]


def changing_check_call() -> tuple[ResponseComputerToolCall, list[str]]:
    from openai.types.responses.response_computer_tool_call import PendingSafetyCheck

    reads: list[str] = []

    class ChangingChecks(ResponseComputerToolCall):
        @override
        def __getattribute__(self, name: str) -> Any:
            if name == "pending_safety_checks":
                reads.append(name)
                return [PendingSafetyCheck(id="approval_needed")] if len(reads) == 1 else []
            return super().__getattribute__(name)

    original = ChangingChecks(**call(actions=[{"type": "wait"}], pending_safety_checks=[]))
    reads.clear()
    return original, reads


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("entry", ["direct", "run"])
@pytest.mark.parametrize("approve", [False, True])
async def test_computer_owns_one_checklist_before_policy_and_replay(
    mode: str, entry: str, approve: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    from openai.types.responses import Response

    original, reads = changing_check_call()
    driver = Driver()
    first = Response.construct(**response([call()]))
    first.output = [original]
    last = Response.construct(**FINAL)
    requests: list[dict[str, Any]] = []
    approvals: list[list[str]] = []

    def policy(value: ResponseComputerToolCall) -> bool:
        approvals.append([check.id for check in value.pending_safety_checks or []])
        return approve

    async def async_policy(value: ResponseComputerToolCall) -> bool:
        return policy(value)

    def reply(**kwargs: Any) -> Response:
        requests.append(deepcopy(kwargs))
        return first if len(requests) == 1 else last

    async def async_reply(**kwargs: Any) -> Response:
        return reply(**kwargs)

    if mode == "sync":
        tools = ComputerToolset(driver)
        with OpenAI(api_key="fake", http_client=httpx2.Client(trust_env=False)) as client:
            monkeypatch.setattr(client.responses, "create", reply)
            if not approve:
                with pytest.raises(ComputerUseError, match="require explicit approval"):
                    if entry == "direct":
                        tools.execute(original, approve_safety_checks=policy)
                    else:
                        tools.run(client, {"model": "", "input": "fixture"}, approve_safety_checks=policy)
            elif entry == "direct":
                out = tools.execute(original, approve_safety_checks=policy)
                assert out.get("acknowledged_safety_checks") == [
                    {"id": "approval_needed", "code": None, "message": None}
                ]
            else:
                assert (
                    tools.run(client, {"model": "", "input": "fixture"}, approve_safety_checks=policy).output_text
                    == "Done"
                )
    else:
        async_tools = AsyncComputerToolset(AsyncDriver(driver))
        async with AsyncOpenAI(api_key="fake", http_client=httpx2.AsyncClient(trust_env=False)) as async_client:
            monkeypatch.setattr(async_client.responses, "create", async_reply)
            if not approve:
                with pytest.raises(ComputerUseError, match="require explicit approval"):
                    if entry == "direct":
                        await async_tools.execute(original, approve_safety_checks=async_policy)
                    else:
                        await async_tools.run(
                            async_client, {"model": "", "input": "fixture"}, approve_safety_checks=async_policy
                        )
            elif entry == "direct":
                out = await async_tools.execute(original, approve_safety_checks=async_policy)
                assert out.get("acknowledged_safety_checks") == [
                    {"id": "approval_needed", "code": None, "message": None}
                ]
            else:
                assert (
                    await async_tools.run(
                        async_client, {"model": "", "input": "fixture"}, approve_safety_checks=async_policy
                    )
                ).output_text == "Done"
    assert reads == ["pending_safety_checks"]
    assert approvals == [["approval_needed"]]
    assert driver.actions == (["wait", "screenshot"] if approve else [])
    if entry == "run" and approve:
        history = requests[1]["input"]
        replayed = next(item for item in history if item.get("type") == "computer_call")
        output = next(item for item in history if item.get("type") == "computer_call_output")
        assert [check["id"] for check in replayed["pending_safety_checks"]] == ["approval_needed"]
        assert [check["id"] for check in output["acknowledged_safety_checks"]] == ["approval_needed"]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_plain_computer_subclass_retains_unknown_wire_fields_and_replay(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from openai.types.responses import Response

    class ExtendedCall(ResponseComputerToolCall):
        pass

    pending = ExtendedCall(**call(actions=[{"type": "wait"}], future_field={"value": ["preserved"]}))
    driver = Driver()
    requests: list[dict[str, Any]] = []
    first = Response.construct(**response([call()]))
    first.output = [pending]
    last = Response.construct(**FINAL)

    def reply(**kwargs: Any) -> Response:
        requests.append(deepcopy(kwargs))
        return first if len(requests) == 1 else last

    async def async_reply(**kwargs: Any) -> Response:
        return reply(**kwargs)

    if mode == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(trust_env=False)) as client:
            monkeypatch.setattr(client.responses, "create", reply)
            ComputerToolset(driver).run(client, {"model": "", "input": "fixture"})
    else:
        async with AsyncOpenAI(api_key="fake", http_client=httpx2.AsyncClient(trust_env=False)) as client:
            monkeypatch.setattr(client.responses, "create", async_reply)
            await AsyncComputerToolset(AsyncDriver(driver)).run(client, {"model": "", "input": "fixture"})
    assert driver.actions == ["wait", "screenshot"]
    replay = next(item for item in requests[1]["input"] if item.get("type") == "computer_call")
    assert replay["future_field"] == {"value": ["preserved"]}


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_nested_check_fields_approved_are_the_fields_acknowledged(mode: str) -> None:
    from openai.types.responses.response_computer_tool_call import PendingSafetyCheck

    reads: dict[str, int] = {"id": 0, "code": 0, "message": 0}
    admitted = {"id": "original_check", "code": "original_code", "message": "original_message"}

    class ChangingCheck(PendingSafetyCheck):
        @override
        def __getattribute__(self, name: str) -> Any:
            if name in reads:
                reads[name] += 1
                return admitted[name] if reads[name] == 1 else "later_" + name
            return super().__getattribute__(name)

    pending = ResponseComputerToolCall(**call(actions=[{"type": "wait"}]))
    pending.pending_safety_checks = [ChangingCheck(id="stored")]
    reads.update({name: 0 for name in reads})
    driver = Driver()
    approved: list[dict[str, str | None]] = []

    def policy(value: ResponseComputerToolCall) -> bool:
        approved.extend(
            {"id": check.id, "code": check.code, "message": check.message}
            for check in value.pending_safety_checks or []
        )
        return True

    async def async_policy(value: ResponseComputerToolCall) -> bool:
        return policy(value)

    if mode == "sync":
        out = ComputerToolset(driver).execute(pending, approve_safety_checks=policy)
    else:
        out = await AsyncComputerToolset(AsyncDriver(driver)).execute(pending, approve_safety_checks=async_policy)
    assert approved == [admitted]
    assert out.get("acknowledged_safety_checks") == [admitted]
    assert reads == {"id": 1, "code": 1, "message": 1}
    assert driver.actions == ["wait", "screenshot"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "fields",
    [
        {"actions": [{"type": "wait"}], "action": None},
        {"actions": None, "action": {"type": "wait"}},
    ],
)
async def test_explicit_null_alternative_cannot_be_replayed_after_effects(mode: str, fields: dict[str, Any]) -> None:
    driver = Driver()
    requests: list[dict[str, Any]] = []
    with pytest.raises(ComputerUseError, match="exactly one"):
        await run(mode, driver, [response([call(**fields)]), FINAL], requests)
    assert driver.actions == [] and len(requests) == 1


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("member", ["type", "screenshot"])
async def test_incomplete_computer_driver_is_rejected_before_effects(mode: str, member: str) -> None:
    driver = Driver()
    current: Any = driver if mode == "sync" else AsyncDriver(driver)
    setattr(current, member, None)
    with pytest.raises(ValueError, match="driver"):
        if mode == "sync":
            ComputerToolset(current)
        else:
            AsyncComputerToolset(current)
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_computer_driver_flavor_is_rejected_before_effects(mode: str) -> None:
    driver = Driver()
    wrong: Any = AsyncDriver(driver) if mode == "sync" else driver
    with pytest.raises(ValueError, match="Computer member.*method flavor"):
        if mode == "sync":
            ComputerToolset(wrong)
        else:
            AsyncComputerToolset(wrong)
    assert driver.actions == []


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("annotation", [Any, "Any", object, "object"])
async def test_computer_driver_opaque_return_annotation(mode: str, annotation: object) -> None:
    driver = Driver()
    implementation = driver if mode == "sync" else AsyncDriver(driver)

    class Wrapper:
        def __getattr__(self, member: str) -> Any:
            method = getattr(implementation, member)

            def wrapped(*args: Any, **kwargs: Any) -> Any:
                return method(*args, **kwargs)

            wrapped.__annotations__["return"] = annotation
            return wrapped

    wrapped: Any = Wrapper()
    pending = ResponseComputerToolCall(**call(actions=[{"type": "wait"}]))
    if mode == "sync":
        result = ComputerToolset(wrapped).execute(pending)
    else:
        result = await AsyncComputerToolset(wrapped).execute(pending)
    assert result["output"] == SCREENSHOT
    assert driver.actions == ["wait", "screenshot"]
