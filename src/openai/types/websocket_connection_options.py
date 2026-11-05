# Native WebSocket options are maintained by the SDK.

from __future__ import annotations

from typing import TYPE_CHECKING
from typing_extensions import Sequence, TypeAlias, TypedDict

__all__ = ["SyncWebSocketConnectionOptions", "WebSocketConnectionOptions", "WebsocketConnectionOptions"]

if TYPE_CHECKING:
    from websockets import Subprotocol
    from websockets.extensions import ClientExtensionFactory


class SyncWebSocketConnectionOptions(TypedDict, total=False):
    """Native options for synchronous WebSocket connections.

    See https://websockets.readthedocs.io/en/stable/reference/sync/client.html#websockets.sync.client.connect
    """

    extensions: Sequence[ClientExtensionFactory] | None
    """List of supported extensions, in order in which they should be negotiated and run."""

    subprotocols: Sequence[Subprotocol] | None
    """List of supported subprotocols, in order of decreasing preference."""

    compression: str | None
    """With unlimited messages (`max_size=None`, the SDK default), compression
    defaults to `None`. With a finite `max_size`, including zero, the native
    `websockets` default enables permessage-deflate. Set `compression="deflate"`
    or `compression=None` to choose explicitly. Factories provided in
    `extensions` can still negotiate compression when this option is `None`.
    """

    # limits
    max_size: int | None
    """Maximum size of incoming messages in bytes. None disables the limit."""

    max_queue: int | None | tuple[int | None, int | None]
    """For synchronous connections, this requires websockets >=14. High-water mark of the buffer where frames are received. It defaults to 16 frames. The low-water mark defaults to max_queue // 4. You may pass a (high, low) tuple to set the high-water and low-water marks. If you want to disable flow control entirely, you may set it to None, although that’s a bad idea."""


class WebSocketConnectionOptions(SyncWebSocketConnectionOptions, total=False):
    """Native options for asynchronous WebSocket connections.

    See https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html#websockets.asyncio.client.connect
    """

    write_limit: int | tuple[int, int | None]
    """High-water mark of write buffer in bytes. It is passed to set_write_buffer_limits(). It defaults to 32 KiB. You may pass a (high, low) tuple to set the high-water and low-water marks."""


# Backward compatibility for pre-rename imports.
WebsocketConnectionOptions: TypeAlias = WebSocketConnectionOptions
