"""Run with each wheel/sdist consumer's Python: python -I -B scripts/fixtures/computer_use_smoke.py."""

import sys
import json
import asyncio
import inspect
from types import SimpleNamespace
from typing import Any, Callable, cast
from pathlib import Path
from contextlib import AsyncExitStack

import httpx2

import openai
from openai.lib import computer
from openai.lib.browser import BrowserDriver, BrowserToolset, AsyncBrowserDriver, AsyncBrowserToolset
from openai.lib.responses_tool_runner import (
    ToolRunnerError,
    ResponsesToolLedger,
    ResponsesToolRunner,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)


async def smoke(lane: str) -> None:
    assert openai.ComputerToolset is computer.ComputerToolset
    assert openai.AsyncComputerToolset is computer.AsyncComputerToolset
    assert openai.ComputerDriver is computer.ComputerDriver
    assert openai.AsyncComputerDriver is computer.AsyncComputerDriver
    assert Path(openai.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), openai.__file__
    effects: list[str] = []
    bodies: list[dict[str, Any]] = []
    checkpoint: Any = None
    resume = False
    image = {"type": "computer_screenshot", "image_url": "data:image/png;base64,cG5n"}

    def adapt(fn: Callable[..., Any]) -> Any:
        if lane == "sync":
            return fn

        async def call(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        return call

    def unexpected(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("Unexpected computer action")

    def read_page(*_args: Any) -> str:
        effects.append("read")
        return "receipt ready"

    def wait(*_args: Any) -> None:
        effects.append("wait")

    def screenshot(*_args: Any) -> Any:
        effects.append("screenshot")
        return image

    driver = SimpleNamespace(
        state=adapt(
            lambda: {"tabs": [{"id": "one", "title": "Receipt", "url": "https://fixture.invalid/", "active": True}]}
        ),
        read_page=adapt(read_page),
    )
    native = SimpleNamespace(
        **{name: adapt(unexpected) for name in ("click", "double_click", "drag", "keypress", "move", "scroll", "type")},
        wait=adapt(wait),
        screenshot=adapt(screenshot),
    )

    def transport(request: httpx2.Request) -> httpx2.Response:
        bodies.append(json.loads(request.content))
        if resume:
            output: list[dict[str, Any]] = [
                {
                    "type": "message",
                    "id": "msg_one",
                    "status": "completed",
                    "role": "assistant",
                    "phase": "final_answer",
                    "content": [{"type": "output_text", "text": "complete", "annotations": []}],
                }
            ]
        else:
            output = [
                {
                    "type": "function_call",
                    "id": "fc_read",
                    "call_id": "read",
                    "name": "browser_read_page",
                    "status": "completed",
                    "arguments": '{"tab_id":null,"filter":"all"}',
                },
                {
                    "type": "computer_call",
                    "id": "cu_one",
                    "call_id": "native_one",
                    "status": "completed",
                    "actions": [{"type": "wait"}],
                },
            ]
        return httpx2.Response(
            200,
            json={
                "id": f"resp_{len(bodies)}",
                "object": "response",
                "created_at": 0,
                "model": "",
                "status": "completed",
                "output": output,
            },
        )

    def save(value: Any) -> None:
        nonlocal checkpoint
        checkpoint = value
        # A durable resumable boundary survived a lost recorder acknowledgement.
        if not resume and value["phase"] == "boundary" and value["returned_call_ids"]:
            raise RuntimeError("Synthetic lost acknowledgement")

    async def invoke(value: Any) -> Any:
        return await value if inspect.isawaitable(value) else value

    async with AsyncExitStack() as stack:
        if lane == "sync":
            client: Any = stack.enter_context(
                openai.OpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=0,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
                )
            )
            runner: Any = ResponsesToolRunner(
                browser=BrowserToolset(cast(BrowserDriver, driver), members=["read_page"]),
                computer=openai.ComputerToolset(cast(computer.ComputerDriver, native)),
            )
            ledger: Any = ResponsesToolLedger
        else:
            client = await stack.enter_async_context(
                openai.AsyncOpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=0,
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
                )
            )
            runner = AsyncResponsesToolRunner(
                browser=AsyncBrowserToolset(cast(AsyncBrowserDriver, driver), members=["read_page"]),
                computer=openai.AsyncComputerToolset(cast(computer.AsyncComputerDriver, native)),
            )
            ledger = AsyncResponsesToolLedger
        params: Any = {"model": "", "input": "Process the receipt", "store": False}
        try:
            await invoke(runner.run(client, params, max_steps=3, ledger=ledger("package-smoke", adapt(save))))
        except ToolRunnerError:
            pass  # The recorder deliberately rejected the acknowledgement after saving the boundary.
        else:
            raise AssertionError("Run continued after losing its checkpoint acknowledgement")
        assert len(bodies) == 1
        assert checkpoint["phase"] == "boundary"
        assert checkpoint["returned_call_ids"] == ["read", "native_one"]
        assert effects == ["read", "wait", "screenshot"]
        previous = checkpoint
        resume = True
        fresh = [{"role": "user", "content": [{"type": "input_text", "text": "Continue"}]}]
        final = await invoke(
            runner.run(
                client,
                {**params, "input": fresh},
                ledger=ledger(
                    "package-smoke",
                    adapt(save),
                    previous,
                ),
            )
        )
        assert final.output_text == "complete"
        assert len(bodies) == 2
        assert bodies[1]["input"] == previous["history"] + fresh
        returned = [item for item in bodies[1]["input"] if item.get("type", "").endswith("_call_output")]
        assert [item["call_id"] for item in returned] == ["read", "native_one"]
        assert json.loads(returned[0]["output"][0]["text"])["result"] == "receipt ready"
        assert returned[1]["output"] == image
        assert effects == ["read", "wait", "screenshot"]
    print(f"Installed computer-use smoke {lane}: PASS")


async def main() -> None:
    await smoke("sync")
    await smoke("async")


if __name__ == "__main__":
    asyncio.run(main())
