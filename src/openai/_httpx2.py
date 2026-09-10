from __future__ import annotations

import sys
from typing import Any, Protocol, cast

import httpx2

from ._constants import DEFAULT_TIMEOUT, DEFAULT_CONNECTION_LIMITS


class _LegacyHttpxModule(Protocol):
    Auth: type[httpx2.Auth]
    Client: type[httpx2.Client]
    AsyncClient: type[httpx2.AsyncClient]
    URL: type[httpx2.URL]
    Response: type[httpx2.Response]
    Timeout: type[httpx2.Timeout]
    Limits: type[httpx2.Limits]
    TimeoutException: type[httpx2.TimeoutException]
    HTTPStatusError: type[httpx2.HTTPStatusError]
    StreamConsumed: type[httpx2.StreamConsumed]
    RequestNotRead: type[httpx2.RequestNotRead]


def _loaded_legacy_httpx() -> _LegacyHttpxModule | None:
    module = sys.modules.get("httpx")
    return cast(_LegacyHttpxModule, module) if module is not None else None


def is_httpx2_sync_client(value: object) -> bool:
    return isinstance(value, httpx2.Client)


def is_httpx2_async_client(value: object) -> bool:
    return isinstance(value, httpx2.AsyncClient)


def is_legacy_httpx_sync_client(value: object) -> bool:
    module = _loaded_legacy_httpx()
    return module is not None and isinstance(value, module.Client)


def is_legacy_httpx_async_client(value: object) -> bool:
    module = _loaded_legacy_httpx()
    return module is not None and isinstance(value, module.AsyncClient)


def normalize_httpx_url(value: str | httpx2.URL) -> httpx2.URL:
    if isinstance(value, httpx2.URL):
        return value

    module = _loaded_legacy_httpx()
    legacy_value: object = value
    if module is not None and isinstance(legacy_value, module.URL):
        return httpx2.URL(str(legacy_value))

    return httpx2.URL(value)


def http_response_types() -> tuple[type[httpx2.Response], ...]:
    module = _loaded_legacy_httpx()
    return (httpx2.Response,) if module is None else (httpx2.Response, module.Response)


def normalize_httpx_timeout(value: float | httpx2.Timeout | None) -> float | httpx2.Timeout | None:
    module = _loaded_legacy_httpx()
    if module is not None and isinstance(value, module.Timeout):
        return httpx2.Timeout(**value.as_dict())
    return value


def normalize_httpx2_timeout(value: float | httpx2.Timeout | None) -> float | httpx2.Timeout | None:
    return normalize_httpx_timeout(value)


def normalize_legacy_httpx_timeout(value: float | httpx2.Timeout | None) -> float | httpx2.Timeout | None:
    module = _loaded_legacy_httpx()
    if module is not None and isinstance(value, httpx2.Timeout):
        return module.Timeout(**value.as_dict())
    return value


def normalize_httpx2_auth(value: httpx2.Auth) -> httpx2.Auth:
    module = _loaded_legacy_httpx()
    if module is not None and type(value) is module.Auth:
        return httpx2.Auth()
    return value


def normalize_legacy_httpx_auth(value: httpx2.Auth) -> httpx2.Auth:
    module = _loaded_legacy_httpx()
    if module is not None and type(value) is httpx2.Auth:
        return module.Auth()
    return value


def timeout_exceptions() -> tuple[type[httpx2.TimeoutException], ...]:
    module = _loaded_legacy_httpx()
    return (httpx2.TimeoutException,) if module is None else (httpx2.TimeoutException, module.TimeoutException)


def status_exceptions() -> tuple[type[httpx2.HTTPStatusError], ...]:
    module = _loaded_legacy_httpx()
    return (httpx2.HTTPStatusError,) if module is None else (httpx2.HTTPStatusError, module.HTTPStatusError)


def stream_consumed_exceptions() -> tuple[type[httpx2.StreamConsumed], ...]:
    module = _loaded_legacy_httpx()
    return (httpx2.StreamConsumed,) if module is None else (httpx2.StreamConsumed, module.StreamConsumed)


def request_not_read_exceptions() -> tuple[type[httpx2.RequestNotRead], ...]:
    module = _loaded_legacy_httpx()
    return (httpx2.RequestNotRead,) if module is None else (httpx2.RequestNotRead, module.RequestNotRead)


def _set_httpx2_defaults(kwargs: dict[str, Any]) -> None:
    kwargs["timeout"] = normalize_httpx2_timeout(kwargs.get("timeout", DEFAULT_TIMEOUT))

    limits = kwargs.get("limits", DEFAULT_CONNECTION_LIMITS)
    module = _loaded_legacy_httpx()
    if module is not None and isinstance(limits, module.Limits):
        limits = httpx2.Limits(
            max_connections=limits.max_connections,
            max_keepalive_connections=limits.max_keepalive_connections,
            keepalive_expiry=limits.keepalive_expiry,
        )
    kwargs["limits"] = limits
    kwargs.setdefault("follow_redirects", True)


def DefaultHttpx2Client(**kwargs: Any) -> httpx2.Client:
    """Create an HTTPX2 client with the SDK's recommended defaults."""
    _set_httpx2_defaults(kwargs)
    return httpx2.Client(**kwargs)


def DefaultAsyncHttpx2Client(**kwargs: Any) -> httpx2.AsyncClient:
    """Create an async HTTPX2 client with the SDK's recommended defaults."""
    _set_httpx2_defaults(kwargs)
    return httpx2.AsyncClient(**kwargs)
