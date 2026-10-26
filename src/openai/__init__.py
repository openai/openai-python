# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os as _os
import typing as _t
from typing_extensions import override

from . import types
from ._types import NOT_GIVEN, Omit, NoneType, NotGiven, Transport, ProxiesTypes, omit, not_given
from ._utils import file_from_path
from ._client import Client, OpenAI, Stream, Timeout, Transport, AsyncClient, AsyncOpenAI, AsyncStream, RequestOptions
from ._httpx2 import (
    DefaultHttpx2Client as DefaultHttpx2Client,
    DefaultAsyncHttpx2Client as DefaultAsyncHttpx2Client,
    normalize_httpx_url as _normalize_httpx_url,
)
from ._models import BaseModel
from ._version import __title__, __version__
from ._response import APIResponse as APIResponse, AsyncAPIResponse as AsyncAPIResponse
from ._constants import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_CONNECTION_LIMITS
from ._exceptions import (
    APIError,
    OAuthError as OAuthError,
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
    LengthFinishReasonError as LengthFinishReasonError,
    WebSocketQueueFullError,
    UnprocessableEntityError,
    APIResponseValidationError,
    InvalidWebhookSignatureError as InvalidWebhookSignatureError,
    ContentFilterFinishReasonError as ContentFilterFinishReasonError,
    WebSocketConnectionClosedError,
)
from ._base_client import DefaultHttpxClient, DefaultAioHttpClient, DefaultAsyncHttpxClient
from ._utils._logs import setup_logging as _setup_logging
from ._data_residency import DataResidency
from ._legacy_response import HttpxBinaryResponseContent as HttpxBinaryResponseContent
from .types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides

__all__ = [
    "types",
    "__version__",
    "__title__",
    "NoneType",
    "Transport",
    "ProxiesTypes",
    "NotGiven",
    "NOT_GIVEN",
    "not_given",
    "Omit",
    "omit",
    "OpenAIError",
    "APIError",
    "APIStatusError",
    "APITimeoutError",
    "APIConnectionError",
    "APIResponseValidationError",
    "BadRequestError",
    "AuthenticationError",
    "OAuthError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "LengthFinishReasonError",
    "ContentFilterFinishReasonError",
    "InvalidWebhookSignatureError",
    "Timeout",
    "RequestOptions",
    "DataResidency",
    "Client",
    "AsyncClient",
    "Stream",
    "AsyncStream",
    "OpenAI",
    "AsyncOpenAI",
    "BedrockOpenAI",
    "AsyncBedrockOpenAI",
    "file_from_path",
    "BaseModel",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_CONNECTION_LIMITS",
    "DefaultHttpxClient",
    "DefaultAsyncHttpxClient",
    "DefaultAioHttpClient",
    "DefaultHttpx2Client",
    "DefaultAsyncHttpx2Client",
    "ReconnectingEvent",
    "ReconnectingOverrides",
    "WebSocketQueueFullError",
    "WebSocketConnectionClosedError",
]

if not _t.TYPE_CHECKING:
    from ._utils._resources_proxy import resources as resources

from .lib import (
    azure as _azure,
    bedrock as _bedrock,
    pydantic_function_tool as pydantic_function_tool,
    pydantic_responses_function_tool as pydantic_responses_function_tool,
)
from .version import VERSION as VERSION
from .lib.azure import AzureOpenAI as AzureOpenAI, AsyncAzureOpenAI as AsyncAzureOpenAI
from .lib.bedrock import BedrockOpenAI as BedrockOpenAI, AsyncBedrockOpenAI as AsyncBedrockOpenAI
from .lib._old_api import *

_COMPUTER_EXPORTS = (
    "ComputerToolset",
    "AsyncComputerToolset",
    "ComputerDriver",
    "AsyncComputerDriver",
)
_STREAMING_EXPORTS = (
    "AssistantEventHandler",
    "AsyncAssistantEventHandler",
)

if _t.TYPE_CHECKING:
    from .lib.computer import (
        ComputerDriver as ComputerDriver,
        ComputerToolset as ComputerToolset,
        AsyncComputerDriver as AsyncComputerDriver,
        AsyncComputerToolset as AsyncComputerToolset,
    )
    from .lib.streaming import (
        AssistantEventHandler as AssistantEventHandler,
        AsyncAssistantEventHandler as AsyncAssistantEventHandler,
    )
else:

    def __getattr__(name: str) -> _t.Any:
        if name in _COMPUTER_EXPORTS:
            from importlib import import_module

            value = getattr(import_module(".lib.computer", __name__), name)
            globals()[name] = value
            return value
        if name in _STREAMING_EXPORTS:
            from importlib import import_module

            value = getattr(import_module(".lib.streaming", __name__), name)
            globals()[name] = value
            return value
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    def __dir__() -> list[str]:
        return sorted(set(globals()) | set(_COMPUTER_EXPORTS) | set(_STREAMING_EXPORTS))


_setup_logging()

# Update the __module__ attribute for exported symbols so that
# error messages point to this module instead of the module
# it was originally defined in, e.g.
# openai._exceptions.NotFoundError -> openai.NotFoundError
__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        try:
            __locals[__name].__module__ = "openai"
        except (TypeError, AttributeError):
            # Some of our exported symbols are builtins which we can't set attributes for.
            pass

__all__ += ["ComputerToolset", "AsyncComputerToolset", "ComputerDriver", "AsyncComputerDriver"]
# ------ Module level client ------
import typing as _t

import httpx2 as _httpx

from ._base_client import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES

api_key: str | None = None

admin_api_key: str | None = None

organization: str | None = None

project: str | None = None

webhook_secret: str | None = None

base_url: str | _httpx.URL | None = None

timeout: float | Timeout | None = DEFAULT_TIMEOUT

max_retries: int = DEFAULT_MAX_RETRIES

default_headers: _t.Mapping[str, str] | None = None

default_query: _t.Mapping[str, object] | None = None

http_client: _httpx.Client | None = None


_ApiType = _t.Literal["openai", "azure", "amazon-bedrock"]

api_type: _ApiType | None = _t.cast(_ApiType, _os.environ.get("OPENAI_API_TYPE"))

api_version: str | None = _os.environ.get("OPENAI_API_VERSION")

azure_endpoint: str | None = _os.environ.get("AZURE_OPENAI_ENDPOINT")

azure_ad_token: str | None = None

azure_ad_token_provider: _azure.AzureADTokenProvider | None = None

_bedrock_api_key: str | None = None

bedrock_token_provider: _bedrock.BedrockTokenProvider | None = None


class _ModuleClient(OpenAI):
    # Note: we have to use type: ignores here as overriding class members
    # with properties is technically unsafe but it is fine for our use case

    @property  # type: ignore
    @override
    def api_key(self) -> str | None:
        return api_key

    @api_key.setter  # type: ignore
    def api_key(self, value: str | None) -> None:  # type: ignore
        global api_key

        api_key = value

    @property  # type: ignore
    @override
    def admin_api_key(self) -> str | None:
        return admin_api_key

    @admin_api_key.setter  # type: ignore
    def admin_api_key(self, value: str | None) -> None:  # type: ignore
        global admin_api_key

        admin_api_key = value

    @property  # type: ignore
    @override
    def organization(self) -> str | None:
        return organization

    @organization.setter  # type: ignore
    def organization(self, value: str | None) -> None:  # type: ignore
        global organization

        organization = value

    @property  # type: ignore
    @override
    def project(self) -> str | None:
        return project

    @project.setter  # type: ignore
    def project(self, value: str | None) -> None:  # type: ignore
        global project

        project = value

    @property  # type: ignore
    @override
    def webhook_secret(self) -> str | None:
        return webhook_secret

    @webhook_secret.setter  # type: ignore
    def webhook_secret(self, value: str | None) -> None:  # type: ignore
        global webhook_secret

        webhook_secret = value

    @property
    @override
    def base_url(self) -> _httpx.URL:
        if base_url is not None:
            return _normalize_httpx_url(base_url)

        return super().base_url

    @base_url.setter
    def base_url(self, url: _httpx.URL | str) -> None:
        super().base_url = url  # type: ignore[misc]

    @property  # type: ignore
    @override
    def timeout(self) -> float | Timeout | None:
        return timeout

    @timeout.setter  # type: ignore
    def timeout(self, value: float | Timeout | None) -> None:  # type: ignore
        global timeout

        timeout = value

    @property  # type: ignore
    @override
    def max_retries(self) -> int:
        return max_retries

    @max_retries.setter  # type: ignore
    def max_retries(self, value: int) -> None:  # type: ignore
        global max_retries

        max_retries = value

    @property  # type: ignore
    @override
    def _custom_headers(self) -> _t.Mapping[str, str] | None:
        return default_headers

    @_custom_headers.setter  # type: ignore
    def _custom_headers(self, value: _t.Mapping[str, str] | None) -> None:  # type: ignore
        global default_headers

        default_headers = value

    @property  # type: ignore
    @override
    def _custom_query(self) -> _t.Mapping[str, object] | None:
        return default_query

    @_custom_query.setter  # type: ignore
    def _custom_query(self, value: _t.Mapping[str, object] | None) -> None:  # type: ignore
        global default_query

        default_query = value

    @property  # type: ignore
    @override
    def _client(self) -> _httpx.Client:
        return http_client or super()._client

    @_client.setter  # type: ignore
    def _client(self, value: _httpx.Client) -> None:  # type: ignore
        global http_client

        http_client = value


class _AzureModuleClient(_ModuleClient, AzureOpenAI):  # type: ignore
    ...


class _BedrockModuleClient(_ModuleClient, BedrockOpenAI):  # type: ignore
    @property  # type: ignore
    @override
    def api_key(
        self,
    ) -> str | None:
        from .lib._module_runtime import BedrockModuleClient_api_key

        return BedrockModuleClient_api_key(self)

    @api_key.setter  # type: ignore
    def api_key(
        self,
        value: str | None,
    ) -> None:
        from .lib._module_runtime import BedrockModuleClient_api_key_setter

        return BedrockModuleClient_api_key_setter(self, value)

    @override
    def _refresh_api_key(
        self,
    ) -> str:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._module_runtime import BedrockModuleClient_refresh_api_key

        return BedrockModuleClient_refresh_api_key(_runtime_cast(_RuntimeAny, super()).__thisclass__, self)

    @override
    def _legacy_auth_configuration(
        self,
    ) -> _bedrock._LegacyAuthConfiguration:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._module_runtime import BedrockModuleClient_legacy_auth_configuration

        return BedrockModuleClient_legacy_auth_configuration(_runtime_cast(_RuntimeAny, super()).__thisclass__, self)


class _AmbiguousModuleClientUsageError(OpenAIError):  # type: ignore[reportUnusedClass]
    def __init__(
        self,
    ) -> None:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._module_runtime import AmbiguousModuleClientUsageError_init

        return AmbiguousModuleClientUsageError_init(_runtime_cast(_RuntimeAny, super()).__thisclass__, self)


def _has_openai_credentials() -> bool:  # type: ignore[reportUnusedFunction]
    from .lib._module_runtime import has_openai_credentials

    return has_openai_credentials()


def _has_azure_credentials() -> bool:  # type: ignore[reportUnusedFunction]
    from .lib._module_runtime import has_azure_credentials

    return has_azure_credentials()


def _has_azure_ad_credentials() -> bool:  # type: ignore[reportUnusedFunction]
    from .lib._module_runtime import has_azure_ad_credentials

    return has_azure_ad_credentials()


_client: OpenAI | None = None


def _load_client() -> OpenAI:  # type: ignore[reportUnusedFunction]
    from .lib._module_runtime import load_client

    return load_client()


def _reset_client() -> None:  # type: ignore[reportUnusedFunction]
    global _client

    _client = None


from ._module_client import (
    beta as beta,
    chat as chat,
    live as live,
    admin as admin,
    audio as audio,
    evals as evals,
    files as files,
    images as images,
    models as models,
    safety as safety,
    skills as skills,
    videos as videos,
    batches as batches,
    uploads as uploads,
    realtime as realtime,
    webhooks as webhooks,
    decisions as decisions,
    responses as responses,
    containers as containers,
    embeddings as embeddings,
    completions as completions,
    fine_tuning as fine_tuning,
    moderations as moderations,
    conversations as conversations,
    vector_stores as vector_stores,
    content_provenance_checks as content_provenance_checks,
)
