from __future__ import annotations

from copy import deepcopy
from typing import Any, cast

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, omit
from openai.lib.decisions_tool_runner import DecisionsToolRunner, AsyncDecisionCandidate, AsyncDecisionsToolRunner
from openai.lib.responses_tool_runner import (
    RegisteredFunction,
    ResponsesToolLedger,
    ResponsesToolRunner,
    AsyncRegisteredFunction,
    ResponsesToolCheckpoint,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)

from .test_decisions_tool_runner import DONE, PARAMS as DECISION_PARAMS, decision
from .test_responses_tool_runner import TOOL, FINAL, PARAMS, fn, resp


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "api,source",
    [("responses", value) for value in ("default", "request", "remove", "none")]
    + [("decisions", "default"), ("decisions", "none")],
)
async def test_runner_rotates_keys_between_turns_not_retries(lane: str, api: str, source: str) -> None:
    sent: list[httpx2.Headers] = []
    actions: list[str] = []

    def transport(request: httpx2.Request) -> httpx2.Response:
        sent.append(request.headers)
        if len(sent) in (1, 3):
            return httpx2.Response(
                500, json={"error": {"message": "retry this request"}}, headers={"retry-after-ms": "0"}
            )
        if api == "decisions":
            return httpx2.Response(200, json=decision("finish" if actions else "act"))
        return httpx2.Response(200, json=FINAL if actions else resp([fn("record", "one", text="act")], "first"))

    def act() -> str:
        actions.append("act")
        return "done"

    def execute(_args: dict[str, object]) -> str:
        return act()

    async def execute_async(_args: dict[str, object]) -> str:
        return act()

    async def act_async() -> str:
        return act()

    async def observe_async() -> str:
        return ",".join(actions)

    async def candidates_async(_observation: object) -> list[AsyncDecisionCandidate]:
        return [
            {"id": "finish", "description": "Done", "done": True},
            {"id": "act", "description": "Act", "execute": act_async},
        ]

    defaults = {"x-kept": "yes", **({} if source == "none" else {"Idempotency-Key": "client-first"})}
    params = PARAMS.copy()
    if source == "request":
        cast(dict[str, Any], params)["extra_headers"] = {"idempotency-key": "request-first"}
    elif source == "remove":
        cast(dict[str, Any], params)["extra_headers"] = {"idempotency-key": omit}

    if lane == "sync":
        with OpenAI(
            api_key="synthetic-test-key",
            max_retries=1,
            default_headers=defaults,
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:
            if api == "responses":
                ResponsesToolRunner(functions=[RegisteredFunction(tool=TOOL, execute=execute)]).run(client, params)
            else:
                DecisionsToolRunner(
                    observe=lambda: ",".join(actions),
                    candidates=lambda _: [DONE, {"id": "act", "description": "Act", "execute": act}],
                ).run(client, DECISION_PARAMS)
    else:
        async with AsyncOpenAI(
            api_key="synthetic-test-key",
            max_retries=1,
            default_headers=defaults,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
        ) as async_client:
            if api == "responses":
                await AsyncResponsesToolRunner(
                    functions=[AsyncRegisteredFunction(tool=TOOL, execute=execute_async)]
                ).run(async_client, params)
            else:
                await AsyncDecisionsToolRunner(observe=observe_async, candidates=candidates_async).run(
                    async_client, DECISION_PARAMS
                )
    assert actions == ["act"]
    assert len(sent) == 4
    keys = [headers.get("idempotency-key") for headers in sent]
    if source in ("none", "remove"):
        assert keys == [None, None, None, None]
    else:
        first = "request-first" if source == "request" else "client-first"
        assert keys[:2] == [first, first]
        assert keys[2] and keys[2] != first
        assert keys[3] == keys[2]
    assert [headers.get("x-kept") for headers in sent] == ["yes", "yes", "yes", "yes"]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_responses_ledger_resume_rotates_default_key_and_preserves_inputs(lane: str) -> None:
    sent: list[httpx2.Headers] = []
    checkpoints: list[ResponsesToolCheckpoint] = []
    resumed: list[ResponsesToolCheckpoint] = []
    actions: list[str] = []
    defaults = {"Idempotency-Key": "initial-request", "x-kept": "default", "x-run": "run"}
    params = PARAMS.copy()

    def transport(request: httpx2.Request) -> httpx2.Response:
        sent.append(request.headers)
        return httpx2.Response(200, json=resp([fn("record", "one", text="act")], "first") if len(sent) == 1 else FINAL)

    def execute(_args: dict[str, object]) -> str:
        actions.append("act")
        return "done"

    async def execute_async(args: dict[str, object]) -> str:
        return execute(args)

    async def save(checkpoint: ResponsesToolCheckpoint) -> None:
        checkpoints.append(deepcopy(checkpoint))

    async def save_resumed(checkpoint: ResponsesToolCheckpoint) -> None:
        resumed.append(checkpoint)

    if lane == "sync":
        with OpenAI(
            api_key="synthetic-test-key",
            default_headers=defaults,
            http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
        ) as client:
            runner = ResponsesToolRunner(functions=[RegisteredFunction(tool=TOOL, execute=execute)])
            runner.run(
                client,
                params,
                ledger=ResponsesToolLedger("resume-key", lambda checkpoint: checkpoints.append(deepcopy(checkpoint))),
            )
            boundary = next(
                checkpoint
                for checkpoint in checkpoints
                if checkpoint["phase"] == "boundary"
                and checkpoint["consumed_requests"] > 0
                and "one" in checkpoint["returned_call_ids"]
            )
            before = deepcopy((boundary, defaults, params))
            runner.run(client, params, ledger=ResponsesToolLedger("resume-key", resumed.append, boundary))
    else:
        async with AsyncOpenAI(
            api_key="synthetic-test-key",
            default_headers=defaults,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
        ) as async_client:
            async_runner = AsyncResponsesToolRunner(
                functions=[AsyncRegisteredFunction(tool=TOOL, execute=execute_async)]
            )
            await async_runner.run(async_client, params, ledger=AsyncResponsesToolLedger("resume-key", save))
            boundary = next(
                checkpoint
                for checkpoint in checkpoints
                if checkpoint["phase"] == "boundary"
                and checkpoint["consumed_requests"] > 0
                and "one" in checkpoint["returned_call_ids"]
            )
            before = deepcopy((boundary, defaults, params))
            await async_runner.run(
                async_client, params, ledger=AsyncResponsesToolLedger("resume-key", save_resumed, boundary)
            )
    assert len(sent) == 3
    assert sent[0].get("idempotency-key") == "initial-request"
    assert sent[2].get("idempotency-key") and sent[2].get("idempotency-key") != "initial-request"
    assert sent[2].get("x-kept") == "default"
    assert sent[2].get("x-run") == "run"
    assert actions == ["act"]
    assert any(checkpoint["phase"] == "final" for checkpoint in resumed)
    assert (boundary, defaults, params) == before
