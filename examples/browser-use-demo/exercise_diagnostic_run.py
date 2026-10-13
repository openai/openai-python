"""Reconstruct a real, wrong local browser action without exposing private data in export."""

import sys
import json
import shutil
import asyncio
from typing import cast

import httpx2 as httpx
from server import serve
from diagnostics import DiagnosticCapture, read_diagnostic_trace
from playwright.async_api import BrowserContext


async def check_cleanup() -> None:
    # server installs the adjacent browser examples on the path before runner imports file_state.
    from runner import Run

    class OwnedContext:
        def __init__(self, fail_close: bool, close_entered: asyncio.Event) -> None:
            self.fail_close = fail_close
            self.close_entered = close_entered

        async def close(self) -> None:
            self.close_entered.set()
            if self.fail_close:
                raise RuntimeError("finite owned close failure")

    for fail_close in (False, True):
        capture = DiagnosticCapture()
        agent_gate = asyncio.Event()
        launch_gate = asyncio.Event()
        close_entered = asyncio.Event()

        async def held(gate: asyncio.Event) -> None:
            await gate.wait()

        try:
            async with serve(0, diagnostic_capture=capture) as app:
                run = Run(app, {"taskId": "support", "api": "decisions", "mode": "rehearsal"})
                app.current = run
                run.context = cast(BrowserContext, OwnedContext(fail_close, close_entered))
                run.agent = asyncio.create_task(held(agent_gate))
                run.launch_retirement = asyncio.create_task(held(launch_gate))
                filename = capture.directory / "run-1.jsonl"
                run.stop()
                await asyncio.wait_for(close_entered.wait(), 2)
                assert run.busy() and read_diagnostic_trace(filename)["incomplete"]
                agent_gate.set()
                await asyncio.wait_for(run.agent, 2)
                assert run.busy() and read_diagnostic_trace(filename)["incomplete"]
                launch_gate.set()
                assert run.cleanup is not None
                await asyncio.wait_for(run.cleanup, 2)
                trace = read_diagnostic_trace(filename)
                assert not trace["incomplete"]
                final = [row for row in trace["records"] if row["kind"] == "run" and "cleanup" in row["data"]]
                assert len(final) == 1
                assert final[0]["data"]["cleanup"] == ("failed" if fail_close else "completed")
                if fail_close:
                    assert final[0]["data"]["status"] == "cleanup_failed" and run.busy()
                    try:
                        await app.close()
                    except RuntimeError as error:
                        assert str(error) == "Workspace cleanup did not finish."
                    else:
                        raise AssertionError("failed resource cleanup must stay unavailable")
                else:
                    assert not run.busy()
                    await app.close()
                # The test observed the real application's failure; release its retained failed test owner.
                app.current = None
            print(
                f"PASS {'failed' if fail_close else 'completed'} cleanup joins agent and late launch before trace close"
            )
        finally:
            agent_gate.set()
            launch_gate.set()
            shutil.rmtree(capture.directory)


async def main() -> None:
    secret = "synthetic-diagnostic-credential"
    capture = DiagnosticCapture((secret,))
    requests = 0

    def dispatch(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        assert request.url.path == "/v1/decisions"
        body = json.loads(request.content)
        label = ("Click Technical", "Click Technical", "Click Account")[requests]
        choice = next(item["value"] for item in body["questions"][0]["choices"] if item.get("description") == label)
        requests += 1
        return httpx.Response(
            200,
            json={
                "object": "decision",
                "id": f"local-{requests}",
                "model": "local-diagnostic-check",
                "answers": [
                    {
                        "name": "next_action",
                        "type": "choice",
                        "choice": choice,
                        "confidence": 1,
                        "probabilities": [{"value": choice, "probability": 1}],
                    }
                ],
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 1,
                    "total_tokens": 11,
                    "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                    "output_tokens_details": {"reasoning_tokens": 0},
                },
            },
        )

    try:
        async with (
            serve(
                0,
                secret,
                {"decisions": "local-diagnostic-check"},
                transport=httpx.MockTransport(dispatch),
                diagnostic_capture=capture,
            ) as app,
            httpx.AsyncClient(base_url=app.origin) as client,
        ):
            client.headers.update({"X-Demo-Token": app.token, "Origin": app.origin})
            started = await client.post("/api/start", json={"taskId": "support", "api": "decisions", "mode": "live"})
            assert started.status_code == 200
            deadline = asyncio.get_running_loop().time() + 20
            run = started.json()
            while asyncio.get_running_loop().time() < deadline:
                run = (await client.get("/api/state")).json()["run"]
                if run["owner"] == "stopped" and not run["closing"]:
                    break
                await asyncio.sleep(0.02)
            assert run["result"] == "unverified" and requests == 3
            exported = (await client.get("/api/export", params={"run": run["id"]})).json()
            assert exported["cleanup"] == "completed"
            assert exported["diagnostics"]["usage"] == {
                "recordedRequests": 3,
                "missingRequests": 0,
                "complete": True,
                "inputTokens": 30,
                "outputTokens": 3,
                "totalTokens": 33,
            }
            public = json.dumps(exported)
            assert all(
                value not in public
                for value in (secret, "Charged twice", "Technical", str(capture.directory), "data:image/")
            )
            filename = capture.directory / "run-1.jsonl"
            trace = read_diagnostic_trace(filename)
            assert not trace["incomplete"]
            records = trace["records"]
            choices = next(record["data"] for record in records if record["kind"] == "choices")
            selected = next(
                record["data"]
                for record in records
                if record["kind"] == "runner" and record["data"]["stage"] == "selection"
            )
            assert (
                next(choice["description"] for choice in choices if choice["id"] == selected["call_id"])
                == "Click Technical"
            )
            assert any(
                record["kind"] == "observation" and "Charged twice" in json.dumps(record["data"]) for record in records
            )
            assert any(
                record["kind"] == "effect" and record["data"]["state"]["results"][0]["choice"] == "Technical"
                for record in records
            )
            assert any(record["kind"] == "verification" and record["data"]["verified"] is False for record in records)
            assert "data:image/" not in filename.read_text()
            assert (await client.get("/run-1.jsonl")).status_code == 404
        print("PASS actual wrong choice is reconstructible from private trace; safe export retains actual usage only")
    finally:
        shutil.rmtree(capture.directory)


if __name__ == "__main__":
    asyncio.run(check_cleanup() if sys.argv[1:] == ["--cleanup"] else main())
