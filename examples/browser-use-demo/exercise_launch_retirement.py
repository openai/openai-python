"""A pending ordinary launch must settle the agent and retain one cleanup owner."""

from __future__ import annotations

import json
import asyncio
from typing import Any, cast

from server import Fieldwork, WorkspaceBrowser
from playwright.async_api import Playwright


async def exercise(fail_close: bool) -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    class LocalBrowser:
        closes = 0

        def once(self, _event: str, _callback: object) -> None:
            pass

        async def close(self) -> None:
            self.closes += 1
            if fail_close:
                raise RuntimeError("Controlled launch retirement failure")

    class LocalChromium:
        launches = 0

        async def launch(self, **_options: Any) -> LocalBrowser:
            self.launches += 1
            entered.set()
            await release.wait()
            return opened

    class LocalPlaywright:
        chromium = LocalChromium()

    opened = LocalBrowser()
    local = LocalPlaywright()
    browser = WorkspaceBrowser(cast(Playwright, local))
    app = Fieldwork(browser, "http://127.0.0.1:41234")
    headers = {"Host": "127.0.0.1:41234", "Origin": app.origin, "X-Demo-Token": app.token}
    body = json.dumps({"taskId": "support", "api": "decisions", "mode": "rehearsal"}).encode()
    started = await app.handle("POST", "/api/start", headers, body)
    assert started.status == 200
    run = app.current
    assert run is not None and run.agent is not None
    try:
        await entered.wait()
        run.stop()
        done, _ = await asyncio.wait({run.agent}, timeout=0.75)
        assert run.agent in done, "Agent remained blocked on abandoned browser launch."
        assert run.status == "stopped" and run.busy()
        assert run.cleanup_status == "pending" and opened.closes == 0
        reply = await app.handle("POST", "/api/start", headers, body)
        assert reply.status == 409 and local.chromium.launches == 1
        release.set()
        assert run.cleanup is not None
        await asyncio.wait_for(asyncio.shield(run.cleanup), 1)
        assert opened.closes == 1
        assert run.cleanup_status == ("failed" if fail_close else "completed")
        assert run.busy() is fail_close
        await browser.close()
        assert opened.closes == 1
    finally:
        release.set()
        await asyncio.gather(run.agent, *([run.cleanup] if run.cleanup else []), return_exceptions=True)
        await browser.close()


async def main() -> None:
    await exercise(False)
    await exercise(True)
    print(json.dumps({"checks": 2, "passed": True, "api_calls": 0, "vendor_calls": 0}))


if __name__ == "__main__":
    asyncio.run(main())
