"""Check the borrowed-browser example's human approval policy without a browser."""

from __future__ import annotations

import json
import asyncio
from typing import cast
from unittest.mock import patch

import run as example
import httpx2
from browser_driver import PlaywrightBrowser

from openai import AsyncOpenAI
from openai.lib.browser import KeyInput, TypeInput, BrowserState


class Driver:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def state(self) -> BrowserState:
        return {"tabs": [{"id": "1", "title": "Fixture", "url": "https://fixture.invalid", "active": True}]}

    async def type(self, _arguments: TypeInput) -> None:
        self.calls.append("type")

    async def key(self, _arguments: KeyInput) -> None:
        self.calls.append("key")

    def allows(self, url: str) -> bool:
        return url == "https://fixture.invalid"


async def check(member: str, arguments: dict[str, object], *, automatic: bool, allowed: bool) -> None:
    driver = Driver()
    prompts: list[str] = []
    requests = 0

    def approve(prompt: str) -> str:
        prompts.append(prompt)
        return "y"

    def respond(_request: httpx2.Request) -> httpx2.Response:
        nonlocal requests
        requests += 1
        output: list[dict[str, object]] = []
        if requests == 1:
            output.append(
                {
                    "id": "fc_fixture",
                    "type": "function_call",
                    "call_id": "call_fixture",
                    "name": f"browser_{member}",
                    "arguments": json.dumps(arguments),
                    "status": "completed",
                }
            )
        else:
            assert requests == 2
            output.append(
                {
                    "id": "msg_fixture",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": "done", "annotations": []}],
                }
            )
        return httpx2.Response(
            200,
            json={
                "id": f"resp_{requests}",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": "",
                "output": output,
            },
        )

    with patch.object(example, "input", approve, create=True):
        async with AsyncOpenAI(
            api_key="fixture-key-not-real",
            base_url="https://fixture.invalid/v1",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(respond)),
        ) as client:
            await example.make_runner(cast(PlaywrightBrowser, driver), auto_approve_fixture=automatic).run(
                client, {"model": "", "input": "Check synthetic approval", "store": False}, max_steps=2
            )
    assert driver.calls == ([member] if allowed else []), (member, automatic, driver.calls)
    assert len(prompts) == (1 if allowed and not automatic else 0), (member, automatic, prompts)


async def main() -> None:
    key: dict[str, object] = {"tab_id": "1", "keys": ["Enter"]}
    unbound_type: dict[str, object] = {"tab_id": "1", "target": None, "text": "Synthetic note"}
    bound_type: dict[str, object] = {"tab_id": "1", "target": "original-field", "text": "Synthetic note"}
    for member, arguments, automatic, allowed in (
        ("key", key, False, False),
        ("type", unbound_type, False, False),
        ("type", bound_type, False, True),
        ("key", key, True, True),
        ("type", unbound_type, True, True),
    ):
        await asyncio.wait_for(check(member, arguments, automatic=automatic, allowed=allowed), timeout=5)
    print("PASS: human approval refuses unbound input; targeted input and explicit fixture mode still work.")


if __name__ == "__main__":
    asyncio.run(main())
