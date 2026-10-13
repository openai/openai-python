"""One Fieldwork run over an owned host fixture and a separate fixed Linux guest."""

from __future__ import annotations

import os
import json
import asyncio
import secrets
from typing import TYPE_CHECKING, Any, cast
from email.message import Message
from collections.abc import Mapping, Callable
from typing_extensions import override

from runner import Reply, MixedHostInputRefusedError, now, failure
from file_state import wait_for_decision
from file_download import DownloadOwner, digest, milliseconds
from browser_driver import PlaywrightBrowser, origin
from desktop_workspace import DesktopWorkspace, input_action
from playwright.async_api import ElementHandle, WebSocketRoute

from openai import AsyncOpenAI
from openai.lib.browser import (
    TabInput,
    ClickInput,
    BrowserError,
    BrowserState,
    BrowserReadV1,
    ReadPageInput,
    AsyncBrowserDriver,
    AsyncBrowserToolset,
    BrowserConfirmContext,
)
from openai.lib.computer import ComputerActionInput, AsyncComputerToolset
from openai.types.responses import Response, ResponseComputerToolCall
from openai.lib.responses_tool_runner import (
    AsyncRegisteredFunction,
    ResponsesToolCheckpoint,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)
from openai.types.responses.function_tool_param import FunctionToolParam

if TYPE_CHECKING:
    from runner import Run

RECEIPT = b"Desktop receipt D-2201"
INSTRUCTION = (
    "There are TWO DIFFERENT workspaces. Use browser_* tools ONLY on the Host browser dispatch page. "
    "Read and route case D-2201 there, then call approved_receipt with the observed case_id. "
    "Native computer screenshots and coordinates refer ONLY to the isolated guest desktop. "
    "Enter the approved receipt in the open editor on the RIGHT and save with Ctrl+S. "
    "Never use the guest browser on the left. Stop after saving."
)
RULE: FunctionToolParam = {
    "type": "function",
    "name": "approved_receipt",
    "strict": True,
    "description": "After routing D-2201 in the Host browser, fetch and disclose the one approved public receipt.",
    "parameters": {
        "type": "object",
        "properties": {"case_id": {"type": "string"}},
        "required": ["case_id"],
        "additionalProperties": False,
    },
}


class MixedWorkspace(DesktopWorkspace):
    def __init__(self, run: Run) -> None:
        super().__init__(run)
        self.selected = "host"
        self.selection = 0
        self.routes = 0
        self.results = 0
        self.result_path = "/result/" + secrets.token_hex(24)
        self.routed = False
        self.disclosed = False
        self.route_ref: str | None = None
        self.route_handle: ElementHandle | None = None
        self.checked_route = False
        self.download: DownloadOwner | None = None
        self.grant: dict[str, str] | None = None
        self.receiving = False

    @override
    async def initialize(self) -> None:
        run = self.run
        context = await run.app.browser.new_context(
            run=run, viewport={"width": 1024, "height": 768}, service_workers="block", accept_downloads=False
        )
        run.context = context
        if run.owner != "agent" or run.phase_cancel.is_set():
            await run.close_owned(context.close)
            return
        await context.add_cookies(
            [
                {
                    "name": "fieldwork_workspace",
                    "value": run.workspace_token,
                    "url": run.app.origin,
                    "httpOnly": True,
                    "sameSite": "Strict",
                }
            ]
        )
        url = run.app.origin + "/dispatch"
        run.driver = PlaywrightBrowser(
            context, {origin(url)}, owned_fixture_urls=frozenset({url, run.app.origin + "/route"})
        )
        await context.route("**/*", run.driver.guard)

        async def refuse_socket(route: WebSocketRoute) -> None:
            await route.close()

        await context.route_web_socket("**/*", refuse_socket)

        def closed(*_args: object) -> None:
            if run.owner != "stopped":
                run.stop("browser_closed")

        context.once("close", closed)
        await run.driver.new_tab({"url": url})
        run.task_tab, run.task_page = run.driver.page(None)
        self.route_handle = await run.task_page.locator("#route").element_handle()
        if not self.route_handle:
            raise BrowserError("Original dispatch control is missing.")

        async def approve_file(_prepared: Mapping[str, object]) -> bool:
            point = self.binding()
            approved = await run.ask("Fetch the one local public receipt and show its text to the model")
            return approved and self.matches(point) and run.owner == "agent" and not run.phase_cancel.is_set()

        created = await DownloadOwner.create(
            run.task_page,
            {
                "allow_download": True,
                "record": await run.task_page.locator('[data-record-id="result-case"]').element_handle(),
                "control": await run.task_page.locator("button[data-result]").element_handle(),
                "record_id": "result-case",
            },
            approve_file,
        )
        if run.closed or run.owner != "agent" or run.phase_cancel.is_set():
            await run.close_owned(created.stop)
            return
        self.download = created
        await super().initialize()

    @override
    async def retire(self) -> None:
        try:
            if self.download:
                await self.download.stop()
        finally:
            await super().retire()

    @override
    def binding(self) -> dict[str, Any] | None:
        basic = super().binding()
        if not basic or not self.run.task_tab:
            return None
        return {**basic, "tabId": self.run.task_tab, "view": self.selected, "sequence": self.selection}

    @override
    def matches(self, binding: dict[str, Any] | None) -> bool:
        point = self.binding()
        if not binding or not point or not super().matches(binding):
            return False
        return all(binding.get(name) == point[name] for name in ("tabId", "view", "sequence"))

    @override
    async def frame(self, *, cancelled: Callable[[], bool] | None = None) -> None:
        if self.selected == "guest":
            await super().frame(cancelled=cancelled)
            return
        point = self.binding()
        if not point:
            return
        assert self.run.task_page is not None
        page = self.run.task_page
        pixels = await wait_for_decision(lambda: page.screenshot(type="png"), cancelled)
        if not (cancelled and cancelled()) and self.matches(point):
            run = self.run
            run.frame, run.view_binding = pixels, point
            run.view = {
                "status": "live",
                "sequence": run.view["sequence"] + 1,
                "at": now(),
                "width": 1024,
                "height": 768,
            }

    async def select(self, selected: str) -> None:
        self.selected = selected
        self.selection += 1
        self.run.view_binding = self.run.frame = None
        await self.run.refresh_view()

    async def fixture(
        self, method: str, path: str, headers: Message[str, str] | Mapping[str, str], body: bytes
    ) -> Reply:
        run = self.run
        if method == "GET" and path == "/dispatch":
            from pathlib import Path

            page = (Path(__file__).resolve().parents[1] / "browser" / "mixed-fixture.html").read_bytes()
            return Reply(
                200,
                page,
                {
                    "Content-Type": "text/html; charset=utf-8",
                    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'",
                },
            )
        if method == "POST" and path == "/route":
            try:
                value = json.loads(body)
            except (ValueError, UnicodeDecodeError):
                value = None
            if (
                headers.get("Origin") != run.app.origin
                or not self.checked_route
                or self.routes
                or value != {"case_id": "D-2201", "action": "route"}
            ):
                return failure(403, "No matching dispatch control.")
            self.routes += 1
            return Reply(204, b"", {})
        if method == "GET" and (path == "/result" or path.startswith("/result/")):
            if (
                path != self.result_path
                or not self.receiving
                or not self.routed
                or self.routes != 1
                or self.results != 0
                or run.owner != "agent"
                or run.phase_cancel.is_set()
            ):
                return failure(403, "No matching receipt.")
            self.results += 1
            return Reply(200, RECEIPT, {"Content-Type": "application/octet-stream"})
        return failure(404, "Unknown route.")

    @override
    async def proof(self, *, cancelled: Callable[[], bool] | None = None, finalize: bool = False) -> dict[str, Any]:
        assert self.guest is not None
        phase = self.run.phase_cancel if self.run.owner == "agent" else None
        read = self.guest.seal if finalize else self.guest.verify
        result = await asyncio.to_thread(read, cancelled=cancelled or (phase.is_set if phase else None))
        verified = (
            self.routed
            and self.routes == 1
            and self.results == 1
            and self.disclosed
            and result["file_matches"] is True
            and result["browser_matches"] is False
            and result["browser_effects"] == 0
        )
        return {
            "revision": self.routes,
            "finished": finalize or bool(verified),
            "verified": bool(verified),
            "results": {
                "host_routes": self.routes,
                "receipts": self.results,
                "disclosed": self.disclosed,
                "guest_browser_effects": result["browser_effects"],
                "file_matches": result["file_matches"],
            },
        }

    async def state(self) -> BrowserState:
        assert self.run.driver is not None
        return await self.run.driver.state()

    async def read_page(self, args: ReadPageInput) -> BrowserReadV1:
        if args.get("tab_id") not in (None, self.run.task_tab):
            raise BrowserError("Read the fixed Host dispatch tab.")
        assert self.run.driver is not None
        result = await self.run.driver.read_page(args)
        assert not isinstance(result, str)
        matches = [item for item in result["elements"] if item["role"] == "button" and item["label"] == "Route D-2201"]
        self.route_ref = matches[0]["ref"] if len(matches) == 1 else None
        return result

    async def get_page_text(self, args: TabInput) -> str | BrowserReadV1:
        assert self.run.driver is not None
        return await self.run.driver.get_page_text(args)

    async def click(self, args: ClickInput) -> None:
        run = self.run
        if (
            self.routed
            or args.get("target") != self.route_ref
            or not self.route_ref
            or args.get("tab_id") not in (None, run.task_tab)
            or run.owner not in ("agent", "human", "draining-to-agent")
        ):
            raise BrowserError("Read and select the original Host Route control.")
        assert run.driver is not None and run.task_page is not None
        original = await run.driver._target(self.route_ref, run.task_tab)
        if not await original.evaluate("(target, original) => target === original", self.route_handle):
            raise BrowserError("The original Route control was replaced.")
        self.checked_route = True
        try:
            await run.driver.click(args)
            await run.task_page.locator("button[data-result]:enabled").wait_for(timeout=2000)
            if self.routes != 1:
                raise BrowserError("No matching local dispatch receipt.")
            self.routed = True
        finally:
            self.checked_route = False

    async def receipt(self, args: dict[str, Any]) -> str:
        run = self.run
        if (
            args != {"case_id": "D-2201"}
            or not self.routed
            or self.routes != 1
            or self.disclosed
            or not self.download
            or run.phase_cancel.is_set()
            or run.owner != "agent"
        ):
            raise BrowserError("Receipt request refused.")
        prior = self.download.receipt()
        if prior.get("completed") is True:
            point = self.binding()
            if not await run.ask("Show the already verified public receipt to the model") or not self.matches(point):
                raise BrowserError("Receipt disclosure refused.")
            result = prior
        else:
            if prior.get("attempted") or self.download.revoked:
                raise BrowserError("Receipt transfer needs reconciliation.")
            if not self.grant:
                self.grant = self.download.issue(
                    {"url": self.run.app.origin + self.result_path, "count": len(RECEIPT), "sha256": digest(RECEIPT)},
                    milliseconds() + 30000,
                )
            self.receiving = True
            try:
                result = json.loads(
                    await self.download.download(
                        {"grant_id": self.grant["grant_id"]}, cancelled=run.phase_cancel.is_set
                    )
                )
            finally:
                self.receiving = False
                transferred = self.download.receipt()
                if (
                    run.phase_cancel.is_set()
                    and transferred.get("status") == "refused"
                    and transferred.get("attempted") is False
                    and self.download.grant is None
                    and self.download.work is None
                    and not self.download.revoked
                    and self.download.state()["cleanup"] != "pending"
                ):
                    self.grant = None
        if (
            result.get("status") != "completed"
            or result.get("completed") is not True
            or result.get("count") != len(RECEIPT)
            or result.get("sha256") != digest(RECEIPT)
            or self.results != 1
            or run.phase_cancel.is_set()
            or run.owner != "agent"
        ):
            raise BrowserError("Receipt was not verified.")
        self.disclosed = True
        return RECEIPT.decode("ascii")

    def permits(self, action: dict[str, Any]) -> bool:
        if action["type"] in ("screenshot", "wait"):
            return True
        if action["type"] in ("click", "move"):
            return (
                512 <= action["x"] < 1024
                and 80 <= action["y"] < 768
                and (action["type"] != "click" or action["button"] == "left")
            )
        if action["type"] == "type":
            return self.disclosed and action["text"] == RECEIPT.decode("ascii")
        if action["type"] == "keypress":
            return self.disclosed and [key.upper() for key in action["keys"]] in (["CTRL", "A"], ["CTRL", "S"])
        return False

    def valid_input(self, body: dict[str, Any]) -> bool:
        rest = {name: value for name, value in body.items() if name not in ("tabId", "view", "sequence")}
        action = input_action(rest, self.scroll_target)
        if not action:
            return False
        if self.selected == "host":
            return action["type"] == "click" and not self.routed
        return self.permits(action)

    @override
    async def human_input(self, body: dict[str, Any]) -> None:
        if self.selected == "host":
            if not self.valid_input(body):
                raise ValueError("Choose the original Route control.")
            await self.read_page({"tab_id": self.run.task_tab, "filter": "all"})
            assert self.route_handle is not None and self.route_ref is not None
            box = await self.route_handle.bounding_box()
            if not box:
                raise ValueError("The original Host route control is unavailable.")
            if not (
                box["x"] <= body["x"] < box["x"] + box["width"] and box["y"] <= body["y"] < box["y"] + box["height"]
            ):
                raise MixedHostInputRefusedError()
            await self.click({"tab_id": self.run.task_tab, "target": self.route_ref})
            await self.run.capture()
        else:
            if not self.valid_input(body):
                raise ValueError("Choose an allowed bounded guest input.")
            await super().human_input(
                {name: value for name, value in body.items() if name not in ("tabId", "view", "sequence")}
            )

    @override
    async def execute(self, client: AsyncOpenAI) -> str:
        run = self.run
        assert self.download is not None and self.guest is not None
        download = self.download
        native_approved = False
        target = self.download.area / "phase.json"
        temporary = self.download.area / "phase-next.json"
        phase_id = f"mixed-{run.id}-{run.version}"
        run.phase_index += 1

        async def save(checkpoint: ResponsesToolCheckpoint) -> None:
            data = json.dumps(checkpoint, ensure_ascii=True, allow_nan=False).encode("ascii")
            with temporary.open("xb") as file:
                os.chmod(file.fileno(), 0o600)
                file.write(data)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, target)
            directory = os.open(download.area, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
            run.record(
                "tools",
                phaseIndex=run.phase_index,
                phase=checkpoint["phase"],
                attempted=len(checkpoint["attempted_call_ids"]),
                returned=len(checkpoint["returned_call_ids"]),
            )

        async def confirm(_context: BrowserConfirmContext) -> bool:
            point = self.binding()
            allowed = await run.ask("Host browser - route D-2201")
            return allowed and self.matches(point) and run.owner == "agent" and not run.phase_cancel.is_set()

        async def before_action(action: ComputerActionInput) -> bool:
            nonlocal native_approved
            if not self.permits(action.to_dict()) or run.phase_cancel.is_set() or run.owner != "agent":
                return False
            if action.type in ("screenshot", "wait"):
                return True
            if not native_approved:
                native_approved = await run.ask("Isolated desktop - enter the approved receipt in the editor")
            return native_approved and run.owner == "agent" and not run.phase_cancel.is_set()

        async def safety(_call: ResponseComputerToolCall) -> bool:
            return await run.ask("Approve the pending guest action flagged by the API safety check")

        async def phase(computer: AsyncComputerToolset) -> Response:
            read = await self.read_page({"tab_id": run.task_tab, "filter": "all"})
            image = await computer.driver.screenshot()
            assert "image_url" in image
            instruction = (
                INSTRUCTION
                + f" Host routed: {self.routed}; receipt disclosed: {self.disclosed}. "
                + (f"Already approved public receipt: {RECEIPT.decode('ascii')}. " if self.disclosed else "")
                + "Current Host browser: "
                + json.dumps(read)
            )
            runner = AsyncResponsesToolRunner(
                browser=AsyncBrowserToolset(
                    cast(AsyncBrowserDriver, self),
                    members=("list_tabs", "read_page", "get_page_text", "click"),
                    confirm=confirm,
                ),
                computer=computer,
                functions=[AsyncRegisteredFunction(tool=RULE, execute=self.receipt)],
            )
            model = run.app.models["responses"]
            assert model is not None
            return await runner.run(
                client,
                {
                    "model": model,
                    "store": False,
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": instruction},
                                {"type": "input_image", "image_url": image["image_url"], "detail": "auto"},
                            ],
                        }
                    ],
                },
                max_steps=run.step_limit - run.turns,
                cancelled=run.phase_cancel.is_set,
                on_diagnostic=run.diagnostics.event,
                ledger=AsyncResponsesToolLedger(run_id=phase_id, save=save),
                before_action=before_action,
                approve_safety_checks=safety,
            )

        try:
            await self.guest.operation_async(phase)
            final = await self.proof()
            if final["verified"]:
                final = await self.proof(finalize=True)
            run.result = "verified" if final["verified"] else "unverified"
            return run.result
        finally:

            async def close_ledger() -> None:
                temporary.unlink(missing_ok=True)
                target.unlink(missing_ok=True)

            await run.close_owned(close_ledger)
