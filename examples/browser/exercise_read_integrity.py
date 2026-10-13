"""Finite browser read, generation and public-value checks. No API calls."""

from __future__ import annotations

import json
import asyncio
from typing import Literal, Callable, Awaitable, cast
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import patch
from typing_extensions import override

from browser_driver import PlaywrightBrowser
from playwright.async_api import Browser, JSHandle, async_playwright

from openai.lib.browser import TabInput, BrowserError, BrowserReadV1, BrowserCancelledError

HTML = '<main data-record-id="a:b"><input id="allowed" type="text" aria-label="Allowed" data-browser-field="c" value="shown"><input id="other" type="text" aria-label="Other" data-browser-field="other" value="hidden"></main><main data-record-id="a"><input id="denied" type="text" aria-label="Denied" data-browser-field="b:c" value="unlisted"><input id="native-PaSsWoRd" type="PaSsWoRd"><input id="native-FiLe" type="file"><input id="native-HiDdEn" type="hidden"></main>'


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())


async def tab_case(
    browser: Browser, origin: str, url: str, owned_case: bool, member: Literal["switch_tab", "close_tab"]
) -> int:
    fixture = await browser.new_context()
    driver = PlaywrightBrowser(fixture, {origin}, owned_fixture_urls=frozenset({url}) if owned_case else None)
    first = await fixture.new_page()
    witness = await fixture.new_page()
    selected = (await driver.state())["tabs"][0]["id"]
    action: TabInput = {"tab_id": selected}
    execute = driver.switch_tab if member == "switch_tab" else driver.close_tab
    try:
        try:
            await execute(action, cancelled=lambda: True)
        except BrowserCancelledError:
            pass
        else:
            raise AssertionError("Pre-cancelled tab action was admitted")
        assert len((await driver.state())["tabs"]) == 2
        assert not first.is_closed()
        entered, release, stop = asyncio.Event(), asyncio.Event(), asyncio.Event()
        close_entered, close_release, close_finished = asyncio.Event(), asyncio.Event(), asyncio.Event()
        native_close = fixture.close

        async def held() -> None:
            entered.set()
            await release.wait()

        async def held_close(*, reason: str | None = None) -> None:
            close_entered.set()
            await close_release.wait()
            try:
                await native_close(reason=reason)
            finally:
                close_finished.set()

        name = "bring_to_front" if member == "switch_tab" else "close"
        with patch.object(first, name, held), patch.object(fixture, "close", held_close):
            pending = asyncio.create_task(execute(action, cancelled=stop.is_set))
            try:
                await asyncio.wait_for(entered.wait(), 3)
                stop.set()
                try:
                    await asyncio.wait_for(asyncio.shield(pending), 2)
                except BrowserCancelledError:
                    pass
                else:
                    raise AssertionError("Stop did not cancel the admitted tab operation")
                try:
                    await driver.state()
                except RuntimeError as error:
                    assert "retired" in str(error)
                else:
                    raise AssertionError("Interrupted driver was reusable")
                assert not witness.is_closed()
                if owned_case:
                    await asyncio.wait_for(close_entered.wait(), 2)
                    close_release.set()
                    await asyncio.wait_for(close_finished.wait(), 2)
                    assert witness.is_closed()
                release.set()
                try:
                    await driver.state()
                except RuntimeError as error:
                    assert "retired" in str(error)
                else:
                    raise AssertionError("Late tab work revived retired driver")
            finally:
                release.set()
                close_release.set()
        return 6
    finally:
        await fixture.close()


async def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    serving = Thread(target=server.serve_forever, daemon=True)
    serving.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    url, second = origin + "/fixture", origin + "/second"
    observations: list[dict[str, object]] = []
    checks = 0
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            try:
                for replaced in ("options", "encoder"):
                    fixture = await browser.new_context()
                    borrowed = PlaywrightBrowser(fixture, {origin})
                    try:
                        target = await fixture.new_page()
                        await target.set_content(
                            '<p>Å漢😀 shipment</p><select aria-label="Current choice">'
                            '<option value="one">Å漢😀 one</option><option value="two">Two</option></select>'
                        )
                        selected = (await borrowed.state())["tabs"][0]["id"]
                        await target.evaluate(
                            """(kind) => {
                              if (kind === 'options') {
                                Object.defineProperty(document.querySelector('select').options, Symbol.iterator, {
                                  value() { throw new Error('fixture called page option iterator'); },
                                });
                              } else {
                                window.TextEncoder = class {
                                  constructor() { throw new Error('fixture called page encoder'); }
                                };
                              }
                            }""",
                            replaced,
                        )
                        result = await borrowed.read_page({"tab_id": selected, "filter": "all"})
                        assert not isinstance(result, str)
                        choice = next(item for item in result["elements"] if item["label"] == "Current choice")
                        assert "options" in choice
                        assert choice["options"][0]["value"] == "one"
                        assert "Å漢😀 shipment" in result["text"]
                        found = await borrowed.find({"tab_id": selected, "query": "Current choice"})
                        assert not isinstance(found, str)
                        assert found["elements"][0]["label"] == "Current choice"
                        assert "Å漢😀 shipment" in await borrowed.get_page_text({"tab_id": selected})
                        assert not target.is_closed()
                        checks += 3
                    finally:
                        await fixture.close()
                for member in ("read_page", "find", "click"):
                    fixture = await browser.new_context()
                    borrowed = PlaywrightBrowser(fixture, {origin})
                    sentinel = await browser.new_page()
                    try:
                        await sentinel.set_content("<p>Caller still owns this page</p>")
                        target = await fixture.new_page()
                        await target.set_content("<button>Current choice</button>")
                        selected = (await borrowed.state())["tabs"][0]["id"]
                        prior = await borrowed.read_page({"tab_id": selected, "filter": "all"})
                        assert not isinstance(prior, str)
                        ref = prior["elements"][0]["ref"]
                        await target.evaluate("""() => {
                            const matches = Element.prototype.matches;
                            let once = true;
                            Element.prototype.matches = function(selector) {
                                if (once) {
                                    once = false;
                                    const until = performance.now() + 8000;
                                    while (performance.now() < until) {}
                                }
                                return matches.call(this, selector);
                            };
                        }""")
                        started = asyncio.get_running_loop().time()
                        try:
                            if member == "read_page":
                                await borrowed.read_page({"tab_id": selected, "filter": "all"})
                            elif member == "find":
                                await borrowed.find({"tab_id": selected, "query": "Current choice"})
                            else:
                                await borrowed.click({"tab_id": selected, "target": ref})
                        except BrowserError as exc:
                            assert "timed out" in str(exc)
                        else:
                            raise AssertionError("A stalled renderer exceeded the observation deadline")
                        assert asyncio.get_running_loop().time() - started < 7.2
                        for operation in (
                            borrowed.state,
                            lambda held=borrowed, tab=selected, target_ref=ref: held.click(
                                {"tab_id": tab, "target": target_ref}
                            ),
                        ):
                            try:
                                await operation()
                            except RuntimeError:
                                pass
                            else:
                                raise AssertionError("Expired borrowed read left the driver usable")
                        assert not target.is_closed()
                        assert await sentinel.text_content("p") == "Caller still owns this page"
                        checks += 1
                    finally:
                        await fixture.close()
                        await sentinel.close()
                context = await browser.new_context()
                driver = PlaywrightBrowser(context, {origin})
                page = await context.new_page()
                await page.goto(url)
                tab = (await driver.state())["tabs"][0]["id"]

                async def read() -> BrowserReadV1:
                    report = await driver.read_page({"tab_id": tab, "filter": "all"})
                    assert not isinstance(report, str), "Full fixture read must return structured elements"
                    return report

                initial = await read()
                assert initial["elements"]
                previous = next(iter(driver._refs[tab].values()))[0]
                original_dispose = previous.dispose
                reached, release = asyncio.Event(), asyncio.Event()

                async def dispose() -> None:
                    reached.set()
                    await release.wait()
                    await original_dispose()

                previous.dispose = dispose
                early = asyncio.create_task(read())
                await asyncio.wait_for(reached.wait(), 3)
                later = await read()
                release.set()
                caught = None
                try:
                    await early
                except Exception as error:
                    caught = error
                observations.append({"case": "generation", "rejected": caught is not None})
                assert caught is not None, "earlier read must not publish the newer generation"
                live = next(item for item in later["elements"] if item["label"] == "Allowed")
                await driver.type({"tab_id": tab, "target": live["ref"], "text": "still fresh"})
                assert await page.locator("#allowed").input_value() == "still fresh"
                assert not page.is_closed()
                checks += 3

                native_evaluate = page.evaluate_handle
                mismatch: Literal[
                    "label", "value", "missing-value", "private-PaSsWoRd", "private-FiLe", "private-HiDdEn"
                ] = "label"

                async def mismatch_evaluate(expression: str, arg: object = None) -> JSHandle:
                    scan = await native_evaluate(expression, arg)
                    original_property = scan.get_property

                    async def get_property(property_name: str) -> JSHandle:
                        handle = await original_property(property_name)
                        if property_name == "report" and mismatch in ("label", "value"):
                            original_value = handle.json_value

                            async def altered() -> object:
                                report = json.loads(await original_value())
                                report["elements"][0][mismatch] = "Mismatched projection"
                                return json.dumps(report)

                            handle.json_value = altered
                        if property_name == "targets" and (
                            mismatch == "missing-value" or mismatch.startswith("private-")
                        ):
                            original_properties = handle.get_properties

                            async def cut_bindings() -> dict[str, JSHandle]:
                                properties = await original_properties()
                                for candidate in properties.values():
                                    original_candidate = candidate.get_property

                                    async def candidate_property(
                                        property_name: str,
                                        *,
                                        native: Callable[[str], Awaitable[JSHandle]] = original_candidate,
                                    ) -> JSHandle:
                                        part = await native(property_name)
                                        if property_name == "node" and mismatch.startswith("private-"):
                                            await part.dispose()
                                            actual = await page.query_selector("#native-" + mismatch[8:])
                                            assert actual is not None
                                            return actual
                                        if property_name == "binding" and mismatch == "missing-value":
                                            original_json = part.json_value

                                            async def missing_slot() -> object:
                                                fields = await original_json()
                                                del fields[20:]
                                                return fields

                                            part.json_value = missing_slot
                                        return part

                                    candidate.get_property = candidate_property
                                return properties

                            handle.get_properties = cut_bindings
                        return handle

                    scan.get_property = get_property
                    return scan

                page.evaluate_handle = mismatch_evaluate
                for mismatch in (
                    "label",
                    "value",
                    "missing-value",
                    "private-PaSsWoRd",
                    "private-FiLe",
                    "private-HiDdEn",
                ):
                    caught = None
                    try:
                        await read()
                    except Exception as error:
                        caught = error
                    observations.append({"case": "projection " + mismatch, "rejected": caught is not None})
                    assert caught is not None, "captured binding must agree with the published " + mismatch
                    assert not page.is_closed()
                page.evaluate_handle = native_evaluate
                ordinary = await read()
                entry = next(item for item in ordinary["elements"] if item["label"] == "Allowed")
                await driver.type({"tab_id": tab, "target": entry["ref"], "text": "normal"})
                assert await page.locator("#allowed").input_value() == "normal"
                await driver.type({"tab_id": tab, "target": entry["ref"], "text": "same reference"})
                assert await page.locator("#allowed").input_value() == "same reference"
                checks += 14
                full_ready, full_gate = asyncio.Event(), asyncio.Event()
                text_ready, text_gate = asyncio.Event(), asyncio.Event()

                async def ordered(expression: str, arg: object = None) -> JSHandle:
                    scan = await native_evaluate(expression, arg)
                    assert isinstance(arg, dict), "Fixture read requires scan options"
                    if cast(dict[str, object], arg).get("textOnly"):
                        text_ready.set()
                        await text_gate.wait()
                    else:
                        full_ready.set()
                        await full_gate.wait()
                    return scan

                page.evaluate_handle = ordered
                producing = asyncio.create_task(read())
                await asyncio.wait_for(full_ready.wait(), 3)
                text = asyncio.create_task(driver.get_page_text({"tab_id": tab}))
                await asyncio.wait_for(text_ready.wait(), 3)
                full_gate.set()
                issued = await producing
                text_gate.set()
                assert isinstance(await text, str)
                page.evaluate_handle = native_evaluate
                future = await read()
                prior_refs = {item["ref"] for item in issued["elements"]}
                assert all(item["ref"] not in prior_refs for item in future["elements"]), (
                    "text-only read must not rewind ref counter"
                )
                observations.append({"case": "text-only counter", "unique": True})
                checks += 2
                await page.set_content("""
                    <button disabled>Unavailable</button>
                    <fieldset disabled><select aria-label="Unavailable select"><option>One</option></select></fieldset>
                    <input readonly aria-label="Read only" value="fixed">
                    <input id="editable" aria-label="Editable" value="before">
                    <select id="choice" aria-label="Current choice">
                      <option value="one">One</option><option value="">Empty</option>
                    </select>
                """)
                controls = await read()
                assert [item["label"] for item in controls["elements"]] == ["Editable", "Current choice"]
                assert "unsupported_control" in controls["omitted"]
                choice = next(item for item in controls["elements"] if item["label"] == "Current choice")
                assert choice.get("value") == "one"
                await driver.select_option({"tab_id": tab, "target": choice["ref"], "values": [""]})
                await driver.select_option({"tab_id": tab, "target": choice["ref"], "values": ["one"]})
                assert await page.locator("#choice").input_value() == "one"
                await driver.select_option({"tab_id": tab, "target": choice["ref"], "values": [""]})
                checks += 1
                changed = await read()
                assert (
                    next(item for item in changed["elements"] if item["label"] == "Current choice").get("value") == ""
                )
                editable = next(item for item in changed["elements"] if item["label"] == "Editable")
                await page.locator("#editable").evaluate("(element) => { element.readOnly = true; }")
                try:
                    await driver.type({"tab_id": tab, "target": editable["ref"], "text": "must not dispatch"})
                except BrowserError:
                    pass
                else:
                    raise AssertionError("Unavailable ref reached native input")
                assert await page.locator("#editable").input_value() == "before"
                refreshed = await read()
                assert [item["label"] for item in refreshed["elements"]] == ["Current choice"]
                assert not page.is_closed()
                checks += 8
                displayed = 'Room "A" \\ north 😺'
                await page.set_content(
                    '<main><p id="name"></p><input aria-label="Note" value="">'
                    '<input type="PaSsWoRd" value="private"><input type="file" aria-label="Private file">'
                    '<input type="hidden" value="private hidden">'
                    '<input type=" password " aria-label="Invalid type" value="ordinary"></main>'
                )
                await page.locator("#name").evaluate("(element, value) => { element.textContent = value; }", displayed)
                await page.locator('input[aria-label="Note"]').fill(displayed)
                quoted = await read()
                assert quoted["text"] == displayed
                assert quoted["elements"][0].get("value") == displayed
                assert "private" in quoted["omitted"]
                assert [item["label"] for item in quoted["elements"]] == ["Note", "Invalid type"]
                assert quoted["elements"][1].get("value") == "ordinary"
                assert "private hidden" not in json.dumps(quoted)
                checks += 6
                await page.set_content('<input id="ship" aria-label="Ship   order"><input aria-label="Other">')
                spaced = await driver.find({"tab_id": tab, "query": "  ship \n ORDER  "})
                assert not isinstance(spaced, str)
                assert [item["label"] for item in spaced["elements"]] == ["Ship   order"]
                await driver.type({"tab_id": tab, "target": spaced["elements"][0]["ref"], "text": "found"})
                assert await page.locator("#ship").input_value() == "found"
                option = f'<option value="{"v" * 384}">{"L" * 128}</option>'
                await page.set_content(
                    "".join(f'<select aria-label="Choice {index}">{option * 24}</select>' for index in range(6))
                )
                prefix = await read()
                assert [item["label"] for item in prefix["elements"]] == [
                    "Choice 0",
                    "Choice 1",
                    "Choice 2",
                    "Choice 3",
                ]
                assert "report_limit" in prefix["omitted"]
                assert len(json.dumps(prefix, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) <= 65_536
                choices = prefix["elements"][0].get("options")
                assert choices is not None and len(choices) == 24
                observations.append(
                    {
                        "case": "borrowed search whitespace and report prefix",
                        "matched": True,
                        "count": len(prefix["elements"]),
                    }
                )
                checks += 6
                await context.close()

                owned = await browser.new_context()
                owned_driver = PlaywrightBrowser(
                    owned,
                    {origin},
                    owned_fixture_urls=frozenset({url, second}),
                    public_values=frozenset({(url, "a:b", "c"), (url, "a", "other")}),
                )
                owned_page = await owned.new_page()
                await owned_page.goto(url)
                owned_tab = (await owned_driver.state())["tabs"][0]["id"]
                report = await owned_driver.read_page({"tab_id": owned_tab, "filter": "all"})
                assert not isinstance(report, str), "Full owned read must return structured elements"
                by_name = {item["label"]: item for item in report["elements"]}
                assert by_name["Allowed"].get("value") == "shown"
                assert "value" not in by_name["Denied"]
                assert "value" not in by_name["Other"]
                await owned_page.goto(second)
                report = await owned_driver.read_page({"tab_id": owned_tab, "filter": "all"})
                assert not isinstance(report, str), "Full owned read must return structured elements"
                assert all("value" not in item for item in report["elements"])
                checks += 4
                await owned.close()
                for owned_case in (False, True):
                    checks += await tab_case(browser, origin, url, owned_case, "switch_tab")
                    checks += await tab_case(browser, origin, url, owned_case, "close_tab")
                print(json.dumps({"checks": checks, "observations": observations, "api_calls": 0, "vendor_calls": 0}))
            finally:
                await browser.close()
    finally:
        server.shutdown()
        server.server_close()
        serving.join()


if __name__ == "__main__":
    asyncio.run(main())
