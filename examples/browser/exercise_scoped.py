"""Scoped reads in a real local browser, with no model or vendor calls."""

from __future__ import annotations

import json
import asyncio
from typing import Any
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

from browser_driver import open_browser

from openai.lib.browser import AsyncBrowserToolset, BrowserConfirmContext
from openai.types.responses import ResponseFunctionToolCall


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        html = Path(__file__).with_name("scoped-fixture.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


async def approve(_ctx: BrowserConfirmContext) -> bool:
    return True


async def main(url: str) -> None:
    async with open_browser(url, owned_fixture_urls=frozenset({url})) as driver:
        selected, page = driver.page(None)
        tools = AsyncBrowserToolset(driver, members=["read_page", "read_page_scoped", "click"], confirm=approve)
        sequence = 0

        async def execute(member: str, args: dict[str, object]) -> dict[str, Any]:
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
                )
            )
            blocks = result["output"]
            assert isinstance(blocks, list) and blocks[0]["type"] == "input_text"
            return json.loads(blocks[0]["text"])

        async def discover() -> dict[str, Any]:
            result = await execute("read_page_scoped", {"tab_id": None, "root": None, "depth": 32, "filter": "all"})
            assert result["ok"] is True
            assert [scope["label"] for scope in result["result"]["scopes"]] == ["Order North", "Order South"]
            assert "Secret" not in result["result"]["text"]
            return result["result"]

        first = await discover()
        north, south = first["scopes"][0]["ref"], first["scopes"][1]["ref"]
        not_an_action = await execute("click", {"tab_id": None, "target": south})
        assert not_an_action["ok"] is False
        assert await page.locator("#picked").text_content() == "none"
        scoped = await execute("read_page_scoped", {"tab_id": None, "root": south, "depth": 32, "filter": "all"})
        assert scoped["ok"] is True
        assert "Public South" in scoped["result"]["text"] and "Deep South" in scoped["result"]["text"]
        assert "North" not in scoped["result"]["text"] and "Secret" not in scoped["result"]["text"]
        assert [element["label"] for element in scoped["result"]["elements"]] == ["Open"]
        assert (await execute("click", {"tab_id": None, "target": scoped["result"]["elements"][0]["ref"]}))[
            "ok"
        ] is True
        assert await page.locator("#picked").text_content() == "south"
        assert (await execute("read_page_scoped", {"tab_id": None, "root": north, "depth": 32, "filter": "all"}))[
            "ok"
        ] is False
        second = await discover()
        shallow = await execute(
            "read_page_scoped",
            {"tab_id": None, "root": second["scopes"][1]["ref"], "depth": 1, "filter": "all"},
        )
        assert (
            shallow["ok"] is True
            and "Deep" not in shallow["result"]["text"]
            and "Public" not in shallow["result"]["text"]
        )

        for mutation in ("hidden", "replace", "rename", "tab"):
            await driver.navigate({"tab_id": selected, "url": url})
            observed = await discover()
            old = observed["scopes"][1]["ref"]
            if mutation == "hidden":
                await page.locator("section").nth(1).evaluate("node => { node.hidden = true; }")
            elif mutation == "replace":
                await page.locator("section").nth(1).evaluate("node => { node.replaceWith(node.cloneNode(true)); }")
            elif mutation == "rename":
                await (
                    page.locator("section")
                    .nth(1)
                    .evaluate("node => { node.setAttribute('aria-label', 'Other order'); }")
                )
            else:
                await driver.new_tab({"url": url})
                await driver.switch_tab({"tab_id": selected})
            stale = await execute("read_page_scoped", {"tab_id": None, "root": old, "depth": 32, "filter": "all"})
            assert stale["ok"] is False, mutation

        await driver.navigate({"tab_id": selected, "url": url})
        legacy = await execute("read_page", {"tab_id": None, "filter": "all"})
        assert legacy["ok"] is True and "scopes" not in legacy["result"]
        assert [element["label"] for element in legacy["result"]["elements"]] == ["Open", "Open"]
        print(
            json.dumps(
                {
                    "success": True,
                    "picked": "south",
                    "depth": "bounded",
                    "privacy": True,
                    "stale": ["read", "hidden", "replace", "rename", "tab"],
                    "legacy": True,
                }
            )
        )


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        asyncio.run(main(f"http://127.0.0.1:{server.server_port}/scoped"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
