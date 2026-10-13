"""Portable approved transfers through local CDP and two independent local sources."""

from __future__ import annotations

import os
import json
import socket
import asyncio
import tempfile
import threading
from typing import cast
from pathlib import Path
from datetime import timedelta
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from collections.abc import Mapping, Callable, Sequence
from typing_extensions import Protocol, TypedDict, override

from file_upload import UploadOwner
from file_download import DownloadOwner, digest, milliseconds
from browser_driver import PlaywrightBrowser, origin
from playwright.async_api import FilePayload, async_playwright

from openai.lib.browser import BrowserFileOutcome, AsyncBrowserToolset, BrowserConfirmContext
from openai.types.responses import ResponseFunctionToolCall

PAGE = b"""<!doctype html><title>Archive desk</title>
<section data-record-id="LETTER-847"><input type=file aria-label="Attach manuscript"></section>
<section data-record-id="SCAN-619"><button>Retrieve signed scan</button></section>"""
CONTENT = b"Local manuscript " * 3600


class SourceServer(ThreadingHTTPServer):
    requests: list[tuple[str, dict[str, str]]]
    arrived: threading.Event
    release: threading.Event


class FileAction(Protocol):
    async def __call__(
        self, args: dict[str, object], *, cancelled: Callable[[], bool] | None = None
    ) -> dict[str, object]: ...


class FileBrowser(PlaywrightBrowser):
    upload_file: FileAction
    download_file: FileAction


class FileResult(TypedDict):
    ok: bool
    result: BrowserFileOutcome


class FileSelection(Protocol):
    async def __call__(
        self,
        files: str | Path | FilePayload | Sequence[str | Path] | Sequence[FilePayload],
        *,
        timeout: float | timedelta | None = None,
        no_wait_after: bool | None = None,
    ) -> None: ...


class Source(BaseHTTPRequestHandler):
    @override
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.path == "/desk":
            self.send_response(200)
            self.send_header("content-type", "text/html")
            self.send_header("content-length", str(len(PAGE)))
            self.end_headers()
            self.wfile.write(PAGE)
            return
        assert isinstance(self.server, SourceServer)
        self.server.requests.append((self.path, dict(self.headers)))
        self.server.arrived.set()
        mode = self.path.split("?", 1)[0]
        if mode == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/scan?should-not-fetch")
            self.end_headers()
            return
        data = CONTENT if mode != "/large" else b"x" * (65536 + 2048)
        self.send_response(200)
        self.send_header("content-type", "application/octet-stream")
        self.send_header("content-encoding", "identity")
        self.end_headers()
        try:
            if mode == "/stall":
                self.wfile.write(data[:8192])
                self.wfile.flush()
                self.server.release.wait(5)
                self.wfile.write(data[8192:])
            else:
                self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass


async def execute(toolset: AsyncBrowserToolset, member: str, grant: str) -> FileResult:
    call = ResponseFunctionToolCall(
        type="function_call",
        name="browser_" + member,
        arguments=json.dumps({"grant_id": grant}),
        call_id="portable",
        id="portable",
        status="completed",
    )
    returned = await toolset.execute(call)
    output = returned["output"]
    assert isinstance(output, list)
    assert output[0]["type"] == "input_text"
    return cast(FileResult, json.loads(output[0]["text"]))


async def main() -> None:
    sources = [SourceServer(("127.0.0.1", 0), Source) for _ in range(2)]
    threads: list[threading.Thread] = []
    for source in sources:
        source.requests = []
        source.arrived = threading.Event()
        source.release = threading.Event()
        thread = threading.Thread(target=source.serve_forever, daemon=True)
        thread.start()
        threads.append(thread)
    try:
        with socket.socket() as allocator:
            allocator.bind(("127.0.0.1", 0))
            cdp_port = allocator.getsockname()[1]
        async with async_playwright() as playwright:
            launched = await playwright.chromium.launch(
                headless=True,
                chromium_sandbox=True,
                args=[f"--remote-debugging-port={cdp_port}"],
                env={name: value for name in ("PATH", "HOME", "TMPDIR") if (value := os.environ.get(name)) is not None},
            )
            try:
                attached = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{cdp_port}")
                context = await attached.new_context(service_workers="block", accept_downloads=False)
                page_url = f"http://127.0.0.1:{sources[0].server_port}/desk"
                driver = FileBrowser(context, {origin(page_url)}, owned_fixture_urls=frozenset({page_url}))
                await context.route("**/*", driver.guard)
                await driver.new_tab({"url": page_url})
                _, page = driver.page(None)
                consent = asyncio.Event()
                consent.set()
                offered = asyncio.Event()

                async def approve(_prepared: Mapping[str, object]) -> bool:
                    offered.set()
                    await consent.wait()
                    return True

                async def confirm(_context: BrowserConfirmContext) -> bool:
                    return True

                upload = await UploadOwner.create(
                    page,
                    {
                        "allow_upload": True,
                        "record": await page.locator('[data-record-id="LETTER-847"]').element_handle(),
                        "control": await page.locator("input").element_handle(),
                        "record_id": "LETTER-847",
                    },
                    approve,
                )
                try:
                    assert upload.area.parent == Path(tempfile.gettempdir())
                    name = upload.generated_name()
                    (upload.upload_root / name).write_bytes(b"Archive from this run")
                    grant = await upload.prepare(upload.upload_root, name, milliseconds() + 30000)
                    driver.upload_file = upload.upload_file
                    tools = AsyncBrowserToolset(driver, members=["upload_file"], confirm=confirm)
                    assert (await execute(tools, "upload_file", "wrong"))["ok"] is False
                    result = await execute(tools, "upload_file", grant["grant_id"])
                    assert result["ok"] and result["result"] == {
                        "version": 1,
                        "status": "completed",
                        "effect": "completed",
                        "cleanup": "not_started",
                    }, result
                    assert await upload.control.evaluate("el=>el.files.length") == 1
                    assert not (await execute(tools, "upload_file", grant["grant_id"]))["ok"]
                finally:
                    await upload.stop()
                assert not upload.area.exists()

                for direction, timing in [
                    (direction, timing) for direction in ("upload", "download") for timing in ("during", "after")
                ]:
                    sending = direction == "upload"
                    record_id = "LETTER-847" if sending else "SCAN-619"
                    control = await page.locator("input" if sending else "button").element_handle()
                    assert control is not None
                    if sending:
                        await control.set_input_files([])
                    child: asyncio.Task[None] | None = None
                    release_child = asyncio.Event()

                    async def stop_later() -> None:
                        await release_child.wait()  # noqa: B023 -- Child finishes before the next case.
                        await owner.stop()  # noqa: B023 -- Child finishes before the next owner is created.

                    async def stop_from_approval(_summary: Mapping[str, object]) -> bool:
                        nonlocal child
                        await asyncio.sleep(0)
                        if timing == "during":  # noqa: B023 -- Approval finishes before the next case.
                            await owner.stop()  # noqa: B023 -- The transfer finishes before another owner is created.
                            assert owner.state()["cleanup"] == "pending"  # noqa: B023 -- This is the same admitted owner.
                        else:
                            child = asyncio.create_task(stop_later())
                        return True

                    config: dict[str, object] = {
                        "allow_upload" if sending else "allow_download": True,
                        "record": await page.locator(f'[data-record-id="{record_id}"]').element_handle(),
                        "control": control,
                        "record_id": record_id,
                    }
                    before = len(sources[0].requests)
                    if sending:
                        owner = await UploadOwner.create(page, config, stop_from_approval)
                        name = owner.generated_name()
                        (owner.upload_root / name).write_bytes(CONTENT)
                        grant = await owner.prepare(owner.upload_root, name, milliseconds() + 30000)
                        result = await asyncio.wait_for(owner.upload_file({"grant_id": grant["grant_id"]}), timeout=2)
                    else:
                        owner = await DownloadOwner.create(page, config, stop_from_approval)
                        grant = owner.issue(
                            {
                                "url": f"http://127.0.0.1:{sources[0].server_port}/scan?signature=local-child",
                                "count": len(CONTENT),
                                "sha256": digest(CONTENT),
                            },
                            milliseconds() + 30000,
                        )
                        result = await asyncio.wait_for(owner.download_file({"grant_id": grant["grant_id"]}), timeout=2)
                    assert result["status"] == ("interrupted" if timing == "during" else "completed")
                    assert result["effect"] == ("none" if timing == "during" else "completed")
                    if timing == "after":
                        assert owner.state()["cleanup"] == "not_started"
                        assert child is not None
                        release_child.set()
                        await asyncio.wait_for(child, timeout=2)
                    assert owner.state()["cleanup"] == "completed"
                    assert not owner.area.exists() and len(sources[0].requests) == before + (
                        not sending and timing == "after"
                    )
                    if sending:
                        assert await control.evaluate("el=>el.files.length") == (0 if timing == "during" else 1)
                    await owner.stop()

                for index, source in enumerate(sources):
                    for mode in (
                        "scan",
                        "digest",
                        "large",
                        "redirect",
                        "stall",
                        "replaced",
                        "expired",
                        "stop-approval",
                        "stop-admitted",
                    ):
                        offered.clear()
                        source.arrived.clear()
                        source.release.clear()
                        consent.set()
                        record = await page.locator('[data-record-id="SCAN-619"]').element_handle()
                        control = await page.locator("button").element_handle()
                        download = await DownloadOwner.create(
                            page,
                            {
                                "allow_download": True,
                                "record": record,
                                "control": control,
                                "record_id": "SCAN-619",
                            },
                            approve,
                        )
                        before = len(source.requests)
                        try:
                            source_mode = (
                                "stall"
                                if mode == "stop-admitted"
                                else "scan"
                                if mode in ("digest", "replaced", "expired", "stop-approval")
                                else mode
                            )
                            source_url = f"http://127.0.0.1:{source.server_port}/{source_mode}?signature=local-{index}"
                            metadata: dict[str, object] = {
                                "url": source_url,
                                "count": len(CONTENT),
                                "sha256": "0" * 64 if mode == "digest" else digest(CONTENT),
                            }
                            if mode == "scan":
                                for bad_url in (
                                    f"http://localhost:{source.server_port}/scan",
                                    f"http://@127.0.0.1:{source.server_port}/scan",
                                    source_url + "#fragment",
                                    "https://user:secret@example.test/a",
                                    "ftp://127.0.0.1/scan",
                                ):
                                    try:
                                        download.issue(dict(metadata, url=bad_url), milliseconds() + 30000)
                                        raise AssertionError("Invalid source was accepted")
                                    except ValueError:
                                        pass
                            deadline = milliseconds() + (60 if mode == "expired" else 30000)
                            grant = download.issue(metadata, deadline)
                            metadata.update(url="http://127.0.0.1:1/changed", count=0, sha256="1" * 64)
                            driver.download_file = download.download_file
                            tools = AsyncBrowserToolset(driver, members=["download_file"], confirm=confirm)
                            if mode == "expired":
                                await asyncio.sleep(0.08)
                            if mode == "replaced":
                                await control.evaluate("el=>el.replaceWith(el.cloneNode(true))")
                            if mode == "scan":
                                consent.clear()
                                pending = asyncio.create_task(execute(tools, "download_file", grant["grant_id"]))
                                try:
                                    await asyncio.wait_for(offered.wait(), 2)
                                    try:
                                        await execute(tools, "download_file", grant["grant_id"])
                                    except RuntimeError as error:
                                        assert str(error) == "Browser toolset is busy with another call."
                                    else:
                                        raise AssertionError("Concurrent SDK call was accepted.")
                                    refused = await download.download_file({"grant_id": grant["grant_id"]})
                                    assert (refused["status"], refused["effect"]) == ("refused", "none"), refused
                                finally:
                                    consent.set()
                                    result = await pending
                            elif mode.startswith("stop-"):
                                if mode == "stop-approval":
                                    consent.clear()
                                pending = asyncio.create_task(download.download_file({"grant_id": grant["grant_id"]}))
                                if mode == "stop-approval":
                                    await asyncio.wait_for(offered.wait(), 2)
                                else:
                                    assert await asyncio.to_thread(source.arrived.wait, 2)
                                # Queue Stop before the refused adapter resumes. Its own
                                # call must stay refused despite the owner being stopped.
                                busy = asyncio.create_task(download.download_file({"grant_id": grant["grant_id"]}))
                                stopping = asyncio.create_task(download.stop())
                                prior = await busy
                                assert (prior["status"], prior["effect"]) == ("refused", "none"), prior
                                consent.set()
                                result = await asyncio.wait_for(pending, 2)
                                await asyncio.wait_for(stopping, 2)
                                assert (result["status"], result["effect"]) == (
                                    "interrupted",
                                    "none" if mode == "stop-approval" else "unknown",
                                ), result
                                assert (prior["status"], prior["effect"]) == ("refused", "none"), prior
                                assert len(source.requests) - before == (0 if mode == "stop-approval" else 1)
                                continue
                            elif mode == "stall":
                                cancelled = asyncio.Event()
                                pending = asyncio.create_task(
                                    download.download_file({"grant_id": grant["grant_id"]}, cancelled=cancelled.is_set)
                                )
                                assert await asyncio.to_thread(source.arrived.wait, 2)
                                cancelled.set()
                                result = await asyncio.wait_for(pending, 2)
                                assert result == {
                                    "version": 1,
                                    "status": "interrupted",
                                    "effect": "unknown",
                                    "cleanup": "not_started",
                                }, result
                                source.release.set()
                                continue
                            else:
                                result = await execute(tools, "download_file", grant["grant_id"])
                            if mode == "scan":
                                assert result["ok"] and result["result"]["effect"] == "completed", result
                                assert not (await execute(tools, "download_file", grant["grant_id"]))["ok"]
                            else:
                                assert not result["ok"], result
                                assert result["result"]["effect"] == (
                                    "none" if mode in ("expired", "replaced") else "unknown"
                                ), result
                            assert len(source.requests) - before == (0 if mode in ("expired", "replaced") else 1)
                            assert "signature" not in json.dumps(result) and "sha256" not in json.dumps(result)
                            assert download.stats["readBytes"] <= 65537
                        finally:
                            consent.set()
                            source.release.set()
                            await download.stop()
                            assert not download.area.exists() and download.state()["cleanup"] == "completed"
                for admitted in (False, True):
                    offered.clear()
                    consent.set()
                    if not admitted:
                        consent.clear()
                    selected = asyncio.Event()
                    released = asyncio.Event()
                    record = await page.locator('[data-record-id="LETTER-847"]').element_handle()
                    control = await page.locator("input").element_handle()
                    await control.set_input_files([])
                    original = control.set_input_files

                    async def held_selection(
                        files: str | Path | FilePayload | Sequence[str | Path] | Sequence[FilePayload],
                        *,
                        timeout: float | timedelta | None = None,
                        no_wait_after: bool | None = None,
                        original: FileSelection = original,
                        selected: asyncio.Event = selected,
                        released: asyncio.Event = released,
                    ) -> None:
                        await original(files, timeout=timeout, no_wait_after=no_wait_after)
                        selected.set()
                        await released.wait()

                    control.set_input_files = held_selection
                    upload = await UploadOwner.create(
                        page,
                        {"allow_upload": True, "record": record, "control": control, "record_id": "LETTER-847"},
                        approve,
                    )
                    try:
                        name = upload.generated_name()
                        (upload.upload_root / name).write_bytes(CONTENT)
                        grant = await upload.prepare(upload.upload_root, name, milliseconds() + 30000)
                        pending = asyncio.create_task(upload.upload_file({"grant_id": grant["grant_id"]}))
                        await asyncio.wait_for(selected.wait() if admitted else offered.wait(), 2)
                        busy = asyncio.create_task(upload.upload_file({"grant_id": grant["grant_id"]}))
                        stopping = asyncio.create_task(upload.stop())
                        prior = await busy
                        assert (prior["status"], prior["effect"]) == ("refused", "none"), prior
                        consent.set()
                        released.set()
                        result = await asyncio.wait_for(pending, 2)
                        await asyncio.wait_for(stopping, 2)
                        assert (result["status"], result["effect"]) == (
                            "interrupted",
                            "unknown" if admitted else "none",
                        ), result
                        assert (prior["status"], prior["effect"]) == ("refused", "none"), prior
                        assert await control.evaluate("el => el.files[0]?.size ?? 0") == (
                            len(CONTENT) if admitted else 0
                        )
                    finally:
                        consent.set()
                        released.set()
                        await upload.stop()
                        assert not upload.area.exists() and upload.state()["cleanup"] == "completed"
                for source in sources:
                    for path, headers in source.requests:
                        headers = {key.lower(): value for key, value in headers.items()}
                        assert path.startswith(("/scan?", "/digest?", "/large?", "/redirect?", "/stall?"))
                        assert "cookie" not in headers and "authorization" not in headers
                        assert headers.get("accept-encoding") == "identity"
                await context.close()
            finally:
                await launched.close()
    finally:
        for source, thread in zip(sources, threads, strict=True):
            source.release.set()
            await asyncio.to_thread(source.shutdown)
            source.server_close()
            thread.join()
    print(
        "PASS Python CDP: actual SDK opt-in files, two sources, portable IDs, one-use/expiry/concurrent refusal, digest/cap/redirect/cancellation and cleanup"
    )


if __name__ == "__main__":
    asyncio.run(main())
