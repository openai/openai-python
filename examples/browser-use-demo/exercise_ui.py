"""Check private-link UI, actual pixels and the owned reservation report."""

from __future__ import annotations

import json
import asyncio

from server import serve
from booking import BookingBrowser
from read_only import example_browser_channel
from playwright.async_api import async_playwright

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
            await dashboard.goto(app.launch_url)
            await dashboard.wait_for_function("location.hash === ''")
            assert app.token not in await dashboard.content()
            await dashboard.locator("#mode").select_option("rehearsal")
            await dashboard.locator("#start").click()
            await dashboard.locator("#approval").wait_for(state="visible", timeout=25000)
            await dashboard.wait_for_function("""() => {
              const image = document.querySelector('#screen');
              return image.naturalWidth === 1024 && getComputedStyle(image).display !== 'none';
            }""")
            await dashboard.locator("#refuse").click()
            await dashboard.wait_for_function(
                "() => document.querySelector('#status').textContent.toLowerCase().includes('refus')"
            )
            print("PASS UI: private link, real pixels, refusal; report has actual status and options.")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
