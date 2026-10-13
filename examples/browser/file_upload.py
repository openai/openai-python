"""Optional fixed fixture upload; never opens an arbitrary existing host root."""

from __future__ import annotations

import os
import re
import json
import stat
import time
import shutil
import asyncio
import hashlib
import secrets
import tempfile
from types import MappingProxyType
from pathlib import Path
from collections.abc import Mapping, Callable, Awaitable
from typing_extensions import TypedDict

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

CAP = 64 * 1024
PARENT = Path(__file__).resolve().parent
ELIGIBLE = """(el,[doc,row,id]) =>
 el.ownerDocument===doc && doc===window.document && el.isConnected &&
 row.isConnected && row.dataset.recordId===id &&
 el.closest('[data-record-id]')===row && el.matches('input[type=file]:not(:disabled)')"""


def digest(value: bytes | bytearray) -> str:
    return hashlib.sha256(value).hexdigest()


def milliseconds() -> int:
    return time.time_ns() // 1_000_000


def refusal() -> dict[str, object]:
    return {"status": "refused", "attempted": False, "completed": False}


def unknown() -> dict[str, object]:
    return {"status": "unknown", "attempted": True, "completed": False}


async def no_hook() -> None:
    pass


class _Grant(TypedDict):
    id: str
    session: str
    count: int
    sha256: str
    expires_at: int
    buffer: bytearray


class UploadOwner:
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
    upload_root: Path
    active_session: str
    after_stat: Callable[[], Awaitable[None]]
    _state: FileState

    @classmethod
    async def create(
        cls,
        page: Page,
        configuration: dict[str, object] | None,
        approve: Callable[[Mapping[str, object]], Awaitable[object]],
        after_stat: Callable[[], Awaitable[None]] = no_hook,
    ) -> UploadOwner:
        if not getattr(os, "O_NOFOLLOW", None) or not getattr(os, "O_NONBLOCK", None):
            raise ValueError(
                "Uploads are not supported on this platform: non-following, nonblocking file opens are required."
            )
        area = Path(tempfile.mkdtemp(prefix="openai-file-upload-"))
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
            result.upload_root = area / "upload"
            result.quarantine = area / "quarantine"
            result.upload_root.mkdir(mode=0o700)
            result.quarantine.mkdir(mode=0o700)
            result.allowed = configuration is not None and configuration.get("allow_upload") is True
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
                raise ValueError("File owner initialization refused.")
            result.record, result.control, result.record_id = record, control, record_id
            result.session = secrets.token_hex(16)
            result.active_session = result.session
            result.page = page
            document = await page.evaluate_handle("document")
            result.document = document
            result._document_disposed = False
            result._cleanup_task = None
            if page.url != result.url:
                raise ValueError("File owner initialization refused.")
            result.approve, result.after_stat = approve, after_stat
            result.grant = None
            result.revoked = False
            result.stopped = False
            result.work = None
            result.last = refusal()
            result._state = FileState("upload")
            return result
        except Exception:
            await abandon()
            raise ValueError("File owner initialization refused.") from None
        except BaseException:
            await abandon()
            raise

    def generated_name(self) -> str:
        return "f_" + secrets.token_hex(12)

    def receipt(self) -> dict[str, object]:
        return dict(self.last)

    def state(self) -> FileStateV1:
        return self._state.snapshot()

    def change_session(self) -> None:
        self.active_session = secrets.token_hex(16)

    async def prepare(self, root: Path, name: object, expires_at: int) -> dict[str, str]:
        if (
            self.work is None
            and self.grant is not None
            and (self.grant["expires_at"] <= milliseconds() or self.grant["session"] != self.active_session)
        ):
            self.grant["buffer"][:] = b"\0" * len(self.grant["buffer"])
            self.grant = None
        if (
            not self.allowed
            or self.revoked
            or self.work is not None
            or self.grant is not None
            or root != self.upload_root
            or type(name) is not str
            or re.fullmatch(r"f_[a-f0-9]{24}", name) is None
            or type(expires_at) is not int
            or not milliseconds() < expires_at <= milliseconds() + 30_000
        ):
            self._state.prepare("refused")
            raise ValueError("File preparation refused.")
        # Stop waits for this operation's release, not the caller's next work.
        self.work = completion = asyncio.get_running_loop().create_future()
        prepared_session = self.active_session
        frozen = bytearray()
        try:
            try:
                root_stat = self.upload_root.lstat()
                path = self.upload_root / name
                pre = path.lstat()
                if not stat.S_ISDIR(root_stat.st_mode) or not stat.S_ISREG(pre.st_mode) or pre.st_size > CAP:
                    raise ValueError()
                descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                try:
                    checked = os.fstat(descriptor)
                    if (
                        not stat.S_ISREG(checked.st_mode)
                        or checked.st_size > CAP
                        or (checked.st_dev, checked.st_ino) != (pre.st_dev, pre.st_ino)
                    ):
                        raise ValueError()
                    await self.after_stat()
                    while len(frozen) <= CAP:
                        chunk = os.read(descriptor, CAP + 1 - len(frozen))
                        if not chunk:
                            break
                        frozen.extend(chunk)
                    if len(frozen) > CAP:
                        raise ValueError()
                finally:
                    os.close(descriptor)
                if self.revoked or prepared_session != self.active_session or expires_at <= milliseconds():
                    raise ValueError()
                self.grant = {
                    "id": secrets.token_hex(24),
                    "session": prepared_session,
                    "buffer": frozen,
                    "count": len(frozen),
                    "sha256": digest(frozen),
                    "expires_at": expires_at,
                }
                return {
                    "grant_id": str(self.grant["id"]),
                    "label": "Approved fixture document",
                }
            except asyncio.CancelledError:
                self._state.prepare("interrupted")
                self.revoked = True
                frozen[:] = b"\0" * len(frozen)
                raise
            except Exception:
                self._state.prepare("interrupted" if self.stopped else "refused")
                frozen[:] = b"\0" * len(frozen)
                raise ValueError("File preparation refused.") from None
        finally:
            completion.set_result(None)
            self.work = None

    async def stop(self) -> None:
        self._state.clean("pending")
        self.revoked = True
        self.stopped = True
        approval = approving_owner.get()
        if approval is not None and approval["owner"] is self._state and approval["active"]:
            return
        operation = self.work
        if operation is not None:
            # Cancelling Stop must not cancel the pending operation's completion.
            await asyncio.shield(operation)
        if self.grant is not None:
            snapshot = self.grant["buffer"]
            assert isinstance(snapshot, bytearray)
            snapshot[:] = b"\0" * len(snapshot)
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

    async def upload_file(
        self, args: dict[str, object], *, cancelled: Callable[[], bool] | None = None
    ) -> dict[str, object]:
        _, outcome = await self._upload(args, cancelled)
        return outcome

    async def upload(self, args: dict[str, object], *, cancelled: Callable[[], bool] | None = None) -> str:
        receipt, _ = await self._upload(args, cancelled)
        return receipt

    async def _upload(
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
        try:
            if (
                chosen is None
                or set(args) != {"grant_id"}
                or args["grant_id"] != chosen["id"]
                or chosen["session"] != self.active_session
                or chosen["expires_at"] <= milliseconds()
                or interrupted()
                or self.page.url != self.url
                or not await wait_for_decision(
                    lambda: self.control.evaluate(ELIGIBLE, [self.document, self.record, self.record_id]), interrupted
                )
            ):
                raise ValueError("File transfer refused")
            approval = FileApproval(owner=self._state, active=True)
            token = approving_owner.set(approval)
            try:
                approved = await wait_for_decision(
                    lambda: self.approve(
                        MappingProxyType(
                            {
                                "label": "Approved fixture document",
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
                approved is not True
                or self.revoked
                or interrupted()
                or self.grant is not chosen
                or chosen["expires_at"] <= milliseconds()
                or chosen["session"] != self.active_session
                or self.page.url != self.url
                or not eligible
            ):
                raise ValueError("File transfer refused")
            self.grant = None
            admitted = True
            self.last = unknown()
            self._state.transfer("in_progress", "unknown")
            snapshot = chosen["buffer"]
            assert isinstance(snapshot, bytearray)
            # Python Playwright requires immutable bytes. The native transport owns
            # that one bounded copy; wiping our staging does not erase renderer copies.
            await self.control.set_input_files(
                {
                    "name": "approved.bin",
                    "mimeType": "application/octet-stream",
                    "buffer": bytes(snapshot),
                }
            )
            if (
                not self.revoked
                and not interrupted()
                and chosen["session"] == self.active_session
                and self.page.url == self.url
                and await wait_for_decision(
                    lambda: self.control.evaluate(ELIGIBLE, [self.document, self.record, self.record_id]), interrupted
                )
            ):
                self.last = {
                    "status": "completed",
                    "attempted": True,
                    "completed": True,
                    "count": chosen["count"],
                    "sha256": chosen["sha256"],
                }
        except asyncio.CancelledError:
            task_cancelled = True
            self.last = unknown() if admitted else refusal()
            self.revoked = True
            if not admitted and chosen is not None:
                self.grant = None
                snapshot = chosen["buffer"]
                assert isinstance(snapshot, bytearray)
                snapshot[:] = b"\0" * len(snapshot)
            raise
        except Exception:
            self.last = unknown() if admitted else refusal()
            if (
                not admitted
                and chosen is not None
                and self.grant is chosen
                and (
                    interrupted() or chosen["expires_at"] <= milliseconds() or chosen["session"] != self.active_session
                )
            ):
                chosen["buffer"][:] = b"\0" * len(chosen["buffer"])
                self.grant = None
        finally:
            try:
                try:
                    was_interrupted = task_cancelled or interrupted()
                except Exception:
                    was_interrupted = True
                    self.last = unknown() if admitted else refusal()
                receipt = json.dumps(self.last)
                outcome = browser_outcome(receipt, was_interrupted, self._state.cleanup)
                if self.last["completed"]:
                    self._state.transfer("completed", "completed")
                elif was_interrupted:
                    self._state.transfer("interrupted", "unknown" if admitted else "none")
                else:
                    self._state.transfer("unknown" if admitted else "refused", "unknown" if admitted else "none")
            finally:
                if admitted:
                    assert chosen is not None
                    snapshot = chosen["buffer"]
                    assert isinstance(snapshot, bytearray)
                    snapshot[:] = b"\0" * len(snapshot)
                    if not self.last["completed"]:
                        self.revoked = True
                completion.set_result(None)
                self.work = None
                if self._state.cleanup == "pending":
                    try:
                        await self.stop()
                    except FileCleanupIncompleteError:
                        # Preserve the interrupted transfer's receipt; explicit Stop reports incomplete cleanup.
                        pass
        return receipt, outcome
