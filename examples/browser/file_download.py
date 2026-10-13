"""Optional single granted loopback HTTP result, never an arbitrary browser download."""

from __future__ import annotations

import os
import re
import json
import time
import shutil
import asyncio
import hashlib
import secrets
import tempfile
from types import MappingProxyType
from pathlib import Path
from urllib.parse import urlsplit
from collections.abc import Mapping, Callable, Awaitable
from typing_extensions import TypedDict

import httpx2
from file_state import (
    FileState,
    FileStateV1,
    FileApproval,
    FileCleanupIncompleteError,
    approving_owner,
    browser_outcome,
    wait_for_decision,
    wait_for_file_cleanup,
)
from playwright.async_api import Page, JSHandle, ElementHandle

CAP = 65536
QUANTUM = 8192
PARENT = Path(__file__).resolve().parent
ELIGIBLE = """(el,[doc,row,id]) =>
 el.ownerDocument===doc && doc===window.document && el.isConnected &&
 row.isConnected && row.dataset.recordId===id &&
 el.closest('[data-record-id]')===row && el.matches('button:not(:disabled)')"""


def digest(value: bytes | bytearray) -> str:
    return hashlib.sha256(value).hexdigest()


def milliseconds() -> int:
    return time.time_ns() // 1_000_000


def refusal() -> dict[str, object]:
    return {"status": "refused", "attempted": False, "completed": False}


def unknown() -> dict[str, object]:
    return {"status": "unknown", "attempted": True, "completed": False}


class _Grant(TypedDict):
    id: str
    session: str
    count: int
    sha256: str
    expires_at: int
    url: str


class DownloadOwner:
    area: Path
    quarantine: Path
    page: Page
    document: JSHandle
    _document_disposed: bool
    _cleanup_task: asyncio.Task[None] | None
    record: ElementHandle
    control: ElementHandle
    record_id: str
    grant: _Grant | None
    last: dict[str, object]
    allowed: bool
    url: str
    session: str
    stopped: bool
    revoked: bool
    work: asyncio.Future[None] | None
    approve: Callable[[Mapping[str, object]], Awaitable[object]]
    client: httpx2.AsyncClient | None
    _stats: dict[str, int]
    _state: FileState

    @classmethod
    async def create(
        cls,
        page: Page,
        configuration: dict[str, object] | None,
        approve: Callable[[Mapping[str, object]], Awaitable[object]],
    ) -> DownloadOwner:
        area = Path(tempfile.mkdtemp(prefix="openai-file-download-"))
        document: JSHandle | None = None

        async def abandon() -> None:
            try:
                if document is not None:
                    await document.dispose()
            except Exception:
                # Keep the initialization error; local staging must still go.
                pass
            finally:
                shutil.rmtree(area)

        try:
            result = cls()
            result.area = area
            result.quarantine = area / "quarantine"
            result.quarantine.mkdir(mode=0o700)
            result.allowed = configuration is not None and configuration.get("allow_download") is True
            record = configuration.get("record") if configuration else None
            control = configuration.get("control") if configuration else None
            record_id = configuration.get("record_id") if configuration else None
            result.url = page.url
            if (
                not isinstance(record, ElementHandle)
                or not isinstance(control, ElementHandle)
                or type(record_id) is not str
                or not record_id
            ):
                raise ValueError()
            result.record, result.control, result.record_id = record, control, record_id
            result.page = page
            document = await page.evaluate_handle("document")
            result.document = document
            result._document_disposed = False
            result._cleanup_task = None
            if page.url != result.url:
                raise ValueError()
            result.approve = approve
            result.session = secrets.token_hex(16)
            result.grant = None
            result.revoked = False
            result.stopped = False
            result.work = None
            result.client = None
            result.last = refusal()
            result._state = FileState("download")
            result._stats = {
                "requests": 0,
                "readBytes": 0,
                "writtenBytes": 0,
                "peakFileBytes": 0,
            }
            return result
        except Exception:
            await abandon()
            raise ValueError("Result owner initialization refused.") from None
        except BaseException:
            await abandon()
            raise

    @property
    def stats(self) -> dict[str, int]:
        # Diagnostics are not authority; the grant budget must never be caller-reset.
        return dict(self._stats)

    def receipt(self) -> dict[str, object]:
        return dict(self.last)

    def state(self) -> FileStateV1:
        return self._state.snapshot()

    def change_session(self) -> None:
        self.session = secrets.token_hex(16)

    def issue(self, source: dict[str, object], expires_at: int) -> dict[str, str]:
        metadata = dict(source) if type(source) is dict else {}
        url, count, sha256 = (metadata.get(name) for name in ("url", "count", "sha256"))
        url_text = url if type(url) is str else ""
        try:
            parsed = urlsplit(url_text)
            valid_url = bool(
                parsed
                and parsed.hostname
                and parsed.port != 0
                and "@" not in parsed.netloc
                and "#" not in url_text
                and not any(ord(c) <= 32 for c in url_text)
                and (parsed.scheme == "https" or parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "::1"))
            )
        except ValueError:
            valid_url = False
        if (
            not self.allowed
            or self.revoked
            or self.work is not None
            or self.grant is not None
            or self._stats["requests"] != 0
            or set(metadata) != {"url", "count", "sha256"}
            or not valid_url
            or type(count) is not int
            or not 0 <= count <= CAP
            or type(sha256) is not str
            or re.fullmatch(r"[a-f0-9]{64}", sha256) is None
            or type(expires_at) is not int
            or not milliseconds() < expires_at <= milliseconds() + 30_000
        ):
            self._state.prepare("refused")
            raise ValueError("Result grant refused.")
        self.grant = {
            "id": secrets.token_hex(24),
            "session": self.session,
            "count": count,
            "sha256": sha256,
            "url": url_text,
            "expires_at": expires_at,
        }
        return {"grant_id": str(self.grant["id"]), "label": "Prepared fixture result"}

    async def stop(self) -> None:
        self._state.clean("pending")
        self.revoked = self.stopped = True
        approval = approving_owner.get()
        if approval is not None and approval["owner"] is self._state and approval["active"]:
            return
        operation = self.work
        # Interrupt only the owned connection, never cancel the entire calling Task.
        if self.client is not None:
            await self.client.aclose()
        if operation is not None:
            await asyncio.shield(operation)
        self.grant = None
        if self._cleanup_task is None:

            async def cleanup() -> None:
                if self.area.exists():
                    shutil.rmtree(self.area)
                if not self._document_disposed:
                    await self.document.dispose()
                    self._document_disposed = True
                self._state.clean("completed")

            def completed(task: asyncio.Task[None]) -> None:
                failed = task.cancelled() or task.exception() is not None
                if failed and self._cleanup_task is task:
                    self._cleanup_task = None

            self._cleanup_task = asyncio.create_task(cleanup())
            self._cleanup_task.add_done_callback(completed)
        await wait_for_file_cleanup(self._cleanup_task)

    async def download_file(
        self, args: dict[str, object], *, cancelled: Callable[[], bool] | None = None
    ) -> dict[str, object]:
        _, outcome = await self._download(args, cancelled)
        return outcome

    async def download(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None = None) -> str:
        receipt, _ = await self._download(args, cancelled)
        return receipt

    async def _download(
        self, args: dict[str, object], cancelled: Callable[[], bool] | None
    ) -> tuple[str, dict[str, object]]:
        if self.work is not None or self.revoked:
            self._state.transfer("refused", "none", current=False)
            receipt = json.dumps(refusal())
            return receipt, browser_outcome(receipt, False, self._state.cleanup)
        self.work = completion = asyncio.get_running_loop().create_future()
        self._state.transfer("in_progress", "none")
        chosen = self.grant
        admitted = False
        task_cancelled = False
        interrupted: Callable[[], bool] = lambda: self.stopped or bool(cancelled and cancelled())
        file: Path | None = None
        try:
            if (
                chosen is None
                or set(args) != {"grant_id"}
                or args["grant_id"] != chosen["id"]
                or chosen["session"] != self.session
                or chosen["expires_at"] <= milliseconds()
                or interrupted()
                or self.page.url != self.url
                or not await wait_for_decision(
                    lambda: self.control.evaluate(ELIGIBLE, [self.document, self.record, self.record_id]), interrupted
                )
            ):
                raise ValueError("Result response refused")
            approval = FileApproval(owner=self._state, active=True)
            token = approving_owner.set(approval)
            try:
                agreed = await wait_for_decision(
                    lambda: self.approve(
                        MappingProxyType(
                            {
                                "label": "Prepared fixture result",
                                "count": chosen["count"],
                                "sha256": chosen["sha256"],
                            }
                        )
                    ),
                    interrupted,
                )
            finally:
                approval["active"] = False
                approving_owner.reset(token)
            eligible = await wait_for_decision(
                lambda: self.control.evaluate(ELIGIBLE, [self.document, self.record, self.record_id]), interrupted
            )
            if (
                agreed is not True
                or self.revoked
                or interrupted()
                or self.grant is not chosen
                or chosen["expires_at"] <= milliseconds()
                or chosen["session"] != self.session
                or self.page.url != self.url
                or not eligible
            ):
                raise ValueError("Result response refused")
            self.grant = None
            admitted = True
            self.last = unknown()
            self._state.transfer("in_progress", "unknown")
            deadline = chosen["expires_at"]
            # No browser cookies, proxy env, netrc, inherited headers, auth or redirects.
            self.client = client = httpx2.AsyncClient(trust_env=False, follow_redirects=False, timeout=None)

            # One absolute lifetime includes headers, body and final identity check.
            # The completion Future still resolves only after cancellation cleanup.
            async def receive() -> None:
                nonlocal file
                async with client:
                    self._stats["requests"] += 1
                    async with client.stream(
                        "GET",
                        chosen["url"],
                        headers={
                            "accept": "application/octet-stream",
                            "accept-encoding": "identity",
                        },
                    ) as response:
                        declared = response.headers.get("content-length")
                        if (
                            response.status_code != 200
                            or response.headers.get("content-encoding", "identity") != "identity"
                            or response.headers.get("content-type") != "application/octet-stream"
                            or sum(len(k) + len(v) + 4 for k, v in response.headers.raw) > 8192
                            or (
                                declared is not None
                                and (
                                    not declared.isascii() or not declared.isdigit() or int(declared) != chosen["count"]
                                )
                            )
                        ):
                            raise ValueError()
                        file = self.quarantine / ("q_" + secrets.token_hex(12))
                        fd = os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                        checksum = hashlib.sha256()
                        buffered = bytearray()
                        try:
                            # HTTPX may prebuffer at the parser. This caps raw bytes
                            # delivered to this application and owned file writes only.
                            async for octet in response.aiter_raw(chunk_size=1):
                                if self.revoked or interrupted() or milliseconds() >= deadline:
                                    raise ValueError()
                                self._stats["readBytes"] += len(octet)
                                if self._stats["readBytes"] > CAP:
                                    raise ValueError()
                                buffered.extend(octet)
                                if len(buffered) == QUANTUM:
                                    checksum.update(buffered)
                                    self._write(fd, buffered)
                                    buffered.clear()
                            if buffered:
                                checksum.update(buffered)
                                self._write(fd, buffered)
                        finally:
                            buffered[:] = b"\0" * len(buffered)
                            os.close(fd)
                        actual = checksum.hexdigest()
                        still_current = await self.control.evaluate(
                            ELIGIBLE, [self.document, self.record, self.record_id]
                        )
                        if (
                            self.revoked
                            or interrupted()
                            or milliseconds() >= deadline
                            or chosen["session"] != self.session
                            or self.page.url != self.url
                            or not still_current
                            or self._stats["readBytes"] != chosen["count"]
                            or actual != chosen["sha256"]
                        ):
                            raise ValueError()
                        self.last = {
                            "status": "completed",
                            "attempted": True,
                            "completed": True,
                            "count": self._stats["readBytes"],
                            "sha256": actual,
                        }

            receiving = asyncio.create_task(receive())
            try:
                while not receiving.done():
                    done, _ = await asyncio.wait(
                        {receiving}, timeout=min(0.05, max(0, (deadline - milliseconds()) / 1000))
                    )
                    if not done and (interrupted() or milliseconds() >= deadline):
                        receiving.cancel()
                        await asyncio.gather(receiving, return_exceptions=True)
                        raise ValueError()
                receiving.result()
            finally:
                if not receiving.done():
                    receiving.cancel()
                    await asyncio.gather(receiving, return_exceptions=True)
        except asyncio.CancelledError:
            task_cancelled = True
            self.last = unknown() if admitted else refusal()
            self.revoked = True
            self.grant = None
            raise
        except Exception:
            self.last = unknown() if admitted else refusal()
            if not admitted and interrupted() and self.grant is chosen:
                self.grant = None
        finally:
            try:
                receipt = json.dumps(self.last)
                was_interrupted = task_cancelled or interrupted()
                outcome = browser_outcome(receipt, was_interrupted, self._state.cleanup)
                if self.last["completed"]:
                    self._state.transfer("completed", "completed")
                elif was_interrupted:
                    self._state.transfer("interrupted", "unknown" if admitted else "none")
                else:
                    self._state.transfer("unknown" if admitted else "refused", "unknown" if admitted else "none")
                self.client = None
                if admitted and not self.last["completed"]:
                    self.revoked = True
                    if file is not None:
                        try:
                            file.unlink(missing_ok=True)
                        except OSError:
                            self._state.clean("pending")
                            raise
            finally:
                completion.set_result(None)
                self.work = None
                if self._state.cleanup == "pending":
                    try:
                        await self.stop()
                    except FileCleanupIncompleteError:
                        # Preserve the interrupted transfer's receipt; explicit Stop reports incomplete cleanup.
                        pass
        return receipt, outcome

    def _write(self, fd: int, data: bytearray) -> None:
        offset = 0
        while offset < len(data):
            count = os.write(fd, data[offset:])
            if not count:
                raise OSError()
            offset += count
            self._stats["writtenBytes"] += count
        self._stats["peakFileBytes"] = max(self._stats["peakFileBytes"], os.fstat(fd).st_size)
