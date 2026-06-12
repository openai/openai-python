from __future__ import annotations

from typing import Callable, Protocol, Awaitable
from weakref import WeakKeyDictionary
from dataclasses import dataclass

import httpx

from ._models import FinalRequestOptions
from ._exceptions import OpenAIError


class _Provider:
    """Opaque configuration returned by an OpenAI-owned provider factory."""

    __slots__ = ("__weakref__",)


@dataclass
class _ProviderRuntime:
    name: str
    base_url: str | httpx.URL
    transform_request: Callable[[FinalRequestOptions], FinalRequestOptions] | None = None
    transform_async_request: Callable[[FinalRequestOptions], Awaitable[FinalRequestOptions]] | None = None
    prepare_request: Callable[[httpx.Request], None] | None = None
    prepare_async_request: Callable[[httpx.Request], Awaitable[None]] | None = None
    normalize_response: Callable[[httpx.Response], httpx.Response] | None = None
    normalize_async_response: Callable[[httpx.Response], Awaitable[httpx.Response]] | None = None


class _ProviderDefinition(Protocol):
    @property
    def name(self) -> str: ...

    def configure(self) -> _ProviderRuntime: ...


_provider_definitions: WeakKeyDictionary[_Provider, _ProviderDefinition] = WeakKeyDictionary()


def _create_provider(definition: _ProviderDefinition) -> _Provider:  # pyright: ignore[reportUnusedFunction]
    provider = _Provider()
    _provider_definitions[provider] = definition
    return provider


def _provider_name(provider: _Provider) -> str:  # pyright: ignore[reportUnusedFunction]
    return _get_provider_definition(provider).name


def _configure_provider(provider: _Provider) -> _ProviderRuntime:  # pyright: ignore[reportUnusedFunction]
    return _get_provider_definition(provider).configure()


def _get_provider_definition(provider: _Provider) -> _ProviderDefinition:
    try:
        return _provider_definitions[provider]
    except (KeyError, TypeError) as exc:
        raise OpenAIError("Invalid provider. Providers must be created by an OpenAI provider factory.") from exc
