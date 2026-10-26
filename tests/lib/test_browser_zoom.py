from __future__ import annotations

import json
from typing import cast
from typing_extensions import override

import pytest

from openai.lib.browser import BrowserError, BrowserState, BrowserToolset, AsyncBrowserToolset
from openai.types.responses import ResponseFunctionToolCall
from openai.types.responses.response_input_param import FunctionCallOutput


class ZoomDriver:
    def __init__(self) -> None:
        self.states = 0
        self.captures: list[dict[str, object]] = []
        self.image: object = {"type": "input_image", "image_url": "data:image/png;base64,b3JpZ2luYWw="}
        self.change_image = False

    def state(self) -> BrowserState:
        self.states += 1
        if self.change_image and self.states == 2:
            image = self.image
            assert isinstance(image, dict)
            image = cast(dict[str, object], image)
            image["image_url"] = "data:image/png;base64,Y2hhbmdlZA=="
            image["private_metadata"] = "not part of the approved image"
        return {"tabs": [{"id": "one", "title": "Public fixture", "url": "https://fixture.example/", "active": True}]}

    def zoom(self, args: dict[str, object]) -> object:
        self.captures.append(args)
        return self.image


class AsyncZoomDriver:
    def __init__(self, driver: ZoomDriver) -> None:
        self.driver = driver

    async def state(self) -> BrowserState:
        return self.driver.state()

    async def zoom(self, args: dict[str, object]) -> object:
        return self.driver.zoom(args)


def zoom_call(args: object) -> ResponseFunctionToolCall:
    return ResponseFunctionToolCall(
        type="function_call", name="browser_zoom", call_id="zoom_one", status="completed", arguments=json.dumps(args)
    )


def text(result: FunctionCallOutput) -> dict[str, object]:
    output = result["output"]
    assert isinstance(output, list) and output[0]["type"] == "input_text"
    return cast(dict[str, object], json.loads(output[0]["text"]))


async def dispatch(
    browser: BrowserToolset | AsyncBrowserToolset, args: object, *, skip: bool = False
) -> FunctionCallOutput:
    if isinstance(browser, AsyncBrowserToolset):
        return (await browser._execute(zoom_call(args), skip=skip))[0]
    return browser._execute(zoom_call(args), skip=skip)[0]


@pytest.fixture(params=["sync", "async"])
def zoom_browser(request: pytest.FixtureRequest) -> tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset]:
    driver = ZoomDriver()
    browser = BrowserToolset(driver) if request.param == "sync" else AsyncBrowserToolset(AsyncZoomDriver(driver))
    return driver, browser


async def test_zoom_returns_a_native_image_and_detaches_it_before_final_state(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
) -> None:
    driver, browser = zoom_browser
    driver.change_image = True
    result = await dispatch(browser, {"tab_id": None, "region": [10, 20, 41, 73]})
    assert text(result)["ok"] is True
    assert "result" not in text(result)
    content = result["output"]
    assert isinstance(content, list)
    assert content[1] == {"type": "input_image", "image_url": "data:image/png;base64,b3JpZ2luYWw="}
    assert driver.states == 2
    assert driver.captures == [{"tab_id": None, "region": [10, 20, 41, 73]}]


@pytest.mark.parametrize(
    "region",
    [
        None,
        [],
        [0, 0, 1],
        [0, 0, 1, 1, 2],
        [True, 0, 1, 1],
        [0.0, 0, 1, 1],
        [-1, 0, 1, 1],
        [0, 0, 2**53, 1],
        [2, 0, 1, 1],
        [0, 2, 1, 1],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ],
)
async def test_invalid_regions_refuse_before_capture(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
    region: object,
) -> None:
    driver, browser = zoom_browser
    result = await dispatch(browser, {"tab_id": None, "region": region})
    assert text(result)["ok"] is False
    assert driver.captures == []


@pytest.mark.parametrize(
    "args",
    [
        {"region": [0, 0, 1, 1]},
        {"tab_id": 3, "region": [0, 0, 1, 1]},
        {"tab_id": None, "region": [0, 0, 1, 1], "path": "/private/file"},
    ],
)
async def test_zoom_rejects_unknown_or_missing_fields_before_capture(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
    args: object,
) -> None:
    driver, browser = zoom_browser
    result = await dispatch(browser, args)
    assert text(result)["ok"] is False
    assert driver.captures == []


@pytest.mark.parametrize(
    "image",
    [
        None,
        {},
        {"type": "input_text", "text": "private"},
        {"type": "input_image", "image_url": ""},
        {"type": "input_image", "image_url": " \t\n"},
        {"type": "input_image", "file_id": " \t\n"},
        {"type": "input_image", "image_url": "uri", "file_id": " "},
        {"type": "input_image", "image_url": "uri", "detail": "unknown"},
        {"type": "input_image", "image_url": "uri", "private": "metadata"},
    ],
)
async def test_invalid_zoom_image_stops_before_final_state(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
    image: object,
) -> None:
    driver, browser = zoom_browser
    driver.image = image
    with pytest.raises(RuntimeError, match=r"^Browser zoom must return a valid input_image\.$"):
        await dispatch(browser, {"tab_id": None, "region": [0, 0, 1, 1]})
    assert len(driver.captures) == 1
    assert driver.states == 1


@pytest.mark.parametrize("skip", [False, True])
async def test_zoom_does_not_read_unneeded_policy_getters(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
    monkeypatch: pytest.MonkeyPatch,
    skip: bool,
) -> None:
    driver, browser = zoom_browser

    def forbidden(_self: object) -> object:
        pytest.fail("readonly or skipped zoom must not inspect approval or URL policy")

    monkeypatch.setattr(type(browser), "confirm", property(forbidden), raising=False)
    monkeypatch.setattr(type(browser), "url_policy", property(forbidden), raising=False)
    result = await dispatch(browser, {"tab_id": None, "region": [0, 0, 1, 1]}, skip=skip)
    assert text(result)["ok"] is (not skip)
    assert len(driver.captures) == (0 if skip else 1)


async def test_zoom_image_is_detached_before_post_capture_cancellation_poll(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
) -> None:
    driver, browser = zoom_browser

    def cancelled() -> bool:
        if driver.captures:
            image = driver.image
            assert isinstance(image, dict)
            cast(dict[str, object], image)["image_url"] = "data:image/png;base64,Y2hhbmdlZA=="
        return False

    request = zoom_call({"tab_id": None, "region": [0, 0, 1, 1]})
    result = (
        await browser.execute(request, cancelled=cancelled)
        if isinstance(browser, AsyncBrowserToolset)
        else browser.execute(request, cancelled=cancelled)
    )
    content = result["output"]
    assert isinstance(content, list)
    assert content[1] == {"type": "input_image", "image_url": "data:image/png;base64,b3JpZ2luYWw="}


@pytest.mark.parametrize(
    "image",
    [
        {"type": "input_image", "file_id": "file_one", "detail": "original"},
        {"type": "input_image", "image_url": "https://fixture.example/crop.png", "file_id": None},
        {"type": "input_image", "file_id": "id", "image_url": "uri"},
    ],
)
async def test_zoom_accepts_each_native_image_source(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
    image: dict[str, object],
) -> None:
    driver, browser = zoom_browser
    driver.image = image
    result = await dispatch(browser, {"tab_id": "one", "region": [0, 0, 1, 1]})
    content = result["output"]
    assert isinstance(content, list) and content[1] == image
    assert text(result) == {
        "ok": True,
        "state": {"tabs": [{"id": "one", "title": "Public fixture", "url": "https://fixture.example", "active": True}]},
    }
    assert driver.states == 2
    assert driver.captures == [{"tab_id": "one", "region": [0, 0, 1, 1]}]


async def test_excluded_zoom_is_not_inspected_or_dispatched(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    driver, existing = zoom_browser

    def forbidden(_self: object) -> object:
        pytest.fail("excluded zoom must not be inspected")

    browser: BrowserToolset | AsyncBrowserToolset
    if isinstance(existing, AsyncBrowserToolset):
        async_driver = AsyncZoomDriver(driver)
        monkeypatch.setattr(type(async_driver), "zoom", property(forbidden))
        browser = AsyncBrowserToolset(async_driver, members=["list_tabs"])
    else:
        monkeypatch.setattr(type(driver), "zoom", property(forbidden))
        browser = BrowserToolset(driver, members=["list_tabs"])

    with pytest.raises(BrowserError, match="disabled"):
        await dispatch(browser, {"tab_id": None, "region": [0, 0, 1, 1]})
    assert driver.captures == [] and driver.states == 0


async def test_zoom_snapshots_native_strings_without_subclass_hooks(
    zoom_browser: tuple[ZoomDriver, BrowserToolset | AsyncBrowserToolset],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MutableURL(str):
        replacement = "data:image/png;base64,initial-hook"

        @override
        def __str__(self) -> str:
            return "data:image/png;base64,str-hook"

        def __deepcopy__(self, _memo: dict[int, object]) -> str:
            return self.replacement

    driver, browser = zoom_browser
    source = MutableURL("data:image/png;base64,b3JpZ2luYWw=")
    driver.image = {"type": MutableURL("input_image"), "image_url": source, "detail": MutableURL("original")}
    original_state = driver.state

    def state() -> BrowserState:
        result = original_state()
        if driver.states == 2:
            source.replacement = "data:image/png;base64,private-final-state"
        return result

    monkeypatch.setattr(driver, "state", state)
    result = await dispatch(browser, {"tab_id": None, "region": [0, 0, 1, 1]})
    content = result["output"]
    assert isinstance(content, list)
    assert content[1] == {
        "type": "input_image",
        "image_url": "data:image/png;base64,b3JpZ2luYWw=",
        "detail": "original",
    }
    assert driver.states == 2
