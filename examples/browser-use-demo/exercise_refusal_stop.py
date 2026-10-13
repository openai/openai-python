"""Check refusal results and elapsed time with a finite local request."""

import asyncio

import httpx2 as httpx
from server import serve


async def check(stopped: bool) -> None:
    entered, release = asyncio.Event(), asyncio.Event()
    draining = asyncio.Event()
    requests = 0

    async def dispatch(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        assert request.url.path == "/v1/decisions"
        requests += 1
        entered.set()
        if stopped:
            try:
                await asyncio.wait_for(release.wait(), 5)
            except asyncio.CancelledError:
                # A custom transport can take time to release its active request.
                draining.set()
                await asyncio.wait_for(release.wait(), 5)
        return httpx.Response(
            200,
            json={
                "model": "local-fixture",
                "answers": [{"type": "refusal", "name": "next_action"}],
                "usage": {
                    "input_tokens": 1,
                    "output_tokens": 1,
                    "total_tokens": 2,
                    "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                    "output_tokens_details": {"reasoning_tokens": 0},
                },
            },
        )

    async with (
        serve(0, "local-fixture", {"decisions": "local-fixture"}, transport=httpx.MockTransport(dispatch)) as app,
        httpx.AsyncClient(base_url=app.origin, headers={"X-Demo-Token": app.token, "Origin": app.origin}) as client,
    ):
        try:
            response = await client.post("/api/start", json={"taskId": "support", "api": "decisions", "mode": "live"})
            assert response.status_code == 200
            await asyncio.wait_for(entered.wait(), 5)
            if stopped:
                current = (await client.get("/api/state")).json()["run"]
                response = await client.post("/api/stop", json={"runId": current["id"]})
                assert response.status_code == 200
                await asyncio.wait_for(draining.wait(), 5)
                first = (await client.get("/api/state")).json()["run"]
                assert first["owner"] == "stopped" and first["closing"]
                await asyncio.sleep(0.04)
                second = (await client.get("/api/state")).json()["run"]
                exported = (await client.get("/api/export", params={"run": second["id"]})).json()
                assert second["elapsedMs"] > first["elapsedMs"], "Duration advances while the request drains."
                assert exported["elapsedMs"] >= second["elapsedMs"]
                release.set()
            deadline = asyncio.get_running_loop().time() + 8
            while True:
                run = (await client.get("/api/state")).json()["run"]
                if run["owner"] == "stopped" and not run["closing"]:
                    break
                assert asyncio.get_running_loop().time() < deadline
                await asyncio.sleep(0.01)
            assert run["status"] == ("stopped" if stopped else "refused")
            assert run["result"] == "unverified"
            assert requests == 1 and run["fixture"]["results"] == []
            exported = (await client.get("/api/export", params={"run": run["id"]})).json()
            assert exported["status"] == run["status"] and exported["result"] == "unverified"
            assert exported["cleanup"] == "completed"
            await asyncio.sleep(0.02)
            assert (await client.get("/api/state")).json()["run"]["elapsedMs"] == run["elapsedMs"]
            print("PASS Stop duration and cleanup" if stopped else "PASS refusal status and unverified result")
        finally:
            release.set()


async def main() -> None:
    for stopped in (False, True):
        await check(stopped)


asyncio.run(main())
