"""Run the booking page, approval, handoff and authentication against loopback."""

from __future__ import annotations

import json
import time
import asyncio
from typing import Any
from unittest.mock import patch
from collections.abc import Callable
from typing_extensions import override

import httpx2 as httpx
from server import Fieldwork, serve
from playwright.async_api import Locator, ElementHandle


def binding(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "runId": state["id"],
        "ownerVersion": state["ownerVersion"],
        "tabId": state["browser"]["tabId"],
        "sequence": state["browser"]["sequence"],
    }


async def check_live_case(
    app: Fieldwork,
    post: Callable[[str, dict[str, Any]], Any],
    until: Callable[[Callable[[dict[str, Any]], bool]], Any],
    api: str,
    outcome: str,
) -> None:
    app.models = {api: f"local-{api}"}
    entered, cancelled = asyncio.Event(), asyncio.Event()
    requests: list[httpx.Request] = []

    class PendingBody(httpx.AsyncByteStream):
        @override
        async def __aiter__(self):
            try:
                entered.set()
                yield b"event: response.created\ndata: " if api == "responses" else b'{"id":'
                await asyncio.Event().wait()
            finally:
                cancelled.set()

    async def forward(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if outcome == "cancelled":
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream" if api == "responses" else "application/json"},
                stream=PendingBody(),
            )
        entered.set()
        return httpx.Response(
            401,
            headers={"x-request-id": "sk-local-marker"},
            json={"error": {"message": "sk-local-marker test-only", "type": "authentication_error"}},
        )

    app.transport = httpx.MockTransport(forward)
    try:
        started = await post("/api/start", {"taskId": "reservation", "api": api, "mode": "live"})
        observed = await until(lambda s: entered.is_set() or (s["owner"] == "stopped" and not s["closing"]))
        assert entered.is_set(), (api, outcome, observed)
        assert len(requests) == 1
        request = requests[0]
        body = json.loads(request.content)
        assert request.method == "POST" and request.url.path == f"/v1/{api}"
        assert request.headers["authorization"] == "Bearer test-only"
        assert body["model"] == f"local-{api}" and body["input"]
        if api == "responses":
            assert body["stream"] is True and body["tools"]
        else:
            assert body["questions"]
        if outcome == "cancelled":
            await post("/api/stop", {"runId": started["id"]})
            await asyncio.wait_for(cancelled.wait(), timeout=5)
        stopped = await until(lambda s: s["owner"] == "stopped" and not s["closing"])
        assert len(requests) == stopped["requests"] == 1
        assert stopped["result"] == "unverified" and stopped["fixture"]["results"] == {}
        assert not stopped["uncertainEffects"] and "sk-local-marker" not in json.dumps(stopped)
        if outcome == "denied":
            assert stopped["status"] == "failed" and stopped["apiFailure"]["status"] == 401
            assert "test-only" not in json.dumps(stopped["apiFailure"])
        else:
            assert stopped["status"] == "stopped" and stopped["apiFailure"] is None
    finally:
        await app.transport.aclose()
        app.transport = None


async def check_state_during_live_close(
    app: Fieldwork, client: httpx.AsyncClient, post: Callable[[str, dict[str, Any]], Any]
) -> None:
    sent, reply = asyncio.Event(), asyncio.Event()
    entered, finish = asyncio.Event(), asyncio.Event()
    app.models = {"responses": "local-responses"}

    async def forward(_request: httpx.Request) -> httpx.Response:
        sent.set()
        await reply.wait()
        return httpx.Response(401, json={"error": {"message": "local refusal", "type": "authentication_error"}})

    real_evaluate = Locator.evaluate

    async def delayed(locator: Locator, expression: str, *args: Any, **kwargs: Any) -> Any:
        result = await real_evaluate(locator, expression, *args, **kwargs)
        if expression == "body => Number(body.dataset.revision)" and not entered.is_set():
            entered.set()
            await asyncio.wait_for(finish.wait(), 8)
        return result

    app.transport = httpx.MockTransport(forward)
    try:
        await post("/api/start", {"taskId": "reservation", "api": "responses", "mode": "live"})
        await asyncio.wait_for(sent.wait(), 10)
        with patch.object(Locator, "evaluate", delayed):
            snapshot = asyncio.create_task(client.get("/api/state"))
            await asyncio.wait_for(entered.wait(), 5)
            reply.set()
            current = app.current
            assert current and current.agent
            await asyncio.wait_for(asyncio.shield(current.agent), 5)
            assert current.owner == "stopped" and current.cleanup
            await asyncio.wait_for(asyncio.shield(current.cleanup), 5)
            finish.set()
            response = await asyncio.wait_for(snapshot, 5)
            response.raise_for_status()
            state = response.json()["run"]
            assert state["owner"] == "stopped" and state["browser"] is None
            assert state["view"]["status"] == "closed" and state["result"] == "unverified"
    finally:
        reply.set()
        finish.set()
        await app.transport.aclose()
        app.transport = None
    print("PASS final live error during a dashboard state read: no stale binding or HTTP 400.")


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

        for api in ("responses", "decisions"):
            for outcome in ("denied", "cancelled"):
                await check_live_case(app, post, until, api, outcome)
        print("PASS live Responses/Decisions: forwarding, safe denial and cancelled open body.")
        await check_state_during_live_close(app, client, post)
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
        current = app.current
        assert current is not None and current.task_page is not None
        revision = await current.task_page.locator("body").get_attribute("data-revision")
        previous = binding(human)
        await post("/api/input", {**binding(human), "action": "key", "key": "Tab"})
        assert await current.task_page.locator("body").get_attribute("data-revision") == revision
        assert (await client.post("/api/input", json={**previous, "action": "key", "key": "Tab"})).status_code == 409, (
            "Focus changed even though the form revision did not"
        )
        human = await state()
        assert binding(human)["sequence"] > previous["sequence"]
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
        previous = await until(lambda s: s["owner"] == "human" and not s["humanInputBusy"])
        submitted_run = app.current
        assert submitted_run is not None and submitted_run.task_page is not None
        await submitted_run.task_page.get_by_label("Guest name").fill("Grace")
        stale = await client.post("/api/input", json={**binding(previous), "action": "type", "text": " stale"})
        assert stale.status_code == 409, "An old screenshot admitted input after the fixture changed"
        assert await submitted_run.task_page.get_by_label("Guest name").input_value() == "Grace"
        fresh = await state()
        assert binding(fresh)["sequence"] > binding(previous)["sequence"]
        await submitted_run.task_page.get_by_role("button", name="Reserve table").click()
        await submitted_run.task_page.get_by_label("Guest name").fill("Ada")
        receipt = await submitted_run.inspect()
        assert receipt["verified"] is False, "Editing a confirmed form cannot change the submitted booking"
        assert receipt["results"]["fields"]["Guest name"] == "Grace"
        await post("/api/stop", {"runId": submitted_run.id})
        stopped = await until(lambda s: s["owner"] == "stopped" and not s["closing"])
        assert stopped["result"] == "unverified"
        input_entered, input_release = asyncio.Event(), asyncio.Event()
        original_fill = ElementHandle.fill

        async def held_fill(element: ElementHandle, value: str, **kwargs: Any) -> None:
            await original_fill(element, value, **kwargs)
            if not input_entered.is_set():
                input_entered.set()
                await asyncio.wait_for(input_release.wait(), timeout=5)

        with patch.object(ElementHandle, "fill", held_fill):
            try:
                await post("/api/start", {"taskId": "reservation", "api": "decisions", "mode": "rehearsal"})
                await asyncio.wait_for(input_entered.wait(), timeout=5)
                before_input = await state()
                assert before_input["owner"] == "agent"
                await post("/api/take-control", binding(before_input))
                input_release.set()
                handoff = await until(lambda s: s["owner"] == "human" or (s["owner"] == "stopped" and not s["closing"]))
                assert handoff["owner"] == "stopped", "An uncertain action must not be handed to the human"
                assert handoff["status"] == "handoff_unavailable"
                assert handoff["uncertainEffects"] is True
            finally:
                input_release.set()
        print("PASS booking: auth, approval, fresh handoff, pixels, independent result, Stop.")


if __name__ == "__main__":
    asyncio.run(run())
