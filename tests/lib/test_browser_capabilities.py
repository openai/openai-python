from __future__ import annotations

from copy import deepcopy
from typing import Callable, cast

import pytest

from openai.lib.browser import (
    BrowserError,
    BrowserState,
    BrowserToolset,
    AsyncBrowserToolset,
    BrowserCancelledError,
    BrowserConfirmContext,
)
from openai.types.responses.response_input_param import FunctionCallOutput

from .test_browser import call, payload

MUTATORS = ("click_at", "drag_path", "hold_keys")
MEMBERS = (*MUTATORS, "read_page_scoped")
ARGS: dict[str, dict[str, object]] = {
    "click_at": {"tab_id": None, "x": 0, "y": 9007199254740991, "button": "middle", "click_count": 2, "keys": ["Alt"]},
    "drag_path": {"tab_id": "one", "path": [{"x": 2, "y": 7}, {"x": 9, "y": 0}], "keys": ["Control", "Shift"]},
    "hold_keys": {"tab_id": None, "keys": ["ArrowDown", "Shift"], "duration_ms": 3000},
    "read_page_scoped": {"tab_id": "one", "root": None, "depth": 32, "filter": "all"},
}
REPORT = {
    "version": 1,
    "text": "Two orders",
    "elements": [{"ref": "element_one", "role": "button", "label": "Open"}],
    "omitted": [],
    "scopes": [{"ref": "section_one", "label": "Order one"}],
}


class Driver:
    def __init__(self) -> None:
        self.states = 0
        self.effects: list[tuple[str, dict[str, object], Callable[[], bool] | None]] = []
        self.report: object = deepcopy(REPORT)
        self.change_report = False

    def state(self) -> BrowserState:
        self.states += 1
        if self.change_report and self.states == 2:
            report = cast(dict[str, object], self.report)
            cast(list[dict[str, object]], report["scopes"])[0]["ref"] = "changed"
            cast(list[dict[str, object]], report["elements"])[0]["label"] = "private"
        return {"tabs": [{"id": "one", "title": "Public", "url": "https://fixture.invalid/", "active": True}]}

    def click_at(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> None:
        self.effects.append(("click_at", args, cancelled))

    def drag_path(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> str:
        self.effects.append(("drag_path", args, cancelled))
        return "Dragged"

    def hold_keys(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> None:
        self.effects.append(("hold_keys", args, cancelled))

    def read_page_scoped(self, args: dict[str, object]) -> object:
        self.effects.append(("read_page_scoped", args, None))
        return self.report


class AsyncDriver:
    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    async def state(self) -> BrowserState:
        return self.driver.state()

    async def click_at(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> None:
        self.driver.click_at(args, cancelled=cancelled)

    async def drag_path(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> str:
        return self.driver.drag_path(args, cancelled=cancelled)

    async def hold_keys(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> None:
        self.driver.hold_keys(args, cancelled=cancelled)

    async def read_page_scoped(self, args: dict[str, object]) -> object:
        return self.driver.read_page_scoped(args)


def toolset(
    lane: str, driver: Driver, *, members: list[str] | None = None, approval: bool | None = None
) -> BrowserToolset | AsyncBrowserToolset:
    def confirm(_ctx: BrowserConfirmContext) -> bool:
        return approval is True

    async def async_confirm(ctx: BrowserConfirmContext) -> bool:
        return confirm(ctx)

    if lane == "sync":
        return BrowserToolset(driver, members=members, confirm=None if approval is None else confirm)
    return AsyncBrowserToolset(
        AsyncDriver(driver), members=members, confirm=None if approval is None else async_confirm
    )


async def dispatch(
    browser: BrowserToolset | AsyncBrowserToolset,
    member: str,
    args: object,
    cancelled: Callable[[], bool] | None = None,
) -> FunctionCallOutput:
    request = call(member, args)
    if isinstance(browser, AsyncBrowserToolset):
        return await browser.execute(request, cancelled=cancelled)
    return browser.execute(request, cancelled=cancelled)


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_triple_click_is_one_driver_call(lane: str) -> None:
    driver = Driver()
    browser = toolset(lane, driver, members=["click_at"], approval=True)
    args = {**ARGS["click_at"], "click_count": 3}
    assert payload(await dispatch(browser, "click_at", args))["ok"]
    assert driver.effects == [("click_at", args, None)]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", MEMBERS)
async def test_default_capabilities_reject_before_driver_state_or_policy(lane: str, member: str) -> None:
    driver = Driver()
    browser = toolset(lane, driver)
    assert [tool["name"] for tool in browser.tools] == ["browser_list_tabs"]
    with pytest.raises(BrowserError, match="disabled"):
        await dispatch(browser, member, ARGS[member])
    assert driver.states == 0
    assert driver.effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", MEMBERS)
async def test_unselected_methods_and_policies_are_never_read(
    lane: str, member: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = Driver()
    implementation = driver if lane == "sync" else AsyncDriver(driver)

    def forbidden(_self: object) -> None:
        pytest.fail("disabled member/policy was accessed")

    monkeypatch.setattr(type(implementation), member, property(forbidden))
    browser = (
        BrowserToolset(cast(Driver, implementation))
        if lane == "sync"
        else AsyncBrowserToolset(cast(AsyncDriver, implementation))
    )
    monkeypatch.setattr(type(browser), "confirm", property(forbidden), raising=False)
    monkeypatch.setattr(type(browser), "url_policy", property(forbidden), raising=False)
    with pytest.raises(BrowserError, match="disabled"):
        await dispatch(browser, member, ARGS[member])
    assert driver.states == 0


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", MEMBERS)
def test_selected_capability_requires_implementation(lane: str, member: str) -> None:
    class StateOnly:
        def state(self) -> BrowserState:
            return {"tabs": []}

    class AsyncStateOnly:
        async def state(self) -> BrowserState:
            return {"tabs": []}

    with pytest.raises(ValueError, match="not implemented"):
        if lane == "sync":
            BrowserToolset(StateOnly(), members=[member], confirm=lambda _: True)
        else:
            AsyncBrowserToolset(AsyncStateOnly(), members=[member])


def test_implicit_selection_keeps_all_original_methods_but_never_registers_new_ones() -> None:
    class AllMethods(Driver):
        def __getattr__(self, _name: str) -> Callable[[object], None]:
            return lambda _: None

    browser = BrowserToolset(AllMethods(), confirm=lambda _: True, url_policy=lambda _ctx, _url: True)
    assert [tool["name"] for tool in browser.tools] == [
        "browser_navigate",
        "browser_read_page",
        "browser_get_page_text",
        "browser_find",
        "browser_click",
        "browser_type",
        "browser_key",
        "browser_scroll",
        "browser_select_option",
        "browser_hover",
        "browser_screenshot",
        "browser_zoom",
        "browser_new_tab",
        "browser_list_tabs",
        "browser_switch_tab",
        "browser_close_tab",
        "browser_scroll_to",
        "browser_wait_for",
    ]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", MUTATORS)
async def test_mutators_need_explicit_confirmation_and_pass_call_cancellation(lane: str, member: str) -> None:
    driver = Driver()
    with pytest.raises(ValueError, match="require confirm"):
        toolset(lane, driver, members=[member])
    browser = toolset(lane, driver, members=[member], approval=False)
    denied = payload(await dispatch(browser, member, ARGS[member]))
    assert denied["ok"] is False and driver.effects == []
    browser = toolset(lane, driver, members=[member], approval=True)
    cancelled = lambda: False
    result = payload(await dispatch(browser, member, ARGS[member], cancelled))
    assert result["ok"] is True
    assert driver.effects == [(member, ARGS[member], cancelled)]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", MUTATORS)
async def test_cancelled_mutators_cannot_reach_driver(lane: str, member: str) -> None:
    driver = Driver()
    browser = toolset(lane, driver, members=[member], approval=True)
    with pytest.raises(BrowserCancelledError):
        await dispatch(browser, member, ARGS[member], lambda: True)
    assert driver.effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "member,field,value",
    [
        ("click_at", "x", True),
        ("click_at", "x", -1),
        ("click_at", "y", 2**53),
        ("click_at", "y", 1.0),
        ("click_at", "button", "wheel"),
        ("click_at", "click_count", True),
        ("click_at", "click_count", 4),
        ("click_at", "keys", ["Alt", "Alt"]),
        ("click_at", "keys", ["Command"]),
        ("drag_path", "path", [{"x": 0, "y": 0}]),
        ("drag_path", "path", [{"x": 0, "y": 0}] * 101),
        ("drag_path", "path", [{"x": 0, "y": 0}, {"x": 1, "y": 2, "extra": "no"}]),
        ("drag_path", "path", [{"x": 0, "y": 0}, {"x": 1, "y": False}]),
        ("drag_path", "path", [{"x": 0, "y": 0}, {"x": 1}]),
        ("drag_path", "keys", ["Shift", "Shift"]),
        ("hold_keys", "keys", []),
        ("hold_keys", "keys", list("123456789")),
        ("hold_keys", "keys", ["a", "a"]),
        ("hold_keys", "keys", [""]),
        ("hold_keys", "keys", ["é" * 33]),
        ("hold_keys", "keys", ["\ud800"]),
        ("hold_keys", "duration_ms", 0),
        ("hold_keys", "duration_ms", 3001),
        ("hold_keys", "duration_ms", True),
        ("read_page_scoped", "depth", 0),
        ("read_page_scoped", "depth", 33),
        ("read_page_scoped", "depth", True),
        ("read_page_scoped", "root", ""),
        ("read_page_scoped", "root", "é" * 129),
        ("read_page_scoped", "root", "\ud800"),
        ("read_page_scoped", "filter", "all_frames"),
        ("read_page_scoped", "unexpected", "no"),
    ],
)
async def test_invalid_vectors_never_reach_driver(lane: str, member: str, field: str, value: object) -> None:
    driver = Driver()
    browser = toolset(lane, driver, members=[member], approval=True)
    result = payload(await dispatch(browser, member, {**ARGS[member], field: value}))
    assert result["ok"] is False
    assert driver.effects == []


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_scoped_reads_project_and_snapshot_before_final_state(lane: str) -> None:
    driver = Driver()
    raw = cast(dict[str, object], driver.report)
    raw["driver_private"] = "unreported"
    cast(list[dict[str, object]], raw["scopes"])[0]["internal"] = "unreported"
    driver.change_report = True
    browser = toolset(lane, driver, members=["read_page_scoped"])
    result = payload(await dispatch(browser, "read_page_scoped", ARGS["read_page_scoped"]))
    assert result["ok"] is True
    assert result["result"] == REPORT
    assert driver.states == 2


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "result",
    [
        None,
        "legacy",
        {key: value for key, value in REPORT.items() if key != "scopes"},
        {**REPORT, "scopes": None},
        {**REPORT, "scopes": [{"ref": "section", "label": "one"}] * 101},
        {**REPORT, "scopes": [{"ref": "section", "label": "one"}, {"ref": "section", "label": "two"}]},
        {**REPORT, "scopes": [{"ref": "element_one", "label": "collision"}]},
        {**REPORT, "scopes": [{"ref": "", "label": "one"}]},
        {**REPORT, "scopes": [{"ref": "valid", "label": "é" * 129}]},
        {**REPORT, "scopes": [{"ref": "\ud800", "label": "one"}]},
        {**REPORT, "elements": [{"ref": "scope", "role": "region", "label": "not actionable"}]},
    ],
)
async def test_invalid_scope_reports_stop_before_final_state(lane: str, result: object) -> None:
    driver = Driver()
    driver.report = deepcopy(result)
    browser = toolset(lane, driver, members=["read_page_scoped"])
    with pytest.raises(RuntimeError, match="Browser read report failed"):
        await dispatch(browser, "read_page_scoped", ARGS["read_page_scoped"])
    assert driver.states == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("count", [101, 1000])
async def test_v1_driver_selected_scope_sizes(lane: str, count: int) -> None:
    driver = Driver()
    driver.report = {
        "version": 1,
        "text": "🦄" * 20_000,
        "elements": [],
        "omitted": [],
        "scopes": [{"ref": str(n) + "x" * 250, "label": "y" * 256} for n in range(count)],
    }
    browser = toolset(lane, driver, members=["read_page_scoped"])
    result = await dispatch(browser, "read_page_scoped", ARGS["read_page_scoped"])
    assert payload(result)["result"] == driver.report
    assert driver.states == 2


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_diagnostics_cannot_rewrite_read_result_and_numeric_id_stops_before_state(lane: str) -> None:
    from openai.lib.tool_diagnostics import ToolDiagnostic

    driver = Driver()
    browser = toolset(lane, driver, members=["read_page_scoped"])

    def diagnostic(event: ToolDiagnostic) -> None:
        if event["stage"] == "action" and event["reason"] == "completed":
            current = cast(dict[str, object], driver.report)
            current["text"] = "changed"
            current["elements"] = []

    request = call("read_page_scoped", ARGS["read_page_scoped"])
    if isinstance(browser, BrowserToolset):
        result = browser.execute(request, on_diagnostic=diagnostic)
    else:
        result = await browser.execute(request, on_diagnostic=diagnostic)
    assert payload(result)["result"] == REPORT
    before = driver.states
    invalid = call("read_page_scoped", ARGS["read_page_scoped"])
    invalid.call_id = cast(str, 7)
    with pytest.raises(RuntimeError, match="string call_id"):
        if isinstance(browser, BrowserToolset):
            browser.execute(invalid)
        else:
            await browser.execute(invalid)
    assert driver.states == before
