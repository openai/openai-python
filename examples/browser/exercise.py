"""Run real browser actions through scripted Responses calls, without an API key."""

from __future__ import annotations

import json
import base64
import asyncio
import argparse
from types import SimpleNamespace
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import AsyncMock
from typing_extensions import override

import httpx2
from run import make_runner, fixture_server
from browser_driver import PlaywrightBrowser, origin, open_browser
from playwright.async_api import Error

from openai import AsyncOpenAI
from openai.lib.browser import BrowserError, AsyncBrowserToolset
from openai.types.responses import ResponseFunctionToolCall


async def check_driver_boundaries() -> None:
    denied_requests: list[str] = []

    class DeniedHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            denied_requests.append(self.path)
            self.send_response(200)
            self.end_headers()

        @override
        def log_message(self, format: str, *args: object) -> None:
            pass

    denied = ThreadingHTTPServer(("127.0.0.1", 0), DeniedHandler)
    denied_url = f"http://127.0.0.1:{denied.server_port}/denied"

    class AllowedHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", denied_url)
                self.end_headers()
                return
            body = (
                "<!doctype html><title>Boundary fixture</title>"
                '<input type="password" aria-label="Password" value="SYNTHETIC_PASSWORD">'
                '<label for="hidden-label" hidden>HIDDEN_LABEL_SECRET</label><input id="hidden-label">'
                '<button id="first" onclick="document.body.dataset.clicked=\'first\'">First<span hidden>HIDDEN_CHILD_SECRET</span></button>'
                '<button id="second" onclick="document.body.dataset.clicked=\'second\'">Second</button>'
                f'<a target="_blank" href="{denied_url}">Popup</a><a href="/redirect">Redirect</a>'
                '<script>window.privateFixture="HIDDEN_SCRIPT_SECRET";</script>'
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        @override
        def log_message(self, format: str, *args: object) -> None:
            pass

    allowed = ThreadingHTTPServer(("127.0.0.1", 0), AllowedHandler)
    servers = [allowed, denied]
    threads = [Thread(target=server.serve_forever, daemon=True) for server in servers]
    for thread in threads:
        thread.start()
    url = f"http://127.0.0.1:{allowed.server_port}/"
    try:
        async with open_browser(url) as driver:
            for status, fail in ((200, False), (301, False), (200, True)):
                route = AsyncMock()
                route.request = SimpleNamespace(url=url)
                response = SimpleNamespace(status=status, dispose=AsyncMock())
                route.fetch.return_value = response
                if fail:
                    route.fulfill.side_effect = Error("Synthetic response consumption failure")
                await driver.guard(route)
                route.fetch.assert_awaited_once_with(max_redirects=0, timeout=0)
                response.dispose.assert_awaited_once_with()
                if status == 301 or fail:
                    route.abort.assert_awaited_once_with("failed")
                else:
                    route.abort.assert_not_awaited()
            initial = await driver.find({"tab_id": "1", "query": "First"})
            assert not isinstance(initial, str)
            assert [item["label"] for item in initial["elements"]] == ["First"]
            observed = await driver.read_page({"tab_id": "1", "filter": "all"})
            assert not isinstance(observed, str) and observed["version"] == 1
            assert "SYNTHETIC_PASSWORD" not in json.dumps(observed) and "_SECRET" not in json.dumps(observed)
            assert "_SECRET" not in await driver.get_page_text({"tab_id": "1"})
            refs = {item["label"]: item["ref"] for item in observed["elements"]}
            first = refs["First"]
            _, page = driver.page("1")
            await page.evaluate(
                "ref => { const a=document.querySelector('#first'); const b=document.querySelector('#second'); b.dataset.sdkBrowserRef=ref; a.before(b); }",
                first,
            )
            await driver.click({"tab_id": "1", "target": first})
            assert await page.locator("body").get_attribute("data-clicked") == "first"
            await driver.click({"tab_id": "1", "target": refs["Popup"]})
            await driver.click({"tab_id": "1", "target": refs["Redirect"]})
            assert denied_requests == []
            await driver.navigate({"tab_id": "1", "url": url})
            refreshed = await driver.find({"tab_id": "1", "query": "First"})
            assert not isinstance(refreshed, str)
            next_ref = next(item["ref"] for item in refreshed["elements"] if item["label"] == "First")
            assert next_ref != first
            try:
                await driver.click({"tab_id": "1", "target": first})
                raise AssertionError("A stale reference was accepted.")
            except BrowserError:
                pass
            await page.evaluate("() => { const b=document.querySelector('#first'); b.replaceWith(b.cloneNode(true)); }")
            try:
                await driver.click({"tab_id": "1", "target": next_ref})
                raise AssertionError("A replaced element was accepted.")
            except BrowserError:
                pass
            assert await page.locator("body").get_attribute("data-clicked") is None
            assert denied_requests == []
            await page.set_content('<main id="fixture"></main>')
            await page.evaluate("""() => {
              const main = document.querySelector('#fixture');
              const text = document.createElement('p');
              text.textContent = 'Visible text '.repeat(4000);
              main.append(text);
              for (let count=0; count < 2400; count+=1) {
                const item = document.createElement('button');
                item.textContent = `Item ${count}`;
                main.append(item);
              }
              const secret = document.createElement('input');
              secret.type = 'password';
              secret.value = 'LOCAL_PASSWORD_SENTINEL';
              main.prepend(secret);
            }""")
            limited = await driver.read_page({"tab_id": "1", "filter": "all"})
            assert not isinstance(limited, str) and limited["version"] == 1
            assert len(limited["elements"]) == 100
            assert set(limited["omitted"]) >= {"target_limit", "text_limit", "work_limit"}
            assert len(json.dumps(limited, ensure_ascii=False).encode()) <= 65536
            assert "LOCAL_PASSWORD_SENTINEL" not in json.dumps(limited)
            text_only = await driver.get_page_text({"tab_id": "1"})
            assert isinstance(text_only, str) and len(text_only.encode()) <= 16384
            found = await driver.find({"tab_id": "1", "query": limited["elements"][0]["label"]})
            assert not isinstance(found, str)
            assert any(item["label"] == limited["elements"][0]["label"] for item in found["elements"])
            assert all(item["ref"] != limited["elements"][0]["ref"] for item in found["elements"])
            await page.set_content(
                '<label for="field">Note</label><input id="field">'
                '<label for="choice">Service</label><select id="choice">'
                '<option value="standard">Standard</option><option value="express">Express</option></select>'
            )
            form = await driver.read_page({"tab_id": "1", "filter": "interactive"})
            assert not isinstance(form, str)
            field_ref = next(item["ref"] for item in form["elements"] if item["label"] == "Note")
            choice_ref = next(item["ref"] for item in form["elements"] if item["label"] == "Service")
            await driver.type({"tab_id": "1", "target": field_ref, "text": "Initial"})
            await driver.type({"tab_id": "1", "target": field_ref, "text": "Updated"})
            assert await page.locator("#field").input_value() == "Updated"
            await driver.select_option({"tab_id": "1", "target": choice_ref, "values": ["express"]})
            await driver.select_option({"tab_id": "1", "target": choice_ref, "values": ["standard"]})
            await driver.select_option({"tab_id": "1", "target": choice_ref, "values": ["express"]})
            assert await page.locator("#choice").input_value() == "express"
            await page.locator('option[value="standard"]').evaluate(
                "(node) => { node.textContent = 'Different service'; }"
            )
            try:
                await driver.select_option({"tab_id": "1", "target": choice_ref, "values": ["standard"]})
            except BrowserError:
                pass
            else:
                raise AssertionError("An old reference selected an option whose value now means something else.")
            assert await page.locator("#choice").input_value() == "express"
            await page.set_content('<base href="/before/"><a href="receipt">Local receipt</a>')
            local = await driver.read_page({"tab_id": "1", "filter": "interactive"})
            assert not isinstance(local, str)
            local_link = local["elements"][0]["ref"]
            await page.locator("base").evaluate("(node) => { node.href='/after/'; }")
            try:
                await driver.click({"tab_id": "1", "target": local_link})
            except Exception:
                pass
            else:
                raise AssertionError("A local link used a different destination than its read.")
            assert page.url == url
            await page.set_content('<label for="check">Include</label><input type="checkbox" id="check">')
            check_read = await driver.read_page({"tab_id": "1", "filter": "interactive"})
            assert not isinstance(check_read, str)
            check_ref = check_read["elements"][0]["ref"]
            await page.locator("#check").evaluate("(node) => { node.checked = true; }")
            try:
                await driver.click({"tab_id": "1", "target": check_ref})
            except BrowserError:
                pass
            else:
                raise AssertionError("A checkbox ref toggled a state different from its read.")
            assert await page.locator("#check").is_checked()
            fresh_check = await driver.read_page({"tab_id": "1", "filter": "interactive"})
            assert not isinstance(fresh_check, str)
            await driver.click({"tab_id": "1", "target": fresh_check["elements"][0]["ref"]})
            assert not await page.locator("#check").is_checked()
            await page.set_content('<label for="note">Note</label><textarea id="note"></textarea>')
            await page.locator("#note").fill("😺" * 128 + "\t")
            tools = AsyncBrowserToolset(driver, members=["read_page"])
            result = await tools.execute(
                ResponseFunctionToolCall(
                    name="browser_read_page",
                    call_id="local-multibyte-budget",
                    type="function_call",
                    arguments=json.dumps({"tab_id": "1", "filter": "interactive"}),
                )
            )
            blocks = result["output"]
            assert isinstance(blocks, list)
            output = blocks[0]
            assert output["type"] == "input_text"
            multibyte = json.loads(output["text"])
            assert multibyte["ok"] is True
            assert multibyte["result"]["elements"][0]["value"] == "😺" * 128
            assert "value" in multibyte["result"]["omitted"]
            for changed, selector, attribute, value in (
                ("label", "#action", "aria-label", "Revised action"),
                ("role", "#action", "role", "switch"),
                ("disabled", "#action", "disabled", ""),
                ("inline action", "#action", "onclick", "document.body.dataset.effects='1'"),
                ("destination", "#link", "href", "/updated"),
                ("private field", "#field", "type", "password"),
                ("readonly field", "#field", "readonly", ""),
                ("form destination", "#form", "action", "/updated"),
            ):
                await page.set_content(
                    '<form id="form"><button id="action" type="button">Action</button>'
                    '<a id="link" href="/original">Link</a><label for="field">Note</label><input id="field"></form>'
                )
                read = await driver.read_page({"tab_id": "1", "filter": "interactive"})
                assert not isinstance(read, str)
                wanted = "Link" if selector == "#link" else "Note" if selector == "#field" else "Action"
                target = next(item["ref"] for item in read["elements"] if item["label"] == wanted)
                await page.locator(selector).evaluate(
                    "(node, change) => node.setAttribute(change.attribute, change.value)",
                    {"attribute": attribute, "value": value},
                )
                try:
                    if wanted == "Note":
                        await driver.type({"tab_id": "1", "target": target, "text": "Synthetic note"})
                    else:
                        await driver.click({"tab_id": "1", "target": target})
                except BrowserError:
                    pass
                else:
                    raise AssertionError(f"Changed borrowed {changed} accepted the old reference")
                assert await page.locator("#field").input_value() == ""
                assert await page.locator("body").get_attribute("data-effects") is None
        print("PASS: stale, forged and replaced refs, hidden/password content, and redirect/popup origin guards.")
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join()


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    await check_driver_boundaries()
    requests = 0

    with fixture_server() as url:
        async with open_browser(url) as driver:

            def transport(request: httpx2.Request) -> httpx2.Response:
                nonlocal requests
                requests += 1
                body = json.loads(request.content)
                base: dict[str, object] = {
                    "id": f"resp_{requests}",
                    "object": "response",
                    "created_at": 0,
                    "status": "completed",
                    "model": "",
                }

                def calls(actions: list[tuple[str, dict[str, object]]]) -> httpx2.Response:
                    return httpx2.Response(
                        200,
                        json={
                            **base,
                            "output": [
                                {
                                    "id": f"fc_{requests}_{index}",
                                    "call_id": f"call_{requests}_{index}",
                                    "type": "function_call",
                                    "status": "completed",
                                    "name": name,
                                    "arguments": json.dumps(arguments),
                                }
                                for index, (name, arguments) in enumerate(actions)
                            ],
                        },
                    )

                if requests == 1:
                    return calls(
                        [
                            ("browser_read_page", {"tab_id": None, "filter": "interactive"}),
                            ("lookup_code", {}),
                        ]
                    )
                if requests == 2:
                    outputs = {
                        item["call_id"]: item["output"]
                        for item in body["input"]
                        if item.get("type") == "function_call_output"
                    }
                    observed = json.loads(outputs["call_1_0"][0]["text"])
                    assert observed["ok"] is True
                    assert observed["result"]["version"] == 1
                    refs = {item["label"]: item["ref"] for item in observed["result"]["elements"]}
                    party = next(item for item in observed["result"]["elements"] if item["label"] == "Party size")
                    assert [choice["value"] for choice in party["options"]] == ["1", "2", "4"]
                    code = json.loads(outputs["call_1_1"])["code"]
                    return calls(
                        [
                            ("browser_type", {"target": refs["Name"], "text": "Ada", "tab_id": None}),
                            ("browser_select_option", {"target": refs["Party size"], "values": ["2"], "tab_id": None}),
                            ("browser_select_option", {"target": refs["Time"], "values": ["18:00"], "tab_id": None}),
                            ("browser_type", {"target": refs["Confirmation code"], "text": code, "tab_id": None}),
                            ("browser_click", {"target": refs["Reserve"], "tab_id": None}),
                            ("browser_new_tab", {"url": url + "notes"}),
                            ("browser_get_page_text", {"tab_id": "2"}),
                            ("browser_switch_tab", {"tab_id": "1"}),
                            ("browser_screenshot", {"tab_id": "1"}),
                        ]
                    )
                assert requests == 3
                final = body["input"][-1]
                assert final["type"] == "function_call_output"
                assert final["output"][1]["type"] == "input_image"
                png = base64.b64decode(final["output"][1]["image_url"].split(",", 1)[1], validate=True)
                assert png.startswith(bytes.fromhex("89504e470d0a1a0a"))
                if args.screenshot:
                    args.screenshot.write_bytes(png)
                return httpx2.Response(
                    200,
                    json={
                        **base,
                        "output": [
                            {
                                "id": "msg_done",
                                "type": "message",
                                "role": "assistant",
                                "status": "completed",
                                "phase": "final_answer",
                                "content": [
                                    {"type": "output_text", "text": "Scripted reservation complete.", "annotations": []}
                                ],
                            }
                        ],
                    },
                )

            async with AsyncOpenAI(
                api_key="fixture-key-not-real",
                base_url="http://fixture.invalid/v1",
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
            ) as client:
                result = await make_runner(driver, auto_approve_fixture=True).run(
                    client, {"model": "", "input": "Exercise the synthetic reservation", "store": False}, max_steps=4
                )
            _, page = driver.page("1")
            reservation: object = await page.evaluate("window.reservation")
            assert reservation == {"name": "Ada", "size": "2", "time": "18:00", "code": "SDK-42"}
            assert len((await driver.state())["tabs"]) == 2 and driver.active == "1"
            assert result.output_text == "Scripted reservation complete."
            browser = driver.context.browser
            assert browser is not None
            for event in ("dialog", "download"):
                disposable = await browser.new_context(service_workers="block")
                owned = PlaywrightBrowser(disposable, {origin(url)}, owned_fixture_urls=frozenset({url}))
                await owned.new_tab({"url": url})
                failed = AsyncMock()
                failed.type = "alert"
                failed.dismiss.side_effect = Error("Synthetic event transport closed")
                failed.cancel.side_effect = Error("Synthetic event transport closed")
                if event == "dialog":
                    await owned._dismiss(failed, "1")
                    failed.dismiss.assert_awaited_once_with()
                else:
                    await owned._download(failed, "1")
                    failed.cancel.assert_awaited_once_with()
                try:
                    await owned.state()
                except RuntimeError as error:
                    assert "retired" in str(error)
                else:
                    raise AssertionError(f"{event} failure left an uncertain context usable")
                await disposable.close()
            print("PASS: structured refs, form, function, tabs and native image output drove a real browser.")


if __name__ == "__main__":
    asyncio.run(main())
