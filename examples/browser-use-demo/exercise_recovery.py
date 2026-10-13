"""Launch recovery uses a real local Chromium. No API calls."""

from __future__ import annotations

import json
import asyncio
from typing import Any
from unittest.mock import patch

from server import Fieldwork, WorkspaceBrowser, serve
from playwright.async_api import Error, Browser, async_playwright


async def main() -> None:
    from runner import Run

    async with async_playwright() as playwright:
        owner = WorkspaceBrowser(playwright)
        original = playwright.chromium.launch
        count = 0

        async def launch(**options: Any) -> Browser:
            nonlocal count
            count += 1
            if count == 1:
                raise Error("Controlled first launch failure")
            return await original(**options)

        try:
            with patch.object(playwright.chromium, "launch", launch):
                try:
                    await owner.new_context()
                except Error:
                    pass
                else:
                    raise AssertionError("The controlled launch did not fail.")
                assert count == 1
                context = await owner.new_context()
                before = await owner.opened()
                assert count == 2 and context in owner.contexts
                await before.close()
                context = await owner.new_context()
                after = await owner.opened()
                assert count == 3 and after is not before and context in owner.contexts
                await context.close()
        finally:
            await owner.close()
        print("PASS launch failure and browser disconnection permit a fresh workspace; one browser per live cache")

    async with async_playwright() as playwright:
        owner = WorkspaceBrowser(playwright)
        app = Fieldwork(owner, "http://127.0.0.1:1")
        try:
            for outcome in ("committed", "wrong", "not_committed"):
                run = Run(app, {"environment": "browser", "taskId": "service", "api": "responses", "mode": "live"})
                context = await owner.new_context()
                run.context = context
                run.task_page = await context.new_page()
                business = run.business
                assert business is not None
                expected = {
                    "operation": "schedule",
                    "job": run.task["job"],
                    "date": run.task["fields"]["Visit date"],
                    "technician": run.task["fields"]["Technician"],
                    "note": run.task["fields"]["Service note"] if outcome != "wrong" else "Different approved note",
                }
                permit = business.authorize(expected)
                received = None
                if outcome != "not_committed":
                    received = asyncio.create_task(business.receive({}, json.dumps(expected).encode()))
                    await permit["staged"]

                    async def rejected_dom(*_args: Any, **_kwargs: Any) -> Any:
                        raise Error("Controlled DOM acknowledgement failure after the host committed")

                    with patch.object(run.task_page, "wait_for_function", rejected_dom):
                        try:
                            await business.finish(permit)
                        except Error:
                            pass
                        else:
                            raise AssertionError("The controlled DOM acknowledgement must fail")
                    assert (await received).status == 200
                run.stop("browser_closed")
                assert run.result == ("verified" if outcome == "committed" else "unverified")
                assert run.status == "browser_closed"
                assert business.snapshot()["verified"] is (outcome == "committed")
                assert run.cleanup is not None
                await run.cleanup
        finally:
            await owner.close()
    print("PASS committed, wrong and precommit host records preserve truthful verification on Stop")

    original_close = WorkspaceBrowser.close
    original_wait = asyncio.wait
    release = asyncio.Event()
    reaped = asyncio.Event()

    async def held_close(self: WorkspaceBrowser) -> None:
        await release.wait()
        try:
            await original_close(self)
        finally:
            reaped.set()

    async def short_shutdown(*args: Any, **kwargs: Any) -> Any:
        if kwargs.get("timeout") == 35:
            kwargs["timeout"] = 0.02
        return await original_wait(*args, **kwargs)

    with patch.object(WorkspaceBrowser, "close", held_close), patch.object(asyncio, "wait", short_shutdown):
        try:
            try:
                async with serve(0) as app:
                    context = await app.browser.new_context()
                    await context.new_page()
            except RuntimeError as error:
                assert "Workspace cleanup did not finish" in str(error)
            else:
                raise AssertionError("A held owned browser close must report incomplete shutdown")
            assert not reaped.is_set()
        finally:
            release.set()
            await asyncio.wait_for(reaped.wait(), 2)
    print("PASS public serve exit covers browser cleanup in the existing deadline and observes later settlement")


if __name__ == "__main__":
    asyncio.run(main())
