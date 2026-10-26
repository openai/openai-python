from __future__ import annotations

import json
import time
import asyncio
from typing import Any, Callable, cast
from threading import Lock, Barrier
from contextvars import ContextVar
from typing_extensions import Literal, TypedDict, override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.responses import Response, ResponseComputerToolCall, ResponseFunctionToolCall
from openai.lib.responses_tool_runner import (
    ToolRunnerError,
    RegisteredFunction,
    ResponsesToolLedger,
    ResponsesToolRunner,
    AsyncRegisteredFunction,
    ResponsesToolCheckpoint,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
    ToolRunnerCancelledError,
)

from .test_responses_tool_runner import TOOL, FINAL, PARAMS, fn, sse, resp


class WindowOptions(TypedDict, total=False):
    max_concurrent_calls: int


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("limit", [1, 2])
async def test_independent_calls_inherit_dispatch_context_without_leaking_to_siblings(lane: str, limit: int) -> None:
    tenant = ContextVar("test_runner_tenant", default="unset")
    requests: list[dict[str, Any]] = []
    first = resp([fn("record", f"c{index}", text=str(index)) for index in range(4)], "first")
    rendezvous = Barrier(limit, timeout=2)
    entered = 0
    ready = asyncio.Event()

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, content=sse(first if len(requests) == 1 else FINAL)
        )

    def record(args: dict[str, object]) -> str:
        observed = tenant.get()
        tenant.set("worker-" + str(args["text"]))
        rendezvous.wait()
        return observed

    async def arecord(args: dict[str, object]) -> str:
        nonlocal entered
        observed = tenant.get()
        tenant.set("worker-" + str(args["text"]))
        entered += 1
        if entered % limit == 0:
            ready.set()
        await asyncio.wait_for(ready.wait(), timeout=2)
        return observed

    token = tenant.set("request-tenant")
    try:
        if lane == "sync":
            runner = ResponsesToolRunner(functions=[RegisteredFunction(TOOL, record, independent=True)])
            with OpenAI(
                api_key="fixture",
                http_client=httpx2.Client(trust_env=False, transport=httpx2.MockTransport(handler)),
            ) as client:
                runner.run(client, PARAMS, stream=True, eager=True, max_concurrent_calls=limit)
        else:
            async_runner = AsyncResponsesToolRunner(
                functions=[AsyncRegisteredFunction(TOOL, arecord, independent=True)]
            )
            async with AsyncOpenAI(
                api_key="fixture",
                http_client=httpx2.AsyncClient(trust_env=False, transport=httpx2.MockTransport(handler)),
            ) as client_async:
                await async_runner.run(client_async, PARAMS, stream=True, eager=True, max_concurrent_calls=limit)
        assert tenant.get() == "request-tenant"
    finally:
        tenant.reset(token)
    outputs = [item for item in requests[1]["input"] if item.get("type") == "function_call_output"]
    assert [(item["call_id"], item["output"]) for item in outputs] == [
        (f"c{index}", "request-tenant") for index in range(4)
    ]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("limit", [None, 1, 3])
async def test_independent_window_bounds_running_calls_and_replays_all_in_order(lane: str, limit: int | None) -> None:
    requests: list[dict[str, Any]] = []
    lock = Lock()
    active = 0
    peak = 0
    options: WindowOptions = {} if limit is None else {"max_concurrent_calls": limit}
    first = resp([fn("record", f"c{index}", text=str(index)) for index in range(8)], "first")

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, content=sse(first if len(requests) == 1 else FINAL)
        )

    def enter() -> None:
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)

    def leave() -> None:
        nonlocal active
        with lock:
            active -= 1

    def record(args: dict[str, object]) -> str:
        enter()
        time.sleep(0.025)
        leave()
        return cast(str, args["text"])

    async def arecord(args: dict[str, object]) -> str:
        enter()
        await asyncio.sleep(0.025)
        leave()
        return cast(str, args["text"])

    if lane == "sync":
        runner = ResponsesToolRunner(functions=[RegisteredFunction(TOOL, record, independent=True)])
        with OpenAI(api_key="fixture", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            runner.run(client, PARAMS, stream=True, eager=True, **options)
    else:
        async_runner = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, arecord, independent=True)])
        async with AsyncOpenAI(
            api_key="fixture", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            await async_runner.run(client_async, PARAMS, stream=True, eager=True, **options)
    assert 0 < peak <= (2 if limit is None else limit)
    assert active == 0
    outputs = [item for item in requests[1]["input"] if item.get("type") == "function_call_output"]
    assert [(item["call_id"], item["output"]) for item in outputs] == [(f"c{i}", str(i)) for i in range(8)]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_runner_lifecycle_refuses_before_option_truth_checks_and_releases_invalid_preparation(lane: str) -> None:
    reads: list[str] = []
    requests: list[httpx2.Request] = []

    class NewRunOption:
        def __bool__(self) -> bool:
            reads.append("stream")
            raise AssertionError("A refused run must not inspect this option")

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=FINAL)

    if lane == "sync":
        runner = ResponsesToolRunner()
        with OpenAI(api_key="fixture", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            with pytest.raises(ValueError, match="max_concurrent_calls"):
                runner.run(client, PARAMS, max_concurrent_calls=0)
            iterator = runner.iterate(client, PARAMS)
            assert next(iterator).final
            with pytest.raises(RuntimeError):
                runner.run(client, PARAMS, stream=cast(bool, NewRunOption()))
            assert reads == []
            runner.close()
            iterator.close()
            with pytest.raises(RuntimeError):
                runner.run(client, PARAMS, stream=cast(bool, NewRunOption()))
    else:
        async_runner = AsyncResponsesToolRunner()
        async with AsyncOpenAI(
            api_key="fixture", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            with pytest.raises(ValueError, match="max_concurrent_calls"):
                await async_runner.run(client_async, PARAMS, max_concurrent_calls=0)
            async_iterator = async_runner.iterate(client_async, PARAMS)
            assert (await async_iterator.__anext__()).final
            with pytest.raises(RuntimeError):
                await async_runner.run(client_async, PARAMS, stream=cast(bool, NewRunOption()))
            assert reads == []
            async_runner.close()
            await async_iterator.aclose()
            with pytest.raises(RuntimeError):
                await async_runner.run(client_async, PARAMS, stream=cast(bool, NewRunOption()))
    assert reads == [] and len(requests) == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_ledger_saves_the_inspected_native_response_without_subclass_rereads(
    lane: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    reads: list[str] = []
    writes: list[ResponsesToolCheckpoint] = []

    class SwitchingResponse(Response):
        @override
        def __getattribute__(self, name: str) -> Any:
            if name == "status":
                reads.append(name)
                return "completed" if reads.count(name) == 1 else "failed"
            if name == "output":
                reads.append(name)
                return super().__getattribute__(name) if reads.count(name) == 1 else []
            return super().__getattribute__(name)

        @override
        def to_dict(self, **_kwargs: Any) -> dict[str, Any]:
            raise AssertionError("Never serialize the caller's subclass after inspection")

    native = SwitchingResponse.construct(**cast(dict[str, Any], FINAL))
    reads.clear()

    def no_requests(_request: httpx2.Request) -> httpx2.Response:
        raise AssertionError("The native response test must not contact a transport")

    if lane == "sync":
        with OpenAI(
            api_key="fixture", http_client=httpx2.Client(transport=httpx2.MockTransport(no_requests))
        ) as client:

            def reply(*_args: object, **_kwargs: object) -> Response:
                return native

            monkeypatch.setattr(type(client.responses), "create", reply)
            ResponsesToolRunner().run(client, PARAMS, ledger=ResponsesToolLedger("fixed", writes.append))
    else:
        async with AsyncOpenAI(
            api_key="fixture", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(no_requests))
        ) as client_async:

            async def reply_async(*_args: object, **_kwargs: object) -> Response:
                return native

            async def save(value: ResponsesToolCheckpoint) -> None:
                writes.append(value)

            monkeypatch.setattr(type(client_async.responses), "create", reply_async)
            await AsyncResponsesToolRunner().run(client_async, PARAMS, ledger=AsyncResponsesToolLedger("fixed", save))
    assert writes[-1]["phase"] == "final"
    final = writes[-1]["final_response"]
    assert final and final["status"] == "completed" and final["output"] == FINAL["output"]
    assert reads.count("status") == reads.count("output") == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("failure", [None, "error", "cancel"])
@pytest.mark.parametrize("durable", [False, True])
async def test_independent_calls_settle_before_dependent_action_in_original_order(
    lane: str, failure: str | None, durable: bool
) -> None:
    requests: list[dict[str, Any]] = []
    returned: list[str] = []
    effects: list[str] = []
    saved: list[ResponsesToolCheckpoint] = []
    rendezvous = Barrier(2, timeout=2)
    seen = {"first": asyncio.Event(), "second": asyncio.Event()}

    def record(args: dict[str, object], *, cancelled: Callable[[], bool] | None = None) -> str:
        assert cancelled is cancelled_probe
        value = cast(str, args["text"])
        if not durable:
            rendezvous.wait()
        if failure and value == "first":
            if failure == "cancel":
                raise asyncio.CancelledError("sentinel-private-cancellation")
            raise RuntimeError("sentinel-private-failure")
        returned.append(value)
        return value

    async def arecord(args: dict[str, object], *, cancelled: Callable[[], bool] | None = None) -> str:
        assert cancelled is cancelled_probe
        value = cast(str, args["text"])
        seen[value].set()
        if not durable:
            await asyncio.wait_for(seen["second" if value == "first" else "first"].wait(), timeout=2)
        if failure and value == "first":
            if failure == "cancel":
                raise asyncio.CancelledError("sentinel-private-cancellation")
            raise RuntimeError("sentinel-private-failure")
        returned.append(value)
        return value

    def cancelled_probe() -> bool:
        return False

    def barrier(_args: dict[str, object]) -> str:
        assert sorted(returned) == ["first", "second"]
        effects.append("dependent")
        return "done"

    async def abarrier(args: dict[str, object]) -> str:
        return barrier(args)

    async def save(checkpoint: ResponsesToolCheckpoint) -> None:
        saved.append(checkpoint)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        first = resp(
            [
                fn("record", "c1", text="first"),
                fn("record", "c2", text="second"),
                fn("barrier", "c3", text="dependent"),
            ],
            "first",
        )
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, content=sse(first if len(requests) == 1 else FINAL)
        )

    async def exercise() -> None:
        if lane == "sync":
            runner = ResponsesToolRunner(
                functions=[
                    RegisteredFunction(TOOL, record, independent=True),
                    RegisteredFunction({**TOOL, "name": "barrier"}, barrier),
                ]
            )
            with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                runner.run(
                    client,
                    PARAMS,
                    stream=True,
                    eager=True,
                    cancelled=cancelled_probe,
                    ledger=ResponsesToolLedger("independent", saved.append) if durable else None,
                )
        else:
            runner_async = AsyncResponsesToolRunner(
                functions=[
                    AsyncRegisteredFunction(TOOL, arecord, independent=True),
                    AsyncRegisteredFunction({**TOOL, "name": "barrier"}, abarrier),
                ]
            )
            async with AsyncOpenAI(
                api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
            ) as client_async:
                await runner_async.run(
                    client_async,
                    PARAMS,
                    stream=True,
                    eager=True,
                    cancelled=cancelled_probe,
                    ledger=AsyncResponsesToolLedger("independent", save) if durable else None,
                )

    if failure:
        expected = ToolRunnerCancelledError if failure == "cancel" else ToolRunnerError
        with pytest.raises(expected) as exc:
            await exercise()
        assert isinstance(exc.value, ToolRunnerCancelledError) == (failure == "cancel")
        assert "sentinel" not in str(exc.value)
        assert exc.value.attempted_call_ids == (("c1",) if durable else ("c1", "c2"))
        assert exc.value.completed_call_ids == (() if durable else ("c2",))
        assert returned == ([] if durable else ["second"]) and effects == [] and len(requests) == 1
        if durable:
            assert saved[-1]["phase"] == "pending"
            assert saved[-1]["attempted_call_ids"] == ["c1"]
            assert saved[-1]["returned_call_ids"] == []
    else:
        await exercise()
        assert effects == ["dependent"]
        assert [item["call_id"] for item in requests[1]["input"] if item.get("type") == "function_call_output"] == [
            "c1",
            "c2",
            "c3",
        ]
        if durable:
            assert saved[-1]["returned_call_ids"] == ["c1", "c2", "c3"]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("decision", ["execute", "defer", "bad"])
async def test_per_call_early_decision_is_snapshot_and_cannot_cross_allowlist(lane: str, decision: str) -> None:
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    inspected: list[str] = []
    at_complete: list[list[str]] = []

    def record(args: dict[str, object]) -> str:
        value = cast(str, args["text"])
        effects.append(value)
        return value

    async def arecord(args: dict[str, object]) -> str:
        return record(args)

    def before(item: ResponseFunctionToolCall | ResponseComputerToolCall) -> Literal["execute", "defer"]:
        inspected.append(item.call_id)
        assert isinstance(item, ResponseFunctionToolCall)
        item.arguments = '{"text":"mutated"}'
        return cast(Literal["execute", "defer"], decision)

    async def abefore(item: ResponseFunctionToolCall | ResponseComputerToolCall) -> Literal["execute", "defer"]:
        return before(item)

    def on_event(event: Any) -> None:
        if event.type == "response.completed" and event.response.id == "first":
            at_complete.append(effects.copy())

    async def aon_event(event: Any) -> None:
        on_event(event)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        first = resp(
            [
                fn("record", "allowed", text="original"),
                fn("barrier", "blocked", text="later"),
                fn("record", "suffix", text="end"),
            ],
            "first",
        )
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, content=sse(first if len(requests) == 1 else FINAL)
        )

    async def exercise() -> None:
        if lane == "sync":
            runner = ResponsesToolRunner(
                functions=[
                    RegisteredFunction(TOOL, record),
                    RegisteredFunction({**TOOL, "name": "barrier"}, record),
                ],
                early_execution={"functions": ["record"]},
            )
            with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                runner.run(client, PARAMS, stream=True, eager=True, before_early_call=before, on_event=on_event)
        else:
            runner_async = AsyncResponsesToolRunner(
                functions=[
                    AsyncRegisteredFunction(TOOL, arecord),
                    AsyncRegisteredFunction({**TOOL, "name": "barrier"}, arecord),
                ],
                early_execution={"functions": ["record"]},
            )
            async with AsyncOpenAI(
                api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
            ) as client_async:
                await runner_async.run(
                    client_async, PARAMS, stream=True, eager=True, before_early_call=abefore, on_event=aon_event
                )

    if decision == "bad":
        with pytest.raises(ToolRunnerError, match="before_early_call"):
            await exercise()
        assert effects == []
    else:
        await exercise()
        assert effects == ["original", "later", "end"]
        assert at_complete == [["original"] if decision == "execute" else []]
    assert inspected == ["allowed"]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_responses_runner_busy_and_close_from_callback_retains_original_run(lane: str) -> None:
    requests: list[str] = []
    calls: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request.url.path)
        first = resp([fn("record", "original", text="ok")], "first")
        return httpx2.Response(200, json=first if len(requests) == 1 else FINAL)

    if lane == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:

            def record(_args: dict[str, object]) -> str:
                with pytest.raises(RuntimeError, match="busy"):
                    runner.run(client, PARAMS)
                assert runner.close() == {"status": "draining"}
                with pytest.raises(RuntimeError, match="closed"):
                    runner.run(client, PARAMS)
                calls.append("original")
                return "ok"

            runner = ResponsesToolRunner(functions=[RegisteredFunction(TOOL, record)])
            result = runner.run(client, PARAMS)
            assert runner.close() == {"status": "closed"}
    else:
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:

            async def arecord(_args: dict[str, object]) -> str:
                with pytest.raises(RuntimeError, match="busy"):
                    await runner_async.run(client_async, PARAMS)
                assert runner_async.close() == {"status": "draining"}
                with pytest.raises(RuntimeError, match="closed"):
                    await runner_async.run(client_async, PARAMS)
                calls.append("original")
                return "ok"

            runner_async = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, arecord)])
            result = await runner_async.run(client_async, PARAMS)
            assert runner_async.close() == {"status": "closed"}
    assert result.id == "resp_final"
    assert calls == ["original"] and len(requests) == 2


async def test_repeated_cancellation_drains_independent_action_and_keeps_receipts() -> None:
    from openai.lib.responses_tool_runner import ToolRunnerCancelledError

    started = asyncio.Event()
    release = asyncio.Event()
    effects: list[str] = []
    requests: list[str] = []

    async def record(_args: dict[str, object]) -> str:
        started.set()
        await release.wait()
        effects.append("completed-after-release")
        return "done"

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request.url.path)
        first = resp([fn("record", "pending", text="ok")], "first")
        return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(first))

    runner = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(TOOL, record, independent=True)])
    async with AsyncOpenAI(
        api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    ) as client:
        failures: list[ToolRunnerCancelledError] = []

        async def caller() -> None:
            try:
                await runner.run(client, PARAMS, stream=True, eager=True)
            except ToolRunnerCancelledError as exc:
                failures.append(exc)
                raise

        task = asyncio.create_task(caller())
        await asyncio.wait_for(started.wait(), timeout=2)
        task.cancel()
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        task.cancel()
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        assert not task.done()
        assert effects == [] and runner.close() == {"status": "draining"}
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert len(failures) == 1
    assert failures[0].attempted_call_ids == failures[0].completed_call_ids == ("pending",)
    assert effects == ["completed-after-release"] and len(requests) == 1
    assert runner.close() == {"status": "closed"}


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("policy", [False, True], ids=["blanket", "selective"])
@pytest.mark.parametrize("case", ["gap", "out-of-order", "interrupted", "final-gap"])
async def test_sparse_and_out_of_order_stream_keeps_ledger_until_reconciled(lane: str, policy: bool, case: str) -> None:
    requests: list[dict[str, Any]] = []
    saved: list[ResponsesToolCheckpoint] = []
    effects: list[str] = []
    first = (
        FINAL
        if case == "final-gap"
        else resp([fn("record", "c1", text="first"), fn("record", "c2", text="second")], "first")
    )

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        if len(requests) > 1:
            data = sse(FINAL)
        else:
            events = [json.loads(part.removeprefix(b"data: ")) for part in sse(first).split(b"\n\n") if part]
            done = [event for event in events if event["type"] == "response.output_item.done"]
            events = [
                event for event in events if event["type"] not in ("response.output_item.done", "response.completed")
            ]
            if case != "out-of-order":
                events.insert(1, {"type": "response.output_item.added", "output_index": 0, "item": None})
                for event in events[2:] + done:
                    if "output_index" in event:
                        event["output_index"] += 1_000_000
            events.extend(reversed(done) if case == "out-of-order" else done)
            if case != "interrupted":
                events.append({"type": "response.completed", "response": first})
            data = "".join(
                f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events)
            ).encode()
        return httpx2.Response(200, content=data, headers={"content-type": "text/event-stream"})

    def record(args: dict[str, object]) -> str:
        value = cast(str, args["text"])
        effects.append(value)
        return value

    def event(item: object) -> None:
        if getattr(item, "type", None) == "response.completed" and len(requests) == 1:
            assert effects == []
            assert saved[-1]["phase"] == "pending"

    async def arecord(args: dict[str, object]) -> str:
        return record(args)

    async def asave(checkpoint: ResponsesToolCheckpoint) -> None:
        saved.append(checkpoint)

    async def aevent(item: object) -> None:
        event(item)

    async def exercise() -> None:
        if lane == "sync":
            runner = ResponsesToolRunner(
                functions=[RegisteredFunction(TOOL, record)],
                early_execution={"functions": ["record"]} if policy else None,
            )
            with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                runner.run(
                    client,
                    PARAMS,
                    stream=True,
                    eager=True,
                    on_event=event,
                    ledger=ResponsesToolLedger("sparse", saved.append),
                )
        else:
            runner_async = AsyncResponsesToolRunner(
                functions=[AsyncRegisteredFunction(TOOL, arecord)],
                early_execution={"functions": ["record"]} if policy else None,
            )
            async with AsyncOpenAI(
                api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
            ) as client_async:
                await runner_async.run(
                    client_async,
                    PARAMS,
                    stream=True,
                    eager=True,
                    on_event=aevent,
                    ledger=AsyncResponsesToolLedger("sparse", asave),
                )

    if case == "interrupted":
        with pytest.raises(ToolRunnerError):
            await exercise()
        assert len(requests) == 1 and effects == []
        assert saved[-1]["phase"] == "pending"
        assert saved[-1]["returned_call_ids"] == []
    elif case == "final-gap":
        await exercise()
        assert len(requests) == 1 and effects == []
        assert saved[-1]["phase"] == "final" and saved[-1]["returned_call_ids"] == []
    else:
        await exercise()
        assert effects == ["first", "second"]
        assert [item["call_id"] for item in requests[1]["input"] if item.get("type") == "function_call_output"] == [
            "c1",
            "c2",
        ]
        assert saved[-1]["phase"] == "final" and saved[-1]["returned_call_ids"] == ["c1", "c2"]
