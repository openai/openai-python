"""Exercise the Python Fieldwork controls with the real SDK and local Chromium."""

import json
import asyncio
from typing import Any, TypeAlias
from urllib.parse import urlencode
from unittest.mock import patch
from collections.abc import Mapping, Callable

import httpx2 as httpx
from server import Run, serve

# Objects decoded from the local HTTP JSON boundary, matching Fieldwork.snapshot and export.
JSONMap: TypeAlias = dict[str, Any]


def binding(run: JSONMap) -> JSONMap:
    point = run["browser"] or {"tabId": None, "sequence": None}
    return {
        "runId": run["id"],
        "ownerVersion": run["ownerVersion"],
        "tabId": point["tabId"],
        "sequence": point["sequence"],
    }


async def receipt(client: httpx.AsyncClient, run: JSONMap) -> JSONMap:
    response = await client.get("/api/export", params={"run": run["id"]})
    assert response.status_code == 200, response.text
    result = response.json()
    assert set(result) == {
        "version",
        "id",
        "environment",
        "taskId",
        "api",
        "mode",
        "status",
        "owner",
        "result",
        "uncertainEffects",
        "cleanup",
        "requests",
        "turns",
        "stepLimit",
        "elapsedMs",
        "requestHeadersMs",
        "diagnostics",
        "droppedEvents",
        "events",
        "file",
    }, result
    allowed = {
        "request": {"kind", "atMs", "attempt", "phase", "status", "headersMs", "durationMs"},
        "approval": {"kind", "atMs", "outcome"},
        "control": {"kind", "atMs", "owner"},
        "cleanup": {"kind", "atMs", "outcome"},
        "tools": {"kind", "atMs", "phaseIndex", "phase", "attempted", "returned"},
    }
    assert all(set(event) == allowed[event["kind"]] for event in result["events"])
    assert result["id"] == run["id"] and result["elapsedMs"] >= 0
    assert len(result["events"]) <= 256
    # These actual page fields, labels and SDK wire values never enter exported events.
    raw = json.dumps(result)
    for private in (
        "Ada",
        "Inspect drifting sensor",
        "Sensor specialist",
        "INTAKE-501",
        "synthetic-key-for-local-wire",
        "synthetic-wire-model",
        "Done",
        "data:image/",
    ):
        assert private not in raw, private
    return result


async def run_exercise() -> None:
    expected = {
        "support": [
            {"id": "T-1042", "choice": "Billing"},
            {"id": "T-1043", "choice": "Technical"},
            {"id": "T-1044", "choice": "Account"},
        ],
        "reservation": {"confirmation": "TABLE-204"},
        "invoices": [
            {"id": "INV-204", "choice": "Approve"},
            {"id": "INV-205", "choice": "Flag amount mismatch"},
            {"id": "INV-202", "choice": "Flag duplicate"},
        ],
        "stock": [
            {"operation": "ship", "order": "ORDER-301", "sku": "ALT-B"},
            {"operation": "ship", "order": "ORDER-302", "sku": "ALT-R"},
        ],
        "service": [
            {
                "operation": "schedule",
                "job": "SERVICE-401",
                "date": "2026-11-12",
                "technician": "Sensor specialist",
                "note": "Inspect drifting sensor",
            }
        ],
        "files": [{"operation": "attach", "job": "INTAKE-501"}],
    }
    async with serve(0) as app, httpx.AsyncClient(base_url=app.origin, timeout=20) as client:
        home = await client.get("/")
        assert home.status_code == 200
        assert app.token not in home.text
        assert app.token not in (await client.get("/traces")).text
        assert (await client.get("/api/state")).status_code == 403
        client.headers["X-Demo-Token"] = app.token

        async def send(path: str, body: Mapping[str, object], code: int = 200) -> JSONMap:
            answer = await client.post(path, json=body)
            assert answer.status_code == code, (path, answer.status_code, answer.text)
            return answer.json()

        async def wait_for(predicate: Callable[[JSONMap], object]) -> JSONMap:
            run: JSONMap = {}
            for _ in range(300):
                answer = await client.get("/api/state")
                assert answer.status_code == 200, answer.text
                run = answer.json()["run"]
                if predicate(run):
                    return run
                await asyncio.sleep(0.05)
            raise AssertionError(f"State did not settle: {run}")

        assert (await client.get("/tasks.json")).status_code == 404
        assert (await client.get("/../browser-use-demo/tasks.json")).status_code == 404
        dashboard = await client.get("/fixture/invoices")
        assert '"expected"' not in dashboard.text
        bad_host = await client.get("/api/state", headers={"Host": "localhost:1234"})
        assert bad_host.status_code == 403
        no_token = await client.get("/api/state", headers={"X-Demo-Token": "incorrect"})
        assert no_token.status_code == 403

        previous_workspace_cookie = "fieldwork_workspace=previous-unadmitted-run"
        for task in ("support", "reservation", "invoices", "stock", "service", "files"):
            if task == "files":
                await send(
                    "/api/start",
                    {"environment": "browser", "taskId": task, "api": "decisions", "mode": "rehearsal"},
                    400,
                )
            await send(
                "/api/start",
                {
                    "environment": "browser",
                    "taskId": task,
                    "api": "decisions",
                    "mode": "rehearsal",
                    "allowFileUpload": task == "files",
                },
            )
            workspace_checked = False
            workspace_token = None
            route_denials: list[int] = []
            while True:
                current = await wait_for(lambda run: run["approval"] is not None or run["owner"] == "stopped")
                if current["owner"] == "stopped":
                    break
                approval = current["approval"]
                if task in ("stock", "service", "files"):
                    if not workspace_checked:
                        workspace_checked = True
                        # The dashboard credential and a prior run cannot read the workspace.
                        for suffix in ("", "/notes/brief", "/notes/rules"):
                            path = f"/fixture/{task}{suffix}"
                            assert (await client.get(path)).status_code == 403
                            assert (
                                await client.get(path, headers={"Cookie": previous_workspace_cookie})
                            ).status_code == 403
                        active = app.current
                        assert active and active.context and active.task_page
                        workspace_token = active.workspace_token
                        cookies = await active.context.cookies(f"{app.origin}/fixture/{task}")
                        own = next(cookie for cookie in cookies if cookie.get("name") == "fieldwork_workspace")
                        assert own.get("httpOnly") is True and own.get("sameSite") == "Strict"
                        assert workspace_token not in await active.task_page.evaluate("document.cookie")
                        assert workspace_token not in await active.task_page.content()
                        assert workspace_token not in json.dumps(current)

                        async def hold_effect(
                            route: Any,
                            effect: Any,
                            *,
                            stale: str = previous_workspace_cookie,
                            denials: list[int] = route_denials,
                        ) -> None:
                            # The model's click has an active permit by this point. A peer
                            # replay must fail before it can consume that same permit.
                            try:
                                for cookie in ("", stale):
                                    denied = await client.post(
                                        effect.url,
                                        content=effect.post_data_buffer,
                                        headers={
                                            "Origin": app.origin,
                                            "Content-Type": effect.headers.get("content-type", ""),
                                            "Cookie": cookie,
                                        },
                                    )
                                    denials.append(denied.status_code)
                            finally:
                                await route.fallback()

                        await active.task_page.route(f"{app.origin}/fixture/{task}/effect*", hold_effect)
                    spoof = await client.post(
                        f"/fixture/{task}/effect?run={current['id']}" + ("&case=INTAKE-501" if task == "files" else ""),
                        headers={"Origin": app.origin},
                        json={"operation": "ship", "order": "ORDER-301", "sku": "ALT-B"},
                    )
                    assert spoof.status_code == 403, spoof.text
                if task == "files":
                    await send("/api/take-control", binding(current), 403)
                old = {**binding(current), "approvalId": "wrong", "approved": True}
                await send("/api/approval", old, 409)
                await send("/api/approval", {**binding(current), "approvalId": approval["id"], "approved": True})
            current = await wait_for(lambda run: not run["closing"])
            assert current["result"] == "verified", current
            assert current["fixture"]["results"] == expected[task], current["fixture"]
            if task == "reservation":
                assert current["fixture"]["fields"] == {
                    "Guest name": "Ada",
                    "Party size": "2",
                    "Time": "18:00",
                    "Seating": "Indoor",
                }
            if task == "stock":
                assert current["fixture"]["stock"] == [{"sku": "ALT-B", "quantity": 1}, {"sku": "ALT-R", "quantity": 1}]
            if task == "files":
                assert current["fixture"]["file"]["cleanup"] == "completed", current
            exported = await receipt(client, current)
            if workspace_token:
                assert route_denials and all(code == 403 for code in route_denials), route_denials
                assert workspace_token not in json.dumps(exported)
                previous_workspace_cookie = f"fieldwork_workspace={workspace_token}"
            assert exported["status"] == "complete" and exported["cleanup"] == "completed"
            assert exported["requestHeadersMs"] == 0 and exported["requests"] == 0
            assert [event["outcome"] for event in exported["events"] if event["kind"] == "cleanup"] == [
                "pending",
                "completed",
            ]
            approvals = [event["outcome"] for event in exported["events"] if event["kind"] == "approval"]
            assert approvals == ["offered", "approved"] * (2 if task == "stock" else 0 if task == "support" else 1)
            if task == "files":
                assert exported["file"]["cleanup"] == "completed"
                assert exported["file"]["current"] == {"status": "completed", "effect": "completed"}
            else:
                assert exported["file"] is None
            assert current["requests"] == 0 and current["turns"] > 0, current
            checkpoint = current["history"]["checkpoints"][-1]
            image = await client.get(
                "/api/checkpoint?" + urlencode({"run": current["id"], "checkpoint": checkpoint["sequence"]})
            )
            assert image.status_code == 200 and image.content[:2] == b"\xff\xd8"
            print(f"PASS Python SDK rehearsal {task} verified, {current['turns']} turns")

        await send(
            "/api/start", {"environment": "browser", "taskId": "invoices", "api": "decisions", "mode": "rehearsal"}
        )
        held = await wait_for(lambda run: run["approval"] is not None)
        old = {**binding(held), "approvalId": held["approval"]["id"], "approved": True}
        await send("/api/take-control", binding(held))
        human = await wait_for(lambda run: run["owner"] in ("human", "stopped"))
        assert human["owner"] == "human", human
        paused = await receipt(client, human)
        assert paused["status"] == "paused" and paused["owner"] == "human", paused
        await send("/api/approval", old, 409)
        await send("/api/input", {**binding(held), "action": "open_notes"}, 409)
        await send("/api/input", {**binding(human), "action": "open_notes"})
        notes = await wait_for(lambda run: run["browser"] and run["browser"]["role"] == "Notes")
        await send("/api/return-control", binding(notes))
        offered = await wait_for(lambda run: run["approval"] or run["owner"] == "stopped")
        assert offered["approval"], offered
        assert offered["approval"]["id"] != old["approvalId"]
        await send("/api/approval", old, 409)
        await send("/api/stop", {"runId": offered["id"]})
        stopped = await wait_for(lambda run: run["owner"] == "stopped" and not run["closing"])
        assert stopped["result"] == "unverified"
        exported = await receipt(client, stopped)
        assert [event["outcome"] for event in exported["events"] if event["kind"] == "approval"] == [
            "offered",
            "cancelled",
            "offered",
            "cancelled",
        ]
        assert [event["owner"] for event in exported["events"] if event["kind"] == "control"] == [
            "draining-to-human",
            "human",
            "draining-to-agent",
            "agent",
            "stopped",
        ]
        await send(
            "/api/approval", {**binding(offered), "approvalId": offered["approval"]["id"], "approved": True}, 409
        )
        print("PASS Python takeover, Notes, fresh approval, Stop, stale inputs refused")

        await send(
            "/api/start", {"environment": "browser", "taskId": "invoices", "api": "decisions", "mode": "rehearsal"}
        )
        held = await wait_for(lambda value: value["approval"] is not None)
        await send("/api/take-control", binding(held))
        human = await wait_for(lambda value: value["owner"] in ("human", "stopped"))
        assert human["owner"] == "human", human
        run = app.current
        assert run is not None

        async def fail_after_human_input(*, cancelled: Callable[[], bool] | None = None) -> None:
            del cancelled
            raise RuntimeError("Controlled capture failure after browser input")

        run.capture = fail_after_human_input
        await send("/api/input", {**binding(human), "action": "open_notes"}, 409)
        stopped = await wait_for(lambda value: value["owner"] == "stopped" and not value["closing"])
        assert stopped["status"] == "uncertain" and stopped["uncertainEffects"], stopped
        assert run.human is not None and run.human.done() and run.human.exception() is not None
        await send("/api/return-control", binding(human), 409)
        exported = await receipt(client, stopped)
        assert exported["cleanup"] == "completed" and exported["result"] == "unverified"
        print("PASS failed human input capture cannot return control or discard its task")

        await send(
            "/api/start", {"environment": "browser", "taskId": "reservation", "api": "decisions", "mode": "rehearsal"}
        )
        offered = await wait_for(lambda run: run["approval"] or run["owner"] == "stopped")
        assert offered["approval"], offered
        await send("/api/approval", {**binding(offered), "approvalId": offered["approval"]["id"], "approved": False})
        stopped = await wait_for(lambda run: run["owner"] == "stopped" and not run["closing"])
        assert stopped["status"] == "refused" and stopped["result"] == "unverified"
        exported = await receipt(client, stopped)
        assert exported["cleanup"] == "completed"
        assert [event["outcome"] for event in exported["events"] if event["kind"] == "approval"] == [
            "offered",
            "refused",
        ]
        print("PASS Python refusal revokes session")

        # Navigation can invalidate a captured Notes view before Take finishes.
        await send(
            "/api/start", {"environment": "browser", "taskId": "invoices", "api": "decisions", "mode": "rehearsal"}
        )
        await wait_for(lambda run: run["approval"] is not None)
        run = app.current
        assert run is not None and run.driver is not None
        await run.driver.new_tab({"url": run.notes_url + "brief"})
        run.notes_tab, notes_page = run.driver.page(None)
        original_capture = run.capture

        async def capture_then_navigate(*, cancelled: Callable[[], bool] | None = None) -> None:
            await original_capture(cancelled=cancelled)
            if run.owner == "human" and run.transfer is asyncio.current_task():
                current = (await client.get("/api/state")).json()["run"]
                await send("/api/input", {**binding(current), "action": "open_notes"}, 409)
                assert run.human is None
                await notes_page.reload()

        run.capture = capture_then_navigate
        notes = await wait_for(lambda value: value["browser"] and value["browser"]["role"] == "Notes")
        await send("/api/take-control", binding(notes))
        assert run.transfer is not None
        _, pending = await asyncio.wait({run.transfer}, timeout=8)
        assert not pending
        state = (await client.get("/api/state")).json()["run"]
        assert state["owner"] == "stopped" and state["status"] == "handoff_unavailable", state
        assert run.cleanup is not None
        _, pending = await asyncio.wait({run.cleanup}, timeout=5)
        assert not pending
        exported = await receipt(client, state)
        assert exported["cleanup"] == "completed"
        phases = [event.get("owner") for event in exported["events"] if event["kind"] == "control"]
        assert phases[-3:] == ["draining-to-human", "human", "stopped"]
        assert not any(event.get("text") == "Agent work drained. You control the browser." for event in state["events"])
        await send("/api/start", {"taskId": "support", "api": "decisions", "mode": "rehearsal"})
        replaced = await wait_for(lambda value: value["owner"] == "stopped" and not value["closing"])
        assert replaced["result"] == "verified"
        print("PASS Notes navigation after Take capture retires stale binding, cleans, and permits fresh Start")


async def cleanup_failure(*, complete: bool = False) -> None:
    seen = False
    try:
        async with serve(0) as app, httpx.AsyncClient(base_url=app.origin, timeout=10) as client:
            client.headers["X-Demo-Token"] = app.token
            response = await client.post(
                "/api/start",
                json={
                    "environment": "browser",
                    "taskId": "files",
                    "api": "decisions",
                    "mode": "rehearsal",
                    "allowFileUpload": True,
                },
            )
            assert response.status_code == 200, response.text
            run: JSONMap = {}
            for _ in range(100):
                run = (await client.get("/api/state")).json()["run"]
                if run["approval"]:
                    break
                await asyncio.sleep(0.05)
            assert run["approval"]
            assert app.current is not None and app.current.file_owner is not None and app.current.context is not None
            area = app.current.file_owner.area
            original_close = app.current.context.close

            async def failed_close(*, reason: str | None = None) -> None:
                await original_close(reason=reason)
                raise RuntimeError("injected close failure")

            app.current.context.close = failed_close
            if complete:
                assert (
                    await client.post(
                        "/api/approval", json={**binding(run), "approvalId": run["approval"]["id"], "approved": True}
                    )
                ).status_code == 200
            else:
                assert (await client.post("/api/stop", json={"runId": run["id"]})).status_code == 200
            exported: JSONMap = {}
            for _ in range(100):
                exported = await receipt(client, run)
                if exported["cleanup"] == "failed":
                    break
                await asyncio.sleep(0.05)
            assert exported["status"] == "cleanup_failed" and exported["cleanup"] == "failed", exported
            assert exported["result"] == ("verified" if complete else "unverified"), exported
            assert exported["file"]["cleanup"] == "completed" and not area.exists(), exported
            assert [event["outcome"] for event in exported["events"] if event["kind"] == "cleanup"] == [
                "pending",
                "failed",
            ]
            response = await client.post(
                "/api/start", json={"taskId": "support", "api": "decisions", "mode": "rehearsal"}
            )
            assert response.status_code == 409
            seen = True
    except RuntimeError as error:
        assert seen and str(error) == "Workspace cleanup did not finish.", error
    else:
        raise AssertionError("Server close hid the failed cleanup")
    print(f"PASS completed={complete}: cleanup reaps files, preserves checked result, and refuses replacement")


async def capture_failure() -> None:
    original = Run.capture
    for before in (True, False):
        checked: bool | None = None

        async def fail(run: Run, *, cancelled: Callable[[], bool] | None = None, early: bool = before) -> None:
            nonlocal checked
            if early or run.result == "verified":
                checked = run.result == "verified"
                raise RuntimeError("Controlled frame failure")
            await original(run, cancelled=cancelled)

        async with serve(0) as app, httpx.AsyncClient(base_url=app.origin, timeout=10) as client:
            client.headers["X-Demo-Token"] = app.token
            with patch.object(Run, "capture", fail):
                started = await client.post(
                    "/api/start", json={"taskId": "support", "api": "decisions", "mode": "rehearsal"}
                )
                assert started.status_code == 200, started.text
                exported: JSONMap = {}
                for _ in range(200):
                    current = (await client.get("/api/state")).json()["run"]
                    exported = await receipt(client, current)
                    if exported["owner"] == "stopped" and exported["cleanup"] == "completed":
                        break
                    await asyncio.sleep(0.025)
                assert exported["status"] == "failed", exported
                assert exported["result"] == ("unverified" if before else "verified"), exported
                assert checked is (not before)
        print(f"PASS before verification={before}: capture failure preserves the observed result")


if __name__ == "__main__":
    asyncio.run(run_exercise())
    asyncio.run(cleanup_failure())
    asyncio.run(cleanup_failure(complete=True))
    asyncio.run(capture_failure())
