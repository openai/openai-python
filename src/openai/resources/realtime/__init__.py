# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .calls import (
        Calls as Calls,
        AsyncCalls as AsyncCalls,
        CallsWithRawResponse as CallsWithRawResponse,
        AsyncCallsWithRawResponse as AsyncCallsWithRawResponse,
        CallsWithStreamingResponse as CallsWithStreamingResponse,
        AsyncCallsWithStreamingResponse as AsyncCallsWithStreamingResponse,
    )
    from .realtime import (
        Realtime as Realtime,
        AsyncRealtime as AsyncRealtime,
        RealtimeWithRawResponse as RealtimeWithRawResponse,
        AsyncRealtimeWithRawResponse as AsyncRealtimeWithRawResponse,
        RealtimeWithStreamingResponse as RealtimeWithStreamingResponse,
        AsyncRealtimeWithStreamingResponse as AsyncRealtimeWithStreamingResponse,
    )
    from .client_secrets import (
        ClientSecrets as ClientSecrets,
        AsyncClientSecrets as AsyncClientSecrets,
        ClientSecretsWithRawResponse as ClientSecretsWithRawResponse,
        AsyncClientSecretsWithRawResponse as AsyncClientSecretsWithRawResponse,
        ClientSecretsWithStreamingResponse as ClientSecretsWithStreamingResponse,
        AsyncClientSecretsWithStreamingResponse as AsyncClientSecretsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "ClientSecrets": (".client_secrets", "ClientSecrets"),
        "AsyncClientSecrets": (".client_secrets", "AsyncClientSecrets"),
        "ClientSecretsWithRawResponse": (".client_secrets", "ClientSecretsWithRawResponse"),
        "AsyncClientSecretsWithRawResponse": (".client_secrets", "AsyncClientSecretsWithRawResponse"),
        "ClientSecretsWithStreamingResponse": (".client_secrets", "ClientSecretsWithStreamingResponse"),
        "AsyncClientSecretsWithStreamingResponse": (".client_secrets", "AsyncClientSecretsWithStreamingResponse"),
        "Calls": (".calls", "Calls"),
        "AsyncCalls": (".calls", "AsyncCalls"),
        "CallsWithRawResponse": (".calls", "CallsWithRawResponse"),
        "AsyncCallsWithRawResponse": (".calls", "AsyncCallsWithRawResponse"),
        "CallsWithStreamingResponse": (".calls", "CallsWithStreamingResponse"),
        "AsyncCallsWithStreamingResponse": (".calls", "AsyncCallsWithStreamingResponse"),
        "Realtime": (".realtime", "Realtime"),
        "AsyncRealtime": (".realtime", "AsyncRealtime"),
        "RealtimeWithRawResponse": (".realtime", "RealtimeWithRawResponse"),
        "AsyncRealtimeWithRawResponse": (".realtime", "AsyncRealtimeWithRawResponse"),
        "RealtimeWithStreamingResponse": (".realtime", "RealtimeWithStreamingResponse"),
        "AsyncRealtimeWithStreamingResponse": (".realtime", "AsyncRealtimeWithStreamingResponse"),
    }
    _SUBMODULES = {
        "calls",
        "client_secrets",
        "realtime",
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
    "ClientSecrets",
    "AsyncClientSecrets",
    "ClientSecretsWithRawResponse",
    "AsyncClientSecretsWithRawResponse",
    "ClientSecretsWithStreamingResponse",
    "AsyncClientSecretsWithStreamingResponse",
    "Calls",
    "AsyncCalls",
    "CallsWithRawResponse",
    "AsyncCallsWithRawResponse",
    "CallsWithStreamingResponse",
    "AsyncCallsWithStreamingResponse",
    "Realtime",
    "AsyncRealtime",
    "RealtimeWithRawResponse",
    "AsyncRealtimeWithRawResponse",
    "RealtimeWithStreamingResponse",
    "AsyncRealtimeWithStreamingResponse",
]
