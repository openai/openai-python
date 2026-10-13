"""Ordinary phase-ledger failures retain cleanup status and verified business results."""

from __future__ import annotations

import sys
import asyncio
import tempfile
from types import SimpleNamespace
from typing import Any, Callable, cast
from pathlib import Path
from unittest.mock import patch

from server import Fieldwork, WorkspaceBrowser

sys.path.insert(1, str(Path(__file__).resolve().parents[1] / "computer-desktop"))
from runner import Run
from desktop import Desktop
from mixed_workspace import DownloadOwner, MixedWorkspace


async def case(environment: str, verified: bool, fail_close: bool) -> int:
    with tempfile.TemporaryDirectory() as raw:
        area = Path(raw)
        before = set(Path(tempfile.gettempdir()).iterdir())
        app = Fieldwork(
            cast(WorkspaceBrowser, None),
            "http://127.0.0.1:1",
            api_key="local-unused",
            models={"responses": "local-unused", "decisions": None},
            desktop_runtime=area,
        )
        run = Run(app, {"environment": environment, "taskId": environment, "api": "responses", "mode": "live"})
        app.current = run
        workspace = run.workspace
        assert workspace is not None

        async def no_input(_work: object) -> None:
            """Controlled guest settles without invoking its model callback."""

        workspace.guest = cast(Desktop, SimpleNamespace(operation_async=no_input, uncertain_effects=False))
        if isinstance(workspace, MixedWorkspace):
            workspace.download = cast(DownloadOwner, SimpleNamespace(area=area))

        async def inspect(*, cancelled: Callable[[], bool] | None = None) -> dict[str, Any]:
            del cancelled
            return {"finished": False, "verified": False}

        async def proof(*, cancelled: Callable[[], bool] | None = None, finalize: bool = False) -> dict[str, Any]:
            del cancelled
            if fail_close and (finalize or not verified):
                if environment == "desktop":
                    # The real phase created this unique new directory during this one run.
                    entries = [
                        path for path in Path(tempfile.gettempdir()).glob("fieldwork-desktop-*") if path not in before
                    ]
                    assert len(entries) == 1
                    entries[0].rmdir()
                else:
                    (area / "phase.json").mkdir()
            if not verified:
                raise RuntimeError("Controlled pre-verification failure")
            return {"verified": True}

        async def settle(*, cancelled: Callable[[], bool] | None = None) -> None:
            """No live display or guest belongs to this fixture."""
            del cancelled

        with (
            patch.object(run, "capture", settle),
            patch.object(run, "inspect", inspect),
            patch.object(workspace, "proof", proof),
            patch.object(workspace, "retire", settle),
        ):
            run.agent = asyncio.create_task(run.execute())
            await run.agent
            assert run.cleanup is not None
            await run.cleanup
        if isinstance(workspace, MixedWorkspace):
            # This probe provided an area, not a live DownloadOwner to export.
            workspace.download = None
        receipt = run.receipt()
        assert receipt["status"] == ("cleanup_failed" if fail_close else "complete" if verified else "failed"), (
            environment,
            verified,
            fail_close,
            receipt,
        )
        assert receipt["result"] == ("verified" if verified else "unverified")
        assert receipt["cleanup"] == ("failed" if fail_close else "completed")
        assert run.requests == 0
        assert run.busy() is fail_close
        return 5


async def main() -> None:
    checks = 0
    for environment in ("desktop", "mixed"):
        for verified in (True, False):
            for fail_close in (True, False):
                checks += await case(environment, verified, fail_close)
    print({"checks": checks, "api_calls": 0, "vendor_calls": 0})


if __name__ == "__main__":
    asyncio.run(main())
