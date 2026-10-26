from __future__ import annotations

import gc
import json
from types import SimpleNamespace
from typing import Callable, Awaitable, cast
from functools import wraps, partial
from typing_extensions import override

import pytest

from openai._models import construct_type_unchecked
from openai.lib.browser import (
    BROWSER_MEMBERS,
    DEFAULT_BROWSER_MEMBERS,
    BrowserDriver,
    BrowserToolset,
    AsyncBrowserDriver,
    AsyncBrowserToolset,
)
from openai.types.responses import ResponseFunctionToolCall


def state() -> dict[str, object]:
    return {"active_tab_id": None, "tabs": []}


async def async_state() -> dict[str, object]:
    return state()


def read(_action: object) -> str:
    return "owned page"


async def async_read(_action: object) -> str:
    return read(_action)


def decorated_read(function: Callable[[object], str]) -> Callable[[object], str]:
    @wraps(function)
    def wrapped(action: object) -> str:
        return function(action)

    return wrapped


def decorated_async_read(function: Callable[[object], Awaitable[str]]) -> Callable[[object], Awaitable[str]]:
    @wraps(function)
    async def wrapped(action: object) -> str:
        return await function(action)

    return wrapped


class SyncReader:
    def __call__(self, _action: object) -> str:
        return "owned page"


class AsyncReader:
    async def __call__(self, _action: object) -> str:
        return "owned page"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("shape", ["function", "decorated", "callable", "partial"])
async def test_selected_wrong_flavor_stops_before_registration(lane: str, shape: str) -> None:
    sync_read = {
        "function": read,
        "decorated": decorated_read(read),
        "callable": SyncReader(),
        "partial": partial(read),
    }[shape]
    async_read_fn = {
        "function": async_read,
        "decorated": decorated_async_read(async_read),
        "callable": AsyncReader(),
        "partial": partial(async_read),
    }[shape]
    driver = SimpleNamespace(
        state=state if lane == "sync" else async_state,
        get_page_text=async_read_fn if lane == "sync" else sync_read,
    )
    correct = "AsyncBrowserToolset" if lane == "sync" else "BrowserToolset"
    with pytest.raises(ValueError, match=f"get_page_text.*{correct}"):
        if lane == "sync":
            BrowserToolset(cast(BrowserDriver, driver))
        else:
            AsyncBrowserToolset(cast(AsyncBrowserDriver, driver))


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_selected_partial_executes_with_the_matching_flavor(lane: str) -> None:
    driver = SimpleNamespace(
        state=state if lane == "sync" else async_state,
        get_page_text=partial(read if lane == "sync" else async_read),
    )
    request = construct_type_unchecked(
        type_=ResponseFunctionToolCall,
        value={
            "type": "function_call",
            "name": "browser_get_page_text",
            "call_id": "partial",
            "arguments": '{"tab_id":null}',
            "status": "completed",
        },
    )
    if lane == "sync":
        result = BrowserToolset(cast(BrowserDriver, driver)).execute(request)
    else:
        result = await AsyncBrowserToolset(cast(AsyncBrowserDriver, driver)).execute(request)
    assert "owned page" in str(result["output"])


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_additional_members_preserves_partial_defaults_and_avoids_excluded_getters(lane: str) -> None:
    class Dynamic:
        def __getattr__(self, member: str) -> object:
            if member == "state":
                return state if lane == "sync" else async_state
            if member == "get_page_text":
                return read if lane == "sync" else async_read
            if member == "read_page_scoped":
                return read if lane == "sync" else async_read
            if member in set(BROWSER_MEMBERS) - set(DEFAULT_BROWSER_MEMBERS):
                raise AssertionError(f"excluded optional getter: {member}")
            raise AttributeError(member)

    driver = Dynamic()
    toolset = (
        BrowserToolset(cast(BrowserDriver, driver), additional_members=["read_page_scoped"])
        if lane == "sync"
        else AsyncBrowserToolset(cast(AsyncBrowserDriver, driver), additional_members=["read_page_scoped"])
    )
    assert [tool["name"] for tool in toolset.tools] == [
        "browser_get_page_text",
        "browser_list_tabs",
        "browser_read_page_scoped",
    ]
    assert "read_page_scoped" in BROWSER_MEMBERS
    assert "read_page_scoped" not in DEFAULT_BROWSER_MEMBERS
    with pytest.raises(ValueError, match="either members or additional_members"):
        if lane == "sync":
            BrowserToolset(cast(BrowserDriver, driver), members=[], additional_members=[])
        else:
            AsyncBrowserToolset(cast(AsyncBrowserDriver, driver), members=[], additional_members=[])
    with pytest.raises(ValueError, match="not implemented"):
        if lane == "sync":
            BrowserToolset(cast(BrowserDriver, driver), additional_members=["click"])
        else:
            AsyncBrowserToolset(cast(AsyncBrowserDriver, driver), additional_members=["click"])


async def test_uninspectable_sync_wrapper_closes_accidental_coroutine_without_success(
    recwarn: pytest.WarningsRecorder,
) -> None:
    def obscure(action: object) -> object:
        return async_read(action)

    browser = BrowserToolset(cast(BrowserDriver, SimpleNamespace(state=state, get_page_text=obscure)))
    result = browser.execute(
        construct_type_unchecked(
            type_=ResponseFunctionToolCall,
            value={
                "type": "function_call",
                "name": "browser_get_page_text",
                "call_id": "opaque-wrapper",
                "arguments": '{"tab_id":null}',
                "status": "completed",
            },
        )
    )
    payload = json.loads(result["output"][0]["text"])  # type: ignore[index]
    assert payload["error"] == "Browser action failed."
    gc.collect()
    assert not [warning for warning in recwarn if "never awaited" in str(warning.message)]


async def test_async_helper_accepts_unannotated_awaitable_wrapper() -> None:
    def wrapped(action: object):  # type: ignore[no-untyped-def]
        return async_read(action)

    browser = AsyncBrowserToolset(cast(AsyncBrowserDriver, SimpleNamespace(state=async_state, get_page_text=wrapped)))
    result = await browser.execute(
        construct_type_unchecked(
            type_=ResponseFunctionToolCall,
            value={
                "type": "function_call",
                "name": "browser_get_page_text",
                "call_id": "wrapped",
                "arguments": '{"tab_id":null}',
                "status": "completed",
            },
        )
    )
    assert "owned page" in str(result["output"])


def test_inherited_capability_protocol_cannot_advertise_a_stub() -> None:
    from openai.lib.browser import BrowserState, BrowserReadDriver

    class MissingRead(BrowserReadDriver):
        @override
        def state(self) -> BrowserState:
            return {"tabs": []}

    with pytest.raises(TypeError, match="abstract"):
        MissingRead()  # type: ignore[abstract]
