"""Fieldwork Host/Guest native run with a controlled Responses transport."""

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
from mixed_workspace import MixedWorkspace
from playwright.async_api import Route


class ControlledMixed(httpx.AsyncBaseTransport):
    def __init__(self, receipt_handoff: bool = False) -> None:
        self.calls = 0
        self.receipt_handoff = receipt_handoff

    @override
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url.path.endswith("/responses") and body["store"] is False
        names = {tool.get("name") for tool in body["tools"]}
        assert {"browser_read_page", "browser_click", "approved_receipt"} <= names, names
        assert any(tool["type"] == "computer" for tool in body["tools"])
        self.calls += 1
        turn = self.calls
        output: list[JSONMap]
        if turn in (1, 2):
            instruction = body["input"][0]["content"][0]["text"]
            read = json.loads(instruction.split("Current Host browser: ", 1)[1])
            route = next(item for item in read["elements"] if item["label"] == "Route D-2201")
            output = [
                {
                    "type": "function_call",
                    "id": f"fn_{turn}",
                    "call_id": f"call_{turn}",
                    "status": "completed",
                    "name": "browser_click",
                    "arguments": json.dumps({"tab_id": None, "target": route["ref"]}),
                }
            ]
        elif turn == 3 or (self.receipt_handoff and turn == 4):
            output = [
                {
                    "type": "function_call",
                    "id": "receipt",
                    "call_id": "receipt",
                    "status": "completed",
                    "name": "approved_receipt",
                    "arguments": json.dumps({"case_id": "D-2201"}),
                }
            ]
        elif turn == (5 if self.receipt_handoff else 4):
            output = [
                {
                    "type": "computer_call",
                    "id": "write",
                    "call_id": "write",
                    "status": "completed",
                    "actions": [
                        {"type": "click", "button": "left", "x": 700, "y": 180},
                        {"type": "keypress", "keys": ["CTRL", "A"]},
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
                "id": f"resp_{turn}",
                "object": "response",
                "model": "fixture-mixed",
                "status": "completed",
                "created_at": 0,
                "output": output,
            },
        )


def binding(run: JSONMap) -> JSONMap:
    return {"runId": run["id"], **run["desktop"]}


async def main(runtime_dir: Path, receipt_handoff: bool = False) -> None:
    transport = ControlledMixed(receipt_handoff)
    async with serve(0, "synthetic-mixed-wire-key", {"responses": "fixture-mixed"}, transport, runtime_dir) as app:
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
            assert config["mixedAvailable"]
            assert (await client.get("/result")).status_code == 403
            await send("/api/start", {"environment": "mixed", "taskId": "mixed", "api": "responses", "mode": "live"})
            held = await state_until(lambda run: run["approval"] or run["owner"] == "stopped")
            assert held["approval"], held
            active = app.current
            assert active and active.context and active.task_page and isinstance(active.workspace, MixedWorkspace)
            workspace = active.workspace
            cookies = await active.context.cookies(f"{app.origin}/route")
            cookie = next(value for value in cookies if value.get("name") == "fieldwork_workspace")
            assert cookie.get("httpOnly") and cookie.get("sameSite") == "Strict"
            assert active.workspace_token not in await active.task_page.evaluate("document.cookie")
            assert active.workspace_token not in await active.task_page.content()
            assert active.workspace_token not in json.dumps(held)
            route_denials: list[int] = []

            async def hold_route(route: Route) -> None:
                assert workspace.checked_route and workspace.routes == 0
                for supplied in ("", "fieldwork_workspace=previous-run"):
                    denied = await client.post(
                        "/route",
                        headers={"Origin": app.origin, "Cookie": supplied},
                        json={"case_id": "D-2201", "action": "route"},
                    )
                    route_denials.append(denied.status_code)
                    assert denied.status_code == 403 and workspace.routes == 0
                await route.fallback()

            await active.task_page.route(f"{app.origin}/route", hold_route)
            old = {**binding(held), "approvalId": held["approval"]["id"], "approved": True}
            spoof = await client.post(
                "/route", headers={"Origin": app.origin}, json={"case_id": "D-2201", "action": "route"}
            )
            assert spoof.status_code == 403 and (await client.get("/result")).status_code == 403
            await send("/api/take-control", binding(held))
            human = await state_until(
                lambda run: run["owner"] == "stopped" or (run["owner"] == "human" and not run["humanInputBusy"])
            )
            assert human["owner"] == "human", human
            await send("/api/approval", old, 409)
            await send("/api/input", {**binding(human), "action": "click", "x": 1, "y": 1}, 400)
            after_miss = await state_until(lambda run: not run["humanInputBusy"])
            assert after_miss["owner"] == "human" and not after_miss["uncertainEffects"], after_miss
            await send("/api/mixed-view", {**binding(after_miss), "selected": "guest"})
            guest = await state_until(lambda run: run["desktop"] and run["desktop"]["view"] == "guest")
            await send("/api/input", {**binding(human), "action": "click", "x": 700, "y": 180}, 409)
            await send("/api/input", {**binding(guest), "action": "click", "x": 200, "y": 215}, 400)
            await send("/api/input", {**binding(guest), "action": "type", "text": "arbitrary"}, 400)
            point = guest["desktop"]
            image = await client.get(
                f"/api/view?run={guest['id']}&desktopId={point['desktopId']}&ownerVersion={point['ownerVersion']}&view=guest&tabId={point['tabId']}&sequence={point['sequence']}"
            )
            assert (
                image.status_code == 200
                and image.content[:8] == b"\x89PNG\r\n\x1a\n"
                and struct.unpack(">II", image.content[16:24]) == (1024, 768)
            )
            await send("/api/return-control", binding(guest))
            labels: list[str] = []
            receipt_interrupted = False
            while True:
                run = await state_until(lambda state: state["approval"] or state["owner"] == "stopped")
                if run["owner"] == "stopped":
                    break
                approval = run["approval"]
                labels.append(approval["label"])
                if receipt_handoff and not receipt_interrupted and approval["label"].startswith("Fetch the one"):
                    assert (await client.get("/result")).status_code == 403
                    assert (await client.get("/result/guessed")).status_code == 403
                    await send("/api/take-control", binding(run))
                    taken = await state_until(
                        lambda state: (
                            state["owner"] == "stopped" or (state["owner"] == "human" and not state["humanInputBusy"])
                        )
                    )
                    assert taken["owner"] == "human" and not taken["uncertainEffects"], taken
                    await send("/api/return-control", binding(taken))
                    receipt_interrupted = True
                    continue
                await send("/api/approval", old, 409)
                await send("/api/approval", {**binding(run), "approvalId": approval["id"], "approved": True})
            final = await state_until(lambda state: state["owner"] == "stopped" and not state["closing"])
            assert final["result"] == "verified" and final["fixture"]["results"] == {
                "host_routes": 1,
                "receipts": 1,
                "disclosed": True,
                "guest_browser_effects": 0,
                "file_matches": True,
            }, final
            assert receipt_interrupted == receipt_handoff
            assert route_denials == [403, 403]
            assert len(labels) == (4 if receipt_handoff else 3) and transport.calls == (6 if receipt_handoff else 5), (
                labels,
                final,
            )
            exported = await receipt(client, final)
            assert active.workspace_token not in json.dumps(exported)
            assert exported["cleanup"] == "completed" and exported["file"]["cleanup"] == "completed"
            assert exported["file"]["direction"] == "download"
            assert exported["file"]["current"] == {"status": "completed", "effect": "completed"}
            expected_approvals = [
                "offered",
                "cancelled",
                "offered",
                "approved",
                "offered",
                "approved",
                "offered",
                "approved",
            ]
            if receipt_handoff:
                expected_approvals[4:4] = ["offered", "cancelled"]
            assert [
                event["outcome"] for event in exported["events"] if event["kind"] == "approval"
            ] == expected_approvals
            tools = [event for event in exported["events"] if event["kind"] == "tools"]
            assert {event["phaseIndex"] for event in tools} == ({1, 2, 3} if receipt_handoff else {1, 2})
            assert tools[-1]["phase"] == "final" and tools[-1]["attempted"] == tools[-1]["returned"] == (
                2 if receipt_handoff else 3
            )
            assert all(
                private not in json.dumps(exported)
                for private in ("synthetic-mixed-wire-key", "fixture-mixed", "D-2201", "result.txt")
            )
            assert list((runtime_dir / "runs").iterdir()) == [], "Owned guest was not reaped"
            print(
                "PASS native mixed: same run, separate Host/Guest, blocked spoof, Take, stale view, guest browser protected, bounded data entry, return, one receipt and literal native proof, cleanup"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--receipt-handoff", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(args.runtime_dir, args.receipt_handoff))
