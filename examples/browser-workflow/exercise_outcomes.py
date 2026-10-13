"""Check workflow screenshots and failure receipts with local pages and a fake API."""

from __future__ import annotations

import os
import sys
import copy
import json
import asyncio
import argparse
from typing import Any, AsyncGenerator
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import asynccontextmanager
from unittest.mock import patch

import httpx2
import workflow

from openai import AsyncOpenAI
from openai.lib.browser import BrowserConfirmContext


async def allow(_action: BrowserConfirmContext) -> bool:
    return True


async def main(mode: str) -> None:
    if mode == "identifiers":
        original = json.loads((Path(__file__).parent / "assets" / "fixtures.json").read_text())["A"]
        accepted: list[str] = []
        with TemporaryDirectory(prefix="workflow-ids-") as directory:
            fixture_path = Path(directory) / "fixtures.json"
            for name, fragment in (("NUL", "\0"), ("CR", "\r"), ("surrogate", "\ud800")):
                for field in ("requests", "slots"):
                    fixture = copy.deepcopy(original)
                    fixture[field][0]["id"] = f"id-{fragment}-end"
                    if field == "requests":
                        fixture["requestId"] = fixture["requests"][0]["id"]
                    fixture_path.write_text(json.dumps({"C": fixture}))
                    try:
                        with workflow.serve(fixture_path):
                            accepted.append(f"{field}:{name}")
                    except ValueError as error:
                        assert str(error).startswith(f"{field}[0].id is invalid"), error
            fixture_path.write_text(json.dumps({"C-\ud800": original}))
            try:
                with workflow.serve(fixture_path):
                    accepted.append("fixture:surrogate")
            except ValueError as error:
                assert str(error).startswith("Fixture IDs must be nonempty strings"), error
            fixture = copy.deepcopy(original)
            variant = 'C\0\r " & Ω 🌕'
            request_id = 'REQ " & Ω 🌕\nline'
            slot_id = 'ROOM " & Ω 🌕\nline'
            fixture["requestId"] = request_id
            fixture["requests"][0]["id"] = request_id
            fixture["slots"][1]["id"] = slot_id
            fixture_path.write_text(json.dumps({variant: fixture}))
            with workflow.serve(fixture_path) as server:
                async with workflow.open_workflow(server, variant, confirm=allow) as current:
                    request = current.page.locator("[data-request]").first
                    assert await request.get_attribute("data-request") == request_id
                    await request.click()
                    slot = current.page.locator("[data-slot]").nth(1)
                    assert await slot.get_attribute("data-slot") == slot_id
                    assert (
                        await current.page.evaluate(
                            "(id) => JSON.parse(localStorage.getItem(`workflow.${id}.selected`))", variant
                        )
                        == request_id
                    )
                    await slot.click()
                    await current.page.locator('[data-route="dispatch"]').click()
                    send = current.page.locator("[data-send]")
                    assert await send.get_attribute("data-send") == request_id
                    await send.click()
                    stored = await current.stored()
                    assert stored["bookings"][request_id]["slot"] == slot_id
                    assert stored["correspondence"][request_id]["request"] == request_id
                    assert await current.verify()
                    await current.page.reload()
                    assert await current.verify()
                    print("PASS LF, Unicode, quote and ampersand IDs select, book, send and verify after reload")
        assert not accepted, accepted
        print("PASS 6 request/slot IDs and 1 fixture ID rejected before serving; URL-safe fixture IDs round-trip")
        return
    if mode == "pixels":
        with workflow.serve() as server:
            async with workflow.open_workflow(server, "A", confirm=allow) as current:
                for route in ("/inbox", "/schedule", "/dispatch"):
                    result = await current.execute(
                        "navigate", {"tab_id": None, "url": server[0] + route + "?fixture=A"}
                    )
                    assert result["ok"]
                    image = await current.driver.screenshot({"tab_id": None})
                    assert image["type"] == "input_image"
                    image_url = image.get("image_url")
                    assert isinstance(image_url, str) and image_url.startswith("data:image/png;base64,")
        print("PASS screenshots work on all three reviewed workflow pages")
        return

    assert mode in ("browser-loss", "operator-stop")
    original_open = workflow.open_workflow
    active: workflow.Workflow | None = None
    requests = 0

    @asynccontextmanager
    async def remembered(*args: Any, **kwargs: Any) -> AsyncGenerator[workflow.Workflow, None]:
        nonlocal active
        async with original_open(*args, **kwargs) as current:
            active = current
            yield current

    async def respond(request: httpx2.Request) -> httpx2.Response:
        nonlocal requests
        assert request.url.host == "api.openai.com"
        requests += 1
        assert active is not None
        if mode == "browser-loss":
            await active.driver.context.close()
        else:
            raise asyncio.CancelledError()
        return httpx2.Response(
            200,
            json={
                "id": "synthetic",
                "object": "response",
                "status": "completed",
                "output": [
                    {"id": "message", "type": "message", "role": "assistant", "status": "completed", "content": []}
                ],
            },
        )

    def client(**options: Any) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key="synthetic",
            base_url="https://api.openai.com/v1",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(respond)),
            **options,
        )

    with TemporaryDirectory(prefix="workflow-outcome-") as directory:
        receipt = Path(directory) / "receipt.json"
        with (
            patch.object(workflow, "open_workflow", remembered),
            patch.object(workflow, "AsyncOpenAI", client),
            patch.dict(os.environ, {"OPENAI_MODEL": "synthetic", "OPENAI_API_KEY": "synthetic"}),
        ):
            try:
                await workflow.main(
                    argparse.Namespace(
                        mode="run",
                        fixture="A",
                        api="responses",
                        receipt=str(receipt),
                        headed=False,
                        data=None,
                    )
                )
            except SystemExit as error:
                assert error.code == 1
        saved = json.loads(receipt.read_text())
        assert saved["status"] == ("failed" if mode == "browser-loss" else "stopped"), saved
        assert saved["cleanup"] is True
        assert requests == 1
        if mode == "operator-stop":
            assert saved["stored"] == {"bookings": {}, "correspondence": {}}, saved
    print(f"PASS {mode} has the correct CLI receipt and cleanup")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "pixels"))
