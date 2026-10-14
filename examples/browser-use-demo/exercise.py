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
        app.api_key = "test-only"
        for api in ("responses", "decisions"):
            app.models = {api: "test-only"}
            available = (await client.get("/api/state")).json()["liveAvailable"]
            assert available == {name: name == api for name in ("responses", "decisions")}

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
        assert done["fixture"]["results"] == {
            "confirmation": "TABLE-204",
            "fields": {"Guest name": "Ada", "Party size": "2", "Time": "18:00", "Seating": "Indoor"},
        }, done
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
        await post("/api/start", {"taskId": "reservation", "api": "decisions", "mode": "rehearsal"})
        offered = await until(lambda s: s["approval"] is not None)
        current = app.current
        assert current is not None
        original_capture = current.capture
        entered, release = asyncio.Event(), asyncio.Event()

        async def hold_verified(*, cancelled: Callable[[], bool] | None = None) -> None:
            if not entered.is_set() and current.owner == "agent" and current.result == "verified":
                entered.set()
                await asyncio.wait_for(release.wait(), timeout=5)
            await original_capture(cancelled=cancelled)

        current.capture = hold_verified
        try:
            await post("/api/approval", {**binding(offered), "approvalId": offered["approval"]["id"], "approved": True})
            await asyncio.wait_for(entered.wait(), timeout=5)
            verified = await state()
            assert verified["result"] == "verified" and verified["owner"] == "agent"
            await post("/api/take-control", binding(verified))
            release.set()
            human = await until(lambda s: s["owner"] == "human" and not s["humanInputBusy"])
            assert current.task_page is not None
            bounds = await current.task_page.get_by_label("Guest name").bounding_box()
            assert bounds is not None
            await post(
                "/api/input",
                {
                    **binding(human),
                    "action": "click",
                    "x": bounds["x"] + bounds["width"] / 2,
                    "y": bounds["y"] + bounds["height"] / 2,
                },
            )
            human = await state()
            await post("/api/input", {**binding(human), "action": "type", "text": " changed"})
            human = await state()
            assert human["fixture"]["verified"] is False, human["fixture"]
            await post("/api/stop", {"runId": human["id"]})
            stopped = await until(lambda s: s["owner"] == "stopped" and not s["closing"])
            assert stopped["result"] == "unverified", "The old agent result survived human editing and Stop"
        finally:
            release.set()
            current.capture = original_capture
        await post("/api/start", {"taskId": "reservation", "api": "decisions", "mode": "rehearsal"})
        offered = await until(lambda s: s["approval"] is not None)
        await post("/api/take-control", binding(offered))
        await until(lambda s: s["owner"] == "human" and not s["humanInputBusy"])
        submitted_run = app.current
        assert submitted_run is not None and submitted_run.task_page is not None
        await submitted_run.task_page.get_by_label("Guest name").fill("Grace")
        await submitted_run.task_page.get_by_role("button", name="Reserve table").click()
        await submitted_run.task_page.get_by_label("Guest name").fill("Ada")
        receipt = await submitted_run.inspect()
        assert receipt["verified"] is False, "Editing a confirmed form cannot change the submitted booking"
        assert receipt["results"]["fields"]["Guest name"] == "Grace"
        await post("/api/stop", {"runId": submitted_run.id})
        stopped = await until(lambda s: s["owner"] == "stopped" and not s["closing"])
        assert stopped["result"] == "unverified"
        print("PASS booking: auth, approval, fresh handoff, pixels, independent result, Stop.")


if __name__ == "__main__":
    asyncio.run(run())
