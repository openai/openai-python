"""Real Chromium exercise of owned fixture refs and retirement. No API calls."""

from __future__ import annotations

import json
import asyncio
from typing import Any, Callable, Awaitable, cast
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import patch
from typing_extensions import override

import httpx2
from browser_driver import PlaywrightBrowser, open_browser
from playwright.async_api import ElementHandle

from openai import AsyncOpenAI
from openai.lib.browser import BrowserError, BrowserReadV1, AsyncBrowserToolset, BrowserCancelledError
from openai.types.responses import ResponseFunctionToolCall
from openai.lib.responses_tool_runner import AsyncRegisteredFunction, AsyncResponsesToolRunner

HERE = Path(__file__).resolve().parent
EFFECTS: list[dict[str, Any]] = []
CHECKS: list[str] = []
REQUESTS: list[str] = []


class Fixture(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        REQUESTS.append(self.path)
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/SYNTHETIC_PRIVATE_denied")
            self.end_headers()
            return
        if self.path == "/download":
            body = b"SYNTHETIC_PRIVATE file contents"
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", 'attachment; filename="SYNTHETIC_PRIVATE.txt"')
            self.send_header("X-Fixture-Private", "SYNTHETIC_PRIVATE header")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/failed":
            self.send_response(503)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path not in ("/fixture", "/again", "/rich-child"):
            self.send_error(404)
            return
        body = (HERE / ("rich-child.html" if self.path == "/rich-child" else "owned-fixture.html")).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/effect":
            self.send_error(404)
            return
        count = int(self.headers["Content-Length"])
        EFFECTS.append(json.loads(self.rfile.read(count)))
        self.send_response(204)
        self.end_headers()


def function(member: str, arguments: dict[str, object]) -> ResponseFunctionToolCall:
    return ResponseFunctionToolCall(
        id="fc_fixture",
        type="function_call",
        status="completed",
        call_id="fixture",
        name="browser_" + member,
        arguments=json.dumps(arguments),
    )


async def selected(driver: PlaywrightBrowser) -> dict[str, str]:
    page = await driver.read_page({"tab_id": None, "filter": "interactive"})
    assert isinstance(page, dict)
    return {element["label"]: element["ref"] for element in page["elements"]}


async def no_effect(operation: Callable[[], Awaitable[object]]) -> None:
    before = list(EFFECTS)
    try:
        await operation()
    except BrowserError:
        pass
    else:
        raise AssertionError("Expected explicit pre-action refusal")
    assert EFFECTS == before


async def wait_effects(count: int) -> None:
    async def wait() -> None:
        while len(EFFECTS) < count:
            await asyncio.sleep(0.01)

    await asyncio.wait_for(wait(), 3)
    assert len(EFFECTS) == count


async def approve(_context: Any) -> bool:
    return True


async def allow(_context: Any, _url: str) -> bool:
    return True


async def exercise(url: str, urls: frozenset[str]) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)
        assert not {"browser_hover", "browser_key", "browser_scroll"} & {tool["name"] for tool in browser.tools}
        observed = await driver.read_page({"tab_id": None, "filter": "interactive"})
        assert isinstance(observed, dict)
        assert "private" in observed["omitted"] and "SYNTHETIC_PRIVATE" not in json.dumps(observed)
        assert not {"Private", "File"} & {element["label"] for element in observed["elements"]}
        state = await driver.state()
        assert state == await driver.state() and "SYNTHETIC_PRIVATE" not in json.dumps(state)
        assert state["tabs"][0]["title"] == "Owned fixture"
        CHECKS.append("owned-omissions-and-private-title")

        refs = await selected(driver)
        record_node = await page.query_selector("#row")

        # Inherited native disabled state is not reflected by input.disabled.
        # A held ref and a new read must both respect the effective state.
        before = len(EFFECTS)
        field = page.locator("#name")
        previous = await field.input_value()
        actual = await field.evaluate("""e => {
            const group=document.createElement('fieldset');
            e.before(group);group.append(e);group.disabled=true;
            return {property:e.disabled,effective:e.matches(':disabled')};
        }""")
        assert actual == {"property": False, "effective": True}
        await no_effect(lambda: driver.type({"tab_id": None, "target": refs["Name"], "text": "blocked"}))
        assert await field.input_value() == previous
        disabled_read = await selected(driver)
        assert "Name" not in disabled_read and len(EFFECTS) == before
        await field.evaluate("e => e.closest('fieldset').disabled=false")
        enabled = await selected(driver)
        await driver.type({"tab_id": None, "target": enabled["Name"], "text": "fixture input"})
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "case_a", "operation": "input", "value": "fixture input"}
        CHECKS.append("fieldset-effective-disabled-old-and-fresh-ref-revealed-input-one-effect")
        refs = await selected(driver)

        async def rebind(_context: Any) -> bool:
            await page.evaluate("window.installRecord('case_b')")
            return True

        browser.confirm = rebind
        before = len(EFFECTS)
        result = await browser.execute(function("click", {"tab_id": None, "target": refs["Confirm"]}))
        content = result["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        assert json.loads(content[0]["text"])["ok"] is False and len(EFFECTS) == before
        assert record_node is not None and await record_node.evaluate(
            "e => e === document.querySelector('#row') && e.isConnected"
        )
        browser.confirm = approve
        refs = await selected(driver)
        result = await browser.execute(function("click", {"tab_id": None, "target": refs["Confirm"]}))
        content = result["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        assert json.loads(content[0]["text"])["ok"] is True
        await wait_effects(before + 1)
        assert EFFECTS[-1]["id"] == "case_b"
        CHECKS.append("connected-reuse-after-consent-fails-fresh-approval-works")

        await page.evaluate("window.installRecord('case_a')")
        refs = await selected(driver)
        await page.locator("#confirm").evaluate("e => e.disabled = true")
        before = len(EFFECTS)
        await no_effect(lambda: driver.click({"tab_id": None, "target": refs["Confirm"]}))
        # Real Playwright waits after the precheck and later acts on case_b.
        auto_wait = asyncio.create_task(page.locator("#confirm").click())
        await asyncio.sleep(0.12)
        assert not auto_wait.done() and len(EFFECTS) == before
        await page.evaluate("window.installRecord('case_b'); document.querySelector('#confirm').disabled = false")
        await auto_wait
        await wait_effects(before + 1)
        assert EFFECTS[-1]["id"] == "case_b"
        CHECKS.append("disabled-guard-vs-real-playwright-auto-wait")

        await page.evaluate("window.installRecord('case_a'); window.armPreliminary()")
        refs = await selected(driver)
        before = len(EFFECTS)
        await driver.type({"tab_id": None, "target": refs["Name"], "text": "synthetic"})
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "case_a", "operation": "input", "value": "synthetic"}
        await driver.click({"tab_id": None, "target": refs["Confirm"]})
        await wait_effects(before + 2)
        assert EFFECTS[-1]["id"] == "case_a" and await page.evaluate("window.preliminary") == 0
        await page.locator("#name").focus()
        assert await page.evaluate("window.preliminary") == 1
        CHECKS.append("dom-actions-no-focus-pointer-preliminary-events")

        await page.reload()
        await page.evaluate("""() => {
            window.armPreliminary();
            const field = document.querySelector('#name');
            field.required = true; field.value = '';
        }""")
        refs = await selected(driver)
        await no_effect(lambda: driver.click({"tab_id": None, "target": refs["Confirm"]}))
        assert await page.evaluate("window.preliminary") == 0
        await page.evaluate("document.querySelector('#row').checkValidity()")
        assert await page.evaluate("window.preliminary") == 1
        CHECKS.append("invalid-required-form-does-not-dispatch-invalid-before-refusal")

        await page.reload()
        for setup in (
            "document.querySelector('#cover').style.display='block'",
            "document.querySelector('#confirm').className='offscreen'",
            "document.querySelector('#confirm').hidden=true",
            "document.querySelector('#confirm').setAttribute('aria-label', 'Changed')",
            "document.querySelector('#confirm').setAttribute('role', 'link')",
        ):
            refs = await selected(driver)
            await page.evaluate(setup)
            await no_effect(lambda ref=refs["Confirm"]: driver.click({"tab_id": None, "target": ref}))
            await page.reload()
        refs = await selected(driver)
        await page.locator("#name").evaluate("e => e.readOnly = true")
        await no_effect(lambda: driver.type({"tab_id": None, "target": refs["Name"], "text": "blocked"}))
        await page.reload()
        refs = await selected(driver)
        await no_effect(
            lambda: driver.select_option({"tab_id": None, "target": refs["Category"], "values": ["missing"]})
        )
        before = len(EFFECTS)
        await driver.select_option({"tab_id": None, "target": refs["Category"], "values": ["urgent"]})
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "case_a", "operation": "select", "value": "urgent"}
        CHECKS.append("viewport-label-role-writable-and-option-guards")

        refs = await selected(driver)
        ref = refs["Confirm"]
        await no_effect(lambda: driver.click({"tab_id": None, "target": "forged:" + ref}))
        refs = await selected(driver)
        await no_effect(lambda: driver.click({"tab_id": None, "target": ref}))
        await driver.invalidate_references()
        await no_effect(lambda: driver.click({"tab_id": None, "target": refs["Confirm"]}))
        await no_effect(lambda: driver.type({"tab_id": None, "target": None, "text": "blocked"}))
        CHECKS.append("forged-repeated-read-handoff-null-target")

        refs = await selected(driver)
        ref = refs["Confirm"]
        first = driver.active
        await driver.new_tab({"url": url})
        second = driver.active
        await driver.switch_tab({"tab_id": first})
        await no_effect(lambda: driver.click({"tab_id": first, "target": ref}))
        await driver.close_tab({"tab_id": second})
        _, page = driver.page(first)
        refs = await selected(driver)
        await driver.navigate({"tab_id": first, "url": url.replace("/fixture", "/again")})
        await no_effect(lambda: driver.click({"tab_id": first, "target": refs["Confirm"]}))
        refs = await selected(driver)
        await page.go_back()
        await no_effect(lambda: driver.click({"tab_id": first, "target": refs["Confirm"]}))
        refs = await selected(driver)
        await page.evaluate("""() => new Promise(resolve => {
            const f=document.createElement('iframe'); f.src='/again';
            f.onload=resolve; document.body.append(f);
        })""")
        await no_effect(lambda: driver.click({"tab_id": first, "target": refs["Confirm"]}))
        frame = page.frames[-1]
        await frame.evaluate("""() => {
            document.querySelector('#secondary').innerHTML =
              'Visible child<span style="display:none">SYNTHETIC_PRIVATE</span>';
        }""")
        await page.locator("iframe").evaluate("""f => {
            Object.assign(f.style, {position:'fixed', left:'500px', top:'16px',
                                    width:'470px', height:'730px', zIndex:'10'});
        }""")
        observed = await driver.read_page({"tab_id": None, "filter": "interactive"})
        assert "SYNTHETIC_PRIVATE" not in json.dumps(observed) and '"label": "Visible child"' in json.dumps(observed)
        refs = await selected(driver)
        before = len(EFFECTS)
        await driver.click({"tab_id": first, "target": refs["Visible child"]})
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "case_a", "operation": "click", "value": ""}
        refs = await selected(driver)
        # The child's own hit-test still succeeds under this top-level cover.
        await page.locator("#cover").evaluate("e => e.style.display='block'")
        assert await frame.locator("#secondary").evaluate("""e => {
            const r=e.getBoundingClientRect();
            return e.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2));
        }""")
        await no_effect(lambda: driver.click({"tab_id": first, "target": refs["Visible child"]}))
        assert "Visible child" not in json.dumps(await driver.read_page({"tab_id": None, "filter": "interactive"}))
        await page.locator("#cover").evaluate("e => e.style.display='none'")
        await page.locator("iframe").evaluate("f => f.style.transform='scale(.99)'")
        assert "Visible child" not in json.dumps(await driver.read_page({"tab_id": None, "filter": "interactive"}))
        await page.locator("iframe").evaluate("f => f.style.transform='none'")
        CHECKS.append("hidden-label-safe-visible-owned-child-parent-overlay-and-transform-guards")
        refs = await selected(driver)
        await page.locator("iframe").evaluate("f => f.remove()")
        await no_effect(lambda: driver.click({"tab_id": first, "target": refs["Confirm"]}))
        CHECKS.append("tabs-navigation-history-frame-navigate-detach")

        refs = await selected(driver)
        async with open_browser(url, owned_fixture_urls=urls) as other:
            await no_effect(lambda: other.click({"tab_id": None, "target": refs["Confirm"]}))
            fresh = await selected(other)
            await no_effect(lambda: driver.click({"tab_id": first, "target": fresh["Confirm"]}))
        for _ in range(19):
            await driver.new_tab({"url": url})
            await driver.close_tab({"tab_id": driver.active})
            await driver.switch_tab({"tab_id": first})
        state = await driver.state()
        assert state == await driver.state()
        assert "observation" in state
        observation = state["observation"]
        assert len(observation["changes"]) == 32 and observation["dropped_changes"] > 0
        assert [notice["sequence"] for notice in observation["changes"]] == list(
            range(observation["dropped_changes"] + 1, observation["sequence"] + 1)
        )
        observation["changes"][0]["tab_id"] = "external-mutation"
        after = await driver.state()
        assert "observation" in after and after["observation"]["changes"][0]["tab_id"] != "external-mutation"
        CHECKS.append("two-context-forgery-and-bounded-non-consuming-ring")

        await page.evaluate("alert('SYNTHETIC_PRIVATE dialog')")
        async with page.expect_download() as downloaded:
            await page.evaluate("""() => {
                const a=document.createElement('a');
                a.href='/download'; a.textContent='Synthetic';
                document.body.append(a); a.click(); a.remove();
            }""")

        async def download_noticed() -> None:
            while True:
                current = await driver.state()
                if "observation" in current and any(c["type"] == "download" for c in current["observation"]["changes"]):
                    return
                await asyncio.sleep(0.01)

        await asyncio.wait_for(download_noticed(), 3)
        before_redirect = await driver.state()
        assert "observation" in before_redirect
        # A blocked redirect in an owned iframe must leave no URL text in
        # events. It need not replace the inspected main document.
        await page.evaluate("""() => new Promise(resolve => {
            const f=document.createElement('iframe'); f.src='/redirect';
            f.onload=resolve; document.body.append(f);
        })""")
        current = await driver.state()
        assert "observation" in current
        changes = current["observation"]["changes"]
        assert not any(
            c["type"] == "navigation_refused" and c["sequence"] > before_redirect["observation"]["sequence"]
            for c in changes
        )
        assert any(c["type"] == "dialog_dismissed" and c["kind"] == "alert" for c in changes)
        assert any(c["type"] == "download" and c["status"] == "blocked" for c in changes)
        download = await downloaded.value
        assert await download.failure(), "Disabled downloads must fail; do not open a path or export"
        assert "/redirect" in REQUESTS and "/download" in REQUESTS
        assert not any("SYNTHETIC_PRIVATE" in path for path in REQUESTS)
        assert "SYNTHETIC_PRIVATE" not in json.dumps(current)
        assert current == await driver.state()
        CHECKS.append("real-dialog-redirect-download-private-omission-ring")

        async def deny(_context: Any) -> bool:
            return False

        browser.confirm = deny
        refs = await selected(driver)
        current = await driver.state()
        result = await browser.execute(function("click", {"tab_id": first, "target": refs["Confirm"]}))
        content = result["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        assert json.loads(content[0]["text"])["ok"] is False
        assert current == await driver.state()
        original_state = driver.state

        async def read_then_fail() -> Any:
            await original_state()
            raise RuntimeError("Synthetic failed state report")

        driver.state = read_then_fail  # type: ignore[method-assign]
        try:
            await browser.execute(function("list_tabs", {}))
        except RuntimeError as exc:
            assert str(exc) == "Browser state report failed."
        else:
            raise AssertionError("Failed state returned as successful")
        driver.state = original_state  # type: ignore[method-assign]
        assert current == await driver.state()
        CHECKS.append("overflow-ring-survives-refusal-and-failed-state-read")
        browser.confirm = approve
        fresh = await selected(driver)
        before_recovery = len(EFFECTS)
        recovered = await browser.execute(function("click", {"tab_id": first, "target": fresh["Confirm"]}))
        content = recovered["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        assert json.loads(content[0]["text"])["ok"] is True
        await wait_effects(before_recovery + 1)
        CHECKS.append("fresh-browser-action-recovers-after-failed-ring-read")


async def uncertain(url: str, urls: frozenset[str], *, close_fails: bool) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        refs = await selected(driver)
        # Both refs come from the same current observation so a stale-ref
        # refusal cannot disguise a broken unusable latch.
        handle, _, _ = driver._refs[driver.active][refs["Secondary"]]
        evaluate, close = handle.evaluate, driver.context.close
        closing, release = asyncio.Event(), asyncio.Event()

        async def lost_after_dispatch(*args: Any, **kwargs: Any) -> object:
            result = await evaluate(*args, **kwargs)
            assert result is True
            raise RuntimeError("Synthetic lost reply")

        async def held_close(*args: Any, **kwargs: Any) -> None:
            closing.set()
            await release.wait()
            if close_fails:
                raise RuntimeError("Synthetic close failure")
            await close(*args, **kwargs)

        handle.evaluate = lost_after_dispatch  # type: ignore[method-assign]
        driver.context.close = held_close  # type: ignore[method-assign]
        before = len(EFFECTS)
        first = asyncio.create_task(driver.click({"tab_id": None, "target": refs["Secondary"]}))
        await asyncio.wait_for(closing.wait(), 3)
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "case_a", "operation": "click", "value": ""}
        for operation in (
            driver.state,
            lambda: driver.click({"tab_id": None, "target": refs["Confirm"]}),
            lambda: driver.new_tab({"url": url}),
            lambda: driver.get_page_text({"tab_id": None}),
            lambda: driver.type({"tab_id": None, "target": None, "text": "blocked"}),
            driver.invalidate_references,
        ):
            try:
                await operation()
            except RuntimeError as exc:
                assert str(exc) == "Browser driver was retired after an uncertain action."
            else:
                raise AssertionError("Retired driver accepted another operation during held close")
        approvals = 0

        async def approval(_context: Any) -> bool:
            nonlocal approvals
            approvals += 1
            return True

        browser = AsyncBrowserToolset(driver, confirm=approval, url_policy=allow)
        try:
            await browser.execute(function("click", {"tab_id": None, "target": refs["Confirm"]}))
        except RuntimeError as exc:
            assert str(exc) == "Browser state report failed."
        else:
            raise AssertionError("Retired SDK attempted another approved action")
        assert approvals == 0 and len(EFFECTS) == before + 1
        release.set()
        try:
            await first
        except RuntimeError as exc:
            assert str(exc) == ("Synthetic close failure" if close_fails else "Synthetic lost reply")
        else:
            raise AssertionError("Unknown first action was reported successful")
        driver.context.close = close  # type: ignore[method-assign]
        try:
            await driver.state()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Old driver revived after close attempt")
        assert len(EFFECTS) == before + 1
        CHECKS.append("first-effect-lost-reply-latch-close-" + ("failed" if close_fails else "held"))


async def visibility(url: str, urls: frozenset[str], case: str) -> None:
    """Exercise opacity or a covered rotated frame at issuance and dispatch."""
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        if case in ("iframe", "rotate"):
            await page.evaluate("""() => new Promise(resolve => {
                const f=document.createElement('iframe');
                f.id='child'; f.src='/again';
                Object.assign(f.style, {position:'fixed',left:'450px',top:'40px',width:'400px',
                                        height:'400px',border:'0',padding:'0',zIndex:'10'});
                f.onload=resolve; document.body.append(f);
            })""")
            frame = page.frames[-1]
        else:
            frame = page.main_frame
        await frame.locator("#secondary").evaluate("e => e.textContent = 'Visibility check'")
        refs = await selected(driver)
        before = len(EFFECTS)
        await driver.click({"tab_id": None, "target": refs["Visibility check"]})
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "case_a", "operation": "click", "value": ""}
        refs = await selected(driver)
        if case == "button":
            await frame.locator("#secondary").evaluate("e => e.style.opacity = '0'")
        elif case == "row":
            await frame.locator("#row").evaluate("e => e.style.opacity = '0'")
        elif case == "iframe":
            await page.locator("#child").evaluate("e => e.style.opacity = '0'")
        else:
            geometry = await page.evaluate("""() => {
                const f=document.querySelector('#child');
                f.style.rotate='180deg';
                const box=f.getBoundingClientRect();
                const button=f.contentDocument.querySelector('#secondary');
                const target=button.getBoundingClientRect();
                const cx=target.left+target.width/2, cy=target.top+target.height/2;
                const realX=box.right-cx, realY=box.bottom-cy;
                const cover=document.createElement('div');
                cover.id='real-cover';
                Object.assign(cover.style, {position:'fixed', left:(realX-12)+'px',
                    top:(realY-12)+'px',width:'24px',height:'24px',zIndex:'100',background:'black'});
                document.body.append(cover);
                return {transform:getComputedStyle(f).transform, rotate:getComputedStyle(f).rotate,
                    width:box.width,height:box.height,offsetWidth:f.offsetWidth,offsetHeight:f.offsetHeight,
                    uncheckedHit:document.elementFromPoint(box.left+cx,box.top+cy)===f,
                    realHit:document.elementFromPoint(realX,realY)===cover,
                    childHit:button.contains(f.contentDocument.elementFromPoint(cx,cy))};
            }""")
            assert geometry == {
                "transform": "none",
                "rotate": "180deg",
                "width": 400,
                "height": 400,
                "offsetWidth": 400,
                "offsetHeight": 400,
                "uncheckedHit": True,
                "realHit": True,
                "childHit": True,
            }, geometry
        await no_effect(lambda: driver.click({"tab_id": None, "target": refs["Visibility check"]}))
        assert "Visibility check" not in json.dumps(await driver.read_page({"tab_id": None, "filter": "interactive"}))
        await page.reload()
        CHECKS.append("visibility-" + case)


async def refused_navigation(url: str, urls: frozenset[str], member: str) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        approved = 0
        policy_calls = 0
        target = url.replace("/fixture", "/SYNTHETIC_PRIVATE_uninstalled")

        async def confirm(context: Any) -> bool:
            nonlocal approved
            approved += 1
            # Consent is authorized to receive original action arguments.
            assert context["arguments"]["url"] == target
            assert "SYNTHETIC_PRIVATE" not in json.dumps(context["state"])
            return True

        async def policy(context: Any, requested: str) -> bool:
            nonlocal policy_calls
            policy_calls += 1
            assert requested == target
            assert context["arguments"]["url"] == target
            assert "SYNTHETIC_PRIVATE" not in json.dumps(context["state"])
            return True

        browser = AsyncBrowserToolset(driver, confirm=confirm, url_policy=policy)
        args: dict[str, object] = {"url": target}
        if member == "navigate":
            args["tab_id"] = None
        first = await driver.state()
        assert "observation" in first
        before = len(EFFECTS)
        result = await browser.execute(function(member, args))
        content = result["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        reported = json.loads(content[0]["text"])
        assert reported["ok"] is False and "SYNTHETIC_PRIVATE" not in json.dumps(reported)
        assert approved == policy_calls == 1 and len(EFFECTS) == before
        after = await driver.state()
        assert "observation" in after
        assert after["observation"]["sequence"] == first["observation"]["sequence"] + 1
        assert after["observation"]["changes"][-1] == {
            "type": "navigation_refused",
            "sequence": after["observation"]["sequence"],
            "tab_id": driver.active if member == "navigate" else None,
            "reason": "policy",
        }
        assert after["tabs"] == first["tabs"]

        async def deny(_context: Any, requested: str) -> bool:
            assert requested == target
            return False

        browser.url_policy = deny
        result = await browser.execute(function(member, args))
        content = result["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        assert json.loads(content[0]["text"])["ok"] is False
        assert approved == 1 and after == await driver.state() and len(EFFECTS) == before
        assert not any("SYNTHETIC_PRIVATE" in path for path in REQUESTS)
        CHECKS.append("sdk-vs-driver-refused-" + member)


async def event_outputs(url: str, urls: frozenset[str]) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        first, page = driver.page(None)
        callbacks: list[Any] = []

        async def record(context: Any) -> bool:
            callbacks.append(context)
            return True

        browser = AsyncBrowserToolset(driver, confirm=record, url_policy=allow)

        async def output(member: str, arguments: dict[str, object]) -> Any:
            result = await browser.execute(function(member, arguments))
            content = result["output"]
            assert isinstance(content, list) and content[0]["type"] == "input_text"
            return json.loads(content[0]["text"])

        before = await driver.state()
        opened = await output("new_tab", {"url": url.replace("/fixture", "/again")})
        assert opened["ok"]
        second = next(tab["id"] for tab in opened["state"]["tabs"] if tab["id"] != first)
        assert [tab["id"] for tab in opened["state"]["tabs"] if tab["active"]] == [second]
        assert any(
            c["type"] == "tab_opened" and c["tab_id"] == second for c in opened["state"]["observation"]["changes"]
        )
        switched = await output("switch_tab", {"tab_id": first})
        assert switched["ok"]
        assert switched["state"]["observation"]["changes"][-1]["type"] == "tab_switched"
        closed = await output("close_tab", {"tab_id": second})
        assert closed["ok"]
        assert closed["state"]["observation"]["changes"][-1]["tab_id"] == second
        assert closed["state"]["observation"]["changes"][-1]["type"] == "tab_closed"
        assert [tab["id"] for tab in closed["state"]["tabs"] if tab["active"]] == [first]
        listed = await output("list_tabs", {})
        assert listed["state"] == closed["state"] and listed["result"] is None
        assert "observation" in before
        assert before["observation"]["sequence"] < listed["state"]["observation"]["sequence"]
        assert listed["state"] == await driver.state()

        for kind, expected in (("alert", None), ("confirm", False), ("prompt", None)):
            before = await driver.state()
            assert "observation" in before
            after_sequence = before["observation"]["sequence"]
            result = await page.evaluate(
                """kind => {
                    if (kind === 'alert') { window.alert('SYNTHETIC_PRIVATE dialog'); return null; }
                    return window[kind]('SYNTHETIC_PRIVATE dialog');
                }""",
                kind,
            )
            assert result == expected

            async def noticed(after: int = after_sequence) -> Any:
                while True:
                    current = await driver.state()
                    assert "observation" in current
                    for event in current["observation"]["changes"]:
                        if event["type"] == "dialog_dismissed" and event["sequence"] > after:
                            return event
                    await asyncio.sleep(0.01)

            event = await asyncio.wait_for(noticed(), 3)
            assert event == {"type": "dialog_dismissed", "kind": kind, "tab_id": first, "sequence": event["sequence"]}
            state_after_dialog = await output("list_tabs", {})
            assert state_after_dialog["ok"]
            assert "SYNTHETIC_PRIVATE" not in json.dumps(state_after_dialog)

        await page.evaluate("""() => new Promise(resolve => {
            const f=document.createElement('iframe'); f.src='/redirect';
            f.onload=resolve; document.body.append(f);
        })""")
        other_action = await output("switch_tab", {"tab_id": first})
        assert other_action["ok"]
        # This action has no private URL arguments. Its full callback may not inherit redirect data.
        assert "SYNTHETIC_PRIVATE" not in json.dumps({"callback": callbacks[-1], "output": other_action})
        previous = sum(c["type"] == "navigation_refused" for c in other_action["state"]["observation"]["changes"])
        await page.evaluate("""() => new Promise(resolve => {
            const f=document.createElement('iframe'); f.src='/failed';
            f.onload=resolve; document.body.append(f);
        })""")
        failed_http = await output("list_tabs", {})
        assert "/failed" in REQUESTS
        assert failed_http["ok"]
        assert (
            sum(c["type"] == "navigation_refused" for c in failed_http["state"]["observation"]["changes"]) == previous
        )
        assert not any("SYNTHETIC_PRIVATE" in path for path in REQUESTS)
        CHECKS.append("actual-sdk-tab-list-dialog-refusal-notice-and-allowed-http-failure")


async def fresh_click(browser: AsyncBrowserToolset, tab_id: str, target: str, expected: dict[str, str]) -> None:
    before = len(EFFECTS)
    output = await browser.execute(function("click", {"tab_id": tab_id, "target": target}))
    content = output["output"]
    assert isinstance(content, list) and content[0]["type"] == "input_text"
    assert json.loads(content[0]["text"])["ok"] is True
    await wait_effects(before + 1)
    assert EFFECTS[-1] == expected


async def reference_lifecycle(url: str, urls: frozenset[str]) -> None:
    # Install A and B before reading, so a new tab cannot mask missing switch invalidation.
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        first, page = driver.page(None)
        await driver.new_tab({"url": url.replace("/fixture", "/again")})
        second = driver.active
        await driver.switch_tab({"tab_id": first})
        issued = await selected(driver)
        original = await page.query_selector("#confirm")
        assert original is not None
        await driver.switch_tab({"tab_id": second})
        await driver.switch_tab({"tab_id": first})
        assert await original.evaluate("e => e.isConnected && e === document.querySelector('#confirm')")
        await no_effect(lambda: driver.click({"tab_id": first, "target": issued["Confirm"]}))
        fresh = await selected(driver)
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)
        await fresh_click(
            browser, first, fresh["Confirm"], {"id": "case_a", "operation": "submit", "value": "fixture input"}
        )
        CHECKS.append("existing-tabs-A-B-A-explicit-held-ref-zero-fresh-A-one")

    async with open_browser(url, owned_fixture_urls=urls) as driver:
        first, page = driver.page(None)
        issued = await selected(driver)
        original = await page.query_selector("#confirm")
        assert original is not None
        await page.evaluate("window.history.pushState({}, '', '#owned-roundtrip')")
        assert page.url == url + "#owned-roundtrip"
        await page.go_back(wait_until="domcontentloaded")
        assert page.url == url
        assert await original.evaluate("e => e.isConnected && e === document.querySelector('#confirm')")
        await no_effect(lambda: driver.click({"tab_id": first, "target": issued["Confirm"]}))
        fresh = await selected(driver)
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)
        await fresh_click(
            browser, first, fresh["Confirm"], {"id": "case_a", "operation": "submit", "value": "fixture input"}
        )
        CHECKS.append("owned-same-document-roundtrip-same-node-old-zero-fresh-one")

    async with open_browser(url, owned_fixture_urls=urls) as driver:
        first, page = driver.page(None)
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)

        async def attach() -> None:
            await page.evaluate("""() => new Promise(resolve => {
                const f=document.createElement('iframe');
                Object.assign(f.style, {position:'fixed', left:'500px', top:'16px',
                                        width:'470px', height:'730px', zIndex:'10'});
                f.onload=resolve; f.src='/again'; document.body.append(f);
            })""")

        await attach()
        frame = page.frames[-1]
        await frame.locator("#secondary").evaluate("e => e.textContent = 'Visible child'")
        issued = await selected(driver)
        assert "Visible child" in issued
        # Restore the exact child URL and label before trying the held ref.
        await frame.goto(url, wait_until="domcontentloaded")
        await frame.goto(url.replace("/fixture", "/again"), wait_until="domcontentloaded")
        assert frame.url == url.replace("/fixture", "/again")
        await frame.locator("#secondary").evaluate("e => e.textContent = 'Visible child'")
        await no_effect(lambda: driver.click({"tab_id": first, "target": issued["Visible child"]}))
        before_detach = await selected(driver)
        assert "Visible child" in before_detach
        await page.locator("iframe").evaluate("f => f.remove()")
        await no_effect(lambda: driver.click({"tab_id": first, "target": before_detach["Visible child"]}))
        await attach()
        replaced = page.frames[-1]
        await replaced.locator("#secondary").evaluate("e => e.textContent = 'Visible child'")
        fresh = await selected(driver)
        await fresh_click(browser, first, fresh["Visible child"], {"id": "case_a", "operation": "click", "value": ""})
        CHECKS.append("unique-child-navigate-return-old-zero-detach-old-zero-reattach-fresh-one")


async def rich_reads(url: str, urls: frozenset[str], remote: str) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)

        async def report(member: str, args: dict[str, object]) -> BrowserReadV1:
            result = await browser.execute(function(member, args))
            content = result["output"]
            assert isinstance(content, list) and content[0]["type"] == "input_text"
            wire = json.loads(content[0]["text"])
            assert wire["ok"], wire
            observation = wire["result"]
            assert isinstance(observation, dict) and observation["version"] == 1, observation
            assert len(json.dumps(observation, ensure_ascii=False, separators=(",", ":")).encode()) <= 65536
            return cast(BrowserReadV1, observation)

        base = await report("read_page", {"tab_id": None, "filter": "all"})
        encoded = json.dumps(base)
        assert "SYNTHETIC_PRIVATE" not in encoded and "fixture input" not in encoded
        assert "value" in base["omitted"] and "unsupported_root" in base["omitted"]
        held = next(e["ref"] for e in base["elements"] if e["label"] == "Confirm")
        text = await report("get_page_text", {"tab_id": None})
        assert not text["elements"] and "fixture input" not in json.dumps(text)
        before = len(EFFECTS)
        await driver.click({"tab_id": None, "target": held})
        await wait_effects(before + 1)
        CHECKS.append("v1-wire-default-private-values-and-text-read-does-not-revoke")

        # A later mounted match must not disappear behind 100 nonmatches.
        await page.evaluate("""() => {
            for (let i = 0; i < 101; i++) {
              const button = document.createElement('button');
              button.dataset.recordId='case_a';
              button.setAttribute('aria-label', 'Unrelated ' + i); button.type='button';
              Object.assign(button.style, {position:'fixed',left:(i%20*42)+'px',
                  top:(Math.floor(i/20)*30)+'px', width:'40px',height:'28px',padding:'0',margin:'0'});
              document.body.prepend(button);
            }
        }""")
        found = await report("find", {"tab_id": None, "query": "Confirm"})
        assert any(e["label"] == "Confirm" for e in found["elements"]), found
        await page.reload()
        await page.evaluate("""() => {
            const row=document.querySelector('#row');
            const host=document.createElement('section');
            row.prepend(host);
            host.attachShadow({mode:'open'}).innerHTML =
              '<div><span id="shown">Nested BP-1207</span><span hidden id="secret">SYNTHETIC_PRIVATE</span>' +
              '<button aria-labelledby="secret shown">Fallback</button><slot></slot></div>';
            const slot=document.createElement('button'); slot.type='button'; slot.textContent='Slotted';
            host.append(slot);
            const record=Object.freeze({id:'case_a'});
            for (const b of [host.shadowRoot.querySelector('button'),slot])
              b.onclick = () => fetch('/effect', {method:'POST',
                 body:JSON.stringify({id:record.id,operation:'rich',value:''})});
        }""")
        found = await report("find", {"tab_id": None, "query": "nested BP-1207"})
        assert len(found["elements"]) == 1 and found["elements"][0]["label"] == "Nested BP-1207", found
        assert "SYNTHETIC_PRIVATE" not in json.dumps(found)
        held = found["elements"][0]["ref"]
        await page.evaluate("""() => {
          const root=document.querySelector('#row section').shadowRoot;
          root.querySelector('#secret').textContent='CHANGED_PRIVATE';
        }""")
        before = len(EFFECTS)
        await driver.click({"tab_id": None, "target": held})
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "case_a", "operation": "rich", "value": ""}
        slot = await report("find", {"tab_id": None, "query": "Slotted"})
        assert len(slot["elements"]) == 1, slot
        CHECKS.append("query-before-target-cap-shadow-visible-name-slot-hidden-mutation-identity")

        await page.reload()
        await page.evaluate(
            """src => new Promise(resolve => {
            const f=document.createElement('iframe');f.id='rich';
            Object.assign(f.style,{position:'fixed',left:'470px',top:'8px',width:'470px',
                                   height:'450px',border:'0',zIndex:'8'});
            f.onload=resolve;f.src=src;document.body.append(f);
        })""",
            url.replace("/fixture", "/rich-child"),
        )
        child = await report("find", {"tab_id": None, "query": "dispatch bp-1207"})
        assert len(child["elements"]) == 1 and "INTERNAL_ROW_1207" not in json.dumps(child), child
        spaced = await report("find", {"tab_id": None, "query": "  dispatch\n  BP-1207  "})
        assert [element["label"] for element in spaced["elements"]] == ["Dispatch BP-1207"]
        all_visible = await report("read_page", {"tab_id": None, "filter": "all"})
        assert "Dispatch BP-1207" in all_visible["text"]
        await page.locator("#rich").evaluate("e=>e.dataset.browserPrivate=''")
        all_private = await report("read_page", {"tab_id": None, "filter": "all"})
        text_private = await report("get_page_text", {"tab_id": None})
        find_private = await report("find", {"tab_id": None, "query": "Dispatch BP-1207"})
        assert "Dispatch BP-1207" not in json.dumps(all_private), all_private
        assert "Dispatch BP-1207" not in json.dumps(text_private), text_private
        assert not find_private["elements"]
        await page.locator("#rich").evaluate("e=>e.removeAttribute('data-browser-private')")
        revealed_text = await report("get_page_text", {"tab_id": None})
        assert "Dispatch BP-1207" in revealed_text["text"]
        CHECKS.append("same-origin-parent-private-text-and-refs-reveal-normalized-query")
        child = await report("find", {"tab_id": None, "query": "dispatch bp-1207"})
        held = child["elements"][0]["ref"]
        await page.frames[-1].evaluate("window.recycleRich()")
        await no_effect(lambda: driver.click({"tab_id": None, "target": held}))
        child = await report("find", {"tab_id": None, "query": "BP-1207"})
        before = len(EFFECTS)
        await driver.click({"tab_id": None, "target": child["elements"][0]["ref"]})
        await wait_effects(before + 1)
        assert EFFECTS[-1] == {"id": "INTERNAL_ROW_1208", "action": "dispatch"}
        await page.locator("#rich").evaluate("(f,url)=>f.src=url", remote + "/rich-child")
        await page.frames[-1].wait_for_url(remote + "/rich-child")
        remote_read = await report("find", {"tab_id": None, "query": "Dispatch BP-1207"})
        assert not remote_read["elements"] and "Read only: remote frame" in remote_read["text"], remote_read
        assert "Dispatch BP-1207" in remote_read["text"] and "remote_action" in remote_read["omitted"]
        assert "INTERNAL_ROW" not in json.dumps(remote_read) and "PRIVATE_CHILD" not in json.dumps(remote_read)
        missing = await report("find", {"tab_id": None, "query": "No such dispatch"})
        assert "Dispatch BP-1207" not in missing["text"]
        await page.locator("#cover").evaluate("e=>e.style.display='block'")
        covered = await report("find", {"tab_id": None, "query": "Dispatch BP-1207"})
        assert "Dispatch BP-1207" not in json.dumps(covered), covered
        await page.locator("#cover").evaluate("e=>e.style.display='none'")
        revealed = await report("find", {"tab_id": None, "query": "Dispatch BP-1207"})
        assert not revealed["elements"] and "Dispatch BP-1207" in revealed["text"]
        CHECKS.append("same-origin-immutable-effect-recycle-remote-read-only-query-cover-reveal")

        await page.reload()
        await page.evaluate("""() => {
          const container=document.createElement('div');
          for (let i=0;i<2050;i++) {
            const hidden=document.createElement('span');hidden.hidden=true;
            hidden.textContent='SYNTHETIC_PRIVATE';container.append(hidden);
          }
          document.body.prepend(container);
        }""")
        bounded = await report("read_page", {"tab_id": None, "filter": "all"})
        assert "work_limit" in bounded["omitted"] and not bounded["elements"], bounded
        assert "SYNTHETIC_PRIVATE" not in json.dumps(bounded)
        CHECKS.append("all-visited-hidden-siblings-charge-whole-read-work")

    declarations = frozenset({(url, "case_a", "guest"), (url, "case_a", "team")})
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        for invalid in (frozenset({(url, "case_a", "guest\ud800")}), frozenset({(url, "case_a\udfff", "guest")})):
            try:
                PlaywrightBrowser(
                    driver.context, set(driver.allowed_origins), owned_fixture_urls=urls, public_values=invalid
                )
            except ValueError:
                pass
            else:
                raise AssertionError("Non-scalar public value declaration was admitted")
        CHECKS.append("reject-non-scalar-immutable-public-value-declarations")
    async with open_browser(url, owned_fixture_urls=urls, public_values=declarations) as driver:
        value_read = await driver.read_page({"tab_id": None, "filter": "interactive"})
        assert isinstance(value_read, dict)
        by_label = {e["label"]: e for e in value_read["elements"]}
        assert by_label["Name"].get("value") == "fixture input"
        assert by_label["Category"].get("options") == [
            {"label": "Standard", "value": "standard"},
            {"label": "Urgent", "value": "urgent"},
        ]
        _, page = driver.page(None)
        await page.locator("#category option").first.evaluate("""option => {
            option.dataset.browserPrivate='';
            option.value='PRIVATE_OPTION_VALUE';
            option.textContent='PRIVATE_OPTION_LABEL';
        }""")
        redacted = await driver.read_page({"tab_id": None, "filter": "interactive"})
        assert isinstance(redacted, dict) and "PRIVATE_OPTION" not in json.dumps(redacted), redacted
        assert "private" in redacted["omitted"]
        await page.reload()
        await page.locator("#row").evaluate("e => e.dataset.browserPrivate = ''")
        private_read = await driver.read_page({"tab_id": None, "filter": "all"})
        assert "fixture input" not in json.dumps(private_read) and "Confirm" not in json.dumps(private_read)
        await page.reload()
        await driver.navigate({"tab_id": None, "url": url.replace("/fixture", "/again")})
        other = await driver.read_page({"tab_id": None, "filter": "interactive"})
        assert "fixture input" not in json.dumps(other)
        CHECKS.append("declared-tuple-values-private-ancestor-override-exact-document")

    async with open_browser(url, owned_fixture_urls=urls, public_values=declarations) as driver:
        _, page = driver.page(None)
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)
        # A small number of fully visible native selects is enough to exceed
        # the whole-read byte cap. No effect is necessary to prove truncation.
        await page.evaluate("""() => {
          const row=document.querySelector('#row');
          row.innerHTML='';
          for(let index=0;index<12;index++){
            const select=document.createElement('select');
            select.dataset.browserField='team';
            select.setAttribute('aria-label','Queue '+index);
            Object.assign(select.style,{position:'fixed',left:((index%4)*225)+'px',
              top:(Math.floor(index/4)*90)+'px',width:'210px',height:'60px'});
            for(let j=0;j<35;j++){
              const option=document.createElement('option');
              option.value='v'.repeat(500)+j;
              option.textContent='L'.repeat(240)+j;
              select.append(option);
            }
            row.append(select);
          }
        }""")
        output = await browser.execute(function("read_page", {"tab_id": None, "filter": "all"}))
        content = output["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        data = json.loads(content[0]["text"])
        assert data["ok"] is True
        bounded = data["result"]
        assert "report_limit" in bounded["omitted"] and "target_limit" in bounded["omitted"], bounded["omitted"]
        assert len(json.dumps(bounded, ensure_ascii=False, separators=(",", ":")).encode()) <= 65536
        assert bounded["elements"] and all(len(item["options"]) <= 32 for item in bounded["elements"])
        await page.evaluate("""() => {
            document.querySelector('#row').innerHTML='<p></p>';
            document.querySelector('p').textContent='Bounded '.repeat(5000);
        }""")
        output = await browser.execute(function("get_page_text", {"tab_id": None}))
        content = output["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        bounded = json.loads(content[0]["text"])["result"]
        assert len(bounded["text"].encode()) <= 16384 and "text_limit" in bounded["omitted"]
        assert not bounded["elements"]
        CHECKS.append("actual-select-option-report-and-visible-text-utf8-bounds-through-sdk")


async def interrupted_actions(url: str, urls: frozenset[str]) -> None:
    for kind in ("click", "type", "select_option", "set_checked", "scroll_to"):
        async with open_browser(
            url, owned_fixture_urls=urls, public_values=frozenset({(url, "ROW", "choice")})
        ) as driver:
            _, page = driver.page(driver.active)
            await page.evaluate("""() => {
                document.body.innerHTML = `<section data-record-id="ROW">
                  <button id="save">Save row</button>
                  <label for="note">Note</label><input id="note" data-browser-field="note">
                  <label for="choice">Choice</label><select id="choice" size="3" data-browser-field="choice">
                  <option value="standard">Standard</option><option value="express">Express</option></select>
                  <label for="checked">Complete</label><input type="checkbox" id="checked" data-browser-field="checked">
                </section>`;
                const longChoice = document.createElement('option');
                longChoice.textContent = 'Oversized choice';
                longChoice.value = '😺'.repeat(129);
                document.querySelector('#choice').append(longChoice);
            }""")
            report = await driver.read_page({"tab_id": None, "filter": "all"})
            assert isinstance(report, dict)
            choice = next(item for item in report["elements"] if item["label"] == "Choice")
            assert "options" in choice
            assert [(item["label"], item["value"]) for item in choice["options"]] == [
                ("Standard", "standard"),
                ("Express", "express"),
            ]
            assert "value" in report["omitted"]
            refs = {item["label"]: item["ref"] for item in report["elements"]}
            entered, release, drained, stop = asyncio.Event(), asyncio.Event(), asyncio.Event(), asyncio.Event()
            original = ElementHandle.evaluate

            async def evaluate(
                handle: ElementHandle,
                expression: str,
                arg: Any = None,
                *,
                action: str = kind,
                scan: Callable[..., Awaitable[Any]] = original,
                ready: asyncio.Event = entered,
                gate: asyncio.Event = release,
                finished: asyncio.Event = drained,
            ) -> Any:
                payload = cast(object, arg)
                if not isinstance(payload, dict) or cast("dict[str, object]", payload).get("action") != action:
                    return await scan(handle, expression, arg)
                result = await scan(handle, expression, arg)
                assert result is True, action
                ready.set()
                await gate.wait()
                finished.set()
                return result

            with patch.object(ElementHandle, "evaluate", evaluate):
                if kind == "click":
                    request = driver.click({"tab_id": None, "target": refs["Save row"]}, cancelled=stop.is_set)
                elif kind == "type":
                    request = driver.type(
                        {"tab_id": None, "target": refs["Note"], "text": "accepted"}, cancelled=stop.is_set
                    )
                elif kind == "select_option":
                    request = driver.select_option(
                        {"tab_id": None, "target": refs["Choice"], "values": ["express"]}, cancelled=stop.is_set
                    )
                elif kind == "set_checked":
                    request = driver._set_checked(
                        {"tab_id": None, "target": refs["Complete"], "checked": True}, cancelled=stop.is_set
                    )
                else:
                    request = driver._scroll_to({"tab_id": None, "target": refs["Save row"]}, cancelled=stop.is_set)
                task = asyncio.create_task(request)
                closed = asyncio.create_task(page.wait_for_event("close", timeout=1500))
                try:
                    await entered.wait()
                    stop.set()
                    done, pending = await asyncio.wait({task}, timeout=1.5)
                    assert not pending and task in done, kind
                    try:
                        task.result()
                    except (BrowserCancelledError, asyncio.CancelledError):
                        pass
                    else:
                        raise AssertionError(f"Owned {kind} did not report Stop")
                    assert driver._unusable
                    await closed
                    assert page.is_closed()
                    release.set()
                    await drained.wait()
                    try:
                        await driver.state()
                    except RuntimeError:
                        pass
                    else:
                        raise AssertionError("Completed late input revived a retired driver")
                finally:
                    release.set()
                    await asyncio.gather(task, closed, return_exceptions=True)
    print("PASS owned option admission, five postdispatch interrupted actions, delegated context closed")


async def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    second = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    Thread(target=server.serve_forever, daemon=True).start()
    Thread(target=second.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    remote = f"http://127.0.0.1:{second.server_port}"
    url = base + "/fixture"
    urls = frozenset(
        {
            url,
            base + "/again",
            base + "/effect",
            base + "/redirect",
            base + "/download",
            base + "/failed",
            base + "/rich-child",
            remote + "/rich-child",
            remote + "/effect",
        }
    )
    try:
        await interrupted_actions(url, urls)
        await date_feedback(url, urls)
        await forms(url, urls)
        await submit_bounds(url, urls)
        await rich_reads(url, urls, remote)
        await exercise(url, urls)
        await uncertain(url, urls, close_fails=False)
        await uncertain(url, urls, close_fails=True)
        for case in ("button", "row", "iframe", "rotate"):
            await visibility(url, urls, case)
        for member in ("navigate", "new_tab"):
            await refused_navigation(url, urls, member)
        await event_outputs(url, urls)
        await reference_lifecycle(url, urls)
        print(json.dumps({"checks": CHECKS, "effects": EFFECTS, "api_requests": 0}, indent=2))
    finally:
        server.shutdown()
        server.server_close()
        second.shutdown()
        second.server_close()


async def date_feedback(url: str, urls: frozenset[str]) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        await page.evaluate("""() => {
          document.body.innerHTML = `<section id="row" data-record-id="fixture_date">
            <label>Date<input id="date" type="date" name="date"></label>
            <label>Note<textarea id="note" name="note"></textarea></label></section>`;
          window.dateEvents=[];
          for(const kind of ['input','change'])
            document.addEventListener(kind,e=>dateEvents.push([e.type,e.target.id]));
          window.dateSnapshot=()=>({date:date.value,note:note.value,events:dateEvents.slice()});
        }""")
        browser = AsyncBrowserToolset(driver, members=["type"], confirm=approve)
        refs = await selected(driver)
        before = await page.evaluate("dateSnapshot()")
        failed = await browser.execute(function("type", {"tab_id": None, "target": refs["Date"], "text": "12/30/2031"}))
        content = failed["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        result = json.loads(content[0]["text"])
        assert result["ok"] is False and result["error"] == "Use a valid native date in YYYY-MM-DD format.", result
        assert await page.evaluate("dateSnapshot()") == before
        refs = await selected(driver)
        valid = await browser.execute(function("type", {"tab_id": None, "target": refs["Date"], "text": "2031-12-30"}))
        content = valid["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        assert json.loads(content[0]["text"])["ok"] is True
        assert await page.evaluate("dateSnapshot()") == {
            "date": "2031-12-30",
            "note": "",
            "events": [["input", "date"], ["change", "date"]],
        }
        for change in ("stale", "covered", "private"):
            refs = await selected(driver)
            await page.evaluate(
                """kind => {
              if (kind==='stale') date.replaceWith(date.cloneNode(true));
              else if (kind==='private') date.dataset.browserPrivate='';
              else document.body.insertAdjacentHTML('beforeend',
                '<div id="cover" style="display:block;position:fixed;inset:0;z-index:999;background:white"></div>');
            }""",
                change,
            )
            before = await page.evaluate("dateSnapshot()")
            failed = await browser.execute(
                function(
                    "type",
                    {
                        "tab_id": None,
                        "target": refs["Date"],
                        "text": "12/30/2031",
                    },
                )
            )
            content = failed["output"]
            assert isinstance(content, list) and content[0]["type"] == "input_text"
            result = json.loads(content[0]["text"])
            assert result["ok"] is False and "stale" in result["error"].lower(), (change, result)
            assert await page.evaluate("dateSnapshot()") == before, change
            await page.evaluate("""() => {
              document.querySelector('#cover')?.remove(); date.removeAttribute('data-browser-private');
            }""")

        refs = await selected(driver)
        before = await page.evaluate("dateSnapshot()")
        requests: list[dict[str, Any]] = []
        records: list[str] = []

        def transport(request: httpx2.Request) -> httpx2.Response:
            requests.append(json.loads(request.content))
            date = function("type", {"tab_id": None, "target": refs["Date"], "text": "12/30/2031"})
            date.id, date.call_id = "fc_date", "date"
            note = function("type", {"tab_id": None, "target": refs["Note"], "text": "must stay empty"})
            note.id, note.call_id = "fc_note", "note"
            ordinary = ResponseFunctionToolCall(
                id="fc_ordinary",
                call_id="ordinary",
                type="function_call",
                status="completed",
                name="record",
                arguments="{}",
            )
            return httpx2.Response(
                200,
                json={
                    "id": "resp_fixture",
                    "object": "response",
                    "created_at": 0,
                    "status": "completed",
                    "output": [item.model_dump(by_alias=True, exclude_unset=True) for item in (date, note, ordinary)]
                    if len(requests) == 1
                    else [
                        {
                            "id": "msg_fixture",
                            "type": "message",
                            "role": "assistant",
                            "status": "completed",
                            "content": [{"type": "output_text", "text": "done", "annotations": []}],
                        }
                    ],
                },
            )

        async def record(_args: dict[str, object]) -> str:
            records.append("ordinary")
            return "recorded"

        runner = AsyncResponsesToolRunner(
            browser=browser,
            functions=[
                AsyncRegisteredFunction(
                    tool={
                        "type": "function",
                        "name": "record",
                        "strict": True,
                        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
                    },
                    execute=record,
                )
            ],
        )
        async with AsyncOpenAI(
            api_key="synthetic-local-only", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport))
        ) as client:
            await runner.run(client, {"model": "fixture", "input": "Local test"})
        assert len(requests) == 2 and records == ["ordinary"]
        results = [item for item in requests[1]["input"] if item.get("type") == "function_call_output"]
        assert [item["call_id"] for item in results] == ["date", "note", "ordinary"]
        assert json.loads(results[0]["output"][0]["text"])["error"] == "Use a valid native date in YYYY-MM-DD format."
        assert "earlier browser action" in json.loads(results[1]["output"][0]["text"])["error"]
        assert await page.evaluate("dateSnapshot()") == before
        CHECKS.append("native-date-feedback-no-events-recovery-guards-and-real-mixed-batch-skip")


async def submit_bounds(url: str, urls: frozenset[str]) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        browser = AsyncBrowserToolset(driver, members=["read_page", "click"], confirm=approve)
        for length, required, permitted in ((3, False, True), (2400, False, False), (3, True, False), (3, False, True)):
            # Each case installs a fresh form in the same context. The early
            # Send ref can be issued even when a later read reaches its bound.
            await page.evaluate(
                """({length, required}) => {
                  document.body.innerHTML = `
                    <section data-record-id="case_a"><form id="native">
                      <button aria-label="Send">Send</button><div id="fields"></div>
                    </form><output id="receipt"></output></section>`;
                  const form = document.querySelector('#native');
                  const fields = document.querySelector('#fields');
                  for (let index = 0; index < length; index++) {
                    const input = document.createElement('input');
                    input.type = 'hidden'; input.name = 'fixture' + index; input.value = '0';
                    fields.append(input);
                  }
                  if (required) {
                    const input = document.createElement('input');
                    input.required = true; input.setAttribute('aria-label', 'Required');
                    fields.append(input);
                  }
                  window.submission = {clicks: 0, invalid: 0, sent: 0};
                  form.addEventListener('click', () => { window.submission.clicks++; });
                  form.addEventListener('invalid', () => { window.submission.invalid++; }, true);
                  form.addEventListener('submit', (event) => {
                    event.preventDefault(); window.submission.sent++;
                    document.querySelector('#receipt').textContent = 'Sent';
                  });
                }""",
                {"length": length, "required": required},
            )
            result = await browser.execute(function("read_page", {"tab_id": None, "filter": "interactive"}))
            output = result["output"]
            assert isinstance(output, list) and output[0]["type"] == "input_text"
            body = json.loads(output[0]["text"])
            assert body["ok"] is True
            if length > 2000:
                assert "work_limit" in body["result"]["omitted"]
            ref = next(item["ref"] for item in body["result"]["elements"] if item["label"] == "Send")
            result = await browser.execute(function("click", {"tab_id": None, "target": ref}))
            output = result["output"]
            assert isinstance(output, list) and output[0]["type"] == "input_text"
            assert json.loads(output[0]["text"])["ok"] is permitted, (length, required)
            # The real native click, validation and submit callbacks prove both
            # the refusal boundary and successful fresh-read recovery.
            actual = await page.evaluate("""() => ({
                ...window.submission,
                receipt: document.querySelector('#receipt').textContent,
                controls: document.querySelector('#native').elements.length,
            })""")
            assert actual == {
                "clicks": int(permitted),
                "invalid": 0,
                "sent": int(permitted),
                "receipt": "Sent" if permitted else "",
                "controls": length + 1 + int(required),
            }, (length, required, actual)
        CHECKS.append("submit-shared-work-bound-no-click-invalid-or-submit-small-native-validation-and-fresh-recovery")


async def forms(url: str, urls: frozenset[str]) -> None:
    declarations = frozenset(
        (url, "form_a", field) for field in ("note", "date", "range", "check", "r1", "r2", "one", "many")
    )
    setup = """() => {
      document.body.innerHTML = `
        <section id="formrow" data-record-id="form_a">
          <form id="native">
            <label>Note<textarea id="note" data-browser-field="note" name="note"></textarea></label>
            <label>Date<input id="date" type="date" data-browser-field="date" name="date" min="2020-01-01" max="2040-12-31"></label>
            <label>Range<input id="amount" type="range" data-browser-field="range" name="amount" min="0" max="100" step="10"></label>
            <label>Include<input id="check" type="checkbox" data-browser-field="check" name="include"></label>
            <label>First<input id="r1" type="radio" data-browser-field="r1" name="route" value="first" checked></label>
            <label>Single<select id="one" data-browser-field="one" name="single"><option value="a">Alpha</option><option value="b">Beta</option></select></label>
            <label>Multiple<select id="many" multiple size="3" data-browser-field="many" name="tags"><option value="a" selected>Alpha</option><option value="b">Beta</option><option value="c">Gamma</option></select></label>
          </form>
          <label>External<input id="r2" type="radio" data-browser-field="r2" name="route" form="native" value="external"></label>
          <output id="live"></output>
        </section>`;
      window.formEvents=[];
      for (const kind of ['input','change','pointerover','focusin','invalid']) document.addEventListener(kind,e=>{
        window.formEvents.push([e.type,e.target.id]);
        live.textContent=JSON.stringify([...new FormData(native)]);
      });
      window.formSnapshot=()=>({
        values:[...new FormData(native)], selections:[...many.options].map(o=>o.selected),
        checked:[r1.checked,r2.checked,check.checked], events:window.formEvents.slice(), visible:live.textContent
      });
    }"""
    async with open_browser(url, owned_fixture_urls=urls, public_values=declarations) as driver:
        _, page = driver.page(None)
        await page.evaluate(setup)
        browser = AsyncBrowserToolset(
            driver, members=["read_page", "get_page_text", "type", "click", "select_option"], confirm=approve
        )

        async def act(member: str, label: str, extra: dict[str, object], *, ok: bool = True) -> None:
            refs = await selected(driver)
            before = await page.evaluate("formSnapshot()")
            result = await browser.execute(function(member, {"target": refs[label], "tab_id": None, **extra}))
            output = result["output"]
            assert isinstance(output, list) and output[0]["type"] == "input_text"
            assert json.loads(output[0]["text"])["ok"] is ok, (label, output)
            if not ok:
                assert await page.evaluate("formSnapshot()") == before

        await act("type", "Note", {"text": "Fixture only"})
        await act("type", "Date", {"text": "2031-02-03"})
        await act("type", "Range", {"text": "40"})
        await act("click", "Include", {})
        await act("click", "External", {})
        await act("select_option", "Single", {"values": ["b"]})
        await act("select_option", "Multiple", {"values": ["b", "c"]})
        snapshot = await page.evaluate("formSnapshot()")
        assert snapshot["checked"] == [False, True, True]
        assert snapshot["selections"] == [False, True, True]
        assert snapshot["values"] == [
            ["note", "Fixture only"],
            ["date", "2031-02-03"],
            ["amount", "40"],
            ["include", "on"],
            ["single", "b"],
            ["tags", "b"],
            ["tags", "c"],
            ["route", "external"],
        ], snapshot
        assert snapshot["events"] == [
            ["input", "note"],
            ["input", "date"],
            ["change", "date"],
            ["input", "amount"],
            ["change", "amount"],
            ["input", "check"],
            ["change", "check"],
            ["input", "r2"],
            ["change", "r2"],
            ["input", "one"],
            ["change", "one"],
            ["input", "many"],
            ["change", "many"],
        ], snapshot["events"]
        assert json.loads(snapshot["visible"]) == snapshot["values"]
        read = await browser.execute(function("read_page", {"tab_id": None, "filter": "interactive"}))
        content = read["output"]
        assert isinstance(content, list) and content[0]["type"] == "input_text"
        data = json.loads(content[0]["text"])["result"]
        fields = {e["label"]: e for e in data["elements"]}
        assert fields["Include"]["checked"] is True and fields["First"]["checked"] is False
        assert [option["selected"] for option in fields["Multiple"]["options"]] == [False, True, True]
        assert fields["Range"]["value"] == "40"
        assert fields["Note"]["value"] == "Fixture only"
        CHECKS.append("native-forms-events-independent-FormData-external-radio-and-permitted-V1")

        await act("select_option", "Multiple", {"values": []})
        assert await page.evaluate("[...many.selectedOptions].length") == 0
        await act("type", "Date", {"text": ""})
        assert await page.evaluate("date.value") == ""
        for label, text in (
            ("Date", "2031-02-30"),
            ("Date", "01/02/2031"),
            ("Range", "45"),
            ("Range", "110"),
            ("Range", "NaN"),
        ):
            await act("type", label, {"text": text}, ok=False)
        for values in (["a", "missing"], ["b", "b"]):
            await act("select_option", "Multiple", {"values": values}, ok=False)
        await page.evaluate("many.options[2].disabled=true")
        await act("select_option", "Multiple", {"values": ["a", "c"]}, ok=False)
        await page.evaluate(
            "many.options[2].disabled=false;many.options[0].selected=true;many.options[0].dataset.browserPrivate=''"
        )
        await act("select_option", "Multiple", {"values": ["b"]}, ok=False)
        await page.evaluate(
            "delete many.options[0].dataset.browserPrivate;one.insertAdjacentHTML('beforeend','<optgroup disabled><option value=z>Zed</option></optgroup>')"
        )
        await act("select_option", "Single", {"values": ["z"]}, ok=False)
        await page.evaluate("one.insertAdjacentHTML('beforeend','<option value=b>Other beta</option>')")
        await act("select_option", "Single", {"values": ["b"]}, ok=False)
        CHECKS.append("form-full-set-validation-date-range-duplicate-private-disabled-before-any-effect")

        for held in ("check", "group", "owner", "private", "offrecord", "readonly", "covered"):
            await page.evaluate(setup)
            refs = await selected(driver)

            async def confirm_change(_ctx: object, *, case: str = held) -> bool:
                if case == "check":
                    await page.evaluate("check.checked=true")
                elif case == "group":
                    await page.evaluate("r2.checked=true")
                elif case == "owner":
                    await page.evaluate("""() => {
                      const previous=native, peer=r1;
                      const replacement=document.createElement('form');replacement.id=previous.id;
                      const contents=[...previous.childNodes];
                      previous.replaceWith(replacement);replacement.append(...contents);
                      window.formReplaced=peer===r1 && r2.form===replacement && previous!==r2.form;
                    }""")
                    assert await page.evaluate("formReplaced") is True
                elif case == "private":
                    await page.evaluate("r1.dataset.browserPrivate=''")
                elif case == "offrecord":
                    await page.evaluate(
                        "const other=document.createElement('section'); other.dataset.recordId='form_b'; document.body.append(other);other.append(r1)"
                    )
                elif case == "readonly":
                    await page.evaluate("date.readOnly=true")
                else:
                    await page.evaluate("""() => {
                      const b=date.getBoundingClientRect(), cover=document.createElement('div');
                      cover.style=`position:fixed;z-index:999;left:${b.left}px;top:${b.top}px;width:${b.width}px;height:${b.height}px`;
                      document.body.append(cover)
                    }""")
                return True

            control = AsyncBrowserToolset(driver, members=["click", "type"], confirm=confirm_change)
            target = (
                "Include"
                if held == "check"
                else "External"
                if held in ("group", "owner", "private", "offrecord")
                else "Date"
            )
            member = "click" if target != "Date" else "type"
            events = len(await page.evaluate("formEvents"))
            out = await control.execute(
                function(
                    member,
                    {"target": refs[target], "tab_id": None, **({"text": "2030-10-10"} if member == "type" else {})},
                )
            )
            output = out["output"]
            assert isinstance(output, list) and output[0]["type"] == "input_text"
            assert json.loads(output[0]["text"])["ok"] is False, held
            assert len(await page.evaluate("formEvents")) == events
        CHECKS.append("held-consent-ref-check-state-actual-form-owner-external-group-readonly-and-cover")

        await page.evaluate(setup)
        await page.evaluate("formrow.append(r1.parentElement);r2.removeAttribute('form')")
        assert await page.evaluate("r1.form===null && r2.form===null") is True
        await act("click", "External", {})
        assert await page.evaluate("[r1.checked,r2.checked]") == [False, True]
        CHECKS.append("named-native-radio-group-with-null-form-owner")

        await page.evaluate(setup)
        await page.evaluate("r1.removeAttribute('name');r2.removeAttribute('name');r1.dataset.browserPrivate=''")
        await act("click", "External", {})
        assert await page.evaluate("[r1.checked,r2.checked]") == [True, True]
        CHECKS.append("unnamed-native-radios-do-not-group")

        for kind, attribute, dirty, minimum, good, bad in (
            ("date", "1970-01-02", "1970-01-05", "", "1970-01-04", "1970-01-03"),
            ("date", "1970-01-02", "1970-01-05", "1970-01-01", "1970-01-03", "1970-01-04"),
            ("range", "1", "7", "", "3", "2"),
            ("range", "1", "8", "0", "2", "3"),
        ):
            await page.evaluate(
                """({kind,attribute,dirty,minimum}) => {
                  document.body.innerHTML=`<section data-record-id="step">
                    <form id=stepform><label>Stepped<input id=stepped name=value data-browser-field=field
                      type=${kind} value="${attribute}" step=2></label></form><output id=stepout></output></section>`;
                  if (minimum) stepped.min=minimum;
                  stepped.value=dirty;
                  window.stepEvents=[];
                  for (const name of ['input','change','invalid','focusin','pointerover'])
                    stepped.addEventListener(name, e => {
                      stepEvents.push(e.type);
                      stepout.textContent=JSON.stringify([...new FormData(stepform)]);
                    });
                  window.stepSnapshot=()=>({value:stepped.value, attribute:stepped.getAttribute('value'),
                    valid:stepped.validity.valid, mismatch:stepped.validity.stepMismatch,
                    form:[...new FormData(stepform)], events:stepEvents.slice(), visible:stepout.textContent});
                }""",
                {"kind": kind, "attribute": attribute, "dirty": dirty, "minimum": minimum},
            )
            refs = await selected(driver)
            before = await page.evaluate("stepSnapshot()")
            result = await browser.execute(function("type", {"target": refs["Stepped"], "tab_id": None, "text": bad}))
            content = result["output"]
            assert isinstance(content, list) and content[0]["type"] == "input_text"
            assert json.loads(content[0]["text"])["ok"] is False and await page.evaluate("stepSnapshot()") == before
            refs = await selected(driver)
            result = await browser.execute(function("type", {"target": refs["Stepped"], "tab_id": None, "text": good}))
            content = result["output"]
            assert isinstance(content, list) and content[0]["type"] == "input_text"
            current = await page.evaluate("stepSnapshot()")
            assert json.loads(content[0]["text"])["ok"] is True
            assert current == {
                "value": good,
                "attribute": attribute,
                "valid": True,
                "mismatch": False,
                "form": [["value", good]],
                "events": ["input", "change"],
                "visible": json.dumps([["value", good]], separators=(",", ":")),
            }
            read = await driver.read_page({"tab_id": None, "filter": "all"})
            assert isinstance(read, dict)
            assert "value" in read["omitted"]
            assert all("value" not in item for item in read["elements"] if item["label"] == "Stepped")
        CHECKS.append("native-step-base-content-attribute-dirty-property-min-precedence-no-value-disclosure")

    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        await page.evaluate(setup)
        await page.evaluate("note.value='SYNTHETIC_PRIVATE';check.checked=true;r2.checked=true")
        read = await driver.read_page({"tab_id": None, "filter": "all"})
        assert isinstance(read, dict)
        assert "SYNTHETIC_PRIVATE" not in json.dumps(read) and "value" in read["omitted"]
        assert all(not ({"value", "options", "checked"} & e.keys()) for e in read["elements"])
        text = await driver.get_page_text({"tab_id": None})
        assert isinstance(text, dict) and not text["elements"] and "SYNTHETIC_PRIVATE" not in json.dumps(text)
        CHECKS.append("all-form-state-absent-without-launcher-tuple-including-text")

    async with open_browser(url, owned_fixture_urls=urls, public_values=declarations) as driver:
        _, page = driver.page(None)
        await page.evaluate(setup)
        # A first event may run page code before a second event is dispatched.
        await page.evaluate("many.addEventListener('input',()=>{formrow.dataset.recordId='form_b'})")
        refs = await selected(driver)
        before = await page.evaluate("({ ...formSnapshot(), record:formrow.dataset.recordId })")
        assert before["record"] == "form_a" and before["events"] == []
        observed: dict[str, Any] = {}
        close = driver.context.close

        async def record_then_close(*args: Any, **kwargs: Any) -> None:
            try:
                # Read the synchronous event log before the owned context closes.
                observed.update(await page.evaluate("({ ...formSnapshot(), record:formrow.dataset.recordId })"))
            finally:
                await close(*args, **kwargs)

        with patch.object(driver.context, "close", record_then_close):
            try:
                await driver.select_option({"target": refs["Multiple"], "tab_id": None, "values": ["b"]})
            except Exception:
                pass
            else:
                raise AssertionError("Post-input logical replacement must retire the owned context.")
        assert observed["record"] == "form_b" and observed["events"] == [["input", "many"]]
        assert observed["selections"] == [False, True, False]
        assert page.is_closed()
        try:
            await driver.state()
        except RuntimeError:
            pass
        else:
            raise AssertionError("An uncertain form action remained usable.")
        CHECKS.append("input-handler-recycles-record-no-change-to-new-row-retired")

    for event in ("input", "change"):
        async with open_browser(url, owned_fixture_urls=urls, public_values=declarations) as driver:
            _, page = driver.page(None)
            await page.evaluate(setup)
            refs = await selected(driver)
            await page.locator("#one").evaluate(
                "(node, kind) => node.addEventListener(kind, () => { node.value='a'; }, {once:true})", event
            )
            try:
                await driver.select_option({"target": refs["Single"], "tab_id": None, "values": ["b"]})
            except Exception:
                pass
            else:
                raise AssertionError("A select restored its old value but the driver reported success.")
            try:
                await driver.state()
            except RuntimeError:
                pass
            else:
                raise AssertionError("An uncertain select remained usable.")
            CHECKS.append(f"select-restored-during-{event}-retires")

    for label, selector, event, text in (
        ("Note", "#note", "input", "Local note"),
        ("Date", "#date", "change", "2026-10-10"),
        ("Range", "#amount", "change", "40"),
    ):
        async with open_browser(url, owned_fixture_urls=urls, public_values=declarations) as driver:
            _, page = driver.page(None)
            await page.evaluate(setup)
            refs = await selected(driver)
            await page.locator(selector).evaluate(
                "(node, kind) => node.addEventListener(kind, () => { node.value=''; }, {once:true})", event
            )
            try:
                await driver.type({"target": refs[label], "tab_id": None, "text": text})
            except Exception:
                pass
            else:
                raise AssertionError("A text input reverted its value but the driver reported success.")
            try:
                await driver.state()
            except RuntimeError:
                pass
            else:
                raise AssertionError("An uncertain type remained usable.")
            CHECKS.append(f"type-{label}-restored-during-{event}-retires")

    for member, label, fields in (
        ("click", "Include", {}),
        ("type", "Note", {"text": "Local note"}),
        ("select_option", "Single", {"values": ["b"]}),
        ("set_checked", "Include", {"checked": True}),
        ("scroll_to", "Note", {}),
    ):
        async with open_browser(url, owned_fixture_urls=urls, public_values=declarations) as driver:
            tab, page = driver.page(None)
            await page.evaluate(setup)
            refs = await selected(driver)
            action: dict[str, object] = {"target": refs[label], "tab_id": tab, **fields}
            handler = getattr(driver, member)
            try:
                await handler(action, cancelled=lambda: True)
            except BrowserCancelledError:
                pass
            else:
                raise AssertionError("A pre-cancelled input reached dispatch.")
            await driver.state()
            handle = driver._refs[tab][refs[label]][0]
            original = handle.evaluate
            reached = asyncio.Event()
            release = asyncio.Event()
            cancelled = False

            async def delayed(expression: str, arg: Any = None) -> Any:
                result = await original(expression, arg)  # noqa: B023 -- Drained before the next case.
                reached.set()  # noqa: B023
                await release.wait()  # noqa: B023
                return result

            with patch.object(handle, "evaluate", delayed):
                pending = asyncio.create_task(handler(action, cancelled=lambda: cancelled))  # noqa: B023
                await reached.wait()
                cancelled = True
                release.set()
                try:
                    await pending
                except BrowserCancelledError:
                    pass
                else:
                    raise AssertionError("Cancellation after dispatched input did not fail.")
            try:
                await handler(action)
            except RuntimeError:
                pass
            else:
                raise AssertionError("A retired context allowed another input.")
            CHECKS.append(f"cancel-{member}-predispatch-reuse-postdispatch-retire")


if __name__ == "__main__":
    asyncio.run(main())
