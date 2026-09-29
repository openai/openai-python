# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .vaults import (
        Vaults as Vaults,
        AsyncVaults as AsyncVaults,
        VaultsWithRawResponse as VaultsWithRawResponse,
        AsyncVaultsWithRawResponse as AsyncVaultsWithRawResponse,
        VaultsWithStreamingResponse as VaultsWithStreamingResponse,
        AsyncVaultsWithStreamingResponse as AsyncVaultsWithStreamingResponse,
    )
    from .credentials import (
        Credentials as Credentials,
        AsyncCredentials as AsyncCredentials,
        CredentialsWithRawResponse as CredentialsWithRawResponse,
        AsyncCredentialsWithRawResponse as AsyncCredentialsWithRawResponse,
        CredentialsWithStreamingResponse as CredentialsWithStreamingResponse,
        AsyncCredentialsWithStreamingResponse as AsyncCredentialsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Credentials": (".credentials", "Credentials"),
        "AsyncCredentials": (".credentials", "AsyncCredentials"),
        "CredentialsWithRawResponse": (".credentials", "CredentialsWithRawResponse"),
        "AsyncCredentialsWithRawResponse": (".credentials", "AsyncCredentialsWithRawResponse"),
        "CredentialsWithStreamingResponse": (".credentials", "CredentialsWithStreamingResponse"),
        "AsyncCredentialsWithStreamingResponse": (".credentials", "AsyncCredentialsWithStreamingResponse"),
        "Vaults": (".vaults", "Vaults"),
        "AsyncVaults": (".vaults", "AsyncVaults"),
        "VaultsWithRawResponse": (".vaults", "VaultsWithRawResponse"),
        "AsyncVaultsWithRawResponse": (".vaults", "AsyncVaultsWithRawResponse"),
        "VaultsWithStreamingResponse": (".vaults", "VaultsWithStreamingResponse"),
        "AsyncVaultsWithStreamingResponse": (".vaults", "AsyncVaultsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "credentials",
        "vaults",
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
    "Credentials",
    "AsyncCredentials",
    "CredentialsWithRawResponse",
    "AsyncCredentialsWithRawResponse",
    "CredentialsWithStreamingResponse",
    "AsyncCredentialsWithStreamingResponse",
    "Vaults",
    "AsyncVaults",
    "VaultsWithRawResponse",
    "AsyncVaultsWithRawResponse",
    "VaultsWithStreamingResponse",
    "AsyncVaultsWithStreamingResponse",
]
