"""Inspect schemas or invoke SDK-validated calls on an owned local fixture."""

from __future__ import annotations

import json
import asyncio
import argparse
from typing import TYPE_CHECKING, Any, cast
from pathlib import Path
from itertools import count
from threading import Thread
from contextlib import asynccontextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from collections.abc import Callable, AsyncGenerator
from typing_extensions import override

if TYPE_CHECKING:
    from browser_driver import PlaywrightBrowser
    from playwright.async_api import Page

from openai.lib.browser import BrowserError, AsyncBrowserToolset
from openai.types.responses import ResponseFunctionToolCall

_CALL_IDS = count(1)


async def inspect_call(
    helper: AsyncBrowserToolset, member: str, args: dict[str, object], *, cancelled: Callable[[], bool] | None = None
) -> dict[str, Any]:
    number = next(_CALL_IDS)
    call = ResponseFunctionToolCall(
        id=f"inspector-{number}",
        call_id=f"local-{number}",
        status="completed",
        type="function_call",
        name="browser_" + member,
        arguments=json.dumps(args),
    )
    result = await helper.execute(call, cancelled=cancelled)
    output = result["output"]
    assert not isinstance(output, str)
    text = next(part["text"] for part in output if part["type"] == "input_text")
    return cast(dict[str, Any], json.loads(text))


async def check_partial_driver(driver: Any) -> dict[str, bool]:
    """Run common read-only boundary checks on a custom state/read_page driver."""
    approved = False

    async def confirm(_context: Any) -> bool:
        return approved

    helper = AsyncBrowserToolset(
        driver, members=["list_tabs", "read_page"], confirm_reads=["read_page"], confirm=confirm
    )
    state = await inspect_call(helper, "list_tabs", {})
    assert state["ok"], "state must pass SDK validation"
    denied = await inspect_call(helper, "read_page", {"tab_id": None, "filter": "all"})
    assert not denied["ok"], "private read needs consent"
    assert "PRIVATE_INSPECTOR_SENTINEL" not in json.dumps(denied)
    approved = True
    read = await inspect_call(helper, "read_page", {"tab_id": None, "filter": "all"})
    assert read["ok"], "approved read must return a supported result"
    try:
        await inspect_call(helper, "click", {"tab_id": None, "target": "never-advertised"})
    except BrowserError:
        pass
    else:
        raise AssertionError("excluded methods cannot dispatch")
    try:
        await inspect_call(helper, "read_page", {"tab_id": None, "filter": "all"}, cancelled=lambda: True)
    except Exception:
        pass
    else:
        raise AssertionError("Stop must refuse dispatch")
    helper.close()
    try:
        await inspect_call(helper, "list_tabs", {})
    except Exception:
        pass
    else:
        raise AssertionError("A closed helper must refuse new work")
    return {"state": True, "privateRead": True, "approvedRead": True, "disabled": True, "stop": True, "close": True}


class MemoryDriver:
    async def state(self) -> Any:
        return {"tabs": [{"id": "local", "title": "Read only list", "url": "about:blank", "active": True}]}

    async def read_page(self, _args: Any) -> Any:
        return {"version": 1, "text": "Locally supplied rows: Amber, Birch.", "elements": [], "omitted": []}


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_GET(self) -> None:
        files = {"/form": "inspector-form.html", "/canvas": "inspector-canvas.html"}
        file = files.get(self.path)
        if file is None:
            self.send_error(404)
            return
        body = Path(__file__).with_name(file).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@asynccontextmanager
async def open_inspector() -> AsyncGenerator[tuple[PlaywrightBrowser, Page, str], None]:
    from browser_driver import open_browser

    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=server.serve_forever)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        async with open_browser(
            origin + "/form",
            owned_fixture_urls=frozenset((origin + "/form", origin + "/canvas")),
            public_values=frozenset(((origin + "/form", "fixture", "ready"),)),
            public_viewports=frozenset((origin + "/canvas",)),
        ) as base:
            yield base, base.context.pages[0], origin
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


async def exercise(base: Any, page: Any) -> dict[str, object]:
    checks: dict[str, object] = {
        "memory": await check_partial_driver(MemoryDriver()),
        "playwright": await check_partial_driver(base),
    }

    class Broken(MemoryDriver):
        @override
        async def state(self) -> Any:
            return {"tabs": [{"id": "broken", "active": True}]}

    try:
        await check_partial_driver(Broken())
    except Exception:
        checks["invalidState"] = True
    else:
        raise AssertionError("A malformed driver state must fail")
    decision = True

    async def confirm(_context: Any) -> bool:
        return decision

    helper = AsyncBrowserToolset(base, members=["read_page", "set_checked"], confirm=confirm)

    async def find() -> str:
        read = await inspect_call(helper, "read_page", {"tab_id": None, "filter": "interactive"})
        assert read["ok"]
        elements = read["result"]["elements"]
        assert "PRIVATE_INSPECTOR_SENTINEL" not in json.dumps(read)
        assert not any(item["label"] in ("Unavailable", "Private") for item in elements)
        return next(item["ref"] for item in elements if item["label"] == "Ready")

    ref = await find()
    for checked in (True, True, False, False):
        result = await inspect_call(helper, "set_checked", {"tab_id": None, "target": ref, "checked": checked})
        assert result["ok"]
        assert await page.locator("input[type=checkbox]").is_checked() == checked
        ref = await find()
    assert await page.evaluate("() => window.effectCount") == 2
    decision = False
    refused = await inspect_call(helper, "set_checked", {"tab_id": None, "target": ref, "checked": True})
    assert not refused["ok"]
    assert await page.evaluate("() => window.effectCount") == 2
    decision = True
    await page.locator("input[type=checkbox]").evaluate("(node) => node.replaceWith(node.cloneNode(true))")
    replaced = await inspect_call(helper, "set_checked", {"tab_id": None, "target": ref, "checked": True})
    assert not replaced["ok"]
    assert await page.evaluate("() => window.effectCount") == 2
    checks["form"] = {"idempotent": True, "refusals": True, "originalReference": True, "changes": 2}
    ref = await find()
    await page.locator("input[type=checkbox]").evaluate(
        "(node) => node.addEventListener('click', event => event.preventDefault(), {once:true})"
    )
    try:
        await inspect_call(helper, "set_checked", {"tab_id": None, "target": ref, "checked": True})
    except RuntimeError as error:
        assert "state report failed" in str(error)
    else:
        raise AssertionError("Checkbox cancellation was reported as a completed action")
    try:
        await base.read_page({"tab_id": None, "filter": "interactive"})
    except RuntimeError as error:
        assert "retired" in str(error)
    else:
        raise AssertionError("Checkbox cancellation left the owned context reusable")
    checks["cancelledClickRetires"] = True
    return checks


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", choices=("playwright", "memory"), default="playwright")
    parser.add_argument("--exercise", action="store_true")
    parser.add_argument("--member")
    parser.add_argument("--args", default="{}")
    parser.add_argument("--ref-label")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--stop", action="store_true")
    args = parser.parse_args()

    async def inspect(driver: Any, memory: bool) -> None:
        async def confirm(_context: Any) -> bool:
            return args.approve is True

        helper = AsyncBrowserToolset(
            driver,
            members=["list_tabs", "read_page"] if memory else ["list_tabs", "read_page", "set_checked"],
            confirm_reads=["read_page"],
            confirm=confirm,
        )
        if not args.member:
            print(json.dumps(helper.tools, indent=2))
            return
        action = json.loads(args.args)
        if args.ref_label:
            read = await inspect_call(
                helper, "read_page", {"tab_id": None, "filter": "interactive"}, cancelled=lambda: args.stop
            )
            if not read["ok"]:
                print(json.dumps(read, indent=2))
                return
            matching = [item for item in read["result"]["elements"] if item["label"] == args.ref_label]
            if len(matching) != 1:
                raise ValueError("Choose exactly one label from an approved interactive read.")
            action["target"] = matching[0]["ref"]
        print(json.dumps(await inspect_call(helper, args.member, action, cancelled=lambda: args.stop), indent=2))

    if args.driver == "memory" and not args.exercise:
        await inspect(MemoryDriver(), True)
        return
    async with open_inspector() as (base, page, _origin):
        if args.exercise:
            print(json.dumps(await exercise(base, page), indent=2))
            return
        await inspect(base, False)


if __name__ == "__main__":
    asyncio.run(main())
