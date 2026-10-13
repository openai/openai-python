"""Check file-owner disposal with finite local handles and explicit release gates."""

from __future__ import annotations

import json
import asyncio
import tempfile
from types import SimpleNamespace
from typing import Any, cast
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch

from file_upload import UploadOwner, milliseconds
from file_download import DownloadOwner, digest
from playwright.async_api import Page, JSHandle, ElementHandle


class Fixture:
    def __init__(
        self,
        *,
        fail_init: bool = False,
        hold: bool = False,
        fail_once: bool = False,
        held_read: int = 0,
        interrupt: BaseException | None = None,
    ) -> None:
        self.fail_init, self.hold, self.fail_once = fail_init, hold, fail_once
        self.captured = False
        self.interrupt = interrupt
        self.attempts = 0
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.held_read = held_read
        self.reads = self.assignments = 0
        self.read_entered = asyncio.Event()
        self.read_release = asyncio.Event()
        handle = object.__new__(ElementHandle)
        handle.evaluate = self.evaluate_control
        handle.set_input_files = self.set_files
        self.configuration: dict[str, object] = {
            "record": handle,
            "control": handle,
            "record_id": "fixture",
            "allow_upload": True,
            "allow_download": True,
        }

    @property
    def url(self) -> str:
        if self.captured and self.interrupt is not None:
            raise self.interrupt
        return "about:blank#changed" if self.fail_init and self.captured else "about:blank"

    async def evaluate_handle(self, _expression: str) -> JSHandle:
        self.captured = True
        return cast(JSHandle, self)

    async def evaluate_control(self, expression: str, arg: Any = None) -> bool:
        del expression, arg
        self.reads += 1
        if self.reads == self.held_read:
            self.read_entered.set()
            await self.read_release.wait()
        return True

    async def set_files(
        self, files: Any, *, timeout: float | timedelta | None = None, no_wait_after: bool | None = None
    ) -> None:
        del files, timeout, no_wait_after
        self.assignments += 1

    async def dispose(self) -> None:
        self.attempts += 1
        self.entered.set()
        if self.hold:
            await self.release.wait()
        if self.fail_once and self.attempts == 1:
            raise RuntimeError("Fixture disposal failed.")


async def refuse(_context: object) -> bool:
    return False


async def main() -> None:
    checks = 0
    result_bytes = b"Granted fixture result"
    requests = 0

    async def serve_result(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        nonlocal requests
        try:
            await reader.readuntil(b"\r\n\r\n")
            requests += 1
            writer.write(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: "
                + str(len(result_bytes)).encode()
                + b"\r\nConnection: close\r\n\r\n"
                + result_bytes
            )
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async with await asyncio.start_server(serve_result, "127.0.0.1", 0) as server:
        source: dict[str, object] = {
            "url": f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}/result",
            "count": len(result_bytes),
            "sha256": digest(result_bytes),
        }
        for reason in ("expiry", "session"):
            for boundary in ("issue", "transfer"):
                probe = Fixture()
                approval = {"agreed": False}

                async def approve_download(_context: object, approval: dict[str, bool] = approval) -> bool:
                    return approval["agreed"]

                download_owner = await DownloadOwner.create(cast(Page, probe), probe.configuration, approve_download)
                clock = {"now": milliseconds()}

                def download_now(clock: dict[str, int] = clock) -> int:
                    return clock["now"]

                before = requests
                try:
                    with patch("file_download.milliseconds", download_now):
                        first = download_owner.issue(source, clock["now"] + 10_000)
                        try:
                            download_owner.issue(source, clock["now"] + 20_000)
                        except ValueError:
                            pass
                        else:
                            raise AssertionError("A valid grant still occupies the only slot")
                        if reason == "expiry":
                            clock["now"] += 10_001
                        else:
                            download_owner.change_session()
                        if boundary == "transfer":
                            assert (await download_owner.download_file({"grant_id": first["grant_id"]}))[
                                "status"
                            ] == "refused"
                        second = download_owner.issue(source, clock["now"] + 20_000)
                        assert (await download_owner.download_file({"grant_id": first["grant_id"]}))[
                            "status"
                        ] == "refused"
                        assert (await download_owner.download_file({"grant_id": second["grant_id"]}))[
                            "status"
                        ] == "refused"
                        assert requests == before
                        approval["agreed"] = True
                        assert (await download_owner.download_file({"grant_id": second["grant_id"]}))[
                            "status"
                        ] == "completed"
                        assert download_owner.receipt()["sha256"] == source["sha256"]
                        assert requests == before + 1
                        try:
                            download_owner.issue(source, clock["now"] + 20_000)
                        except ValueError:
                            pass
                        else:
                            raise AssertionError("A second GET must never be issued")
                        checks += 1
                finally:
                    await download_owner.stop()
    for reason in ("expiry", "session"):
        for boundary in ("prepare", "transfer"):
            probe = Fixture()

            async def approve(_context: object) -> bool:
                return True

            owner = await UploadOwner.create(cast(Page, probe), probe.configuration, approve)
            clock = {"now": milliseconds()}

            def fixture_now(clock: dict[str, int] = clock) -> int:
                return clock["now"]

            try:
                with patch("file_upload.milliseconds", fixture_now):
                    name = owner.generated_name()
                    (owner.upload_root / name).write_text("First")
                    first = await owner.prepare(owner.upload_root, name, clock["now"] + 10_000)
                    try:
                        await owner.prepare(owner.upload_root, name, clock["now"] + 20_000)
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("A still-valid grant must occupy its slot")
                    if reason == "expiry":
                        clock["now"] += 10_001
                    else:
                        owner.change_session()
                    if boundary == "transfer":
                        assert (await owner.upload_file({"grant_id": first["grant_id"]}))["status"] == "refused"
                    (owner.upload_root / name).write_text("Second")
                    second = await owner.prepare(owner.upload_root, name, clock["now"] + 20_000)
                    assert (await owner.upload_file({"grant_id": first["grant_id"]}))["status"] == "refused"
                    assert probe.assignments == 0
                    assert (await owner.upload_file({"grant_id": second["grant_id"]}))["status"] == "completed"
                    assert owner.receipt()["sha256"] == digest(b"Second")
                    assert probe.assignments == 1
                    checks += 1
            finally:
                await owner.stop()
    probe = Fixture()
    prepare_entered, prepare_release = asyncio.Event(), asyncio.Event()

    async def hold_prepare() -> None:
        prepare_entered.set()
        await prepare_release.wait()

    owner = await UploadOwner.create(cast(Page, probe), probe.configuration, approve, hold_prepare)
    try:
        name = owner.generated_name()
        (owner.upload_root / name).write_text("Session fixture")
        waiting = asyncio.create_task(owner.prepare(owner.upload_root, name, milliseconds() + 20_000))
        await prepare_entered.wait()
        owner.change_session()
        prepare_release.set()
        try:
            await waiting
        except ValueError:
            pass
        else:
            raise AssertionError("Session changed during preparation but grant was issued")
        fresh = await owner.prepare(owner.upload_root, name, milliseconds() + 20_000)
        assert (await owner.upload_file({"grant_id": fresh["grant_id"]}))["status"] == "completed"
        assert probe.assignments == 1
        checks += 1
    finally:
        prepare_release.set()
        await owner.stop()
    for flags in (SimpleNamespace(O_NONBLOCK=4), SimpleNamespace(O_NOFOLLOW=256)):
        unavailable = Fixture()
        with patch("file_upload.os", flags):
            try:
                upload = await UploadOwner.create(cast(Page, unavailable), unavailable.configuration, refuse)
            except ValueError as error:
                assert "not supported on this platform" in str(error)
            else:
                await upload.stop()
                raise AssertionError("Unsupported uploads must fail before creating an owner.")
        assert not unavailable.captured
        checks += 1
    for owner_type in (UploadOwner, DownloadOwner):
        for interruption in (asyncio.CancelledError(), KeyboardInterrupt(), SystemExit()):
            failed = Fixture(interrupt=interruption)
            with tempfile.TemporaryDirectory() as scratch:
                with patch("tempfile.tempdir", scratch):
                    try:
                        await owner_type.create(cast(Page, failed), failed.configuration, refuse)
                    except BaseException as error:
                        assert error is interruption, "Initialization changed the caller's interruption."
                    else:
                        raise AssertionError("Interrupted initialization returned an owner")
                assert failed.attempts == 1, "Initialization must dispose its captured document"
                assert not list(Path(scratch).iterdir()), "Interrupted initialization left staging behind"
            checks += 1
        normal = Fixture()
        owner = await owner_type.create(cast(Page, normal), normal.configuration, refuse)
        await asyncio.gather(owner.stop(), owner.stop())
        await owner.stop()
        assert normal.attempts == 1 and owner.state()["cleanup"] == "completed"
        assert not owner.area.exists()
        checks += 1

        failed = Fixture(fail_init=True)
        try:
            await owner_type.create(cast(Page, failed), failed.configuration, refuse)
        except ValueError as error:
            assert "initialization refused" in str(error)
        else:
            raise AssertionError("Initialization must fail after the document changes.")
        assert failed.attempts == 1
        checks += 1

        held = Fixture(hold=True)
        waiting_owner = await owner_type.create(cast(Page, held), held.configuration, refuse)
        first = asyncio.create_task(waiting_owner.stop())
        await held.entered.wait()
        first.cancel()
        try:
            await first
        except asyncio.CancelledError:
            pass
        assert waiting_owner.state()["cleanup"] == "pending"
        second = asyncio.create_task(waiting_owner.stop())
        held.release.set()
        await second
        assert held.attempts == 1 and waiting_owner.state()["cleanup"] == "completed"
        checks += 1

        retry = Fixture(fail_once=True)
        retry_owner = await owner_type.create(cast(Page, retry), retry.configuration, refuse)
        try:
            await retry_owner.stop()
        except RuntimeError as error:
            assert "Fixture disposal failed" in str(error)
        else:
            raise AssertionError("The failed disposal must reach its caller.")
        assert retry_owner.state()["cleanup"] == "pending"
        await retry_owner.stop()
        assert retry.attempts == 2 and retry_owner.state()["cleanup"] == "completed"
        checks += 1

        slow_failure = Fixture(hold=True, fail_once=True)
        late_owner = await owner_type.create(cast(Page, slow_failure), slow_failure.configuration, refuse)
        incomplete = asyncio.create_task(late_owner.stop())
        await slow_failure.entered.wait()
        assert not late_owner.area.exists()
        try:
            await incomplete
        except Exception as error:
            assert "File cleanup incomplete" in str(error)
        else:
            raise AssertionError("Stop claimed unfinished handle cleanup")
        assert late_owner.state()["cleanup"] == "pending" and slow_failure.attempts == 1
        slow_failure.release.set()
        await asyncio.sleep(0.05)
        await late_owner.stop()
        assert slow_failure.attempts == 2 and late_owner.state()["cleanup"] == "completed"
        checks += 1

    for direction, held_read in (("upload", 1), ("download", 1), ("upload", 3)):
        probe = Fixture(hold=True, held_read=held_read)

        async def approve(_context: object) -> bool:
            return True

        subject: UploadOwner | DownloadOwner
        if direction == "upload":
            subject = await UploadOwner.create(cast(Page, probe), probe.configuration, approve)
            name = subject.generated_name()
            (subject.upload_root / name).write_bytes(b"Fixture")
            grant = await subject.prepare(subject.upload_root, name, milliseconds() + 20_000)
            transfer = asyncio.create_task(subject.upload_file({"grant_id": grant["grant_id"]}))
        else:
            subject = await DownloadOwner.create(cast(Page, probe), probe.configuration, approve)
            grant = subject.issue(
                {"url": "http://127.0.0.1:1/unused", "count": 7, "sha256": digest(b"Fixture")},
                milliseconds() + 20_000,
            )
            transfer = asyncio.create_task(subject.download_file({"grant_id": grant["grant_id"]}))
        await asyncio.wait_for(probe.read_entered.wait(), 2)
        if isinstance(subject, DownloadOwner):
            subject.change_session()
            try:
                subject.issue(
                    {"url": "http://127.0.0.1:1/unused", "count": 7, "sha256": digest(b"Fixture")},
                    milliseconds() + 20_000,
                )
            except ValueError:
                pass
            else:
                raise AssertionError("In-progress transfer cannot be superseded")
        stopping = asyncio.create_task(subject.stop())
        try:
            await asyncio.wait_for(probe.entered.wait(), 2)
            assert not subject.area.exists(), "Local staging must not wait for browser disposal"
            assert subject.state()["cleanup"] == "pending"
            done, waiting = await asyncio.wait({transfer, stopping}, timeout=4.2)
            assert not waiting and transfer in done, f"{direction}: held document blocked Stop"
            result = transfer.result()
            try:
                stopping.result()
            except Exception as error:
                assert "File cleanup incomplete" in str(error)
            else:
                raise AssertionError("Stop claimed unfinished handle cleanup")
            assert result == {
                "version": 1,
                "status": "interrupted",
                "effect": "unknown" if held_read == 3 else "none",
                "cleanup": "pending",
            }, result
            assert subject.receipt() == {
                "status": "unknown" if held_read == 3 else "refused",
                "attempted": held_read == 3,
                "completed": False,
            }
            assert probe.assignments == int(held_read == 3)
            if isinstance(subject, DownloadOwner):
                assert subject.stats["requests"] == 0
            assert probe.attempts == 1
            probe.read_release.set()
            probe.release.set()
            await subject.stop()
            assert probe.attempts == 1 and subject.state()["cleanup"] == "completed"
            checks += 1
        finally:
            probe.read_release.set()
            probe.release.set()
            await asyncio.gather(transfer, stopping, return_exceptions=True)
            await subject.stop()

    active = Fixture()
    started, release = asyncio.Event(), asyncio.Event()

    async def after_stat() -> None:
        started.set()
        await release.wait()

    uploading = await UploadOwner.create(cast(Page, active), active.configuration, refuse, after_stat)
    name = uploading.generated_name()
    (uploading.upload_root / name).write_text("Fixture")
    preparing = asyncio.create_task(uploading.prepare(uploading.upload_root, name, milliseconds() + 30_000))
    await started.wait()
    stopping = asyncio.create_task(uploading.stop())
    await asyncio.sleep(0)
    assert active.attempts == 0
    release.set()
    try:
        await preparing
    except ValueError:
        pass
    else:
        raise AssertionError("Preparation must stop before returning a grant.")
    await stopping
    assert active.attempts == 1
    checks += 1
    print(json.dumps({"checks": checks, "passed": True, "api_calls": 0, "vendor_calls": 0}))


if __name__ == "__main__":
    asyncio.run(main())
