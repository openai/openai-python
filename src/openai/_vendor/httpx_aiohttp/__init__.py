"""Variant of httpx_aiohttp for `httpx2 <https://github.com/pydantic/httpx2>`_.

Requires the optional ``httpx2`` dependency: ``pip install httpx-aiohttp[httpx2]``.
"""

from .client import Httpx2AiohttpClient
from .transport import AiohttpTransport

__all__ = ["AiohttpTransport", "Httpx2AiohttpClient"]
