from __future__ import annotations

import json
import asyncio
from types import SimpleNamespace
from typing import Callable, cast

import pytest

from openai._models import construct_type_unchecked
from openai.lib.browser import (
    BrowserState,
    BrowserDriver,
    BrowserToolset,
    AsyncBrowserDriver,
    AsyncBrowserToolset,
    BrowserCancelledError,
    BrowserConfirmContext,
    BrowserReadConfirmContext,
)
from openai.types.responses import ResponseFunctionToolCall
from openai.lib.tool_diagnostics import ToolDiagnostic


def call(member: str, **args: object) -> ResponseFunctionToolCall:
    return construct_type_unchecked(
        type_=ResponseFunctionToolCall,
        value={
            "type": "function_call",
            "call_id": "real-id",
            "status": "completed",
            "name": "browser_" + member,
            "arguments": json.dumps(args),
        },
    )


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("stage", ["confirm", "read", "url", "throwing_read"])
async def test_browser_approval_cooperative_cancellation(lane: str, stage: str) -> None:
    effects: list[str] = []
    diagnostics: list[ToolDiagnostic] = []
    seen: list[Callable[[], bool] | None] = []
    stopped = False

    def probe() -> bool:
        return stopped

    def state() -> BrowserState:
        effects.append("state")
        return {"tabs": [{"id": "t", "title": "Fixture", "url": "https://fixture.invalid/", "active": True}]}

    async def astate() -> BrowserState:
        return state()

    def effect(_arguments: object) -> str:
        effects.append("driver")
        return "page"

    async def aeffect(arguments: object) -> str:
        return effect(arguments)

    def confirm(
        _ctx: BrowserConfirmContext | BrowserReadConfirmContext, *, cancelled: Callable[[], bool] | None = None
    ) -> bool:
        nonlocal stopped
        if stage != "url":
            seen.append(cancelled)
            stopped = cancelled is probe
        if stage == "throwing_read":
            raise RuntimeError("private confirmation details")
        return True

    async def aconfirm(
        ctx: BrowserConfirmContext | BrowserReadConfirmContext, *, cancelled: Callable[[], bool] | None = None
    ) -> bool:
        return confirm(ctx, cancelled=cancelled)

    def url_policy(_ctx: BrowserConfirmContext, _url: str, *, cancelled: Callable[[], bool] | None = None) -> bool:
        nonlocal stopped
        if stage == "url":
            seen.append(cancelled)
            stopped = cancelled is probe
        return True

    async def aurl_policy(ctx: BrowserConfirmContext, url: str, *, cancelled: Callable[[], bool] | None = None) -> bool:
        return url_policy(ctx, url, cancelled=cancelled)

    reading = stage in ("read", "throwing_read")
    driver = SimpleNamespace(
        state=state if lane == "sync" else astate,
        navigate=effect if lane == "sync" else aeffect,
        get_page_text=effect if lane == "sync" else aeffect,
    )
    request = (
        call("get_page_text", tab_id="t")
        if reading
        else call("navigate", tab_id="t", url="https://fixture.invalid/next")
    )
    with pytest.raises(BrowserCancelledError):
        if lane == "sync":
            BrowserToolset(
                cast(BrowserDriver, driver),
                members=["navigate", "get_page_text"],
                confirm_reads=["get_page_text"] if reading else [],
                confirm=confirm,
                url_policy=url_policy,
            ).execute(request, cancelled=probe, on_diagnostic=diagnostics.append)
        else:
            await AsyncBrowserToolset(
                cast(AsyncBrowserDriver, driver),
                members=["navigate", "get_page_text"],
                confirm_reads=["get_page_text"] if reading else [],
                confirm=aconfirm,
                url_policy=aurl_policy,
            ).execute(request, cancelled=probe, on_diagnostic=diagnostics.append)
    assert seen == [probe]
    assert effects == ([] if reading else ["state"])
    if reading:
        assert [(entry["stage"], entry["reason"]) for entry in diagnostics] == [("approval", "cancelled")]


async def test_held_browser_confirmation_keeps_ownership_through_abort() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()
    stopped = False
    effects: list[str] = []

    async def state() -> BrowserState:
        effects.append("state")
        return {"tabs": [{"id": "t", "title": "Fixture", "url": "https://fixture.invalid/", "active": True}]}

    async def read(_args: object) -> str:
        effects.append("read")
        return "private"

    async def confirm(_ctx: BrowserConfirmContext | BrowserReadConfirmContext) -> bool:
        entered.set()
        await release.wait()
        return True

    browser = AsyncBrowserToolset(
        cast(AsyncBrowserDriver, SimpleNamespace(state=state, get_page_text=read)),
        confirm_reads=["get_page_text"],
        confirm=confirm,
    )
    request = call("get_page_text", tab_id=None)
    task = asyncio.create_task(browser.execute(request, cancelled=lambda: stopped))
    await entered.wait()
    stopped = True
    with pytest.raises(RuntimeError, match="busy"):
        await browser.execute(request)
    assert browser.close() == {"status": "draining"}
    release.set()
    with pytest.raises(BrowserCancelledError):
        await task
    assert browser.close() == {"status": "closed"}
    assert effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", ["list_tabs", "get_page_text", "screenshot"])
async def test_sensitive_read_approval_precedes_any_state_and_preserves_original_args(lane: str, member: str) -> None:
    calls: list[str] = []
    contexts: list[BrowserConfirmContext | BrowserReadConfirmContext] = []

    def state() -> BrowserState:
        calls.append("state")
        return {
            "tabs": [{"id": "t", "title": "sentinel-private-title", "url": "https://private.invalid", "active": True}]
        }

    async def astate() -> BrowserState:
        return state()

    def read(_args: object) -> str:
        calls.append("read")
        return "sentinel-secret-read"

    async def aread(_args: object) -> str:
        return read(_args)

    def confirm(ctx: BrowserConfirmContext | BrowserReadConfirmContext) -> bool:
        contexts.append(ctx.copy())
        ctx["arguments"].clear()
        return False

    async def aconfirm(ctx: BrowserConfirmContext | BrowserReadConfirmContext) -> bool:
        return confirm(ctx)

    driver = SimpleNamespace(state=state if lane == "sync" else astate)
    if member != "list_tabs":
        setattr(driver, member, read if lane == "sync" else aread)
    request = call(member, **({} if member == "list_tabs" else {"tab_id": "t"}))
    if lane == "sync":
        browser = BrowserToolset(cast(BrowserDriver, driver), members=[member], confirm_reads=[member], confirm=confirm)
        output = browser.execute(request)
    else:
        browser_async = AsyncBrowserToolset(
            cast(AsyncBrowserDriver, driver), members=[member], confirm_reads=[member], confirm=aconfirm
        )
        output = await browser_async.execute(request)
    assert calls == []
    assert contexts[0]["state"] is None
    assert contexts[0]["call_id"] == "real-id"
    assert "sentinel" not in json.dumps(output)
    assert "private.invalid" not in json.dumps(output)
    assert "not approved" in json.dumps(output)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("skip", [False, True])
@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "browser_unknown"),
        ("name", "other_tool"),
        ("name", "browser_get_page_text"),
        ("type", "message"),
        ("status", "in_progress"),
        ("status", "incomplete"),
    ],
)
async def test_invalid_browser_call_never_reads_state(
    lane: str, skip: bool, field: str, value: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    effects: list[str] = []
    diagnostics: list[ToolDiagnostic] = []

    def state() -> BrowserState:
        effects.append("state")
        return {
            "tabs": [{"id": "t", "title": "sentinel-private-title", "url": "https://private.invalid", "active": True}]
        }

    async def astate() -> BrowserState:
        return state()

    def confirm(_ctx: BrowserConfirmContext | BrowserReadConfirmContext) -> bool:
        effects.append("confirm")
        return False

    async def aconfirm(ctx: BrowserConfirmContext | BrowserReadConfirmContext) -> bool:
        return confirm(ctx)

    class Driver(SimpleNamespace):
        pass

    driver = Driver(state=state if lane == "sync" else astate)
    request = call("list_tabs")
    setattr(request, field, value)
    browser: BrowserToolset | AsyncBrowserToolset
    if lane == "sync":
        browser = BrowserToolset(cast(BrowserDriver, driver), confirm_reads=["list_tabs"], confirm=confirm)
    else:
        browser = AsyncBrowserToolset(cast(AsyncBrowserDriver, driver), confirm_reads=["list_tabs"], confirm=aconfirm)

    # Even looking up the state property may expose caller-owned browser state.
    def state_property(_self: object) -> object:
        effects.append("state_lookup")
        return state if lane == "sync" else astate

    monkeypatch.setattr(Driver, "state", property(state_property), raising=False)
    if isinstance(browser, BrowserToolset):
        output, ok = browser._execute(request, skip=skip, on_diagnostic=diagnostics.append)
    else:
        output, ok = await browser._execute(request, skip=skip, on_diagnostic=diagnostics.append)

    assert effects == []
    assert ok is False
    assert output.get("call_id") == "real-id"
    content = output["output"]
    assert isinstance(content, list) and len(content) == 1 and content[0]["type"] == "input_text"
    assert json.loads(content[0]["text"]) == {"ok": False, "error": "Browser tool is unavailable or incomplete."}
    assert [(entry["stage"], entry["reason"]) for entry in diagnostics] == [("arguments", "invalid_input")]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_pointer_and_checkbox_are_explicit_and_close_is_reentrant_without_closing_driver(lane: str) -> None:
    checked = False
    touched: list[str] = []
    browser: BrowserToolset | AsyncBrowserToolset

    def state() -> BrowserState:
        return {"tabs": []}

    async def astate() -> BrowserState:
        return state()

    def set_checked(args: object) -> None:
        nonlocal checked
        checked = cast(dict[str, bool], args)["checked"]
        touched.append("check")

    async def aset_checked(args: object) -> None:
        set_checked(args)

    def hover(_args: object) -> None:
        touched.append("hover")
        assert browser.close() == {"status": "draining"}

    async def ahover(args: object) -> None:
        hover(args)

    def confirm(_ctx: BrowserConfirmContext) -> bool:
        return True

    async def aconfirm(_ctx: BrowserConfirmContext) -> bool:
        return confirm(_ctx)

    driver = SimpleNamespace(
        state=state if lane == "sync" else astate,
        set_checked=set_checked if lane == "sync" else aset_checked,
        hover_at=hover if lane == "sync" else ahover,
    )
    if lane == "sync":
        browser = BrowserToolset(cast(BrowserDriver, driver), confirm=confirm)
    else:
        browser = AsyncBrowserToolset(cast(AsyncBrowserDriver, driver), confirm=aconfirm)
    assert [item["name"] for item in browser.tools] == ["browser_list_tabs"]
    if lane == "sync":
        browser = BrowserToolset(
            cast(BrowserDriver, driver), additional_members=["set_checked", "hover_at"], confirm=confirm
        )
    else:
        browser = AsyncBrowserToolset(
            cast(AsyncBrowserDriver, driver), additional_members=["set_checked", "hover_at"], confirm=aconfirm
        )
    for _ in range(2):
        request = call("set_checked", tab_id=None, target="original-ref", checked=True)
        if isinstance(browser, BrowserToolset):
            browser.execute(request)
        else:
            await browser.execute(request)
    assert checked and touched == ["check", "check"]
    request = call("hover_at", tab_id=None, x=1, y=2)
    if isinstance(browser, BrowserToolset):
        browser.execute(request)
    else:
        await browser.execute(request)
    assert touched == ["check", "check", "hover"]
    assert browser.close() == {"status": "closed"}
    with pytest.raises(RuntimeError, match="closed"):
        if isinstance(browser, BrowserToolset):
            browser.execute(request)
        else:
            await browser.execute(request)
    assert touched == ["check", "check", "hover"]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("via_runner", [False, True])
async def test_skipped_protected_read_never_touches_policy_or_state(lane: str, via_runner: bool) -> None:
    import httpx2

    from openai import OpenAI, AsyncOpenAI
    from openai.lib.responses_tool_runner import ResponsesToolRunner, AsyncResponsesToolRunner

    from .test_responses_tool_runner import FINAL, PARAMS, fn, resp

    touched: list[str] = []
    requests: list[dict[str, object]] = []

    def state() -> BrowserState:
        touched.append("state")
        return {
            "tabs": [{"id": "t", "title": "sentinel-private-title", "url": "https://private.invalid", "active": True}]
        }

    async def astate() -> BrowserState:
        return state()

    def click(_args: object) -> None:
        touched.append("click")
        raise RuntimeError("fixture click failed")

    async def aclick(args: object) -> None:
        click(args)

    def read(_args: object) -> str:
        touched.append("read")
        return "sentinel-secret-read"

    async def aread(args: object) -> str:
        return read(args)

    def confirm(ctx: BrowserConfirmContext | BrowserReadConfirmContext) -> bool:
        touched.append("confirm:" + ctx["member"])
        return True

    async def aconfirm(ctx: BrowserConfirmContext | BrowserReadConfirmContext) -> bool:
        return confirm(ctx)

    driver = SimpleNamespace(
        state=state if lane == "sync" else astate,
        get_page_text=read if lane == "sync" else aread,
        click=click if lane == "sync" else aclick,
    )

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(json.loads(request.content))
        first = resp(
            [
                fn("browser_click", "click", tab_id="t", target="ref"),
                fn("browser_get_page_text", "protected", tab_id="t"),
            ],
            "first",
        )
        return httpx2.Response(200, json=first if len(requests) == 1 else FINAL)

    output: object = None
    request = call("get_page_text", tab_id="t")
    if lane == "sync":
        browser = BrowserToolset(
            cast(BrowserDriver, driver),
            members=["click", "get_page_text"],
            confirm_reads=["get_page_text"],
            confirm=confirm,
        )
        if via_runner:
            with OpenAI(api_key="fake", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                ResponsesToolRunner(browser=browser).run(client, PARAMS)
        else:
            output = browser._execute(request, skip=True)[0]
    else:
        browser_async = AsyncBrowserToolset(
            cast(AsyncBrowserDriver, driver),
            members=["click", "get_page_text"],
            confirm_reads=["get_page_text"],
            confirm=aconfirm,
        )
        if via_runner:
            async with AsyncOpenAI(
                api_key="fake", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
            ) as client_async:
                await AsyncResponsesToolRunner(browser=browser_async).run(client_async, PARAMS)
        else:
            output = (await browser_async._execute(request, skip=True))[0]
    if via_runner:
        assert touched == ["state", "confirm:click", "click", "state"]
        history = cast(list[dict[str, object]], requests[1]["input"])
        output = cast(
            object,
            next(
                item
                for item in history
                if item.get("call_id") == "protected" and item.get("type") == "function_call_output"
            ),
        )
    else:
        assert touched == []
    assert "sentinel" not in json.dumps(output)
    assert "private.invalid" not in json.dumps(output)
    assert "not approved" in json.dumps(output)
