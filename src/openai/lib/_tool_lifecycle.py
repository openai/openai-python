from __future__ import annotations

import inspect
from uuid import uuid4
from typing import TYPE_CHECKING, Any, Callable
from threading import Lock
from typing_extensions import Literal, TypedDict

from .._types import Headers
from .._base_client import _merge_headers

if TYPE_CHECKING:
    from .. import OpenAI, AsyncOpenAI


def rotated_idempotency_headers(client: OpenAI | AsyncOpenAI, extra: Headers | None) -> Headers | None:
    headers = dict(extra) if extra is not None else {}
    effective = _merge_headers(client._custom_headers, headers)
    if not any(name.lower() == "idempotency-key" for name in effective):
        return headers if extra is not None else None
    return {
        **{name: value for name, value in headers.items() if name.lower() != "idempotency-key"},
        "Idempotency-Key": f"stainless-python-retry-{uuid4()}",
    }


def callable_flavor(method: Callable[..., object]) -> bool | None:
    """Report known awaitable results without invoking opaque driver wrappers."""
    target = inspect.unwrap(method)
    returns_awaitable = inspect.iscoroutinefunction(target)
    if not returns_awaitable and not inspect.isroutine(target):
        returns_awaitable = inspect.iscoroutinefunction(inspect.unwrap(target.__call__))
    if not returns_awaitable:
        try:
            annotation = inspect.signature(target).return_annotation
        except (TypeError, ValueError):
            return None
        if annotation is inspect.Signature.empty or annotation is Any or annotation is object:
            return None
        text = str(annotation)
        if text in ("Any", "typing.Any", "object", "builtins.object"):
            return None
        returns_awaitable = any(name in text for name in ("Awaitable[", "Coroutine[", "Future["))
    return returns_awaitable


class CloseStatus(TypedDict):
    status: Literal["closed", "draining"]


class ToolLifecycle:
    def __init__(self, name: str) -> None:
        self._name = name
        self._lock = Lock()
        self._active = False
        self._closed = False

    def enter(self) -> None:
        with self._lock:
            if self._closed:
                raise RuntimeError(f"{self._name} is closed.")
            if self._active:
                raise RuntimeError(f"{self._name} is busy with another call.")
            self._active = True

    def exit(self) -> None:
        with self._lock:
            self._active = False

    def close(self) -> CloseStatus:
        with self._lock:
            self._closed = True
            return {"status": "draining" if self._active else "closed"}


def invoke(handler: Callable[..., object], *args: object, cancelled: Callable[[], bool] | None) -> object:
    try:
        signature = inspect.signature(handler)
    except (TypeError, ValueError):
        return handler(*args)
    parameter = signature.parameters.get("cancelled")
    if (
        parameter is not None
        and parameter.kind in (parameter.KEYWORD_ONLY, parameter.POSITIONAL_OR_KEYWORD)
        and "cancelled" not in signature.bind_partial(*args).arguments
    ):
        return handler(*args, cancelled=cancelled)
    return handler(*args)
