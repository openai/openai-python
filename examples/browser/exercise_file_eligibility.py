"""Finite pre/post-admission checks using ordinary local controls; never issue a download."""

from __future__ import annotations

import asyncio
from typing import Any
from collections.abc import Mapping, Callable, Awaitable

from file_upload import UploadOwner
from file_download import DownloadOwner, digest, milliseconds
from playwright.async_api import async_playwright


async def main() -> None:
    checks = 0
    async with async_playwright() as manager:
        browser = await manager.chromium.launch(headless=True)
        try:
            for direction in ("upload", "download"):
                for held_read in (1, 2, 3) if direction == "upload" else (1, 2):
                    for cancellation in ("owner", "caller"):
                        page = await browser.new_page()
                        await page.set_content(
                            '<section data-record-id="fixture"><input type=file><button>Result</button></section>'
                        )
                        control = await page.locator("input" if direction == "upload" else "button").element_handle()
                        record = await page.locator("section").element_handle()
                        assert control is not None and record is not None
                        approvals = 0

                        async def approve(_summary: Mapping[str, object]) -> bool:
                            nonlocal approvals
                            approvals += 1
                            return True

                        configuration: dict[str, object] = {
                            "record": record,
                            "control": control,
                            "record_id": "fixture",
                            "allow_upload": True,
                            "allow_download": True,
                        }
                        owner: UploadOwner | DownloadOwner
                        if direction == "upload":
                            owner = await UploadOwner.create(page, configuration, approve)
                        else:
                            owner = await DownloadOwner.create(page, configuration, approve)
                        reached, release, live = asyncio.Event(), asyncio.Event(), asyncio.Event()
                        original = control.evaluate
                        set_files = control.set_input_files
                        reads = 0
                        assignments = 0

                        async def assign(
                            *args: Any, set_files: Callable[..., Awaitable[None]] = set_files, **kwargs: Any
                        ) -> None:
                            nonlocal assignments
                            assignments += 1
                            await set_files(*args, **kwargs)

                        control.set_input_files = assign

                        async def read(
                            expression: str,
                            arg: Any = None,
                            *,
                            held_read: int = held_read,
                            reached: asyncio.Event = reached,
                            release: asyncio.Event = release,
                            original: Callable[[str, Any], Awaitable[Any]] = original,
                        ) -> Any:
                            nonlocal reads
                            reads += 1
                            if reads == held_read:
                                reached.set()
                                await release.wait()
                                if held_read == 3:
                                    return True
                                raise ValueError("Late local eligibility response.")
                            return await original(expression, arg)

                        control.evaluate = read
                        content = b"local fixture"
                        if isinstance(owner, UploadOwner):
                            name = owner.generated_name()
                            (owner.upload_root / name).write_bytes(content)
                            grant = await owner.prepare(owner.upload_root, name, milliseconds() + 20_000)
                            pending = asyncio.create_task(
                                owner.upload_file({"grant_id": grant["grant_id"]}, cancelled=live.is_set)
                            )
                        else:
                            grant = owner.issue(
                                {"url": "http://127.0.0.1:1/unused", "count": len(content), "sha256": digest(content)},
                                milliseconds() + 20_000,
                            )
                            pending = asyncio.create_task(
                                owner.download_file({"grant_id": grant["grant_id"]}, cancelled=live.is_set)
                            )
                        stopping: asyncio.Task[None] | None = None
                        try:
                            await asyncio.wait_for(reached.wait(), 2)
                            if cancellation == "owner":
                                stopping = asyncio.create_task(owner.stop())
                            else:
                                live.set()
                            tasks = {pending} if stopping is None else {pending, stopping}
                            done, waiting = await asyncio.wait(tasks, timeout=0.9)
                            assert not waiting, (
                                f"Upload/download eligibility read {held_read} blocked {cancellation} Stop"
                            )
                            assert pending in done
                            result = pending.result()
                            attempted = held_read == 3
                            assert (result["status"], result["effect"]) == (
                                "interrupted",
                                "unknown" if attempted else "none",
                            )
                            assert approvals == min(held_read - 1, 1) and assignments == int(attempted)
                            assert owner.receipt() == {
                                "status": "unknown" if attempted else "refused",
                                "attempted": attempted,
                                "completed": False,
                            }
                            if isinstance(owner, DownloadOwner):
                                assert owner.stats["requests"] == 0
                            await owner.stop()
                            assert not owner.area.exists()
                            release.set()
                            await asyncio.sleep(0.07)
                            assert owner.receipt()["completed"] is False and owner.state()["cleanup"] == "completed"
                            checks += 1
                        finally:
                            release.set()
                            await asyncio.gather(pending, return_exceptions=True)
                            if stopping is not None:
                                await asyncio.gather(stopping, return_exceptions=True)
                            await owner.stop()
                            control.evaluate = original
                            await page.close()
        finally:
            await browser.close()
    print({"checks": checks, "api_calls": 0, "vendor_calls": 0})


if __name__ == "__main__":
    asyncio.run(main())
