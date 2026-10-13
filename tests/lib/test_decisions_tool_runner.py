from __future__ import annotations

import json
import asyncio
import inspect
from typing import Any, Callable, Iterator, cast
from typing_extensions import Literal, override

import httpx2
import pytest
from pydantic import StrictStr, StrictBool

from openai import OpenAI, AsyncOpenAI
from openai.types import Decision
from openai.lib.tool_diagnostics import ToolDiagnostic, ToolDiagnosticObserver
from openai.lib.decisions_tool_runner import (
    DecisionCandidate,
    DecisionsRunResult,
    DecisionObservation,
    DecisionsToolRunner,
    DecisionsRunnerParams,
    AsyncDecisionCandidate,
    AsyncDecisionsToolRunner,
    DecisionsToolRunnerError,
    DecisionsToolRunnerCancelledError,
)
from openai.types.decision_input_part_union_param import DecisionInputPartUnionParam

PARAMS: DecisionsRunnerParams = {"model": "", "input": "Complete the fixture.", "safety_identifier": "fixture_user"}
DONE: DecisionCandidate = {"id": "finish", "description": "Task is complete", "done": True}


@pytest.mark.parametrize("kind", ["coroutine", "future"])
async def test_sync_executor_rejects_awaitables_before_recording_completion(kind: str) -> None:
    effects: list[str] = []
    requests: list[dict[str, Any]] = []
    diagnostics: list[ToolDiagnostic] = []

    async def execute() -> None:
        effects.append("act")

    value = execute() if kind == "coroutine" else asyncio.get_running_loop().create_future()
    try:
        with pytest.raises(DecisionsToolRunnerError, match="AsyncDecisionsToolRunner") as exc:
            await run(
                "sync",
                [decision("act"), decision("finish")],
                requests,
                observe=lambda: "fixture",
                candidates=lambda _: [DONE, {"id": "act", "description": "act", "execute": lambda: value}],
                on_diagnostic=diagnostics.append,
            )
        assert exc.value.reason == "async_executor"
        assert exc.value.attempted_candidate_ids == ("act",)
        assert exc.value.completed_candidate_ids == ()
        assert effects == [] and len(requests) == 1
        assert [event["reason"] for event in diagnostics if event["stage"] == "action"] == ["driver_failed"]
        if inspect.iscoroutine(value):
            assert inspect.getcoroutinestate(value) == inspect.CORO_CLOSED
        else:
            assert not value.done() and not value.cancelled()
    finally:
        if inspect.iscoroutine(value):
            value.close()
        else:
            value.cancel()


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    ("field", "missing", "value"),
    [
        ("model", True, None),
        ("model", False, None),
        ("usage", True, None),
        ("usage", False, None),
        ("input_tokens", True, None),
        ("total_tokens", False, "invalid"),
        ("input_tokens_details", False, None),
        ("cached_tokens", True, None),
        ("output_tokens_details", True, None),
        ("reasoning_tokens", False, None),
    ],
)
async def test_requires_complete_decision_metadata_before_dispatch(
    lane: str, field: str, missing: bool, value: object
) -> None:
    response = decision("act")
    owner = response
    if field not in {"model", "usage"}:
        owner = cast(dict[str, object], response["usage"])
        if field == "cached_tokens":
            owner = cast(dict[str, object], owner["input_tokens_details"])
        elif field == "reasoning_tokens":
            owner = cast(dict[str, object], owner["output_tokens_details"])
    if missing:
        del owner[field]
    else:
        owner[field] = value
    effects: list[str] = []
    requests: list[dict[str, Any]] = []

    def candidates(_observation: DecisionObservation) -> list[DecisionCandidate]:
        return [DONE, {"id": "act", "description": "set", "execute": lambda: effects.append("act")}]

    with pytest.raises(DecisionsToolRunnerError) as exc:
        await run(lane, [response, decision("finish")], requests, observe=lambda: "fixture", candidates=candidates)
    assert exc.value.reason == "invalid_answer"
    assert effects == []
    assert len(requests) == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_keeps_decision_metadata_extensions_without_counter_ranges(lane: str) -> None:
    response = decision("finish")
    response["model"] = "fixture-model-not-from-a-list"
    response["extra"] = None
    usage = cast(dict[str, object], response["usage"])
    usage.update(input_tokens=-4, output_tokens=9, total_tokens=0, future={"note": "keep"})
    cast(dict[str, object], usage["input_tokens_details"])["future"] = None
    effects: list[str] = []

    def candidates(_observation: DecisionObservation) -> list[DecisionCandidate]:
        return [DONE, {"id": "act", "description": "unused", "execute": lambda: effects.append("act")}]

    result = await run(lane, [response], [], observe=lambda: "fixture", candidates=candidates)
    assert result["status"] == "unverified"
    assert result["decisions"][0].to_dict() == response
    assert effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("trigger", ["usage", "diagnostic"])
async def test_owns_decision_before_request_metadata(lane: str, trigger: str, monkeypatch: pytest.MonkeyPatch) -> None:
    effects: list[str] = []
    replacement = Decision.construct(**cast(dict[str, Any], decision("act"))).answers[0]

    class MetadataDecision(Decision):
        @override
        def __getattribute__(self, name: str) -> Any:
            if name == "usage" and trigger == "usage":
                self.answers[:] = [replacement]
            return super().__getattribute__(name)

    response = MetadataDecision.construct(**cast(dict[str, Any], decision("finish")))

    def diagnostic(event: ToolDiagnostic) -> None:
        if trigger == "diagnostic" and event["stage"] == "request":
            response.answers[:] = [replacement]

    def execute() -> None:
        effects.append("unselected")

    if lane == "sync":
        with OpenAI(api_key="fixture") as client:

            def create_sync(**_kwargs: object) -> Decision:
                return response

            monkeypatch.setattr(client.decisions, "create", create_sync)
            result = DecisionsToolRunner(
                observe=lambda: "fixture",
                candidates=lambda _: [DONE, {"id": "act", "description": "unused", "execute": execute}],
            ).run(client, PARAMS, on_diagnostic=diagnostic)
    else:

        async def create(**_kwargs: object) -> Decision:
            return response

        async def observe() -> str:
            return "fixture"

        async def aexecute() -> None:
            execute()

        async def candidates(_: DecisionObservation) -> list[AsyncDecisionCandidate]:
            return [cast(AsyncDecisionCandidate, DONE), {"id": "act", "description": "unused", "execute": aexecute}]

        async with AsyncOpenAI(api_key="fixture") as client_async:
            monkeypatch.setattr(client_async.decisions, "create", create)
            result = await AsyncDecisionsToolRunner(observe=observe, candidates=candidates).run(
                client_async, PARAMS, on_diagnostic=diagnostic
            )
    assert result["status"] == "unverified"
    assert effects == []
    assert result["decisions"][0].answers[0].type == "choice"
    assert result["decisions"][0].answers[0].choice == "finish"


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_refusal_snapshot_rechecks_name_after_native_getter(lane: str, monkeypatch: pytest.MonkeyPatch) -> None:
    from openai.types.decision import AnswerAnswerResourceRefusal

    class RenamedRefusal(AnswerAnswerResourceRefusal):
        @override
        def __getattribute__(self, name: str) -> Any:
            value = super().__getattribute__(name)
            if name == "name" and value == "next_action":
                object.__setattr__(self, "name", "different_question")
            return value

    answer = RenamedRefusal(name="next_action", type="refusal")
    response = Decision.construct(**cast(dict[str, Any], decision(None, kind="refusal")))
    response.answers = [answer]
    effects: list[str] = []
    requests: list[str] = []

    if lane == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(trust_env=False)) as client:

            def create_sync(**_kwargs: object) -> Decision:
                requests.append("decision")
                return response

            monkeypatch.setattr(client.decisions, "create", create_sync)
            runner = DecisionsToolRunner(
                observe=lambda: "fixture",
                candidates=lambda _: [
                    DONE,
                    {"id": "act", "description": "Act", "execute": lambda: effects.append("act")},
                ],
            )
            with pytest.raises(DecisionsToolRunnerError) as exc:
                runner.run(client, PARAMS, max_steps=2)
    else:

        async def create_async(**_kwargs: object) -> Decision:
            requests.append("decision")
            return response

        async def observe() -> str:
            return "fixture"

        async def candidates(_observation: DecisionObservation) -> list[AsyncDecisionCandidate]:
            async def act() -> None:
                effects.append("act")

            return [cast(AsyncDecisionCandidate, DONE), {"id": "act", "description": "Act", "execute": act}]

        async with AsyncOpenAI(api_key="fake", http_client=httpx2.AsyncClient(trust_env=False)) as client_async:
            monkeypatch.setattr(client_async.decisions, "create", create_async)
            with pytest.raises(DecisionsToolRunnerError) as exc:
                await AsyncDecisionsToolRunner(observe=observe, candidates=candidates).run(
                    client_async, PARAMS, max_steps=2
                )
    assert exc.value.reason == "invalid_answer"
    assert effects == [] and requests == ["decision"]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_candidate_list_uses_native_indexed_entries(lane: str) -> None:
    class Candidates(list[dict[str, object]]):
        @override
        def __iter__(self) -> Iterator[dict[str, object]]:
            raise AssertionError("Custom iterator must not run")

    requests: list[dict[str, Any]] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        return httpx2.Response(200, json=decision("finish"))

    def execute() -> None:
        raise AssertionError("The unselected action must not run")

    async def aexecute() -> None:
        execute()

    values = Candidates(
        [dict(DONE), {"id": "act", "description": "Unused", "execute": execute if lane == "sync" else aexecute}]
    )
    if lane == "sync":
        with OpenAI(api_key="fixture", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            result = DecisionsToolRunner(
                observe=lambda: "state", candidates=lambda _: cast(list[DecisionCandidate], values)
            ).run(client, PARAMS)
    else:

        async def observe() -> str:
            return "state"

        async def candidates(_observation: DecisionObservation) -> list[AsyncDecisionCandidate]:
            return cast(list[AsyncDecisionCandidate], values)

        async with AsyncOpenAI(
            api_key="fixture", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            result = await AsyncDecisionsToolRunner(observe=observe, candidates=candidates).run(client_async, PARAMS)
    assert result["status"] == "unverified"
    assert len(requests) == 1
    assert requests[0]["questions"][0]["choices"] == [
        {"value": "finish", "description": "Task is complete"},
        {"value": "act", "description": "Unused"},
    ]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_candidate_mapping_cannot_fabricate_missing_fields(lane: str) -> None:
    reads: list[str] = []
    requests: list[httpx2.Request] = []

    class MissingID(dict[str, object]):
        @override
        def get(self, key: str, default: object = None) -> Any:
            reads.append(key)
            if key == "id":
                return "invented"
            return super().get(key, default)

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=decision("invented"))

    values = [MissingID(description="Not defined", done=True)]
    if lane == "sync":
        with OpenAI(api_key="fixture", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            runner = DecisionsToolRunner(
                observe=lambda: "state", candidates=lambda _: cast(list[DecisionCandidate], values)
            )
            with pytest.raises(DecisionsToolRunnerError) as exc:
                runner.run(client, PARAMS)
    else:

        async def observe() -> str:
            return "state"

        async def candidates(_observation: DecisionObservation) -> list[AsyncDecisionCandidate]:
            return cast(list[AsyncDecisionCandidate], values)

        async with AsyncOpenAI(
            api_key="fixture", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:
            runner_async = AsyncDecisionsToolRunner(observe=observe, candidates=candidates)
            with pytest.raises(DecisionsToolRunnerError) as exc:
                await runner_async.run(client_async, PARAMS)
    assert exc.value.reason == "invalid_candidates"
    assert reads == [] and requests == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "fields",
    [
        {"omit": "confidence"},
        {"omit": "probabilities"},
        {"confidence": None},
        {"confidence": "not a number"},
        {"probabilities": None},
        {"probabilities": [None]},
        {"probabilities": [{"value": "act"}]},
        {"probabilities": [{"probability": 0.5}]},
        {"probabilities": [{"value": True, "probability": "not a number"}]},
    ],
)
async def test_complete_choice_required_before_dispatch(lane: str, fields: dict[str, Any]) -> None:
    response = decision("act")
    first = cast(list[dict[str, Any]], response["answers"])[0]
    first.update(fields)
    if "omit" in fields:
        del first[fields["omit"]]
    requests: list[dict[str, Any]] = []
    effects: list[str] = []

    def candidates(_observation: DecisionObservation) -> list[DecisionCandidate]:
        return [
            {"id": "finish", "description": "finished", "done": True},
            {"id": "act", "description": "change fixture", "execute": lambda: effects.append("act")},
        ]

    with pytest.raises(DecisionsToolRunnerError) as failure:
        await run(lane, [response, decision("finish")], requests, observe=lambda: "fixture", candidates=candidates)
    assert failure.value.reason == "invalid_answer"
    assert effects == []
    assert len(requests) == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_complete_choice_probability_values_and_extras_remain_native(lane: str) -> None:
    response = decision("finish")
    first = cast(list[dict[str, Any]], response["answers"])[0]
    first["probabilities"] = [{"value": True, "probability": -2, "extra": "keep"}, {"value": "true", "probability": 3}]
    effects: list[str] = []

    def candidates(_observation: DecisionObservation) -> list[DecisionCandidate]:
        return [
            {"id": "finish", "description": "finished", "done": True},
            {"id": "act", "description": "change fixture", "execute": lambda: effects.append("act")},
        ]

    result = await run(lane, [response], [], observe=lambda: "fixture", candidates=candidates)
    assert result["decisions"][0].to_dict()["answers"] == [first]
    assert effects == []


def decision(value: object, *, name: str = "next_action", kind: str = "choice") -> dict[str, object]:
    return {
        "model": "",
        "usage": {
            "input_tokens": 2,
            "output_tokens": 1,
            "total_tokens": 3,
            "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0},
        },
        "answers": [{"type": kind, "name": name, "choice": value, "confidence": 0.9, "probabilities": []}],
    }


async def run(
    lane: str,
    replies: list[dict[str, object]],
    requests: list[dict[str, Any]],
    *,
    observe: Callable[[], DecisionObservation],
    candidates: Callable[[DecisionObservation], list[DecisionCandidate]],
    verify: Callable[[DecisionObservation], bool] | None = None,
    params: DecisionsRunnerParams | None = None,
    max_steps: int = 20,
    cancelled: Callable[[], bool] | None = None,
    during_request: Callable[[], None] | None = None,
    api_failure: bool = False,
    on_diagnostic: ToolDiagnosticObserver | None = None,
) -> DecisionsRunResult:
    def transport(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/v1/decisions"
        requests.append(json.loads(request.content))
        if during_request:
            during_request()
        if api_failure and len(requests) > 1:
            return httpx2.Response(403, json={"error": {"message": "private body", "type": "blocked"}})
        return httpx2.Response(200, json=replies[len(requests) - 1])

    if lane == "sync":
        with OpenAI(
            api_key="fake",
            max_retries=0,
            base_url="http://fixture.invalid/v1",
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:
            return DecisionsToolRunner(observe=observe, candidates=candidates, verify=verify).run(
                client,
                PARAMS if params is None else params,
                max_steps=max_steps,
                cancelled=cancelled,
                on_diagnostic=on_diagnostic,
            )

    async def observe_async() -> DecisionObservation:
        return observe()

    async def candidates_async(obs: DecisionObservation) -> list[AsyncDecisionCandidate]:
        # Capture each callable now, so mutation of the original candidate after
        # this callback returns cannot change what this fixture registered.
        out: list[AsyncDecisionCandidate] = []
        for value in candidates(obs):
            if value.get("done") is True:
                out.append(cast(AsyncDecisionCandidate, dict(value)))
                continue
            fn = value.get("execute")
            if callable(fn):

                async def execute(selected: Callable[[], object] = fn) -> object:
                    return selected()

                out.append(cast(AsyncDecisionCandidate, {**value, "execute": execute}))
            else:
                out.append(cast(AsyncDecisionCandidate, dict(value)))
        return out

    async def verify_async(obs: DecisionObservation) -> bool:
        assert verify is not None
        return verify(obs)

    async with AsyncOpenAI(
        api_key="fake",
        max_retries=0,
        base_url="http://fixture.invalid/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
    ) as async_client:
        return await AsyncDecisionsToolRunner(
            observe=observe_async,
            candidates=candidates_async,
            verify=verify_async if verify else None,
        ).run(
            async_client,
            PARAMS if params is None else params,
            max_steps=max_steps,
            cancelled=cancelled,
            on_diagnostic=on_diagnostic,
        )


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("at_verification", [False, True])
async def test_missing_observation_part_stops_before_candidates_or_verification(
    lane: str, at_verification: bool
) -> None:
    requests: list[dict[str, Any]] = []
    calls: list[str] = []

    def observe() -> DecisionObservation:
        calls.append("observe")
        if at_verification and len(calls) == 1:
            return "done"
        return cast(DecisionObservation, [{"type": "input_text", "text": "present"}, None])

    def candidates(_: DecisionObservation) -> list[DecisionCandidate]:
        calls.append("candidates")
        if at_verification:
            return [DONE]
        return [DONE, {"id": "act", "description": "set", "execute": lambda: calls.append("execute")}]

    def verify(_: DecisionObservation) -> bool:
        calls.append("verify")
        return True

    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(lane, [decision("finish")], requests, observe=observe, candidates=candidates, verify=verify)
    assert err.value.reason == "failed"
    assert err.value.attempted_candidate_ids == err.value.completed_candidate_ids == ()
    assert calls == (["observe", "candidates", "observe"] if at_verification else ["observe"])
    assert requests == []


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_generated_inline_image_iterable_is_owned_before_callbacks(lane: str) -> None:
    effects: list[str] = []
    raw: list[DecisionInputPartUnionParam] = [
        {"type": "input_text", "text": "safe page"},
        {"type": "input_image", "image_url": "data:image/png;base64,aW1hZ2U="},
    ]
    requests: list[dict[str, Any]] = []

    def candidates(obs: DecisionObservation) -> list[DecisionCandidate]:
        assert not isinstance(obs, str)
        copy = list(obs)
        assert copy[0]["type"] == "input_text"
        copy[0]["text"] = "changed by provider"
        return [{"id": "act", "description": "Perform action", "execute": lambda: effects.append("act")}, DONE]

    result = await run(
        lane,
        [decision("act"), decision("finish")],
        requests,
        observe=lambda: (part for part in raw),
        candidates=candidates,
        verify=lambda _: effects == ["act"],
    )
    assert result["status"] == "verified"
    assert result["attempted_candidate_ids"] == result["completed_candidate_ids"] == ["act"]
    assert len(result["decisions"]) == len(requests) == 2
    for request in requests:
        assert request["input"] == [{"role": "user", "content": PARAMS["input"]}, {"role": "user", "content": raw}]
        assert request["questions"][0]["name"] == "next_action"
        assert request["questions"][0]["choices"] == [
            {"value": "act", "description": "Perform action"},
            {"value": "finish", "description": "Task is complete"},
        ]
        assert request["safety_identifier"] == "fixture_user"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("verification", [True, None, False, 1])
async def test_done_only_has_no_request_and_never_invents_verification(lane: str, verification: object) -> None:
    requests: list[dict[str, Any]] = []
    observations: list[str] = []

    def observe() -> str:
        observations.append("read")
        return "already done"

    async def work() -> DecisionsRunResult:
        return await run(
            lane,
            [],
            requests,
            observe=observe,
            candidates=lambda _: [DONE],
            verify=None if verification is None else lambda _: cast(bool, verification),
        )

    if verification is True or verification is None:
        result = await work()
        assert result["status"] == ("verified" if verification is True else "unverified")
        assert result["decisions"] == [] and result["attempted_candidate_ids"] == []
    else:
        with pytest.raises(DecisionsToolRunnerError) as err:
            await work()
        assert err.value.reason == ("verification_failed" if verification is False else "invalid_verification")
    assert observations == (["read"] if verification is None else ["read", "read"])
    assert requests == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("with_verify", [False, True])
@pytest.mark.parametrize("after_action", [False, True])
async def test_finish_selection_stop_precedes_final_observation_or_result(
    lane: str, with_verify: bool, after_action: bool
) -> None:
    requests: list[dict[str, Any]] = []
    events: list[str] = []
    stopped = False
    completed = not after_action

    def observe() -> DecisionObservation:
        events.append("observe")
        return str(completed)

    def complete() -> None:
        nonlocal completed
        completed = True

    def candidates(_: DecisionObservation) -> list[DecisionCandidate]:
        if completed:
            return [DONE]
        return [DONE, {"id": "set", "description": "Set the local state", "execute": complete}]

    def verify(_: DecisionObservation) -> bool:
        events.append("verify")
        return True

    def diagnostic(event: ToolDiagnostic) -> None:
        nonlocal stopped
        if event["stage"] == "selection" and event.get("call_id") == "finish":
            stopped = True

    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(
            lane,
            [decision("set")] if after_action else [],
            requests,
            observe=observe,
            candidates=candidates,
            verify=verify if with_verify else None,
            cancelled=lambda: stopped,
            on_diagnostic=diagnostic,
        )
    assert err.value.reason == "cancelled"
    assert err.value.attempted_candidate_ids == (("set",) if after_action else ())
    assert err.value.completed_candidate_ids == (("set",) if after_action else ())
    assert events == (["observe", "observe"] if after_action else ["observe"])
    assert len(requests) == int(after_action)


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_am_verification_diagnostic_stop_already_precedes_result(lane: str) -> None:
    requests: list[dict[str, Any]] = []
    stopped = False

    def diagnostic(event: ToolDiagnostic) -> None:
        nonlocal stopped
        if event["stage"] == "verification":
            stopped = True

    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(
            lane,
            [],
            requests,
            observe=lambda: "complete",
            candidates=lambda _: [DONE],
            verify=lambda _: True,
            cancelled=lambda: stopped,
            on_diagnostic=diagnostic,
        )
    assert err.value.reason == "cancelled"
    assert err.value.attempted_candidate_ids == ()
    assert err.value.completed_candidate_ids == ()
    assert not requests


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_refusal_diagnostic_stop_precedes_result(lane: str) -> None:
    requests: list[dict[str, Any]] = []
    effects: list[str] = []
    stopped = False

    def diagnostic(event: ToolDiagnostic) -> None:
        nonlocal stopped
        if event["stage"] == "selection" and event["reason"] == "refused":
            stopped = True

    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(
            lane,
            [decision(None, kind="refusal")],
            requests,
            observe=lambda: "fixture",
            candidates=lambda _: [
                DONE,
                {"id": "set", "description": "Set fixture", "execute": lambda: effects.append("set")},
            ],
            cancelled=lambda: stopped,
            on_diagnostic=diagnostic,
        )
    assert err.value.reason == "cancelled"
    assert err.value.attempted_candidate_ids == ()
    assert err.value.completed_candidate_ids == ()
    assert len(requests) == 1
    assert not effects


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_verification_false_can_choose_again_with_new_observation(lane: str) -> None:
    effects: list[str] = []
    observations: list[int] = []
    requests: list[dict[str, Any]] = []

    def observe() -> str:
        observations.append(len(effects))
        return str(len(effects))

    result = await run(
        lane,
        [decision("finish"), decision("act"), decision("finish")],
        requests,
        max_steps=3,
        observe=observe,
        verify=lambda _: bool(effects),
        candidates=lambda _: [
            {"id": "act", "description": "Change state", "execute": lambda: effects.append("done")},
            DONE,
        ],
    )
    assert result["status"] == "verified"
    assert observations == [0, 0, 0, 1, 1] and effects == ["done"]
    assert len(requests) == 3


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_snapshot_primitive_params_candidates_and_executor_while_api_pending(lane: str) -> None:
    effects: list[str] = []
    source: list[DecisionCandidate] = [
        {"id": "act", "description": "original", "execute": lambda: effects.append("original")},
        DONE.copy(),
    ]
    params: DecisionsRunnerParams = {**PARAMS}
    requests: list[dict[str, Any]] = []

    def mutate() -> None:
        item = cast(dict[str, object], source[0])
        item["execute"] = lambda: effects.append("different")
        item["description"] = "different"
        item["id"] = "other"
        item["done"] = True
        params["input"] = "different task"
        source[:] = [DONE]

    result = await run(
        lane,
        [decision("act")],
        requests,
        observe=lambda: "page",
        candidates=lambda _: source,
        params=params,
        during_request=mutate,
    )
    assert effects == ["original"]
    assert result["status"] == "unverified"
    assert requests[0]["input"][0]["content"] == PARAMS["input"]
    assert requests[0]["questions"][0]["choices"][0] == {"value": "act", "description": "original"}


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("value", ["unknown", True, "other_kind", "wrong_name", "refusal", "extra", "missing"])
async def test_non_action_response_after_effect_preserves_evidence(lane: str, value: object) -> None:
    effects: list[str] = []
    requests: list[dict[str, Any]] = []
    second = decision(value)
    if value == "other_kind":
        second = decision("act", kind="predicate")
    if value == "wrong_name":
        second = decision("act", name="other")
    if value == "refusal":
        second = decision(None, kind="refusal")
    if value in ("extra", "missing"):
        second["answers"] = (
            [*cast(list[object], second["answers"]), *cast(list[object], second["answers"])] if value == "extra" else []
        )

    async def work() -> DecisionsRunResult:
        return await run(
            lane,
            [decision("act"), second],
            requests,
            observe=lambda: "page",
            candidates=lambda _: [
                {"id": "act", "description": "do", "execute": lambda: effects.append("effect")},
                DONE,
            ],
        )

    if value == "refusal":
        result = await work()
        assert result["status"] == "refused"
        assert result["attempted_candidate_ids"] == result["completed_candidate_ids"] == ["act"]
        assert len(result["decisions"]) == 2
    else:
        with pytest.raises(DecisionsToolRunnerError) as err:
            await work()
        assert err.value.reason == "invalid_answer"
        assert err.value.attempted_candidate_ids == err.value.completed_candidate_ids == ("act",)
    assert effects == ["effect"] and len(requests) == 2


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "variant", ["empty", "too_many", "duplicate", "no_done", "two_done", "done_executor", "invalid_executor"]
)
async def test_invalid_registry_fails_before_request(lane: str, variant: str) -> None:
    effects: list[str] = []
    requests: list[dict[str, Any]] = []
    action: DecisionCandidate = {"id": "act", "description": "do", "execute": lambda: effects.append("effect")}
    cases = {
        "empty": [],
        "too_many": [*({"id": str(i), "description": "do", "execute": lambda: None} for i in range(255)), DONE],
        "duplicate": [action, action, DONE],
        "no_done": [action],
        "two_done": [DONE, {"id": "end", "description": "end", "done": True}],
        "done_executor": [{"id": "end", "description": "end", "done": True, "execute": lambda: effects.append("bad")}],
        "invalid_executor": [{"id": "act", "description": "do", "execute": 9}, DONE],
    }
    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(
            lane,
            [],
            requests,
            observe=lambda: "page",
            candidates=lambda _: cast(list[DecisionCandidate], cases[variant]),
        )
    assert err.value.reason == "invalid_candidates"
    assert requests == [] and effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("failure", ["step_limit", "mutate_throw", "cancel", "api"])
async def test_no_repeat_or_lost_evidence_at_interruption(lane: str, failure: str) -> None:
    effects: list[str] = []

    def action() -> None:
        effects.append("effect")
        if failure == "mutate_throw":
            raise RuntimeError("private callback body")

    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(
            lane,
            [decision("act"), decision("act")],
            [],
            observe=lambda: "page",
            candidates=lambda _: [{"id": "act", "description": "do", "execute": action}, DONE],
            max_steps=1 if failure == "step_limit" else 2,
            cancelled=(lambda: bool(effects)) if failure == "cancel" else None,
            api_failure=failure == "api",
        )
    assert effects == ([] if failure == "step_limit" else ["effect"])
    assert err.value.attempted_candidate_ids == (() if failure == "step_limit" else ("act",))
    assert err.value.completed_candidate_ids == (() if failure in ("step_limit", "mutate_throw") else ("act",))
    assert "private" not in str(err.value)
    assert err.value.__cause__ is None


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "bad", [{"stream": True}, {"questions": []}, {"previous_response_id": "resp"}, {"background": False}]
)
async def test_unknown_params_stop_before_observation(lane: str, bad: dict[str, object]) -> None:
    def observe() -> str:
        pytest.fail("called before validation")

    with pytest.raises(DecisionsToolRunnerError, match="supported run options"):
        await run(
            lane,
            [],
            [],
            observe=observe,
            candidates=lambda _: [DONE],
            params=cast(DecisionsRunnerParams, {**PARAMS, **bad}),
        )


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_actual_cancellation_keeps_completed_and_attempted_ids(lane: str) -> None:
    effects: list[str] = []
    calls = 0

    def action() -> None:
        nonlocal calls
        calls += 1
        effects.append("effect")
        if calls == 2:
            raise asyncio.CancelledError("private cancellation detail")

    with pytest.raises(asyncio.CancelledError) as err:
        await run(
            lane,
            [decision("act"), decision("act")],
            [],
            max_steps=3,
            observe=lambda: "page",
            candidates=lambda _: [{"id": "act", "description": "do", "execute": action}, DONE],
        )
    assert isinstance(err.value, DecisionsToolRunnerCancelledError)
    assert err.value.attempted_candidate_ids == ("act", "act")
    assert err.value.completed_candidate_ids == ("act",)
    assert effects == ["effect", "effect"] and "private" not in str(err.value)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
async def test_invalid_request_limit_stops_before_observation(lane: str, limit: object) -> None:
    def observe() -> str:
        pytest.fail("observed before limit validation")

    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(lane, [], [], observe=observe, candidates=lambda _: [DONE], max_steps=cast(int, limit))
    assert err.value.reason == "invalid_params"


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_final_request_can_verify_done_with_255_candidates(lane: str) -> None:
    requests: list[dict[str, Any]] = []
    effects: list[str] = []

    def candidates(_obs: DecisionObservation) -> list[DecisionCandidate]:
        return [
            *[
                {"id": str(index), "description": "perform", "execute": lambda: effects.append("effect")}
                for index in range(254)
            ],
            DONE,
        ]

    result = await run(
        lane,
        [decision("finish")],
        requests,
        max_steps=1,
        observe=lambda: "done",
        candidates=candidates,
        verify=lambda _: True,
    )
    assert result["status"] == "verified"
    assert len(requests) == 1 and len(requests[0]["questions"][0]["choices"]) == 255
    assert effects == []


async def test_async_executor_and_done_marker_snapshot_owns_the_actual_registration() -> None:
    effects: list[str] = []
    requests: list[dict[str, Any]] = []

    async def original() -> None:
        effects.append("original")

    async def replacement() -> None:
        effects.append("replacement")

    registered: list[AsyncDecisionCandidate] = [
        {"id": "act", "description": "original action", "execute": original},
        {"id": "done", "description": "Already complete", "done": True},
    ]

    async def observe() -> str:
        return "page"

    async def candidates(_obs: DecisionObservation) -> list[AsyncDecisionCandidate]:
        return registered

    def transport(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        # This is the same list and TypedDict instance returned by the awaited
        # callback, with no test-fixture conversion between it and the runner.
        item = cast(dict[str, object], registered[0])
        item.update(id="changed", description="changed", execute=replacement, done=True)
        registered[:] = [{"id": "done", "description": "Already complete", "done": True}]
        return httpx2.Response(200, json=decision("act"))

    async with AsyncOpenAI(
        api_key="fake",
        base_url="http://fixture.invalid/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
    ) as client:
        result = await AsyncDecisionsToolRunner(observe=observe, candidates=candidates).run(client, PARAMS)
    assert effects == ["original"]
    assert result["attempted_candidate_ids"] == result["completed_candidate_ids"] == ["act"]
    assert len(requests) == 1 and result["status"] == "unverified"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("variant", ["nested", "altered_error"])
async def test_callback_runner_errors_cannot_replace_outer_execution_evidence(lane: str, variant: str) -> None:
    effects: list[str] = []

    def action() -> None:
        effects.append("started")
        if variant == "altered_error":
            err = DecisionsToolRunnerError("invalid_candidates", ["other"], ["other"])
            err.args = ("private callback details",)
            raise err
        with OpenAI(api_key="fake", base_url="http://fixture.invalid/v1") as nested_client:
            # No request: the nested runner rejects an empty candidate list.
            DecisionsToolRunner(observe=lambda: "nested", candidates=lambda _: []).run(nested_client, PARAMS)

    with pytest.raises(DecisionsToolRunnerError) as err:
        await run(
            lane,
            [decision("act")],
            [],
            observe=lambda: "page",
            candidates=lambda _: [{"id": "act", "description": "run", "execute": action}, DONE],
        )
    assert effects == ["started"]
    assert err.value.reason == "failed"
    assert err.value.attempted_candidate_ids == ("act",)
    assert err.value.completed_candidate_ids == ()
    assert "private" not in str(err.value) and err.value.__cause__ is None


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_pending_request_cannot_retarget_run_observer_or_verifier(lane: str) -> None:
    observed: list[str] = []
    requests: list[dict[str, Any]] = []
    if lane == "sync":

        def observe() -> str:
            observed.append("original")
            return "page"

        runner = DecisionsToolRunner(
            observe=observe,
            candidates=lambda _: [{"id": "act", "description": "run", "execute": lambda: None}, DONE],
            verify=lambda _: False,
        )

        def replacement_candidates(_obs: DecisionObservation) -> list[DecisionCandidate]:
            return [DONE]

        def replacement_verify(_obs: DecisionObservation) -> bool:
            return True

        def transport(request: httpx2.Request) -> httpx2.Response:
            requests.append(json.loads(request.content))
            runner.observe = lambda: "replaced page"
            runner.candidates = replacement_candidates
            runner.verify = replacement_verify
            return httpx2.Response(200, json=decision("finish"))

        with OpenAI(
            api_key="fake",
            base_url="http://fixture.invalid/v1",
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:
            with pytest.raises(DecisionsToolRunnerError) as err:
                runner.run(client, PARAMS, max_steps=1)
    else:

        async def observe_async() -> str:
            observed.append("original")
            return "page"

        async def execute() -> None:
            pass

        async def candidates(_obs: DecisionObservation) -> list[AsyncDecisionCandidate]:
            return [
                {"id": "act", "description": "run", "execute": execute},
                {"id": "finish", "description": "done", "done": True},
            ]

        async def verify(_obs: DecisionObservation) -> bool:
            return False

        async def replacement(_obs: DecisionObservation) -> bool:
            return True

        async def replacement_observe() -> str:
            return "replaced page"

        async_runner = AsyncDecisionsToolRunner(observe=observe_async, candidates=candidates, verify=verify)

        def async_transport(request: httpx2.Request) -> httpx2.Response:
            requests.append(json.loads(request.content))
            async_runner.observe = replacement_observe
            async_runner.verify = replacement
            return httpx2.Response(200, json=decision("finish"))

        async with AsyncOpenAI(
            api_key="fake",
            base_url="http://fixture.invalid/v1",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(async_transport)),
        ) as async_client:
            with pytest.raises(DecisionsToolRunnerError) as err:
                await async_runner.run(async_client, PARAMS, max_steps=1)
    assert err.value.reason == "step_limit"
    assert err.value.attempted_candidate_ids == err.value.completed_candidate_ids == ()
    assert len(requests) == 1 and observed == ["original", "original"]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("observer_fails", [False, True])
async def test_private_observations_do_not_escape_diagnostics_after_failed_decision(
    lane: str, observer_fails: bool
) -> None:
    events: list[ToolDiagnostic] = []
    effects: list[str] = []
    requests: list[dict[str, Any]] = []

    def observe_event(event: ToolDiagnostic) -> None:
        events.append(event.copy())
        event["call_id"] = "replacement"
        if observer_fails:
            raise RuntimeError("sentinel-observer-secret")

    def execute() -> None:
        effects.append("original")
        raise RuntimeError("sentinel-driver-secret")

    with pytest.raises(DecisionsToolRunnerError) as error:
        await run(
            lane,
            [decision("original")],
            requests,
            observe=lambda: [
                {"type": "input_text", "text": "sentinel-private-page"},
                {"type": "input_image", "image_url": "data:image/png;base64,c2VudGluZWw="},
            ],
            candidates=lambda _observation: [
                {"id": "original", "description": "sentinel-secret-description", "execute": execute},
                DONE,
            ],
            on_diagnostic=observe_event,
        )
    assert effects == ["original"]
    assert error.value.attempted_candidate_ids == ("original",)
    assert error.value.completed_candidate_ids == ()
    assert [(event["stage"], event["reason"]) for event in events] == [
        ("request", "completed"),
        ("selection", "completed"),
        ("action", "driver_failed"),
    ]
    assert events[0]["usage"] == {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3}
    assert events[1]["call_id"] == "original" and events[2]["call_id"] == "original"
    assert all(event["duration_ms"] >= 0 for event in events)
    assert "sentinel" not in json.dumps(events)
    assert "data:image" not in json.dumps(events)


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_decisions_admission_closes_from_inflight_callback_without_losing_receipts(lane: str) -> None:
    calls: list[str] = []
    requests: list[str] = []
    done = False

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request.url.path)
        return httpx2.Response(200, json=decision("work"))

    def stopped() -> bool:
        return False

    def work(*, cancelled: Callable[[], bool] | None = None) -> None:
        nonlocal done
        assert cancelled is stopped
        done = True
        calls.append("work")

    if lane == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:

            def observe() -> DecisionObservation:
                if not done:
                    with pytest.raises(RuntimeError, match="busy"):
                        runner.run(client, PARAMS)
                    assert runner.close() == {"status": "draining"}
                    with pytest.raises(RuntimeError, match="closed"):
                        runner.run(client, PARAMS)
                return "state"

            def candidates(_obs: DecisionObservation) -> list[DecisionCandidate]:
                return [DONE] if done else [{"id": "work", "description": "Do work", "execute": work}, DONE]

            runner = DecisionsToolRunner(observe=observe, candidates=candidates)
            result = runner.run(client, PARAMS, cancelled=stopped)
            assert runner.close() == {"status": "closed"}
            with pytest.raises(RuntimeError, match="closed"):
                runner.run(client, PARAMS)
    else:
        async with AsyncOpenAI(
            api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as client_async:

            async def observe_async() -> DecisionObservation:
                if not done:
                    with pytest.raises(RuntimeError, match="busy"):
                        await runner_async.run(client_async, PARAMS)
                    assert runner_async.close() == {"status": "draining"}
                    with pytest.raises(RuntimeError, match="closed"):
                        await runner_async.run(client_async, PARAMS)
                return "state"

            async def awork(*, cancelled: Callable[[], bool] | None = None) -> None:
                work(cancelled=cancelled)

            async def candidates_async(_obs: DecisionObservation) -> list[AsyncDecisionCandidate]:
                finish: AsyncDecisionCandidate = {"id": "finish", "description": "Task is complete", "done": True}
                return [finish] if done else [{"id": "work", "description": "Do work", "execute": awork}, finish]

            runner_async = AsyncDecisionsToolRunner(observe=observe_async, candidates=candidates_async)
            result = await runner_async.run(client_async, PARAMS, cancelled=stopped)
            assert runner_async.close() == {"status": "closed"}
            with pytest.raises(RuntimeError, match="closed"):
                await runner_async.run(client_async, PARAMS)
    assert result["status"] == "unverified"
    assert result["attempted_candidate_ids"] == result["completed_candidate_ids"] == ["work"]
    assert calls == ["work"] and len(requests) == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("selected", ["act", "finish"])
async def test_decisions_final_diagnostic_reports_step_limit(lane: str, selected: str) -> None:
    events: list[ToolDiagnostic] = []
    effects: list[str] = []
    with pytest.raises(DecisionsToolRunnerError) as exc:
        await run(
            lane,
            [decision(selected)],
            [],
            observe=lambda: "Synthetic fixture",
            candidates=lambda _: [
                {"id": "act", "description": "Make change", "execute": lambda: effects.append("act")},
                DONE,
            ],
            verify=lambda _: False,
            max_steps=1,
            on_diagnostic=events.append,
        )
    assert exc.value.reason == "step_limit" and effects == []
    assert (events[-1]["api"], events[-1]["stage"], events[-1]["reason"]) == ("decisions", "run", "step_limit")
    assert "Synthetic fixture" not in json.dumps(events)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("level", ["answer", "answers"])
async def test_decisions_do_not_select_fields_supplied_only_by_subclass_defaults(
    lane: str, level: str, monkeypatch: pytest.MonkeyPatch
) -> None:

    from openai.types import Decision
    from openai.types.decision import Answer, AnswerAnswerResourceChoice

    class Defaults(AnswerAnswerResourceChoice):
        name: str | None = "next_action"
        choice: StrictStr | StrictBool = "act"
        type: Literal["choice"] = "choice"

    effects: list[str] = []
    if level == "answer":
        result = Decision(**cast(dict[str, Any], decision("finish")))
        result.answers = [Defaults(confidence=1, probabilities=[])]
    else:

        class DecisionDefaults(Decision):
            answers: list[Answer] = [
                AnswerAnswerResourceChoice(
                    name="next_action", choice="act", type="choice", confidence=1, probabilities=[]
                )
            ]

        payload = decision("finish")
        del payload["answers"]
        result = DecisionDefaults(**cast(dict[str, Any], payload))

    class DecisionsClient:
        def create(self, **_params: object) -> Decision:
            return result

    class AsyncDecisionsClient:
        async def create(self, **_params: object) -> Decision:
            return result

    if lane == "sync":
        with OpenAI(api_key="fake", http_client=httpx2.Client(trust_env=False)) as client:
            monkeypatch.setattr(client, "decisions", DecisionsClient())
            runner = DecisionsToolRunner(
                observe=lambda: "fixture",
                candidates=lambda _: [
                    {"id": "act", "description": "Act", "execute": lambda: effects.append("act")},
                    DONE,
                ],
            )
            with pytest.raises(DecisionsToolRunnerError) as exc:
                runner.run(client, PARAMS, max_steps=2)
    else:

        async def observe() -> str:
            return "fixture"

        async def candidates(_observation: DecisionObservation) -> list[AsyncDecisionCandidate]:
            async def act() -> None:
                effects.append("act")

            return [{"id": "act", "description": "Act", "execute": act}, cast(AsyncDecisionCandidate, DONE)]

        async with AsyncOpenAI(api_key="fake", http_client=httpx2.AsyncClient(trust_env=False)) as async_client:
            monkeypatch.setattr(async_client, "decisions", AsyncDecisionsClient())
            async_runner = AsyncDecisionsToolRunner(observe=observe, candidates=candidates)
            with pytest.raises(DecisionsToolRunnerError) as exc:
                await async_runner.run(async_client, PARAMS, max_steps=2)
    assert exc.value.reason == "invalid_answer"
    assert effects == []
