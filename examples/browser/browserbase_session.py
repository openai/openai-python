"""Generic browser session lifetime. Provider client, connection grants and logs belong to caller."""

from __future__ import annotations

import re
import time
import asyncio
import inspect
from typing import TYPE_CHECKING, Generic, Literal, TypeVar
from urllib.parse import urlsplit
from collections.abc import Callable, Awaitable
from typing_extensions import TypedDict, NotRequired

if TYPE_CHECKING:
    from browserbase import AsyncBrowserbase
    from playwright.async_api import Browser, BrowserType, BrowserContext, WebSocketRoute

from browser_driver import PlaywrightBrowser, origin

TERMINAL = frozenset(("COMPLETED", "TIMED_OUT", "ERROR"))
LIVE = frozenset(("PENDING", "RUNNING"))
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")


_T = TypeVar("_T")
Status = Literal["complete", "pending", "unverified"]


class SessionConfig(TypedDict):
    allowed_origins: list[str] | tuple[str, ...]
    project_id: NotRequired[str]


class CleanupResult(TypedDict):
    status: Status


class SessionResult(TypedDict, Generic[_T]):
    result: _T | None
    status: Status
    cleanup: _Cleanup


class BrowserSessionError(Exception):
    def __init__(self, cleanup: _Cleanup) -> None:
        super().__init__("Browser session failed.")
        self.cleanup = cleanup


class BrowserSessionCancelled(asyncio.CancelledError):
    def __init__(self, cleanup: _Cleanup) -> None:
        super().__init__("Browser session stopped.")
        self.cleanup = cleanup


class BrowserCleanupNotificationError(BrowserSessionError):
    def __init__(self, cleanup: _Cleanup) -> None:
        super().__init__(cleanup)
        self.args = ("Browser cleanup notification failed.",)


class _Cleanup:
    def __init__(self, client: AsyncBrowserbase | None, owned: bool) -> None:
        self._client = client
        self._owned = owned
        self._context: BrowserContext | None = None
        self._browser: Browser | None = None
        self._id: str | None = None
        self._project: str | None = None
        self._drained = False
        self._complete = False
        self._creating = False
        self._opening: asyncio.Task[PlaywrightBrowser] | None = None
        self._attempt: asyncio.Task[CleanupResult] | None = None
        self._context_close: asyncio.Task[None] | None = None
        self._browser_close: asyncio.Task[None] | None = None

    async def retry(self) -> CleanupResult:
        if not self._drained:
            raise BrowserSessionError(self)
        if self._attempt is None or self._attempt.done():
            self._attempt = asyncio.create_task(self._once())
        return await asyncio.shield(self._attempt)

    async def _once(self) -> CleanupResult:
        if self._complete:
            return {"status": "complete"}
        local_ok = not self._creating
        local_deadline = time.monotonic() + 2.5
        if self._context is not None:
            if self._context_close is None:
                self._context_close = asyncio.create_task(self._context.close())
                self._context_close.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            _, pending = await asyncio.wait({self._context_close}, timeout=max(0, local_deadline - time.monotonic()))
            if pending:
                local_ok = False
            else:
                try:
                    self._context_close.result()
                    self._context = None
                except (Exception, asyncio.CancelledError):
                    local_ok = False
                finally:
                    self._context_close = None
        if self._owned and self._browser is not None and self._context_close is None:
            if self._browser_close is None:
                self._browser_close = asyncio.create_task(self._browser.close())
                self._browser_close.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            _, pending = await asyncio.wait({self._browser_close}, timeout=max(0, local_deadline - time.monotonic()))
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
        if not self._owned:
            self._complete = local_ok
            return {"status": "complete" if self._complete else "pending"}
        if self._id is None:
            return {"status": "unverified"}
        deadline = time.monotonic() + 2.5
        sent = False
        try:
            assert self._client is not None and self._project is not None
            for _ in range(3):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                actual = await self._client.sessions.retrieve(self._id, timeout=remaining)
                if actual.id != self._id or actual.project_id != self._project or actual.status not in LIVE | TERMINAL:
                    return {"status": "pending"}
                if actual.status in TERMINAL:
                    self._complete = local_ok
                    return {"status": "complete" if self._complete else "pending"}
                if not sent:
                    sent = True
                    await self._client.sessions.update(
                        self._id,
                        status="REQUEST_RELEASE",
                        project_id=self._project,
                        timeout=max(0.001, deadline - time.monotonic()),
                    )
        except Exception:
            return {"status": "pending"}
        return {"status": "pending"}


async def with_browserbase_session(
    client: AsyncBrowserbase,
    chromium: BrowserType,
    config: SessionConfig,
    work: Callable[[PlaywrightBrowser, Callable[[], bool]], Awaitable[_T]],
    *,
    on_cleanup: Callable[[_Cleanup], object],
    cancelled: Callable[[], bool] = lambda: False,
) -> SessionResult[_T]:
    """on_cleanup must synchronously store the private handle after drain and initial cleanup."""
    return await _scope(client, chromium, None, config, work, on_cleanup, cancelled, True)


async def with_borrowed_browser(
    browser: Browser,
    config: SessionConfig,
    work: Callable[[PlaywrightBrowser, Callable[[], bool]], Awaitable[_T]],
    *,
    on_cleanup: Callable[[_Cleanup], object],
    cancelled: Callable[[], bool] = lambda: False,
) -> SessionResult[_T]:
    """Close only the new context; on_cleanup receives the private post-drain handle."""
    return await _scope(None, None, browser, config, work, on_cleanup, cancelled, False)


async def _scope(
    client: AsyncBrowserbase | None,
    chromium: BrowserType | None,
    browser: Browser | None,
    config: SessionConfig,
    work: Callable[[PlaywrightBrowser, Callable[[], bool]], Awaitable[_T]],
    on_cleanup: Callable[[_Cleanup], object],
    cancelled: Callable[[], bool],
    owned: bool,
) -> SessionResult[_T]:
    if not callable(on_cleanup):
        raise TypeError("on_cleanup must be callable.")
    stopped = asyncio.Event()
    cleanup = _Cleanup(None, owned)
    cleanup._browser = browser

    def is_stopped() -> bool:
        if not stopped.is_set() and cancelled():
            stopped.set()
        return stopped.is_set()

    def check() -> None:
        if is_stopped():
            raise BrowserSessionCancelled(cleanup)

    async def admitted() -> SessionResult[_T]:
        failed = False
        result = None
        notification_failed = False
        try:
            check()
            if (
                not isinstance(config, dict)  # pyright: ignore[reportUnnecessaryIsInstance]  -- runtime caller validation
                or not callable(work)
                or not isinstance(config.get("allowed_origins"), (list, tuple))  # pyright: ignore[reportUnnecessaryIsInstance] -- runtime caller validation
                or not config["allowed_origins"]
                or any(
                    k in config
                    for k in (
                        "ownedFixture",
                        "owned_fixture_urls",
                        "publicValues",
                        "public_values",
                        "publicViewports",
                        "public_viewports",
                    )
                )
            ):
                raise BrowserSessionError(cleanup)
            allowed: set[str] = set()
            for configured in config["allowed_origins"]:
                parsed = urlsplit(configured)
                if (
                    parsed.scheme not in ("http", "https")
                    or parsed.username is not None
                    or parsed.password is not None
                    or parsed.path
                    or parsed.query
                    or parsed.fragment
                ):
                    raise BrowserSessionError(cleanup)
                allowed.add(origin(configured))
            if owned:
                project = config.get("project_id")
                if not isinstance(project, str) or SAFE_ID.fullmatch(project) is None:
                    raise BrowserSessionError(cleanup)
                assert client is not None and chromium is not None
                cleanup._project = project
                # This borrows the caller's HTTPX pool; close neither the copy nor the supplied client.
                cleanup._client = client.with_options(max_retries=0)
                created = await cleanup._client.sessions.create(
                    api_timeout=60,
                    keep_alive=False,
                    project_id=project,
                    proxies=False,
                    browser_settings={
                        "record_session": False,
                        "log_session": False,
                        "solve_captchas": False,
                        "verified": False,
                        "advanced_stealth": False,
                    },
                    timeout=2.5,
                )
                if (
                    not isinstance(created.id, str)  # pyright: ignore[reportUnnecessaryIsInstance]  -- provider may return unvalidated data
                    or SAFE_ID.fullmatch(created.id) is None
                ):
                    raise BrowserSessionError(cleanup)
                cleanup._id = created.id
                if created.project_id != project:
                    raise BrowserSessionError(cleanup)
                check()
                cleanup._browser = await chromium.connect_over_cdp(created.connect_url, timeout=2500)
            check()
            assert cleanup._browser is not None
            creating_browser = cleanup._browser
            cleanup._creating = True

            async def open_context() -> PlaywrightBrowser:
                try:
                    check()
                    opened = await creating_browser.new_context(
                        service_workers="block", accept_downloads=False, viewport={"width": 1024, "height": 768}
                    )
                    cleanup._context = opened
                    check()
                    driver = PlaywrightBrowser(opened, allowed)
                    await opened.route("**/*", driver.guard)
                    check()

                    async def refuse_socket(route: WebSocketRoute) -> None:
                        await route.close()

                    await opened.route_web_socket("**/*", refuse_socket)
                    check()
                    return driver
                finally:
                    cleanup._creating = False
                    if cleanup._drained:
                        if cleanup._attempt is not None:
                            await asyncio.shield(cleanup._attempt)
                        await cleanup.retry()

            cleanup._opening = asyncio.create_task(open_context())
            cleanup._opening.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            while not cleanup._opening.done():
                check()
                await asyncio.wait({cleanup._opening}, timeout=0.02)
            driver = await cleanup._opening
            check()
            result = await work(driver, is_stopped)
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
            raise BrowserSessionCancelled(cleanup)
        if failed:
            raise BrowserSessionError(cleanup)
        if notification_failed:
            raise BrowserCleanupNotificationError(cleanup)
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
                error = BrowserSessionCancelled(cleanup)
                break
            outer_cancel = True
            stopped.set()
        except BrowserCleanupNotificationError:
            error = BrowserCleanupNotificationError(cleanup)
            break
        except Exception:
            error = BrowserSessionError(cleanup)
            break
    if outer_cancel or stopped.is_set():
        raise BrowserSessionCancelled(cleanup) from None
    if error:
        raise error from None
    assert value is not None
    return value
