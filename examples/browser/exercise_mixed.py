"""No API: real local browser/HTTP. Add --runtime-dir only for a real guest run."""

from __future__ import annotations

import io
import os
import pty
import json
import asyncio
import argparse
from typing import TypeVar, cast
from pathlib import Path
from threading import Event
from unittest.mock import patch
from collections.abc import Callable, Awaitable

import httpx2
import run_mixed
from run_mixed import Desktop, Terminal
from mixed_session import PUBLIC_RECEIPT, Handler, Dispatch, MixedSession, open_mixed
from playwright.async_api import Error, BrowserContext

from openai import AsyncOpenAI
from openai.lib.browser import ClickInput, BrowserCancelledError
from openai.lib.computer import Screenshot, AsyncComputerDriver, ComputerActionInput, AsyncComputerToolset
from openai.lib.responses_tool_runner import ToolRunnerError
from openai.types.responses.computer_action import Keypress


class SimulatedInput:
    """Test-only counter. It cannot verify a guest file or desktop."""

    def __init__(self) -> None:
        self.actions: list[str] = []

    async def screenshot(self) -> Screenshot:
        return {
            "type": "computer_screenshot",
            "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
        }

    async def click(self, action: ComputerActionInput) -> None:
        self.actions.append(action.type)

    async def move(self, action: ComputerActionInput) -> None:
        self.actions.append(action.type)

    async def type(self, action: ComputerActionInput) -> None:
        self.actions.append(action.type)

    async def keypress(self, action: ComputerActionInput) -> None:
        self.actions.append(action.type)

    async def unexpected_action(self, action: ComputerActionInput) -> None:
        raise AssertionError(f"Unexpected computer action in the mixed exercise: {action.type}")

    double_click = unexpected_action
    drag = unexpected_action
    scroll = unexpected_action
    wait = unexpected_action


T = TypeVar("T")


class SimulatedLease:
    """Only tests admission. A simulated desktop must never pass file verification."""

    def __init__(self) -> None:
        self.input = SimulatedInput()
        self.active = False
        self.uncertain_effects = False
        self.stopped = False

    async def operation_async(self, work: Callable[[AsyncComputerToolset], Awaitable[T]]) -> T:
        assert not self.active and not self.stopped, "Overlapping or revoked desktop lease"
        self.active = True
        try:
            return await work(AsyncComputerToolset(cast(AsyncComputerDriver, self.input)))
        finally:
            self.active = False

    def stop(self) -> None:
        self.stopped = True

    def verify(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, object]:
        del cancelled
        return {"file_matches": False, "file_empty": True, "browser_matches": False, "browser_effects": 0}


class Script:
    """Synthetic Responses wire, using refs and tab IDs from actual browser outputs."""

    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.requests = 0
        self.tab = ""
        self.ref = ""
        self.private_result = ""

    def function(self, name: str, args: dict[str, object]) -> dict[str, object]:
        return {
            "type": "function_call",
            "name": name,
            "arguments": json.dumps(args),
            "id": f"fc_{self.requests}",
            "call_id": f"call_{self.requests}",
            "status": "completed",
        }

    def request(self, req: httpx2.Request) -> httpx2.Response:
        assert req.url.path == "/responses", "Only synthetic API route"
        self.requests += 1
        body = json.loads(req.content)
        if self.private_result:
            assert self.private_result not in json.dumps(body), "Private receipt capability reached the model"
        tool_outputs = [item for item in body["input"] if item.get("type") == "function_call_output"]
        step = self.requests
        output: list[dict[str, object]]
        if self.mode in {"resume_snapshot", "resume_stale"} and step > 1:
            step = 6
        if self.mode in {"resume_snapshot", "resume_stale"} and step == 1:
            text = body["input"][0]["content"][0]["text"]
            read, _ = json.JSONDecoder().raw_decode(text.split("Current Host browser: ", 1)[1])
            route = [item for item in read["elements"] if item["label"] == "Route D-2201"]
            assert len(route) == 1, "The resumed phase has no usable Route reference"
            target = self.ref if self.mode == "resume_stale" else route[0]["ref"]
            assert route[0]["ref"] != self.ref, "A pre-handoff reference was reused"
            output = [self.function("browser_click", {"tab_id": None, "target": target})]
        elif step == 1:
            output = [self.function("browser_list_tabs", {})]
        elif step == 2:
            value = json.loads(tool_outputs[-1]["output"][0]["text"])
            self.tab = value["state"]["tabs"][0]["id"]
            output = [self.function("browser_read_page", {"tab_id": self.tab, "filter": "interactive"})]
        elif step == 3:
            value = json.loads(tool_outputs[-1]["output"][0]["text"])
            assert value["ok"], value
            wanted = "Different Route" if self.mode == "wrong_ref" else "Route D-2201"
            self.ref = next(item["ref"] for item in value["result"]["elements"] if item["label"] == wanted)
            if self.mode == "navigation":
                output = [self.function("browser_navigate", {"tab_id": self.tab, "url": "http://127.0.0.1:1/trap"})]
            else:
                output = [self.function("browser_click", {"tab_id": self.tab, "target": self.ref})]
        elif step == 4:
            args: dict[str, object] = {"case_id": "D-2201"}
            if self.mode == "wrong_case":
                args["case_id"] = "D-0000"
            if self.mode == "extra_path":
                args["path"] = "/tmp/NOT_GRANTED"
            if self.mode == "extra_url":
                args["url"] = "http://127.0.0.1:1/trap"
            output = [self.function("approved_receipt", args)]
        elif step == 5:
            if tool_outputs:
                assert tool_outputs[-1]["output"] == PUBLIC_RECEIPT.decode("ascii")
            else:
                assert PUBLIC_RECEIPT.decode("ascii") in body["input"][0]["content"][0]["text"]
            text = "/tmp/NOT_GRANTED" if self.mode == "native_path" else PUBLIC_RECEIPT.decode("ascii")
            output = [
                {
                    "type": "computer_call",
                    "id": "cu_local",
                    "call_id": "call_native",
                    "status": "completed",
                    "actions": [
                        {"type": "click", "button": "left", "x": 700, "y": 180},
                        {"type": "keypress", "keys": ["CTRL", "A"]},
                        {"type": "type", "text": text},
                        {"type": "keypress", "keys": ["CTRL", "S"]},
                    ],
                }
            ]
        else:
            output = [
                {
                    "id": "msg_local",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {"type": "output_text", "text": "Scripted task ended; verify all owners.", "annotations": []}
                    ],
                }
            ]
        return httpx2.Response(
            200,
            json={
                "id": f"resp_{step}",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": "",
                "output": output,
                "parallel_tool_calls": False,
                "tools": body["tools"],
            },
        )


async def check(mode: str, runtime_dir: Path | None = None) -> dict[str, object]:
    script = Script(mode)
    session: MixedSession | None = None
    entered = asyncio.Event()

    async def approve(workspace: str) -> bool:
        if mode == "deny_browser" and workspace.startswith("Host"):
            return False
        if mode == "deny_file" and workspace.startswith("Local"):
            return False
        if mode == "deny_native" and workspace.startswith("Isolated"):
            return False
        if mode == "held_stop" and workspace.startswith("Local"):
            entered.set()
            await asyncio.Event().wait()
        return True

    base_reply = Handler.reply

    def fixture_reply(
        handler: Handler, code: int, body: bytes = b"", content_type: str = "application/octet-stream"
    ) -> None:
        if handler.path.startswith("/result/") and mode == "digest" and body == PUBLIC_RECEIPT:
            body = b"X" * len(body)
        if handler.path.startswith("/result/") and mode == "unknown":
            handler.close_connection = True
            return
        if handler.path.startswith("/result/") and mode == "redirect":
            handler.send_response(302)
            handler.send_header("location", "http://127.0.0.1:1/trap")
            handler.send_header("content-length", "0")
            handler.end_headers()
            return
        base_reply(handler, code, body, content_type)

    desktop: Desktop | None = None
    fake = SimulatedInput()
    computer = AsyncComputerToolset(cast(AsyncComputerDriver, fake))
    try:
        if runtime_dir is not None:
            desktop = await asyncio.to_thread(Desktop, runtime_dir)
        with patch.object(Handler, "reply", fixture_reply):
            async with (
                open_mixed(approve) as current,
                AsyncOpenAI(
                    api_key="synthetic-local",
                    base_url="http://local.invalid/",
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(script.request)),
                    max_retries=0,
                ) as client,
            ):
                session = current
                assert current.download is not None
                area = current.download.area
                if mode == "positive":
                    script.private_result = current.server.result_url
                    async with httpx2.AsyncClient(trust_env=False) as direct:
                        response = await direct.post(
                            current.server.url.removesuffix("/dispatch") + "/route",
                            json={"case_id": "D-2201", "action": "route"},
                        )
                        assert response.status_code == 403 and current.server.routes == 0
                        assert (await direct.get(current.server.url)).status_code == 403
                        assert (
                            await direct.get(current.server.url.removesuffix("/dispatch") + "/result")
                        ).status_code == 403
                        assert (await direct.get(current.server.result_url)).status_code == 409
                    assert current.server.results == 0
                    _, page = current.driver.page(current.driver.active)
                    assert current.server.result_url not in await page.content()
                if mode == "wrong_ref":
                    _, page = current.driver.page(current.driver.active)
                    await page.evaluate("""() => {
                      const button = document.createElement('button');
                      button.textContent = 'Different Route';
                      button.onclick = async () => {
                        const reply = await fetch('/route', {method:'POST',
                          headers:{'Content-Type':'application/json'},
                          body:JSON.stringify({case_id:'D-2201', action:'route'})});
                        if (reply.ok) document.querySelector('[data-result]').disabled = false;
                      };
                      document.querySelector('[data-record-id="D-2201"]').append(button);
                    }""")
                if desktop:
                    assert await asyncio.to_thread(desktop.verify) == {
                        "file_matches": False,
                        "file_empty": True,
                        "browser_matches": False,
                        "browser_effects": 0,
                    }
                    task = asyncio.create_task(desktop.operation_async(lambda tools: current.run(tools, client, "")))
                else:
                    task = asyncio.create_task(current.run(computer, client, ""))
                if mode == "held_stop":
                    await asyncio.wait_for(entered.wait(), 10)
                    current.stop()
                failed: ToolRunnerError | None = None
                try:
                    await asyncio.wait_for(task, 30)
                except ToolRunnerError as exc:
                    failed = exc
                if mode == "positive":
                    assert failed is None, {
                        "requests": script.requests,
                        "attempted": failed.attempted_call_ids if failed else (),
                        "completed": failed.completed_call_ids if failed else (),
                        "routes": current.server.routes,
                        "results": current.server.results,
                        "reason": current.reason,
                        "simulated_actions": fake.actions,
                    }
                    assert current.server.routes == current.server.results == 1
                    assert current.server.browser_routed and current.disclosed
                    assert current.download.state()["current"] == {"status": "completed", "effect": "completed"}
                    if desktop:
                        result = current.proof(await asyncio.to_thread(desktop.verify))
                        assert result["status"] == "verified", result
                    else:
                        assert fake.actions == ["click", "keypress", "type", "keypress"]
                        result = current.proof({})
                        assert result["status"] == "unverified", "Mock native input is never a file proof"
                else:
                    assert failed is not None, mode
                    assert current.reason is not None
                    assert current.server.routes == (0 if mode in {"deny_browser", "navigation", "wrong_ref"} else 1)
                    assert current.server.results == (
                        1 if mode in {"digest", "unknown", "redirect", "deny_native", "native_path"} else 0
                    )
                    assert not fake.actions or mode == "native_path"
                    if mode in {"digest", "unknown", "redirect"}:
                        assert current.download.state()["current"] == {"status": "unknown", "effect": "unknown"}
                        assert not current.disclosed
                        assert current.download.stats["requests"] == 1
                    if desktop and mode == "deny_native":
                        guest = await asyncio.to_thread(desktop.verify)
                        assert guest["file_empty"] is True and guest["browser_effects"] == 0
                    current.stop()
                    earlier = script.requests
                    try:
                        await current.run(computer, client, "")
                    except RuntimeError:
                        pass
                    else:
                        raise AssertionError("A stopped session admitted new work")
                    assert script.requests == earlier
                    result = current.proof({})
                assert current.server.checked_click is False
                summary = {
                    "case": mode,
                    "api": "synthetic MockTransport; external API requests 0",
                    "native": "real guest" if desktop else "simulated input only",
                    "requests": script.requests,
                    "routes": current.server.routes,
                    "results": current.server.results,
                    "status": result["status"],
                }
            assert not area.exists(), "Quarantine was not removed"
            return summary
    finally:
        if session:
            session.stop()
        if desktop is not None:
            await asyncio.to_thread(desktop.stop)


async def handoff(mode: str, runtime_dir: Path | None = None) -> dict[str, object]:
    """Test real browser+file effects. Guest assertions require the real runtime."""
    entered, release = asyncio.Event(), asyncio.Event()
    prompts: list[str] = []
    first = Script("positive")
    seen = 0
    desktop = await asyncio.to_thread(Desktop, runtime_dir) if runtime_dir else cast(Desktop, SimulatedLease())

    async def approve(workspace: str) -> bool:
        nonlocal seen
        prompts.append(workspace)
        if workspace.startswith("Local"):
            seen += 1
            if mode in {"before_receipt", "expired", "stop_in_human"} and seen == 1:
                entered.set()
                await release.wait()
        if workspace.startswith("Isolated") and mode == "after_receipt" and not entered.is_set():
            entered.set()
            await release.wait()
        return True

    try:
        async with (
            open_mixed(approve) as current,
            AsyncOpenAI(
                api_key="synthetic-local",
                base_url="http://local.invalid/",
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(first.request)),
                max_retries=0,
            ) as client,
        ):
            assert current.download is not None
            area = current.download.area
            click = current.driver.click

            async def held_click(action: ClickInput) -> str | None:
                if mode == "route_after":
                    result = await click(action)
                else:
                    result = None
                entered.set()
                await release.wait()
                if mode == "route_before":
                    result = await click(action)
                return result

            if mode in {"route_before", "route_after"}:
                with patch.object(current.driver, "click", held_click):
                    task = asyncio.create_task(current.agent_phase(desktop, client, ""))
                    await asyncio.wait_for(entered.wait(), 15)
                    ledger = json.loads((area / "phase.json").read_text())
                    assert len(ledger) == 14 and ledger["phase"] == "pending"
                    assert ledger["consumed_requests"] == current.requests == first.requests == 3
                    take = asyncio.create_task(current.take(desktop))
                    await asyncio.sleep(0)
                    assert current.owner == "draining" and not current.settled.is_set()
                    assert (area / "phase.json").is_file(), "Do not delete private state before the full lease"
                    try:
                        await current.human(desktop, "host receipt")
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("Human input during the admitted Route")
                    assert current.server.results == 0
                    release.set()
                    outcome = await asyncio.gather(task, take, return_exceptions=True)
            else:
                task = asyncio.create_task(current.agent_phase(desktop, client, ""))
                await asyncio.wait_for(entered.wait(), 15)
                ledger = json.loads((area / "phase.json").read_text())
                assert len(ledger) == 14 and ledger["phase"] == "pending"
                assert ledger["consumed_requests"] == current.requests == first.requests
                assert (area / "phase.json").stat().st_mode & 0o777 == 0o600
                if mode == "expired":
                    assert current.download.grant is not None
                    current.download.grant["expires_at"] = 0
                outcome = await asyncio.gather(task, current.take(desktop), return_exceptions=True)
            assert isinstance(outcome[0], ToolRunnerError), outcome
            assert not (area / "phase.json").exists() and not (area / "phase-next.json").exists()
            if mode == "expired":
                assert isinstance(outcome[1], RuntimeError) and current.owner == "stopped"
                assert current.server.results == 0
                summary: dict[str, object] = {
                    "case": mode,
                    "requests": current.requests,
                    "routes": current.server.routes,
                    "results": 0,
                }
            else:
                assert outcome[1] is None and current.owner == "human", outcome
                assert current.reason is None and current.server.routes == 1 and current.server.browser_routed
                after_download = mode == "after_receipt"
                assert current.server.results == int(after_download)
                assert current.download.stats["requests"] == int(after_download)
                # Both files are human-only and private. They cannot prove a simulated guest file.
                paths = await current.human(desktop, "view")
                assert paths is not None
                assert all(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") for path in paths)
                assert all(path.stat().st_mode & 0o777 == 0o600 for path in paths)
                if mode == "stop_in_human":
                    current.stop()
                    assert all(not path.exists() for path in paths)
                    before = current.requests
                    try:
                        await current.return_control(desktop)
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("Stop allowed Return")
                    assert current.requests == before and current.server.results == 0
                else:
                    grant_id = current.grant_id
                    await current.return_control(desktop)
                    assert all(not path.exists() for path in paths)
                    assert current.owner == "agent" and current.grant_id == grant_id
                    resumed = Script("positive")
                    # First response after Return asks for disclosure; the Route is already proven.
                    resumed.requests = 4 if after_download else 3
                    previous_wire = resumed.requests
                    previous = current.requests
                    async with AsyncOpenAI(
                        api_key="synthetic-local",
                        base_url="http://local.invalid/",
                        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(resumed.request)),
                        max_retries=0,
                    ) as new_client:
                        await current.agent_phase(desktop, new_client, "")
                    assert current.requests == previous + (resumed.requests - previous_wire)
                    assert current.requests <= 20
                    assert current.server.routes == current.server.results == current.download.stats["requests"] == 1
                    assert seen == (2 if mode == "before_receipt" else 1), (
                        "Transfer and completed disclosure cannot replay"
                    )
                    assert any(value.startswith("1:") for value in current.attempted)
                    assert any(value.startswith("2:") for value in current.attempted)
                    assert not (area / "phase.json").exists()
                    if runtime_dir:
                        proof = current.proof(await asyncio.to_thread(desktop.verify))
                        assert proof["status"] == "verified", proof
                    else:
                        assert current.proof({})["status"] == "unverified", "Mock is not native proof"
                summary = {
                    "case": mode,
                    "requests": current.requests,
                    "routes": current.server.routes,
                    "results": current.server.results,
                    "guest": bool(runtime_dir),
                    "owner": current.owner,
                }
        assert not area.exists(), "Owned ledger, snapshots and quarantine not removed"
        return summary
    finally:
        release.set()
        await asyncio.to_thread(desktop.stop)


async def human_budget(runtime_dir: Path | None) -> dict[str, object]:
    """Human completion at the original request limit, with no synthetic success."""
    entered, release = asyncio.Event(), asyncio.Event()
    desktop = await asyncio.to_thread(Desktop, runtime_dir) if runtime_dir else cast(Desktop, SimulatedLease())
    observed = 0

    async def approve(_description: str) -> bool:
        return True

    try:
        async with open_mixed(approve) as current:
            assert current.download is not None

            async def request(req: httpx2.Request) -> httpx2.Response:
                nonlocal observed
                observed += 1
                body = json.loads(req.content)
                if observed < 20:
                    output: list[dict[str, object]] = [
                        {
                            "type": "function_call",
                            "name": "browser_get_page_text",
                            "arguments": json.dumps({"tab_id": current.driver.active}),
                            "id": f"fc_{observed}",
                            "call_id": f"call_{observed}",
                            "status": "completed",
                        }
                    ]
                else:
                    entered.set()
                    await release.wait()
                    output = [
                        {
                            "id": "msg",
                            "type": "message",
                            "role": "assistant",
                            "status": "completed",
                            "content": [{"type": "output_text", "text": "Verify the fixed task.", "annotations": []}],
                        }
                    ]
                return httpx2.Response(
                    200,
                    json={
                        "id": f"resp_{observed}",
                        "object": "response",
                        "created_at": 0,
                        "status": "completed",
                        "model": "",
                        "output": output,
                        "parallel_tool_calls": False,
                        "tools": body["tools"],
                    },
                )

            async with AsyncOpenAI(
                api_key="synthetic-local",
                base_url="http://local.invalid/",
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(request)),
                max_retries=0,
            ) as client:
                task = asyncio.create_task(current.agent_phase(desktop, client, ""))
                await asyncio.wait_for(entered.wait(), 20)
                assert observed == current.requests == 20 and current.server.routes == current.server.results == 0
                take = asyncio.create_task(current.take(desktop))
                await asyncio.sleep(0)
                assert current.owner == "draining" and not current.settled.is_set()
                try:
                    await current.human(desktop, "host route")
                except ValueError:
                    pass
                else:
                    raise AssertionError("Human route overlapped held HTTP/desktop lease")
                assert current.server.routes == 0
                release.set()
                outcome = await asyncio.gather(task, take, return_exceptions=True)
                assert isinstance(outcome[0], ToolRunnerError) and outcome[1] is None, outcome
                assert current.owner == "human" and current.requests == 20
                await current.human(desktop, "host route")
                await current.human(desktop, "host receipt")
                assert current.server.routes == current.server.results == 1 and current.disclosed
                await current.human(desktop, "guest click 700 180")
                await current.human(desktop, "guest select-all")
                await current.human(desktop, "guest type")
                await current.human(desktop, "guest save")
                paths = await current.human(desktop, "view")
                assert paths and all(path.exists() for path in paths)
                await current.return_control(desktop)
                assert all(not path.exists() for path in paths)
                assert current.disclosed and current.requests == 20
                proof = await current.verify(desktop)
                assert proof["status"] == ("verified" if runtime_dir else "unverified"), proof
                assert observed == 20 and current.server.routes == current.server.results == 1
                if not runtime_dir:
                    # A mock cannot finish. Remaining budget still applies: no request21.
                    try:
                        await current.agent_phase(desktop, client, "")
                    except RuntimeError:
                        pass
                    else:
                        raise AssertionError("Request21 was admitted")
                    assert current.reason == "request_limit" and observed == 20
            return {
                "case": "human_finishes_at_original_20_limit",
                "requests": observed,
                "routes": current.server.routes,
                "results": current.server.results,
                "status": proof["status"],
                "guest": bool(runtime_dir),
            }
    finally:
        release.set()
        await asyncio.to_thread(desktop.stop)


async def transfer_interrupt(mode: str) -> dict[str, object]:
    entered, release = asyncio.Event(), asyncio.Event()
    body_entered, body_release = Event(), Event()
    desktop = cast(Desktop, SimulatedLease())
    script = Script("positive")
    approvals = 0

    async def approve(description: str) -> bool:
        nonlocal approvals
        if description.startswith("Local"):
            approvals += 1
        return True

    reply = Handler.reply

    def held_body(
        handler: Handler, code: int, body: bytes = b"", content_type: str = "application/octet-stream"
    ) -> None:
        if handler.path.startswith("/result/") and mode == "stop_transfer":
            body_entered.set()
            if not body_release.wait(4):
                handler.close_connection = True
                return
        reply(handler, code, body, content_type)

    try:
        with patch.object(Handler, "reply", held_body):
            async with (
                open_mixed(approve) as current,
                AsyncOpenAI(
                    api_key="synthetic-local",
                    base_url="http://local.invalid/",
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(script.request)),
                    max_retries=0,
                ) as client,
            ):
                assert current.download is not None
                downloaded = current.download.download

                async def after_transfer(args: dict[str, object]) -> str:
                    result = await downloaded(args)
                    if mode == "before_disclosure" and not entered.is_set():
                        entered.set()
                        await release.wait()
                    return result

                with patch.object(current.download, "download", after_transfer):
                    task = asyncio.create_task(current.agent_phase(desktop, client, ""))
                    if mode == "stop_transfer":
                        assert await asyncio.to_thread(body_entered.wait, 12)
                        assert current.download.stats["requests"] == 1 and current.server.results == 1
                        assert not current.disclosed and not current.settled.is_set()
                        current.stop()
                        # No response body arrives. The original fixed deadline must close it.
                        result = await asyncio.gather(task, return_exceptions=True)
                        body_release.set()
                        assert isinstance(result[0], ToolRunnerError), result
                        assert current.owner == "stopped" and not current.disclosed
                        assert current.download.state()["current"] == {"status": "unknown", "effect": "unknown"}
                        try:
                            await current.take(desktop)
                        except ValueError:
                            pass
                        else:
                            raise AssertionError("An uncertain transfer allowed human control")
                    else:
                        await asyncio.wait_for(entered.wait(), 12)
                        assert current.download.receipt()["completed"] is True
                        assert not current.disclosed and approvals == 1
                        take = asyncio.create_task(current.take(desktop))
                        await asyncio.sleep(0)
                        assert current.owner == "draining" and not current.settled.is_set()
                        release.set()
                        result = await asyncio.gather(task, take, return_exceptions=True)
                        assert isinstance(result[0], ToolRunnerError) and result[1] is None, result
                        assert current.owner == "human" and not current.disclosed
                        assert current.download.receipt()["completed"] is True
                        await current.return_control(desktop)
                        resumed = Script("positive")
                        resumed.requests = 3
                        async with AsyncOpenAI(
                            api_key="synthetic-local",
                            base_url="http://local.invalid/",
                            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(resumed.request)),
                            max_retries=0,
                        ) as other:
                            await current.agent_phase(desktop, other, "")
                        assert current.disclosed and approvals == 2
                    assert current.download.stats["requests"] == current.server.results == current.server.routes == 1
                    assert not (current.download.area / "phase.json").exists()
                    return {
                        "case": mode,
                        "requests": current.requests,
                        "routes": 1,
                        "results": 1,
                        "disclosed": current.disclosed,
                        "status": current.proof({})["status"],
                    }
    finally:
        body_release.set()
        release.set()
        desktop.stop()


async def terminal_handoff() -> dict[str, object]:
    """Exercise the actual terminal reader with a private pseudo-terminal."""
    master, slave = pty.openpty()
    terminal = Terminal()
    desktop = cast(Desktop, SimulatedLease())
    script = Script("positive")

    async def until(condition: Callable[[], bool]) -> None:
        async def observe() -> None:
            while not condition():
                await asyncio.sleep(0.01)

        await asyncio.wait_for(observe(), 12)

    with os.fdopen(slave, "r") as reader, patch("sys.stdin", reader):
        terminal.start()
        try:
            async with (
                open_mixed(terminal.ask) as current,
                AsyncOpenAI(
                    api_key="synthetic-local",
                    base_url="http://local.invalid/",
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(script.request)),
                    max_retries=0,
                ) as client,
            ):
                terminal.session, terminal.desktop = current, desktop
                phase = asyncio.create_task(current.agent_phase(desktop, client, ""))
                await until(lambda: terminal.pending is not None)
                os.write(master, b"take\n")
                await until(lambda: current.owner == "human")
                result = await asyncio.gather(phase, return_exceptions=True)
                assert isinstance(result[0], ToolRunnerError)
                assert current.server.routes == current.server.results == 0
                assert terminal.pending is None and current.settled.is_set()
                # A stale yes has no prompt to authorize. New human input needs
                # the fresh original-target check and its own approval.
                os.write(master, b"yes\n")
                await asyncio.sleep(0.04)
                assert current.server.routes == 0
                os.write(master, b"host route\n")
                await until(lambda: terminal.pending is not None)
                assert current.server.routes == 0
                os.write(master, b"yes\n")
                await until(lambda: current.server.browser_routed)
                assert current.server.routes == 1 and current.server.results == 0
                os.write(master, b"stop\n")
                await until(terminal.stopped.is_set)
                assert current.owner == "stopped" and current.settled.is_set()
                return {"case": "terminal_actual_reader", "routes": 1, "results": 0, "requests": current.requests}
        finally:
            await terminal.close()
            desktop.stop()
            os.close(master)


async def resume_snapshot(mode: str) -> dict[str, object]:
    """The model uses its new phase input directly; no extra read supplies its ref."""
    desktop = cast(Desktop, SimulatedLease())
    first, resumed = Script("positive"), Script(mode)
    entered = asyncio.Event()
    approvals = 0

    async def approve(label: str) -> bool:
        nonlocal approvals
        assert label.startswith("Host"), "Only the fixed Route may need approval in this check"
        approvals += 1
        if approvals == 1:
            entered.set()
            await asyncio.Event().wait()
        return True

    try:
        async with (
            open_mixed(approve) as current,
            AsyncOpenAI(
                api_key="synthetic-local",
                base_url="http://local.invalid/",
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(first.request)),
                max_retries=0,
            ) as before,
            AsyncOpenAI(
                api_key="synthetic-local",
                base_url="http://local.invalid/",
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(resumed.request)),
                max_retries=0,
            ) as after,
        ):
            assert current.download is not None
            area = current.download.area
            active = asyncio.create_task(current.agent_phase(desktop, before, ""))
            await asyncio.wait_for(entered.wait(), 12)
            assert current.server.routes == current.server.results == 0
            await current.take(desktop)
            result = (await asyncio.gather(active, return_exceptions=True))[0]
            assert isinstance(result, ToolRunnerError) and current.owner == "human"
            budget = current.requests
            assert budget == first.requests and current.server.routes == 0
            resumed.ref = first.ref
            await current.return_control(desktop)
            assert current.owner == "agent" and current.server.routes == 0
            result = (await asyncio.gather(current.agent_phase(desktop, after, ""), return_exceptions=True))[0]
            assert current.requests == budget + resumed.requests <= 20
            assert approvals == 2
            if mode == "resume_stale":
                assert isinstance(result, ToolRunnerError) and current.reason == "unverified"
                assert current.server.routes == 0 and not current.server.browser_routed
            else:
                assert not isinstance(result, BaseException)
                assert current.server.routes == 1 and current.server.browser_routed
            assert current.server.results == 0 and not current.disclosed
            report: dict[str, object] = {
                "case": mode,
                "requests": current.requests,
                "routes": current.server.routes,
                "results": current.server.results,
                "approvals": approvals,
            }
        assert not area.exists()
        return report
    finally:
        desktop.stop()


async def launcher_stop(mode: str) -> dict[str, object]:
    """Drive the real launcher lifetime through Stop on a human-owned HTTP request."""
    master, slave = pty.openpty()
    terminal = Terminal()
    desktop = SimulatedLease()
    script = Script("positive")
    body_entered, body_release = Event(), Event()
    captured = io.StringIO()
    reply = Handler.reply

    async def until(condition: Callable[[], bool]) -> None:
        async def observe() -> None:
            while not condition():
                await asyncio.sleep(0.01)

        await asyncio.wait_for(observe(), 12)

    def held_body(
        handler: Handler, code: int, body: bytes = b"", content_type: str = "application/octet-stream"
    ) -> None:
        if handler.path.startswith("/result/"):
            body_entered.set()
            if not body_release.wait(3):
                handler.close_connection = True
                return
        reply(handler, code, body, content_type)

    async def launch() -> int:
        try:
            await run_mixed.main()
        except SystemExit as exc:
            return int(str(exc.code))
        return 0

    api = AsyncOpenAI(
        api_key="synthetic-local",
        base_url="http://local.invalid/",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(script.request)),
        max_retries=0,
    )
    with (
        os.fdopen(slave, "r") as reader,
        patch("sys.stdin", reader),
        patch("sys.stdout", captured),
        patch("sys.argv", ["run_mixed.py", "--live", "--runtime-dir", "/synthetic-unused"]),
        patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic-local", "OPENAI_MODEL": "unused-for-synthetic-http"}),
        patch.object(run_mixed, "Terminal", return_value=terminal),
        patch.object(run_mixed, "Desktop", return_value=desktop),
        patch.object(run_mixed, "AsyncOpenAI", return_value=api),
        patch.object(Handler, "reply", held_body),
    ):
        task = asyncio.create_task(launch())
        try:
            await until(lambda: terminal.pending is not None)
            os.write(master, b"yes\n")
            await until(lambda: terminal.session is not None and terminal.pending is not None)
            current = terminal.session
            assert current is not None and current.download is not None
            area = current.download.area
            os.write(master, b"take\n")
            await until(lambda: current.owner == "human")
            os.write(master, b"host route\n")
            await until(lambda: terminal.pending is not None)
            os.write(master, b"yes\n")
            await until(lambda: current.server.browser_routed and current.settled.is_set())
            os.write(master, b"host receipt\n")
            await until(lambda: terminal.pending is not None)
            os.write(master, b"yes\n")
            assert await asyncio.to_thread(body_entered.wait, 8)
            assert current.server.results == current.download.stats["requests"] == 1
            assert current.download.state()["current"] == {"status": "in_progress", "effect": "unknown"}
            assert not current.settled.is_set()
            os.write(master, b"stop\n")
            await until(terminal.stopped.is_set)
            await asyncio.sleep(0.08)
            assert '{"status":' not in captured.getvalue(), "Launcher printed before the human transfer settled"
            assert not task.done()
            if mode == "confirmed":
                body_release.set()
            assert await asyncio.wait_for(task, 12) == 1
            body_release.set()
            text = captured.getvalue()
            start = text.index('{"status":')
            proof, _ = json.JSONDecoder().raw_decode(text[start:])
            expected = "completed" if mode == "confirmed" else "unknown"
            assert proof["download"]["current"] == {"status": expected, "effect": expected}, proof
            assert proof["download"]["cleanup"] == "completed", proof
            assert current.download.stats["requests"] == current.server.results == current.server.routes == 1
            assert current.settled.is_set() and desktop.stopped and not area.exists()
            assert not current.disclosed and proof["approved_document"] is False
            return {
                "case": "launcher_stop_human_" + mode,
                "status": proof["status"],
                "transfer": proof["download"]["current"],
                "cleanup": proof["download"]["cleanup"],
                "routes": current.server.routes,
                "results": current.server.results,
                "guest": False,
            }
        finally:
            body_release.set()
            terminal.stop()
            await asyncio.gather(task, return_exceptions=True)
            os.close(master)


async def disclosure_keys() -> None:
    for disclosed in (False, True):
        for keys in (["CTRL", "A"], ["CTRL", "S"]):
            prompts: list[str] = []

            async def approve(description: str, current_prompts: list[str] = prompts) -> bool:
                current_prompts.append(description)
                return True

            async with open_mixed(approve) as current:
                current.disclosed = disclosed
                allowed = await current.before_action(Keypress(type="keypress", keys=keys))
                assert allowed is disclosed
                assert current.native_approved is disclosed
                assert len(prompts) == (1 if disclosed else 0)
                if not disclosed:
                    assert current.reason == "refused" and current.owner == "stopped"


async def authorization_cleanup() -> None:
    contexts: list[BrowserContext] = []

    class SetupFailure(RuntimeError):
        pass

    async def fail(_self: Dispatch, context: BrowserContext) -> None:
        contexts.append(context)
        raise SetupFailure("Controlled workspace authorization failure")

    async def approve(_description: str) -> bool:
        return True

    with patch.object(Dispatch, "authorize", fail):
        try:
            async with open_mixed(approve):
                raise AssertionError("Workspace setup unexpectedly succeeded")
        except SetupFailure:
            pass
    assert len(contexts) == 1
    try:
        await contexts[0].new_page()
    except Error:
        pass
    else:
        raise AssertionError("Failed authorization leaked its browser context")

    stopped = asyncio.Event()
    contexts.clear()
    closed_during_setup = False

    async def during_authorize(_self: Dispatch, context: BrowserContext) -> None:
        nonlocal closed_during_setup
        contexts.append(context)
        closed = asyncio.Event()
        context.on("close", lambda _context: closed.set())
        stopped.set()
        try:
            await asyncio.wait_for(closed.wait(), 1)
        except asyncio.TimeoutError:
            pass
        closed_during_setup = closed.is_set()

    with patch.object(Dispatch, "authorize", during_authorize):
        try:
            async with open_mixed(approve, setup_stopped=stopped):
                raise AssertionError("Stop during setup published a mixed workspace")
        except (Error, BrowserCancelledError):
            pass
    assert len(contexts) == 1
    assert closed_during_setup, "Stop must close the owned browser during the held setup await"
    try:
        await contexts[0].new_page()
    except Error:
        pass
    else:
        raise AssertionError("Stop during authorization left the context open")

    class Verifier:
        def __init__(self) -> None:
            self.entered = Event()
            self.release = Event()

        def verify(self, *, cancelled: Callable[[], bool] | None = None) -> dict[str, object]:
            del cancelled
            self.entered.set()
            assert self.release.wait(4)
            return {"file_matches": True, "file_empty": False, "browser_matches": False, "browser_effects": 0}

    async with open_mixed(approve) as current:
        verifier = Verifier()
        checking = asyncio.create_task(current.verify(cast(Desktop, verifier)))
        try:
            assert await asyncio.to_thread(verifier.entered.wait, 2)
            current.stop()
        finally:
            verifier.release.set()
        observed = await checking
        assert observed["status"] == "stopped"
        assert observed["guest_editor"] is True, "A settled guest observation survives Stop"
        assert observed["host_browser"] is False and observed["approved_document"] is False
        assert current.settled.is_set()

    async with open_mixed(approve) as current:
        started = asyncio.Event()
        interrupted = asyncio.Event()

        async def held(_request: httpx2.Request) -> httpx2.Response:
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                interrupted.set()
                raise
            raise AssertionError("A disconnected browser cannot complete a held request")

        async with AsyncOpenAI(
            api_key="local-noncredential",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(held)),
        ) as client:
            driver = SimulatedInput()
            phase = asyncio.create_task(
                current.run(AsyncComputerToolset(cast(AsyncComputerDriver, driver)), client, "fixture")
            )
            await started.wait()
            owned_browser = current.driver.context.browser
            assert owned_browser is not None
            await owned_browser.close()
            done, pending = await asyncio.wait({phase}, timeout=2)
            assert not pending and phase in done, "Browser loss must promptly settle the active request"
            try:
                phase.result()
            except (ToolRunnerError, asyncio.CancelledError):
                pass
            else:
                raise AssertionError("Browser loss must abort the active request")
            assert interrupted.is_set()
            assert current.reason == "browser_closed"
            assert current.server.routes == 0


async def main() -> None:
    await disclosure_keys()
    await authorization_cleanup()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path)
    parser.add_argument(
        "--handoff", action="store_true", help="Exercise Take/Return with held real browser or receipt work"
    )
    parser.add_argument("--launcher-stop", action="store_true", help="Check the terminal Stop and final transfer proof")
    args = parser.parse_args()
    # Do not consume or forward any caller credential into the synthetic API.
    modes = (
        ("positive", "deny_native")
        if args.runtime_dir
        else (
            "positive",
            "deny_browser",
            "deny_file",
            "deny_native",
            "wrong_case",
            "extra_path",
            "extra_url",
            "navigation",
            "digest",
            "unknown",
            "redirect",
            "held_stop",
            "native_path",
            "wrong_ref",
        )
    )
    if args.launcher_stop:
        results = [await asyncio.wait_for(launcher_stop(mode), 40) for mode in ("confirmed", "deadline")]
    elif args.handoff:
        tests = (
            ("before_receipt", "after_receipt")
            if args.runtime_dir
            else (
                "before_receipt",
                "after_receipt",
                "route_before",
                "route_after",
                "expired",
                "stop_in_human",
            )
        )
        results = [await asyncio.wait_for(handoff(mode, args.runtime_dir), 120) for mode in tests]
        results.append(await asyncio.wait_for(human_budget(args.runtime_dir), 120))
        if not args.runtime_dir:
            for mode in ("before_disclosure", "stop_transfer"):
                results.append(await asyncio.wait_for(transfer_interrupt(mode), 35))
            results.append(await asyncio.wait_for(terminal_handoff(), 35))
            for mode in ("resume_snapshot", "resume_stale"):
                results.append(await asyncio.wait_for(resume_snapshot(mode), 35))
    else:
        results = [await check(mode, args.runtime_dir) for mode in modes]
    print(json.dumps({"cases": results, "count": len(results), "guest": bool(args.runtime_dir)}))


if __name__ == "__main__":
    asyncio.run(main())
