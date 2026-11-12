"""Check private-link UI, actual pixels and the owned reservation report."""

from __future__ import annotations

import json
import asyncio

from server import serve
from booking import BookingBrowser
from read_only import example_browser_channel
from playwright.async_api import Route, async_playwright

from openai.lib.browser import AsyncBrowserToolset
from openai.types.responses import ResponseFunctionToolCall


async def main() -> None:
    async with serve() as app, async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True, channel=example_browser_channel(), chromium_sandbox=True
        )
        try:
            context = await browser.new_context()
            driver = BookingBrowser(context, app.origin + "/fixture/reservation")
            await context.route("**/*", driver.guard)
            await driver.open()
            text_tools = AsyncBrowserToolset(driver, members=["get_page_text"])
            text_result = await text_tools.execute(
                ResponseFunctionToolCall(
                    type="function_call",
                    id="text",
                    call_id="text",
                    name=text_tools.tools[0]["name"],
                    arguments='{"tab_id":null}',
                )
            )
            output = text_result["output"]
            assert isinstance(output, list)
            block = output[0]
            assert block["type"] == "input_text"
            assert json.loads(block["text"])["ok"] is True
            before = await driver.read_page({"tab_id": None, "filter": "all"})
            assert "TABLE-204" not in before["text"] and "Confirmed" not in before["text"]
            controls = {item["label"]: item for item in before["elements"]}
            assert [item["value"] for item in controls["Time"].get("options", [])] == ["", "17:00", "18:00", "19:00"]
            await driver.type({"tab_id": None, "target": controls["Guest name"]["ref"], "text": "Ada"})
            for label, value in (("Party size", "2"), ("Time", "18:00"), ("Seating", "Indoor")):
                await driver.select_option({"tab_id": None, "target": controls[label]["ref"], "values": [value]})
            await driver.click({"tab_id": None, "target": controls["Reserve table"]["ref"]})
            text = await driver.get_page_text({"tab_id": None})
            assert text["elements"] == [] and "TABLE-204" in text["text"]
            after = await driver.read_page({"tab_id": None, "filter": "all"})
            assert "Confirmed" in after["text"] and "TABLE-204" in after["text"]
            assert not any(item["label"] == "Reserve table" for item in after["elements"])
            time = next(item for item in after["elements"] if item["label"] == "Time")
            assert [item["value"] for item in time.get("options", []) if item.get("selected")] == ["18:00"]
            await context.close()

            dashboard = await browser.new_page()
            await dashboard.add_init_script("""const decode = HTMLImageElement.prototype.decode;
              HTMLImageElement.prototype.decode = async function () {
                await decode.call(this);
                if (this.id === 'screen' && !document.getElementById('approval').hidden) {
                  HTMLImageElement.prototype.decode = decode;
                  await new Promise(resolve => { window.releaseApprovalFrame = resolve; });
                }
              };""")
            await dashboard.goto(app.launch_url)
            await dashboard.wait_for_function("location.hash === ''")
            assert app.token not in await dashboard.content()
            await dashboard.locator("#mode").select_option("rehearsal")
            await dashboard.locator("#start").click()
            await dashboard.locator("#approval").wait_for(state="visible", timeout=25000)
            await dashboard.wait_for_function("() => typeof window.releaseApprovalFrame === 'function'")
            approval_disabled = await dashboard.locator("#approve").is_disabled()
            refusal_enabled = await dashboard.locator("#refuse").is_enabled()
            await dashboard.evaluate("() => window.releaseApprovalFrame()")
            await dashboard.wait_for_function("""() => {
              const image = document.querySelector('#screen');
              return image.naturalWidth === 1024 && getComputedStyle(image).display !== 'none';
            }""")
            await dashboard.locator("#refuse").click()
            await dashboard.wait_for_function(
                "() => document.querySelector('#status').textContent.toLowerCase().includes('refus')"
            )
            assert approval_disabled and refusal_enabled
            await dashboard.locator("#start").click()
            await dashboard.locator("#approval").wait_for(state="visible", timeout=25000)
            await dashboard.locator("#take-control").click(timeout=25000)
            await dashboard.wait_for_function(
                "() => !document.querySelector('#human-controls').disabled", timeout=15000
            )
            second = await browser.new_page()
            await second.goto(app.launch_url)
            await second.wait_for_function("() => !document.querySelector('#human-controls').disabled")
            assert app.current is not None
            initial = await app.current.binding()
            assert initial is not None
            state_held, state_release = asyncio.Event(), asyncio.Event()

            async def held_state(route: Route) -> None:
                state_held.set()
                await state_release.wait()
                await route.continue_()

            sent: list[str] = []
            dashboard.on("request", lambda request: sent.append(request.url) if "/api/input" in request.url else None)
            await dashboard.route("**/api/state", held_state)
            try:
                await asyncio.wait_for(state_held.wait(), 5)
                await dashboard.evaluate("""() => {
                  const screen = document.getElementById('screen');
                  const decode = screen.decode.bind(screen);
                  screen.decode = async () => {
                    await decode();
                    await new Promise(resolve => { window.releaseFrameDecode = resolve; });
                  };
                }""")
                await second.locator("#human-key").select_option("Tab")
                await second.locator("#send-key").click()
                await second.wait_for_function("() => !document.querySelector('#human-controls').disabled")
                current = await app.current.binding()
                assert current is not None and current["sequence"] != initial["sequence"]
                previous_frame = await dashboard.locator("#screen").get_attribute("src")
                state_release.set()
                await dashboard.wait_for_function(
                    "previous => document.getElementById('screen').src !== previous", arg=previous_frame
                )
                controls = await dashboard.evaluate("""() => {
                  const ids = ['send-text', 'send-key', 'send-scroll'];
                  return {
                    disabled: ids.every(id => document.getElementById(id).matches(':disabled')),
                    screen: document.getElementById('screen').getAttribute('aria-disabled'),
                  };
                }""")
                assert controls == {"disabled": True, "screen": "true"}, controls
                await dashboard.evaluate("""() => {
                  for (const id of ['send-text', 'send-key', 'send-scroll'])
                    document.getElementById(id).click();
                }""")
                assert not sent, sent
                await dashboard.wait_for_function("() => typeof window.releaseFrameDecode === 'function'")
                await dashboard.evaluate("() => window.releaseFrameDecode?.()")
                await dashboard.wait_for_function(
                    "() => !document.querySelector('#human-controls').disabled", timeout=10000
                )
                print("PASS manual input waits for the displayed frame after another dashboard changes focus.")
            finally:
                state_release.set()
                await dashboard.evaluate("() => window.releaseFrameDecode?.()")
                await dashboard.unroute("**/api/state", held_state)
                await second.close()
                await dashboard.locator("#stop").click()
            print("PASS UI: private link, real pixels, refusal; report has actual status and options.")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
