"""Select caller-defined actions with Decisions; do not treat a choice as permission."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from math import isfinite
from time import monotonic
from typing import Callable, Iterable, Awaitable, cast
from inspect import isawaitable, iscoroutine
from dataclasses import dataclass
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .. import OpenAI, AsyncOpenAI
from ..types import Decision
from .._compat import model_copy
from ..types.decision import Usage, Answer, UsageInputTokensDetails, UsageOutputTokensDetails
from ._tool_lifecycle import CloseStatus, ToolLifecycle, invoke, rotated_idempotency_headers
from .tool_diagnostics import ToolDiagnosticObserver, emit_tool_diagnostic
from ..types.decision_create_params import DecisionCreateParams
from ..types.decision_input_part_union_param import DecisionInputPartUnionParam

__all__ = [
    "DecisionObservation",
    "DecisionCandidate",
    "AsyncDecisionCandidate",
    "DecisionActionCandidate",
    "AsyncDecisionActionCandidate",
    "DecisionDoneCandidate",
    "DecisionsRunnerParams",
    "DecisionsRunResult",
    "DecisionsToolRunner",
    "AsyncDecisionsToolRunner",
    "DecisionsToolRunnerError",
    "DecisionsToolRunnerCancelledError",
]

DecisionObservation: TypeAlias = str | Iterable[DecisionInputPartUnionParam]
_OwnedObservation: TypeAlias = str | list[DecisionInputPartUnionParam]


class DecisionActionCandidate(TypedDict, total=False):
    id: Required[str]
    description: Required[str]
    execute: Required[Callable[[], object]]
    done: Literal[False]


class AsyncDecisionActionCandidate(TypedDict, total=False):
    id: Required[str]
    description: Required[str]
    execute: Required[Callable[[], Awaitable[object]]]
    done: Literal[False]


class DecisionDoneCandidate(TypedDict):
    id: str
    description: str
    done: Literal[True]


DecisionCandidate: TypeAlias = DecisionActionCandidate | DecisionDoneCandidate
AsyncDecisionCandidate: TypeAlias = AsyncDecisionActionCandidate | DecisionDoneCandidate


class DecisionsRunnerParams(TypedDict, total=False):
    model: Required[str]
    input: Required[str]
    safety_identifier: str | None


class DecisionsRunResult(TypedDict):
    status: Literal["verified", "unverified", "refused"]
    decisions: list[Decision]
    attempted_candidate_ids: list[str]
    completed_candidate_ids: list[str]


_Reason: TypeAlias = Literal[
    "invalid_params",
    "invalid_candidates",
    "invalid_answer",
    "async_executor",
    "invalid_verification",
    "verification_failed",
    "step_limit",
    "failed",
    "cancelled",
]
_MESSAGES: dict[_Reason, str] = {
    "invalid_params": "Decisions requires a task, model and supported run options.",
    "invalid_candidates": "Candidates must have unique IDs, descriptions, one done choice and valid executors.",
    "invalid_answer": "Decision did not select a registered candidate.",
    "async_executor": "A synchronous executor returned an awaitable; use AsyncDecisionsToolRunner.",
    "invalid_verification": "Verification must return True or False.",
    "verification_failed": "Verification failed with no available action.",
    "step_limit": "Decision run reached max_steps before completion.",
    "failed": "Decision run stopped before completion.",
    "cancelled": "Decision run was cancelled.",
}


class DecisionsToolRunnerError(RuntimeError):
    """Inspect attempted IDs before retrying. Completed IDs mean the executor returned."""

    def __init__(self, reason: _Reason, attempted: list[str], completed: list[str]) -> None:
        super().__init__(_MESSAGES[reason])
        self.reason = reason
        self.attempted_candidate_ids = tuple(attempted)
        self.completed_candidate_ids = tuple(completed)


class DecisionsToolRunnerCancelledError(asyncio.CancelledError):
    """Task cancellation with execution evidence and no callback or API error text."""

    def __init__(self, attempted: list[str], completed: list[str]) -> None:
        super().__init__(_MESSAGES["cancelled"])
        self.reason: Literal["cancelled"] = "cancelled"
        self.attempted_candidate_ids = tuple(attempted)
        self.completed_candidate_ids = tuple(completed)


@dataclass(frozen=True)
class _Candidate:
    id: str
    description: str
    done: bool
    execute: Callable[[], object] | None


class _Run:
    def __init__(self, params: DecisionsRunnerParams, max_steps: int, cancelled: Callable[[], bool] | None) -> None:
        self.attempted: list[str] = []
        self.completed: list[str] = []
        self.decisions: list[Decision] = []
        self.last_error: DecisionsToolRunnerError | None = None
        self.cancelled = cancelled
        if (
            type(max_steps) is not int
            or max_steps < 1
            or set(params) - {"model", "input", "safety_identifier"}
            or not isinstance(cast(object, params.get("model")), str)
            or not isinstance(cast(object, params.get("input")), str)
            or (params.get("safety_identifier") is not None and not isinstance(params.get("safety_identifier"), str))
        ):
            raise self.error("invalid_params")
        self.params = params.copy()

    def error(self, reason: _Reason) -> DecisionsToolRunnerError:
        self.last_error = DecisionsToolRunnerError(reason, self.attempted, self.completed)
        return self.last_error

    def check(self) -> None:
        if self.cancelled is not None and self.cancelled():
            raise self.error("cancelled")

    def own(self, observation: DecisionObservation) -> _OwnedObservation:
        # Materialize one-shot Iterables before copying or exposing them to callbacks.
        owned = observation if isinstance(observation, str) else deepcopy(list(observation))
        if not isinstance(owned, str):
            for supplied in owned:
                part = cast(object, supplied)
                if not isinstance(part, dict):
                    raise self.error("failed")
                fields = cast(dict[str, object], part)
                if fields.get("type") == "input_text":
                    if not isinstance(fields.get("text"), str):
                        raise self.error("failed")
                elif (
                    fields.get("type") != "input_image"
                    or not isinstance(fields.get("image_url"), str)
                    or fields.get("detail") not in (None, "low", "high", "auto", "original")
                ):
                    raise self.error("failed")
        self.check()
        return owned

    def candidates(self, values: list[DecisionCandidate] | list[AsyncDecisionCandidate]) -> list[_Candidate]:
        if not isinstance(cast(object, values), list):
            raise self.error("invalid_candidates")
        native = cast(list[object], values)
        length = list[object].__len__(native)
        if not 1 <= length <= 255:
            raise self.error("invalid_candidates")
        entries = [list[object].__getitem__(native, index) for index in range(length)]
        snapshot: list[_Candidate] = []
        ids: set[str] = set()
        for value in entries:
            if not isinstance(value, dict):
                raise self.error("invalid_candidates")
            fields = cast(dict[str, object], value)
            keys = dict[str, object].keys(fields)
            if keys - {"id", "description", "done", "execute"}:
                raise self.error("invalid_candidates")
            candidate_id = dict[str, object].get(fields, "id")
            description = dict[str, object].get(fields, "description")
            done = dict[str, object].get(fields, "done", False)
            execute = dict[str, object].get(fields, "execute")
            if (
                not isinstance(candidate_id, str)
                or not candidate_id.strip()
                or candidate_id in ids
                or not isinstance(description, str)
                or not description.strip()
                or type(done) is not bool
                or (done and "execute" in keys)
                or (not done and not callable(execute))
            ):
                raise self.error("invalid_candidates")
            ids.add(candidate_id)
            snapshot.append(
                _Candidate(candidate_id, description, done, None if done else cast(Callable[[], object], execute))
            )
        if sum(item.done for item in snapshot) != 1:
            raise self.error("invalid_candidates")
        self.check()
        return snapshot

    def request(self, observation: _OwnedObservation, candidates: list[_Candidate]) -> DecisionCreateParams:
        params: DecisionCreateParams = {
            "model": self.params["model"],
            "input": [{"role": "user", "content": self.params["input"]}, {"role": "user", "content": observation}],
            "questions": [
                {
                    "type": "choice",
                    "name": "next_action",
                    "instructions": "Select the supplied action that best advances the task, or done if the task is complete.",
                    "choices": [{"value": item.id, "description": item.description} for item in candidates],
                }
            ],
        }
        if "safety_identifier" in self.params:
            params["safety_identifier"] = self.params["safety_identifier"]
        return params

    def select(self, decision: Decision, candidates: list[_Candidate]) -> tuple[_Candidate | None, Usage]:
        self.check()
        if "answers" not in decision.model_fields_set:
            raise self.error("invalid_answer")
        answers = cast(object, decision.answers)
        if not isinstance(answers, list) or len(cast(list[object], answers)) != 1:
            raise self.error("invalid_answer")
        answer = cast(list[Answer], answers)[0]
        if not {"name", "type"} <= answer.model_fields_set:
            raise self.error("invalid_answer")
        name, kind = answer.name, answer.type
        if name != "next_action":
            raise self.error("invalid_answer")
        answer = model_copy(answer, deep=True)
        snapshot = model_copy(decision, deep=True)
        usage = cast(object, snapshot.usage)
        if (
            not isinstance(cast(object, snapshot.model), str)
            or not isinstance(usage, Usage)
            or not isinstance(cast(object, usage.input_tokens_details), UsageInputTokensDetails)
            or not isinstance(cast(object, usage.output_tokens_details), UsageOutputTokensDetails)
            or not all(
                type(value) is int
                for value in (
                    usage.input_tokens,
                    usage.output_tokens,
                    usage.total_tokens,
                    usage.input_tokens_details.cache_write_tokens,
                    usage.input_tokens_details.cached_tokens,
                    usage.output_tokens_details.reasoning_tokens,
                )
            )
        ):
            raise self.error("invalid_answer")
        if not {"name", "type"} <= answer.model_fields_set or answer.name != name or answer.type != kind:
            raise self.error("invalid_answer")
        # Preserve the admitted answer even for native subclasses with metadata getters.
        snapshot.answers = [answer]
        self.decisions.append(snapshot)
        if answer.type == "refusal":
            return None, usage
        if (
            answer.type != "choice"
            or not {"choice", "confidence", "probabilities"} <= answer.model_fields_set
            or not isinstance(answer.choice, str)
            or isinstance(answer.confidence, bool)
            or not isinstance(cast(object, answer.confidence), (int, float))
            or not isfinite(answer.confidence)
            or not isinstance(cast(object, answer.probabilities), list)
        ):
            raise self.error("invalid_answer")
        for chance in answer.probabilities:
            if (
                not hasattr(chance, "model_fields_set")
                or not {"value", "probability"} <= chance.model_fields_set
                or not isinstance(cast(object, chance.value), (str, bool))
                or isinstance(chance.probability, bool)
                or not isinstance(cast(object, chance.probability), (int, float))
                or not isfinite(chance.probability)
            ):
                raise self.error("invalid_answer")
        for candidate in candidates:
            if candidate.id == answer.choice:
                return candidate, usage
        raise self.error("invalid_answer")

    def result(self, status: Literal["verified", "unverified", "refused"]) -> DecisionsRunResult:
        self.check()
        return {
            "status": status,
            "decisions": list(self.decisions),
            "attempted_candidate_ids": list(self.attempted),
            "completed_candidate_ids": list(self.completed),
        }

    def verified(self, verification: bool, *, only_done: bool, last_step: bool) -> bool:
        self.check()
        if verification is True:
            return True
        if verification is not False:
            raise self.error("invalid_verification")
        if only_done:
            raise self.error("verification_failed")
        if last_step:
            raise self.error("step_limit")
        return False


class DecisionsToolRunner:
    def __init__(
        self,
        *,
        observe: Callable[[], DecisionObservation],
        candidates: Callable[[DecisionObservation], list[DecisionCandidate]],
        verify: Callable[[DecisionObservation], bool] | None = None,
    ) -> None:
        self.observe = observe
        self.candidates = candidates
        self.verify = verify
        self._lifecycle = ToolLifecycle("Decisions runner")

    def close(self) -> CloseStatus:
        return self._lifecycle.close()

    def run(
        self,
        client: OpenAI,
        params: DecisionsRunnerParams,
        *,
        max_steps: int = 20,
        cancelled: Callable[[], bool] | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
    ) -> DecisionsRunResult:
        self._lifecycle.enter()
        try:
            run = _Run(params, max_steps, cancelled)
        except BaseException:
            self._lifecycle.exit()
            raise
        try:
            observe, candidate_provider, verify = self.observe, self.candidates, self.verify
            for step in range(max_steps):
                run.check()
                observation = run.own(observe())
                candidates = run.candidates(candidate_provider(deepcopy(observation)))
                only_done = len(candidates) == 1
                choice: _Candidate | None
                if only_done:
                    choice = candidates[0]
                else:
                    started = monotonic()
                    try:
                        decision = client.decisions.create(
                            **run.request(observation, candidates),
                            extra_headers=rotated_idempotency_headers(client, None) if step > 0 else None,
                        )
                    except Exception:
                        emit_tool_diagnostic(on_diagnostic, "decisions", "request", "api_failed", started)
                        raise
                    choice, usage = run.select(decision, candidates)
                    emit_tool_diagnostic(on_diagnostic, "decisions", "request", "completed", started, usage=usage)
                    run.check()
                emit_tool_diagnostic(
                    on_diagnostic,
                    "decisions",
                    "selection",
                    "refused" if choice is None else "completed",
                    monotonic(),
                    call_id=choice.id if choice is not None else None,
                )
                if choice is None:
                    return run.result("refused")
                if choice.done:
                    if verify is None:
                        return run.result("unverified")
                    run.check()
                    fresh = run.own(observe())
                    started = monotonic()
                    verification = verify(deepcopy(fresh))
                    emit_tool_diagnostic(
                        on_diagnostic,
                        "decisions",
                        "verification",
                        "completed" if verification is True else "refused",
                        started,
                        call_id=choice.id,
                    )
                    if run.verified(verification, only_done=only_done, last_step=step == max_steps - 1):
                        return run.result("verified")
                    continue
                if step == max_steps - 1:
                    raise run.error("step_limit")
                if choice.execute is None:
                    raise AssertionError("validated action is missing its executor")
                run.check()
                run.attempted.append(choice.id)
                started = monotonic()
                try:
                    result = invoke(choice.execute, cancelled=run.cancelled)
                    if isawaitable(result):
                        if iscoroutine(result):
                            result.close()
                        raise run.error("async_executor")
                except (Exception, asyncio.CancelledError):
                    emit_tool_diagnostic(
                        on_diagnostic, "decisions", "action", "driver_failed", started, call_id=choice.id
                    )
                    raise
                emit_tool_diagnostic(on_diagnostic, "decisions", "action", "completed", started, call_id=choice.id)
                run.completed.append(choice.id)
                run.check()
        except DecisionsToolRunnerError as exc:
            if exc is run.last_error:
                if exc.reason == "step_limit":
                    emit_tool_diagnostic(on_diagnostic, "decisions", "run", "step_limit", monotonic())
                raise
            raise run.error("failed") from None
        except asyncio.CancelledError:
            raise DecisionsToolRunnerCancelledError(run.attempted, run.completed) from None
        except Exception:
            raise run.error("failed") from None
        finally:
            self._lifecycle.exit()

        raise AssertionError("unreachable")


class AsyncDecisionsToolRunner:
    def __init__(
        self,
        *,
        observe: Callable[[], Awaitable[DecisionObservation]],
        candidates: Callable[[DecisionObservation], Awaitable[list[AsyncDecisionCandidate]]],
        verify: Callable[[DecisionObservation], Awaitable[bool]] | None = None,
    ) -> None:
        self.observe = observe
        self.candidates = candidates
        self.verify = verify
        self._lifecycle = ToolLifecycle("Decisions runner")

    def close(self) -> CloseStatus:
        return self._lifecycle.close()

    async def run(
        self,
        client: AsyncOpenAI,
        params: DecisionsRunnerParams,
        *,
        max_steps: int = 20,
        cancelled: Callable[[], bool] | None = None,
        on_diagnostic: ToolDiagnosticObserver | None = None,
    ) -> DecisionsRunResult:
        self._lifecycle.enter()
        try:
            run = _Run(params, max_steps, cancelled)
        except BaseException:
            self._lifecycle.exit()
            raise
        try:
            observe, candidate_provider, verify = self.observe, self.candidates, self.verify
            for step in range(max_steps):
                run.check()
                observation = run.own(await observe())
                candidates = run.candidates(await candidate_provider(deepcopy(observation)))
                only_done = len(candidates) == 1
                choice: _Candidate | None
                if only_done:
                    choice = candidates[0]
                else:
                    started = monotonic()
                    try:
                        decision = await client.decisions.create(
                            **run.request(observation, candidates),
                            extra_headers=rotated_idempotency_headers(client, None) if step > 0 else None,
                        )
                    except Exception:
                        emit_tool_diagnostic(on_diagnostic, "decisions", "request", "api_failed", started)
                        raise
                    choice, usage = run.select(decision, candidates)
                    emit_tool_diagnostic(on_diagnostic, "decisions", "request", "completed", started, usage=usage)
                    run.check()
                emit_tool_diagnostic(
                    on_diagnostic,
                    "decisions",
                    "selection",
                    "refused" if choice is None else "completed",
                    monotonic(),
                    call_id=choice.id if choice is not None else None,
                )
                if choice is None:
                    return run.result("refused")
                if choice.done:
                    if verify is None:
                        return run.result("unverified")
                    run.check()
                    fresh = run.own(await observe())
                    started = monotonic()
                    verification = await verify(deepcopy(fresh))
                    emit_tool_diagnostic(
                        on_diagnostic,
                        "decisions",
                        "verification",
                        "completed" if verification is True else "refused",
                        started,
                        call_id=choice.id,
                    )
                    if run.verified(verification, only_done=only_done, last_step=step == max_steps - 1):
                        return run.result("verified")
                    continue
                if step == max_steps - 1:
                    raise run.error("step_limit")
                if choice.execute is None:
                    raise AssertionError("validated action is missing its executor")
                run.check()
                run.attempted.append(choice.id)
                started = monotonic()
                try:
                    await cast(Awaitable[object], invoke(choice.execute, cancelled=run.cancelled))
                except (Exception, asyncio.CancelledError):
                    emit_tool_diagnostic(
                        on_diagnostic, "decisions", "action", "driver_failed", started, call_id=choice.id
                    )
                    raise
                emit_tool_diagnostic(on_diagnostic, "decisions", "action", "completed", started, call_id=choice.id)
                run.completed.append(choice.id)
                run.check()
        except DecisionsToolRunnerError as exc:
            if exc is run.last_error:
                if exc.reason == "step_limit":
                    emit_tool_diagnostic(on_diagnostic, "decisions", "run", "step_limit", monotonic())
                raise
            raise run.error("failed") from None
        except asyncio.CancelledError:
            raise DecisionsToolRunnerCancelledError(run.attempted, run.completed) from None
        except Exception:
            raise run.error("failed") from None
        finally:
            self._lifecycle.exit()

        raise AssertionError("unreachable")
