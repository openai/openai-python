"""Local Chromium proof for opt-in diagnostic and script tools; no API calls."""

from __future__ import annotations

import sys
import json
import asyncio
from typing import Any, Callable, Awaitable
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import patch
from typing_extensions import override

from sensitive_driver import create_sensitive_driver
from playwright.async_api import async_playwright

from openai.lib.browser import BrowserError, AsyncBrowserToolset, BrowserConfirmContext
from openai.types.responses import ResponseFunctionToolCall


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        html = Path(__file__).with_name("sensitive-fixture.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


class Blocked(BaseHTTPRequestHandler):
    escaped = 0

    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        Blocked.escaped += 1
        self.send_response(200)
        self.end_headers()


async def approve(_ctx: BrowserConfirmContext) -> bool:
    return True


async def main(url: str, blocked: str) -> None:
    sequence = 0

    async def execute(
        tools: AsyncBrowserToolset, member: str, args: dict[str, object], cancelled: Callable[[], bool] | None = None
    ) -> dict[str, Any]:
        nonlocal sequence
        sequence += 1
        result = await tools.execute(
            ResponseFunctionToolCall(
                type="function_call",
                status="completed",
                id=f"i{sequence}",
                call_id=f"c{sequence}",
                name=f"browser_{member}",
                arguments=json.dumps(args),
            ),
            cancelled=cancelled,
        )
        blocks = result["output"]
        assert isinstance(blocks, list) and blocks[0]["type"] == "input_text"
        return json.loads(blocks[0]["text"])

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            disabled_context = await browser.new_context(service_workers="block")
            disabled = await create_sensitive_driver(disabled_context, url)
            assert disabled.read_diagnostics is None and disabled.run_script is None
            await disabled_context.close()

            context = await browser.new_context(service_workers="block")
            driver = await create_sensitive_driver(context, url, diagnostics=True, scripts=True)
            await driver.new_tab({"url": url})
            _, page = driver.page(None)
            tools = AsyncBrowserToolset(
                driver, members=["read_page", "read_diagnostics", "run_script", "click"], confirm=approve
            )
            visible = await execute(tools, "read_page", {"tab_id": None, "filter": "all"})
            assert "SENTINEL" not in visible["result"]["text"] and "synthetic-42" not in visible["result"]["text"]
            diagnostics: dict[str, object] = {"tab_id": None, "source": "console", "limit": 100}
            first = await execute(tools, "read_diagnostics", diagnostics)
            second = await execute(tools, "read_diagnostics", diagnostics)
            assert first["result"] == second["result"]
            assert "console:warning" in first["result"]["text"]
            network = await execute(tools, "read_diagnostics", {**diagnostics, "source": "network"})
            assert "failed" in network["result"]["text"]
            assert "SENTINEL" not in json.dumps([first, network])
            assert first["result"]["elements"] == []
            script = await execute(
                tools,
                "run_script",
                {
                    "tab_id": None,
                    "timeout_ms": 2000,
                    "source": "document.querySelector('#box').setAttribute('x','70');"
                    f"await fetch({json.dumps(blocked)}).catch(() => null); return window.fixtureValue;",
                },
            )
            assert script["result"] == "synthetic-42"
            assert await page.locator("#box").get_attribute("x") == "70"
            assert Blocked.escaped == 0
            stale = await execute(tools, "click", {"tab_id": None, "target": visible["result"]["elements"][0]["ref"]})
            assert stale["ok"] is False
            await context.close()

            root_url = url.rsplit("/", 1)[0]
            root_context = await browser.new_context(service_workers="block")
            root_driver = await create_sensitive_driver(root_context, root_url, diagnostics=True)
            await root_driver.new_tab({"url": root_url})
            root_tools = AsyncBrowserToolset(root_driver, members=["read_diagnostics"], confirm=approve)
            root_report = await execute(
                root_tools, "read_diagnostics", {"tab_id": None, "source": "network", "limit": 100}
            )
            assert root_report["ok"] is True
            await root_driver.navigate({"tab_id": None, "url": root_url})
            assert root_context.pages[0].url == root_url + "/"
            try:
                await root_driver.navigate({"tab_id": None, "url": root_url + "/other"})
            except BrowserError:
                pass
            else:
                raise AssertionError("Sensitive driver admitted an uninstalled fixture")
            await root_context.close()

            async def check_setup(stage: str, mode: str) -> None:
                held_context = await browser.new_context(service_workers="block")
                held = await create_sensitive_driver(held_context, url, scripts=True)
                await held.new_tab({"url": url})
                _, held_page = held.page(None)
                entered = asyncio.Event()
                release = asyncio.Event()
                stopped = asyncio.Event()
                locate = held_page.locator
                invalidate = held.invalidate_references

                def hold_locator(*args: Any, **kwargs: Any) -> Any:
                    locator = locate(*args, **kwargs)
                    if args[0] == "html":
                        acquire = locator.element_handle

                        async def held_acquire(*args: Any, **kwargs: Any) -> Any:
                            entered.set()
                            await release.wait()
                            return await acquire(*args, **kwargs)

                        locator.element_handle = held_acquire
                    return locator

                async def held_invalidate() -> None:
                    entered.set()
                    await release.wait()
                    await invalidate()

                with (
                    patch.object(held_page, "locator", hold_locator if stage == "root" else locate),
                    patch.object(
                        held, "invalidate_references", held_invalidate if stage == "references" else invalidate
                    ),
                ):
                    pending = asyncio.create_task(
                        held._run_script(
                            {
                                "tab_id": None,
                                "source": 'return "done";',
                                "timeout_ms": 80 if mode == "timeout" else 2000,
                            },
                            cancelled=stopped.is_set,
                        )
                    )
                    try:
                        await asyncio.wait_for(entered.wait(), 2)
                        if mode == "cancel":
                            stopped.set()
                        done, _ = await asyncio.wait({pending}, timeout=0.5)
                        assert pending in done, f"{stage} {mode}: still waiting for setup"
                        assert pending.exception() is not None, f"{stage} {mode}: reported success"
                        await held._join_retirement()
                        assert held_page.is_closed()
                        try:
                            await held.state()
                        except (BrowserError, RuntimeError):
                            pass
                        else:
                            raise AssertionError("Retired driver was reused")
                        try:
                            await held.new_tab({"url": url})
                        except (BrowserError, RuntimeError):
                            pass
                        else:
                            raise AssertionError("Retired driver admitted a new tab")
                    finally:
                        release.set()
                        await asyncio.gather(pending, return_exceptions=True)
                        await held_context.close()

            for stage in ("root", "references"):
                for mode in ("timeout", "cancel"):
                    await check_setup(stage, mode)

            for mode in ("ordinary", "timeout", "cancel"):
                closing_context = await browser.new_context(service_workers="block")
                closing_driver = await create_sensitive_driver(closing_context, url, scripts=True)
                await closing_driver.new_tab({"url": url})
                _, closing_page = closing_driver.page(None)
                entered, release, stopped = asyncio.Event(), asyncio.Event(), asyncio.Event()
                original_close = closing_context.close

                async def held_close(
                    entered_gate: asyncio.Event = entered,
                    release_gate: asyncio.Event = release,
                    close: Callable[[], Awaitable[None]] = original_close,
                ) -> None:
                    entered_gate.set()
                    await release_gate.wait()
                    await close()

                with patch.object(closing_context, "close", held_close):
                    script_action = {
                        "tab_id": None,
                        "source": "return 42;",
                        "timeout_ms": 200 if mode == "timeout" else 3000,
                    }
                    operation = closing_driver.run_script
                    assert operation is not None
                    pending = asyncio.ensure_future(operation(script_action, cancelled=stopped.is_set))
                    try:
                        await asyncio.wait_for(entered.wait(), 2)
                        try:
                            await closing_driver.state()
                        except RuntimeError:
                            pass
                        else:
                            raise AssertionError("Closing script driver was reusable")
                        assert not closing_page.is_closed()
                        if mode == "ordinary":
                            done, _ = await asyncio.wait({pending}, timeout=0.075)
                            assert not done, "Ordinary failure did not join cleanup"
                            release.set()
                        elif mode == "cancel":
                            stopped.set()
                        done, _ = await asyncio.wait({pending}, timeout=0.75)
                        assert pending in done, f"Script retirement blocked after {mode}"
                        assert pending.exception() is not None
                        release.set()
                        await closing_driver._join_retirement()
                        assert closing_page.is_closed()
                    finally:
                        release.set()
                        await asyncio.gather(pending, return_exceptions=True)
                        await original_close()

            cancelled_context = await browser.new_context(service_workers="block")
            cancelled_driver = await create_sensitive_driver(cancelled_context, url, scripts=True)
            await cancelled_driver.new_tab({"url": url})
            _, cancelled_page = cancelled_driver.page(None)
            setup_entered, setup_release = asyncio.Event(), asyncio.Event()
            close_entered, close_release = asyncio.Event(), asyncio.Event()
            native_close = cancelled_context.close
            native_invalidate = cancelled_driver.invalidate_references

            async def held_invalidate() -> None:
                setup_entered.set()
                await setup_release.wait()
                await native_invalidate()

            async def cancelled_close() -> None:
                close_entered.set()
                await close_release.wait()
                await native_close()

            with (
                patch.object(cancelled_driver, "invalidate_references", held_invalidate),
                patch.object(cancelled_context, "close", cancelled_close),
            ):
                run = cancelled_driver.run_script
                assert run is not None
                task = asyncio.ensure_future(
                    run(
                        {
                            "tab_id": None,
                            "source": "document.querySelector('#box').setAttribute('x', '71'); return 'ok';",
                            "timeout_ms": 3000,
                        },
                        cancelled=None,
                    )
                )
                try:
                    await asyncio.wait_for(setup_entered.wait(), 2)
                    task.cancel()
                    await asyncio.wait_for(close_entered.wait(), 2)
                    done, _ = await asyncio.wait({task}, timeout=0.5)
                    assert task in done and task.cancelled(), "Task cancellation waited for held context close"
                    try:
                        await cancelled_driver.state()
                    except RuntimeError:
                        pass
                    else:
                        raise AssertionError("Task cancellation revived the driver")
                    try:
                        await cancelled_driver.new_tab({"url": url})
                    except RuntimeError:
                        pass
                    else:
                        raise AssertionError("Cancelled driver admitted a new tab")
                    assert not cancelled_page.is_closed()
                    setup_release.set()
                    assert await cancelled_page.locator("#box").get_attribute("x") == "0"
                    close_release.set()
                    await cancelled_driver._join_retirement()
                    assert cancelled_page.is_closed()
                finally:
                    setup_release.set()
                    close_release.set()
                    await asyncio.gather(task, return_exceptions=True)
                    await native_close()

            if "--bounded" in sys.argv:
                print("PASS bounded sensitive origin, navigation, root/reference setup cancellation and timeout")
                return

            for value in ("42", "({a: 1})", "'é'.repeat(8193)"):
                invalid_context = await browser.new_context(service_workers="block")
                invalid_driver = await create_sensitive_driver(invalid_context, url, scripts=True)
                await invalid_driver.new_tab({"url": url})
                invalid_page = invalid_context.pages[0]
                invalid_tools = AsyncBrowserToolset(invalid_driver, members=["run_script"], confirm=approve)
                try:
                    invalid = await execute(
                        invalid_tools,
                        "run_script",
                        {
                            "tab_id": None,
                            "timeout_ms": 2000,
                            "source": f"document.querySelector('#box').setAttribute('x','71'); return {value};",
                        },
                    )
                except RuntimeError:
                    pass
                else:
                    assert invalid["ok"] is False, invalid
                assert invalid_page.is_closed()
                try:
                    await invalid_driver.state()
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("Retired script driver reused")

            print(
                json.dumps(
                    {
                        "success": True,
                        "console": "warning",
                        "network": "failed",
                        "sentinels": 0,
                        "script": "synthetic-42",
                        "svg": "70",
                        "escaped": Blocked.escaped,
                        "stale": True,
                        "retired": ["timeout", "cancel"],
                    }
                )
            )
        finally:
            await browser.close()


if __name__ == "__main__":
    fixture = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    other = ThreadingHTTPServer(("127.0.0.1", 0), Blocked)
    threads = [Thread(target=server.serve_forever, daemon=True) for server in (fixture, other)]
    for thread in threads:
        thread.start()
    try:
        asyncio.run(
            main(
                f"http://127.0.0.1:{fixture.server_port}/fixture",
                f"http://127.0.0.1:{other.server_port}/SENTINEL_NETWORK",
            )
        )
    finally:
        for server in (fixture, other):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join()
