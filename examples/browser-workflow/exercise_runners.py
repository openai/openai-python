"""Drive both SDK runners through local mocked API transports and real Chromium."""

import json
import asyncio

import httpx2
from exercise import allow
from workflow import serve, open_workflow

from openai import AsyncOpenAI


async def main() -> None:
    with serve() as server:
        for api in ("responses", "decisions"):
            for variant, labels in (
                ("A", ("Open REQ-401", "Reserve R2 Garden", "Outgoing", "Send REQ-401 to cedar@example.test")),
                ("B", ("Open REQ-718", "Reserve T2 Garden", "Outgoing", "Send REQ-718 to aster@example.test")),
            ):
                async with open_workflow(server, variant, confirm=allow) as w:
                    requests = 0
                    phase = 0

                    def transport(
                        request: httpx2.Request, api: str = api, labels: tuple[str, ...] = labels
                    ) -> httpx2.Response:
                        nonlocal requests, phase
                        assert request.url.host == "workflow.invalid"
                        assert request.url.path == f"/v1/{api}"
                        body = json.loads(request.content)
                        step = requests
                        requests += 1
                        if api == "decisions":
                            observation = json.loads(body["input"][1]["content"])
                            assert len(observation["priorActions"]) == min(step, len(labels))
                            choices = body["questions"][0]["choices"]
                            choice = (
                                "done"
                                if step == len(labels)
                                else next(c["value"] for c in choices if c["description"] == f"Click {labels[step]}")
                            )
                            return httpx2.Response(
                                200,
                                json={
                                    "object": "decision",
                                    "id": f"d_{step}",
                                    "model": "",
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
                        response = {
                            "id": f"resp_{step}",
                            "object": "response",
                            "created_at": 0,
                            "status": "completed",
                            "model": "",
                        }
                        if phase == len(labels) * 2:
                            return httpx2.Response(
                                200,
                                json={
                                    **response,
                                    "output": [
                                        {
                                            "id": f"msg_{step}",
                                            "type": "message",
                                            "role": "assistant",
                                            "status": "completed",
                                            "phase": "final_answer",
                                            "content": [
                                                {"type": "output_text", "text": "Booking sent.", "annotations": []}
                                            ],
                                        }
                                    ],
                                },
                            )
                        member = "click" if phase % 2 else "read_page"
                        args: dict[str, object] = {"tab_id": None, "filter": "all"}
                        if member == "click":
                            last = body["input"][-1]
                            assert last["type"] == "function_call_output"
                            observation = json.loads(last["output"][0]["text"])
                            if not observation["ok"]:
                                assert (
                                    "changed" in observation["error"].lower()
                                    or "read again" in observation["error"].lower()
                                )
                                member = "read_page"
                            else:
                                target = next(
                                    e["ref"]
                                    for e in observation["result"]["elements"]
                                    if e["label"] == labels[phase // 2]
                                )
                                args = {"tab_id": None, "target": target}
                                phase += 1
                        else:
                            phase += 1
                        return httpx2.Response(
                            200,
                            json={
                                **response,
                                "output": [
                                    {
                                        "type": "function_call",
                                        "id": f"fc_{step}",
                                        "call_id": f"call_{step}",
                                        "name": f"browser_{member}",
                                        "arguments": json.dumps(args),
                                        "status": "completed",
                                    }
                                ],
                            },
                        )

                    async with AsyncOpenAI(
                        api_key="synthetic-not-a-key",
                        base_url="http://workflow.invalid/v1",
                        max_retries=0,
                        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
                    ) as client:
                        result = await w.run(client, "", api)
                    assert result["status"] == "verified", (api, variant, result["status"])
                    assert w.requests == requests, "receipt counts actual SDK requests"
                    assert len(w.calls) >= len(labels), "receipt records observed SDK effects/selections"
                    assert requests == 5 if api == "decisions" else 9 <= requests <= 16
                print(f"PASS {api} {variant} real browser via mocked SDK transport")


if __name__ == "__main__":
    asyncio.run(main())
