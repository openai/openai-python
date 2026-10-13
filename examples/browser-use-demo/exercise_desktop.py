"""Native Fieldwork desktop with controlled Responses, approvals and handoff."""

from __future__ import annotations

import json
import struct
import asyncio
import argparse
from pathlib import Path
from collections.abc import Mapping, Callable
from typing_extensions import override

import httpx2 as httpx
from server import serve
from exercise import JSONMap, receipt


class ControlledDesktop(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.calls = 0

    @override
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url.path.endswith("/responses") and body["store"] is False
        assert any(tool["type"] in ("computer", "computer_use_preview") for tool in body["tools"])
        self.calls += 1
        output: list[JSONMap]
        if self.calls in (1, 2):
            output = [
                {
                    "type": "computer_call",
                    "id": f"comp_{self.calls}",
                    "call_id": f"call_{self.calls}",
                    "status": "completed",
                    "actions": [
                        {"type": "click", "button": "left", "x": 200, "y": 215},
                        {"type": "click", "button": "left", "x": 700, "y": 180},
                        {"type": "type", "text": "Desktop receipt D-2201"},
                        {"type": "keypress", "keys": ["CTRL", "S"]},
                    ],
                }
            ]
        else:
            output = [
                {
                    "type": "message",
                    "id": "msg",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": "Done", "annotations": []}],
                }
            ]
        return httpx.Response(
            200,
            json={
                "id": f"resp_{self.calls}",
                "object": "response",
                "model": "fixture-desktop",
                "status": "completed",
                "created_at": 0,
                "output": output,
            },
        )


def binding(run: JSONMap) -> JSONMap:
    return {"runId": run["id"], **run["desktop"]}


async def main(runtime_dir: Path) -> None:
    transport = ControlledDesktop()
    async with serve(0, "synthetic-desktop-wire-key", {"responses": "fixture-desktop"}, transport, runtime_dir) as app:
        async with httpx.AsyncClient(base_url=app.origin, timeout=90) as client:
            client.headers["X-Demo-Token"] = app.token

            async def send(path: str, value: Mapping[str, object], status: int = 200) -> JSONMap:
                reply = await client.post(path, json=value)
                assert reply.status_code == status, (path, reply.status_code, reply.text)
                return reply.json()

            async def state_until(predicate: Callable[[JSONMap], object]) -> JSONMap:
                state: JSONMap = {}
                for _ in range(1000):
                    reply = await client.get("/api/state")
                    assert reply.status_code == 200, reply.text
                    state = reply.json()["run"]
                    if predicate(state):
                        return state
                    await asyncio.sleep(0.1)
                raise AssertionError(state)

            config = (await client.get("/api/state")).json()
            assert config["desktopAvailable"] is True
            await send(
                "/api/start",
                {"environment": "desktop", "taskId": "desktop", "api": "decisions", "mode": "rehearsal"},
                400,
            )
            await send(
                "/api/start", {"environment": "desktop", "taskId": "desktop", "api": "responses", "mode": "live"}
            )
            held = await state_until(lambda run: run["approval"] or run["owner"] == "stopped")
            assert held["approval"], held
            old = {**binding(held), "approvalId": held["approval"]["id"], "approved": True}
            await send("/api/take-control", {**binding(held), "desktopId": "earlier-guest"}, 409)
            image = await client.get(
                f"/api/view?run={held['id']}&desktopId={held['desktop']['desktopId']}&ownerVersion={held['ownerVersion']}"
            )
            assert (
                image.status_code == 200
                and image.content[:8] == b"\x89PNG\r\n\x1a\n"
                and struct.unpack(">II", image.content[16:24]) == (1024, 768)
            )
            await send("/api/take-control", binding(held))
            human = await state_until(lambda run: run["owner"] in ("human", "stopped"))
            assert human["owner"] == "human", human
            await send("/api/approval", old, 409)
            await send("/api/input", {**binding(held), "action": "click", "x": 700, "y": 180}, 409)
            # The operator can inspect while holding the exact same native guest.
            await send("/api/input", {**binding(human), "action": "click", "x": 700, "y": 180})
            current = await state_until(lambda run: run["owner"] == "human" and not run["humanInputBusy"])
            await send("/api/return-control", binding(current))
            offered = await state_until(lambda run: run["approval"] or run["owner"] == "stopped")
            assert offered["approval"] and offered["approval"]["id"] != old["approvalId"], offered
            await send("/api/approval", old, 409)
            await send("/api/approval", {**binding(offered), "approvalId": offered["approval"]["id"], "approved": True})
            final = await state_until(lambda run: run["owner"] == "stopped" and not run["closing"])
            assert final["result"] == "verified", final
            assert final["fixture"]["results"] == {"browser_matches": True, "file_matches": True}
            assert final["fixture"]["revision"] == 1 and final["requests"] == 3, final
            exported = await receipt(client, final)
            assert exported["cleanup"] == "completed" and exported["file"] is None
            assert [event["outcome"] for event in exported["events"] if event["kind"] == "approval"] == [
                "offered",
                "cancelled",
                "offered",
                "approved",
            ]
            tools = [event for event in exported["events"] if event["kind"] == "tools"]
            assert {event["phaseIndex"] for event in tools} == {1, 2}
            assert tools[-1]["phase"] == "final" and tools[-1]["attempted"] == tools[-1]["returned"] == 1
            assert all(
                private not in json.dumps(exported)
                for private in ("synthetic-desktop-wire-key", "fixture-desktop", "D-2201", "result.txt")
            )
            assert list((runtime_dir / "runs").iterdir()) == [], "Owned guest was not reaped"
            print(
                "PASS native Fieldwork Desktop: actual Python SDK/Responses, live PNG while approval holds lease, Take, stale control, human native click, Return fresh approval, exact guest proof, cleanup"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    asyncio.run(main(parser.parse_args().runtime_dir))
