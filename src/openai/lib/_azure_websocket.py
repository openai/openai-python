from __future__ import annotations

from typing_extensions import override

from websockets.uri import parse_uri
from websockets.exceptions import SecurityError
from websockets.asyncio.client import connect

__all__ = ["_AzureWebSocketConnect"]


class _AzureWebSocketConnect(connect):
    """Keep Azure's WebSocket authentication on the original origin."""

    @override
    def process_redirect(self, exc: Exception) -> Exception | str:
        uri_or_exc = super().process_redirect(exc)
        if isinstance(uri_or_exc, str):
            current = parse_uri(self.uri)
            target = parse_uri(uri_or_exc)
            if (current.secure, current.host, current.port) != (target.secure, target.host, target.port):
                return SecurityError("Cross-origin Azure WebSocket redirects are not allowed")
        return uri_or_exc
