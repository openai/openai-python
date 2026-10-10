# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .translations import (
        Translations as Translations,
        AsyncTranslations as AsyncTranslations,
        TranslationsWithRawResponse as TranslationsWithRawResponse,
        AsyncTranslationsWithRawResponse as AsyncTranslationsWithRawResponse,
        TranslationsWithStreamingResponse as TranslationsWithStreamingResponse,
        AsyncTranslationsWithStreamingResponse as AsyncTranslationsWithStreamingResponse,
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
        "Translations": (".translations", "Translations"),
        "AsyncTranslations": (".translations", "AsyncTranslations"),
        "TranslationsWithRawResponse": (".translations", "TranslationsWithRawResponse"),
        "AsyncTranslationsWithRawResponse": (".translations", "AsyncTranslationsWithRawResponse"),
        "TranslationsWithStreamingResponse": (".translations", "TranslationsWithStreamingResponse"),
        "AsyncTranslationsWithStreamingResponse": (".translations", "AsyncTranslationsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "client_secrets",
        "translations",
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
    "Translations",
    "AsyncTranslations",
    "TranslationsWithRawResponse",
    "AsyncTranslationsWithRawResponse",
    "TranslationsWithStreamingResponse",
    "AsyncTranslationsWithStreamingResponse",
]
