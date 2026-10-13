"""Finite local Chromium observations for explicit waits and borrowed editing hosts."""

from __future__ import annotations

import sys
import json
import asyncio
import threading
from typing import Any
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

from browser_driver import PlaywrightBrowser
from playwright.async_api import async_playwright


class Fixture(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<!doctype html><title>Fixture</title><h1>Ready marker</h1>")

    @override
    def log_message(self, format: str, *args: object) -> None:
        pass


async def main() -> None:
    mode = sys.argv[1]
    assert mode in ("wait", "editable")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    urls = frozenset(f"{origin}/{letter}" for letter in "abc")
    checked: list[str] = []
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            try:
                if mode == "editable":
                    context = await browser.new_context()
                    try:
                        driver = PlaywrightBrowser(context, {origin})
                        await driver.new_tab({"url": f"{origin}/a"})
                        tab, page = driver.page(None)
                        await page.set_content("""<!doctype html>
                            <div contenteditable aria-label="Bare">before</div>
                            <div contenteditable="true" aria-label="True">before</div>
                            <div contenteditable="plaintext-only" aria-label="Plain">before</div>
                            <div contenteditable="true" aria-label="Root"><span aria-label="Inherited">text</span>
                              <div contenteditable="false" aria-label="Excluded"><span aria-label="False child">fixed</span></div>
                            </div>
                            <div contenteditable="false" aria-label="False">fixed
                              <div contenteditable="true" aria-label="Island">before</div>
                            </div>""")
                        report = await driver.read_page({"tab_id": tab, "filter": "interactive"})
                        assert not isinstance(report, str)
                        assert [item["label"] for item in report["elements"]] == [
                            "Bare",
                            "True",
                            "Plain",
                            "Root",
                            "Island",
                        ]
                        assert all(item["role"] == "textbox" for item in report["elements"])
                        for name in ("Bare", "True", "Plain", "Island"):
                            item = next(value for value in report["elements"] if value["label"] == name)
                            await driver.type({"tab_id": tab, "target": item["ref"], "text": f"edited {name}"})
                            assert await page.get_by_label(name).text_content() == f"edited {name}"
                        root = next(value for value in report["elements"] if value["label"] == "Root")
                        await page.get_by_label("Root").evaluate(
                            "(node) => node.setAttribute('contenteditable', 'false')"
                        )
                        try:
                            await driver.type({"tab_id": tab, "target": root["ref"], "text": "must not apply"})
                        except Exception:
                            pass
                        else:
                            raise AssertionError("changed editability kept a reference")
                        assert "must not apply" not in (await page.get_by_label("Root").text_content() or "")
                        checked.append("hosts and stale guard")
                    finally:
                        await context.close()
                else:
                    for change in (
                        "background",
                        "other_focus",
                        "implicit_focus",
                        "selected_navigation",
                        "selected_close",
                    ):
                        context = await browser.new_context(service_workers="block")
                        try:
                            driver = PlaywrightBrowser(context, {origin}, owned_fixture_urls=urls)
                            await driver.new_tab({"url": f"{origin}/a"})
                            a, page = driver.page(None)
                            await driver.new_tab({"url": f"{origin}/b"})
                            b, _ = driver.page(None)
                            await driver.new_tab({"url": f"{origin}/c"})
                            if change == "implicit_focus":
                                await driver.switch_tab({"tab_id": a})
                            target = None if change == "implicit_focus" else a
                            wait = driver.wait_for
                            assert wait is not None
                            if change == "background":
                                assert (
                                    await wait({"tab_id": target, "text": "Ready marker", "timeout_ms": 4000})
                                    == "Visible condition met."
                                )
                            else:
                                entered, release = asyncio.Event(), asyncio.Event()
                                frame = page.main_frame
                                native = frame.locator
                                held = False

                                def locator(
                                    *args: Any,
                                    _native: Any = native,
                                    _entered: asyncio.Event = entered,
                                    _release: asyncio.Event = release,
                                    **kwargs: Any,
                                ) -> Any:
                                    found = _native(*args, **kwargs)
                                    if args[0] == "html" and not held:
                                        evaluate = found.evaluate_handle

                                        async def hold(*values: Any, **options: Any) -> Any:
                                            nonlocal held
                                            result = await evaluate(*values, **options)
                                            held = True
                                            _entered.set()
                                            await _release.wait()
                                            return result

                                        found.evaluate_handle = hold
                                    return found

                                frame.locator = locator
                                pending = asyncio.ensure_future(
                                    wait({"tab_id": target, "text": "Ready marker", "timeout_ms": 4000})
                                )
                                await entered.wait()
                                try:
                                    if change.endswith("focus"):
                                        await driver.switch_tab({"tab_id": b})
                                    if change == "selected_navigation":
                                        await page.reload()
                                    if change == "selected_close":
                                        await page.close()
                                finally:
                                    release.set()
                                (result,) = await asyncio.gather(pending, return_exceptions=True)
                                if change == "other_focus":
                                    assert result == "Visible condition met.", result
                                else:
                                    assert isinstance(result, BaseException), (change, result)
                            checked.append(change)
                        finally:
                            await context.close()
            finally:
                await browser.close()
    finally:
        server.shutdown()
        worker.join()
        server.server_close()
    print(json.dumps({"mode": mode, "checked": checked}))


if __name__ == "__main__":
    asyncio.run(main())
