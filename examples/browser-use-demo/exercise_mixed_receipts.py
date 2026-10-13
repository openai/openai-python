"""Check mixed receipt recovery and the private delivery endpoint without a VM."""

from __future__ import annotations

import json
import asyncio
from typing import Any, cast
from pathlib import Path
from unittest.mock import AsyncMock, patch

from server import Run, Fieldwork, WorkspaceBrowser
from file_download import DownloadOwner, digest
from mixed_workspace import RECEIPT, MixedWorkspace

from openai.lib.browser import BrowserError


def workspace() -> tuple[Fieldwork, Run, MixedWorkspace]:
    app = Fieldwork(cast(WorkspaceBrowser, None), "http://127.0.0.1:1", desktop_runtime=Path("/unused"))
    run = Run(app, {"environment": "mixed", "taskId": "mixed", "api": "responses", "mode": "live"})
    app.current = run
    assert isinstance(run.workspace, MixedWorkspace)
    run.workspace.routed = True
    run.workspace.routes = 1
    return app, run, run.workspace


async def recovery(boundary: str, *, approved: bool = True, current: bool = True) -> None:
    _app, run, subject = workspace()

    class Download:
        grant: dict[str, str] | None = None
        work = None
        revoked = False
        issues = 0
        calls = 0
        last: dict[str, Any] = {"status": "refused", "attempted": False, "completed": False}

        def issue(self, _source: object, _expires: int) -> dict[str, str]:
            assert self.grant is None and not self.last["attempted"]
            self.issues += 1
            self.grant = {"grant_id": str(self.issues)}
            return self.grant.copy()

        def receipt(self) -> dict[str, Any]:
            return self.last.copy()

        def state(self) -> dict[str, str]:
            return {"cleanup": "completed"}

        async def download(self, args: dict[str, object], **_kwargs: object) -> str:
            self.calls += 1
            assert args == self.grant, "The workspace reused a revoked grant"
            self.grant = None
            if self.calls == 1 and boundary == "before_transfer":
                run.phase_cancel.set()
            else:
                self.last = {
                    "status": "completed",
                    "attempted": True,
                    "completed": True,
                    "count": len(RECEIPT),
                    "sha256": digest(RECEIPT),
                }
                subject.results = 1
                if self.calls == 1:
                    run.phase_cancel.set()
            return json.dumps(self.last)

    owner = Download()
    subject.download = cast(DownloadOwner, owner)
    with (
        patch.object(subject, "binding", return_value={"test": "current"}),
        patch.object(subject, "matches", return_value=current),
        patch.object(run, "ask", new_callable=AsyncMock, return_value=approved) as approve,
    ):
        try:
            await subject.receipt({"case_id": "D-2201"})
        except BrowserError:
            pass
        else:
            raise AssertionError("Interrupted transfer disclosed a receipt")
        assert not subject.disclosed
        run.phase_cancel = asyncio.Event()
        if not approved or not current:
            try:
                await subject.receipt({"case_id": "D-2201"})
            except BrowserError:
                pass
            else:
                raise AssertionError("A refused or stale approval disclosed the receipt")
            assert not subject.disclosed and owner.calls == 1 and owner.issues == 1
            approve.assert_awaited_once()
            return
        assert await subject.receipt({"case_id": "D-2201"}) == RECEIPT.decode()
        assert subject.disclosed and subject.results == 1
        assert owner.issues == (2 if boundary == "before_transfer" else 1)
        assert owner.calls == (2 if boundary == "before_transfer" else 1)
        assert approve.await_count == (0 if boundary == "before_transfer" else 1)


async def uncertain_transfer(*, revoked: bool) -> None:
    _app, _run, subject = workspace()

    class Download:
        revoked: bool = False

        def receipt(self) -> dict[str, object]:
            return {"status": "refused" if revoked else "unknown", "attempted": not revoked, "completed": False}

        def issue(self, _source: object, _expires: int) -> None:
            raise AssertionError("An uncertain or revoked transfer received a new grant")

    owner = Download()
    owner.revoked = revoked
    subject.download = cast(DownloadOwner, owner)
    try:
        await subject.receipt({"case_id": "D-2201"})
    except BrowserError:
        pass
    else:
        raise AssertionError("An uncertain transfer was retried")
    assert not subject.disclosed and subject.results == 0


async def capability() -> None:
    app, _run, subject = workspace()
    subject.receiving = True
    headers = {"Host": "127.0.0.1:1"}
    for path in ("/result", "/result/guessed"):
        reply = await app.handle("GET", path, headers, b"")
        assert reply.status == 403 and subject.results == 0
    path = subject.result_path
    other = workspace()[2]
    assert path != other.result_path and path.startswith("/result/")
    reply = await app.handle("GET", path, headers, b"")
    assert reply.status == 200 and reply.body == RECEIPT and subject.results == 1
    assert (await app.handle("GET", path, headers, b"")).status == 403


async def route_capability() -> None:
    app, run, subject = workspace()
    subject.routed, subject.routes, subject.checked_route = False, 0, True
    headers = {"Host": "127.0.0.1:1", "Origin": app.origin}
    body = b'{"case_id":"D-2201","action":"route"}'
    for cookie in ("", "fieldwork_workspace=previous-run"):
        forged = {**headers, "Cookie": cookie}
        assert (await app.handle("GET", "/dispatch", forged, b"")).status == 403
        assert (await app.handle("POST", "/route", forged, body)).status == 403
        assert subject.routes == 0
    authorized = {**headers, "Cookie": f"fieldwork_workspace={run.workspace_token}"}
    page = await app.handle("GET", "/dispatch", authorized, b"")
    assert page.status == 200 and run.workspace_token.encode() not in page.body
    assert (await app.handle("POST", "/route", authorized, body)).status == 204
    assert subject.routes == 1
    assert (await app.handle("POST", "/route", authorized, body)).status == 403
    app.current = replacement = Run(
        app, {"environment": "mixed", "taskId": "mixed", "api": "responses", "mode": "live"}
    )
    assert isinstance(replacement.workspace, MixedWorkspace)
    replacement.workspace.checked_route = True
    assert (await app.handle("POST", "/route", authorized, body)).status == 403
    assert replacement.workspace.routes == 0


async def main() -> None:
    failures: list[str] = []
    for name, check in (
        ("before_transfer", recovery("before_transfer")),
        ("after_transfer", recovery("after_transfer")),
        ("refused_disclosure", recovery("after_transfer", approved=False)),
        ("stale_disclosure", recovery("after_transfer", current=False)),
        ("unknown_transfer", uncertain_transfer(revoked=False)),
        ("revoked_transfer", uncertain_transfer(revoked=True)),
        ("private_endpoint", capability()),
        ("route_capability", route_capability()),
    ):
        try:
            await asyncio.wait_for(check, 3)
        except Exception as error:
            failures.append(f"{name}: {type(error).__name__}: {error}")
    assert not failures, failures
    print("PASS: fresh receipt grants, disclosure-only recovery, and private one-shot delivery.")


if __name__ == "__main__":
    asyncio.run(main())
