"""Local HTTP exercises for real Python SDK requests; never connects to an API provider."""

from __future__ import annotations

import json
import asyncio
from typing import cast
from collections.abc import Mapping, Callable
from typing_extensions import override

import httpx2 as httpx
from server import serve
from exercise import JSONMap, binding, receipt


def stream(items: list[JSONMap], number: int) -> httpx.Response:
    complete = {
        "id": f"resp_{number}",
        "object": "response",
        "created_at": 0,
        "model": "synthetic-wire-model",
        "status": "completed",
        "output": items,
    }
    events: list[JSONMap] = [
        {"type": "response.created", "response": {**complete, "status": "in_progress", "output": []}}
    ]
    for index, item in enumerate(items):
        initial = {**item, "arguments": ""} if item["type"] == "function_call" else item
        events.append({"type": "response.output_item.added", "output_index": index, "item": initial})
        if item["type"] == "function_call":
            events.append(
                {
                    "type": "response.function_call_arguments.delta",
                    "output_index": index,
                    "item_id": item["id"],
                    "delta": item["arguments"],
                }
            )
        events.append({"type": "response.output_item.done", "output_index": index, "item": item})
    events.append({"type": "response.completed", "response": complete})
    content = "".join(
        f"data: {json.dumps({**event, 'sequence_number': sequence})}\n\n" for sequence, event in enumerate(events)
    ).encode()
    return httpx.Response(200, content=content, headers={"content-type": "text/event-stream"})


class ControlledAPI(httpx.AsyncBaseTransport):
    def __init__(self, hold: bool = False) -> None:
        self.hold = hold
        self.arrived = asyncio.Event()
        self.release = asyncio.Event()
        self.calls: list[JSONMap] = []
        self.clicks = 0

    @override
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        self.calls.append({"path": request.url.path, "body": body})
        self.arrived.set()
        if self.hold:
            await self.release.wait()
        if request.url.path.endswith("/decisions"):
            candidates = body["questions"][0]["choices"]
            choice = next(
                item["value"]
                for item in candidates
                if item.get("description") == ("Click Billing", "Click Technical", "Click Account")[self.clicks]
            )
            self.clicks += 1
            return httpx.Response(
                200,
                json={
                    "object": "decision",
                    "id": "controlled",
                    "model": "synthetic-wire-model",
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
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                        "output_tokens_details": {"reasoning_tokens": 0},
                    },
                },
            )
        assert request.url.path.endswith("/responses"), request.url
        turn = len(self.calls)
        if self.clicks == 3:
            return stream(
                [
                    {
                        "id": "msg",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": "Done", "annotations": []}],
                    }
                ],
                turn,
            )
        if turn % 2 == 0:
            name = next(tool["name"] for tool in body["tools"] if tool["name"].endswith("read_page"))
            args = {"tab_id": None, "filter": "all"}
        else:
            # Parse only the observation carried over the SDK wire, not the server's Run.
            history = body["input"]
            if turn == 1:
                text = next(
                    part["text"]
                    for item in history
                    for part in item.get("content", [])
                    if part.get("type") == "input_text" and part["text"].startswith("{")
                )
            else:
                read = next(item for item in reversed(history) if item.get("type") == "function_call_output")
                text = read["output"]
                if isinstance(text, list):
                    parts = cast(list[JSONMap], text)
                    text = next(part["text"] for part in parts if "text" in part)
            value = json.loads(text)
            if turn != 1:
                assert value["ok"] is True, value
                value = value["result"]
            element = next(
                item for item in value["elements"] if item["label"] == ("Billing", "Technical", "Account")[self.clicks]
            )
            args = {"tab_id": None, "target": element["ref"]}
            name = next(tool["name"] for tool in body["tools"] if tool["name"].endswith("click"))
            self.clicks += 1
        return stream(
            [
                {
                    "type": "function_call",
                    "status": "completed",
                    "id": f"fc_{turn}",
                    "call_id": f"call_{turn}",
                    "name": name,
                    "arguments": json.dumps(args),
                }
            ],
            turn,
        )


async def exercise(api_name: str, mode: str) -> None:
    transport = ControlledAPI(hold=mode != "complete")
    async with serve(0, "synthetic-key-for-local-wire", {api_name: "synthetic-wire-model"}, transport) as app:
        async with httpx.AsyncClient(base_url=app.origin, timeout=15) as client:
            client.headers["X-Demo-Token"] = app.token

            async def send(path: str, value: Mapping[str, object], status: int = 200) -> None:
                reply = await client.post(path, json=value)
                assert reply.status_code == status, (path, reply.status_code, reply.text)

            async def state_until(predicate: Callable[[JSONMap], object]) -> JSONMap:
                state: JSONMap = {}
                for _ in range(220):
                    response = await client.get("/api/state")
                    assert response.status_code == 200, response.text
                    state = response.json()["run"]
                    assert (
                        "synthetic-key-for-local-wire" not in response.text
                        and "synthetic-wire-model" not in response.text
                    )
                    if predicate(state):
                        return state
                    await asyncio.sleep(0.05)
                raise AssertionError(state)

            await send("/api/start", {"environment": "browser", "taskId": "support", "api": api_name, "mode": "live"})
            await asyncio.wait_for(transport.arrived.wait(), 5)
            if mode == "complete":
                state = await state_until(lambda run: run["owner"] == "stopped" and not run["closing"])
                assert state["status"] == "complete" and state["fixture"]["results"] == [
                    {"id": "T-1042", "choice": "Billing"},
                    {"id": "T-1043", "choice": "Technical"},
                    {"id": "T-1044", "choice": "Account"},
                ], state
                assert state["requests"] == len(transport.calls)
            else:
                active = await state_until(lambda run: run["browser"] is not None)
                if mode == "take":
                    await send("/api/take-control", binding(active))
                    state = await state_until(lambda run: run["owner"] == "human")
                    assert state["status"] == "paused" and state["fixture"]["results"] == [], state
                    assert len(transport.calls) == 1 and not transport.release.is_set()
                    await send("/api/stop", {"runId": state["id"]})
                else:
                    await send("/api/stop", {"runId": active["id"]})
                    state = await state_until(lambda run: run["owner"] == "stopped")
                state = await state_until(lambda run: not run["closing"])
                assert state["fixture"]["results"] == [] and state["result"] == "unverified", state
                assert len(transport.calls) == 1
            exported = await receipt(client, state)
            assert exported["cleanup"] == "completed"
            requests = [event for event in exported["events"] if event["kind"] == "request"]
            assert len(requests) == exported["requests"] == len(transport.calls)
            if mode == "complete":
                assert all(
                    event["phase"] == "headers" and event["status"] == 200 and event["durationMs"] >= event["headersMs"]
                    for event in requests
                )
                assert exported["requestHeadersMs"] == sum(event["headersMs"] for event in requests)
            else:
                assert len(requests) == 1
                assert requests[0]["phase"] == "cancelled" and requests[0]["headersMs"] is None
                assert requests[0]["durationMs"] is not None and exported["requestHeadersMs"] == 0
                # Old network was retired without a server reply; no old request can affect the new workspace.
                assert not transport.release.is_set()
                await send("/api/start", {"taskId": "support", "api": api_name, "mode": "live"})
                replacement = await state_until(lambda run: run["id"] != state["id"] and run["requests"] == 1)
                assert len(transport.calls) == 2
                assert replacement["fixture"]["results"] == []
                await send("/api/stop", {"runId": replacement["id"]})
                await state_until(lambda run: run["owner"] == "stopped" and not run["closing"])
                assert len(transport.calls) == 2
            assert exported["elapsedMs"] <= state["elapsedMs"] + 1
            print(f"PASS controlled {api_name} HTTP {mode} ({len(transport.calls)} SDK requests)")


async def main() -> None:
    for api_name in ("decisions", "responses"):
        for mode in ("complete", "stop", "take"):
            await exercise(api_name, mode)


if __name__ == "__main__":
    asyncio.run(main())
