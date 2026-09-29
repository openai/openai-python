from __future__ import annotations

from typing_extensions import override

from websockets.uri import parse_uri
from websockets.version import version as websockets_version
from websockets.exceptions import SecurityError
from websockets.sync.client import ClientConnection as SyncWebSocketConnection
from websockets.asyncio.client import connect

__all__ = ["_WebSocketConnect", "_recv_bytes"]


def _recv_bytes(connection: SyncWebSocketConnection) -> bytes:
    if not websockets_version.startswith("13."):
        return connection.recv(decode=False)
    # websockets 13 decodes text frames unconditionally in its sync API.
    # Re-encoding preserves their wire bytes; binary messages are already bytes.
    message = connection.recv()
    return message.encode("utf-8") if isinstance(message, str) else message


class _WebSocketConnect(connect):
    """Keep WebSocket authentication on the original origin."""

    _redirect_error_message = "Cross-origin WebSocket redirects are not allowed"

    @override
    def process_redirect(self, exc: Exception) -> Exception | str:
        uri_or_exc = super().process_redirect(exc)
        if isinstance(uri_or_exc, str):
            current = parse_uri(self.uri)
            target = parse_uri(uri_or_exc)
            if (current.secure, current.host, current.port) != (target.secure, target.host, target.port):
                return SecurityError(self._redirect_error_message)
        return uri_or_exc
