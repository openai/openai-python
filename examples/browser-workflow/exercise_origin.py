"""Check that another website cannot load local workflow data as a script."""

import asyncio

from workflow import serve
from playwright.async_api import Error, async_playwright


async def main() -> None:
    with serve() as protected, serve() as other:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                page = await browser.new_page()
                await page.goto(other[0] + "/inbox?fixture=A")
                assert await page.evaluate("Boolean(window.workflowFixtures?.A)")
                await page.evaluate("delete window.workflowFixtures")
                try:
                    await page.add_script_tag(url=protected[0] + "/fixtures.js")
                except Error:
                    pass
                else:
                    raise AssertionError("Another origin loaded local workflow fixtures")
                assert await page.evaluate("window.workflowFixtures === undefined")
                await page.add_script_tag(url=other[0] + "/fixtures.js")
                assert await page.evaluate("Boolean(window.workflowFixtures?.A)")
            finally:
                await browser.close()
    print("PASS local scripts load, while another origin cannot load workflow fixtures")


if __name__ == "__main__":
    asyncio.run(main())
