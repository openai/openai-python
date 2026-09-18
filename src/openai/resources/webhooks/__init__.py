# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .webhooks import (
        Webhooks as Webhooks,
        AsyncWebhooks as AsyncWebhooks,
        WebhooksWithRawResponse as WebhooksWithRawResponse,
        AsyncWebhooksWithRawResponse as AsyncWebhooksWithRawResponse,
        WebhooksWithStreamingResponse as WebhooksWithStreamingResponse,
        AsyncWebhooksWithStreamingResponse as AsyncWebhooksWithStreamingResponse,
    )
    from .event_types import (
        EventTypes as EventTypes,
        AsyncEventTypes as AsyncEventTypes,
        EventTypesWithRawResponse as EventTypesWithRawResponse,
        AsyncEventTypesWithRawResponse as AsyncEventTypesWithRawResponse,
        EventTypesWithStreamingResponse as EventTypesWithStreamingResponse,
        AsyncEventTypesWithStreamingResponse as AsyncEventTypesWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "EventTypes": (".event_types", "EventTypes"),
        "AsyncEventTypes": (".event_types", "AsyncEventTypes"),
        "EventTypesWithRawResponse": (".event_types", "EventTypesWithRawResponse"),
        "AsyncEventTypesWithRawResponse": (".event_types", "AsyncEventTypesWithRawResponse"),
        "EventTypesWithStreamingResponse": (".event_types", "EventTypesWithStreamingResponse"),
        "AsyncEventTypesWithStreamingResponse": (".event_types", "AsyncEventTypesWithStreamingResponse"),
        "Webhooks": (".webhooks", "Webhooks"),
        "AsyncWebhooks": (".webhooks", "AsyncWebhooks"),
        "WebhooksWithRawResponse": (".webhooks", "WebhooksWithRawResponse"),
        "AsyncWebhooksWithRawResponse": (".webhooks", "AsyncWebhooksWithRawResponse"),
        "WebhooksWithStreamingResponse": (".webhooks", "WebhooksWithStreamingResponse"),
        "AsyncWebhooksWithStreamingResponse": (".webhooks", "AsyncWebhooksWithStreamingResponse"),
    }
    _SUBMODULES = {
        "event_types",
        "webhooks",
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
    "EventTypes",
    "AsyncEventTypes",
    "EventTypesWithRawResponse",
    "AsyncEventTypesWithRawResponse",
    "EventTypesWithStreamingResponse",
    "AsyncEventTypesWithStreamingResponse",
    "Webhooks",
    "AsyncWebhooks",
    "WebhooksWithRawResponse",
    "AsyncWebhooksWithRawResponse",
    "WebhooksWithStreamingResponse",
    "AsyncWebhooksWithStreamingResponse",
]
