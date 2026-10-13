"""One approved host-browser receipt and an isolated guest editor."""

from __future__ import annotations

import os
import json
import base64
import asyncio
import secrets
from typing import TYPE_CHECKING, Literal
from pathlib import Path
from threading import Lock, Thread
from contextlib import asynccontextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from collections.abc import Mapping, Callable, Awaitable, AsyncGenerator
from typing_extensions import override

from file_download import ELIGIBLE, DownloadOwner, digest, milliseconds
from browser_driver import PlaywrightBrowser, open_browser
from playwright.async_api import ElementHandle, BrowserContext

from openai import AsyncOpenAI
from openai.lib.browser import (
    TabInput,
    FindInput,
    ClickInput,
    BrowserState,
    BrowserReadV1,
    NavigateInput,
    ReadPageInput,
    AsyncBrowserToolset,
    BrowserCancelledError,
    BrowserConfirmContext,
)
from openai.lib.computer import ComputerUseError, ComputerActionInput, AsyncComputerToolset
from openai.types.responses import Response, FunctionToolParam, ResponseComputerToolCall, computer_action as modern
from openai.lib.responses_tool_runner import (
    AsyncRegisteredFunction,
    ResponsesToolCheckpoint,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)

if TYPE_CHECKING:
    from desktop import Desktop

PUBLIC_RECEIPT = b"Desktop receipt D-2201"
TASK = (
    "This synthetic dispatch task has TWO DIFFERENT workspaces. "
    "browser_* tools control only the Host browser Dispatch receipts page. Read and route case D-2201 there. "
    "Call approved_receipt with its observed case_id, then use native computer tools to save the returned text "
    "in the already open editor on the RIGHT of the isolated desktop. Use Ctrl+A and Ctrl+S there. "
    "Native computer screenshots and coordinates show ONLY the isolated desktop, never the Host browser. "
    "Do not use the browser on the LEFT of the guest; it belongs to a different task and must remain unchanged. "
    "Use no paths or other sites. Stop after saving."
)
RULE: FunctionToolParam = {
    "type": "function",
    "name": "approved_receipt",
    "description": "After routing in the Host browser, fetch and disclose the one approved public dispatch receipt.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {"case_id": {"type": "string"}},
        "required": ["case_id"],
        "additionalProperties": False,
    },
}
Approval = Callable[[str], Awaitable[bool]]


class Dispatch(ThreadingHTTPServer):
    """Actual local server receipts. Never treat a model's answer as its state."""

    daemon_threads = True

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), Handler)
        self.routes = 0
        self.results = 0
        self.result_lock = Lock()
        self.checked_click = False
        self.browser_routed = False
        self._workspace_token = secrets.token_urlsafe(32)
        self._result_path = "/result/" + secrets.token_urlsafe(32)
        self.thread = Thread(target=self.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}/dispatch"

    @property
    def result_url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}{self._result_path}"

    async def authorize(self, context: BrowserContext) -> None:
        await context.add_cookies(
            [
                {
                    "name": "mixed_workspace",
                    "value": self._workspace_token,
                    "url": self.url,
                    "httpOnly": True,
                    "sameSite": "Strict",
                }
            ]
        )

    def authorized(self, cookie: str) -> bool:
        return any(value.strip() == f"mixed_workspace={self._workspace_token}" for value in cookie.split(";"))

    def close(self) -> None:
        self.shutdown()
        self.server_close()
        self.thread.join(2)
        if self.thread.is_alive():
            raise RuntimeError("Dispatch server did not stop.")


class Handler(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def reply(self, code: int, body: bytes = b"", content_type: str = "application/octet-stream") -> None:
        self.send_response(code)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        assert isinstance(self.server, Dispatch)
        if self.path == self.server._result_path:
            with self.server.result_lock:
                available = self.server.routes == 1 and self.server.browser_routed and self.server.results == 0
                if available:
                    self.server.results += 1
            self.reply(200 if available else 409, PUBLIC_RECEIPT if available else b"")
        elif not self.server.authorized(self.headers.get("cookie", "")):
            self.reply(403)
        elif self.path == "/dispatch":
            self.reply(200, Path(__file__).with_name("mixed-fixture.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self.reply(404)

    def do_POST(self) -> None:
        assert isinstance(self.server, Dispatch)
        if not self.server.authorized(self.headers.get("cookie", "")):
            self.reply(403)
            return
        if self.path != "/route":
            self.reply(404)
            return
        try:
            length = int(self.headers.get("content-length", "-1"))
            if self.headers.get("content-type") != "application/json" or not 0 <= length <= 256:
                raise ValueError()
            body = json.loads(self.rfile.read(length))
            if body != {"case_id": "D-2201", "action": "route"} or not self.server.checked_click:
                raise ValueError()
        except (ValueError, OSError):
            self.reply(400)
            return
        if self.server.routes:
            self.reply(409)
        else:
            self.server.routes += 1
            self.reply(204)


class MixedSession:
    """One lifetime, including every complete agent and human desktop lease."""

    def __init__(self, server: Dispatch, driver: PlaywrightBrowser, route: ElementHandle, approve: Approval) -> None:
        self.server = server
        self.driver = driver
        self.route = route
        self.ask = approve
        self.stopping = asyncio.Event()
        self.phase_cancel = asyncio.Event()
        self.owner: Literal["agent", "draining", "human", "returning", "stopped"] = "agent"
        self.settled = asyncio.Event()
        self.settled.set()
        self.changed = asyncio.Event()
        self.phase = 0
        self.requests = 0
        self.attempted: set[str] = set()
        self.completed: set[str] = set()
        self.ledger: AsyncResponsesToolLedger | None = None
        self.reason: str | None = None
        self.active_run: asyncio.Task[Response] | None = None
        self.disclosed = False
        self.native_approved = False
        self.download: DownloadOwner | None = None
        self.grant_id: str | None = None

    def stop(self, reason: str = "stopped") -> None:
        if self.reason is None:
            self.reason = reason
        self.stopping.set()
        self.phase_cancel.set()
        self.owner = "stopped"
        self.changed.set()
        self.remove_snapshots()

    def remove_snapshots(self) -> None:
        if self.download is not None:
            for name in ("host.png", "guest.png"):
                (self.download.area / name).unlink(missing_ok=True)

    async def approval(self, workspace: str) -> bool:
        if self.stopping.is_set() or self.phase_cancel.is_set():
            return False
        pending = asyncio.ensure_future(self.ask(workspace))
        stopped = asyncio.create_task(self.phase_cancel.wait())
        try:
            done, _ = await asyncio.wait({pending, stopped}, return_when=asyncio.FIRST_COMPLETED)
            agreed = pending in done and pending.result() is True and not self.phase_cancel.is_set()
            if not agreed and not self.phase_cancel.is_set():
                self.stop("refused")
            return agreed
        finally:
            # Terminal approval must settle even if Stop arrives before input.
            pending.cancel()
            stopped.cancel()
            await asyncio.gather(pending, stopped, return_exceptions=True)

    async def state(self, *, cancelled: Callable[[], bool] | None = None) -> BrowserState:
        return await self.driver.state(cancelled=cancelled)

    async def click(self, action: ClickInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        """Grant the fixed POST only while the checked browser action owns it."""
        if self.phase_cancel.is_set() or self.stopping.is_set() or self.server.browser_routed:
            raise RuntimeError("Session stopped.")
        current = await self.driver._target(action["target"], action["tab_id"], cancelled=cancelled)
        if not await self.driver._observation(
            lambda: current.evaluate("(target, original) => target === original", self.route), cancelled
        ):
            self.stop("refused")
            raise ValueError("This receipt requires the original Route control.")
        if self.phase_cancel.is_set():
            raise RuntimeError("Session stopped.")
        self.server.checked_click = True
        try:
            await self.driver.click(action, cancelled=cancelled)
            _, page = self.driver.page(self.driver.active)
            await page.locator("button[data-result]:enabled").wait_for(timeout=2000)
            if self.server.routes != 1:
                raise RuntimeError("No matching dispatch receipt.")
            self.server.browser_routed = True
        finally:
            self.server.checked_click = False

    async def read_page(
        self, action: ReadPageInput, *, cancelled: Callable[[], bool] | None = None
    ) -> str | BrowserReadV1:
        return await self.driver.read_page(action, cancelled=cancelled)

    async def find(self, action: FindInput, *, cancelled: Callable[[], bool] | None = None) -> str | BrowserReadV1:
        return await self.driver.find(action, cancelled=cancelled)

    async def get_page_text(
        self, action: TabInput, *, cancelled: Callable[[], bool] | None = None
    ) -> str | BrowserReadV1:
        return await self.driver.get_page_text(action, cancelled=cancelled)

    async def navigate(self, action: NavigateInput, *, cancelled: Callable[[], bool] | None = None) -> str:
        return await self.driver.navigate(action, cancelled=cancelled)

    async def confirm(self, _context: BrowserConfirmContext) -> bool:
        return await self.approval("Host browser - route receipt")

    async def url_policy(self, _context: BrowserConfirmContext, url: str) -> bool:
        if url != self.server.url:
            self.stop("refused")
            return False
        return not self.phase_cancel.is_set()

    async def file_approval(self, _prepared: Mapping[str, object]) -> bool:
        return await self.approval("Local function - fetch this fixed public receipt AND show its text to the model")

    async def receipt(self, arguments: dict[str, object]) -> str:
        owner = self.download
        if (
            self.phase_cancel.is_set()
            or arguments != {"case_id": "D-2201"}
            or not self.server.browser_routed
            or self.server.routes != 1
            or self.disclosed
            or owner is None
        ):
            self.stop("refused")
            raise ValueError("Receipt request refused.")
        result = owner.receipt()
        if result.get("completed") is not True:
            if self.grant_id is None:
                self.grant_id = owner.issue(
                    {
                        "url": self.server.result_url,
                        "count": len(PUBLIC_RECEIPT),
                        "sha256": digest(PUBLIC_RECEIPT),
                    },
                    milliseconds() + 30_000,
                )["grant_id"]
            try:
                result = json.loads(
                    await owner.download({"grant_id": self.grant_id}, cancelled=self.phase_cancel.is_set)
                )
            finally:
                transferred = owner.receipt()
                if (
                    self.phase_cancel.is_set()
                    and transferred.get("status") == "refused"
                    and transferred.get("attempted") is False
                ):
                    # The download owner revoked this unused grant; Return needs fresh approval.
                    self.grant_id = None
        else:
            # A new phase cannot replay disclosure or repeat the HTTP transfer.
            if not await self.approval("Local function - disclose the already verified public receipt"):
                raise ValueError("Receipt disclosure refused.")
        if self.phase_cancel.is_set():
            if result.get("attempted") is True and result.get("completed") is not True:
                self.stop("unknown")
            raise ValueError("Receipt phase ended before disclosure.")
        if result.get("completed") is not True or self.server.results != 1:
            self.stop("refused" if result.get("attempted") is False else "unknown")
            raise ValueError("Receipt was not verified.")
        self.disclosed = True
        # Return the trusted public constant after verification; never open quarantine bytes.
        return PUBLIC_RECEIPT.decode("ascii")

    async def before_action(self, action: ComputerActionInput) -> bool:
        if self.phase_cancel.is_set():
            return False
        if action.type in {"screenshot", "wait"}:
            return True
        allowed = False
        if action.type == "click" or action.type == "move":
            allowed = (
                512 <= action.x < 1024 and 80 <= action.y < 768 and (action.type != "click" or action.button == "left")
            )
        elif action.type == "type":
            allowed = self.disclosed and action.text == PUBLIC_RECEIPT.decode("ascii")
        elif action.type == "keypress":
            allowed = self.disclosed and [key.upper() for key in action.keys] in (["CTRL", "A"], ["CTRL", "S"])
        if not allowed:
            self.stop("refused")
            return False
        if not self.native_approved:
            self.native_approved = await self.approval("Isolated desktop - enter the approved receipt in the editor")
        return self.native_approved and not self.phase_cancel.is_set()

    async def safety(self, _call: ResponseComputerToolCall) -> bool:
        return await self.approval("Isolated desktop - API requests a safety decision for the pending task action")

    async def run(self, computer: AsyncComputerToolset, client: AsyncOpenAI, model: str) -> Response:
        pending = asyncio.create_task(self._run(computer, client, model))
        self.active_run = pending
        try:
            return await pending
        finally:
            if self.active_run is pending:
                self.active_run = None

    async def _run(self, computer: AsyncComputerToolset, client: AsyncOpenAI, model: str) -> Response:
        if self.phase_cancel.is_set() or self.stopping.is_set():
            raise RuntimeError("Session stopped.")
        browser = AsyncBrowserToolset(
            self,
            members=("list_tabs", "read_page", "get_page_text", "find", "click", "navigate"),
            confirm=self.confirm,
            url_policy=self.url_policy,
        )
        runner = AsyncResponsesToolRunner(
            browser=browser,
            computer=computer,
            functions=[AsyncRegisteredFunction(tool=RULE, execute=self.receipt)],
        )
        # The original single-phase exercise can still call run() inside its lease.
        # The interactive launcher gives every phase fresh observations, never history.
        task = TASK
        if self.ledger is not None:
            read = await self.driver.read_page(
                {"tab_id": self.driver.active, "filter": "all"}, cancelled=self.phase_cancel.is_set
            )
            image = await computer.driver.screenshot()
            image_url = image.get("image_url")
            if not isinstance(image_url, str):
                raise ValueError("The guest returned no current image.")
            task += (
                f"\nPhase {self.phase}. Route verified: {self.server.browser_routed}. "
                f"Receipt already fetched: {self.download is not None and self.download.receipt().get('completed') is True}. "
                "If already routed, do not Route again. If the receipt was already disclosed, use it without calling approved_receipt again. "
                f"Current Host browser: {json.dumps(read)}"
            )
            if self.disclosed:
                task += f"\nPreviously approved and verified public receipt: {PUBLIC_RECEIPT.decode('ascii')}"
            return await runner.run(
                client,
                {
                    "model": model,
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": task},
                                {"type": "input_image", "image_url": image_url, "detail": "auto"},
                            ],
                        }
                    ],
                    "store": False,
                },
                max_steps=20 - self.requests,
                cancelled=self.phase_cancel.is_set,
                ledger=self.ledger,
                before_action=self.before_action,
                approve_safety_checks=self.safety,
            )
        return await runner.run(
            client,
            {"model": model, "input": TASK, "store": False},
            max_steps=20,
            cancelled=self.phase_cancel.is_set,
            before_action=self.before_action,
            approve_safety_checks=self.safety,
        )

    async def agent_phase(self, desktop: Desktop, client: AsyncOpenAI, model: str) -> Response:
        if self.owner != "agent" or not self.settled.is_set() or self.requests >= 20 or self.download is None:
            self.stop("request_limit" if self.requests >= 20 else "stopped")
            raise RuntimeError("No agent phase can be admitted.")
        self.settled.clear()
        self.phase += 1
        self.native_approved = False
        seen_requests = 0
        target = self.download.area / "phase.json"
        temporary = self.download.area / "phase-next.json"

        async def save(checkpoint: ResponsesToolCheckpoint) -> None:
            nonlocal seen_requests
            # A ledger callback commits the full private checkpoint before reporting
            # admission. Raw histories are never exported or reused after a handoff.
            data = json.dumps(checkpoint, ensure_ascii=True, allow_nan=False).encode("ascii")
            with temporary.open("xb") as file:
                os.chmod(temporary, 0o600)
                file.write(data)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, target)
            directory = os.open(self.download.area if self.download else target.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
            count = checkpoint["consumed_requests"]
            self.requests += count - seen_requests
            seen_requests = count
            self.attempted.update(f"{self.phase}:{value}" for value in checkpoint["attempted_call_ids"])
            self.completed.update(f"{self.phase}:{value}" for value in checkpoint["returned_call_ids"])

        self.ledger = AsyncResponsesToolLedger(run_id=f"mixed-phase-{self.phase}", save=save)
        try:
            return await desktop.operation_async(lambda computer: self.run(computer, client, model))
        except BaseException:
            if desktop.uncertain_effects:
                self.stop("unknown")
            elif self.owner == "agent":
                self.stop("unverified")
            raise
        finally:
            self.ledger = None
            temporary.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
            self.settled.set()

    def agent_owns(self) -> bool:
        return self.owner == "agent" and not self.stopping.is_set()

    async def verify(self, desktop: Desktop) -> dict[str, object]:
        if not self.agent_owns() or not self.settled.is_set():
            raise ValueError("Verification requires the settled original owner.")
        self.settled.clear()
        try:
            result = self.proof(await asyncio.to_thread(desktop.verify, cancelled=self.phase_cancel.is_set))
            if result["status"] == "verified" and self.agent_owns() and not self.phase_cancel.is_set():
                result = self.proof(await asyncio.to_thread(desktop.seal, cancelled=self.phase_cancel.is_set))
            if not self.agent_owns() or self.phase_cancel.is_set():
                result["status"] = self.reason or "unverified"
            return result
        except ComputerUseError:
            if not self.phase_cancel.is_set():
                raise
            return self.proof({})
        finally:
            self.settled.set()

    async def reconcile(self, desktop: Desktop) -> None:
        download = self.download
        if download is None or desktop.uncertain_effects or download.receipt().get("status") == "unknown":
            self.stop("unknown")
            raise RuntimeError("An effect cannot be reconciled.")
        try:
            _, page = self.driver.page(self.driver.active)
            if (
                page.url != self.server.url
                or not await self.route.evaluate(
                    "(button) => button.isConnected && button.ownerDocument===document && button.id==='route'"
                )
                or (self.server.routes != int(self.server.browser_routed))
                or (
                    self.server.browser_routed
                    and not await download.control.evaluate(
                        ELIGIBLE, [download.document, download.record, download.record_id]
                    )
                )
                or (download.grant is not None and download.grant["expires_at"] <= milliseconds())
            ):
                raise ValueError()
            await self.driver.invalidate_references()
        except Exception:
            self.stop("unverified")
            raise RuntimeError("Original browser, receipt or grant is no longer eligible.") from None

    async def drain(self, desktop: Desktop) -> None:
        try:
            await asyncio.wait_for(self.settled.wait(), 5)
            await self.reconcile(desktop)
        except Exception:
            if not self.stopping.is_set():
                self.stop("unknown")
            await asyncio.to_thread(desktop.stop)
            raise

    async def take(self, desktop: Desktop) -> None:
        if self.owner != "agent" or self.stopping.is_set():
            raise ValueError("Take is unavailable.")
        self.owner = "draining"
        self.phase_cancel.set()
        await self.drain(desktop)
        if self.owner != "draining":
            raise RuntimeError("Take stopped.")
        self.phase_cancel = asyncio.Event()
        self.native_approved = False
        self.owner = "human"
        self.changed.set()

    async def return_control(self, desktop: Desktop) -> None:
        if self.owner != "human" or self.stopping.is_set():
            raise ValueError("Return is unavailable.")
        self.owner = "returning"
        self.phase_cancel.set()
        self.remove_snapshots()
        await self.drain(desktop)
        if self.owner != "returning":
            raise RuntimeError("Return stopped.")
        self.phase_cancel = asyncio.Event()
        self.native_approved = False
        self.owner = "agent"
        self.changed.set()

    async def human(self, desktop: Desktop, command: str) -> tuple[Path, Path] | None:
        if self.owner != "human" or not self.settled.is_set() or self.phase_cancel.is_set() or self.download is None:
            raise ValueError("Human input is unavailable until the active lease has settled.")
        self.settled.clear()
        try:

            async def work(computer: AsyncComputerToolset) -> tuple[Path, Path] | None:
                if command == "view":
                    _, page = self.driver.page(self.driver.active)
                    host = await page.screenshot(type="png")
                    guest = await computer.driver.screenshot()
                    image_url = guest.get("image_url")
                    if not isinstance(image_url, str) or not image_url.startswith("data:image/png;base64,"):
                        raise ValueError("The guest returned no current PNG.")
                    if self.owner != "human" or self.phase_cancel.is_set() or self.download is None:
                        raise RuntimeError("The view is no longer current.")
                    host_path, guest_path = self.download.area / "host.png", self.download.area / "guest.png"
                    self.remove_snapshots()
                    for path, data in (
                        (host_path, host),
                        (guest_path, base64.b64decode(image_url.removeprefix("data:image/png;base64,"), validate=True)),
                    ):
                        with path.open("xb") as file:
                            os.chmod(path, 0o600)
                            file.write(data)
                    return host_path, guest_path
                if command == "host route":
                    read = await self.driver.find({"query": "Route D-2201", "tab_id": self.driver.active})
                    if not isinstance(read, dict) or len(read["elements"]) != 1:
                        raise ValueError("The original Route is unavailable.")
                    if not await self.approval("Host browser - route receipt"):
                        raise ValueError("Route approval declined.")
                    await self.click({"tab_id": self.driver.active, "target": read["elements"][0]["ref"]})
                    return None
                if command == "host receipt":
                    await self.receipt({"case_id": "D-2201"})
                    return None
                words = command.split()
                if len(words) == 4 and words[:2] == ["guest", "click"]:
                    action: ComputerActionInput = modern.Click(
                        type="click", button="left", x=int(words[2]), y=int(words[3])
                    )
                elif command == "guest type":
                    action = modern.Type(type="type", text=PUBLIC_RECEIPT.decode("ascii"))
                elif command in {"guest select-all", "guest save"}:
                    action = modern.Keypress(
                        type="keypress", keys=["CTRL", "A" if command == "guest select-all" else "S"]
                    )
                else:
                    raise ValueError("Unknown human command.")
                if not await self.before_action(action):
                    raise ValueError("Guest input refused.")
                if action.type == "click":
                    await computer.driver.click(action)
                elif action.type == "type":
                    await computer.driver.type(action)
                elif action.type == "keypress":
                    await computer.driver.keypress(action)
                return None

            return await desktop.operation_async(work)
        except BaseException:
            if desktop.uncertain_effects:
                self.stop("unknown")
            raise
        finally:
            self.settled.set()

    def proof(self, guest: dict[str, object]) -> dict[str, object]:
        download = self.download.state() if self.download else None
        host = self.server.browser_routed and self.server.routes == 1
        document = (
            download is not None
            and download["current"] == {"status": "completed", "effect": "completed"}
            and self.server.results == 1
            and self.disclosed
        )
        saved = (
            guest.get("file_matches") is True
            and guest.get("file_empty") is False
            and guest.get("browser_matches") is False
            and guest.get("browser_effects") == 0
        )
        return {
            "status": self.reason or ("verified" if host and document and saved else "unverified"),
            "host_browser": host,
            "approved_document": document,
            "guest_editor": saved,
            "download": download,
            "requests": self.requests,
            "attempted_call_ids": sorted(self.attempted),
            "completed_call_ids": sorted(self.completed),
        }


@asynccontextmanager
async def open_mixed(approve: Approval, *, setup_stopped: asyncio.Event | None = None) -> AsyncGenerator[MixedSession]:
    server = Dispatch()
    origin = server.url.removesuffix("/dispatch")
    try:
        async with open_browser(
            server.url,
            handle_sigint=False,
            owned_fixture_urls=frozenset({server.url, origin + "/route"}),
            context_setup=server.authorize,
            setup_stopped=setup_stopped,
        ) as driver:
            _, page = driver.page(driver.active)

            async def retire_setup() -> None:
                assert setup_stopped is not None
                await setup_stopped.wait()
                await driver.context.close()

            retirement = asyncio.create_task(retire_setup()) if setup_stopped is not None else None
            session: MixedSession | None = None

            def disconnected(*_args: object) -> None:
                if session is not None:
                    session.stop("browser_closed")
                    if session.active_run is not None:
                        session.active_run.cancel()

            try:
                try:
                    route = await page.locator("#route").element_handle()
                    session = MixedSession(server, driver, route, approve)
                    session.download = await DownloadOwner.create(
                        page,
                        {
                            "allow_download": True,
                            "record": await page.locator('[data-record-id="result-case"]').element_handle(),
                            "control": await page.locator("button[data-result]").element_handle(),
                            "record_id": "result-case",
                        },
                        session.file_approval,
                    )
                    if setup_stopped is not None and setup_stopped.is_set():
                        raise BrowserCancelledError("Mixed setup was stopped.")
                    browser = driver.context.browser
                    assert browser is not None
                    browser.once("disconnected", disconnected)
                finally:
                    if retirement is not None:
                        retirement.cancel()
                        await asyncio.gather(retirement, return_exceptions=True)
                yield session
            finally:
                if session is not None:
                    if driver.context.browser is not None:
                        driver.context.browser.remove_listener("disconnected", disconnected)
                    session.stop()
                    if session.download:
                        await session.download.stop()
    finally:
        await asyncio.to_thread(server.close)
