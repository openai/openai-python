from __future__ import annotations

from ._websocket import _WebSocketConnect

__all__ = ["_AzureWebSocketConnect"]


class _AzureWebSocketConnect(_WebSocketConnect):
    """Keep Azure's WebSocket authentication on the original origin."""

    _redirect_error_message = "Cross-origin Azure WebSocket redirects are not allowed"
