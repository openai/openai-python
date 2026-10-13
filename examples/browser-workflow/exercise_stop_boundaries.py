"""Verify cancellation forwarding and final workflow proof with a local response."""

from __future__ import annotations

import json
import asyncio
from typing import Any, cast

import httpx2
from workflow import serve, approval_text, open_workflow
from browser_driver import PlaywrightBrowser

from openai import AsyncOpenAI
from openai.lib.browser import BrowserConfirmContext


async def main() -> None:
    stopped = False
    forwarded = False

    def cancelled() -> bool:
        return stopped

    class Description:
        async def describe_target(self, _action: object, *, cancelled: Any = None) -> dict[str, str]:
            nonlocal stopped, forwarded
            forwarded = callable(cancelled)
            stopped = True
            raise asyncio.CancelledError()

    action = cast(BrowserConfirmContext, {"member": "click", "arguments": {"tab_id": None, "target": "ref"}})
    try:
        await approval_text(cast(PlaywrightBrowser, Description()), action, cancelled=cancelled)
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("Approval description must observe Stop.")
    assert forwarded

    records = {
        "bookings": {"REQ-401": {"request": "REQ-401", "slot": "R2", "time": "10:00"}},
        "correspondence": {"REQ-401": {"request": "REQ-401", "slot": "R2", "recipient": "cedar@example.test"}},
    }

    async def confirm(_action: BrowserConfirmContext) -> bool:
        return True

    with serve() as server:
        async with open_workflow(server, "A", confirm=confirm) as workflow:
            await workflow.page.evaluate(
                """saved => {
              localStorage.setItem('workflow.A.bookings', JSON.stringify(saved.bookings));
              localStorage.setItem('workflow.A.correspondence', JSON.stringify(saved.correspondence));
            }""",
                records,
            )
            assert await workflow.verify()
            evaluate = workflow.page.evaluate
            entered = asyncio.Event()
            release = asyncio.Event()

            async def stop_after_read(expression: str, arg: Any = None) -> Any:
                value = await evaluate(expression, arg)
                entered.set()
                await release.wait()
                return value

            workflow.page.evaluate = stop_after_read
            requests = 0

            def transport(_request: httpx2.Request) -> httpx2.Response:
                nonlocal requests
                requests += 1
                return httpx2.Response(
                    200,
                    json={
                        "id": "response",
                        "object": "response",
                        "status": "completed",
                        "output": [
                            {
                                "id": "message",
                                "type": "message",
                                "role": "assistant",
                                "status": "completed",
                                "content": [{"type": "output_text", "text": "Done", "annotations": []}],
                            }
                        ],
                    },
                )

            async with AsyncOpenAI(
                api_key="local-fixture",
                max_retries=0,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
            ) as client:
                running = asyncio.create_task(workflow.run(client, "", "responses"))
                await entered.wait()
                workflow.stopped = True
                try:
                    done, _ = await asyncio.wait({running}, timeout=0.75)
                    assert running in done, "Saved-record read did not stop."
                    assert running.cancelled(), "Stop during final verification must prevent verified status."
                finally:
                    release.set()
                    await asyncio.gather(running, return_exceptions=True)
            assert requests == 1 and workflow.stopped
            assert workflow.verified_records == records
            assert workflow.runner_error is None
    print(json.dumps({"checks": 2, "passed": True, "api_calls": 0, "vendor_calls": 0}))


if __name__ == "__main__":
    asyncio.run(main())
