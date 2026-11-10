from __future__ import annotations

from typing import Callable
from typing_extensions import override

import pytest

from openai.lib.browser import BrowserError, BrowserState, BrowserToolset, AsyncBrowserToolset

from .test_browser import payload
from .test_browser_capabilities import dispatch

MEMBERS = ["upload_file", "download_file"]
ARGS = {"grant_id": "task-grant"}
COMPLETED = {"version": 1, "status": "completed", "effect": "completed", "cleanup": "completed"}


class Driver:
    def __init__(self, result: object = None) -> None:
        self.result = result
        self.states = 0
        self.calls = 0
        self.cancel: Callable[[], bool] | None = None
        self.on_state: Callable[[], None] = lambda: None

    def state(self) -> BrowserState:
        self.states += 1
        self.on_state()
        return {"tabs": []}

    def upload_file(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> object:
        assert args == ARGS
        self.calls += 1
        self.cancel = cancelled
        return self.result

    download_file = upload_file


class AsyncDriver:
    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    async def state(self) -> BrowserState:
        return self.driver.state()

    async def upload_file(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None) -> object:
        return self.driver.upload_file(args, cancelled=cancelled)

    download_file = upload_file


def tools(
    lane: str, driver: Driver, members: list[str] | None, approve: bool | None = True
) -> BrowserToolset | AsyncBrowserToolset:
    async def confirmation(_ctx: object) -> bool:
        return approve is True

    if lane == "async":
        return AsyncBrowserToolset(
            AsyncDriver(driver), members=members, confirm=None if approve is None else confirmation
        )
    return BrowserToolset(driver, members=members, confirm=None if approve is None else lambda _: approve is True)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", MEMBERS)
async def test_file_members_need_explicit_selection_and_consent(lane: str, member: str) -> None:
    driver = Driver(COMPLETED)
    hidden = tools(lane, driver, None, None)
    with pytest.raises(BrowserError, match="disabled"):
        await dispatch(hidden, member, ARGS)
    assert driver.states == 0 and driver.calls == 0
    with pytest.raises(ValueError, match="require confirm"):
        tools(lane, driver, [member], None)
    result = payload(await dispatch(tools(lane, driver, [member], False), member, ARGS))
    assert result["ok"] is False and driver.calls == 0


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "args",
    [
        {},
        {"grant_id": ""},
        {"grant_id": 1},
        {"grant_id": "é" * 129},
        {"grant_id": "\ud800"},
        {**ARGS, "path": "/private/file"},
    ],
)
async def test_invalid_file_grants_do_not_reach_handler(lane: str, args: dict[str, object]) -> None:
    driver = Driver(COMPLETED)
    result = payload(await dispatch(tools(lane, driver, MEMBERS), "upload_file", args))
    assert result["ok"] is False and driver.calls == 0


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", MEMBERS)
@pytest.mark.parametrize(
    "status,effect,cleanup",
    [
        ("completed", "completed", "completed"),
        ("refused", "none", "not_started"),
        ("unknown", "unknown", "pending"),
        ("interrupted", "none", "completed"),
        ("interrupted", "unknown", "pending"),
    ],
)
async def test_terminal_file_outcome_is_snapshotted(
    lane: str, member: str, status: str, effect: str, cleanup: str
) -> None:
    original = {"version": 1, "status": status, "effect": effect, "cleanup": cleanup}
    value = original.copy()
    driver = Driver(value)

    def mutate() -> None:
        if driver.states == 2:
            value["cleanup"] = "not_started"

    driver.on_state = mutate
    cancelled = lambda: False
    result = payload(await dispatch(tools(lane, driver, MEMBERS), member, ARGS, cancelled))
    assert result["result"] == original
    assert result["ok"] is (status == "completed")
    assert driver.cancel is cancelled and driver.calls == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "value",
    [
        None,
        "uploaded",
        {},
        {**COMPLETED, "version": True},
        {**COMPLETED, "status": "in_progress"},
        {**COMPLETED, "status": "refused"},
        {**COMPLETED, "effect": "unknown"},
        {**COMPLETED, "cleanup": "failed"},
        {**COMPLETED, "path": "/private/file"},
    ],
)
async def test_invalid_file_result_stops_before_final_state(lane: str, value: object) -> None:
    driver = Driver(value)
    with pytest.raises(RuntimeError, match="file result failed"):
        await dispatch(tools(lane, driver, MEMBERS), "download_file", ARGS)
    assert driver.states == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_file_result_hides_errors_from_driver_keys(lane: str) -> None:
    class PrivateKey(str):
        __hash__ = str.__hash__

        @override
        def __eq__(self, other: object) -> bool:
            raise ValueError("SYNTHETIC_PRIVATE_ERROR")

    driver = Driver({"version": 1, PrivateKey("status"): "completed", "effect": "completed", "cleanup": "completed"})
    with pytest.raises(RuntimeError, match="^Browser file result failed.$"):
        await dispatch(tools(lane, driver, MEMBERS), "download_file", ARGS)
    assert driver.states == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_file_result_rejects_key_aliases_with_private_serialized_text(lane: str) -> None:
    class PrivateAlias(str):
        @override
        def __hash__(self) -> int:
            return hash("status")

        @override
        def __eq__(self, other: object) -> bool:
            return other == "status"

    value = {
        "version": 1,
        PrivateAlias("SYNTHETIC_PRIVATE_KEY"): "completed",
        "effect": "completed",
        "cleanup": "completed",
    }
    driver = Driver(value)
    with pytest.raises(RuntimeError, match="^Browser file result failed.$"):
        await dispatch(tools(lane, driver, MEMBERS), "download_file", ARGS)
    assert driver.states == 1
