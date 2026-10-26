from __future__ import annotations

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

from .test_browser import payload
from .test_browser_capabilities import dispatch

ARGS: dict[str, dict[str, object]] = {
    "read_diagnostics": {"tab_id": None, "source": "console", "limit": 100},
    "run_script": {"tab_id": None, "source": "return 1", "timeout_ms": 30_000},
}


class Driver:
    def __init__(self) -> None:
        self.states = 0
        self.calls: list[str] = []
        self.result: object = ""
        self.cancel: Callable[[], bool] | None = None
        self.script_args: dict[str, object] | None = None

    def state(self) -> BrowserState:
        self.states += 1
        return {"tabs": [{"id": "one", "title": "Public", "url": "http://127.0.0.1/", "active": True}]}

    def read_diagnostics(self, _args: dict[str, object]) -> object:
        self.calls.append("diagnostics")
        return self.result

    def run_script(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> object:
        self.calls.append("script")
        self.script_args = args
        self.cancel = cancelled
        return self.result


class AsyncDriver:
    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    async def state(self) -> BrowserState:
        return self.driver.state()

    async def read_diagnostics(self, args: dict[str, object]) -> object:
        return self.driver.read_diagnostics(args)

    async def run_script(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> object:
        return self.driver.run_script(args, cancelled=cancelled)


def toolset(
    lane: str, driver: Driver, members: list[str] | None, approve: bool | None
) -> BrowserToolset | AsyncBrowserToolset:
    async def confirmation(_ctx: object) -> bool:
        return approve is True

    if lane == "async":
        return AsyncBrowserToolset(
            AsyncDriver(driver), members=members, confirm=None if approve is None else confirmation
        )
    return BrowserToolset(driver, members=members, confirm=None if approve is None else lambda _: approve is True)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", ARGS)
async def test_sensitive_disabled_before_state_or_property(
    lane: str, member: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    driver = Driver()
    implementation = driver if lane == "sync" else AsyncDriver(driver)

    def forbidden(_self: object) -> None:
        pytest.fail("disabled driver handler or policy was read")

    monkeypatch.setattr(type(implementation), member, property(forbidden))
    browser = (
        BrowserToolset(cast(Driver, implementation))
        if lane == "sync"
        else AsyncBrowserToolset(cast(AsyncDriver, implementation))
    )
    monkeypatch.setattr(type(browser), "confirm", property(forbidden), raising=False)
    with pytest.raises(BrowserError, match="disabled"):
        await dispatch(browser, member, ARGS[member])
    assert driver.states == 0 and driver.calls == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", ARGS)
@pytest.mark.parametrize("approve", [None, False])
async def test_sensitive_needs_approval(lane: str, member: str, approve: bool | None) -> None:
    driver = Driver()
    if approve is None:
        with pytest.raises(ValueError, match="require confirm"):
            toolset(lane, driver, [member], approve)
        assert driver.states == 0 and driver.calls == []
        return
    result = payload(await dispatch(toolset(lane, driver, [member], approve), member, ARGS[member]))
    assert result["ok"] is False and driver.calls == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    ("member", "field", "bad"),
    [
        ("read_diagnostics", "source", "all"),
        ("read_diagnostics", "limit", 0),
        ("read_diagnostics", "limit", 101),
        ("read_diagnostics", "limit", True),
        ("run_script", "source", ""),
        ("run_script", "source", 123),
        ("run_script", "source", "\ud800"),
        ("run_script", "timeout_ms", 0),
        ("run_script", "timeout_ms", 30_001),
        ("run_script", "timeout_ms", True),
    ],
)
async def test_bad_sensitive_args_do_not_call_handler(lane: str, member: str, field: str, bad: object) -> None:
    driver = Driver()
    result = payload(await dispatch(toolset(lane, driver, [member], True), member, {**ARGS[member], field: bad}))
    assert result["ok"] is False and driver.calls == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    ("member", "result"),
    [
        ("read_diagnostics", None),
        ("read_diagnostics", "text"),
        (
            "read_diagnostics",
            {"version": 1, "text": "", "elements": [{"ref": "b", "role": "button", "label": "B"}], "omitted": []},
        ),
        ("read_diagnostics", {"version": 1, "text": "\ud800", "elements": [], "omitted": []}),
        ("run_script", None),
        ("run_script", {"text": "private"}),
        ("run_script", "\ud800"),
    ],
)
async def test_sensitive_invalid_result_fails_before_final_state(lane: str, member: str, result: object) -> None:
    driver = Driver()
    driver.result = result
    with pytest.raises(RuntimeError):
        await dispatch(toolset(lane, driver, [member], True), member, ARGS[member])
    assert driver.states == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "source",
    ["/*" + "x" * 32_768 + "*/return 1", "/*" + "é" * 16_384 + "*/return 1"],
    ids=["large-ascii", "large-unicode"],
)
async def test_approved_results_and_live_cancel_reach_script(lane: str, source: str) -> None:
    driver = Driver()
    driver.result = {"version": 1, "text": "warning é" * 8193, "elements": [], "omitted": []}
    approvals: list[BrowserConfirmContext] = []

    def confirm(context: BrowserConfirmContext) -> bool:
        approvals.append(context)
        return True

    async def async_confirm(context: BrowserConfirmContext) -> bool:
        return confirm(context)

    browser = (
        AsyncBrowserToolset(AsyncDriver(driver), members=list(ARGS), confirm=async_confirm)
        if lane == "async"
        else BrowserToolset(driver, members=list(ARGS), confirm=confirm)
    )
    assert payload(await dispatch(browser, "read_diagnostics", ARGS["read_diagnostics"]))["result"] == driver.result
    driver.result = "é" * 32_768
    stopped = False

    def cancelled() -> bool:
        return stopped

    assert (
        payload(await dispatch(browser, "run_script", {**ARGS["run_script"], "source": source}, cancelled))["result"]
        == driver.result
    )
    assert approvals[1]["arguments"]["source"] == source
    assert driver.script_args == {**ARGS["run_script"], "source": source}
    assert driver.cancel is not None
    assert driver.cancel is cancelled and driver.cancel() is False
    stopped = True
    assert driver.cancel()
    with pytest.raises(BrowserCancelledError):
        await dispatch(browser, "run_script", ARGS["run_script"], cancelled)
    assert driver.calls == ["diagnostics", "script"]
