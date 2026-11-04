# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations, annotations as annotations

import os as os
from typing import (
    TYPE_CHECKING as TYPE_CHECKING,
    Any as Any,
    Mapping as Mapping,
    Callable as Callable,
    Iterable as Iterable,
    Awaitable as Awaitable,
    cast as cast,
)
from typing_extensions import Self as Self, Unpack as Unpack, override as override

import httpx2 as httpx2

from . import _exceptions as _exceptions
from ._qs import Querystring as Querystring
from .auth import (
    WorkloadIdentity as WorkloadIdentity,
    WorkloadIdentityAuth as WorkloadIdentityAuth,
    X509WorkloadIdentity as X509WorkloadIdentity,
)
from ._types import (
    Omit as Omit,
    Query as Query,
    Headers as Headers,
    Timeout as Timeout,
    NotGiven as NotGiven,
    Transport as Transport,
    ProxiesTypes as ProxiesTypes,
    HttpxSendArgs as HttpxSendArgs,
    RequestOptions as RequestOptions,
    omit as omit,
    not_given as not_given,
)
from ._utils import (
    is_given as is_given,
    is_mapping as is_mapping,
    is_mapping_t as is_mapping_t,
    get_async_library as get_async_library,
)
from ._compat import cached_property as cached_property
from ._httpx2 import (
    normalize_httpx_url as normalize_httpx_url,
    is_httpx2_sync_client as is_httpx2_sync_client,
    is_httpx2_async_client as is_httpx2_async_client,
)
from ._models import SecurityOptions as SecurityOptions, FinalRequestOptions as FinalRequestOptions
from ._version import __version__ as __version__
from ._provider import (
    _Provider as _Provider,
    _provider_name as _provider_name,
    _ProviderRuntime as _ProviderRuntime,
    _configure_provider as _configure_provider,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from .auth._x509 import (
    MTLS_API_BASE_URL as MTLS_API_BASE_URL,
    SyncX509WorkloadIdentityAuth as SyncX509WorkloadIdentityAuth,
    AsyncX509WorkloadIdentityAuth as AsyncX509WorkloadIdentityAuth,
    validate_x509_api_url as validate_x509_api_url,
    is_x509_workload_identity as is_x509_workload_identity,
    x509_data_residency_base_url as x509_data_residency_base_url,
    validate_x509_api_credentials as validate_x509_api_credentials,
    x509_safe_environment_headers as x509_safe_environment_headers,
    validate_x509_request_authority as validate_x509_request_authority,
)
from ._exceptions import OpenAIError as OpenAIError, APIStatusError as APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES as DEFAULT_MAX_RETRIES,
    SyncAPIClient as SyncAPIClient,
    AsyncAPIClient as AsyncAPIClient,
    _merge_mappings as _merge_mappings,
)
from ._data_residency import DataResidency as DataResidency, resolve_data_residency as resolve_data_residency
from .lib._client_auth import _has_header as _has_header, _has_omitted_header as _has_omitted_header

if TYPE_CHECKING:
    from .resources import (
        beta as _beta,
        chat as _chat,
        live as _live,
        admin as _admin,
        audio as _audio,
        evals as _evals,
        files as _files,
        images as _images,
        models as _models,
        safety as _safety,
        skills as _skills,
        videos as _videos,
        batches as _batches,
        uploads as _uploads,
        realtime as _realtime,
        webhooks as _webhooks,
        decisions as _decisions,
        responses as _responses,
        containers as _containers,
        embeddings as _embeddings,
        completions as _completions,
        fine_tuning as _fine_tuning,
        moderations as _moderations,
        conversations as _conversations,
        vector_stores as _vector_stores,
        content_provenance_checks as _content_provenance_checks,
    )
    from .resources.files import Files, AsyncFiles
    from .resources.images import Images, AsyncImages
    from .resources.models import Models, AsyncModels
    from .resources.videos import Videos, AsyncVideos
    from .resources.batches import Batches, AsyncBatches
    from .resources.beta.beta import Beta, AsyncBeta
    from .resources.chat.chat import Chat, AsyncChat
    from .resources.decisions import Decisions, AsyncDecisions
    from .resources.live.live import Live, AsyncLive
    from .resources.embeddings import Embeddings, AsyncEmbeddings
    from .resources.admin.admin import Admin, AsyncAdmin
    from .resources.audio.audio import Audio, AsyncAudio
    from .resources.completions import Completions, AsyncCompletions
    from .resources.evals.evals import Evals, AsyncEvals
    from .resources.moderations import Moderations, AsyncModerations
    from .resources.safety.safety import Safety, AsyncSafety
    from .resources.skills.skills import Skills, AsyncSkills
    from .resources.uploads.uploads import Uploads, AsyncUploads
    from .resources.realtime.realtime import Realtime, AsyncRealtime
    from .resources.webhooks.webhooks import Webhooks, AsyncWebhooks
    from .resources.responses.responses import Responses, AsyncResponses
    from .resources.containers.containers import Containers, AsyncContainers
    from .resources.fine_tuning.fine_tuning import FineTuning, AsyncFineTuning
    from .resources.content_provenance_checks import ContentProvenanceChecks, AsyncContentProvenanceChecks
    from .resources.conversations.conversations import Conversations, AsyncConversations
    from .resources.vector_stores.vector_stores import VectorStores, AsyncVectorStores

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "OpenAI", "AsyncOpenAI", "Client", "AsyncClient"]

WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER = "workload-identity-auth"


class OpenAI(SyncAPIClient):
    workload_identity: WorkloadIdentity | X509WorkloadIdentity | None
    _workload_identity_auth: WorkloadIdentityAuth | SyncX509WorkloadIdentityAuth | None
    _provider: _Provider | None
    _provider_runtime: _ProviderRuntime | None
    _base_url_was_default: bool
    _data_residency: DataResidency | None
    _ambient_authorizations: frozenset[str]
    _api_key_provider: Callable[[], str] | None

    # client options
    api_key: str
    admin_api_key: str | None
    organization: str | None
    project: str | None
    webhook_secret: str | None

    websocket_base_url: str | httpx2.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    @property
    @override
    def base_url(
        self,
    ) -> httpx2.URL:
        from .lib._client_auth import syncbase_url

        return syncbase_url(self)

    @base_url.setter
    def base_url(
        self,
        url: httpx2.URL | str,
    ) -> None:
        from .lib._client_auth import syncbase_url_set

        return syncbase_url_set(self, url)

    def _send_with_auth_retry(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        retried: bool = False,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import sync_send_with_auth_retry

        return sync_send_with_auth_retry(
            _runtime_cast(_RuntimeAny, super()).__thisclass__, self, request, stream=stream, retried=retried, **kwargs
        )

    @override
    def _send_request(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        from .lib._client_auth import sync_send_request

        return sync_send_request(self, request, stream=stream, **kwargs)

    @property
    @override
    def auth_headers(
        self,
    ) -> dict[str, str]:
        from .lib._client_auth import syncauth_headers

        return syncauth_headers(self)

    @override
    def _prepare_options(
        self,
        options: FinalRequestOptions,
    ) -> FinalRequestOptions:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import sync_prepare_options

        return sync_prepare_options(_runtime_cast(_RuntimeAny, super()).__thisclass__, self, options)

    @override
    def _prepare_request(
        self,
        request: httpx2.Request,
    ) -> None:
        from .lib._client_auth import sync_prepare_request

        return sync_prepare_request(self, request)

    @override
    def _custom_auth(
        self,
        security: SecurityOptions,
    ) -> httpx2.Auth | None:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import sync_custom_auth

        return sync_custom_auth(_runtime_cast(_RuntimeAny, super()).__thisclass__, self, security)

    def _refresh_api_key(
        self,
    ) -> str:
        from .lib._client_auth import sync_refresh_api_key

        return sync_refresh_api_key(self)

    def _websocket_query_params_fallback(self, url: httpx2.URL, extra_query: Query) -> httpx2.QueryParams:
        # Remove replaced logical defaults before encoding nested query values.
        overridden = dict.fromkeys(extra_query, omit)
        overridden_prefixes = tuple(f"{key}[" for key in overridden)
        defaults = _merge_mappings(self.default_query, overridden)
        params = httpx2.QueryParams(self.qs.stringify(cast(Any, defaults))).merge(url.params)
        params = httpx2.QueryParams(
            [
                (key, value)
                for key, value in params.multi_items()
                if key not in overridden and not key.startswith(overridden_prefixes)
            ]
        )
        if isinstance(extra_query, httpx2.QueryParams):
            return params.merge(extra_query)
        # Per-call None and sequences retain blank values and repeated keys;
        # defaults continue to use the REST encoder's configured array format.
        values = _merge_mappings({}, extra_query)
        for key, value in values.items():
            if value is None:
                values[key] = ""
            elif isinstance(value, (list, tuple)):
                values[key] = ["" if item is None else item for item in cast(Iterable[object], value)]
        return params.merge(self.qs.stringify(cast(Any, values), array_format="repeat"))

    def __init__(
        self,
        *,
        api_key: str | Callable[[], str] | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | X509WorkloadIdentity | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        provider: _Provider | None = None,
        base_url: str | httpx2.URL | None | NotGiven = not_given,
        data_residency: DataResidency | None = None,
        websocket_base_url: str | httpx2.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx2.Client | None = None,
        _strict_response_validation: bool = False,
        _enforce_credentials: bool = True,
    ) -> None:
        """Construct a new synchronous OpenAI client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `OPENAI_API_KEY`
        - `admin_api_key` from `OPENAI_ADMIN_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        - `webhook_secret` from `OPENAI_WEBHOOK_SECRET`

        When `provider` is supplied, authentication and the base URL are configured by that provider instead.
        `data_residency` selects an OpenAI regional endpoint and cannot be combined with
        `base_url`, `websocket_base_url`, or `provider`.
        """
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import sync__init__

        return sync__init__(
            _runtime_cast(_RuntimeAny, super()).__thisclass__,
            self,
            api_key=api_key,
            admin_api_key=admin_api_key,
            workload_identity=workload_identity,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            provider=provider,
            base_url=base_url,
            data_residency=data_residency,
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=_enforce_credentials,
        )

    @cached_property
    def decisions(self) -> Decisions:
        from .resources.decisions import Decisions

        return Decisions(self)

    @cached_property
    def completions(self) -> Completions:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import Completions

        return Completions(self)

    @cached_property
    def chat(self) -> Chat:
        from .resources.chat import Chat

        return Chat(self)

    @cached_property
    def embeddings(self) -> Embeddings:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import Embeddings

        return Embeddings(self)

    @cached_property
    def files(self) -> Files:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import Files

        return Files(self)

    @cached_property
    def images(self) -> Images:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import Images

        return Images(self)

    @cached_property
    def content_provenance_checks(self) -> ContentProvenanceChecks:
        from .resources.content_provenance_checks import ContentProvenanceChecks

        return ContentProvenanceChecks(self)

    @cached_property
    def audio(self) -> Audio:
        from .resources.audio import Audio

        return Audio(self)

    @cached_property
    def moderations(self) -> Moderations:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import Moderations

        return Moderations(self)

    @cached_property
    def models(self) -> Models:
        """List and describe the various models available in the API."""
        from .resources.models import Models

        return Models(self)

    @cached_property
    def fine_tuning(self) -> FineTuning:
        from .resources.fine_tuning import FineTuning

        return FineTuning(self)

    @cached_property
    def vector_stores(self) -> VectorStores:
        from .resources.vector_stores import VectorStores

        return VectorStores(self)

    @cached_property
    def safety(self) -> Safety:
        from .resources.safety import Safety

        return Safety(self)

    @cached_property
    def webhooks(self) -> Webhooks:
        from .resources.webhooks import Webhooks

        return Webhooks(self)

    @cached_property
    def beta(self) -> Beta:
        from .resources.beta import Beta

        return Beta(self)

    @cached_property
    def batches(self) -> Batches:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import Batches

        return Batches(self)

    @cached_property
    def uploads(self) -> Uploads:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import Uploads

        return Uploads(self)

    @cached_property
    def admin(self) -> Admin:
        from .resources.admin import Admin

        return Admin(self)

    @cached_property
    def responses(self) -> Responses:
        """Create and manage model responses."""
        from .resources.responses import Responses

        return Responses(self)

    @cached_property
    def live(self) -> Live:
        from .resources.live import Live

        return Live(self)

    @cached_property
    def realtime(self) -> Realtime:
        from .resources.realtime import Realtime

        return Realtime(self)

    @cached_property
    def conversations(self) -> Conversations:
        """Manage conversations and conversation items."""
        from .resources.conversations import Conversations

        return Conversations(self)

    @cached_property
    def evals(self) -> Evals:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import Evals

        return Evals(self)

    @cached_property
    def containers(self) -> Containers:
        from .resources.containers import Containers

        return Containers(self)

    @cached_property
    def skills(self) -> Skills:
        from .resources.skills import Skills

        return Skills(self)

    @cached_property
    def videos(self) -> Videos:
        from .resources.videos import Videos

        return Videos(self)

    @cached_property
    def with_raw_response(self) -> OpenAIWithRawResponse:
        return OpenAIWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAIWithStreamedResponse:
        return OpenAIWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @override
    def _auth_headers(
        self,
        security: SecurityOptions,
    ) -> dict[str, str]:
        from .lib._client_auth import sync_auth_headers

        return sync_auth_headers(self, security)

    @property
    def _bearer_auth(
        self,
    ) -> dict[str, str]:
        from .lib._client_auth import sync_bearer_auth

        return sync_bearer_auth(self)

    @property
    def _admin_api_key_auth(self) -> dict[str, str]:
        admin_api_key = self.admin_api_key
        if admin_api_key is None:
            return {}
        return {"Authorization": f"Bearer {admin_api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            "OpenAI-Organization": self.organization if self.organization is not None else Omit(),
            "OpenAI-Project": self.project if self.project is not None else Omit(),
            **self._custom_headers,
        }

    @override
    def _validate_headers(
        self,
        headers: Headers,
        custom_headers: Headers,
    ) -> None:
        from .lib._client_auth import sync_validate_headers

        return sync_validate_headers(self, headers, custom_headers)

    def copy(
        self,
        *,
        api_key: str | Callable[[], str] | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | X509WorkloadIdentity | None = None,
        provider: _Provider | None | NotGiven = not_given,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx2.URL | None = None,
        base_url: str | httpx2.URL | None | NotGiven = not_given,
        data_residency: DataResidency | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx2.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _enforce_credentials: bool | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        `data_residency` replaces the inherited HTTP and WebSocket endpoints, without changing this client.
        """
        from .lib._client_auth import synccopy

        return synccopy(
            self,
            api_key=api_key,
            admin_api_key=admin_api_key,
            workload_identity=workload_identity,
            provider=provider,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            websocket_base_url=websocket_base_url,
            base_url=base_url,
            data_residency=data_residency,
            timeout=timeout,
            http_client=http_client,
            max_retries=max_retries,
            default_headers=default_headers,
            set_default_headers=set_default_headers,
            default_query=default_query,
            set_default_query=set_default_query,
            _enforce_credentials=_enforce_credentials,
            _extra_kwargs=_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx2.Response,
    ) -> APIStatusError:
        data = body.get("error", body) if is_mapping(body) else body
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=data)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=data)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=data)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=data)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=data)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=data)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=data)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=data)
        return APIStatusError(err_msg, response=response, body=data)


class AsyncOpenAI(AsyncAPIClient):
    workload_identity: WorkloadIdentity | X509WorkloadIdentity | None
    _workload_identity_auth: WorkloadIdentityAuth | AsyncX509WorkloadIdentityAuth | None
    _provider: _Provider | None
    _provider_runtime: _ProviderRuntime | None
    _base_url_was_default: bool
    _data_residency: DataResidency | None
    _ambient_authorizations: frozenset[str]
    _api_key_provider: Callable[[], Awaitable[str]] | None

    # client options
    api_key: str
    admin_api_key: str | None
    organization: str | None
    project: str | None
    webhook_secret: str | None

    websocket_base_url: str | httpx2.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    @property
    @override
    def base_url(
        self,
    ) -> httpx2.URL:
        from .lib._client_auth import asyncbase_url

        return asyncbase_url(self)

    @base_url.setter
    def base_url(
        self,
        url: httpx2.URL | str,
    ) -> None:
        from .lib._client_auth import asyncbase_url_set

        return asyncbase_url_set(self, url)

    async def _send_with_auth_retry(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        retried: bool = False,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import async_send_with_auth_retry

        return await async_send_with_auth_retry(
            _runtime_cast(_RuntimeAny, super()).__thisclass__, self, request, stream=stream, retried=retried, **kwargs
        )

    @override
    async def _send_request(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        from .lib._client_auth import async_send_request

        return await async_send_request(self, request, stream=stream, **kwargs)

    @property
    @override
    def auth_headers(
        self,
    ) -> dict[str, str]:
        from .lib._client_auth import asyncauth_headers

        return asyncauth_headers(self)

    @override
    async def _prepare_options(
        self,
        options: FinalRequestOptions,
    ) -> FinalRequestOptions:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import async_prepare_options

        return await async_prepare_options(_runtime_cast(_RuntimeAny, super()).__thisclass__, self, options)

    @override
    async def _prepare_request(
        self,
        request: httpx2.Request,
    ) -> None:
        from .lib._client_auth import async_prepare_request

        return await async_prepare_request(self, request)

    @property
    @override
    def custom_auth(
        self,
    ) -> httpx2.Auth | None:
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import asynccustom_auth

        return asynccustom_auth(_runtime_cast(_RuntimeAny, super()).__thisclass__, self)

    async def _refresh_api_key(
        self,
    ) -> str:
        from .lib._client_auth import async_refresh_api_key

        return await async_refresh_api_key(self)

    def _websocket_query_params_fallback(self, url: httpx2.URL, extra_query: Query) -> httpx2.QueryParams:
        # Remove replaced logical defaults before encoding nested query values.
        overridden = dict.fromkeys(extra_query, omit)
        overridden_prefixes = tuple(f"{key}[" for key in overridden)
        defaults = _merge_mappings(self.default_query, overridden)
        params = httpx2.QueryParams(self.qs.stringify(cast(Any, defaults))).merge(url.params)
        params = httpx2.QueryParams(
            [
                (key, value)
                for key, value in params.multi_items()
                if key not in overridden and not key.startswith(overridden_prefixes)
            ]
        )
        if isinstance(extra_query, httpx2.QueryParams):
            return params.merge(extra_query)
        # Per-call None and sequences retain blank values and repeated keys;
        # defaults continue to use the REST encoder's configured array format.
        values = _merge_mappings({}, extra_query)
        for key, value in values.items():
            if value is None:
                values[key] = ""
            elif isinstance(value, (list, tuple)):
                values[key] = ["" if item is None else item for item in cast(Iterable[object], value)]
        return params.merge(self.qs.stringify(cast(Any, values), array_format="repeat"))

    def __init__(
        self,
        *,
        api_key: str | Callable[[], Awaitable[str]] | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | X509WorkloadIdentity | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        provider: _Provider | None = None,
        base_url: str | httpx2.URL | None | NotGiven = not_given,
        data_residency: DataResidency | None = None,
        websocket_base_url: str | httpx2.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx2.AsyncClient | None = None,
        _strict_response_validation: bool = False,
        _enforce_credentials: bool = True,
    ) -> None:
        """Construct a new async AsyncOpenAI client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `OPENAI_API_KEY`
        - `admin_api_key` from `OPENAI_ADMIN_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        - `webhook_secret` from `OPENAI_WEBHOOK_SECRET`

        When `provider` is supplied, authentication and the base URL are configured by that provider instead.
        `data_residency` selects an OpenAI regional endpoint and cannot be combined with
        `base_url`, `websocket_base_url`, or `provider`.
        """
        from typing import Any as _RuntimeAny, cast as _runtime_cast

        from .lib._client_auth import async__init__

        return async__init__(
            _runtime_cast(_RuntimeAny, super()).__thisclass__,
            self,
            api_key=api_key,
            admin_api_key=admin_api_key,
            workload_identity=workload_identity,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            provider=provider,
            base_url=base_url,
            data_residency=data_residency,
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
            _enforce_credentials=_enforce_credentials,
        )

    @cached_property
    def decisions(self) -> AsyncDecisions:
        from .resources.decisions import AsyncDecisions

        return AsyncDecisions(self)

    @cached_property
    def completions(self) -> AsyncCompletions:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import AsyncCompletions

        return AsyncCompletions(self)

    @cached_property
    def chat(self) -> AsyncChat:
        from .resources.chat import AsyncChat

        return AsyncChat(self)

    @cached_property
    def embeddings(self) -> AsyncEmbeddings:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import AsyncEmbeddings

        return AsyncEmbeddings(self)

    @cached_property
    def files(self) -> AsyncFiles:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import AsyncFiles

        return AsyncFiles(self)

    @cached_property
    def images(self) -> AsyncImages:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import AsyncImages

        return AsyncImages(self)

    @cached_property
    def content_provenance_checks(self) -> AsyncContentProvenanceChecks:
        from .resources.content_provenance_checks import AsyncContentProvenanceChecks

        return AsyncContentProvenanceChecks(self)

    @cached_property
    def audio(self) -> AsyncAudio:
        from .resources.audio import AsyncAudio

        return AsyncAudio(self)

    @cached_property
    def moderations(self) -> AsyncModerations:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import AsyncModerations

        return AsyncModerations(self)

    @cached_property
    def models(self) -> AsyncModels:
        """List and describe the various models available in the API."""
        from .resources.models import AsyncModels

        return AsyncModels(self)

    @cached_property
    def fine_tuning(self) -> AsyncFineTuning:
        from .resources.fine_tuning import AsyncFineTuning

        return AsyncFineTuning(self)

    @cached_property
    def vector_stores(self) -> AsyncVectorStores:
        from .resources.vector_stores import AsyncVectorStores

        return AsyncVectorStores(self)

    @cached_property
    def safety(self) -> AsyncSafety:
        from .resources.safety import AsyncSafety

        return AsyncSafety(self)

    @cached_property
    def webhooks(self) -> AsyncWebhooks:
        from .resources.webhooks import AsyncWebhooks

        return AsyncWebhooks(self)

    @cached_property
    def beta(self) -> AsyncBeta:
        from .resources.beta import AsyncBeta

        return AsyncBeta(self)

    @cached_property
    def batches(self) -> AsyncBatches:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import AsyncBatches

        return AsyncBatches(self)

    @cached_property
    def uploads(self) -> AsyncUploads:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import AsyncUploads

        return AsyncUploads(self)

    @cached_property
    def admin(self) -> AsyncAdmin:
        from .resources.admin import AsyncAdmin

        return AsyncAdmin(self)

    @cached_property
    def responses(self) -> AsyncResponses:
        """Create and manage model responses."""
        from .resources.responses import AsyncResponses

        return AsyncResponses(self)

    @cached_property
    def live(self) -> AsyncLive:
        from .resources.live import AsyncLive

        return AsyncLive(self)

    @cached_property
    def realtime(self) -> AsyncRealtime:
        from .resources.realtime import AsyncRealtime

        return AsyncRealtime(self)

    @cached_property
    def conversations(self) -> AsyncConversations:
        """Manage conversations and conversation items."""
        from .resources.conversations import AsyncConversations

        return AsyncConversations(self)

    @cached_property
    def evals(self) -> AsyncEvals:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import AsyncEvals

        return AsyncEvals(self)

    @cached_property
    def containers(self) -> AsyncContainers:
        from .resources.containers import AsyncContainers

        return AsyncContainers(self)

    @cached_property
    def skills(self) -> AsyncSkills:
        from .resources.skills import AsyncSkills

        return AsyncSkills(self)

    @cached_property
    def videos(self) -> AsyncVideos:
        from .resources.videos import AsyncVideos

        return AsyncVideos(self)

    @cached_property
    def with_raw_response(self) -> AsyncOpenAIWithRawResponse:
        return AsyncOpenAIWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAIWithStreamedResponse:
        return AsyncOpenAIWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @override
    def _auth_headers(
        self,
        security: SecurityOptions,
    ) -> dict[str, str]:
        from .lib._client_auth import async_auth_headers

        return async_auth_headers(self, security)

    @property
    def _bearer_auth(
        self,
    ) -> dict[str, str]:
        from .lib._client_auth import async_bearer_auth

        return async_bearer_auth(self)

    @property
    def _admin_api_key_auth(self) -> dict[str, str]:
        admin_api_key = self.admin_api_key
        if admin_api_key is None:
            return {}
        return {"Authorization": f"Bearer {admin_api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            "OpenAI-Organization": self.organization if self.organization is not None else Omit(),
            "OpenAI-Project": self.project if self.project is not None else Omit(),
            **self._custom_headers,
        }

    @override
    def _validate_headers(
        self,
        headers: Headers,
        custom_headers: Headers,
    ) -> None:
        from .lib._client_auth import async_validate_headers

        return async_validate_headers(self, headers, custom_headers)

    def copy(
        self,
        *,
        api_key: str | Callable[[], Awaitable[str]] | None = None,
        admin_api_key: str | None = None,
        workload_identity: WorkloadIdentity | X509WorkloadIdentity | None = None,
        provider: _Provider | None | NotGiven = not_given,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx2.URL | None = None,
        base_url: str | httpx2.URL | None | NotGiven = not_given,
        data_residency: DataResidency | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx2.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _enforce_credentials: bool | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        `data_residency` replaces the inherited HTTP and WebSocket endpoints, without changing this client.
        """
        from .lib._client_auth import asynccopy

        return asynccopy(
            self,
            api_key=api_key,
            admin_api_key=admin_api_key,
            workload_identity=workload_identity,
            provider=provider,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            websocket_base_url=websocket_base_url,
            base_url=base_url,
            data_residency=data_residency,
            timeout=timeout,
            http_client=http_client,
            max_retries=max_retries,
            default_headers=default_headers,
            set_default_headers=set_default_headers,
            default_query=default_query,
            set_default_query=set_default_query,
            _enforce_credentials=_enforce_credentials,
            _extra_kwargs=_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx2.Response,
    ) -> APIStatusError:
        data = body.get("error", body) if is_mapping(body) else body
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=data)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=data)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=data)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=data)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=data)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=data)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=data)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=data)
        return APIStatusError(err_msg, response=response, body=data)


class OpenAIWithRawResponse:
    _client: OpenAI

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    @cached_property
    def decisions(self) -> _decisions.DecisionsWithRawResponse:
        from .resources.decisions import DecisionsWithRawResponse

        return DecisionsWithRawResponse(self._client.decisions)

    @cached_property
    def completions(self) -> _completions.CompletionsWithRawResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import CompletionsWithRawResponse

        return CompletionsWithRawResponse(self._client.completions)

    @cached_property
    def chat(self) -> _chat.ChatWithRawResponse:
        from .resources.chat import ChatWithRawResponse

        return ChatWithRawResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> _embeddings.EmbeddingsWithRawResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import EmbeddingsWithRawResponse

        return EmbeddingsWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> _files.FilesWithRawResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import FilesWithRawResponse

        return FilesWithRawResponse(self._client.files)

    @cached_property
    def images(self) -> _images.ImagesWithRawResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import ImagesWithRawResponse

        return ImagesWithRawResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> _content_provenance_checks.ContentProvenanceChecksWithRawResponse:
        from .resources.content_provenance_checks import ContentProvenanceChecksWithRawResponse

        return ContentProvenanceChecksWithRawResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> _audio.AudioWithRawResponse:
        from .resources.audio import AudioWithRawResponse

        return AudioWithRawResponse(self._client.audio)

    @cached_property
    def moderations(self) -> _moderations.ModerationsWithRawResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import ModerationsWithRawResponse

        return ModerationsWithRawResponse(self._client.moderations)

    @cached_property
    def models(self) -> _models.ModelsWithRawResponse:
        """List and describe the various models available in the API."""
        from .resources.models import ModelsWithRawResponse

        return ModelsWithRawResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> _fine_tuning.FineTuningWithRawResponse:
        from .resources.fine_tuning import FineTuningWithRawResponse

        return FineTuningWithRawResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> _vector_stores.VectorStoresWithRawResponse:
        from .resources.vector_stores import VectorStoresWithRawResponse

        return VectorStoresWithRawResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> _safety.SafetyWithRawResponse:
        from .resources.safety import SafetyWithRawResponse

        return SafetyWithRawResponse(self._client.safety)

    @cached_property
    def webhooks(self) -> _webhooks.WebhooksWithRawResponse:
        from .resources.webhooks import WebhooksWithRawResponse

        return WebhooksWithRawResponse(self._client.webhooks)

    @cached_property
    def beta(self) -> _beta.BetaWithRawResponse:
        from .resources.beta import BetaWithRawResponse

        return BetaWithRawResponse(self._client.beta)

    @cached_property
    def batches(self) -> _batches.BatchesWithRawResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import BatchesWithRawResponse

        return BatchesWithRawResponse(self._client.batches)

    @cached_property
    def uploads(self) -> _uploads.UploadsWithRawResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import UploadsWithRawResponse

        return UploadsWithRawResponse(self._client.uploads)

    @cached_property
    def admin(self) -> _admin.AdminWithRawResponse:
        from .resources.admin import AdminWithRawResponse

        return AdminWithRawResponse(self._client.admin)

    @cached_property
    def responses(self) -> _responses.ResponsesWithRawResponse:
        """Create and manage model responses."""
        from .resources.responses import ResponsesWithRawResponse

        return ResponsesWithRawResponse(self._client.responses)

    @cached_property
    def live(self) -> _live.LiveWithRawResponse:
        from .resources.live import LiveWithRawResponse

        return LiveWithRawResponse(self._client.live)

    @cached_property
    def realtime(self) -> _realtime.RealtimeWithRawResponse:
        from .resources.realtime import RealtimeWithRawResponse

        return RealtimeWithRawResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> _conversations.ConversationsWithRawResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import ConversationsWithRawResponse

        return ConversationsWithRawResponse(self._client.conversations)

    @cached_property
    def evals(self) -> _evals.EvalsWithRawResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import EvalsWithRawResponse

        return EvalsWithRawResponse(self._client.evals)

    @cached_property
    def containers(self) -> _containers.ContainersWithRawResponse:
        from .resources.containers import ContainersWithRawResponse

        return ContainersWithRawResponse(self._client.containers)

    @cached_property
    def skills(self) -> _skills.SkillsWithRawResponse:
        from .resources.skills import SkillsWithRawResponse

        return SkillsWithRawResponse(self._client.skills)

    @cached_property
    def videos(self) -> _videos.VideosWithRawResponse:
        from .resources.videos import VideosWithRawResponse

        return VideosWithRawResponse(self._client.videos)


class AsyncOpenAIWithRawResponse:
    _client: AsyncOpenAI

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client

    @cached_property
    def decisions(self) -> _decisions.AsyncDecisionsWithRawResponse:
        from .resources.decisions import AsyncDecisionsWithRawResponse

        return AsyncDecisionsWithRawResponse(self._client.decisions)

    @cached_property
    def completions(self) -> _completions.AsyncCompletionsWithRawResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import AsyncCompletionsWithRawResponse

        return AsyncCompletionsWithRawResponse(self._client.completions)

    @cached_property
    def chat(self) -> _chat.AsyncChatWithRawResponse:
        from .resources.chat import AsyncChatWithRawResponse

        return AsyncChatWithRawResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> _embeddings.AsyncEmbeddingsWithRawResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import AsyncEmbeddingsWithRawResponse

        return AsyncEmbeddingsWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> _files.AsyncFilesWithRawResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import AsyncFilesWithRawResponse

        return AsyncFilesWithRawResponse(self._client.files)

    @cached_property
    def images(self) -> _images.AsyncImagesWithRawResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import AsyncImagesWithRawResponse

        return AsyncImagesWithRawResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> _content_provenance_checks.AsyncContentProvenanceChecksWithRawResponse:
        from .resources.content_provenance_checks import AsyncContentProvenanceChecksWithRawResponse

        return AsyncContentProvenanceChecksWithRawResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> _audio.AsyncAudioWithRawResponse:
        from .resources.audio import AsyncAudioWithRawResponse

        return AsyncAudioWithRawResponse(self._client.audio)

    @cached_property
    def moderations(self) -> _moderations.AsyncModerationsWithRawResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import AsyncModerationsWithRawResponse

        return AsyncModerationsWithRawResponse(self._client.moderations)

    @cached_property
    def models(self) -> _models.AsyncModelsWithRawResponse:
        """List and describe the various models available in the API."""
        from .resources.models import AsyncModelsWithRawResponse

        return AsyncModelsWithRawResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> _fine_tuning.AsyncFineTuningWithRawResponse:
        from .resources.fine_tuning import AsyncFineTuningWithRawResponse

        return AsyncFineTuningWithRawResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> _vector_stores.AsyncVectorStoresWithRawResponse:
        from .resources.vector_stores import AsyncVectorStoresWithRawResponse

        return AsyncVectorStoresWithRawResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> _safety.AsyncSafetyWithRawResponse:
        from .resources.safety import AsyncSafetyWithRawResponse

        return AsyncSafetyWithRawResponse(self._client.safety)

    @cached_property
    def webhooks(self) -> _webhooks.AsyncWebhooksWithRawResponse:
        from .resources.webhooks import AsyncWebhooksWithRawResponse

        return AsyncWebhooksWithRawResponse(self._client.webhooks)

    @cached_property
    def beta(self) -> _beta.AsyncBetaWithRawResponse:
        from .resources.beta import AsyncBetaWithRawResponse

        return AsyncBetaWithRawResponse(self._client.beta)

    @cached_property
    def batches(self) -> _batches.AsyncBatchesWithRawResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import AsyncBatchesWithRawResponse

        return AsyncBatchesWithRawResponse(self._client.batches)

    @cached_property
    def uploads(self) -> _uploads.AsyncUploadsWithRawResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import AsyncUploadsWithRawResponse

        return AsyncUploadsWithRawResponse(self._client.uploads)

    @cached_property
    def admin(self) -> _admin.AsyncAdminWithRawResponse:
        from .resources.admin import AsyncAdminWithRawResponse

        return AsyncAdminWithRawResponse(self._client.admin)

    @cached_property
    def responses(self) -> _responses.AsyncResponsesWithRawResponse:
        """Create and manage model responses."""
        from .resources.responses import AsyncResponsesWithRawResponse

        return AsyncResponsesWithRawResponse(self._client.responses)

    @cached_property
    def live(self) -> _live.AsyncLiveWithRawResponse:
        from .resources.live import AsyncLiveWithRawResponse

        return AsyncLiveWithRawResponse(self._client.live)

    @cached_property
    def realtime(self) -> _realtime.AsyncRealtimeWithRawResponse:
        from .resources.realtime import AsyncRealtimeWithRawResponse

        return AsyncRealtimeWithRawResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> _conversations.AsyncConversationsWithRawResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import AsyncConversationsWithRawResponse

        return AsyncConversationsWithRawResponse(self._client.conversations)

    @cached_property
    def evals(self) -> _evals.AsyncEvalsWithRawResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import AsyncEvalsWithRawResponse

        return AsyncEvalsWithRawResponse(self._client.evals)

    @cached_property
    def containers(self) -> _containers.AsyncContainersWithRawResponse:
        from .resources.containers import AsyncContainersWithRawResponse

        return AsyncContainersWithRawResponse(self._client.containers)

    @cached_property
    def skills(self) -> _skills.AsyncSkillsWithRawResponse:
        from .resources.skills import AsyncSkillsWithRawResponse

        return AsyncSkillsWithRawResponse(self._client.skills)

    @cached_property
    def videos(self) -> _videos.AsyncVideosWithRawResponse:
        from .resources.videos import AsyncVideosWithRawResponse

        return AsyncVideosWithRawResponse(self._client.videos)


class OpenAIWithStreamedResponse:
    _client: OpenAI

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    @cached_property
    def decisions(self) -> _decisions.DecisionsWithStreamingResponse:
        from .resources.decisions import DecisionsWithStreamingResponse

        return DecisionsWithStreamingResponse(self._client.decisions)

    @cached_property
    def completions(self) -> _completions.CompletionsWithStreamingResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import CompletionsWithStreamingResponse

        return CompletionsWithStreamingResponse(self._client.completions)

    @cached_property
    def chat(self) -> _chat.ChatWithStreamingResponse:
        from .resources.chat import ChatWithStreamingResponse

        return ChatWithStreamingResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> _embeddings.EmbeddingsWithStreamingResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import EmbeddingsWithStreamingResponse

        return EmbeddingsWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> _files.FilesWithStreamingResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import FilesWithStreamingResponse

        return FilesWithStreamingResponse(self._client.files)

    @cached_property
    def images(self) -> _images.ImagesWithStreamingResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import ImagesWithStreamingResponse

        return ImagesWithStreamingResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> _content_provenance_checks.ContentProvenanceChecksWithStreamingResponse:
        from .resources.content_provenance_checks import ContentProvenanceChecksWithStreamingResponse

        return ContentProvenanceChecksWithStreamingResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> _audio.AudioWithStreamingResponse:
        from .resources.audio import AudioWithStreamingResponse

        return AudioWithStreamingResponse(self._client.audio)

    @cached_property
    def moderations(self) -> _moderations.ModerationsWithStreamingResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import ModerationsWithStreamingResponse

        return ModerationsWithStreamingResponse(self._client.moderations)

    @cached_property
    def models(self) -> _models.ModelsWithStreamingResponse:
        """List and describe the various models available in the API."""
        from .resources.models import ModelsWithStreamingResponse

        return ModelsWithStreamingResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> _fine_tuning.FineTuningWithStreamingResponse:
        from .resources.fine_tuning import FineTuningWithStreamingResponse

        return FineTuningWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> _vector_stores.VectorStoresWithStreamingResponse:
        from .resources.vector_stores import VectorStoresWithStreamingResponse

        return VectorStoresWithStreamingResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> _safety.SafetyWithStreamingResponse:
        from .resources.safety import SafetyWithStreamingResponse

        return SafetyWithStreamingResponse(self._client.safety)

    @cached_property
    def webhooks(self) -> _webhooks.WebhooksWithStreamingResponse:
        from .resources.webhooks import WebhooksWithStreamingResponse

        return WebhooksWithStreamingResponse(self._client.webhooks)

    @cached_property
    def beta(self) -> _beta.BetaWithStreamingResponse:
        from .resources.beta import BetaWithStreamingResponse

        return BetaWithStreamingResponse(self._client.beta)

    @cached_property
    def batches(self) -> _batches.BatchesWithStreamingResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import BatchesWithStreamingResponse

        return BatchesWithStreamingResponse(self._client.batches)

    @cached_property
    def uploads(self) -> _uploads.UploadsWithStreamingResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import UploadsWithStreamingResponse

        return UploadsWithStreamingResponse(self._client.uploads)

    @cached_property
    def admin(self) -> _admin.AdminWithStreamingResponse:
        from .resources.admin import AdminWithStreamingResponse

        return AdminWithStreamingResponse(self._client.admin)

    @cached_property
    def responses(self) -> _responses.ResponsesWithStreamingResponse:
        """Create and manage model responses."""
        from .resources.responses import ResponsesWithStreamingResponse

        return ResponsesWithStreamingResponse(self._client.responses)

    @cached_property
    def live(self) -> _live.LiveWithStreamingResponse:
        from .resources.live import LiveWithStreamingResponse

        return LiveWithStreamingResponse(self._client.live)

    @cached_property
    def realtime(self) -> _realtime.RealtimeWithStreamingResponse:
        from .resources.realtime import RealtimeWithStreamingResponse

        return RealtimeWithStreamingResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> _conversations.ConversationsWithStreamingResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import ConversationsWithStreamingResponse

        return ConversationsWithStreamingResponse(self._client.conversations)

    @cached_property
    def evals(self) -> _evals.EvalsWithStreamingResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import EvalsWithStreamingResponse

        return EvalsWithStreamingResponse(self._client.evals)

    @cached_property
    def containers(self) -> _containers.ContainersWithStreamingResponse:
        from .resources.containers import ContainersWithStreamingResponse

        return ContainersWithStreamingResponse(self._client.containers)

    @cached_property
    def skills(self) -> _skills.SkillsWithStreamingResponse:
        from .resources.skills import SkillsWithStreamingResponse

        return SkillsWithStreamingResponse(self._client.skills)

    @cached_property
    def videos(self) -> _videos.VideosWithStreamingResponse:
        from .resources.videos import VideosWithStreamingResponse

        return VideosWithStreamingResponse(self._client.videos)


class AsyncOpenAIWithStreamedResponse:
    _client: AsyncOpenAI

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client

    @cached_property
    def decisions(self) -> _decisions.AsyncDecisionsWithStreamingResponse:
        from .resources.decisions import AsyncDecisionsWithStreamingResponse

        return AsyncDecisionsWithStreamingResponse(self._client.decisions)

    @cached_property
    def completions(self) -> _completions.AsyncCompletionsWithStreamingResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import AsyncCompletionsWithStreamingResponse

        return AsyncCompletionsWithStreamingResponse(self._client.completions)

    @cached_property
    def chat(self) -> _chat.AsyncChatWithStreamingResponse:
        from .resources.chat import AsyncChatWithStreamingResponse

        return AsyncChatWithStreamingResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> _embeddings.AsyncEmbeddingsWithStreamingResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import AsyncEmbeddingsWithStreamingResponse

        return AsyncEmbeddingsWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> _files.AsyncFilesWithStreamingResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import AsyncFilesWithStreamingResponse

        return AsyncFilesWithStreamingResponse(self._client.files)

    @cached_property
    def images(self) -> _images.AsyncImagesWithStreamingResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import AsyncImagesWithStreamingResponse

        return AsyncImagesWithStreamingResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> _content_provenance_checks.AsyncContentProvenanceChecksWithStreamingResponse:
        from .resources.content_provenance_checks import AsyncContentProvenanceChecksWithStreamingResponse

        return AsyncContentProvenanceChecksWithStreamingResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> _audio.AsyncAudioWithStreamingResponse:
        from .resources.audio import AsyncAudioWithStreamingResponse

        return AsyncAudioWithStreamingResponse(self._client.audio)

    @cached_property
    def moderations(self) -> _moderations.AsyncModerationsWithStreamingResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import AsyncModerationsWithStreamingResponse

        return AsyncModerationsWithStreamingResponse(self._client.moderations)

    @cached_property
    def models(self) -> _models.AsyncModelsWithStreamingResponse:
        """List and describe the various models available in the API."""
        from .resources.models import AsyncModelsWithStreamingResponse

        return AsyncModelsWithStreamingResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> _fine_tuning.AsyncFineTuningWithStreamingResponse:
        from .resources.fine_tuning import AsyncFineTuningWithStreamingResponse

        return AsyncFineTuningWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> _vector_stores.AsyncVectorStoresWithStreamingResponse:
        from .resources.vector_stores import AsyncVectorStoresWithStreamingResponse

        return AsyncVectorStoresWithStreamingResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> _safety.AsyncSafetyWithStreamingResponse:
        from .resources.safety import AsyncSafetyWithStreamingResponse

        return AsyncSafetyWithStreamingResponse(self._client.safety)

    @cached_property
    def webhooks(self) -> _webhooks.AsyncWebhooksWithStreamingResponse:
        from .resources.webhooks import AsyncWebhooksWithStreamingResponse

        return AsyncWebhooksWithStreamingResponse(self._client.webhooks)

    @cached_property
    def beta(self) -> _beta.AsyncBetaWithStreamingResponse:
        from .resources.beta import AsyncBetaWithStreamingResponse

        return AsyncBetaWithStreamingResponse(self._client.beta)

    @cached_property
    def batches(self) -> _batches.AsyncBatchesWithStreamingResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import AsyncBatchesWithStreamingResponse

        return AsyncBatchesWithStreamingResponse(self._client.batches)

    @cached_property
    def uploads(self) -> _uploads.AsyncUploadsWithStreamingResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import AsyncUploadsWithStreamingResponse

        return AsyncUploadsWithStreamingResponse(self._client.uploads)

    @cached_property
    def admin(self) -> _admin.AsyncAdminWithStreamingResponse:
        from .resources.admin import AsyncAdminWithStreamingResponse

        return AsyncAdminWithStreamingResponse(self._client.admin)

    @cached_property
    def responses(self) -> _responses.AsyncResponsesWithStreamingResponse:
        """Create and manage model responses."""
        from .resources.responses import AsyncResponsesWithStreamingResponse

        return AsyncResponsesWithStreamingResponse(self._client.responses)

    @cached_property
    def live(self) -> _live.AsyncLiveWithStreamingResponse:
        from .resources.live import AsyncLiveWithStreamingResponse

        return AsyncLiveWithStreamingResponse(self._client.live)

    @cached_property
    def realtime(self) -> _realtime.AsyncRealtimeWithStreamingResponse:
        from .resources.realtime import AsyncRealtimeWithStreamingResponse

        return AsyncRealtimeWithStreamingResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> _conversations.AsyncConversationsWithStreamingResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import AsyncConversationsWithStreamingResponse

        return AsyncConversationsWithStreamingResponse(self._client.conversations)

    @cached_property
    def evals(self) -> _evals.AsyncEvalsWithStreamingResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import AsyncEvalsWithStreamingResponse

        return AsyncEvalsWithStreamingResponse(self._client.evals)

    @cached_property
    def containers(self) -> _containers.AsyncContainersWithStreamingResponse:
        from .resources.containers import AsyncContainersWithStreamingResponse

        return AsyncContainersWithStreamingResponse(self._client.containers)

    @cached_property
    def skills(self) -> _skills.AsyncSkillsWithStreamingResponse:
        from .resources.skills import AsyncSkillsWithStreamingResponse

        return AsyncSkillsWithStreamingResponse(self._client.skills)

    @cached_property
    def videos(self) -> _videos.AsyncVideosWithStreamingResponse:
        from .resources.videos import AsyncVideosWithStreamingResponse

        return AsyncVideosWithStreamingResponse(self._client.videos)


Client = OpenAI

AsyncClient = AsyncOpenAI
