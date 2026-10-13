"""Owned Chromium navigation, scroll and wait checks. Only local fixture traffic."""

from __future__ import annotations

import json
import time
import asyncio
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from browser_driver import PlaywrightBrowser, open_browser
from exercise_owned import EFFECTS, REQUESTS, Fixture, allow, approve, function, selected, no_effect, wait_effects

from openai.lib.browser import (
    BrowserError,
    BrowserReadV1,
    AsyncBrowserToolset,
    ReadPageScopedInput,
    BrowserCancelledError,
    BrowserConfirmContext,
)
from openai.types.responses.response_input_param import FunctionCallOutput

CHECKS: list[str] = []


def payload(output: FunctionCallOutput) -> dict[str, object]:
    blocks = output["output"]
    assert isinstance(blocks, list) and blocks[0]["type"] == "input_text"
    value: dict[str, object] = json.loads(blocks[0]["text"])
    return value


async def history(url: str, urls: frozenset[str]) -> None:
    async with open_browser(
        url, owned_fixture_urls=urls, public_values=frozenset({(url, "case_a", "guest")})
    ) as driver:
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)
        selected_tab, page = driver.page(None)
        before = await selected(driver)
        # Back may reach the initial blank page; it must not promise a transition.
        result = payload(await browser.execute(function("navigate", {"url": "back", "tab_id": selected_tab})))
        assert result["result"] == "History navigation checked." and result["ok"] is True
        await no_effect(lambda: driver.click({"target": before["Secondary"], "tab_id": selected_tab}))
        if page.url == "about:blank":
            result = payload(await browser.execute(function("navigate", {"url": "back", "tab_id": selected_tab})))
            assert result["result"] == "History navigation checked." and page.url == "about:blank"
        await driver.navigate({"url": url, "tab_id": selected_tab})
        CHECKS.append("null-history-invalidates-without-transition-claim")

        for address, expected in [
            (url.replace("/fixture", "/again"), "/again"),
            ("back", "/fixture"),
            ("forward", "/again"),
            ("reload", "/again"),
        ]:
            before = await selected(driver)
            previous = len(EFFECTS)
            result = payload(await browser.execute(function("navigate", {"url": address, "tab_id": selected_tab})))
            assert result["ok"] is True and page.url.endswith(expected)
            assert "SYNTHETIC_PRIVATE" not in json.dumps(result)
            await no_effect(partial(driver.click, {"target": before["Secondary"], "tab_id": selected_tab}))
            read = await driver.read_page({"tab_id": selected_tab, "filter": "interactive"})
            assert isinstance(read, dict)
            name = next(element for element in read["elements"] if element["label"] == "Name")
            assert ("value" in name) is (expected == "/fixture")
            button = next(element for element in read["elements"] if element["label"] == "Secondary")
            await driver.click({"target": button["ref"], "tab_id": selected_tab})
            await wait_effects(previous + 1)
            assert EFFECTS[-1]["id"] == "case_a" and EFFECTS[-1]["operation"] == "click"
        CHECKS.append("back-forward-reload-raw-policy-fresh-refs-tuple-document")

        current = page.url
        browser.url_policy = None
        denied = payload(await browser.execute(function("navigate", {"url": "back", "tab_id": selected_tab})))
        assert denied["ok"] is False and page.url == current
        CHECKS.append("removed-history-policy-does-not-navigate")

    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        # A no-network history entry must not disclose page text, screenshot,
        # or inherited field consent merely because its origin matches.
        await page.evaluate("history.pushState({}, '', '/SYNTHETIC_PRIVATE_route')")
        for action in (
            lambda: driver.state(),
            lambda: driver.get_page_text({"tab_id": None}),
            lambda: driver.screenshot({"tab_id": None}),
        ):
            try:
                await action()
            except RuntimeError as exc:
                assert "SYNTHETIC_PRIVATE" not in str(exc)
            else:
                raise AssertionError("uninstalled same-document URL disclosed state")
        assert "/SYNTHETIC_PRIVATE_route" not in REQUESTS
        CHECKS.append("uninstalled-no-network-history-never-disclosed")

    async with open_browser(url) as generic:
        assert generic.wait_for is None and generic.scroll_to is None
        try:
            PlaywrightBrowser(generic.context, set(generic.allowed_origins), owned_fixture_urls=urls)
        except ValueError:
            pass
        else:
            raise AssertionError("borrowed populated context claimed owned history")
        CHECKS.append("borrowed-context-not-upgraded-to-owned-history")


async def scrolling(url: str, urls: frozenset[str]) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        browser = AsyncBrowserToolset(driver, confirm=approve, url_policy=allow)
        _, page = driver.page(None)
        await page.evaluate("""() => {
          const box=document.createElement('div'); box.id='panel';
          box.style='height:170px;width:400px;overflow:auto';
          const sibling=document.createElement('div'); sibling.id='sibling';
          sibling.style='height:170px;width:400px;overflow:auto';
          sibling.innerHTML='<div style="height:1400px">Side panel</div>';
          row.before(box,sibling); box.append(row); row.prepend(secondary);
          window.armPreliminary();
        }""")
        original = await selected(driver)
        await page.evaluate("""() => {
          const gap=document.createElement('div'); gap.style.height='1000px'; row.prepend(gap);
        }""")
        offsets = """() => [panel.scrollTop,sibling.scrollTop,scrollX,scrollY,window.preliminary,window.revision]"""
        before = await page.evaluate(offsets)
        result = payload(
            await browser.execute(function("scroll_to", {"target": original["Secondary"], "tab_id": None}))
        )
        after = await page.evaluate(offsets)
        assert result["ok"] is True and after[0] > before[0] and after[1:] == before[1:]
        await no_effect(lambda: driver.click({"target": original["Secondary"], "tab_id": None}))
        fresh = await selected(driver)
        count = len(EFFECTS)
        await driver.click({"target": fresh["Secondary"], "tab_id": None})
        await wait_effects(count + 1)
        assert EFFECTS[-1]["operation"] == "click" and await page.evaluate("window.preliminary") == 0
        CHECKS.append("target-only-nearest-panel-old-ref-stale-no-pointer-or-focus")

        for condition in ("forged", "recycled", "hidden", "covered", "covered_inside"):
            refs = await selected(driver)
            await page.evaluate("panel.scrollTop=0")
            target = refs["Secondary"] if condition != "forged" else "forged"

            async def held_consent(_ctx: BrowserConfirmContext, *, held: str = condition) -> bool:
                if held == "recycled":
                    await page.evaluate("window.installRecord('case_b')")
                elif held == "hidden":
                    await page.evaluate("row.style.opacity='0'")
                elif held in ("covered", "covered_inside"):
                    await page.evaluate(
                        """inside => {
                          const r=panel.getBoundingClientRect(), cover=document.createElement('div');
                          cover.id='panel-cover';
                          cover.style=`position:fixed;z-index:999;background:white;left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px`;
                          (inside ? panel : document.body).append(cover);
                        }""",
                        held == "covered_inside",
                    )
                return True

            controlled = AsyncBrowserToolset(driver, members=["scroll_to"], confirm=held_consent)
            before = await page.evaluate(offsets)
            result = payload(await controlled.execute(function("scroll_to", {"target": target, "tab_id": None})))
            assert result["ok"] is False and await page.evaluate(offsets) == before
            await page.evaluate(
                "document.querySelector('#panel-cover')?.remove(); row.style.opacity='1'; window.installRecord('case_a'); panel.scrollTop=1000"
            )
        CHECKS.append("forged-hidden-recycled-inside-and-outside-covered-clipped-scroll-refuses-before-effects")

    async with open_browser(url, owned_fixture_urls=urls) as driver:
        _, page = driver.page(None)
        await page.evaluate(
            """other => {
                const frame=document.createElement('iframe');frame.id='child';
                frame.style='position:fixed;left:12px;top:12px;width:750px;height:500px;z-index:10';
                frame.src=other;document.body.append(frame);
            }""",
            url.replace("/fixture", "/again"),
        )
        frame_handle = await page.wait_for_selector("#child")
        assert frame_handle is not None
        frame = await frame_handle.content_frame()
        assert frame is not None
        await frame.wait_for_selector("#secondary")
        await frame.evaluate(
            """() => {
              const box=document.createElement('div');box.id='panel';
              box.style='height:170px;width:300px;overflow:auto';
              row.before(box);box.append(row);row.prepend(secondary);
            }"""
        )
        # The final Secondary ref in this known fixture belongs to the child.
        refs = await selected(driver)
        await frame.evaluate(
            "row.prepend(Object.assign(document.createElement('div'),{id:'gap'}));gap.style.height='1000px'"
        )
        for condition in ("covered", "partial_cover", "rotated"):

            async def obstruct(_ctx: BrowserConfirmContext, *, held: str = condition) -> bool:
                if held == "covered":
                    await page.evaluate(
                        """() => {
                          const cover=document.createElement('div');cover.id='obstruction';
                          cover.style='position:fixed;inset:0;background:white;z-index:100';document.body.append(cover);
                        }"""
                    )
                elif held == "partial_cover":
                    bounds = await frame.locator("#panel").bounding_box()
                    assert bounds is not None
                    await page.evaluate(
                        """bounds => {
                          const cover=document.createElement('div');cover.id='obstruction';
                          cover.style=`position:fixed;left:${bounds.x}px;top:${bounds.y}px;width:${bounds.width}px;height:${bounds.height}px;background:white;z-index:100`;
                          document.body.append(cover);
                        }""",
                        bounds,
                    )
                    assert await page.evaluate("""() => {
                      const box=child.getBoundingClientRect(), panel=child.contentDocument.querySelector('#panel').getBoundingClientRect();
                      return [document.elementFromPoint(box.x+box.width/2,box.y+box.height/2)?.id,
                        document.elementFromPoint(box.x+child.clientLeft+panel.x+panel.width/2,
                          box.y+child.clientTop+panel.y+panel.height/2)?.id];
                    }""") == ["child", "obstruction"]
                else:
                    await page.evaluate("child.style.rotate='180deg'")
                return True

            browser = AsyncBrowserToolset(driver, members=["scroll_to"], confirm=obstruct)
            baseline = await frame.evaluate("[panel.scrollTop,window.revision]")
            result = payload(
                await browser.execute(function("scroll_to", {"target": refs["Secondary"], "tab_id": None}))
            )
            assert result["ok"] is False and await frame.evaluate("[panel.scrollTop,window.revision]") == baseline
            await page.evaluate("document.querySelector('#obstruction')?.remove();child.style.rotate='none'")
        browser = AsyncBrowserToolset(driver, members=["scroll_to"], confirm=approve)
        result = payload(await browser.execute(function("scroll_to", {"target": refs["Secondary"], "tab_id": None})))
        assert result["ok"] is True and (await frame.evaluate("panel.scrollTop")) > 0
        CHECKS.append("same-origin-frame-full-and-partial-cover-and-rotate-refuse-visible-positive")


async def waiting(url: str, urls: frozenset[str]) -> None:
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        browser = AsyncBrowserToolset(driver, members=["wait_for"])
        tab, page = driver.page(None)
        refs = await selected(driver)
        started = time.monotonic()
        pending = asyncio.create_task(
            browser.execute(function("wait_for", {"text": "gate ready", "timeout_ms": 1500, "tab_id": tab}))
        )
        await asyncio.sleep(0.12)
        assert not pending.done()
        await page.evaluate(
            """() => {const note=document.createElement('p');note.textContent='gate   ready';document.body.append(note)}"""
        )
        result = payload(await pending)
        assert result["result"] == "Visible condition met." and time.monotonic() - started < 1.5
        # A read-only wait has issued and revoked no action refs.
        before = len(EFFECTS)
        await driver.click({"target": refs["Secondary"], "tab_id": tab})
        await wait_effects(before + 1)
        CHECKS.append("wait-gated-visible-condition-old-ref-retained")
    for text in ("SYNTHETIC_PRIVATE", "NESTED_SECRET", "PRIVATE_SECRET", "never appears"):
        # A read pending at its deadline can retire this disposable context.
        async with open_browser(url, owned_fixture_urls=urls) as driver:
            browser = AsyncBrowserToolset(driver, members=["wait_for"])
            tab, page = driver.page(None)
            await page.evaluate("""() => {
              const p=document.createElement('p');
              p.innerHTML='<span hidden>NESTED_SECRET</span><span data-browser-private>PRIVATE_SECRET</span>';
              document.body.append(p);
            }""")
            started = time.monotonic()
            result = payload(
                await browser.execute(function("wait_for", {"text": text, "timeout_ms": 125, "tab_id": tab}))
            )
            assert result["ok"] is False and result["error"] == "Visible condition timed out."
            assert 0.10 <= time.monotonic() - started <= 0.8
    CHECKS.append("wait-hidden-private-password-and-absent-time-out")
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        browser = AsyncBrowserToolset(driver, members=["wait_for"])
        tab, _ = driver.page(None)
        stop = False

        def cancelled() -> bool:
            return stop

        pending = asyncio.create_task(
            browser.execute(
                function("wait_for", {"text": "cancel gate", "timeout_ms": 1000, "tab_id": tab}), cancelled=cancelled
            )
        )
        await asyncio.sleep(0.06)
        stop = True
        try:
            await pending
        except BrowserCancelledError:
            pass
        else:
            raise AssertionError("cancelled wait reported success")
        CHECKS.append("persistent-cancel-wait-drains")
    async with open_browser(url, owned_fixture_urls=urls) as driver:
        browser = AsyncBrowserToolset(driver, members=["wait_for"])
        tab, page = driver.page(None)
        pending = asyncio.create_task(
            browser.execute(function("wait_for", {"text": "after navigation", "timeout_ms": 1000, "tab_id": tab}))
        )
        await asyncio.sleep(0.06)
        await driver.navigate({"url": url.replace("/fixture", "/again"), "tab_id": tab})
        await page.evaluate("document.body.append(document.createTextNode('after navigation'))")
        result = payload(await pending)
        assert result["ok"] is False
        CHECKS.append("wait-does-not-follow-new-document")


async def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    url = base + "/fixture"
    urls = frozenset(base + path for path in ("/fixture", "/again", "/effect", "/redirect"))
    try:
        await history(url, urls)
        await scrolling(url, urls)
        await waiting(url, urls)
        for mode in ("deadline", "Stop"):
            async with open_browser(url, owned_fixture_urls=urls) as driver:
                tab, page = driver.page(None)
                held = await selected(driver)
                original = driver._read_owned
                arrived = asyncio.Event()
                release = asyncio.Event()
                stopped = False
                count = len(EFFECTS)
                driver.context.once("close", lambda _context: release.set())  # noqa: B023 -- The context closes before the next loop case.

                async def controlled_read(
                    tab_id: str | None,
                    *,
                    full: bool,
                    text_only: bool = False,
                    query: str = "",
                    deadline: float | None = None,
                    scoped: ReadPageScopedInput | None = None,
                    wait_generation: int | None = None,
                ) -> BrowserReadV1:
                    arrived.set()  # noqa: B023 -- This observation drains before advancing the loop.
                    await release.wait()  # noqa: B023 -- This observation drains before advancing the loop.
                    return await original(  # noqa: B023 -- This context stays current until the read drains.
                        tab_id,
                        full=full,
                        text_only=text_only,
                        query=query,
                        deadline=deadline,
                        scoped=scoped,
                        wait_generation=wait_generation,
                    )

                limit = asyncio.get_running_loop().call_later(2, release.set)
                try:
                    with patch.object(driver, "_read_owned", controlled_read):
                        assert driver.wait_for is not None
                        start = time.monotonic()
                        reading = asyncio.ensure_future(
                            driver.wait_for(
                                {
                                    "tab_id": tab,
                                    "text": "not present",
                                    "timeout_ms": 150 if mode == "deadline" else 30000,
                                },
                                cancelled=lambda: stopped,  # noqa: B023 -- Reading is awaited before advancing the loop.
                            )
                        )
                        notified = asyncio.create_task(arrived.wait())
                        try:
                            done, _ = await asyncio.wait(
                                {reading, notified}, timeout=2, return_when=asyncio.FIRST_COMPLETED
                            )
                            if reading in done:
                                await reading
                                raise AssertionError("The wait finished before entering its observation.")
                            assert notified in done, "The controlled observation did not start."
                        finally:
                            notified.cancel()
                            await asyncio.gather(notified, return_exceptions=True)
                        if mode == "Stop":
                            stopped = True
                        try:
                            await reading
                        except (BrowserError, BrowserCancelledError):
                            pass
                        else:
                            raise AssertionError("A stalled observation succeeded")
                        assert time.monotonic() - start < 1.2
                    assert len(EFFECTS) == count
                    try:
                        await driver.click({"tab_id": tab, "target": held["Secondary"]})
                    except RuntimeError:
                        pass
                    else:
                        raise AssertionError("A retired context accepted an old reference")
                    assert driver._retirement is not None
                    await driver._retirement
                    assert page.is_closed()
                    assert len(EFFECTS) == count
                    CHECKS.append(f"stalled-scan-{mode}-retires-before-late-effect")
                finally:
                    limit.cancel()
                    release.set()
        print(json.dumps({"checks": CHECKS, "effects": len(EFFECTS), "requests": len(REQUESTS), "api_requests": 0}))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    asyncio.run(main())
