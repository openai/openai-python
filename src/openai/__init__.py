# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os as _os

from . import types
from ._types import NoneType, Transport, ProxiesTypes
from ._utils import file_from_path
from ._client import (
    Client,
    OpenAI,
    Stream,
    Timeout,
    Transport,
    AsyncClient,
    AsyncOpenAI,
    AsyncStream,
    RequestOptions,
)
from ._version import __title__, __version__
from ._exceptions import (
    APIError,
    OpenAIError,
    ConflictError,
    NotFoundError,
    APIStatusError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    UnprocessableEntityError,
    APIResponseValidationError,
)

__all__ = [
    "types",
    "__version__",
    "__title__",
    "NoneType",
    "Transport",
    "ProxiesTypes",
    "OpenAIError",
    "APIError",
    "APIStatusError",
    "APITimeoutError",
    "APIConnectionError",
    "APIResponseValidationError",
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "Timeout",
    "RequestOptions",
    "Client",
    "AsyncClient",
    "Stream",
    "AsyncStream",
    "OpenAI",
    "AsyncOpenAI",
    "file_from_path",
]

from .version import VERSION as VERSION

# Update the __module__ attribute for exported symbols so that
# error messages point to this module instead of the module
# it was originally defined in, e.g.
# openai._exceptions.NotFoundError -> openai.NotFoundError
__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        try:
            setattr(__locals[__name], "__module__", "openai")
        except (TypeError, AttributeError):
            # Some of our exported symbols are builtins which we can't set attributes for.
            pass

# ------ Module level client ------
import typing as _t

import httpx as _httpx

from ._base_client import DEFAULT_LIMITS, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES

api_key: str | None = _os.environ.get("OPENAI_API_KEY")

organization: str | None = _os.environ.get("OPENAI_ORG_ID") or None

base_url: str | None = None

timeout: float | Timeout | None = DEFAULT_TIMEOUT

max_retries: int = DEFAULT_MAX_RETRIES

default_headers: _t.Mapping[str, str] | None = None

default_query: _t.Mapping[str, object] | None = None

# See httpx documentation for [custom transports](https://www.python-httpx.org/advanced/#custom-transports)
transport: Transport | None = None

# See httpx documentation for [proxies](https://www.python-httpx.org/advanced/#http-proxying)
proxies: ProxiesTypes | None = None

# See httpx documentation for [limits](https://www.python-httpx.org/advanced/#pool-limit-configuration)
connection_pool_limits: _httpx.Limits = DEFAULT_LIMITS


class _ModuleClient(OpenAI):
    # Note: we have to use type: ignores here as overriding class members
    # with properties is technically unsafe but it is fine for our use case

    @property  # type: ignore
    def api_key(self) -> str | None:
        return api_key

    @api_key.setter  # type: ignore
    def api_key(self, value: str | None) -> None:  # type: ignore
        global api_key

        api_key = value

    @property  # type: ignore
    def organization(self) -> str | None:
        return organization

    @organization.setter  # type: ignore
    def organization(self, value: str | None) -> None:  # type: ignore
        global organization

        organization = value

    @property
    def base_url(self) -> _httpx.URL:
        if base_url is not None:
            # mypy doesn't use the type from the setter
            self._client.base_url = base_url  # type: ignore[assignment]

        return self._client.base_url

    @base_url.setter
    def base_url(self, url: _httpx.URL | str) -> None:
        # mypy doesn't use the type from the setter
        self._client.base_url = url  # type: ignore[assignment]

    @property  # type: ignore
    def timeout(self) -> float | Timeout | None:
        return timeout

    @timeout.setter  # type: ignore
    def timeout(self, value: float | Timeout | None) -> None:  # type: ignore
        global timeout

        timeout = value

    @property  # type: ignore
    def max_retries(self) -> int:
        return max_retries

    @max_retries.setter  # type: ignore
    def max_retries(self, value: int) -> None:  # type: ignore
        global max_retries

        max_retries = value

    @property  # type: ignore
    def _custom_headers(self) -> _t.Mapping[str, str] | None:
        return default_headers

    @_custom_headers.setter  # type: ignore
    def _custom_headers(self, value: _t.Mapping[str, str] | None) -> None:  # type: ignore
        global default_headers

        default_headers = value

    @property  # type: ignore
    def _custom_query(self) -> _t.Mapping[str, object] | None:
        return default_query

    @_custom_query.setter  # type: ignore
    def _custom_query(self, value: _t.Mapping[str, object] | None) -> None:  # type: ignore
        global default_query

        default_query = value

    def __del__(self) -> None:
        try:
            super().__del__()
        except Exception:
            pass


_client: OpenAI | None = None


def _load_client() -> OpenAI:  # type: ignore[reportUnusedFunction]
    global _client

    if (
        _client is None
        # if these options have been changed then we need to rebuild
        # the underlying http client
        or _client._transport != transport
        or _client._proxies != proxies
        or _client._limits != connection_pool_limits
    ):
        _client = _ModuleClient(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            transport=transport,
            proxies=proxies,
            connection_pool_limits=connection_pool_limits,
        )
        return _client

    return _client


def _reset_client() -> None:  # type: ignore[reportUnusedFunction]
    global _client

    _client = None


from ._module_client import chat as chat
from ._module_client import audio as audio
from ._module_client import edits as edits
from ._module_client import files as files
from ._module_client import images as images
from ._module_client import models as models
from ._module_client import embeddings as embeddings
from ._module_client import fine_tunes as fine_tunes
from ._module_client import completions as completions
from ._module_client import fine_tuning as fine_tuning
from ._module_client import moderations as moderations
