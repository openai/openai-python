from __future__ import annotations

import json
from typing import Any, Callable, cast
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib.browser import (
    ClickInput,
    BrowserError,
    WaitForInput,
    NavigateInput,
    BrowserToolset,
    AsyncBrowserToolset,
    BrowserCancelledError,
    BrowserConfirmContext,
)
from openai.types.responses import ResponseFunctionToolCall
from openai.lib.responses_tool_runner import (
    EarlyExecution,
    ToolRunnerError,
    ResponsesToolLedger,
    ResponsesToolRunner,
    ResponsesToolCheckpoint,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)
from openai.types.responses.response_input_param import FunctionCallOutput

from .test_browser import Desktop, AsyncDesktop, call, payload, reported_state
from .test_responses_tool_runner import FINAL, PARAMS, fn, sse, resp


class Navigation(Desktop):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[object] = []

    @override
    def navigate(self, action: NavigateInput) -> None:
        self.events.append(("navigate", action["url"]))

    def scroll_to(self, action: ClickInput) -> None:
        self.events.append(("scroll_to", action["target"]))

    def wait_for(self, action: WaitForInput, *, cancelled: Callable[[], bool] | None) -> str:
        self.events.append(("wait_for", action["text"]))
        if cancelled and cancelled():
            raise BrowserCancelledError("Browser execution was cancelled.")
        return "Visible condition met."


class AsyncNavigation(AsyncDesktop):
    def __init__(self, desktop: Navigation) -> None:
        super().__init__(desktop)
        self.navigation = desktop

    async def scroll_to(self, action: ClickInput) -> None:
        self.navigation.scroll_to(action)

    async def wait_for(self, action: WaitForInput, *, cancelled: Callable[[], bool] | None) -> str:
        return self.navigation.wait_for(action, cancelled=cancelled)


async def dispatch(
    browser: BrowserToolset | AsyncBrowserToolset,
    request: ResponseFunctionToolCall,
    cancelled: Callable[[], bool] | None = None,
) -> FunctionCallOutput:
    if isinstance(browser, AsyncBrowserToolset):
        return await browser.execute(request, cancelled=cancelled)
    return browser.execute(request, cancelled=cancelled)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("value", ["back", "forward", "reload", "https://allowed.example/"])
async def test_history_argument_uses_raw_policy_and_strict_confirmation(lane: str, value: str) -> None:
    driver = Navigation()

    def policy(ctx: BrowserConfirmContext, url: str) -> bool:
        driver.events.append(("policy", url))
        ctx["arguments"]["url"] = "file:///elsewhere"
        return True

    def confirm(ctx: BrowserConfirmContext) -> bool:
        driver.events.append(("confirm", ctx["arguments"]["url"]))
        ctx["arguments"]["url"] = "file:///elsewhere"
        return True

    async def async_policy(ctx: BrowserConfirmContext, url: str) -> bool:
        return policy(ctx, url)

    async def async_confirm(ctx: BrowserConfirmContext) -> bool:
        return confirm(ctx)

    browser = (
        BrowserToolset(driver, members=["navigate"], confirm=confirm, url_policy=policy)
        if lane == "sync"
        else AsyncBrowserToolset(
            AsyncNavigation(driver), members=["navigate"], confirm=async_confirm, url_policy=async_policy
        )
    )
    request = call("navigate", {"url": value, "tab_id": None})
    result = await dispatch(browser, request)
    assert result.get("call_id") == request.call_id and payload(result)["ok"] is True
    assert driver.events == [("policy", value), ("confirm", value), ("navigate", value)]
    driver.events.clear()
    browser.url_policy = None
    assert payload(await dispatch(browser, request))["ok"] is False
    assert driver.events == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "args",
    [
        {"text": "", "timeout_ms": 10, "tab_id": None},
        {"text": " \n\t", "timeout_ms": 10, "tab_id": None},
        {"text": "\ud800", "timeout_ms": 10, "tab_id": None},
        {"text": "🦉" * 65, "timeout_ms": 10, "tab_id": None},
        *({"text": "ready", "timeout_ms": ms, "tab_id": None} for ms in (False, 0, -1, 1.1, 30001, 2**53)),
        {"text": "ready", "timeout_ms": 1},
        {"text": "ready", "timeout_ms": 1, "tab_id": None, "selector": "*"},
    ],
)
async def test_wait_rejects_invalid_native_arguments_before_driver(lane: str, args: dict[str, object]) -> None:
    driver = Navigation()
    browser = (
        BrowserToolset(driver, members=["wait_for"])
        if lane == "sync"
        else AsyncBrowserToolset(AsyncNavigation(driver), members=["wait_for"])
    )
    result = payload(await dispatch(browser, call("wait_for", args)))
    assert result["ok"] is False and result["state"] == reported_state() and driver.events == []


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_wait_touches_no_irrelevant_policy_and_passes_same_predicate(
    lane: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = Navigation()
    browser = (
        BrowserToolset(driver, members=["wait_for"])
        if lane == "sync"
        else AsyncBrowserToolset(AsyncNavigation(driver), members=["wait_for"])
    )

    def excluded(_self: object) -> None:
        pytest.fail("wait must not read irrelevant policy")

    monkeypatch.setattr(type(browser), "confirm", property(excluded), raising=False)
    monkeypatch.setattr(type(browser), "url_policy", property(excluded), raising=False)
    request = call("wait_for", {"text": "  " + "🦉" * 64 + "\n", "timeout_ms": 30000, "tab_id": None})
    assert payload(await dispatch(browser, request))["result"] == "Visible condition met."
    driver.events.clear()

    def cancelled_in_wait() -> bool:
        return bool(driver.events)

    with pytest.raises(BrowserCancelledError):
        await dispatch(browser, request, cancelled_in_wait)
    assert driver.events == [("wait_for", "  " + "🦉" * 64 + "\n")]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_scroll_to_needs_confirmation_and_disabled_methods_stay_unread(
    lane: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = Navigation()
    selected = ["scroll_to"]
    with pytest.raises(ValueError, match="confirm"):
        if lane == "sync":
            BrowserToolset(driver, members=selected)
        else:
            AsyncBrowserToolset(AsyncNavigation(driver), members=selected)

    async def confirm(_ctx: BrowserConfirmContext) -> bool:
        return False

    browser = (
        BrowserToolset(driver, members=selected, confirm=lambda _ctx: False)
        if lane == "sync"
        else AsyncBrowserToolset(AsyncNavigation(driver), members=selected, confirm=confirm)
    )
    selected[:] = ["wait_for"]
    assert payload(await dispatch(browser, call("scroll_to", {"target": "observed", "tab_id": None})))["ok"] is False
    assert driver.events == []

    def excluded(_self: object) -> None:
        pytest.fail("disabled member or policy was accessed")

    monkeypatch.setattr(type(browser.driver), "wait_for", property(excluded))
    with pytest.raises(BrowserError, match="disabled"):
        await dispatch(browser, call("wait_for", {"text": "ready", "timeout_ms": 1, "tab_id": None}))
    assert driver.events == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("early,last", [(None, False), ({"functions": ["browser_wait_for"]}, False), (None, True)])
async def test_navigation_wait_sse_replay_order_and_last_request(
    lane: str, early: EarlyExecution | None, last: bool
) -> None:
    driver = Navigation()
    requests: list[dict[str, Any]] = []
    records: list[ResponsesToolCheckpoint] = []
    first = resp(
        [
            fn("browser_wait_for", "wait1", text="ready", timeout_ms=30, tab_id=None),
            fn("browser_scroll_to", "scroll1", target="observed", tab_id=None),
        ],
        "step1",
    )

    def transport(request: httpx2.Request) -> httpx2.Response:
        requests.append(cast(dict[str, Any], json.loads(request.content)))
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, content=sse(first if len(requests) == 1 else FINAL)
        )

    def approve(ctx: BrowserConfirmContext) -> bool:
        driver.events.append(("confirm", ctx["member"]))
        return True

    async def async_approve(ctx: BrowserConfirmContext) -> bool:
        return approve(ctx)

    async def save(record: ResponsesToolCheckpoint) -> None:
        records.append(record)

    try:
        if lane == "sync":
            browser = BrowserToolset(driver, members=["wait_for", "scroll_to"], confirm=approve)
            runner = ResponsesToolRunner(browser=browser, early_execution=early)
            with OpenAI(
                api_key="fake",
                base_url="http://fixture.invalid/v1",
                http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
            ) as client:
                result = runner.run(
                    client,
                    PARAMS,
                    stream=True,
                    eager=early is not None,
                    max_steps=1 if last else 3,
                    ledger=ResponsesToolLedger("fixture-run", records.append),
                )
        else:
            browser_async = AsyncBrowserToolset(
                AsyncNavigation(driver), members=["wait_for", "scroll_to"], confirm=async_approve
            )
            async_runner = AsyncResponsesToolRunner(browser=browser_async, early_execution=early)
            async with AsyncOpenAI(
                api_key="fake",
                base_url="http://fixture.invalid/v1",
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
            ) as client_async:
                result = await async_runner.run(
                    client_async,
                    PARAMS,
                    stream=True,
                    eager=early is not None,
                    max_steps=1 if last else 3,
                    ledger=AsyncResponsesToolLedger("fixture-run", save),
                )
    except ToolRunnerError as error:
        assert last and error.attempted_call_ids == ()
        assert len(requests) == 1 and not driver.events and records[-1]["phase"] == "boundary"
        return
    assert not last and result.id == "resp_final" and len(requests) == 2
    assert driver.events == [("wait_for", "ready"), ("confirm", "scroll_to"), ("scroll_to", "observed")]
    outputs = [item for item in requests[1]["input"] if item.get("type") == "function_call_output"]
    assert [item["call_id"] for item in outputs] == ["wait1", "scroll1"]
    assert json.loads(outputs[0]["output"][0]["text"])["result"] == "Visible condition met."
    assert records[-1]["attempted_call_ids"] == records[-1]["returned_call_ids"] == ["wait1", "scroll1"]
