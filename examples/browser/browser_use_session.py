"""Own a standalone browser-use Cloud browser; borrow its CDP browser for one task."""

from __future__ import annotations

import re
import asyncio
import inspect
import ipaddress
from uuid import UUID
from typing import Generic, TypeVar
from urllib.parse import urlsplit
from collections.abc import Callable, Awaitable
from typing_extensions import TypedDict

from browser_driver import PlaywrightBrowser, origin
from browser_use_sdk import (  # pyright: ignore[reportMissingTypeStubs] -- 3.4.2 has no py.typed marker
    AsyncBrowserUse,
)
from browserbase_session import Status, CleanupResult, _Cleanup as BorrowedCleanup, with_borrowed_browser
from playwright.async_api import Browser, BrowserType
from browser_use_sdk.generated.v2.models import (  # pyright: ignore[reportMissingTypeStubs] -- 3.4.2 has no py.typed marker
    BrowserSessionView,
    BrowserSessionStatus,
)

_T = TypeVar("_T")


def _standalone(actual: BrowserSessionView, expected: UUID) -> bool:
    return actual.id == expected and "agent_session_id" in actual.model_fields_set and actual.agent_session_id is None


class SessionResult(TypedDict, Generic[_T]):
    result: _T | None
    status: Status
    cleanup: _Cleanup


class BrowserUseError(Exception):
    def __init__(self, cleanup: _Cleanup) -> None:
        super().__init__("Browser session failed.")
        self.cleanup = cleanup


class BrowserUseCancelled(asyncio.CancelledError):
    def __init__(self, cleanup: _Cleanup) -> None:
        super().__init__("Browser session stopped.")
        self.cleanup = cleanup


class CleanupNotificationError(BrowserUseError):
    def __init__(self, cleanup: _Cleanup) -> None:
        super().__init__(cleanup)
        self.args = ("Browser cleanup notification failed.",)


class _Cleanup:
    def __init__(self) -> None:
        self._client: AsyncBrowserUse | None = None
        self._id: UUID | None = None
        self._browser: Browser | None = None
        self._inner: BorrowedCleanup | None = None
        self._drained = False
        self._complete = False
        self._attempt: asyncio.Task[CleanupResult] | None = None
        self._browser_close: asyncio.Task[None] | None = None

    def _save_inner(self, handle: BorrowedCleanup) -> None:
        self._inner = handle

    async def retry(self) -> CleanupResult:
        if not self._drained:
            raise BrowserUseError(self)
        if self._attempt is None or self._attempt.done():
            self._attempt = asyncio.create_task(self._once())
        return await asyncio.shield(self._attempt)

    async def _once(self) -> CleanupResult:
        if self._complete:
            return {"status": "complete"}
        try:
            local_ok = True
            if self._inner is not None:
                local_ok = (await self._inner.retry())["status"] == "complete"
                if local_ok:
                    self._inner = None
            if self._browser is not None and self._inner is None:
                if self._browser_close is None:
                    self._browser_close = asyncio.create_task(self._browser.close())
                    self._browser_close.add_done_callback(
                        lambda done: done.exception() if not done.cancelled() else None
                    )
                _, pending = await asyncio.wait({self._browser_close}, timeout=2.5)
                if pending:
                    local_ok = False
                else:
                    try:
                        self._browser_close.result()
                        self._browser = None
                    except (Exception, asyncio.CancelledError):
                        local_ok = False
                    finally:
                        self._browser_close = None
            if self._client is None or self._id is None:
                if self._client is not None:
                    await self._client.close()
                    self._client = None
                return {"status": "unverified"}
            actual = await self._client.browsers.get(str(self._id))
            if not _standalone(actual, self._id):
                return {"status": "unverified"}
            if actual.status is BrowserSessionStatus.active:
                await self._client.browsers.stop(str(self._id))
                actual = await self._client.browsers.get(str(self._id))
                if not _standalone(actual, self._id):
                    return {"status": "unverified"}
            if actual.status is not BrowserSessionStatus.stopped:
                return {"status": "pending"}
            if local_ok:
                await self._client.close()
                self._client = None
                self._complete = True
            return {"status": "complete" if self._complete else "pending"}
        except Exception:
            return {"status": "pending"}


async def with_standalone_browser(
    chromium: BrowserType,
    allowed_origins: list[str],
    work: Callable[[PlaywrightBrowser, Callable[[], bool]], Awaitable[_T]],
    *,
    api_key: str,
    base_url: str,
    on_cleanup: Callable[[_Cleanup], object],
    cancelled: Callable[[], bool] = lambda: False,
) -> SessionResult[_T]:
    """on_cleanup synchronously stores a private handle after drain and initial cleanup."""
    if not callable(on_cleanup):
        raise TypeError("on_cleanup must be callable.")
    cleanup = _Cleanup()
    stopped = asyncio.Event()

    def is_stopped() -> bool:
        if not stopped.is_set() and cancelled():
            stopped.set()
        return stopped.is_set()

    def check() -> None:
        if is_stopped():
            raise BrowserUseCancelled(cleanup)

    async def admitted() -> SessionResult[_T]:
        result = None
        failed = False
        notification_failed = False
        try:
            check()
            if (
                not isinstance(api_key, str)  # pyright: ignore[reportUnnecessaryIsInstance] -- validate caller at runtime
                or not api_key.strip()
                or not isinstance(base_url, str)  # pyright: ignore[reportUnnecessaryIsInstance] -- validate caller at runtime
                or not base_url.strip()
                or not callable(work)
                or not isinstance(allowed_origins, list)  # pyright: ignore[reportUnnecessaryIsInstance] -- validate caller at runtime
                or not allowed_origins
            ):
                raise BrowserUseError(cleanup)
            destination = urlsplit(base_url)
            host = destination.hostname
            # Accessing port also checks malformed or out-of-range port numbers.
            _ = destination.port
            try:
                loopback = host == "localhost" or (host is not None and ipaddress.ip_address(host).is_loopback)
            except ValueError:
                loopback = False
            if (
                re.fullmatch(r"https?://[^/?#@\\\s]+(?:[/?][^#\\\s]*)?", base_url, flags=re.IGNORECASE) is None
                or not host
                or destination.username is not None
                or destination.password is not None
                or destination.fragment
                or (destination.scheme != "https" and not (destination.scheme == "http" and loopback))
            ):
                raise BrowserUseError(cleanup)
            origins = tuple(allowed_origins)
            for configured in origins:
                parsed = urlsplit(configured)
                if (
                    parsed.scheme not in ("http", "https")
                    or parsed.username is not None
                    or parsed.password is not None
                    or parsed.path
                    or parsed.query
                    or parsed.fragment
                ):
                    raise BrowserUseError(cleanup)
                origin(configured)
            cleanup._client = AsyncBrowserUse(api_key=api_key, base_url=base_url, timeout=2.5, max_retries=0)
            created = await cleanup._client.browsers.create(
                timeout=1,
                proxy_country_code=None,
                enableRecording=False,
                browser_screen_width=1024,
                browser_screen_height=768,
                allow_resizing=False,
            )
            cleanup._id = created.id
            check()
            actual = await cleanup._client.browsers.get(str(cleanup._id))
            check()
            if (
                not _standalone(actual, cleanup._id)
                or actual.status is not BrowserSessionStatus.active
                or not actual.cdp_url
            ):
                raise BrowserUseError(cleanup)
            cleanup._browser = await chromium.connect_over_cdp(actual.cdp_url, timeout=2500)
            check()
            outcome = await with_borrowed_browser(
                cleanup._browser,
                {"allowed_origins": origins},
                work,
                cancelled=is_stopped,
                on_cleanup=cleanup._save_inner,
            )
            result = outcome["result"]
            check()
        except (Exception, asyncio.CancelledError):
            failed = True
        finally:
            cleanup._drained = True
            status = await cleanup.retry()
            try:
                notification = on_cleanup(cleanup)
                if inspect.isawaitable(notification):
                    if inspect.iscoroutine(notification):
                        notification.close()
                    notification_failed = True
            except (Exception, asyncio.CancelledError):
                notification_failed = True
        if stopped.is_set():
            raise BrowserUseCancelled(cleanup)
        if failed:
            raise BrowserUseError(cleanup)
        if notification_failed:
            raise CleanupNotificationError(cleanup)
        return {"result": result, "status": status["status"], "cleanup": cleanup}

    lifetime = asyncio.create_task(admitted())
    outer_cancel = False
    error = None
    value = None
    while True:
        try:
            value = await asyncio.shield(lifetime)
            break
        except asyncio.CancelledError:
            if lifetime.done():
                error = BrowserUseCancelled(cleanup)
                break
            outer_cancel = True
            stopped.set()
        except CleanupNotificationError:
            error = CleanupNotificationError(cleanup)
            break
        except Exception:
            error = BrowserUseError(cleanup)
            break
    if outer_cancel or stopped.is_set():
        raise BrowserUseCancelled(cleanup) from None
    if error:
        raise error from None
    assert value is not None
    return value
