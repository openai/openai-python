from __future__ import annotations

import inspect
from uuid import uuid4
from typing import TYPE_CHECKING, Callable
from threading import Lock
from typing_extensions import Literal, TypedDict

from .._types import Headers
from .._base_client import _merge_headers

if TYPE_CHECKING:
    from .. import OpenAI, AsyncOpenAI


def rotated_idempotency_headers(client: OpenAI | AsyncOpenAI, extra: Headers | None) -> Headers | None:
    headers = extra or {}
    effective = _merge_headers(client._custom_headers, headers)
    if not any(name.lower() == "idempotency-key" for name in effective):
        return None
    return {
        **{name: value for name, value in headers.items() if name.lower() != "idempotency-key"},
        "Idempotency-Key": f"stainless-python-retry-{uuid4()}",
    }


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
