"""Optional local network checks for the browser fixture. No API requests.

Run --case basic, chain, popup, redirects, or origin to diagnose boundaries separately. The
default runs them all; a failed counter assertion is not a successful refusal.
"""

from __future__ import annotations

import os
import re
import json
import base64
import asyncio
import argparse
from typing import Any, cast
from threading import Event, Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

from browser_driver import origin as canonical_origin, open_browser
from playwright.async_api import Page, Error, async_playwright

from openai.lib.browser import BrowserError

ALLOWED_HITS: list[str] = []
DENIED_HITS: list[str] = []
CHECKS: list[str] = []
HOLD = Event()
CONTRACT_HITS: list[dict[str, object]] = []


class Fixture(BaseHTTPRequestHandler):
    denied_origin = ""
    is_denied = False

    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        hits = DENIED_HITS if self.is_denied else ALLOWED_HITS
        path = self.path
        hits.append(("upgrade:" if self.headers.get("upgrade") else "") + path)
        if path.startswith("/contract/") and not self.is_denied:
            data = self.rfile.read(int(self.headers.get("content-length", "0")))
            CONTRACT_HITS.append({"path": path, "method": self.command, "body": data.decode()})
            redirect = re.fullmatch(r"/contract/status/(301|302|303|307|308)", path)
            body = b""
            if redirect:
                status, headers = int(redirect[1]), {"Location": "../target?scope=exact"}
            elif path == "/contract/cross":
                port = cast(ThreadingHTTPServer, self.server).server_port
                status, headers = 302, {"Location": f"http://localhost:{port}/contract/remote"}
            elif path == "/contract/cache":
                status, headers = 304, {"Location": self.denied_origin + "/unused-304-location"}
            else:
                status, headers = 200, {"Content-Type": "text/plain"}
                body = b"fixture contract body"
        elif self.is_denied:
            body = b"Denied counter control"
            status, headers = 200, {"Content-Type": "text/html"}
        elif path == "/chain":
            body = b""
            status, headers = 302, {"Location": "/hop"}
        elif path == "/hop":
            body = b""
            status, headers = 307, {"Location": self.denied_origin + "/end"}
        elif path == "/good-chain":
            body = b""
            status, headers = 302, {"Location": "/positive"}
        elif path == "/script.js":
            body = b"window.fixtureScript = 1"
            status, headers = 200, {"Content-Type": "text/javascript"}
        elif path == "/sw.js":
            body = b"self.addEventListener('fetch', () => {})"
            status, headers = 200, {"Content-Type": "text/javascript"}
        elif path == "/image.gif":
            body = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==")
            status, headers = 200, {"Content-Type": "image/gif"}
        else:
            body = b"<!doctype html><title>Local request fixture</title><body>Permitted fixture</body>"
            status, headers = 200, {"Content-Type": "text/html"}
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if path == "/hold":
            HOLD.wait(3)
        try:
            if self.command != "HEAD":
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self) -> None:
        self.do_GET()

    def do_HEAD(self) -> None:
        self.do_GET()


class Denied(Fixture):
    is_denied = True


async def wait_hit(hits: list[str], target: str) -> None:
    async def wait() -> None:
        while target not in hits:
            await asyncio.sleep(0.01)

    await asyncio.wait_for(wait(), 2.4)
    assert target in hits, f"Missing positive evidence for {target}"


async def fetch_fixture(page: Page, path: str, **options: object) -> dict[str, Any]:
    return await page.evaluate(
        """async ({path,options}) => {
          try {const response=await fetch(path,options);return {status:response.status,text:await response.text()};}
          catch {return {status:0,text:''};}
        }""",
        {"path": path, "options": options},
    )


async def check(case: str) -> None:
    denied = ThreadingHTTPServer(("127.0.0.1", 0), Denied)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    threads = [Thread(target=s.serve_forever, daemon=True) for s in (denied, server)]
    for thread in threads:
        thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    alternate = f"http://localhost:{server.server_port}"
    blocked = f"http://127.0.0.1:{denied.server_port}"
    Fixture.denied_origin = blocked
    url = origin + "/fixture"
    paths = (
        "/fixture",
        "/positive",
        "/good-chain",
        "/chain",
        "/hop",
        "/image.gif",
        "/script.js",
        "/sw.js",
        "/hold",
        "/contract/target?scope=exact",
        "/contract/cross",
        "/contract/cache",
        *(f"/contract/status/{code}" for code in (301, 302, 303, 307, 308)),
    )
    urls = frozenset({*(origin + path for path in paths), alternate + "/positive", alternate + "/contract/remote"})
    try:
        # Positive control of the independent counter, never a real public site.
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                env={key: value for key in ("PATH", "HOME", "TMPDIR") if (value := os.environ.get(key)) is not None},
            )
            try:
                context = await browser.new_context(service_workers="block")
                page = await context.new_page()
                await page.goto(blocked + "/counter-control", timeout=3000)
                assert DENIED_HITS == ["/counter-control"], DENIED_HITS
                await context.close()
            finally:
                await browser.close()
        DENIED_HITS.clear()
        CHECKS.append("unguarded isolated positive proves denied server counter is live")
        async with open_browser(url, owned_fixture_urls=urls) as driver:
            tab, page = driver.page(None)
            page.set_default_timeout(2800)
            await page.evaluate("""() => {
                document.cookie='only_this_run=present; SameSite=Lax';
                localStorage.setItem('only_this_run','present');
            }""")
            await driver.navigate({"tab_id": tab, "url": origin + "/positive"})
            assert page.url == origin + "/positive"
            await wait_hit(ALLOWED_HITS, "/positive")
            await driver.navigate({"tab_id": tab, "url": url})
            CHECKS.append("direct allowed navigation reaches real positive endpoint")
            if case in ("all", "basic"):
                results: Any = await page.evaluate(
                    """async ({allowed,cross,blocked}) => {
                  const resource=(tag,src)=>new Promise(resolve=>{
                    const node=document.createElement(tag);
                    const done=event=>resolve(event.type);
                    node.onload=done;node.onerror=done;node.src=src;document.body.append(node);
                  });
                  const fetchText=async url=>{
                    try{return {ok:(await fetch(url)).ok};}catch{return {ok:false};}
                  };
                  const out={
                    allowedImage:await resource('img',allowed+'/image.gif'),
                    deniedImage:await resource('img',blocked+'/image.gif'),
                    allowedScript:await resource('script',allowed+'/script.js'),
                    deniedScript:await resource('script',blocked+'/script.js'),
                    scriptRan:window.fixtureScript,
                    allowedFetch:await fetchText(allowed+'/positive'),
                    deniedFetch:await fetchText(blocked+'/fetch'),
                    sameFrame:await resource('iframe',allowed+'/positive'),
                    crossFrame:await resource('iframe',cross+'/positive'),
                    deniedFrame:await resource('iframe',blocked+'/child'),
                  };
                  const child=[...document.querySelectorAll('iframe')].find(node=>node.src===cross+'/positive');
                  try{out.parentReadsChild=!!child.contentWindow.document;}catch{out.parentReadsChild=false;}
                  const socket=url=>new Promise(resolve=>{
                    const ws=new WebSocket(url);
                    ws.onopen=()=>{ws.close();resolve('open')};
                    ws.onerror=()=>resolve('error');ws.onclose=()=>resolve('close');
                  });
                  out.allowedSocket=await socket(allowed.replace('http:','ws:')+'/socket');
                  out.deniedSocket=await socket(blocked.replace('http:','ws:')+'/socket');
                  try{
                    const registration=await navigator.serviceWorker.register('/sw.js');
                    out.worker=registration?'registered':'blocked';
                  }catch {out.worker='blocked';}
                  return out;
                }""",
                    {"allowed": origin, "cross": alternate, "blocked": blocked},
                )
                assert results["allowedImage"] == results["allowedScript"] == "load", results
                assert results["scriptRan"] == 1 and results["allowedFetch"] == {"ok": True}, results
                assert results["sameFrame"] == results["crossFrame"] == "load", results
                assert not results["parentReadsChild"]
                assert any(frame.url == alternate + "/positive" for frame in page.frames)
                assert results["deniedImage"] == results["deniedScript"] == "error", results
                assert results["deniedFetch"] == {"ok": False}, results
                assert results["allowedSocket"] != "open" and results["deniedSocket"] != "open", results
                assert results["worker"] == "blocked" and "/sw.js" not in ALLOWED_HITS, results
                assert not any(hit.startswith("upgrade:") for hit in ALLOWED_HITS)
                assert DENIED_HITS == [], DENIED_HITS
                CHECKS.extend(
                    [
                        "allowed image, script, fetch, same/cross-origin frame load",
                        "denied image, script, fetch and child frame never reach independent server",
                        "both WebSocket origins blocked; worker registration and script blocked",
                    ]
                )
                pending = asyncio.create_task(
                    page.evaluate("fetch('/hold').then(r => r.text()).catch(() => 'canceled')")
                )
                await wait_hit(ALLOWED_HITS, "/hold")
                await driver.context.close()
                try:
                    await pending
                except Error:
                    pass
                else:
                    raise AssertionError("Held request survived closed context")
                assert DENIED_HITS == []
                CHECKS.append("closing owned context cancels admitted allowed body; not counted as policy refusal")
        async with open_browser(url, owned_fixture_urls=urls) as driver:
            tab, page = driver.page(None)
            state = await page.evaluate("""() => ({
                cookies:document.cookie,saved:localStorage.getItem('only_this_run'),
                controlled:!!navigator.serviceWorker.controller
            })""")
            assert state == {"cookies": "", "saved": None, "controlled": False}, state
            assert DENIED_HITS == [], DENIED_HITS
            CHECKS.append("fresh run has no prior cookie, local storage or worker")
            if case in ("all", "redirects"):
                for method in ("GET", "HEAD", "POST"):
                    CONTRACT_HITS.clear()
                    options: dict[str, object] = {"method": method}
                    if method == "POST":
                        options["body"] = "fixture payload"
                    direct = await fetch_fixture(page, "/contract/target?scope=exact", **options)
                    assert direct == {"status": 200, "text": "" if method == "HEAD" else "fixture contract body"}, (
                        direct
                    )
                    body = "fixture payload" if method == "POST" else ""
                    assert CONTRACT_HITS == [{"path": "/contract/target?scope=exact", "method": method, "body": body}]
                    for code in (301, 302, 303, 307, 308):
                        CONTRACT_HITS.clear()
                        result = await fetch_fixture(page, f"/contract/status/{code}", **options)
                        print(json.dumps({"code": code, "method": method, "result": result, "requests": CONTRACT_HITS}))
                        assert CONTRACT_HITS == [
                            {"path": f"/contract/status/{code}", "method": method, "body": body}
                        ], ("A redirect fetched or replayed an allowed target", CONTRACT_HITS)
                        assert result == {"status": 0, "text": ""}, result
                CONTRACT_HITS.clear()
                cache = await fetch_fixture(page, "/contract/cache", headers={"If-None-Match": "fixture"})
                assert cache == {"status": 304, "text": ""}, cache
                assert CONTRACT_HITS == [{"path": "/contract/cache", "method": "GET", "body": ""}]
                assert DENIED_HITS == []
                CHECKS.append("direct GET/HEAD/POST and 304; redirects stop after first effect without retry")
            if case in ("all", "origin"):
                for configured, expected in (
                    ("https://BÜCHER.de", "https://xn--bcher-kva.de:443"),
                    ("https://faß.de", "https://xn--fa-hia.de:443"),
                    ("http://%65xample.com:81", "http://example.com:81"),
                    ("http://[0:0:0:0:0:0:0:1]:81", "http://[::1]:81"),
                    ("http://0x7f000001:81", "http://127.0.0.1:81"),
                    ("http://127.1:0", "http://127.0.0.1:0"),
                ):
                    serialized = await page.evaluate("url => new URL(url).href", configured)
                    assert canonical_origin(configured) == expected
                    assert canonical_origin(serialized) == expected
                CHECKS.append("IDNA, escaped hosts and IP aliases match Chromium without changing ports")
                prior = await driver.state()
                assert "observation" in prior
                sequence = prior["observation"]["sequence"]
                direct = await page.evaluate(
                    """url=>new Promise(resolve=>{
                      const iframe=document.createElement('iframe');
                      iframe.onload=()=>{try{resolve({loaded:true,readable:!!iframe.contentWindow.document});}
                        catch{resolve({loaded:true,readable:false});}};
                      iframe.onerror=()=>resolve({loaded:false,readable:false});
                      iframe.src=url;document.body.append(iframe);
                    })""",
                    alternate + "/contract/remote",
                )
                assert direct == {"loaded": True, "readable": False}, direct
                assert any(frame.url == alternate + "/contract/remote" for frame in page.frames)
                CONTRACT_HITS.clear()
                await page.evaluate(
                    """url=>new Promise(resolve=>{
                      const iframe=document.createElement('iframe');
                      iframe.onload=()=>resolve('load');iframe.onerror=()=>resolve('error');
                      iframe.src=url;document.body.append(iframe);
                    })""",
                    origin + "/contract/cross",
                )
                print(json.dumps({"origin_navigation": CONTRACT_HITS}))
                assert CONTRACT_HITS == [{"path": "/contract/cross", "method": "GET", "body": ""}], (
                    "Changed-origin navigation fetched a target",
                    CONTRACT_HITS,
                )
                reported = await driver.state()
                assert "observation" in reported
                assert not any(
                    change["sequence"] > sequence and change["type"] == "navigation_refused"
                    for change in reported["observation"]["changes"]
                ), "Allowed unsupported redirect mislabeled as URL-policy refusal"
                CHECKS.append("native remote origin isolated; redirect navigation refused without policy event")
            if case in ("all", "popup"):
                async with page.expect_popup(timeout=2800) as popup:
                    await page.evaluate("url=>window.open(url)", blocked + "/popup")
                opened = await popup.value
                try:
                    await opened.wait_for_load_state("domcontentloaded", timeout=2800)
                except Error:
                    pass
                assert DENIED_HITS == [], DENIED_HITS
                # The SDK cannot obtain a valid starting state here. Even with the
                # driver's active ID, raw driver reads and close must refuse.
                for action in (
                    driver.state,
                    lambda: driver.read_page({"tab_id": driver.active, "filter": "all"}),
                    lambda: driver.close_tab({"tab_id": driver.active}),
                ):
                    try:
                        await action()
                    except RuntimeError as error:
                        assert "outside its installed fixture" in str(error)
                    else:
                        raise AssertionError("Blocked popup became an owned page")
                # The blocked error document is not an installed fixture. Close it before reading owned state.
                await opened.close()
                reported = await driver.state()
                assert "observation" in reported
                assert any(item["type"] == "navigation_refused" for item in reported["observation"]["changes"])
                assert len(reported["observation"]["changes"]) <= 32
                CHECKS.append("blocked popup refuses state/read/close; launcher closes it and original state recovers")
            if case in ("all", "chain"):
                try:
                    await driver.navigate({"tab_id": tab, "url": origin + "/chain"})
                except BrowserError as error:
                    assert "outcome is unknown; context retired" in str(error), error
                except Error:
                    pass
                await wait_hit(ALLOWED_HITS, "/chain")
                print(json.dumps({"checks_before_chain": CHECKS, "allowed": ALLOWED_HITS, "denied": DENIED_HITS}))
                assert [hit for hit in ALLOWED_HITS if hit in ("/chain", "/hop")] == ["/chain"]
                assert DENIED_HITS == [], f"Allowed redirect hop reached denied server: {DENIED_HITS}"
                CHECKS.append("denied redirect chain stopped before next host request")
        print(
            json.dumps(
                {
                    "success": True,
                    "checks": CHECKS,
                    "allowed": ALLOWED_HITS,
                    "denied": DENIED_HITS,
                    "api_requests": 0,
                    "not_proved": [
                        "OS/host-process firewall",
                        "WebRTC",
                        "DNS/other protocols",
                        "hosted provider egress",
                    ],
                },
                indent=2,
            )
        )
    finally:
        HOLD.set()
        for server_to_close in (server, denied):
            server_to_close.shutdown()
            server_to_close.server_close()
        for thread in threads:
            thread.join(timeout=4)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("all", "basic", "chain", "popup", "redirects", "origin"), default="all")
    options = parser.parse_args()
    await asyncio.wait_for(check(options.case), 35)


if __name__ == "__main__":
    asyncio.run(main())
