"""Variant of httpx_aiohttp for `httpx2 <https://github.com/pydantic/httpx2>`_.

Requires the optional ``httpx2`` dependency: ``pip install httpx-aiohttp[httpx2]``.
"""

from typing import TYPE_CHECKING, Any

from .client import Httpx2AiohttpClient

if TYPE_CHECKING:
    from .transport import AiohttpTransport

__all__ = ["AiohttpTransport", "Httpx2AiohttpClient"]


def __getattr__(name: str) -> Any:
    if name == "AiohttpTransport":
        from .transport import AiohttpTransport

        globals()[name] = AiohttpTransport
        return AiohttpTransport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
