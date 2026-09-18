# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .api_keys import (
        APIKeys as APIKeys,
        AsyncAPIKeys as AsyncAPIKeys,
        APIKeysWithRawResponse as APIKeysWithRawResponse,
        AsyncAPIKeysWithRawResponse as AsyncAPIKeysWithRawResponse,
        APIKeysWithStreamingResponse as APIKeysWithStreamingResponse,
        AsyncAPIKeysWithStreamingResponse as AsyncAPIKeysWithStreamingResponse,
    )
    from .service_accounts import (
        ServiceAccounts as ServiceAccounts,
        AsyncServiceAccounts as AsyncServiceAccounts,
        ServiceAccountsWithRawResponse as ServiceAccountsWithRawResponse,
        AsyncServiceAccountsWithRawResponse as AsyncServiceAccountsWithRawResponse,
        ServiceAccountsWithStreamingResponse as ServiceAccountsWithStreamingResponse,
        AsyncServiceAccountsWithStreamingResponse as AsyncServiceAccountsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "APIKeys": (".api_keys", "APIKeys"),
        "AsyncAPIKeys": (".api_keys", "AsyncAPIKeys"),
        "APIKeysWithRawResponse": (".api_keys", "APIKeysWithRawResponse"),
        "AsyncAPIKeysWithRawResponse": (".api_keys", "AsyncAPIKeysWithRawResponse"),
        "APIKeysWithStreamingResponse": (".api_keys", "APIKeysWithStreamingResponse"),
        "AsyncAPIKeysWithStreamingResponse": (".api_keys", "AsyncAPIKeysWithStreamingResponse"),
        "ServiceAccounts": (".service_accounts", "ServiceAccounts"),
        "AsyncServiceAccounts": (".service_accounts", "AsyncServiceAccounts"),
        "ServiceAccountsWithRawResponse": (".service_accounts", "ServiceAccountsWithRawResponse"),
        "AsyncServiceAccountsWithRawResponse": (".service_accounts", "AsyncServiceAccountsWithRawResponse"),
        "ServiceAccountsWithStreamingResponse": (".service_accounts", "ServiceAccountsWithStreamingResponse"),
        "AsyncServiceAccountsWithStreamingResponse": (".service_accounts", "AsyncServiceAccountsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "api_keys",
        "service_accounts",
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
    "APIKeys",
    "AsyncAPIKeys",
    "APIKeysWithRawResponse",
    "AsyncAPIKeysWithRawResponse",
    "APIKeysWithStreamingResponse",
    "AsyncAPIKeysWithStreamingResponse",
    "ServiceAccounts",
    "AsyncServiceAccounts",
    "ServiceAccountsWithRawResponse",
    "AsyncServiceAccountsWithRawResponse",
    "ServiceAccountsWithStreamingResponse",
    "AsyncServiceAccountsWithStreamingResponse",
]
