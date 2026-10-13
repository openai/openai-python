"""Use the actual shared dashboard in Chromium, then check failure cleanup."""

from __future__ import annotations

import socket
import asyncio
from unittest.mock import patch

from server import Fieldwork, serve
from exercise_controls import main as check_browser_controls
from playwright.async_api import Request


async def main() -> None:
    async with serve(0) as app:
        page = await app.browser.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        anonymous = await app.browser.new_page()
        anonymous_requests: list[str] = []
        anonymous.on("request", lambda req: anonymous_requests.append(req.url) if "/api/" in req.url else None)
        await anonymous.goto(app.origin)
        await anonymous.locator("#message").get_by_text("Open the private link", exact=False).wait_for()
        assert await anonymous.locator("#start").is_disabled()
        await anonymous.goto(app.origin + "/traces")
        await anonymous.locator("#status").get_by_text("Open the private link", exact=False).wait_for()
        assert await anonymous.locator("#reload").is_disabled()
        assert not anonymous_requests
        await anonymous.close()
        leaks: list[bool] = []
        authorized: list[bool] = []

        def check_request(request: Request) -> None:
            headers = request.headers
            if app.token in request.url or app.token in headers.get("referer", ""):
                leaks.append(True)
            if request.url == app.origin + "/api/state" and headers.get("x-demo-token") == app.token:
                authorized.append(True)

        page.on("request", check_request)
        await page.goto(app.launch_url)
        await page.wait_for_function("document.querySelector('#availability').textContent.includes('rehearsal')")
        assert page.url == app.origin + "/"
        assert authorized
        await page.get_by_text("Usage and diagnostics", exact=True).click()
        await page.get_by_role("link", name="Open saved trace viewer (view only)").click()
        await page.wait_for_function("document.querySelector('#status').textContent.includes('No capture')")
        assert page.url == app.origin + "/traces"
        await page.get_by_role("link", name="Return to live dashboard").click()
        await page.wait_for_function("document.querySelector('#availability').textContent.includes('rehearsal')")
        assert page.url == app.origin + "/"
        await page.reload()
        await page.locator("#message").get_by_text("Open the private link", exact=False).wait_for()
        assert await page.locator("#start").is_disabled()
        assert not leaks
        print(
            "PASS unauthenticated pages never poll; owner navigation and reload remove fragment; URLs/referrers do not leak"
        )
        await page.goto(app.launch_url)
        await page.locator('[data-task="invoices"]').click()
        await page.locator("#mode").select_option("rehearsal")
        await page.locator("#start").click()
        await page.locator("#approval").wait_for(state="visible", timeout=10000)
        await page.wait_for_function("""() => {
          const image=document.querySelector('#screen');
          return image.naturalWidth===1024 && !document.querySelector('#take-control').disabled;
        }""")
        await page.locator("#take-control").click()
        await page.wait_for_function(
            "() => document.querySelector('#owner-status').textContent.includes('You control') && !document.querySelector('#open-notes').disabled"
        )
        assert await page.locator("#approval").is_hidden()
        await page.locator("#open-notes").click()
        await page.wait_for_function("""() => {
            const tabs=document.querySelector('#browser-tab');
            return tabs.selectedOptions[0]?.textContent==='Notes' && !document.querySelector('#return-control').disabled;
        }""")
        await page.locator("#return-control").click()
        await page.locator("#approval").wait_for(state="visible")
        await page.locator("#approve").click()
        await page.wait_for_function("() => document.querySelector('#status').textContent.includes('Verified')")
        assert not errors, errors
        print("PASS actual shared UI: current pixels, approval, Take, Notes, Return, fresh approval and verification")
        await page.close()

    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]

    async def failed_close(_self: Fieldwork) -> None:
        raise RuntimeError("fixture teardown failure")

    with patch.object(Fieldwork, "close", failed_close):
        try:
            async with serve(port):
                pass
        except RuntimeError as exc:
            assert str(exc) == "fixture teardown failure"
        else:
            raise AssertionError("Expected the teardown failure")
    # A subsequent startup at the identical address proves the listener was retired.
    async with serve(port) as again:
        assert again.origin.endswith(":" + str(port))
    print("PASS listener and Chromium retired after app.close failure")
    await check_browser_controls()


if __name__ == "__main__":
    asyncio.run(main())
