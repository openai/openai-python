#!/usr/bin/env -S uv run python
"""Exercise the real browser and SDK helper without an API key or model request."""

from __future__ import annotations

import os
import json
import base64
import asyncio
import argparse
from types import SimpleNamespace
from typing import Any
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

import httpx2
from run import open_browser
from playwright_browser import PlaywrightBrowser, origin
from playwright.async_api import Page, Error, FloatRect

from openai import AsyncOpenAI
from openai.lib.computer import ComputerUseError, ComputerActionInput, AsyncComputerToolset
from openai.types.responses import computer_action as actions


async def check_guard() -> None:
    driver = PlaywrightBrowser(Mock(spec=Page), {origin("http://fixture.invalid")})
    for status in (200, 204, 304, 301, 302, 303, 307, 308):
        route = AsyncMock()
        route.request = SimpleNamespace(url="http://fixture.invalid/page")
        response = SimpleNamespace(status=status, dispose=AsyncMock())
        route.fetch.return_value = response
        await driver.guard(route)
        route.fetch.assert_awaited_once_with(max_redirects=0)
        route.continue_.assert_not_awaited()
        response.dispose.assert_awaited_once_with()
        if status in (301, 302, 303, 307, 308):
            route.abort.assert_awaited_once_with("failed")
            route.fulfill.assert_not_awaited()
        else:
            route.fulfill.assert_awaited_once_with(response=response)
            route.abort.assert_not_awaited()
    denied = AsyncMock()
    denied.request = SimpleNamespace(url="http://fixture.invalid:81/page")
    await driver.guard(denied)
    denied.abort.assert_awaited_once_with("blockedbyclient")
    denied.fetch.assert_not_awaited()
    for configured, requested in (
        ("https://BÜCHER.de", "https://xn--bcher-kva.de/page"),
        ("http://%65xample.com:81", "http://example.com:81/page"),
        ("http://[0:0:0:0:0:0:0:1]:81", "http://[::1]:81/page"),
        ("http://0x7f000001:81", "http://127.0.0.1:81/page"),
    ):
        equivalent = AsyncMock()
        equivalent.request = SimpleNamespace(url=requested)
        response = SimpleNamespace(status=200, dispose=AsyncMock())
        equivalent.fetch.return_value = response
        await PlaywrightBrowser(Mock(spec=Page), {origin(configured)}).guard(equivalent)
        equivalent.fulfill.assert_awaited_once_with(response=response)
        equivalent.abort.assert_not_awaited()
    for invalid in ("http://example.1", "http://%3A%3A1", "http://[fe80::1%25lo0]", "http://@fixture.invalid"):
        rejected = AsyncMock()
        rejected.request = SimpleNamespace(url=invalid)
        await driver.guard(rejected)
        rejected.abort.assert_awaited_once_with("blockedbyclient")
        rejected.fetch.assert_not_awaited()
    failure = AsyncMock()
    failure.request = SimpleNamespace(url="http://fixture.invalid/page")
    failure.fetch.side_effect = Error("Synthetic local transport failure.")
    await driver.guard(failure)
    failure.abort.assert_awaited_once_with("failed")
    failure.fulfill.assert_not_awaited()
    incomplete = AsyncMock()
    incomplete.request = SimpleNamespace(url="http://fixture.invalid/page")
    response = SimpleNamespace(status=200, dispose=AsyncMock())
    incomplete.fetch.return_value = response
    incomplete.fulfill.side_effect = Error("Synthetic response consumption failure.")
    await driver.guard(incomplete)
    incomplete.abort.assert_awaited_once_with("failed")
    response.dispose.assert_awaited_once_with()


async def check_borrowed_key_release() -> None:
    page = Mock(spec=Page)
    page.keyboard = AsyncMock()
    page.mouse = AsyncMock()
    page.close = AsyncMock()
    page.screenshot = AsyncMock()
    page.keyboard.up.side_effect = [Error("Synthetic release failure"), None, None]
    driver = PlaywrightBrowser(page, {origin("http://fixture.invalid")})
    try:
        await driver.keypress(actions.Keypress(type="keypress", keys=["CTRL", "ALT", "SHIFT"]))
    except ComputerUseError:
        pass
    else:
        raise AssertionError("The failed release must retire the borrowed adapter.")
    assert [call.args[0] for call in page.keyboard.up.await_args_list] == ["Shift", "Alt", "Control"]
    for work in (
        lambda: driver.keypress(actions.Keypress(type="keypress", keys=["a"])),
        lambda: driver.type(actions.Type(type="type", text="refused")),
        lambda: driver.wait(actions.Wait(type="wait")),
        driver.screenshot,
    ):
        try:
            await work()
        except ComputerUseError:
            pass
        else:
            raise AssertionError("A retired borrowed adapter must refuse every input and screenshot.")
    page.close.assert_not_awaited()
    page.keyboard.insert_text.assert_not_awaited()
    page.screenshot.assert_not_awaited()
    assert page.keyboard.down.await_count == 3

    for failure in (Error("Synthetic press failure"), asyncio.CancelledError()):
        page = Mock(spec=Page)
        page.keyboard = AsyncMock()
        page.mouse = AsyncMock()
        page.close = AsyncMock()
        page.screenshot = AsyncMock()
        page.keyboard.down.side_effect = [None, failure]
        driver = PlaywrightBrowser(page, {origin("http://fixture.invalid")})
        try:
            await driver.keypress(actions.Keypress(type="keypress", keys=["CTRL", "ALT", "SHIFT"]))
        except (Error, asyncio.CancelledError):
            pass
        else:
            raise AssertionError("An uncertain key press must stop the action.")
        assert [call.args[0] for call in page.keyboard.up.await_args_list] == ["Alt", "Control"]
        for work in (
            lambda current=driver: current.type(actions.Type(type="type", text="refused")),
            driver.screenshot,
        ):
            try:
                await work()
            except ComputerUseError:
                pass
            else:
                raise AssertionError("An uncertain press must retire the borrowed driver.")
        assert page.keyboard.down.await_count == 2
        page.keyboard.insert_text.assert_not_awaited()
        page.screenshot.assert_not_awaited()
        page.close.assert_not_awaited()


async def check_borrowed_mouse_release() -> None:
    for failure in (Error("Synthetic release failure"), asyncio.CancelledError()):
        page = Mock(spec=Page)
        page.keyboard = AsyncMock()
        page.mouse = AsyncMock()
        page.close = AsyncMock()
        page.screenshot = AsyncMock()
        page.mouse.up.side_effect = failure
        driver = PlaywrightBrowser(page, {origin("http://fixture.invalid")})
        try:
            await driver.drag(
                actions.Drag(
                    type="drag", path=[actions.DragPath(x=10, y=10), actions.DragPath(x=20, y=20)], keys=["CTRL"]
                )
            )
        except (ComputerUseError, asyncio.CancelledError) as error:
            assert isinstance(error, asyncio.CancelledError) == isinstance(failure, asyncio.CancelledError)
        else:
            raise AssertionError("An uncertain mouse release must retire the borrowed adapter.")
        page.mouse.up.assert_awaited_once_with()
        page.keyboard.up.assert_awaited_once_with("Control")
        for work in (
            lambda current=driver: current.move(actions.Move(type="move", x=30, y=30, keys=[])),
            lambda current=driver: current.type(actions.Type(type="type", text="refused")),
            driver.screenshot,
        ):
            try:
                await work()
            except ComputerUseError:
                pass
            else:
                raise AssertionError("A failed mouse release must prevent further input and screenshots.")
        assert page.mouse.move.await_count == 2
        page.keyboard.insert_text.assert_not_awaited()
        page.screenshot.assert_not_awaited()
        page.close.assert_not_awaited()


async def check_input_outcome() -> None:
    for member in ("click", "type"):
        for failure in (Error("Synthetic input failure"), asyncio.CancelledError()):
            page = Mock(spec=Page)
            page.keyboard = AsyncMock()
            page.mouse = AsyncMock()
            page.close = AsyncMock()
            page.screenshot = AsyncMock()
            driver = PlaywrightBrowser(page, set())
            if member == "click":
                page.mouse.click.side_effect = failure
                work = driver.click(actions.Click(type="click", button="left", x=10, y=10, keys=["CTRL", "SHIFT"]))
            else:
                page.keyboard.insert_text.side_effect = failure
                work = driver.type(actions.Type(type="type", text="fixture"))
            try:
                await work
            except (Error, asyncio.CancelledError):
                pass
            else:
                raise AssertionError("The uncertain input outcome must escape.")
            page.keyboard.insert_text.reset_mock(side_effect=True)
            assert [call.args[0] for call in page.keyboard.up.await_args_list] == (
                ["Shift", "Control"] if member == "click" else []
            )
            for next_work in (
                lambda current=driver: current.type(actions.Type(type="type", text="next")),
                driver.screenshot,
            ):
                try:
                    await next_work()
                except ComputerUseError:
                    pass
                else:
                    raise AssertionError("Uncertain input must retire the adapter, even after successful releases.")
            page.keyboard.insert_text.assert_not_awaited()
            page.screenshot.assert_not_awaited()
            page.close.assert_not_awaited()


async def check_cancelled_input_release() -> None:
    for member in ("keypress", "click", "drag"):
        for release_failure in (Error("Synthetic release failure"), asyncio.CancelledError("second cancellation")):
            page = Mock(spec=Page)
            page.keyboard = AsyncMock()
            page.mouse = AsyncMock()
            page.close = AsyncMock()
            page.screenshot = AsyncMock()
            driver = PlaywrightBrowser(page, set())

            async def wait_for_cancellation(*_args: Any, **_kwargs: Any) -> None:
                await asyncio.Future()

            if member == "keypress":

                async def hold_third(name: str) -> None:
                    if name == "Shift":
                        await wait_for_cancellation()

                page.keyboard.down.side_effect = hold_third
                work = driver.keypress(actions.Keypress(type="keypress", keys=["CTRL", "ALT", "SHIFT"]))
            elif member == "click":
                page.mouse.click.side_effect = wait_for_cancellation
                work = driver.click(
                    actions.Click(type="click", button="left", x=10, y=10, keys=["CTRL", "ALT", "SHIFT"])
                )
            else:

                async def hold_move(x: float, y: float) -> None:
                    if x == 20 and y == 20:
                        await wait_for_cancellation()

                page.mouse.move.side_effect = hold_move
                page.mouse.up.side_effect = release_failure
                work = driver.drag(
                    actions.Drag(
                        type="drag",
                        path=[actions.DragPath(x=10, y=10), actions.DragPath(x=20, y=20)],
                        keys=["CTRL", "ALT", "SHIFT"],
                    )
                )
            page.keyboard.up.side_effect = [release_failure, None, None]
            try:
                await asyncio.wait_for(work, timeout=0.02)
            except asyncio.TimeoutError:
                pass
            else:
                raise AssertionError("Cancellation must remain a timeout even if release fails.")
            assert [call.args[0] for call in page.keyboard.up.await_args_list] == ["Shift", "Alt", "Control"]
            if member == "drag":
                page.mouse.up.assert_awaited_once_with()
            for next_work in (
                lambda current=driver: current.type(actions.Type(type="type", text="next")),
                driver.screenshot,
            ):
                try:
                    await next_work()
                except ComputerUseError:
                    pass
                else:
                    raise AssertionError("Cancelled input must retire the borrowed adapter.")
            page.keyboard.insert_text.assert_not_awaited()
            page.screenshot.assert_not_awaited()
            page.close.assert_not_awaited()

    for release in ("key", "mouse"):
        page = Mock(spec=Page)
        page.keyboard = AsyncMock()
        page.mouse = AsyncMock()
        page.close = AsyncMock()
        page.screenshot = AsyncMock()
        driver = PlaywrightBrowser(page, set())

        async def hold_release(*_args: Any, **_kwargs: Any) -> None:
            await asyncio.Future()

        async def release_key(name: str) -> None:
            if name == "Shift":
                await hold_release()

        if release == "key":
            page.keyboard.up.side_effect = release_key
            work = driver.keypress(actions.Keypress(type="keypress", keys=["CTRL", "ALT", "SHIFT"]))
        else:
            page.mouse.up.side_effect = hold_release
            work = driver.drag(
                actions.Drag(
                    type="drag",
                    path=[actions.DragPath(x=10, y=10), actions.DragPath(x=20, y=20)],
                    keys=["CTRL", "ALT", "SHIFT"],
                )
            )
        try:
            await asyncio.wait_for(work, timeout=0.02)
        except asyncio.TimeoutError:
            pass
        else:
            raise AssertionError("Cancellation during the first release must remain a timeout.")
        assert [call.args[0] for call in page.keyboard.up.await_args_list] == ["Shift", "Alt", "Control"]
        if release == "mouse":
            page.mouse.up.assert_awaited_once_with()
        try:
            await driver.screenshot()
        except ComputerUseError:
            pass
        else:
            raise AssertionError("A cancelled release must retire the borrowed adapter.")
        page.screenshot.assert_not_awaited()
        page.close.assert_not_awaited()


async def check_launch_policy() -> None:
    for value in (
        "https://fixture.invalid/safe",
        "https://fixture.invalid/?page=2",
        "https://fixture.invalid/#safe",
        "https://fixture.invalid?",
        "https://fixture.invalid#",
    ):
        with patch("run.async_playwright") as start:
            try:
                async with open_browser(None, [value], headless=True):
                    raise AssertionError("A malformed permission must not launch a browser.")
            except ValueError:
                pass
            else:
                raise AssertionError("Origin permissions must not silently discard a path, query, or fragment.")
            start.assert_not_called()

    supplied = {
        "OPENAI_API_KEY": "synthetic-api-key",
        "UNRELATED_SECRET": "synthetic-secret",
        "PATH": "/fixture/bin",
        "HOME": "/fixture/home",
        "TMPDIR": "/fixture/tmp",
        "DISPLAY": ":fixture",
        "WAYLAND_DISPLAY": "wayland-fixture",
        "XAUTHORITY": "/fixture/xauthority",
        "XDG_RUNTIME_DIR": "/fixture/runtime",
    }
    for headless in (True, False):
        page = Mock(spec=Page)
        page.set_content = AsyncMock()
        context = AsyncMock()
        context.new_page.return_value = page
        browser = AsyncMock()
        browser.new_context.return_value = context
        launch = AsyncMock(return_value=browser)
        playwright = AsyncMock()
        playwright.__aenter__.return_value = SimpleNamespace(chromium=SimpleNamespace(launch=launch))
        with (
            patch("run.async_playwright", return_value=playwright),
            patch("run.sys.platform", "linux"),
            patch.dict(os.environ, supplied, clear=True),
        ):
            async with open_browser(None, ["https://BÜCHER.de/", "http://[::1]:81"], headless=headless) as driver:
                assert driver.allowed_origins == {"https://xn--bcher-kva.de:443", "http://[::1]:81"}
        assert launch.await_args is not None
        expected = {"PATH", "HOME", "TMPDIR"}
        if not headless:
            expected.update(("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY", "XDG_RUNTIME_DIR"))
        assert launch.await_args.kwargs["env"] == {name: supplied[name] for name in expected}
        browser.close.assert_awaited_once_with()


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshot", type=Path, help="Optionally save the final scripted PNG")
    args = parser.parse_args()
    await check_guard()
    await check_borrowed_key_release()
    await check_borrowed_mouse_release()
    await check_input_outcome()
    await check_cancelled_input_release()
    await check_launch_policy()
    for scheme, port in (("http", 80), ("https", 443)):
        assert origin(f"{scheme}://example.com:0") != origin(f"{scheme}://example.com/")
        assert origin(f"{scheme}://example.com:{port}") == origin(f"{scheme}://example.com/")
    async with open_browser(None, [], headless=True) as driver:
        name = await driver.page.locator("#name").bounding_box()
        submit = await driver.page.locator("#submit").bounding_box()
        assert name and submit

        def click(box: FloatRect) -> dict[str, Any]:
            return {
                "type": "click",
                "button": "left",
                "x": int(box["x"] + box["width"] / 2),
                "y": int(box["y"] + box["height"] / 2),
            }

        actions = [click(name), {"type": "type", "text": "Ada"}, click(submit)]
        requests = 0

        def transport(request: httpx2.Request) -> httpx2.Response:
            nonlocal requests
            requests += 1
            body = json.loads(request.content)
            base: dict[str, Any] = {
                "id": f"resp_{requests}",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": "test-only-computer",
            }
            if requests == 1:
                return httpx2.Response(
                    200,
                    json={
                        **base,
                        "output": [
                            {
                                "id": "cu_1",
                                "call_id": "call_1",
                                "type": "computer_call",
                                "status": "completed",
                                "pending_safety_checks": [],
                                "actions": actions,
                            }
                        ],
                    },
                )
            assert requests == 2, "unexpected model request"
            output = body["input"][-1]
            assert output["type"] == "computer_call_output" and output["call_id"] == "call_1"
            image_url = output["output"]["image_url"]
            assert image_url.startswith("data:image/png;base64,")
            png = base64.b64decode(image_url.split(",", 1)[1], validate=True)
            assert png.startswith(bytes.fromhex("89504e470d0a1a0a"))
            if args.screenshot:
                args.screenshot.write_bytes(png)
            return httpx2.Response(
                200,
                json={
                    **base,
                    "output": [
                        {
                            "id": "msg_1",
                            "type": "message",
                            "role": "assistant",
                            "status": "completed",
                            "phase": "final_answer",
                            "content": [
                                {"type": "output_text", "text": "Scripted actions complete", "annotations": []}
                            ],
                        }
                    ],
                },
            )

        async def allow_fixture_action(action: ComputerActionInput) -> bool:
            # This exercise controls the complete action list and uses only the bundled local page.
            return action.type in {"click", "type", "screenshot"}

        async with AsyncOpenAI(
            api_key="fixture-key-not-real",
            base_url="http://fixture.invalid/v1",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
        ) as client:
            result = await AsyncComputerToolset(driver).run(
                client,
                {"model": "test-only-computer", "input": "Greet Ada", "store": False},
                before_action=allow_fixture_action,
            )
        assert requests == 2
        assert result.output_text == "Scripted actions complete"
        assert await driver.page.locator("#result").inner_text() == "Hello, Ada!"
        print("PASS: scripted Responses calls drove the real page; its screenshot returned to the helper.")


if __name__ == "__main__":
    asyncio.run(main())
