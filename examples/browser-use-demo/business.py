"""Server-owned fixture records and one-use permits for stock, service and files."""

from __future__ import annotations

import json
import asyncio
import hashlib
from typing import TYPE_CHECKING, Any
from email.message import Message
from collections.abc import Mapping, Callable, Sequence

from runner import as_json, failure
from file_state import wait_for_decision

if TYPE_CHECKING:
    from runner import Run, Reply

from typing_extensions import TypedDict, NotRequired

from openai.lib.browser import BrowserError, BrowserReadElement

INTAKE = b"SYNTHETIC_PRIVATE_INTAKE_NOTE_501\nReceived at the local fixture dock.\n"


class Permit(TypedDict):
    operation: dict[str, Any]
    version: int
    staged: asyncio.Future[bool]
    reply: asyncio.Future[Reply]
    received: bool
    timer: NotRequired[asyncio.TimerHandle]


class Business:
    def __init__(self, run: Run) -> None:
        self.run = run
        self.results: list[dict[str, Any]] = []
        self.balance = {item["sku"]: item["quantity"] for item in run.task.get("stock", [])}
        self.pending: Permit | None = None
        self.denied = 0
        self.bindings: dict[str, dict[str, Any]] = {}

    async def bind_read(
        self, elements: Sequence[BrowserReadElement], *, cancelled: Callable[[], bool] | None = None
    ) -> None:
        run = self.run
        assert run.task_page is not None
        controls = run.task_page.locator("button")
        buttons = await wait_for_decision(
            lambda: controls.evaluate_all("""nodes => nodes.map(button => ({
              label: button.innerText.trim(), record: button.closest('[data-record-id]')?.dataset.recordId
            }))"""),
            cancelled,
        )
        self.bindings = {}
        fields: dict[str, str] = {}
        if run.task_id == "service":
            for label in run.task["fields"]:
                matches = [item for item in elements if item["label"] == label]
                if len(matches) != 1:
                    return
                value = matches[0].get("value")
                if not isinstance(value, str):
                    return
                fields[label] = value
        for element in elements:
            if element["role"] != "button":
                continue
            matches = [button for button in buttons if button["label"] == element["label"]]
            if len(matches) != 1:
                continue
            if (
                fields
                and all(fields.values())
                and element["label"] == f"Schedule {run.task['job']}"
                and matches[0]["record"] == run.task["job"]
            ):
                self.bindings[element["ref"]] = {
                    "operation": "schedule",
                    "job": run.task["job"],
                    "date": fields["Visit date"],
                    "technician": fields["Technician"],
                    "note": fields["Service note"],
                }
            for order in run.task.get("orders", []):
                for stock in run.task["stock"]:
                    if (
                        element["label"] == f"Ship {order['id']} with {stock['sku']}"
                        and matches[0]["record"] == order["id"]
                    ):
                        self.bindings[element["ref"]] = {"operation": "ship", "order": order["id"], "sku": stock["sku"]}

    def authorize(self, operation: dict[str, Any]) -> Permit:
        run = self.run
        if self.pending or not operation or run.owner != "agent" or run.phase_cancel.is_set():
            raise BrowserError("Read the current business record before requesting approval.")
        loop = asyncio.get_running_loop()
        permit: Permit = {
            "operation": dict(operation),
            "version": run.version,
            "staged": loop.create_future(),
            "reply": loop.create_future(),
            "received": False,
        }
        self.pending = permit
        permit["timer"] = loop.call_later(5, self.revoke, permit)
        return permit

    def revoke(self, permit: Permit | None) -> None:
        if permit and self.pending is permit:
            self.pending = None
            timer = permit.get("timer")
            if timer:
                timer.cancel()
            if not permit["staged"].done():
                permit["staged"].set_result(False)
            if not permit["reply"].done():
                permit["reply"].set_result(failure(403, "No matching business approval."))

    async def receive(self, headers: Message[str, str] | Mapping[str, str], data: bytes) -> Reply:
        run, permit = self.run, self.pending
        if (
            not permit
            or permit["received"]
            or run.owner != "agent"
            or run.version != permit["version"]
            or run.phase_cancel.is_set()
        ):
            self.denied += 1
            return failure(403, "No matching business approval.")
        expected = permit["operation"]
        if run.task_id == "files":
            if (
                headers.get("Content-Type") != "application/octet-stream"
                or headers.get("Content-Encoding") not in (None, "identity")
                or len(data) != expected["count"]
                or hashlib.sha256(data).hexdigest() != expected["sha256"]
            ):
                self.denied += 1
                self.revoke(permit)
                return failure(403, "No matching business approval.")
        else:
            try:
                value = json.loads(data)
            except (ValueError, UnicodeDecodeError):
                value = None
            if (
                type(value) is not dict
                or value != expected
                or (
                    run.task_id == "stock"
                    and (
                        any(item["order"] == expected["order"] for item in self.results)
                        or self.balance.get(expected["sku"], 0) < 1
                    )
                )
                or (run.task_id == "service" and self.results)
            ):
                self.denied += 1
                return failure(403, "No matching business approval.")
        permit["received"] = True
        permit["staged"].set_result(True)
        return await permit["reply"]

    async def finish(self, permit: Permit) -> None:
        phase = self.run.phase_cancel
        if (
            not await permit["staged"]
            or self.pending is not permit
            or self.run.owner != "agent"
            or self.run.version != permit["version"]
            or self.run.phase_cancel.is_set()
        ):
            raise BrowserError("The checked business action was not completed.")
        operation = permit["operation"]
        if self.run.task_id == "stock":
            self.balance[operation["sku"]] -= 1
        self.results.append(dict(operation))
        revision = len(self.results)
        permit["reply"].set_result(as_json({"revision": revision}))
        page = self.run.task_page
        assert page is not None
        await wait_for_decision(
            lambda: page.wait_for_function(
                "value => Number(document.body.dataset.revision) === value", arg=revision, timeout=5000
            ),
            phase.is_set,
        )

    def snapshot(self) -> dict[str, Any]:
        run = self.run
        task = run.task
        finished = len(self.results) == len(task.get("orders", [None]))
        verified = False
        if finished:
            if run.task_id == "stock":
                verified = all(
                    any(
                        item["order"] == order["id"]
                        and any(
                            stock["sku"] == item["sku"] and stock["colour"] == order["colour"]
                            for stock in task["stock"]
                        )
                        for item in self.results
                    )
                    for order in task["orders"]
                )
            elif run.task_id == "service":
                verified = self.results[0] == {
                    "operation": "schedule",
                    "job": task["job"],
                    "date": task["fields"]["Visit date"],
                    "technician": task["fields"]["Technician"],
                    "note": task["fields"]["Service note"],
                }
            else:
                verified = self.results[0] == {
                    "operation": "attach",
                    "job": task["job"],
                    "count": len(INTAKE),
                    "sha256": hashlib.sha256(INTAKE).hexdigest(),
                }
        results = [dict(item) for item in self.results]
        if run.task_id == "files":
            results = [{"operation": item["operation"], "job": item["job"]} for item in results]
        result: dict[str, Any] = {
            "revision": len(results),
            "finished": finished,
            "verified": verified,
            "results": results,
            "denied": self.denied,
        }
        if run.task_id == "stock":
            result["stock"] = [{"sku": sku, "quantity": quantity} for sku, quantity in self.balance.items()]
        if run.task_id == "files":
            result["file"] = run.file_owner.state() if run.file_owner else None
        return result
