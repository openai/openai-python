# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .responses import (
        Responses as Responses,
        AsyncResponses as AsyncResponses,
        ResponsesWithRawResponse as ResponsesWithRawResponse,
        AsyncResponsesWithRawResponse as AsyncResponsesWithRawResponse,
        ResponsesWithStreamingResponse as ResponsesWithStreamingResponse,
        AsyncResponsesWithStreamingResponse as AsyncResponsesWithStreamingResponse,
    )
    from .input_items import (
        InputItems as InputItems,
        AsyncInputItems as AsyncInputItems,
        InputItemsWithRawResponse as InputItemsWithRawResponse,
        AsyncInputItemsWithRawResponse as AsyncInputItemsWithRawResponse,
        InputItemsWithStreamingResponse as InputItemsWithStreamingResponse,
        AsyncInputItemsWithStreamingResponse as AsyncInputItemsWithStreamingResponse,
    )
    from .input_tokens import (
        InputTokens as InputTokens,
        AsyncInputTokens as AsyncInputTokens,
        InputTokensWithRawResponse as InputTokensWithRawResponse,
        AsyncInputTokensWithRawResponse as AsyncInputTokensWithRawResponse,
        InputTokensWithStreamingResponse as InputTokensWithStreamingResponse,
        AsyncInputTokensWithStreamingResponse as AsyncInputTokensWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "InputItems": (".input_items", "InputItems"),
        "AsyncInputItems": (".input_items", "AsyncInputItems"),
        "InputItemsWithRawResponse": (".input_items", "InputItemsWithRawResponse"),
        "AsyncInputItemsWithRawResponse": (".input_items", "AsyncInputItemsWithRawResponse"),
        "InputItemsWithStreamingResponse": (".input_items", "InputItemsWithStreamingResponse"),
        "AsyncInputItemsWithStreamingResponse": (".input_items", "AsyncInputItemsWithStreamingResponse"),
        "InputTokens": (".input_tokens", "InputTokens"),
        "AsyncInputTokens": (".input_tokens", "AsyncInputTokens"),
        "InputTokensWithRawResponse": (".input_tokens", "InputTokensWithRawResponse"),
        "AsyncInputTokensWithRawResponse": (".input_tokens", "AsyncInputTokensWithRawResponse"),
        "InputTokensWithStreamingResponse": (".input_tokens", "InputTokensWithStreamingResponse"),
        "AsyncInputTokensWithStreamingResponse": (".input_tokens", "AsyncInputTokensWithStreamingResponse"),
        "Responses": (".responses", "Responses"),
        "AsyncResponses": (".responses", "AsyncResponses"),
        "ResponsesWithRawResponse": (".responses", "ResponsesWithRawResponse"),
        "AsyncResponsesWithRawResponse": (".responses", "AsyncResponsesWithRawResponse"),
        "ResponsesWithStreamingResponse": (".responses", "ResponsesWithStreamingResponse"),
        "AsyncResponsesWithStreamingResponse": (".responses", "AsyncResponsesWithStreamingResponse"),
    }
    _SUBMODULES = {
        "input_items",
        "input_tokens",
        "responses",
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
    "InputItems",
    "AsyncInputItems",
    "InputItemsWithRawResponse",
    "AsyncInputItemsWithRawResponse",
    "InputItemsWithStreamingResponse",
    "AsyncInputItemsWithStreamingResponse",
    "InputTokens",
    "AsyncInputTokens",
    "InputTokensWithRawResponse",
    "AsyncInputTokensWithRawResponse",
    "InputTokensWithStreamingResponse",
    "AsyncInputTokensWithStreamingResponse",
    "Responses",
    "AsyncResponses",
    "ResponsesWithRawResponse",
    "AsyncResponsesWithRawResponse",
    "ResponsesWithStreamingResponse",
    "AsyncResponsesWithStreamingResponse",
]
