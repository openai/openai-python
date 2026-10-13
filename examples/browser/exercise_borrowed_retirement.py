"""A borrowed driver must retire after uncertain native input without closing its caller's context."""

from __future__ import annotations

import json
import asyncio
from typing import Any, Callable, Awaitable, cast
from contextlib import ExitStack
from unittest.mock import AsyncMock, patch, create_autospec

from browser_driver import PlaywrightBrowser
from playwright.async_api import (
    Page,
    Error as PlaywrightError,
    Mouse,
    Route,
    Request,
    JSHandle,
    Keyboard,
    ElementHandle,
    BrowserContext,
    async_playwright,
)

from openai.lib.browser import BrowserError, AsyncBrowserToolset, BrowserCancelledError
from openai.types.responses import ResponseFunctionToolCall


async def main() -> None:
    # Controlled page registrations exercise a live count, without a popup workload.
    registry = create_autospec(BrowserContext, instance=True)
    registry.pages = []
    registry.close = AsyncMock()
    limited = PlaywrightBrowser(
        registry, {"http://127.0.0.1:80"}, owned_fixture_urls=frozenset({"http://127.0.0.1/fixture"})
    )
    for _ in range(120):
        page = create_autospec(Page, instance=True)
        page.is_closed.return_value = False
        limited._register(page)
        ident = limited.active
        limited._closed_tab(ident)
    assert not (await limited.state())["tabs"]
    for _ in range(100):
        page = create_autospec(Page, instance=True)
        page.is_closed.return_value = False
        page.url = "about:blank"
        limited._register(page)
    assert len((await limited.state())["tabs"]) == 100
    page = create_autospec(Page, instance=True)
    page.is_closed.return_value = False
    limited._register(page)
    try:
        await limited.state()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Owned registry admitted more than 100 live pages")
    assert limited._retirement is not None
    await limited._retirement
    registry.close.assert_awaited_once()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, chromium_sandbox=True)
        context = await browser.new_context()
        find_context = await browser.new_context()
        try:
            trial = PlaywrightBrowser(find_context, set())
            fixture = await find_context.new_page()
            await fixture.set_content(
                """<button>Other</button><button onclick="document.body.dataset.saved='yes'">Straße</button><button>Later</button>"""
            )
            tab, _ = trial.page(None)
            before = await trial.read_page({"tab_id": tab, "filter": "interactive"})
            assert not isinstance(before, str)
            previous = next(item["ref"] for item in before["elements"] if item["label"] == "Other")
            native_scan = fixture.evaluate_handle
            captured: list[str] = []
            with ExitStack() as patches:

                async def scan_targets(expression: str, arg: Any = None) -> JSHandle:
                    scan = await native_scan(expression, arg)
                    property = scan.get_property

                    async def capture_targets(name: str) -> JSHandle:
                        value = await property(name)
                        if name == "targets":
                            properties = value.get_properties

                            async def capture_nodes() -> dict[str, JSHandle]:
                                candidates = await properties()
                                for candidate in candidates.values():
                                    native_property = candidate.get_property

                                    async def capture_node(
                                        member: str,
                                        *,
                                        candidate: JSHandle = candidate,
                                        native_property: Callable[[str], Awaitable[JSHandle]] = native_property,
                                    ) -> JSHandle:
                                        if member == "node":
                                            captured.append(await candidate.evaluate("value => value.item.label"))
                                        return await native_property(member)

                                    patches.enter_context(
                                        patch.object(candidate, "get_property", side_effect=capture_node)
                                    )
                                return candidates

                            patches.enter_context(patch.object(value, "get_properties", side_effect=capture_nodes))
                        return value

                    patches.enter_context(patch.object(scan, "get_property", side_effect=capture_targets))
                    return scan

                patches.enter_context(patch.object(fixture, "evaluate_handle", side_effect=scan_targets))
                matches = await trial.find({"tab_id": tab, "query": "STRASSE"})
            assert not isinstance(matches, str)
            assert [item["label"] for item in matches["elements"]] == ["Straße"]
            assert captured == ["Straße"]
            disposed: list[str | None] = []
            native_dispose = ElementHandle.dispose

            async def disposed_click(handle: ElementHandle) -> None:
                disposed.append(await handle.text_content())
                await native_dispose(handle)

            with patch.object(ElementHandle, "dispose", disposed_click):
                try:
                    await trial.click({"tab_id": tab, "target": previous})
                except BrowserError:
                    pass
                else:
                    raise AssertionError("A ref excluded by the fresh find was still usable")
                try:
                    await trial.click({"tab_id": tab, "target": matches["elements"][0]["ref"]}, cancelled=lambda: True)
                except BrowserCancelledError:
                    pass
                else:
                    raise AssertionError("Pre-aborted click dispatched")
                assert disposed == []
                await trial.click({"tab_id": tab, "target": matches["elements"][0]["ref"]})
                assert disposed == ["Straße"]
                assert await fixture.get_attribute("body", "data-saved") == "yes"
            fresh = await trial.read_page({"tab_id": tab, "filter": "all"})
            assert not isinstance(fresh, str)
            assert [item["label"] for item in fresh["elements"]] == ["Other", "Straße", "Later"]
        finally:
            await find_context.close()
        try:
            for kind in ("click", "fill", "untargeted", "select", "key", "scroll", "hover"):
                for outcome in ("failed", "cancelled"):
                    current = await browser.new_context()
                    try:
                        trial = PlaywrightBrowser(current, set())
                        fixture = await current.new_page()
                        await fixture.set_content(
                            '<button id="button">Count</button><label for="note">Note</label><input id="note">'
                            '<label for="choice">Choice</label><select id="choice">'
                            "<option>a</option><option>b</option></select>"
                        )
                        ident = (await trial.state())["tabs"][0]["id"]
                        read = await trial.read_page({"tab_id": ident, "filter": "interactive"})
                        assert not isinstance(read, str)
                        refs = {item["label"]: item["ref"] for item in read["elements"]}
                        await fixture.locator("#note").focus()
                        stop = asyncio.Event()
                        cls: Any
                        if kind in ("click", "fill", "select", "hover"):
                            cls = ElementHandle
                        elif kind in ("untargeted", "key"):
                            cls = Keyboard
                        else:
                            cls = Mouse
                        member = {
                            "click": "click",
                            "fill": "fill",
                            "select": "select_option",
                            "hover": "hover",
                            "untargeted": "insert_text",
                            "key": "press",
                            "scroll": "wheel",
                        }[kind]
                        native = getattr(cls, member)
                        dispatched = 0

                        async def performed(
                            *args: Any,
                            impl: Any = native,
                            state: str = outcome,
                            stopped: asyncio.Event = stop,
                            **kwargs: Any,
                        ) -> Any:
                            nonlocal dispatched
                            result = await impl(*args, **kwargs)
                            dispatched += 1
                            if state == "failed":
                                raise RuntimeError("Synthetic local transport failure after input.")
                            stopped.set()
                            return result

                        consumed: list[str | None] = []

                        async def consume(handle: ElementHandle, *, consumed: list[str | None] = consumed) -> None:
                            consumed.append(await handle.get_attribute("id"))
                            await native_dispose(handle)
                            raise PlaywrightError("Synthetic Playwright remote object already closed.")

                        with ExitStack() as patches:
                            patches.enter_context(patch.object(cls, member, performed))
                            if kind == "click":
                                patches.enter_context(patch.object(ElementHandle, "dispose", consume))
                            try:
                                if kind == "click":
                                    await trial.click({"tab_id": ident, "target": refs["Count"]}, cancelled=stop.is_set)
                                elif kind == "fill" or kind == "untargeted":
                                    await trial.type(
                                        {
                                            "tab_id": ident,
                                            "target": refs["Note"] if kind == "fill" else None,
                                            "text": "entered",
                                        },
                                        cancelled=stop.is_set,
                                    )
                                elif kind == "select":
                                    await trial.select_option(
                                        {"tab_id": ident, "target": refs["Choice"], "values": ["b"]},
                                        cancelled=stop.is_set,
                                    )
                                elif kind == "key":
                                    await trial._key({"tab_id": ident, "keys": ["A"]}, cancelled=stop.is_set)
                                elif kind == "scroll":
                                    await trial._scroll(
                                        {"tab_id": ident, "direction": "down", "amount": 100}, cancelled=stop.is_set
                                    )
                                else:
                                    await trial._hover(
                                        {"tab_id": ident, "target": refs["Count"]}, cancelled=stop.is_set
                                    )
                            except BrowserCancelledError:
                                assert outcome == "cancelled"
                            except BrowserError as error:
                                assert outcome == "failed"
                                assert str(error) == "Borrowed browser input outcome is unknown; driver retired."
                            else:
                                raise AssertionError(f"{kind} succeeded after {outcome}")
                            assert dispatched == 1, kind
                            if kind == "click":
                                assert consumed == ["button"]
                            try:
                                await trial.state()
                            except RuntimeError:
                                pass
                            else:
                                raise AssertionError(f"{kind} remained usable after {outcome}")
                        witness = await current.new_page()
                        assert await witness.evaluate("2 + 2") == 4
                    finally:
                        await current.close()
            for url, member in (
                ("back", "go_back"),
                ("forward", "go_forward"),
                ("reload", "reload"),
                ("ordinary", "goto"),
            ):
                for outcome in ("failed", "cancelled"):
                    history_context = await browser.new_context()
                    posts: list[str | None] = []
                    fixture_origin = "http://127.0.0.1:31337"
                    destination = f"{fixture_origin}/records" if url == "ordinary" else url

                    async def synthetic_route(
                        route: Route,
                        _request: Request,
                        *,
                        records: list[str | None] = posts,
                        current_origin: str = fixture_origin,
                    ) -> None:
                        if route.request.url == f"{current_origin}/records":
                            records.append(route.request.method)
                        await route.fulfill(
                            content_type="text/html", body="<title>History</title><button>Record</button>"
                        )

                    await history_context.route(f"{fixture_origin}/**", synthetic_route)
                    try:
                        history_driver = PlaywrightBrowser(history_context, {fixture_origin})
                        fixture = await history_context.new_page()
                        await fixture.goto(f"{fixture_origin}/form")
                        ident = (await history_driver.state())["tabs"][0]["id"]
                        try:
                            await history_driver.navigate({"tab_id": "missing", "url": destination})
                        except BrowserError:
                            pass
                        else:
                            raise AssertionError("Unknown history tab was dispatched")
                        assert len((await history_driver.state())["tabs"]) == 1
                        try:
                            await history_driver.navigate({"tab_id": ident, "url": destination}, cancelled=lambda: True)
                        except BrowserCancelledError:
                            pass
                        else:
                            raise AssertionError("Already-cancelled navigation was dispatched")
                        if url == "ordinary":
                            try:
                                await history_driver.navigate({"tab_id": ident, "url": "invalid absolute URL"})
                            except BrowserError:
                                pass
                            else:
                                raise AssertionError("Invalid URL was dispatched")
                            await history_driver.navigate({"tab_id": ident, "url": f"{fixture_origin}/permitted"})
                        stop = asyncio.Event()
                        native_goto = fixture.goto

                        async def resubmitted(
                            *_args: object,
                            page: Page = fixture,
                            stopped: asyncio.Event = stop,
                            result: str = outcome,
                            method: str = url,
                            target_url: str = destination,
                            goto: Any = native_goto,
                            **_kwargs: object,
                        ) -> None:
                            if method == "ordinary":
                                await goto(target_url)
                            else:
                                await page.evaluate(
                                    "async () => { await fetch('/records', { method: 'POST', body: 'synthetic-record' }); }"
                                )
                            if result == "failed":
                                raise RuntimeError("Synthetic transport failure after a history resubmission")
                            stopped.set()

                        with patch.object(fixture, member, resubmitted):
                            for effect in (
                                lambda driver=history_driver, tab=ident, target=destination, stopped=stop: (
                                    driver.navigate({"tab_id": tab, "url": target}, cancelled=stopped.is_set)
                                ),
                                lambda driver=history_driver, tab=ident, target=destination: driver.navigate(
                                    {"tab_id": tab, "url": target}
                                ),
                                history_driver.state,
                            ):
                                try:
                                    await effect()
                                except (BrowserError, BrowserCancelledError, RuntimeError):
                                    pass
                                else:
                                    raise AssertionError(f"{url} remained usable after {outcome}")
                            assert posts == ["GET" if url == "ordinary" else "POST"]
                        witness = await history_context.new_page()
                        assert await witness.evaluate("2 + 2") == 4
                    finally:
                        await history_context.close()
            driver = PlaywrightBrowser(context, set())
            page = await context.new_page()
            await page.set_content("""<form onsubmit="event.preventDefault();this.dataset.saved='1'">
                <input id="submit" type="submit" value="Save form"><input type="button" value="Help">
                <input type="reset" value="Reset form"><input type="image" alt="Image action" value="PRIVATE_IMAGE_VALUE">
                <input type="submit" aria-label="Named submit" value="Not the name">
                <label for="labelled">Visible reset</label><input id="labelled" type="reset" value="Other reset">
                <input type="password" aria-label="PRIVATE_PASSWORD_LABEL" value="PRIVATE_PASSWORD_VALUE">
                <input type="file" aria-label="PRIVATE_FILE_LABEL"></form>""")
            form_tab = (await driver.state())["tabs"][0]["id"]
            form = await driver.read_page({"tab_id": form_tab, "filter": "interactive"})
            assert not isinstance(form, str)
            assert [(item["role"], item["label"]) for item in form["elements"]] == [
                ("button", "Save form"),
                ("button", "Help"),
                ("button", "Reset form"),
                ("button", "Image action"),
                ("button", "Named submit"),
                ("button", "Visible reset"),
            ]
            assert all("value" not in item for item in form["elements"])
            assert "PRIVATE_" not in json.dumps(form)
            await page.locator("#submit").evaluate("(input) => { input.value = 'Archive form'; }")
            try:
                await driver.click({"tab_id": form_tab, "target": form["elements"][0]["ref"]})
            except BrowserError:
                pass
            else:
                raise AssertionError("An input button renamed since reading must be re-observed.")
            assert await page.locator("form").get_attribute("data-saved") is None
            renamed = await driver.read_page({"tab_id": form_tab, "filter": "interactive"})
            assert not isinstance(renamed, str) and renamed["elements"][0]["label"] == "Archive form"
            await driver.click({"tab_id": form_tab, "target": renamed["elements"][0]["ref"]})
            assert await page.locator("form").get_attribute("data-saved") == "1"
            await page.set_content(
                """<button onclick="document.body.dataset.count=String(Number(document.body.dataset.count||0)+1)">Count</button>
                <label for="note">Note</label><input id="note">
                <label for="service">Service</label><select id="service">
                  <option value="standard">Standard</option><option value="express">Express</option></select>"""
            )
            tab_id = (await driver.state())["tabs"][0]["id"]
            title_tools = AsyncBrowserToolset(driver, members=["read_page"])
            for title, expected in (
                ("Short fixture title", "Short fixture title"),
                ("😺" * 256 + "é" + "extra" * 50_000, "😺" * 256),
            ):
                await page.evaluate("(value) => { document.title = value; }", title)
                title_result = await title_tools.execute(
                    ResponseFunctionToolCall(
                        name="browser_read_page",
                        call_id="title-fixture",
                        type="function_call",
                        arguments=json.dumps({"tab_id": tab_id, "filter": "interactive"}),
                    )
                )
                contents = title_result["output"]
                assert not isinstance(contents, str)
                part = contents[0]
                assert part["type"] == "input_text"
                output = json.loads(part["text"])
                assert output["ok"] is True
                assert output["state"]["tabs"][0]["title"] == expected
            report = await driver.read_page({"tab_id": tab_id, "filter": "interactive"})
            assert not isinstance(report, str)
            target = next(item["ref"] for item in report["elements"] if item["label"] == "Count")
            note = next(item["ref"] for item in report["elements"] if item["label"] == "Note")
            service = next(item["ref"] for item in report["elements"] if item["label"] == "Service")
            refused: list[str] = []
            for name in ("click", "type", "select", "hover"):
                owned_by_caller = await browser.new_context()
                trial = PlaywrightBrowser(owned_by_caller, set())
                checked_page = await owned_by_caller.new_page()
                await checked_page.set_content(await page.content())
                ident = (await trial.state())["tabs"][0]["id"]
                current = await trial.read_page({"tab_id": ident, "filter": "interactive"})
                assert not isinstance(current, str)
                refs = {item["label"]: item["ref"] for item in current["elements"]}
                evaluate = checked_page.evaluate
                entered, release, drained, stop = asyncio.Event(), asyncio.Event(), asyncio.Event(), asyncio.Event()

                async def during_scan(
                    expression: str,
                    arg: Any = None,
                    *,
                    scan: Callable[..., Awaitable[Any]] = evaluate,
                    ready: asyncio.Event = entered,
                    gate: asyncio.Event = release,
                    finished: asyncio.Event = drained,
                ) -> Any:
                    payload = cast(object, arg)
                    if not isinstance(payload, dict) or cast("dict[str, object]", payload).get("checkedNode") is None:
                        return await scan(expression, arg)
                    ready.set()
                    await gate.wait()
                    try:
                        return await scan(expression, arg)
                    finally:
                        finished.set()

                with patch.object(checked_page, "evaluate", during_scan):
                    if name == "click":
                        request = trial.click({"tab_id": ident, "target": refs["Count"]}, cancelled=stop.is_set)
                    elif name == "type":
                        request = trial.type(
                            {"tab_id": ident, "target": refs["Note"], "text": "cancelled"}, cancelled=stop.is_set
                        )
                    elif name == "select":
                        request = trial.select_option(
                            {"tab_id": ident, "target": refs["Service"], "values": ["express"]}, cancelled=stop.is_set
                        )
                    else:
                        request = trial._hover({"tab_id": ident, "target": refs["Count"]}, cancelled=stop.is_set)
                    pending_input = asyncio.create_task(request)
                    try:
                        await entered.wait()
                        stop.set()
                        done, pending = await asyncio.wait({pending_input}, timeout=1.5)
                        assert not pending and pending_input in done, name
                        try:
                            pending_input.result()
                        except BrowserCancelledError:
                            refused.append(name)
                        else:
                            raise AssertionError(f"{name} did not report Stop before dispatch")
                        try:
                            await trial.state()
                        except RuntimeError:
                            pass
                        else:
                            raise AssertionError("Interrupted ref validation left the driver usable")
                        assert await checked_page.evaluate("() => Number(document.body.dataset.count || 0)") == 0
                        assert await checked_page.locator("#note").input_value() == ""
                        assert await checked_page.locator("#service").input_value() == "standard"
                        witness = await owned_by_caller.new_page()
                        assert await witness.evaluate("() => 2 + 2") == 4
                    finally:
                        release.set()
                        await drained.wait()
                        await asyncio.gather(pending_input, return_exceptions=True)
                        await owned_by_caller.close()
            await page.locator("#note").focus()
            try:
                await driver.type(
                    {"tab_id": tab_id, "target": None, "text": "cancelled untargeted"}, cancelled=lambda: True
                )
            except BrowserCancelledError:
                refused.append("untargeted")
            observed = {
                "refused": refused,
                "clicks": await page.evaluate("Number(document.body.dataset.count || 0)"),
                "note": await page.locator("#note").input_value(),
                "service": await page.locator("#service").input_value(),
            }
            assert observed == {
                "refused": ["click", "type", "select", "hover", "untargeted"],
                "clicks": 0,
                "note": "",
                "service": "standard",
            }, observed
            await driver.type({"tab_id": tab_id, "target": note, "text": "accepted"})
            values = ["express"]
            original_scan = page.evaluate

            async def changed(expression: str, arg: Any = None) -> Any:
                found = await original_scan(expression, arg)
                if isinstance(arg, dict) and cast("dict[str, object]", arg).get("checkedNode") is not None:
                    values[0] = "standard"
                return found

            with patch.object(page, "evaluate", changed):
                await driver.select_option({"tab_id": tab_id, "target": service, "values": values})
            assert values == ["standard"]
            assert await page.locator("#note").input_value() == "accepted"
            assert await page.locator("#service").input_value() == "express"
            for invalid in ("standard", [{"label": "Standard"}]):
                try:
                    await driver.select_option({"tab_id": tab_id, "target": service, "values": cast(Any, invalid)})
                except BrowserError:
                    pass
                else:
                    raise AssertionError("Direct borrowed select accepted non-string-list option values")
                assert await page.locator("#service").input_value() == "express"
            await driver.select_option({"tab_id": tab_id, "target": service, "values": ["standard"]})
            assert await page.locator("#service").input_value() == "standard"
            await page.locator("#note").evaluate("(node) => node.remove()")
            try:
                await driver.type({"tab_id": tab_id, "target": note, "text": "removed"})
            except BrowserError:
                pass
            else:
                raise AssertionError("A removed control accepted input")
            print("PASS select snapshot, repeated selection, and removed control refusal")
            try:
                await driver.click({"tab_id": tab_id, "target": "nonexistent"})
            except BrowserError:
                pass
            else:
                raise AssertionError("Nonexistent reference was dispatched")
            assert len((await driver.state())["tabs"]) == 1
            native_click = ElementHandle.click

            async def after_dispatch(handle: ElementHandle, **kwargs: Any) -> None:
                await native_click(handle, **kwargs)
                raise RuntimeError("Synthetic transport failure after native input")

            with patch.object(ElementHandle, "click", after_dispatch):
                for effect in (
                    lambda: driver.click({"tab_id": tab_id, "target": target}),
                    lambda: driver.click({"tab_id": tab_id, "target": target}),
                    driver.state,
                ):
                    try:
                        await effect()
                    except (BrowserError, RuntimeError):
                        pass
                    else:
                        raise AssertionError("Uncertain borrowed driver remained usable")
            assert await page.evaluate("document.body.dataset.count") == "1"
            witness = await context.new_page()
            assert await witness.evaluate("2 + 2") == 4
            print(json.dumps({"pass": True, "dispatched": 1, "staleReusable": True, "callerContextSurvived": True}))
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
