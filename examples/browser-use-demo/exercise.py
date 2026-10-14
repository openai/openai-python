"""Run the booking page, approval, handoff and authentication against loopback."""

from __future__ import annotations

import time
import asyncio
from typing import Any
from collections.abc import Callable

import httpx2 as httpx
from server import serve


def binding(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "runId": state["id"],
        "ownerVersion": state["ownerVersion"],
        "tabId": state["browser"]["tabId"],
        "sequence": state["browser"]["sequence"],
    }


async def run() -> None:
    async with serve() as app, httpx.AsyncClient(base_url=app.origin, trust_env=False) as client:
        assert (await client.get("/api/state")).status_code == 403
        assert (
            await client.get("/api/state", headers={"Origin": "https://example.org", "X-Demo-Token": app.token})
        ).status_code == 403
        client.headers["X-Demo-Token"] = app.token

        async def state() -> dict[str, Any]:
            result = await client.get("/api/state")
            result.raise_for_status()
            return result.json()["run"]

        async def post(path: str, body: dict[str, Any]) -> dict[str, Any]:
            result = await client.post(path, json=body)
            result.raise_for_status()
            return result.json()

        async def until(predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                current = await state()
                if predicate(current):
                    return current
                if current["owner"] == "stopped" and not current["closing"]:
                    raise AssertionError(current)
                await asyncio.sleep(0.03)
            raise TimeoutError("Booking exercise timed out.")

        await post("/api/start", {"taskId": "reservation", "api": "decisions", "mode": "rehearsal"})
        offered = await until(lambda s: s["approval"] is not None)
        assert offered["requests"] == 0 and offered["result"] != "verified"
        await post("/api/take-control", binding(offered))
        human = await until(lambda s: s["owner"] == "human" and not s["humanInputBusy"])
        assert not human["approval"] and human["fixture"]["results"] == {}
        assert (
            await client.post(
                "/api/approval", json={**binding(offered), "approvalId": offered["approval"]["id"], "approved": True}
            )
        ).status_code == 409
        assert (
            await client.post("/api/input", json={**binding(offered), "action": "key", "key": "Tab"})
        ).status_code == 409
        frame = await client.get(
            "/api/screenshot",
            params={
                "run": human["id"],
                "tabId": human["screenshotBinding"]["tabId"],
                "sequence": human["screenshotBinding"]["sequence"],
            },
        )
        assert frame.status_code == 200 and frame.content[:2] == b"\xff\xd8"
        await post("/api/input", {**binding(human), "action": "key", "key": "Tab"})
        human = await state()
        await post("/api/return-control", binding(human))
        offered = await until(lambda s: s["approval"] is not None)
        await post("/api/approval", {**binding(offered), "approvalId": offered["approval"]["id"], "approved": True})
        done = await until(lambda s: s["owner"] == "stopped" and not s["closing"])
        assert done["result"] == "verified" and done["requests"] == 0, done
        assert done["fixture"]["results"] == {"confirmation": "TABLE-204"}, done
        assert all(
            done["fixture"]["fields"].get(k) == v
            for k, v in {"Guest name": "Ada", "Party size": "2", "Time": "18:00", "Seating": "Indoor"}.items()
        )
        await post("/api/start", {"taskId": "reservation", "api": "decisions", "mode": "rehearsal"})
        offered = await until(lambda s: s["approval"] is not None)
        await post("/api/stop", {"runId": offered["id"]})
        stopped = await until(lambda s: s["owner"] == "stopped" and not s["closing"])
        assert stopped["result"] == "unverified" and stopped["fixture"]["results"] == {}
        assert (
            await client.post("/api/input", json={**binding(offered), "action": "key", "key": "Enter"})
        ).status_code == 409
        print("PASS booking: auth, approval, fresh handoff, pixels, independent result, Stop.")


if __name__ == "__main__":
    asyncio.run(run())
