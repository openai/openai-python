# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .items import (
        Items as Items,
        AsyncItems as AsyncItems,
        ItemsWithRawResponse as ItemsWithRawResponse,
        AsyncItemsWithRawResponse as AsyncItemsWithRawResponse,
        ItemsWithStreamingResponse as ItemsWithStreamingResponse,
        AsyncItemsWithStreamingResponse as AsyncItemsWithStreamingResponse,
    )
    from .conversations import (
        Conversations as Conversations,
        AsyncConversations as AsyncConversations,
        ConversationsWithRawResponse as ConversationsWithRawResponse,
        AsyncConversationsWithRawResponse as AsyncConversationsWithRawResponse,
        ConversationsWithStreamingResponse as ConversationsWithStreamingResponse,
        AsyncConversationsWithStreamingResponse as AsyncConversationsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Items": (".items", "Items"),
        "AsyncItems": (".items", "AsyncItems"),
        "ItemsWithRawResponse": (".items", "ItemsWithRawResponse"),
        "AsyncItemsWithRawResponse": (".items", "AsyncItemsWithRawResponse"),
        "ItemsWithStreamingResponse": (".items", "ItemsWithStreamingResponse"),
        "AsyncItemsWithStreamingResponse": (".items", "AsyncItemsWithStreamingResponse"),
        "Conversations": (".conversations", "Conversations"),
        "AsyncConversations": (".conversations", "AsyncConversations"),
        "ConversationsWithRawResponse": (".conversations", "ConversationsWithRawResponse"),
        "AsyncConversationsWithRawResponse": (".conversations", "AsyncConversationsWithRawResponse"),
        "ConversationsWithStreamingResponse": (".conversations", "ConversationsWithStreamingResponse"),
        "AsyncConversationsWithStreamingResponse": (".conversations", "AsyncConversationsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "conversations",
        "items",
    }

    def __getattr__(name: str) -> _t.Any:
        import importlib

        if name in _EXPORTS:
            module_name, symbol_name = _EXPORTS[name]
            value = getattr(importlib.import_module(module_name, __name__), symbol_name)
        elif name in _SUBMODULES:
            value = importlib.import_module(f".{name}", __name__)
        else:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        globals()[name] = value
        return value

    def __dir__() -> list[str]:
        return sorted(set(globals()) | set(_EXPORTS) | _SUBMODULES)


__all__ = [
    "Items",
    "AsyncItems",
    "ItemsWithRawResponse",
    "AsyncItemsWithRawResponse",
    "ItemsWithStreamingResponse",
    "AsyncItemsWithStreamingResponse",
    "Conversations",
    "AsyncConversations",
    "ConversationsWithRawResponse",
    "AsyncConversationsWithRawResponse",
    "ConversationsWithStreamingResponse",
    "AsyncConversationsWithStreamingResponse",
]
