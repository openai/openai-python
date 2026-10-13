"""Check bounded find results and origin-only state in a local browser."""

import asyncio

from browser_driver import PlaywrightBrowser
from playwright.async_api import async_playwright


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            context = await browser.new_context()
            buttons = "".join(
                f"<button>{'Target early' if index == 0 else f'Choice {index}'}</button>" for index in range(100)
            )
            html = buttons + "<button>Target late</button><button>Straße</button>"
            html += f'<a href="/{"x" * 4097}">Overbudget link</a><output></output>'
            html += """<script>document.addEventListener('click', event => {
              if (event.target.tagName === 'BUTTON') document.querySelector('output').textContent = event.target.textContent;
            });</script>"""
            await context.route("**/*", lambda route: route.fulfill(content_type="text/html; charset=utf-8", body=html))
            page = await context.new_page()
            await page.goto("https://fixture.invalid/private/" + "x" * 20_000 + "?token=local#secret")
            driver = PlaywrightBrowser(context, {"https://fixture.invalid"})
            state = await driver.state()
            assert state["tabs"][0]["url"] == "https://fixture.invalid"
            tab_id = state["tabs"][0]["id"]
            initial = await driver.read_page({"tab_id": tab_id, "filter": "interactive"})
            assert isinstance(initial, dict)
            assert len(initial["elements"]) == 100 and "target_limit" in initial["omitted"]
            found = await driver.find({"tab_id": tab_id, "query": "Target"})
            assert isinstance(found, dict)
            assert [item["label"] for item in found["elements"]] == ["Target early", "Target late"]
            await driver.click({"tab_id": tab_id, "target": found["elements"][0]["ref"]})
            assert await page.locator("output").text_content() == "Target early"
            await driver.click({"tab_id": tab_id, "target": found["elements"][1]["ref"]})
            assert await page.locator("output").text_content() == "Target late"
            folded = await driver.find({"tab_id": tab_id, "query": "STRASSE"})
            assert isinstance(folded, dict)
            assert [item["label"] for item in folded["elements"]] == ["Straße"]
            all_items = await driver.find({"tab_id": tab_id, "query": ""})
            assert isinstance(all_items, dict)
            assert len(all_items["elements"]) == 100 and "target_limit" in all_items["omitted"]
            excluded = await driver.find({"tab_id": tab_id, "query": "Overbudget"})
            assert isinstance(excluded, dict)
            assert not excluded["elements"] and "unsupported_control" in excluded["omitted"]
            await context.close()
            print(
                "PASS origin-only state, bounded read/find, late reference actions, Unicode match, oversized binding refusal"
            )
        finally:
            await browser.close()


asyncio.run(main())
