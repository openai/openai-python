from __future__ import annotations

import json
import asyncio
from copy import deepcopy
from typing import Any, Callable, Sequence, cast
from datetime import datetime, timezone
from typing_extensions import override

import pytest

from openai.lib.browser import (
    TabInput,
    ZoomInput,
    BrowserTab,
    ClickInput,
    ScrollInput,
    BrowserError,
    BrowserState,
    NavigateInput,
    BrowserToolset,
    AsyncBrowserToolset,
    BrowserObservationV1,
    BrowserConfirmContext,
)
from openai.types.responses import ResponseFunctionToolCall
from openai.types.responses.parsed_response import ParsedResponseFunctionToolCall
from openai.types.responses.response_input_param import FunctionCallOutput
from openai.types.responses.response_input_image_content_param import ResponseInputImageContentParam


def call(member: str, args: object) -> ResponseFunctionToolCall:
    return ResponseFunctionToolCall(
        type="function_call",
        name="browser_" + member,
        call_id="call_one",
        status="completed",
        arguments=json.dumps(args),
    )


def payload(result: FunctionCallOutput) -> dict[str, object]:
    content = result["output"]
    assert isinstance(content, list) and content[0]["type"] == "input_text"
    return cast(dict[str, object], json.loads(content[0]["text"]))


def reported_state(title: str = "Page") -> BrowserState:
    return {"tabs": [{"id": "one", "title": title, "url": "https://allowed.example", "active": True}]}


class Desktop:
    def __init__(self) -> None:
        self.url = "https://allowed.example/"
        self.clicked: list[str] = []

    def state(self) -> BrowserState:
        return {"tabs": [{"id": "one", "title": "Page", "url": self.url, "active": True}]}

    def navigate(self, action: NavigateInput) -> None:
        self.url = action["url"]

    def click(self, action: ClickInput) -> None:
        if action["target"] == "private":
            raise ValueError("file:///Users/private/password")
        if action["target"] == "missing":
            raise BrowserError("Element is no longer on the page.")
        self.clicked.append(action["target"])

    def get_page_text(self, action: TabInput) -> str:
        assert action["tab_id"] in (None, "one")
        return "Local page content"

    def screenshot(self, action: TabInput) -> ResponseInputImageContentParam:
        assert action["tab_id"] in (None, "one")
        return {"type": "input_image", "image_url": "data:image/png;base64,cG5n"}

    def zoom(self, action: ZoomInput) -> ResponseInputImageContentParam:
        assert action["tab_id"] in (None, "one")
        return {"type": "input_image", "image_url": "data:image/png;base64,Y3JvcA=="}


class AsyncDesktop:
    def __init__(self, desktop: Desktop) -> None:
        self.desktop = desktop

    async def state(self) -> BrowserState:
        return self.desktop.state()

    async def navigate(self, action: NavigateInput) -> None:
        self.desktop.navigate(action)

    async def click(self, action: ClickInput) -> None:
        self.desktop.click(action)

    async def get_page_text(self, action: TabInput) -> str:
        return self.desktop.get_page_text(action)

    async def screenshot(self, action: TabInput) -> ResponseInputImageContentParam:
        return self.desktop.screenshot(action)

    async def zoom(self, action: ZoomInput) -> ResponseInputImageContentParam:
        return self.desktop.zoom(action)


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_member_selection_snapshots_capabilities_and_never_reads_excluded_methods(
    lane: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    desktop = Desktop()
    driver = desktop if lane == "sync" else AsyncDesktop(desktop)
    reads: list[bool] = []
    original_state = desktop.state

    def excluded(_self: object) -> None:
        pytest.fail("excluded driver method must not be read")

    def state() -> BrowserState:
        reads.append(True)
        return original_state()

    async def async_state() -> BrowserState:
        return state()

    monkeypatch.setattr(type(driver), "navigate", property(excluded))
    monkeypatch.setattr(driver, "state", state if lane == "sync" else async_state)
    selected = ["screenshot", "get_page_text"]
    browser = (
        BrowserToolset(desktop, members=selected)
        if lane == "sync"
        else AsyncBrowserToolset(cast(AsyncDesktop, driver), members=selected)
    )
    selected[:] = ["navigate"]
    assert [tool["name"] for tool in browser.tools] == ["browser_get_page_text", "browser_screenshot"]

    async def dispatch(request: ResponseFunctionToolCall) -> FunctionCallOutput:
        if isinstance(browser, AsyncBrowserToolset):
            return await browser.execute(request)
        return browser.execute(request)

    assert payload(await dispatch(call("get_page_text", {"tab_id": None})))["state"] == reported_state()
    reads.clear()
    for member, args in [("navigate", {"url": "https://allowed.example/", "tab_id": None}), ("list_tabs", {})]:
        with pytest.raises(BrowserError, match="disabled"):
            await dispatch(call(member, args))
    assert reads == []
    empty = (
        BrowserToolset(desktop, members=[])
        if lane == "sync"
        else AsyncBrowserToolset(cast(AsyncDesktop, driver), members=[])
    )
    assert empty.tools == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("members", ["click", ["click", "click"], ["__class__"], ["unknown"], [1], {"click"}])
def test_invalid_member_selection_precedes_driver_access(lane: str, members: object) -> None:
    class UnavailableDriver:
        def __getattr__(self, _name: str) -> object:
            pytest.fail("invalid selection must not inspect the driver")

    toolset = BrowserToolset if lane == "sync" else AsyncBrowserToolset
    with pytest.raises(ValueError, match="unique fixed"):
        toolset(cast(Any, UnavailableDriver()), members=cast(Sequence[str], members))
    driver = Desktop() if lane == "sync" else AsyncDesktop(Desktop())
    with pytest.raises(ValueError, match="not implemented"):
        toolset(cast(Any, driver), members=["hover"])


async def execute(
    lane: str,
    desktop: Desktop,
    request: ResponseFunctionToolCall,
    confirm: Callable[[BrowserConfirmContext], bool],
    policy: Callable[[BrowserConfirmContext, str], bool],
) -> FunctionCallOutput:
    if lane == "sync":
        return BrowserToolset(desktop, confirm=confirm, url_policy=policy).execute(request)

    async def async_confirm(ctx: BrowserConfirmContext) -> bool:
        return confirm(ctx)

    async def async_policy(ctx: BrowserConfirmContext, url: str) -> bool:
        return policy(ctx, url)

    return await AsyncBrowserToolset(AsyncDesktop(desktop), confirm=async_confirm, url_policy=async_policy).execute(
        request
    )


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_policy_and_confirmation_receive_detached_snapshots(lane: str) -> None:
    desktop = Desktop()

    def policy(ctx: BrowserConfirmContext, url: str) -> bool:
        ctx["arguments"]["url"] = "https://attacker.example/"
        ctx["state"]["tabs"].clear()
        return url.startswith("https://allowed.example/")

    def confirm(ctx: BrowserConfirmContext) -> bool:
        assert ctx["state"]["tabs"][0]["url"] == "https://allowed.example"
        ctx["arguments"]["url"] = "file:///private"
        return True

    result = await execute(
        lane, desktop, call("navigate", {"url": "https://allowed.example/tasks", "tab_id": None}), confirm, policy
    )
    assert payload(result)["ok"] is True
    assert desktop.url == "https://allowed.example/tasks"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("kind", ["empty", "native-json", "bare-parsed", "parsed-model", "invalid-extra"])
async def test_direct_browser_native_replay_precedes_state_and_approval(lane: str, kind: str) -> None:
    class Reported(Desktop):
        def __init__(self) -> None:
            super().__init__()
            self.events: list[str] = []

        @override
        def state(self) -> BrowserState:
            self.events.append("state")
            return super().state()

    driver = Reported()
    request = call("click", {"tab_id": "one", "target": "button"})
    if kind == "empty":
        request.call_id = ""
    elif kind == "native-json":
        setattr(request, "extra", {"at": datetime(2025, 1, 2, tzinfo=timezone.utc), "json": [None, True, 3]})  # noqa: B010
    elif kind == "bare-parsed":
        setattr(request, "parsed_arguments", object())  # noqa: B010
        setattr(request, "created_by", object())  # noqa: B010
    elif kind == "parsed-model":
        request = ParsedResponseFunctionToolCall(
            type="function_call",
            arguments=request.arguments,
            name=request.name,
            call_id=request.call_id,
            status=request.status,
            parsed_arguments=object(),
        )
    else:
        setattr(request, "extra", {"nested": object()})  # noqa: B010

    def approve(_ctx: BrowserConfirmContext) -> bool:
        driver.events.append("approval")
        return True

    if kind == "invalid-extra":
        with pytest.raises((TypeError, ValueError)):
            await execute(lane, driver, request, approve, lambda _ctx, _url: True)
        assert not driver.events and not driver.clicked
    else:
        returned = await execute(lane, driver, request, approve, lambda _ctx, _url: True)
        assert returned.get("call_id") == request.call_id and payload(returned)["ok"]
        assert driver.events == ["state", "approval", "state"] and driver.clicked == ["button"]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("observed", [False, True], ids=["legacy", "v1"])
async def test_approval_snapshots_keep_native_state_strings(lane: str, observed: bool) -> None:
    class NativeString(str):
        @override
        def __str__(self) -> str:
            return "Changed by str override"

        def __deepcopy__(self, _memo: dict[int, object]) -> str:
            return "Changed during copy"

    class WithNativeStrings(Desktop):
        @override
        def state(self) -> BrowserState:
            value: BrowserState = {
                "tabs": [
                    {
                        "id": NativeString("one"),
                        "title": NativeString('Native "title" ☀'),
                        "url": NativeString("about:blank"),
                        "active": True,
                    }
                ]
            }
            if observed:
                value["observation"] = {
                    "version": 1,
                    "sequence": 4,
                    "dropped_changes": 0,
                    "title_truncated": False,
                    "changes": [
                        {"type": "navigation", "tab_id": NativeString("one"), "sequence": 1},
                        {"type": "navigation_refused", "tab_id": None, "sequence": 2, "reason": "policy"},
                        {"type": "download", "tab_id": NativeString("one"), "sequence": 3, "status": "blocked"},
                        {"type": "dialog_dismissed", "tab_id": NativeString("one"), "sequence": 4, "kind": "alert"},
                    ],
                }
                # Literal notice fields admit the same native string contents.
                for change in value["observation"]["changes"]:
                    change["type"] = cast(Any, NativeString(change["type"]))
                    for name in ("reason", "status", "kind"):
                        if name in change:
                            raw = cast(dict[str, str], change)
                            raw[name] = NativeString(raw[name])
            return value

    desktop = WithNativeStrings()
    native = json.loads(json.dumps(desktop.state(), ensure_ascii=True))
    snapshots: list[dict[str, object]] = []

    def consent(ctx: BrowserConfirmContext, url: str | None = None) -> bool:
        snapshot = json.loads(json.dumps(ctx, ensure_ascii=True))
        snapshots.append(snapshot)
        assert snapshot["state"] == native
        assert snapshot["arguments"] == {"url": "https://allowed.example/tasks", "tab_id": "one"}
        if url is not None:
            assert url == "https://allowed.example/tasks"
        ctx["arguments"].clear()
        ctx["state"]["tabs"].clear()
        return True

    result = payload(
        await execute(
            lane, desktop, call("navigate", {"url": "https://allowed.example/tasks", "tab_id": "one"}), consent, consent
        )
    )
    assert len(snapshots) == 2
    assert result["ok"] is True and result["state"] == native
    assert desktop.url == "https://allowed.example/tasks"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("opaque", [False, True], ids=["nested-json", "nonserializable"])
async def test_only_declared_tab_fields_cross_confirmation_and_output(lane: str, opaque: bool) -> None:
    class DriverTab(BrowserTab):
        internal: dict[str, object]

    class WithMetadata(Desktop):
        def __init__(self) -> None:
            super().__init__()
            self.reports: list[BrowserState] = []

        @override
        def state(self) -> BrowserState:
            internal: dict[str, object] = {"nested": {"marker": "SYNTHETIC_PRIVATE", "labels": ["session"]}}
            if opaque:
                internal["handle"] = object()
            tab: DriverTab = {
                "id": "one",
                "title": "After" if self.clicked else "Before",
                "url": self.url,
                "active": True,
                "internal": internal,
            }
            value: BrowserState = {"tabs": [tab]}
            self.reports.append(value)
            return value

    desktop = WithMetadata()
    confirmations: list[BrowserState] = []

    def confirm(ctx: BrowserConfirmContext) -> bool:
        confirmations.append(ctx["state"])
        # This local change must reach neither the driver nor subsequent model output.
        ctx["state"]["tabs"][0]["title"] = "Confirmation-local"
        return True

    first = payload(
        await execute(
            lane, desktop, call("click", {"target": "button", "tab_id": "one"}), confirm, lambda _ctx, _url: True
        )
    )
    listing = payload(await execute(lane, desktop, call("list_tabs", {}), confirm, lambda _ctx, _url: True))
    expected: BrowserState = {
        "tabs": [{"id": "one", "title": "After", "url": "https://allowed.example", "active": True}]
    }
    assert first == listing == {"ok": True, "state": expected, "result": None}
    assert confirmations == [
        {"tabs": [{"id": "one", "title": "Confirmation-local", "url": "https://allowed.example", "active": True}]}
    ]
    assert desktop.clicked == ["button"]
    assert [report["tabs"][0]["title"] for report in desktop.reports] == ["Before", "After", "After", "After"]


valid_observation: dict[str, object] = {
    "version": 1,
    "sequence": 0,
    "dropped_changes": 0,
    "title_truncated": False,
    "changes": [],
}


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "case,observation",
    [
        ("null", None),
        ("wrong_version", {**valid_observation, "version": 2}),
        ("bool_version", {**valid_observation, "version": True}),
        ("negative_sequence", {**valid_observation, "sequence": -1}),
        ("bool_sequence", {**valid_observation, "sequence": False}),
        ("unsafe_sequence", {**valid_observation, "sequence": 9007199254740992, "dropped_changes": 9007199254740992}),
        ("negative_dropped", {**valid_observation, "dropped_changes": -1}),
        ("bool_dropped", {**valid_observation, "dropped_changes": False}),
        ("numeric_truncation", {**valid_observation, "title_truncated": 1}),
        ("fraction_sequence", {**valid_observation, "sequence": 0.5}),
        ("not_a_list", {**valid_observation, "changes": {}}),
        (
            "late_event_gap",
            {
                **valid_observation,
                "sequence": 33,
                "changes": [{"type": "navigation", "tab_id": "one", "sequence": min(i, 32)} for i in range(1, 34)],
            },
        ),
        (
            "counter_gap",
            {**valid_observation, "sequence": 2, "changes": [{"type": "navigation", "tab_id": "one", "sequence": 2}]},
        ),
        (
            "event_gap",
            {**valid_observation, "sequence": 1, "changes": [{"type": "navigation", "tab_id": "one", "sequence": 2}]},
        ),
        (
            "event_bool",
            {
                **valid_observation,
                "sequence": 1,
                "changes": [{"type": "navigation", "tab_id": "one", "sequence": True}],
            },
        ),
        (
            "unknown_event",
            {**valid_observation, "sequence": 1, "changes": [{"type": "login", "tab_id": "one", "sequence": 1}]},
        ),
        (
            "null_required_tab",
            {**valid_observation, "sequence": 1, "changes": [{"type": "navigation", "tab_id": None, "sequence": 1}]},
        ),
        (
            "bad_reason",
            {
                **valid_observation,
                "sequence": 1,
                "changes": [
                    {"type": "navigation_refused", "tab_id": None, "reason": "SYNTHETIC_PRIVATE", "sequence": 1}
                ],
            },
        ),
        (
            "bad_dialog",
            {
                **valid_observation,
                "sequence": 1,
                "changes": [{"type": "dialog_dismissed", "tab_id": "one", "kind": "SYNTHETIC_PRIVATE", "sequence": 1}],
            },
        ),
        (
            "bad_download",
            {
                **valid_observation,
                "sequence": 1,
                "changes": [{"type": "download", "tab_id": None, "status": "SYNTHETIC_PRIVATE", "sequence": 1}],
            },
        ),
        (
            "blank_tab",
            {**valid_observation, "sequence": 1, "changes": [{"type": "tab_closed", "tab_id": "", "sequence": 1}]},
        ),
        (
            "long_event_id",
            {
                **valid_observation,
                "sequence": 1,
                "changes": [{"type": "navigation", "tab_id": "𐍈" * 32 + "x", "sequence": 1}],
            },
        ),
        *[(f"missing_{key}", {k: v for k, v in valid_observation.items() if k != key}) for key in valid_observation],
    ],
)
async def test_malformed_observation_refuses_before_effect(lane: str, case: str, observation: object) -> None:
    class Reported(Desktop):
        @override
        def state(self) -> BrowserState:
            value = super().state()
            # A customer driver's returned value need not obey its annotation.
            value["observation"] = cast(BrowserObservationV1, observation)
            return value

    desktop = Reported()
    with pytest.raises(RuntimeError, match=r"^Browser state report failed\.$"):
        await execute(
            lane,
            desktop,
            call("click", {"target": "button", "tab_id": None}),
            lambda _ctx: True,
            lambda _ctx, _url: True,
        )
    assert not desktop.clicked, case


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("at", [1, 2])
@pytest.mark.parametrize("counter", [float("nan"), float("inf"), -float("inf")])
async def test_nonfinite_observation_stops_at_the_actual_read(lane: str, at: int, counter: float) -> None:
    class Reported(Desktop):
        def __init__(self) -> None:
            super().__init__()
            self.reads = 0

        @override
        def state(self) -> BrowserState:
            self.reads += 1
            value = super().state()
            # A driver can violate its annotation at runtime; never send it to the model.
            value["observation"] = cast(
                BrowserObservationV1,
                {
                    "version": 1,
                    "sequence": counter if self.reads == at else 0,
                    "dropped_changes": 0,
                    "title_truncated": False,
                    "changes": [],
                },
            )
            return value

    desktop = Reported()
    with pytest.raises(RuntimeError, match=r"^Browser state report failed\.$"):
        await execute(
            lane,
            desktop,
            call("click", {"target": "button", "tab_id": None}),
            lambda _ctx: True,
            lambda _ctx, _url: True,
        )
    assert desktop.reads == at
    assert desktop.clicked == ([] if at == 1 else ["button"])


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_denied_navigation_precedes_confirmation(lane: str) -> None:
    desktop = Desktop()

    def confirm(_ctx: BrowserConfirmContext) -> bool:
        pytest.fail("confirmation must not run after denied URL policy")

    result = await execute(
        lane, desktop, call("navigate", {"url": "file:///private", "tab_id": None}), confirm, lambda _ctx, _url: False
    )
    assert payload(result)["ok"] is False
    assert desktop.url == "https://allowed.example/"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("phase", ["state", "url_policy"])
async def test_active_execution_keeps_original_state_and_policy_callbacks(
    lane: str, phase: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    desktop = Desktop()
    driver = desktop if lane == "sync" else AsyncDesktop(desktop)
    original_state = desktop.state

    def next_state() -> BrowserState:
        value = original_state()
        value["tabs"][0]["title"] = "Next execution"
        return value

    async def async_next_state() -> BrowserState:
        return next_state()

    def allow(_ctx: BrowserConfirmContext) -> bool:
        return True

    async def async_allow(_ctx: BrowserConfirmContext) -> bool:
        return True

    def allow_url(_ctx: BrowserConfirmContext, _url: str) -> bool:
        return True

    async def async_allow_url(_ctx: BrowserConfirmContext, _url: str) -> bool:
        return True

    def mutate() -> None:
        monkeypatch.setattr(driver, "state", next_state if lane == "sync" else async_next_state)
        monkeypatch.setattr(browser, "confirm", allow if lane == "sync" else async_allow)
        monkeypatch.setattr(browser, "url_policy", allow_url if lane == "sync" else async_allow_url)

    def read_state() -> BrowserState:
        if phase == "state":
            mutate()
        return original_state()

    async def async_read_state() -> BrowserState:
        state = read_state()
        await asyncio.sleep(0)
        return state

    def refuse(_ctx: BrowserConfirmContext) -> bool:
        return False

    async def async_refuse(_ctx: BrowserConfirmContext) -> bool:
        return False

    def policy(_ctx: BrowserConfirmContext, _url: str) -> bool:
        if phase == "url_policy":
            mutate()
            return True
        return False

    async def async_policy(ctx: BrowserConfirmContext, url: str) -> bool:
        approved = policy(ctx, url)
        await asyncio.sleep(0)
        return approved

    monkeypatch.setattr(driver, "state", read_state if lane == "sync" else async_read_state)
    browser = (
        BrowserToolset(desktop, confirm=refuse, url_policy=policy)
        if lane == "sync"
        else AsyncBrowserToolset(cast(AsyncDesktop, driver), confirm=async_refuse, url_policy=async_policy)
    )
    request = call("navigate", {"url": "https://allowed.example/tasks", "tab_id": None})
    if isinstance(browser, AsyncBrowserToolset):
        first = await browser.execute(request)
    else:
        first = browser.execute(request)
    outcome = payload(first)
    assert outcome["ok"] is False
    assert outcome["error"] == (
        "Browser navigation was not approved."
        if phase == "state"
        else "Browser action was not approved. Do not retry it unless the user asks."
    )
    assert desktop.url == "https://allowed.example/"
    assert outcome["state"] == reported_state()

    # The owner may replace callbacks between calls. Only the active call kept the old references.
    if isinstance(browser, AsyncBrowserToolset):
        second = await browser.execute(request)
    else:
        second = browser.execute(request)
    assert payload(second) == {"ok": True, "state": reported_state("Next execution"), "result": None}
    assert desktop.url == "https://allowed.example/tasks"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "args",
    [
        {"target": "button"},
        {"target": "button", "tab_id": None, "javascript": "anything"},
        {"target": 7, "tab_id": None},
        {"target": "button", "tab_id": ["one"]},
    ],
)
async def test_invalid_input_never_reaches_driver(lane: str, args: dict[str, object]) -> None:
    desktop = Desktop()
    result = await execute(lane, desktop, call("click", args), lambda _: True, lambda _ctx, _url: True)
    assert payload(result)["ok"] is False
    assert desktop.clicked == []


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_refusal_error_and_image_output(lane: str) -> None:
    desktop = Desktop()
    denied = await execute(
        lane, desktop, call("click", {"target": "button", "tab_id": None}), lambda _: False, lambda _ctx, _url: True
    )
    assert payload(denied)["ok"] is False and desktop.clicked == []
    private = await execute(
        lane, desktop, call("click", {"target": "private", "tab_id": None}), lambda _: True, lambda _ctx, _url: True
    )
    assert payload(private)["error"] == "Browser action failed."
    missing = await execute(
        lane, desktop, call("click", {"target": "missing", "tab_id": None}), lambda _: True, lambda _ctx, _url: True
    )
    assert payload(missing)["error"] == "Element is no longer on the page."
    picture = await execute(
        lane, desktop, call("screenshot", {"tab_id": "one"}), lambda _: True, lambda _ctx, _url: True
    )
    content = picture["output"]
    assert isinstance(content, list)
    assert content[1] == {"type": "input_image", "image_url": "data:image/png;base64,cG5n"}
    assert picture.get("call_id") == "call_one"


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_mutation_confirmation_does_not_deny_reads(lane: str) -> None:
    desktop = Desktop()
    decisions: list[str] = []

    def refuse_change(ctx: BrowserConfirmContext) -> bool:
        decisions.append(ctx["member"])
        return False

    text = await execute(lane, desktop, call("get_page_text", {"tab_id": None}), refuse_change, lambda _ctx, _url: True)
    tabs = await execute(lane, desktop, call("list_tabs", {}), refuse_change, lambda _ctx, _url: True)
    picture = await execute(lane, desktop, call("screenshot", {"tab_id": None}), refuse_change, lambda _ctx, _url: True)
    denied = await execute(
        lane, desktop, call("click", {"target": "button", "tab_id": None}), refuse_change, lambda _ctx, _url: True
    )

    assert payload(text)["result"] == "Local page content"
    assert payload(tabs)["state"] == reported_state()
    content = picture["output"]
    assert isinstance(content, list) and content[1]["type"] == "input_image"
    assert payload(denied)["ok"] is False
    assert decisions == ["click"]
    assert desktop.clicked == []


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_unneeded_policy_accessors_are_not_read_and_required_ones_fail_safely(
    lane: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    desktop = Desktop()

    async def confirm(_ctx: BrowserConfirmContext) -> bool:
        return True

    browser = (
        BrowserToolset(desktop, members=["click", "get_page_text"], confirm=lambda _ctx: True)
        if lane == "sync"
        else AsyncBrowserToolset(AsyncDesktop(desktop), members=["click", "get_page_text"], confirm=confirm)
    )

    def unavailable(_self: object) -> None:
        raise ValueError("private policy configuration")

    monkeypatch.setattr(type(browser), "confirm", property(unavailable), raising=False)
    monkeypatch.setattr(type(browser), "url_policy", property(unavailable), raising=False)
    read = call("get_page_text", {"tab_id": None})
    write = call("click", {"target": "button", "tab_id": None})
    if isinstance(browser, AsyncBrowserToolset):
        assert payload(await browser.execute(read))["result"] == "Local page content"
        with pytest.raises(RuntimeError, match=r"^Browser policy lookup failed\.$"):
            await browser.execute(write)
    else:
        assert payload(browser.execute(read))["result"] == "Local page content"
        with pytest.raises(RuntimeError, match=r"^Browser policy lookup failed\.$"):
            browser.execute(write)
    assert desktop.clicked == []


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_removed_confirmation_cannot_authorize_mutation(lane: str) -> None:
    desktop = Desktop()
    click = call("click", {"target": "button", "tab_id": None})
    listing = call("list_tabs", {})
    if lane == "sync":
        browser = BrowserToolset(desktop, confirm=lambda _: True, url_policy=lambda _ctx, _url: True)
        browser.confirm = None
        tabs, denied = browser.execute(listing), browser.execute(click)
    else:

        async def confirm(_ctx: BrowserConfirmContext) -> bool:
            return True

        async def policy(_ctx: BrowserConfirmContext, _url: str) -> bool:
            return True

        async_browser = AsyncBrowserToolset(AsyncDesktop(desktop), confirm=confirm, url_policy=policy)
        async_browser.confirm = None
        tabs, denied = await async_browser.execute(listing), await async_browser.execute(click)
    assert payload(tabs)["state"] == reported_state()
    assert payload(denied)["ok"] is False
    assert desktop.clicked == []


def test_partial_driver_and_required_policies() -> None:
    class ReadOnly:
        def state(self) -> BrowserState:
            return {"tabs": []}

    browser = BrowserToolset(ReadOnly())
    assert [tool["name"] for tool in browser.tools] == ["browser_list_tabs"]
    assert payload(browser.execute(call("click", {"target": "a", "tab_id": None})))["ok"] is False
    with pytest.raises(ValueError, match="confirm"):
        BrowserToolset(Desktop())
    with pytest.raises(ValueError, match="url_policy"):
        BrowserToolset(Desktop(), confirm=lambda _: True)


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_broken_state_is_not_sent_to_model(lane: str) -> None:
    class Broken(Desktop):
        @override
        def state(self) -> BrowserState:
            raise BrowserError("private data from a page")

    with pytest.raises(RuntimeError, match="Browser state report failed"):
        await execute(lane, Broken(), call("list_tabs", {}), lambda _: True, lambda _ctx, _url: True)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("failure", ["access", "invalid"])
async def test_invalid_state_reader_fails_without_exposing_data_or_acting(
    lane: str, failure: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    desktop = Desktop()
    driver = desktop if lane == "sync" else AsyncDesktop(desktop)

    def read_state() -> BrowserState:
        return cast(BrowserState, {"tabs": [{"private data from a page": "not a tab"}]})

    async def async_read_state() -> BrowserState:
        return read_state()

    def unavailable(_self: object) -> None:
        raise BrowserError("private data from a page")

    if failure == "access":
        monkeypatch.setattr(type(driver), "state", property(unavailable))
    else:
        monkeypatch.setattr(driver, "state", read_state if lane == "sync" else async_read_state)

    async def confirm(_ctx: BrowserConfirmContext) -> bool:
        return True

    browser = (
        BrowserToolset(desktop, members=["click"], confirm=lambda _ctx: True)
        if lane == "sync"
        else AsyncBrowserToolset(cast(AsyncDesktop, driver), members=["click"], confirm=confirm)
    )
    request = call("click", {"target": "button", "tab_id": None})
    with pytest.raises(RuntimeError, match=r"^Browser state report failed\.$") as exc:
        if isinstance(browser, AsyncBrowserToolset):
            await browser.execute(request)
        else:
            browser.execute(request)
    assert "private data" not in str(exc.value)
    assert desktop.clicked == []


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_invalid_image_source_cannot_hide_behind_a_valid_file(lane: str) -> None:
    class Broken(Desktop):
        @override
        def screenshot(self, action: TabInput) -> ResponseInputImageContentParam:
            assert action["tab_id"] is None
            return cast(ResponseInputImageContentParam, {"type": "input_image", "image_url": 123, "file_id": "file"})

    with pytest.raises(RuntimeError, match="at least one"):
        await execute(lane, Broken(), call("screenshot", {"tab_id": None}), lambda _: True, lambda _ctx, _url: True)


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_screenshot_is_detached_before_final_state(lane: str) -> None:
    class MutableScreenshot(Desktop):
        def __init__(self) -> None:
            super().__init__()
            self.image: ResponseInputImageContentParam = {
                "type": "input_image",
                "image_url": "data:image/png;base64,b3JpZ2luYWw=",
            }
            self.captured = False

        @override
        def screenshot(self, action: TabInput) -> ResponseInputImageContentParam:
            self.captured = True
            return self.image

        @override
        def state(self) -> BrowserState:
            if self.captured:
                self.image["image_url"] = "data:image/png;base64,Y2hhbmdlZA=="
            return super().state()

    desktop = MutableScreenshot()
    result = await execute(lane, desktop, call("screenshot", {"tab_id": None}), lambda _: True, lambda _ctx, _url: True)
    expected = {"type": "input_image", "image_url": "data:image/png;base64,b3JpZ2luYWw="}
    assert isinstance(result["output"], list)
    assert result["output"][1] == expected
    cast(dict[str, object], desktop.image).clear()
    assert result["output"][1] == expected


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", ["screenshot", "zoom"])
async def test_image_breakpoint_is_detached_and_blank_or_invalid_image_is_rejected(lane: str, member: str) -> None:
    class ImageDriver(Desktop):
        def __init__(self) -> None:
            super().__init__()
            self.image: ResponseInputImageContentParam = {
                "type": "input_image",
                "file_id": "file_observed",
                "image_url": "data:image/png;base64,b3JpZ2luYWw=",
                "prompt_cache_breakpoint": {"mode": "explicit"},
            }
            self.captured = False

        @override
        def screenshot(self, action: TabInput) -> ResponseInputImageContentParam:
            self.captured = True
            return self.image

        @override
        def zoom(self, action: ZoomInput) -> ResponseInputImageContentParam:
            self.captured = True
            return self.image

        @override
        def state(self) -> BrowserState:
            if self.captured:
                point = self.image.get("prompt_cache_breakpoint")
                if point is not None:
                    cast(dict[str, object], point)["mode"] = "changed"
            return super().state()

    args = {"tab_id": None} if member == "screenshot" else {"tab_id": None, "region": [0, 0, 10, 10]}
    desktop = ImageDriver()
    expected = deepcopy(desktop.image)
    result = await execute(lane, desktop, call(member, args), lambda _: True, lambda _ctx, _url: True)
    assert isinstance(result["output"], list) and result["output"][1] == expected
    for invalid in (
        {"type": "input_image", "image_url": "  "},
        {"type": "input_image", "image_url": " ", "file_id": "file_ok"},
        {"type": "input_image", "image_url": "data:image/png;base64,YQ==", "file_id": ""},
        {"type": "input_image", "file_id": "file_ok", "prompt_cache_breakpoint": {"mode": "automatic"}},
        {"type": "input_image", "file_id": "file_ok", "prompt_cache_breakpoint": {"mode": "explicit", "extra": "x"}},
    ):
        desktop = ImageDriver()
        desktop.image = cast(ResponseInputImageContentParam, invalid)
        with pytest.raises(RuntimeError, match="input_image"):
            await execute(lane, desktop, call(member, args), lambda _: True, lambda _ctx, _url: True)


class RichReads:
    def __init__(self, result: object) -> None:
        self.result = result
        self.reads = 0
        self.after: Callable[[], None] = lambda: None
        self.invalid_final = False

    def state(self) -> BrowserState:
        self.reads += 1
        if self.reads == 2:
            self.after()
            if self.invalid_final:
                return cast(BrowserState, {"tabs": "bad"})
        return {"tabs": []}

    def read_page(self, _args: object) -> object:
        return self.result

    def find(self, _args: object) -> object:
        return self.result

    def get_page_text(self, _args: object) -> object:
        return self.result

    def click(self, _args: object) -> object:
        return self.result


class AsyncRichReads:
    def __init__(self, driver: RichReads) -> None:
        self.driver = driver
        self.held = asyncio.Event()
        self.release = asyncio.Event()
        self.hold_final = False

    async def state(self) -> BrowserState:
        if self.hold_final and self.driver.reads == 1:
            self.held.set()
            await self.release.wait()
        return self.driver.state()

    async def read_page(self, _args: object) -> object:
        return self.driver.result

    async def find(self, _args: object) -> object:
        return self.driver.result

    async def get_page_text(self, _args: object) -> object:
        return self.driver.result

    async def click(self, _args: object) -> object:
        return self.driver.result


def read_args(member: str) -> dict[str, object]:
    args: dict[str, object] = {"tab_id": None}
    if member == "read_page":
        args["filter"] = "all"
    elif member == "find":
        args["query"] = "Zoë"
    elif member == "click":
        args["target"] = "opaque-ref"
    return args


def read_report() -> dict[str, Any]:
    return {
        "version": 1,
        "text": 'Remote: "quoted" résumé 😀',
        "elements": [
            {
                "ref": "opaque-ref",
                "role": "combobox",
                "label": "Zoë",
                "value": "",
                "options": [{"label": "Keep", "value": "k"}, {"label": "Remove", "value": "r"}],
            }
        ],
        "omitted": ["remote_action", "private"],
    }


async def execute_read(lane: str, driver: RichReads, member: str) -> FunctionCallOutput:
    request = call(member, read_args(member))
    if lane == "sync":
        return BrowserToolset(driver, members=[member], confirm=lambda _: True).execute(request)

    async def confirm(_ctx: BrowserConfirmContext) -> bool:
        return True

    return await AsyncBrowserToolset(AsyncRichReads(driver), members=[member], confirm=confirm).execute(request)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("count", [101, 1000])
async def test_v1_driver_selected_collection_sizes(lane: str, count: int) -> None:
    report = read_report()
    elements: list[dict[str, object]] = [{"ref": str(n), "role": "button", "label": "Select"} for n in range(count)]
    elements[-1] = {
        "ref": "choices",
        "role": "listbox",
        "label": "Choices",
        "options": [{"label": str(n), "value": str(n), "selected": n == 32} for n in range(33)],
    }
    report["elements"] = elements
    assert payload(await execute_read(lane, RichReads(report), "read_page"))["result"] == report


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("transition", ["sequence", "dropped_changes", "downgrade"])
async def test_invalid_observation_transition_refuses_final_read(lane: str, transition: str) -> None:
    class Observed(RichReads):
        @override
        def state(self) -> BrowserState:
            self.reads += 1
            value: dict[str, object] = {"tabs": []}
            if transition == "sequence":
                sequence = 2 if self.reads == 1 else 1
                value["observation"] = {
                    **valid_observation,
                    "sequence": sequence,
                    "changes": [{"type": "navigation", "tab_id": "one", "sequence": n} for n in range(1, sequence + 1)],
                }
            elif self.reads == 1:
                value["observation"] = {**valid_observation, "sequence": 2, "dropped_changes": 2}
            elif transition == "dropped_changes":
                value["observation"] = {
                    **valid_observation,
                    "sequence": 3,
                    "dropped_changes": 1,
                    "changes": [{"type": "navigation", "tab_id": "one", "sequence": n} for n in (2, 3)],
                }
            return cast(BrowserState, value)

    driver = Observed("read")
    with pytest.raises(RuntimeError, match="Browser state"):
        await execute_read(lane, driver, "read_page")
    assert driver.reads == 2


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("rewrite", [False, True])
async def test_observation_overlap_drop_append(lane: str, rewrite: bool) -> None:
    class Observed(RichReads):
        @override
        def state(self) -> BrowserState:
            self.reads += 1
            changes: list[dict[str, object]] = [
                {"type": "navigation", "tab_id": "one", "sequence": n} for n in range(1, 4)
            ]
            dropped = 0
            if self.reads > 1:
                dropped = 1
                changes = changes[1:] + [{"type": "navigation", "tab_id": "one", "sequence": 4}]
                if rewrite:
                    changes[0] = {"type": "download", "tab_id": "one", "sequence": 2, "status": "blocked"}
            return cast(
                BrowserState,
                {
                    "tabs": [],
                    "observation": {
                        "version": 1,
                        "sequence": dropped + len(changes),
                        "dropped_changes": dropped,
                        "title_truncated": False,
                        "changes": changes,
                    },
                },
            )

    driver = Observed("ordinary read")
    if rewrite:
        with pytest.raises(RuntimeError, match="Browser state"):
            await execute_read(lane, driver, "read_page")
    else:
        output = payload(await execute_read(lane, driver, "read_page"))
        observed = cast(BrowserState, output["state"]).get("observation")
        assert observed is not None
        assert [event["sequence"] for event in observed["changes"]] == [2, 3, 4]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "url,expected",
    [
        ("data:text/plain,SYNTHETIC_PRIVATE", "data:"),
        ("file:///sandbox/SYNTHETIC_PRIVATE.txt", "file:"),
        ("blob:https://fixture.invalid/SYNTHETIC_PRIVATE", "blob:"),
        ("mailto:SYNTHETIC_PRIVATE@fixture.invalid", "mailto:"),
        ("about:blank", "about:blank"),
    ],
)
async def test_legacy_tab_state_removes_payload_urls(lane: str, url: str, expected: str) -> None:
    class Driver(RichReads):
        @override
        def state(self) -> BrowserState:
            return {"tabs": [{"id": "tab", "title": "Fixture", "url": url, "active": True}]}

    result = payload(await execute_read(lane, Driver("Fixture"), "read_page"))
    assert result["state"] == {"tabs": [{"id": "tab", "title": "Fixture", "url": expected, "active": True}]}
    assert "SYNTHETIC_PRIVATE" not in str(result)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "title,expected,truncated,already_truncated",
    [
        ("a" * 1025, "a" * 1024, True, False),
        ("é" * 513, "é" * 512, True, False),
        ("😀" * 257, "😀" * 256, True, False),
        ("é" * 512, "é" * 512, False, False),
        ("Short", "Short", True, True),
    ],
    ids=["ascii", "multibyte", "emoji", "exact-boundary", "already-truncated"],
)
async def test_observed_long_title_is_projected(
    lane: str, title: str, expected: str, truncated: bool, already_truncated: bool
) -> None:
    observation: BrowserObservationV1 = {
        "version": 1,
        "sequence": 0,
        "dropped_changes": 0,
        "title_truncated": already_truncated,
        "changes": [],
    }

    class Driver(RichReads):
        @override
        def state(self) -> BrowserState:
            return {
                "tabs": [{"id": "one", "title": title, "url": "https://fixture.invalid/", "active": True}],
                "observation": observation,
            }

    result = payload(await execute_read(lane, Driver("Visible text"), "read_page"))
    state = cast(BrowserState, result["state"])
    assert state["tabs"][0]["title"] == expected
    assert "observation" in state
    assert state["observation"]["title_truncated"] is truncated
    assert observation["title_truncated"] is already_truncated


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_invalid_unicode_after_projected_title_is_rejected(lane: str) -> None:
    class Driver(RichReads):
        @override
        def state(self) -> BrowserState:
            return {
                "tabs": [
                    {"id": "one", "title": "a" * 2048 + "\ud800", "url": "https://fixture.invalid/", "active": True}
                ],
                "observation": {
                    "version": 1,
                    "sequence": 0,
                    "dropped_changes": 0,
                    "title_truncated": False,
                    "changes": [],
                },
            }

    with pytest.raises(RuntimeError, match="Browser state"):
        await execute_read(lane, Driver("Visible text"), "read_page")


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("observed", [False, True])
async def test_101_reported_tabs_work_with_or_without_observation(lane: str, observed: bool) -> None:
    reported_state: BrowserState = {
        "tabs": [
            {"id": str(index), "title": "Fixture", "url": "https://fixture.invalid/", "active": index == 0}
            for index in range(101)
        ]
    }
    if observed:
        reported_state["observation"] = {
            "version": 1,
            "sequence": 0,
            "dropped_changes": 0,
            "title_truncated": False,
            "changes": [],
        }

    class Driver(RichReads):
        @override
        def state(self) -> BrowserState:
            return reported_state

    result = payload(await execute_read(lane, Driver("Fixture"), "read_page"))
    expected_state: BrowserState = {
        "tabs": [
            {
                "id": str(index),
                "title": "Fixture",
                "url": "https://fixture.invalid",
                "active": index == 0,
            }
            for index in range(101)
        ]
    }
    if observed:
        expected_state["observation"] = {
            "version": 1,
            "sequence": 0,
            "dropped_changes": 0,
            "title_truncated": False,
            "changes": [],
        }
    assert result["state"] == expected_state


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("count", [33, 1024])
async def test_observation_projects_all_driver_retained_events(lane: str, count: int) -> None:
    changes = [
        {"type": "navigation", "tab_id": "one", "sequence": index + 8, "private": "SYNTHETIC_PRIVATE"}
        for index in range(count)
    ]

    class Driver(RichReads):
        @override
        def state(self) -> BrowserState:
            return {
                **super().state(),
                "observation": {
                    "version": 1,
                    "sequence": count + 7,
                    "dropped_changes": 7,
                    "title_truncated": False,
                    "changes": cast(Any, changes),
                },
            }

    result = payload(await execute_read(lane, Driver("Fixture"), "read_page"))
    projected = cast(dict[str, Any], result["state"])["observation"]
    assert projected == {
        "version": 1,
        "sequence": count + 7,
        "dropped_changes": 7,
        "title_truncated": False,
        "changes": [{"type": "navigation", "tab_id": "one", "sequence": index + 8} for index in range(count)],
    }


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_form_read_state_is_detached_and_original_roles_still_ignore_private_fields(lane: str) -> None:
    report = read_report()
    elements: list[dict[str, Any]] = [
        {"ref": "c", "role": "checkbox", "label": "Include", "checked": True},
        {"ref": "r", "role": "radio", "label": "Standard", "checked": False},
        {"ref": "s", "role": "slider", "label": "Quantity", "value": "40"},
        {
            "ref": "m",
            "role": "listbox",
            "label": "Tags",
            "options": [
                {"label": "One", "value": "1", "selected": True},
                {"label": "Two", "value": "2", "selected": False},
            ],
        },
    ]
    report["elements"] = elements
    expected = deepcopy(report)
    for role in ("button", "textbox", "combobox"):
        legacy: dict[str, Any] = {"ref": role, "role": role, "label": role, "options": [{"label": "Old", "value": "v"}]}
        expected["elements"].append(deepcopy(legacy))
        legacy["checked"] = object()
        legacy["options"][0]["selected"] = object()
        report["elements"].append(legacy)
    driver = RichReads(report)

    def mutate_at_final_state() -> None:
        report["elements"][0]["checked"] = False
        report["elements"][3]["options"][0]["selected"] = False

    driver.after = mutate_at_final_state
    assert payload(await execute_read(lane, driver, "find"))["result"] == expected


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "role,field,bad",
    [
        ("checkbox", "checked", 1),
        ("radio", "checked", "false"),
        ("checkbox", "checked", None),
        ("listbox", "selected", 0),
        ("listbox", "selected", {"private": "SYNTHETIC_PRIVATE"}),
    ],
)
async def test_new_form_state_invalid_bool_is_fatal_before_final_read(
    lane: str,
    role: str,
    field: str,
    bad: object,
) -> None:
    report = read_report()
    item: dict[str, Any] = {"ref": "form", "role": role, "label": "Form"}
    if field == "selected":
        item["options"] = [{"label": "One", "value": "v", "selected": bad}]
    else:
        item[field] = bad
    report["elements"] = [item]
    driver = RichReads(report)
    with pytest.raises(RuntimeError, match=r"^Browser read report failed\.$"):
        await execute_read(lane, driver, "read_page")
    assert driver.reads == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_form_state_survives_reports_beyond_64_kib(lane: str) -> None:
    report = read_report()
    report["text"] = ""
    report["elements"] = [
        {
            "ref": str(i),
            "role": "listbox",
            "label": "Labels",
            "options": [{"label": "Choice", "value": "x" * 280, "selected": j % 2 == 0} for j in range(12)],
        }
        for i in range(14)
    ]
    size = len(json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode())
    assert 0 <= 65_536 - size <= 16_384
    report["text"] = "a" * (65_536 - size)
    assert payload(await execute_read(lane, RichReads(report), "read_page"))["result"] == report
    report["text"] += "a"
    driver = RichReads(report)
    assert payload(await execute_read(lane, driver, "read_page"))["result"] == report
    assert driver.reads == 2


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", ["read_page", "find", "get_page_text"])
async def test_rich_read_projects_only_known_fields_and_snapshots_before_final_state(lane: str, member: str) -> None:
    report = read_report()
    if member == "get_page_text":
        report["elements"] = []
    expected = deepcopy(report)
    report["internal"] = object()
    if report["elements"]:
        report["elements"][0]["private"] = object()
        report["elements"][0]["options"][0]["private"] = object()
    driver = RichReads(report)

    def mutate() -> None:
        report["text"] = "SECRET_AFTER"
        report["omitted"].clear()
        if report["elements"]:
            report["elements"][0]["options"][0]["label"] = "SECRET_AFTER"
            report["elements"][0]["ref"] = "SECRET_AFTER"

    driver.after = mutate
    result = await execute_read(lane, driver, member)
    assert payload(result) == {"ok": True, "state": {"tabs": []}, "result": expected}
    assert driver.reads == 2
    assert "SECRET_AFTER" not in str(result)


async def test_rich_read_copies_before_async_final_state_yields() -> None:
    report = read_report()
    expected = deepcopy(report)
    driver = RichReads(report)
    async_driver = AsyncRichReads(driver)
    async_driver.hold_final = True
    browser = AsyncBrowserToolset(async_driver, members=["find"])
    task = asyncio.create_task(browser.execute(call("find", read_args("find"))))
    await asyncio.wait_for(async_driver.held.wait(), 2)
    report["elements"][0]["label"] = "SECRET_DURING_WAIT"
    report["elements"][0]["options"].clear()
    async_driver.release.set()
    result = await task
    assert payload(result)["result"] == expected
    assert "SECRET_DURING_WAIT" not in str(result)


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_rich_read_snapshots_before_post_handler_cancellation_callback(lane: str) -> None:
    report = read_report()
    expected = deepcopy(report)

    class Issuing(RichReads):
        issued = False

        @override
        def find(self, _args: object) -> object:
            self.issued = True
            return self.result

    class AsyncIssuing(AsyncRichReads):
        @override
        async def find(self, args: object) -> object:
            return self.driver.find(args)

    driver = Issuing(report)

    def cancelled() -> bool:
        if driver.issued:
            report["text"] = "SECRET_IN_CALLBACK"
            report["elements"][0]["options"].clear()
        return False

    request = call("find", read_args("find"))
    if lane == "sync":
        result = BrowserToolset(driver, members=["find"]).execute(request, cancelled=cancelled)
    else:
        result = await AsyncBrowserToolset(AsyncIssuing(driver), members=["find"]).execute(request, cancelled=cancelled)
    assert payload(result)["result"] == expected
    assert "SECRET_IN_CALLBACK" not in str(result)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("member", ["read_page", "find", "get_page_text"])
@pytest.mark.parametrize("legacy", [None, "", "page", '{"version":1,"elements":"invalid"}'])
async def test_rich_reads_keep_legacy_results_exact(lane: str, member: str, legacy: str | None) -> None:
    assert payload(await execute_read(lane, RichReads(legacy), member))["result"] == legacy


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "bad",
    [
        {"version": 2},
        {"version": True},
        {"text": "missing version"},
        {"text": "\ud800"},
        {"elements": [{"ref": "", "role": "button", "label": "Save"}]},
        {"elements": [{"ref": "x", "role": "textbox", "label": ""}]},
        {"elements": [{"ref": "x", "role": "link", "label": "unsupported"}]},
        {"elements": [{"ref": "x", "role": "button", "label": "b"}] * 2},
        {"elements": [{"ref": "x" * 257, "role": "textbox", "label": "n"}]},
        {"elements": [{"ref": "x", "role": "textbox", "label": "é" * 129}]},
        {"elements": [{"ref": "x", "role": "textbox", "label": "n", "value": "é" * 257}]},
        {"elements": [{"ref": "x", "role": "combobox", "label": "n", "options": [{"label": "", "value": "b"}]}]},
        {"elements": [{"ref": "x", "role": "textbox", "label": "n", "value": None}]},
        {"omitted": ["private", "private"]},
        {"omitted": ["unknown"]},
        {"omitted": [None]},
        {"omitted": "private"},
    ],
)
async def test_rich_read_invalid_report_is_fatal_before_final_state(lane: str, bad: dict[str, object]) -> None:
    report = read_report()
    report.update(bad)
    if "missing version" in str(bad):
        del report["version"]
    driver = RichReads(report)
    with pytest.raises(RuntimeError, match=r"^Browser read report failed\.$"):
        await execute_read(lane, driver, "read_page")
    assert driver.reads == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_rich_text_may_not_issue_refs_and_actions_do_not_accept_rich_results(lane: str) -> None:
    with pytest.raises(RuntimeError, match=r"^Browser read report failed\.$"):
        await execute_read(lane, RichReads(read_report()), "get_page_text")
    with pytest.raises(RuntimeError, match="Browser actions must return a string or None"):
        await execute_read(lane, RichReads(read_report()), "click")


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_rich_read_does_not_skip_final_state_validation(lane: str) -> None:
    driver = RichReads(read_report())
    driver.invalid_final = True
    with pytest.raises(RuntimeError, match=r"^Browser state report failed\.$"):
        await execute_read(lane, driver, "find")
    assert driver.reads == 2


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_rich_read_retains_large_unicode_and_escaped_text(lane: str) -> None:
    report = read_report()
    report["text"] = ""
    report["elements"] = [
        {
            "ref": str(n),
            "role": "combobox",
            "label": "Select",
            "options": [{"label": "Choice", "value": "😀" * 20 + '"' * 30} for _ in range(12)],
        }
        for n in range(30)
    ]
    size = len(json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode())
    assert 49_152 <= size < 65_536
    report["text"] = "a" * (65_536 - size)
    assert len(json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode()) == 65_536
    assert payload(await execute_read(lane, RichReads(report), "read_page"))["result"] == report
    report["text"] += "😀" * 100_000
    assert payload(await execute_read(lane, RichReads(report), "read_page"))["result"] == report


class MaskedReadText(str):
    @override
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return b"x"

    @override
    def __eq__(self, other: object) -> bool:
        return True

    __hash__ = str.__hash__


class ConcealedReadList(list[object]):
    @override
    def __len__(self) -> int:
        return 0


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("field", ["text", "role", "omitted", "option"])
async def test_v1_scalar_overrides_never_bypass_read_limits(lane: str, field: str) -> None:
    report = read_report()
    if field == "text":
        report["text"] = MaskedReadText("PRIVATE" * 3000)
    elif field == "role":
        report["elements"][0]["role"] = MaskedReadText("not-a-supported-role")
    elif field == "omitted":
        report["omitted"] = [MaskedReadText("not-an-omission")]
    else:
        report["elements"][0]["options"][0]["value"] = MaskedReadText("PRIVATE" * 90)
    driver = RichReads(report)
    with pytest.raises(RuntimeError, match=r"^Browser read report failed\.$"):
        await execute_read(lane, driver, "read_page")
    assert driver.reads == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("case", ["text-target", "many-targets", "many-options"])
async def test_v1_collection_length_overrides_cannot_hide_action_targets(lane: str, case: str) -> None:
    report = read_report()
    member = "read_page"
    if case == "text-target":
        report["elements"] = ConcealedReadList(report["elements"])
        member = "get_page_text"
    elif case == "many-targets":
        report["elements"] = ConcealedReadList({"ref": str(n), "role": "button", "label": "Select"} for n in range(101))
    else:
        report["elements"][0]["options"] = ConcealedReadList({"label": "Choice", "value": "x"} for _ in range(33))
    driver = RichReads(report)
    with pytest.raises(RuntimeError, match=r"^Browser read report failed\.$"):
        await execute_read(lane, driver, member)
    assert driver.reads == 1


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_legacy_subclassed_string_is_still_ordinary_read_text(lane: str) -> None:
    legacy = MaskedReadText("legacy page")
    result = payload(await execute_read(lane, RichReads(legacy), "get_page_text"))
    assert result["result"] == "legacy page"


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("collection", ["elements", "options", "omitted"])
async def test_v1_lookup_cannot_grow_an_admitted_collection(lane: str, collection: str) -> None:
    report = read_report()
    name = "label" if collection == "options" else "ref"

    class GrowingKey:
        grew = False

        @override
        def __hash__(self) -> int:
            return hash(name)

        @override
        def __eq__(self, other: object) -> bool:
            if other != name:
                return False
            if not self.grew:
                self.grew = True
                if collection == "elements":
                    report["elements"].extend({"ref": str(n), "role": "button", "label": "Extra"} for n in range(100))
                elif collection == "options":
                    report["elements"][0]["options"].extend({"label": "Extra", "value": "e"} for _ in range(32))
                else:
                    report["omitted"].append("private")
            return True

    if collection == "options":
        report["elements"][0]["options"] = [{GrowingKey(): "Patio", "value": "patio"}]
    else:
        report["elements"] = [{GrowingKey(): "opaque-ref", "role": "button", "label": "Visible"}]
        if collection == "omitted":
            report["omitted"] = []
    result = payload(await execute_read(lane, RichReads(report), "find"))["result"]
    expected = read_report()
    if collection == "options":
        expected["elements"][0]["options"] = [{"label": "Patio", "value": "patio"}]
    else:
        expected["elements"] = [{"ref": "opaque-ref", "role": "button", "label": "Visible"}]
        if collection == "omitted":
            expected["omitted"] = []
    assert result == expected


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_tab_projection_uses_checked_entries_not_custom_iterator(lane: str) -> None:
    class IndexedTabs(list[BrowserTab]):
        @override
        def __iter__(self) -> Any:
            raise AssertionError("Browser must project the validated number of entries")

    class IndexedDesktop(Desktop):
        @override
        def state(self) -> BrowserState:
            return {
                "tabs": IndexedTabs([{"id": "one", "title": "Page", "url": self.url, "active": True}]),
                "observation": {
                    "version": 1,
                    "sequence": 0,
                    "dropped_changes": 0,
                    "title_truncated": False,
                    "changes": [],
                },
            }

    desktop = IndexedDesktop()
    result = await execute(lane, desktop, call("list_tabs", {}), lambda _: True, lambda _ctx, _url: True)
    assert cast(dict[str, Any], payload(result)["state"])["tabs"] == [
        {"id": "one", "title": "Page", "url": "https://allowed.example", "active": True}
    ]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("partial", [False, True])
async def test_browser_post_handler_cancel_precedes_output_validation(lane: str, partial: bool) -> None:
    from openai.lib.browser import BrowserCancelledError
    from openai.lib.tool_diagnostics import ToolDiagnostic

    stopped = False
    events: list[ToolDiagnostic] = []

    class CancellingDesktop(Desktop):
        @override
        def screenshot(self, action: TabInput) -> ResponseInputImageContentParam:
            nonlocal stopped
            stopped = True
            return cast(ResponseInputImageContentParam, None) if partial else super().screenshot(action)

    desktop = CancellingDesktop()
    if lane == "sync":
        browser = BrowserToolset(desktop, members=["screenshot"])
        with pytest.raises(BrowserCancelledError):
            browser.execute(
                call("screenshot", {"tab_id": None}), cancelled=lambda: stopped, on_diagnostic=events.append
            )
    else:
        async_browser = AsyncBrowserToolset(AsyncDesktop(desktop), members=["screenshot"])
        with pytest.raises(BrowserCancelledError):
            await async_browser.execute(
                call("screenshot", {"tab_id": None}), cancelled=lambda: stopped, on_diagnostic=events.append
            )
    assert events[-1]["stage"] == "action" and events[-1]["reason"] == "cancelled"
    assert not any(event["reason"] in ("completed", "invalid_output") for event in events)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("key", ["access_token", "sig", "Signature", "X-Goog-Signature", "X-Goog-Credential"])
async def test_legacy_tab_credentials_excluded_from_approval_and_model(lane: str, key: str) -> None:
    seen: list[str] = []
    desktop = Desktop()
    desktop.url = (
        f"https://user:synthetic-password@allowed.example/path?q=1&{key}=synthetic-query#id_token=synthetic-fragment"
    )

    def consent(ctx: BrowserConfirmContext) -> bool:
        seen.append(ctx["state"]["tabs"][0]["url"])
        return True

    result = await execute(
        lane, desktop, call("click", {"tab_id": "one", "target": "button"}), consent, lambda _ctx, _url: True
    )
    projected = payload(result)
    assert seen == ["https://allowed.example"]
    assert cast(dict[str, Any], projected["state"])["tabs"][0]["url"] == seen[0]
    assert not any(
        value in json.dumps(projected) for value in ("synthetic-password", "synthetic-query", "synthetic-fragment")
    )


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://allowed.example/orders/42?view=details", "https://allowed.example"),
        ("https://allowed.example:8443/orders/42", "https://allowed.example:8443"),
        ("https://allowed.example/" + "a" * 20_000, "https://allowed.example"),
        ("about:blank", "about:blank"),
        ("data:text/plain,local-fixture", "data:"),
    ],
    ids=["path", "port", "long-path", "blank", "opaque"],
)
async def test_legacy_url_projection_preserves_context_without_paths(lane: str, url: str, expected: str) -> None:
    desktop = Desktop()
    desktop.url = url
    result = payload(await execute(lane, desktop, call("list_tabs", {}), lambda _: True, lambda _ctx, _url: True))
    assert result["state"] == {"tabs": [{"id": "one", "title": "Page", "url": expected, "active": True}]}
    desktop.url = expected
    repeated = payload(await execute(lane, desktop, call("list_tabs", {}), lambda _: True, lambda _ctx, _url: True))
    assert repeated["state"] == result["state"]


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("length", [2047, 2048])
async def test_legacy_url_limits_apply_to_projected_value(lane: str, length: int) -> None:
    desktop = Desktop()
    desktop.url = "x" * length + ":private"
    if length == 2047:
        result = payload(await execute(lane, desktop, call("list_tabs", {}), lambda _: True, lambda _ctx, _url: True))
        assert result["state"] == {"tabs": [{"id": "one", "title": "Page", "url": "x" * length + ":", "active": True}]}
    else:
        with pytest.raises(RuntimeError, match="Browser state report failed"):
            await execute(lane, desktop, call("list_tabs", {}), lambda _: True, lambda _ctx, _url: True)


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize("part", ["path", "query", "fragment", "userinfo", "origin"])
async def test_observed_url_bounds_apply_after_projection(lane: str, part: str) -> None:
    private_value = "x" * 100_000
    url = {
        "path": f"https://allowed.example/{private_value}",
        "query": f"https://allowed.example/?token={private_value}",
        "fragment": f"https://allowed.example/#{private_value}",
        "userinfo": f"https://user:{private_value}@allowed.example/",
        "origin": "https://" + "a." * 1024 + "example/",
    }[part]

    class ObservedDesktop(Desktop):
        @override
        def state(self) -> BrowserState:
            value = super().state()
            value["observation"] = {
                "version": 1,
                "sequence": 0,
                "dropped_changes": 0,
                "title_truncated": False,
                "changes": [],
            }
            return value

    desktop = ObservedDesktop()
    desktop.url = url
    seen: list[str] = []

    def consent(context: BrowserConfirmContext) -> bool:
        seen.append(context["state"]["tabs"][0]["url"])
        return True

    if part == "origin":
        with pytest.raises(RuntimeError, match="Browser state report failed"):
            await execute(
                lane, desktop, call("click", {"tab_id": "one", "target": "button"}), consent, lambda _ctx, _url: True
            )
        assert seen == []
        return
    result = payload(
        await execute(
            lane, desktop, call("click", {"tab_id": "one", "target": "button"}), consent, lambda _ctx, _url: True
        )
    )
    assert seen == ["https://allowed.example"]
    assert cast(dict[str, Any], result["state"])["tabs"][0]["url"] == "https://allowed.example"


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_scroll_schema_and_runtime_share_the_portable_integer_limit(lane: str) -> None:
    amounts: list[int] = []

    class Scroller(Desktop):
        def scroll(self, action: ScrollInput) -> None:
            amounts.append(action["amount"])

    class AsyncScroller(AsyncDesktop):
        async def scroll(self, action: ScrollInput) -> None:
            amounts.append(action["amount"])

    async def approve(_ctx: BrowserConfirmContext) -> bool:
        return True

    driver = Scroller()
    browser = (
        BrowserToolset(driver, members=["scroll"], confirm=lambda _ctx: True)
        if lane == "sync"
        else AsyncBrowserToolset(AsyncScroller(driver), members=["scroll"], confirm=approve)
    )
    schema = next(tool["parameters"] for tool in browser.tools if tool["name"] == "browser_scroll")
    assert isinstance(schema, dict)
    properties = cast(dict[str, Any], schema["properties"])
    assert properties["amount"]["maximum"] == 9007199254740991
    for amount in (9007199254740991, 9007199254740992):
        request = call("scroll", {"tab_id": "one", "direction": "down", "amount": amount})
        result = (
            await browser.execute(request) if isinstance(browser, AsyncBrowserToolset) else browser.execute(request)
        )
        assert payload(result)["ok"] is (amount == 9007199254740991)
    assert amounts == [9007199254740991]


@pytest.mark.parametrize("lane", ["sync", "async"])
async def test_browser_observation_length_captured_once(lane: str) -> None:
    class ChangingLength(list[dict[str, object]]):
        def __init__(self) -> None:
            super().__init__({"type": "navigation", "tab_id": "one", "sequence": index + 1} for index in range(40))
            self.reads = 0

        @override
        def __len__(self) -> int:
            self.reads += 1
            return 0 if self.reads < 3 else super().__len__()

    class ObservedDesktop(Desktop):
        @override
        def state(self) -> BrowserState:
            return {
                **super().state(),
                "observation": {
                    "version": 1,
                    "sequence": 0,
                    "dropped_changes": 0,
                    "title_truncated": False,
                    "changes": cast(Any, ChangingLength()),
                },
            }

    result = await execute(lane, ObservedDesktop(), call("list_tabs", {}), lambda _ctx: True, lambda _ctx, _url: True)
    projected = cast(dict[str, Any], payload(result)["state"])["observation"]
    assert projected["sequence"] == 0 and projected["changes"] == []


@pytest.mark.parametrize("lane", ["sync", "async"])
@pytest.mark.parametrize(
    "url",
    [
        "https:user:synthetic-password@allowed.example/path",
        r"https:\\user:synthetic-password@allowed.example/path",
        "http:user:synthetic-password@allowed.example/path",
    ],
)
async def test_legacy_http_url_with_unparsed_authority_never_reaches_approval(lane: str, url: str) -> None:
    desktop = Desktop()
    desktop.url = url
    seen: list[BrowserConfirmContext] = []

    def consent(ctx: BrowserConfirmContext) -> bool:
        seen.append(ctx)
        return True

    with pytest.raises(RuntimeError) as caught:
        await execute(
            lane, desktop, call("click", {"tab_id": "one", "target": "button"}), consent, lambda _ctx, _url: True
        )
    assert "synthetic-password" not in str(caught.value)
    assert seen == []
