from __future__ import annotations

import sys
import importlib
from typing import Any, Protocol, cast

import httpx

from ._constants import DEFAULT_TIMEOUT, DEFAULT_CONNECTION_LIMITS


class _Httpx2Module(Protocol):
    Auth: type[httpx.Auth]
    Client: type[httpx.Client]
    AsyncClient: type[httpx.AsyncClient]
    Timeout: type[httpx.Timeout]
    Limits: type[httpx.Limits]
    TimeoutException: type[httpx.TimeoutException]
    HTTPStatusError: type[httpx.HTTPStatusError]
    StreamConsumed: type[httpx.StreamConsumed]
    RequestNotRead: type[httpx.RequestNotRead]


def _loaded_httpx2() -> _Httpx2Module | None:
    module = sys.modules.get("httpx2")
    if module is None:
        return None
    return cast(_Httpx2Module, module)


def _supports_httpx2() -> bool:
    return sys.version_info >= (3, 10)


def _require_httpx2() -> _Httpx2Module:
    if not _supports_httpx2():
        raise RuntimeError(
            "HTTPX2 requires Python 3.10 or later; install the httpx2 extra on a supported interpreter: "
            "pip install 'openai[httpx2]'"
        )

    try:
        module = importlib.import_module("httpx2")
    except ImportError:
        raise RuntimeError("To use HTTPX2, install the httpx2 extra: pip install 'openai[httpx2]'") from None

    return cast(_Httpx2Module, module)


def is_httpx2_sync_client(value: object) -> bool:
    module = _loaded_httpx2()
    return module is not None and isinstance(value, module.Client)


def is_httpx2_async_client(value: object) -> bool:
    module = _loaded_httpx2()
    return module is not None and isinstance(value, module.AsyncClient)


def normalize_httpx_timeout(value: float | httpx.Timeout | None) -> float | httpx.Timeout | None:
    module = _loaded_httpx2()
    if module is not None and isinstance(value, module.Timeout):
        return httpx.Timeout(**value.as_dict())
    return value


def normalize_httpx2_timeout(value: float | httpx.Timeout | None) -> float | httpx.Timeout | None:
    if isinstance(value, httpx.Timeout):
        return _require_httpx2().Timeout(**value.as_dict())
    return value


def normalize_httpx2_auth(value: httpx.Auth) -> httpx.Auth:
    if type(value) is httpx.Auth:
        return _require_httpx2().Auth()
    return value


def timeout_exceptions() -> tuple[type[httpx.TimeoutException], ...]:
    module = _loaded_httpx2()
    if module is None:
        return (httpx.TimeoutException,)
    return (httpx.TimeoutException, module.TimeoutException)


def status_exceptions() -> tuple[type[httpx.HTTPStatusError], ...]:
    module = _loaded_httpx2()
    if module is None:
        return (httpx.HTTPStatusError,)
    return (httpx.HTTPStatusError, module.HTTPStatusError)


def stream_consumed_exceptions() -> tuple[type[httpx.StreamConsumed], ...]:
    module = _loaded_httpx2()
    if module is None:
        return (httpx.StreamConsumed,)
    return (httpx.StreamConsumed, module.StreamConsumed)


def request_not_read_exceptions() -> tuple[type[httpx.RequestNotRead], ...]:
    module = _loaded_httpx2()
    if module is None:
        return (httpx.RequestNotRead,)
    return (httpx.RequestNotRead, module.RequestNotRead)


def _set_httpx2_defaults(kwargs: dict[str, Any]) -> _Httpx2Module:
    module = _require_httpx2()
    timeout = kwargs.get("timeout", DEFAULT_TIMEOUT)
    kwargs["timeout"] = normalize_httpx2_timeout(timeout)

    limits = kwargs.get("limits", DEFAULT_CONNECTION_LIMITS)
    if isinstance(limits, httpx.Limits):
        kwargs["limits"] = module.Limits(
            max_connections=limits.max_connections,
            max_keepalive_connections=limits.max_keepalive_connections,
            keepalive_expiry=limits.keepalive_expiry,
        )

    kwargs.setdefault("follow_redirects", True)
    return module


def DefaultHttpx2Client(**kwargs: Any) -> httpx.Client:
    """Create an experimental HTTPX2 client with the SDK's recommended defaults."""
    module = _set_httpx2_defaults(kwargs)
    return module.Client(**kwargs)


def DefaultAsyncHttpx2Client(**kwargs: Any) -> httpx.AsyncClient:
    """Create an experimental async HTTPX2 client with the SDK's recommended defaults."""
    module = _set_httpx2_defaults(kwargs)
    return module.AsyncClient(**kwargs)
