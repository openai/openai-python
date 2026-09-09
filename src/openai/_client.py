# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping, Callable, Awaitable
from typing_extensions import Self, Unpack, override

import httpx2

from . import _exceptions
from ._qs import Querystring
from .auth import WorkloadIdentity, WorkloadIdentityAuth, X509WorkloadIdentity
from ._types import (
    Omit,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    HttpxSendArgs,
    RequestOptions,
    not_given,
)
from ._utils import (
    is_given,
    is_mapping,
    is_mapping_t,
    get_async_library,
)
from ._compat import cached_property
from ._httpx2 import normalize_httpx_url, is_httpx2_sync_client, is_httpx2_async_client
from ._models import SecurityOptions, FinalRequestOptions
from ._version import __version__
from ._provider import _Provider, _provider_name, _ProviderRuntime, _configure_provider
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from .auth._x509 import (
    MTLS_API_BASE_URL,
    SyncX509WorkloadIdentityAuth,
    AsyncX509WorkloadIdentityAuth,
    validate_x509_api_url,
    is_x509_workload_identity,
    x509_data_residency_base_url,
    validate_x509_api_credentials,
    x509_safe_environment_headers,
    validate_x509_request_authority,
)
from ._exceptions import OpenAIError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from ._data_residency import DataResidency, resolve_data_residency

if TYPE_CHECKING:
    from .resources import (
        beta,
        chat,
        admin,
        audio,
        evals,
        files,
        images,
        models,
        safety,
        skills,
        videos,
        batches,
        uploads,
        realtime,
        responses,
        containers,
        embeddings,
        completions,
        fine_tuning,
        moderations,
        conversations,
        vector_stores,
        content_provenance_checks,
    )
    from .resources.files import Files, AsyncFiles
    from .resources.images import Images, AsyncImages
    from .resources.models import Models, AsyncModels
    from .resources.videos import Videos, AsyncVideos
    from .resources.batches import Batches, AsyncBatches
    from .resources.beta.beta import Beta, AsyncBeta
    from .resources.chat.chat import Chat, AsyncChat
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


def _has_header(headers: Headers, header: str) -> bool:
    header = header.lower()
    return any(key.lower() == header for key in headers)


def _has_omitted_header(headers: Headers, header: str) -> bool:
    header = header.lower()
    return any(key.lower() == header and isinstance(value, Omit) for key, value in headers.items())


class OpenAI(SyncAPIClient):
    # client options
    api_key: str
    admin_api_key: str | None
    workload_identity: WorkloadIdentity | X509WorkloadIdentity | None
    organization: str | None
    project: str | None
    webhook_secret: str | None
    _workload_identity_auth: WorkloadIdentityAuth | SyncX509WorkloadIdentityAuth | None
    _provider: _Provider | None
    _provider_runtime: _ProviderRuntime | None
    _base_url_was_default: bool
    _data_residency: DataResidency | None
    _ambient_authorizations: frozenset[str]

    websocket_base_url: str | httpx2.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    @property
    @override
    def base_url(self) -> httpx2.URL:
        return self._base_url

    @base_url.setter
    def base_url(self, url: httpx2.URL | str) -> None:
        normalized_url = normalize_httpx_url(url)
        if is_x509_workload_identity(self.workload_identity):
            validate_x509_api_url(normalized_url)
        self._base_url = self._enforce_trailing_slash(normalized_url)
        self._base_url_was_default = False
        self._data_residency = None

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
        # Configure a custom httpx2 client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx2 documentation](https://httpx2.pydantic.dev/api/#client) for more details.
        http_client: httpx2.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
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
        base_url = resolve_data_residency(
            data_residency, base_url, provider=provider, websocket_base_url=websocket_base_url
        )
        base_url = x509_data_residency_base_url(base_url, data_residency, workload_identity)
        provider_runtime: _ProviderRuntime | None = None
        if provider is not None:
            provider_name = _provider_name(provider)
            conflicts = [
                name
                for name, value in (
                    ("api_key", api_key),
                    ("admin_api_key", admin_api_key),
                    ("workload_identity", workload_identity),
                    ("base_url", base_url),
                )
                if value is not None
            ]
            if conflicts:
                formatted = ", ".join(f"`{name}`" for name in conflicts)
                raise OpenAIError(
                    f"`provider` cannot be combined with top-level {formatted}. "
                    f"Move provider authentication and routing options into `{provider_name}(...)`."
                )

            provider_runtime = _configure_provider(provider)

        self._provider = provider
        self._provider_runtime = provider_runtime

        if api_key is not None and api_key != WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER and workload_identity is not None:
            raise OpenAIError("The `api_key` and `workload_identity` arguments are mutually exclusive")

        if is_x509_workload_identity(workload_identity):
            workload_identity = workload_identity.copy()
        self.workload_identity = workload_identity if provider_runtime is None else None

        if provider_runtime is not None:
            self.api_key = ""
            self._api_key_provider = None
            self._workload_identity_auth = None
        elif workload_identity is not None:
            self.api_key = WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
            self._api_key_provider = None
            self._workload_identity_auth = None
        else:
            if api_key is None:
                api_key = os.environ.get("OPENAI_API_KEY")
            if callable(api_key):
                self.api_key = ""
                self._api_key_provider: Callable[[], str] | None = api_key  # type: ignore[no-redef]
            else:
                self.api_key = api_key or ""
                self._api_key_provider = None
            self._workload_identity_auth = None

        if admin_api_key is None and provider_runtime is None:
            admin_api_key = os.environ.get("OPENAI_ADMIN_KEY")
        self.admin_api_key = admin_api_key if provider_runtime is None else None

        if (
            provider_runtime is None
            and _enforce_credentials
            and not self.api_key
            and self._api_key_provider is None
            and workload_identity is None
            and self.admin_api_key is None
        ):
            raise OpenAIError(
                "Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable."
            )

        if organization is None and provider_runtime is None:
            organization = os.environ.get("OPENAI_ORG_ID")
        self.organization = organization

        if project is None and provider_runtime is None:
            project = os.environ.get("OPENAI_PROJECT_ID")
        self.project = project

        if webhook_secret is None:
            webhook_secret = os.environ.get("OPENAI_WEBHOOK_SECRET")
        self.webhook_secret = webhook_secret

        self.websocket_base_url = websocket_base_url

        if is_x509_workload_identity(workload_identity):
            x509_identity = workload_identity
            subject_token_identity = None
        elif workload_identity is None:
            x509_identity = None
            subject_token_identity = None
        elif "provider" in workload_identity:
            x509_identity = None
            subject_token_identity = workload_identity
        else:
            raise OpenAIError("Invalid `workload_identity` configuration: expected an X.509 or subject-token identity")
        if provider_runtime is not None:
            base_url = provider_runtime.base_url
        elif base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        self._base_url_was_default = provider_runtime is None and base_url is None
        self._data_residency = data_residency
        if base_url is None:
            base_url = MTLS_API_BASE_URL if x509_identity is not None else "https://api.openai.com/v1"
        if x509_identity is not None:
            validate_x509_api_url(base_url)

        self._ambient_authorizations = frozenset()
        custom_headers_env = os.environ.get("OPENAI_CUSTOM_HEADERS") if provider_runtime is None else None
        if custom_headers_env is not None:
            parsed: dict[str, str] = {}
            for line in custom_headers_env.split("\n"):
                colon = line.find(":")
                if colon >= 0:
                    parsed[line[:colon].strip()] = line[colon + 1 :].strip()
            explicit_headers: Mapping[str, str] = default_headers if is_mapping_t(default_headers) else {}
            explicit_authorization = any(name.lower() == "authorization" for name in explicit_headers)
            if explicit_authorization:
                parsed = {name: value for name, value in parsed.items() if name.lower() != "authorization"}
            elif x509_identity is None:
                self._ambient_authorizations = frozenset(
                    value for name, value in parsed.items() if name.lower() == "authorization"
                )
            default_headers = {
                **x509_safe_environment_headers(parsed, x509_identity),
                **explicit_headers,
            }

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        if x509_identity is not None:
            self._workload_identity_auth = SyncX509WorkloadIdentityAuth(
                workload_identity=x509_identity.copy(), http_client=self._client, max_retries=max_retries
            )
        elif subject_token_identity is not None:
            self._workload_identity_auth = WorkloadIdentityAuth(
                workload_identity=subject_token_identity,
                _use_httpx2=is_httpx2_sync_client(self._client),
            )

        self._default_stream_cls = Stream

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
        from .resources.responses import Responses

        return Responses(self)

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

    def _send_with_auth_retry(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        retried: bool = False,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        used_access_token: str | None = None
        request_is_replayable = False
        x509_auth = self._workload_identity_auth

        if x509_auth is not None:
            if isinstance(x509_auth, SyncX509WorkloadIdentityAuth):
                if x509_auth.workload_identity != self.workload_identity:
                    raise OpenAIError("X.509 workload identity cannot be changed after client construction")
                validate_x509_api_url(request.url, expected_origin=self.base_url)
                validate_x509_request_authority(request)
                validate_x509_api_credentials(request)
            if x509_auth._follow_redirects is not None:
                kwargs["follow_redirects"] = x509_auth._follow_redirects
            authorization = request.headers.get("Authorization")
            if authorization == f"Bearer {WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}":
                used_access_token = (
                    x509_auth.get_token_for_request(request)
                    if isinstance(x509_auth, SyncX509WorkloadIdentityAuth)
                    else x509_auth.get_token()
                )
                request.headers["Authorization"] = f"Bearer {used_access_token}"
                request_is_replayable = x509_auth._can_retry_request(request)

        if isinstance(x509_auth, SyncX509WorkloadIdentityAuth):
            response = x509_auth.send_api_request(
                request,
                expected_origin=self.base_url,
                expected_authorization=request.headers.get("Authorization"),
                stream=stream,
                **kwargs,
            )
        else:
            response = super()._send_request(request, stream=stream, **kwargs)
        if response.status_code != 401 or self._workload_identity_auth is None or used_access_token is None:
            return response

        self._workload_identity_auth.invalidate_token(used_access_token)
        if retried or not request_is_replayable:
            return response

        response.close()
        self._workload_identity_auth._prepare_retry_request(request)
        request.headers["Authorization"] = f"Bearer {WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}"
        return self._send_with_auth_retry(request, stream=stream, retried=True, **kwargs)

    @override
    def _send_request(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        response = self._send_with_auth_retry(request, stream=stream, **kwargs)
        if self._provider_runtime is not None and self._provider_runtime.normalize_response is not None:
            response = self._provider_runtime.normalize_response(response)
        return response

    @override
    def _auth_headers(self, security: SecurityOptions) -> dict[str, str]:
        if self._provider_runtime is not None:
            return {}

        headers: dict[str, str] = {}
        if security.get("bearer_auth", False):
            for key, value in self._bearer_auth.items():
                headers.setdefault(key, value)
        if security.get("admin_api_key_auth", False):
            for key, value in self._admin_api_key_auth.items():
                headers.setdefault(key, value)
        return headers

    @property
    def _bearer_auth(self) -> dict[str, str]:
        api_key = self.api_key
        if not api_key:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        if self._provider_runtime is not None:
            return {}

        api_key = self.api_key
        if not api_key or api_key == WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

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
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self._provider_runtime is not None:
            return

        if _has_header(headers, "Authorization") or _has_omitted_header(custom_headers, "Authorization"):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected either api_key or admin_api_key to be set. Or for one of the `Authorization` or `Authorization` headers to be explicitly omitted"'
        )

    @override
    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if self._provider_runtime is not None:
            if self._provider_runtime.transform_request is not None:
                options = self._provider_runtime.transform_request(options)
        elif self._api_key_provider is not None and options.security.get("bearer_auth", False):
            self._refresh_api_key()

        return super()._prepare_options(options)

    @override
    def _prepare_request(self, request: httpx2.Request) -> None:
        if self._provider_runtime is not None and self._provider_runtime.prepare_request is not None:
            self._provider_runtime.prepare_request(request)

    @override
    def _custom_auth(self, security: SecurityOptions) -> httpx2.Auth | None:
        if self._provider_runtime is not None or isinstance(self._workload_identity_auth, SyncX509WorkloadIdentityAuth):
            return httpx2.Auth()

        return super()._custom_auth(security)

    def _refresh_api_key(self) -> str:
        if self._api_key_provider is not None:
            self.api_key = self._api_key_provider()

        return self.api_key

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
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        provider_changed = not isinstance(provider, NotGiven) and provider is not self._provider
        inherited_organization = None if provider_changed else self.organization
        inherited_project = None if provider_changed else self.project

        headers: Mapping[str, str] = {} if provider_changed else self._custom_headers
        if (
            is_x509_workload_identity(workload_identity)
            and not is_x509_workload_identity(self.workload_identity)
            and self._ambient_authorizations
        ):
            headers = {
                name: value
                for name, value in headers.items()
                if name.lower() != "authorization" or value not in self._ambient_authorizations
            }
        if default_headers is not None:
            if any(name.lower() == "authorization" for name in default_headers):
                headers = {name: value for name, value in headers.items() if name.lower() != "authorization"}
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client

        next_provider = self._provider if isinstance(provider, NotGiven) else provider
        explicit_base_url = base_url is not None and not isinstance(base_url, NotGiven)
        next_workload_identity = workload_identity if workload_identity is not None else self.workload_identity
        if api_key is not None and workload_identity is None:
            next_workload_identity = None
        current_x509 = is_x509_workload_identity(self.workload_identity)
        next_x509 = is_x509_workload_identity(next_workload_identity)
        mode_changed = current_x509 != next_x509
        effective_data_residency = data_residency
        if effective_data_residency is None and mode_changed and not explicit_base_url:
            effective_data_residency = self._data_residency
        base_url = resolve_data_residency(
            effective_data_residency,
            not_given if base_url is None and data_residency is None else base_url,
            provider=next_provider,
            websocket_base_url=websocket_base_url,
        )
        base_url = x509_data_residency_base_url(base_url, effective_data_residency, next_workload_identity)
        preserve_default_base_url = False
        auth_options: dict[str, Any]
        if next_provider is not None:
            auth_options = {
                "provider": next_provider,
                "api_key": api_key,
                "admin_api_key": admin_api_key,
                "workload_identity": workload_identity,
                "base_url": base_url,
            }
        elif self._provider is not None:
            auth_options = {
                "api_key": api_key,
                "admin_api_key": admin_api_key,
                "workload_identity": workload_identity,
                "base_url": base_url,
            }
        else:
            inherited_base_url = None if mode_changed and self._base_url_was_default else self.base_url
            preserve_default_base_url = base_url is None and not mode_changed and self._base_url_was_default
            auth_options = {
                "api_key": api_key
                if workload_identity is not None
                else api_key or self._api_key_provider or self.api_key,
                "admin_api_key": admin_api_key or self.admin_api_key,
                "workload_identity": next_workload_identity,
                "base_url": base_url or inherited_base_url,
            }

        copied = self.__class__(
            organization=organization or inherited_organization,
            project=project or inherited_project,
            webhook_secret=webhook_secret or self.webhook_secret,
            websocket_base_url=None if data_residency is not None else websocket_base_url or self.websocket_base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            _enforce_credentials=True if _enforce_credentials is None else _enforce_credentials,
            **auth_options,
            **_extra_kwargs,
        )
        if preserve_default_base_url:
            copied._base_url_was_default = True
        overridden_authorizations = default_headers if default_headers is not None else set_default_headers
        explicit_authorization_override = overridden_authorizations is not None and any(
            name.lower() == "authorization" for name in overridden_authorizations
        )
        if (
            self._ambient_authorizations
            and not explicit_authorization_override
            and any(
                name.lower() == "authorization" and value in self._ambient_authorizations
                for name, value in copied._custom_headers.items()
            )
        ):
            copied._ambient_authorizations = self._ambient_authorizations
        if data_residency is not None:
            copied._data_residency = data_residency
        elif not explicit_base_url and not provider_changed:
            copied._data_residency = self._data_residency
        return copied

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
    # client options
    api_key: str
    admin_api_key: str | None
    workload_identity: WorkloadIdentity | X509WorkloadIdentity | None
    organization: str | None
    project: str | None
    webhook_secret: str | None
    _workload_identity_auth: WorkloadIdentityAuth | AsyncX509WorkloadIdentityAuth | None
    _provider: _Provider | None
    _provider_runtime: _ProviderRuntime | None
    _base_url_was_default: bool
    _data_residency: DataResidency | None
    _ambient_authorizations: frozenset[str]

    websocket_base_url: str | httpx2.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    @property
    @override
    def base_url(self) -> httpx2.URL:
        return self._base_url

    @base_url.setter
    def base_url(self, url: httpx2.URL | str) -> None:
        normalized_url = normalize_httpx_url(url)
        if is_x509_workload_identity(self.workload_identity):
            validate_x509_api_url(normalized_url)
        self._base_url = self._enforce_trailing_slash(normalized_url)
        self._base_url_was_default = False
        self._data_residency = None

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
        # Configure a custom httpx2 client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx2 documentation](https://httpx2.pydantic.dev/api/#asyncclient) for more details.
        http_client: httpx2.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
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
        base_url = resolve_data_residency(
            data_residency, base_url, provider=provider, websocket_base_url=websocket_base_url
        )
        base_url = x509_data_residency_base_url(base_url, data_residency, workload_identity)
        provider_runtime: _ProviderRuntime | None = None
        if provider is not None:
            provider_name = _provider_name(provider)
            conflicts = [
                name
                for name, value in (
                    ("api_key", api_key),
                    ("admin_api_key", admin_api_key),
                    ("workload_identity", workload_identity),
                    ("base_url", base_url),
                )
                if value is not None
            ]
            if conflicts:
                formatted = ", ".join(f"`{name}`" for name in conflicts)
                raise OpenAIError(
                    f"`provider` cannot be combined with top-level {formatted}. "
                    f"Move provider authentication and routing options into `{provider_name}(...)`."
                )

            provider_runtime = _configure_provider(provider)

        self._provider = provider
        self._provider_runtime = provider_runtime

        if api_key is not None and api_key != WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER and workload_identity is not None:
            raise OpenAIError("The `api_key` and `workload_identity` arguments are mutually exclusive")

        if is_x509_workload_identity(workload_identity):
            workload_identity = workload_identity.copy()
        self.workload_identity = workload_identity if provider_runtime is None else None

        if provider_runtime is not None:
            self.api_key = ""
            self._api_key_provider = None
            self._workload_identity_auth = None
        elif workload_identity is not None:
            self.api_key = WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
            self._api_key_provider = None
            self._workload_identity_auth = None
        else:
            if api_key is None:
                api_key = os.environ.get("OPENAI_API_KEY")
            if callable(api_key):
                self.api_key = ""
                self._api_key_provider: Callable[[], Awaitable[str]] | None = api_key  # type: ignore[no-redef]
            else:
                self.api_key = api_key or ""
                self._api_key_provider = None
            self._workload_identity_auth = None

        if admin_api_key is None and provider_runtime is None:
            admin_api_key = os.environ.get("OPENAI_ADMIN_KEY")
        self.admin_api_key = admin_api_key if provider_runtime is None else None

        if (
            provider_runtime is None
            and _enforce_credentials
            and not self.api_key
            and self._api_key_provider is None
            and workload_identity is None
            and self.admin_api_key is None
        ):
            raise OpenAIError(
                "Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable."
            )

        if organization is None and provider_runtime is None:
            organization = os.environ.get("OPENAI_ORG_ID")
        self.organization = organization

        if project is None and provider_runtime is None:
            project = os.environ.get("OPENAI_PROJECT_ID")
        self.project = project

        if webhook_secret is None:
            webhook_secret = os.environ.get("OPENAI_WEBHOOK_SECRET")
        self.webhook_secret = webhook_secret

        self.websocket_base_url = websocket_base_url

        if is_x509_workload_identity(workload_identity):
            x509_identity = workload_identity
            subject_token_identity = None
        elif workload_identity is None:
            x509_identity = None
            subject_token_identity = None
        elif "provider" in workload_identity:
            x509_identity = None
            subject_token_identity = workload_identity
        else:
            raise OpenAIError("Invalid `workload_identity` configuration: expected an X.509 or subject-token identity")
        if provider_runtime is not None:
            base_url = provider_runtime.base_url
        elif base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        self._base_url_was_default = provider_runtime is None and base_url is None
        self._data_residency = data_residency
        if base_url is None:
            base_url = MTLS_API_BASE_URL if x509_identity is not None else "https://api.openai.com/v1"
        if x509_identity is not None:
            validate_x509_api_url(base_url)

        self._ambient_authorizations = frozenset()
        custom_headers_env = os.environ.get("OPENAI_CUSTOM_HEADERS") if provider_runtime is None else None
        if custom_headers_env is not None:
            parsed: dict[str, str] = {}
            for line in custom_headers_env.split("\n"):
                colon = line.find(":")
                if colon >= 0:
                    parsed[line[:colon].strip()] = line[colon + 1 :].strip()
            explicit_headers: Mapping[str, str] = default_headers if is_mapping_t(default_headers) else {}
            explicit_authorization = any(name.lower() == "authorization" for name in explicit_headers)
            if explicit_authorization:
                parsed = {name: value for name, value in parsed.items() if name.lower() != "authorization"}
            elif x509_identity is None:
                self._ambient_authorizations = frozenset(
                    value for name, value in parsed.items() if name.lower() == "authorization"
                )
            default_headers = {
                **x509_safe_environment_headers(parsed, x509_identity),
                **explicit_headers,
            }

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        if x509_identity is not None:
            self._workload_identity_auth = AsyncX509WorkloadIdentityAuth(
                workload_identity=x509_identity.copy(), http_client=self._client, max_retries=max_retries
            )
        elif subject_token_identity is not None:
            self._workload_identity_auth = WorkloadIdentityAuth(
                workload_identity=subject_token_identity,
                _use_httpx2=is_httpx2_async_client(self._client),
            )

        self._default_stream_cls = AsyncStream

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
        from .resources.responses import AsyncResponses

        return AsyncResponses(self)

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

    async def _send_with_auth_retry(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        retried: bool = False,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        used_access_token: str | None = None
        request_is_replayable = False
        x509_auth = self._workload_identity_auth

        if x509_auth is not None:
            if isinstance(x509_auth, AsyncX509WorkloadIdentityAuth):
                if x509_auth.workload_identity != self.workload_identity:
                    raise OpenAIError("X.509 workload identity cannot be changed after client construction")
                validate_x509_api_url(request.url, expected_origin=self.base_url)
                validate_x509_request_authority(request)
                validate_x509_api_credentials(request)
            if x509_auth._follow_redirects is not None:
                kwargs["follow_redirects"] = x509_auth._follow_redirects
            authorization = request.headers.get("Authorization")
            if authorization == f"Bearer {WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}":
                used_access_token = (
                    await x509_auth.get_token_for_request(request)
                    if isinstance(x509_auth, AsyncX509WorkloadIdentityAuth)
                    else await x509_auth.get_token_async()
                )
                request.headers["Authorization"] = f"Bearer {used_access_token}"
                request_is_replayable = x509_auth._can_retry_request(request)

        if isinstance(x509_auth, AsyncX509WorkloadIdentityAuth):
            response = await x509_auth.send_api_request(
                request,
                expected_origin=self.base_url,
                expected_authorization=request.headers.get("Authorization"),
                stream=stream,
                **kwargs,
            )
        else:
            response = await super()._send_request(request, stream=stream, **kwargs)
        if response.status_code != 401 or self._workload_identity_auth is None or used_access_token is None:
            return response

        self._workload_identity_auth.invalidate_token(used_access_token)
        if retried or not request_is_replayable:
            return response

        await response.aclose()
        self._workload_identity_auth._prepare_retry_request(request)
        request.headers["Authorization"] = f"Bearer {WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}"
        return await self._send_with_auth_retry(request, stream=stream, retried=True, **kwargs)

    @override
    async def _send_request(
        self,
        request: httpx2.Request,
        *,
        stream: bool,
        **kwargs: Unpack[HttpxSendArgs],
    ) -> httpx2.Response:
        response = await self._send_with_auth_retry(request, stream=stream, **kwargs)
        if self._provider_runtime is not None:
            if self._provider_runtime.normalize_async_response is not None:
                response = await self._provider_runtime.normalize_async_response(response)
            elif self._provider_runtime.normalize_response is not None:
                response = self._provider_runtime.normalize_response(response)
        return response

    @override
    def _auth_headers(self, security: SecurityOptions) -> dict[str, str]:
        if self._provider_runtime is not None:
            return {}

        headers: dict[str, str] = {}
        if security.get("bearer_auth", False):
            for key, value in self._bearer_auth.items():
                headers.setdefault(key, value)
        if security.get("admin_api_key_auth", False):
            for key, value in self._admin_api_key_auth.items():
                headers.setdefault(key, value)
        return headers

    @property
    def _bearer_auth(self) -> dict[str, str]:
        api_key = self.api_key
        if not api_key:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        if self._provider_runtime is not None:
            return {}

        api_key = self.api_key
        if not api_key or api_key == WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

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
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self._provider_runtime is not None:
            return

        if _has_header(headers, "Authorization") or _has_omitted_header(custom_headers, "Authorization"):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected either api_key or admin_api_key to be set. Or for one of the `Authorization` or `Authorization` headers to be explicitly omitted"'
        )

    @override
    async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if self._provider_runtime is not None:
            if self._provider_runtime.transform_async_request is not None:
                options = await self._provider_runtime.transform_async_request(options)
            elif self._provider_runtime.transform_request is not None:
                options = self._provider_runtime.transform_request(options)
        elif self._api_key_provider is not None and options.security.get("bearer_auth", False):
            await self._refresh_api_key()

        return await super()._prepare_options(options)

    @override
    async def _prepare_request(self, request: httpx2.Request) -> None:
        if self._provider_runtime is None:
            return

        if self._provider_runtime.prepare_async_request is not None:
            await self._provider_runtime.prepare_async_request(request)
        elif self._provider_runtime.prepare_request is not None:
            self._provider_runtime.prepare_request(request)

    @property
    @override
    def custom_auth(self) -> httpx2.Auth | None:
        if self._provider_runtime is not None or isinstance(
            self._workload_identity_auth, AsyncX509WorkloadIdentityAuth
        ):
            return httpx2.Auth()

        return super().custom_auth

    async def _refresh_api_key(self) -> str:
        if self._api_key_provider is not None:
            self.api_key = await self._api_key_provider()

        return self.api_key

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
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        provider_changed = not isinstance(provider, NotGiven) and provider is not self._provider
        inherited_organization = None if provider_changed else self.organization
        inherited_project = None if provider_changed else self.project

        headers: Mapping[str, str] = {} if provider_changed else self._custom_headers
        if (
            is_x509_workload_identity(workload_identity)
            and not is_x509_workload_identity(self.workload_identity)
            and self._ambient_authorizations
        ):
            headers = {
                name: value
                for name, value in headers.items()
                if name.lower() != "authorization" or value not in self._ambient_authorizations
            }
        if default_headers is not None:
            if any(name.lower() == "authorization" for name in default_headers):
                headers = {name: value for name, value in headers.items() if name.lower() != "authorization"}
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        next_provider = self._provider if isinstance(provider, NotGiven) else provider
        explicit_base_url = base_url is not None and not isinstance(base_url, NotGiven)
        next_workload_identity = workload_identity if workload_identity is not None else self.workload_identity
        if api_key is not None and workload_identity is None:
            next_workload_identity = None
        current_x509 = is_x509_workload_identity(self.workload_identity)
        next_x509 = is_x509_workload_identity(next_workload_identity)
        mode_changed = current_x509 != next_x509
        effective_data_residency = data_residency
        if effective_data_residency is None and mode_changed and not explicit_base_url:
            effective_data_residency = self._data_residency
        base_url = resolve_data_residency(
            effective_data_residency,
            not_given if base_url is None and data_residency is None else base_url,
            provider=next_provider,
            websocket_base_url=websocket_base_url,
        )
        base_url = x509_data_residency_base_url(base_url, effective_data_residency, next_workload_identity)
        preserve_default_base_url = False
        auth_options: dict[str, Any]
        if next_provider is not None:
            auth_options = {
                "provider": next_provider,
                "api_key": api_key,
                "admin_api_key": admin_api_key,
                "workload_identity": workload_identity,
                "base_url": base_url,
            }
        elif self._provider is not None:
            auth_options = {
                "api_key": api_key,
                "admin_api_key": admin_api_key,
                "workload_identity": workload_identity,
                "base_url": base_url,
            }
        else:
            inherited_base_url = None if mode_changed and self._base_url_was_default else self.base_url
            preserve_default_base_url = base_url is None and not mode_changed and self._base_url_was_default
            auth_options = {
                "api_key": api_key
                if workload_identity is not None
                else api_key or self._api_key_provider or self.api_key,
                "admin_api_key": admin_api_key or self.admin_api_key,
                "workload_identity": next_workload_identity,
                "base_url": base_url or inherited_base_url,
            }

        copied = self.__class__(
            organization=organization or inherited_organization,
            project=project or inherited_project,
            webhook_secret=webhook_secret or self.webhook_secret,
            websocket_base_url=None if data_residency is not None else websocket_base_url or self.websocket_base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            _enforce_credentials=True if _enforce_credentials is None else _enforce_credentials,
            **auth_options,
            **_extra_kwargs,
        )
        if preserve_default_base_url:
            copied._base_url_was_default = True
        overridden_authorizations = default_headers if default_headers is not None else set_default_headers
        explicit_authorization_override = overridden_authorizations is not None and any(
            name.lower() == "authorization" for name in overridden_authorizations
        )
        if (
            self._ambient_authorizations
            and not explicit_authorization_override
            and any(
                name.lower() == "authorization" and value in self._ambient_authorizations
                for name, value in copied._custom_headers.items()
            )
        ):
            copied._ambient_authorizations = self._ambient_authorizations
        if data_residency is not None:
            copied._data_residency = data_residency
        elif not explicit_base_url and not provider_changed:
            copied._data_residency = self._data_residency
        return copied

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
    def completions(self) -> completions.CompletionsWithRawResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import CompletionsWithRawResponse

        return CompletionsWithRawResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.ChatWithRawResponse:
        from .resources.chat import ChatWithRawResponse

        return ChatWithRawResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsWithRawResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import EmbeddingsWithRawResponse

        return EmbeddingsWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.FilesWithRawResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import FilesWithRawResponse

        return FilesWithRawResponse(self._client.files)

    @cached_property
    def images(self) -> images.ImagesWithRawResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import ImagesWithRawResponse

        return ImagesWithRawResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> content_provenance_checks.ContentProvenanceChecksWithRawResponse:
        from .resources.content_provenance_checks import ContentProvenanceChecksWithRawResponse

        return ContentProvenanceChecksWithRawResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> audio.AudioWithRawResponse:
        from .resources.audio import AudioWithRawResponse

        return AudioWithRawResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.ModerationsWithRawResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import ModerationsWithRawResponse

        return ModerationsWithRawResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.ModelsWithRawResponse:
        """List and describe the various models available in the API."""
        from .resources.models import ModelsWithRawResponse

        return ModelsWithRawResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.FineTuningWithRawResponse:
        from .resources.fine_tuning import FineTuningWithRawResponse

        return FineTuningWithRawResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.VectorStoresWithRawResponse:
        from .resources.vector_stores import VectorStoresWithRawResponse

        return VectorStoresWithRawResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> safety.SafetyWithRawResponse:
        from .resources.safety import SafetyWithRawResponse

        return SafetyWithRawResponse(self._client.safety)

    @cached_property
    def beta(self) -> beta.BetaWithRawResponse:
        from .resources.beta import BetaWithRawResponse

        return BetaWithRawResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.BatchesWithRawResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import BatchesWithRawResponse

        return BatchesWithRawResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.UploadsWithRawResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import UploadsWithRawResponse

        return UploadsWithRawResponse(self._client.uploads)

    @cached_property
    def admin(self) -> admin.AdminWithRawResponse:
        from .resources.admin import AdminWithRawResponse

        return AdminWithRawResponse(self._client.admin)

    @cached_property
    def responses(self) -> responses.ResponsesWithRawResponse:
        from .resources.responses import ResponsesWithRawResponse

        return ResponsesWithRawResponse(self._client.responses)

    @cached_property
    def realtime(self) -> realtime.RealtimeWithRawResponse:
        from .resources.realtime import RealtimeWithRawResponse

        return RealtimeWithRawResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> conversations.ConversationsWithRawResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import ConversationsWithRawResponse

        return ConversationsWithRawResponse(self._client.conversations)

    @cached_property
    def evals(self) -> evals.EvalsWithRawResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import EvalsWithRawResponse

        return EvalsWithRawResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.ContainersWithRawResponse:
        from .resources.containers import ContainersWithRawResponse

        return ContainersWithRawResponse(self._client.containers)

    @cached_property
    def skills(self) -> skills.SkillsWithRawResponse:
        from .resources.skills import SkillsWithRawResponse

        return SkillsWithRawResponse(self._client.skills)

    @cached_property
    def videos(self) -> videos.VideosWithRawResponse:
        from .resources.videos import VideosWithRawResponse

        return VideosWithRawResponse(self._client.videos)


class AsyncOpenAIWithRawResponse:
    _client: AsyncOpenAI

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client

    @cached_property
    def completions(self) -> completions.AsyncCompletionsWithRawResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import AsyncCompletionsWithRawResponse

        return AsyncCompletionsWithRawResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.AsyncChatWithRawResponse:
        from .resources.chat import AsyncChatWithRawResponse

        return AsyncChatWithRawResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsWithRawResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import AsyncEmbeddingsWithRawResponse

        return AsyncEmbeddingsWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.AsyncFilesWithRawResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import AsyncFilesWithRawResponse

        return AsyncFilesWithRawResponse(self._client.files)

    @cached_property
    def images(self) -> images.AsyncImagesWithRawResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import AsyncImagesWithRawResponse

        return AsyncImagesWithRawResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> content_provenance_checks.AsyncContentProvenanceChecksWithRawResponse:
        from .resources.content_provenance_checks import AsyncContentProvenanceChecksWithRawResponse

        return AsyncContentProvenanceChecksWithRawResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> audio.AsyncAudioWithRawResponse:
        from .resources.audio import AsyncAudioWithRawResponse

        return AsyncAudioWithRawResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.AsyncModerationsWithRawResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import AsyncModerationsWithRawResponse

        return AsyncModerationsWithRawResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.AsyncModelsWithRawResponse:
        """List and describe the various models available in the API."""
        from .resources.models import AsyncModelsWithRawResponse

        return AsyncModelsWithRawResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.AsyncFineTuningWithRawResponse:
        from .resources.fine_tuning import AsyncFineTuningWithRawResponse

        return AsyncFineTuningWithRawResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.AsyncVectorStoresWithRawResponse:
        from .resources.vector_stores import AsyncVectorStoresWithRawResponse

        return AsyncVectorStoresWithRawResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> safety.AsyncSafetyWithRawResponse:
        from .resources.safety import AsyncSafetyWithRawResponse

        return AsyncSafetyWithRawResponse(self._client.safety)

    @cached_property
    def beta(self) -> beta.AsyncBetaWithRawResponse:
        from .resources.beta import AsyncBetaWithRawResponse

        return AsyncBetaWithRawResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.AsyncBatchesWithRawResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import AsyncBatchesWithRawResponse

        return AsyncBatchesWithRawResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.AsyncUploadsWithRawResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import AsyncUploadsWithRawResponse

        return AsyncUploadsWithRawResponse(self._client.uploads)

    @cached_property
    def admin(self) -> admin.AsyncAdminWithRawResponse:
        from .resources.admin import AsyncAdminWithRawResponse

        return AsyncAdminWithRawResponse(self._client.admin)

    @cached_property
    def responses(self) -> responses.AsyncResponsesWithRawResponse:
        from .resources.responses import AsyncResponsesWithRawResponse

        return AsyncResponsesWithRawResponse(self._client.responses)

    @cached_property
    def realtime(self) -> realtime.AsyncRealtimeWithRawResponse:
        from .resources.realtime import AsyncRealtimeWithRawResponse

        return AsyncRealtimeWithRawResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> conversations.AsyncConversationsWithRawResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import AsyncConversationsWithRawResponse

        return AsyncConversationsWithRawResponse(self._client.conversations)

    @cached_property
    def evals(self) -> evals.AsyncEvalsWithRawResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import AsyncEvalsWithRawResponse

        return AsyncEvalsWithRawResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.AsyncContainersWithRawResponse:
        from .resources.containers import AsyncContainersWithRawResponse

        return AsyncContainersWithRawResponse(self._client.containers)

    @cached_property
    def skills(self) -> skills.AsyncSkillsWithRawResponse:
        from .resources.skills import AsyncSkillsWithRawResponse

        return AsyncSkillsWithRawResponse(self._client.skills)

    @cached_property
    def videos(self) -> videos.AsyncVideosWithRawResponse:
        from .resources.videos import AsyncVideosWithRawResponse

        return AsyncVideosWithRawResponse(self._client.videos)


class OpenAIWithStreamedResponse:
    _client: OpenAI

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    @cached_property
    def completions(self) -> completions.CompletionsWithStreamingResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import CompletionsWithStreamingResponse

        return CompletionsWithStreamingResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.ChatWithStreamingResponse:
        from .resources.chat import ChatWithStreamingResponse

        return ChatWithStreamingResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsWithStreamingResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import EmbeddingsWithStreamingResponse

        return EmbeddingsWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.FilesWithStreamingResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import FilesWithStreamingResponse

        return FilesWithStreamingResponse(self._client.files)

    @cached_property
    def images(self) -> images.ImagesWithStreamingResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import ImagesWithStreamingResponse

        return ImagesWithStreamingResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> content_provenance_checks.ContentProvenanceChecksWithStreamingResponse:
        from .resources.content_provenance_checks import ContentProvenanceChecksWithStreamingResponse

        return ContentProvenanceChecksWithStreamingResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> audio.AudioWithStreamingResponse:
        from .resources.audio import AudioWithStreamingResponse

        return AudioWithStreamingResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.ModerationsWithStreamingResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import ModerationsWithStreamingResponse

        return ModerationsWithStreamingResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.ModelsWithStreamingResponse:
        """List and describe the various models available in the API."""
        from .resources.models import ModelsWithStreamingResponse

        return ModelsWithStreamingResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.FineTuningWithStreamingResponse:
        from .resources.fine_tuning import FineTuningWithStreamingResponse

        return FineTuningWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.VectorStoresWithStreamingResponse:
        from .resources.vector_stores import VectorStoresWithStreamingResponse

        return VectorStoresWithStreamingResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> safety.SafetyWithStreamingResponse:
        from .resources.safety import SafetyWithStreamingResponse

        return SafetyWithStreamingResponse(self._client.safety)

    @cached_property
    def beta(self) -> beta.BetaWithStreamingResponse:
        from .resources.beta import BetaWithStreamingResponse

        return BetaWithStreamingResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.BatchesWithStreamingResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import BatchesWithStreamingResponse

        return BatchesWithStreamingResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.UploadsWithStreamingResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import UploadsWithStreamingResponse

        return UploadsWithStreamingResponse(self._client.uploads)

    @cached_property
    def admin(self) -> admin.AdminWithStreamingResponse:
        from .resources.admin import AdminWithStreamingResponse

        return AdminWithStreamingResponse(self._client.admin)

    @cached_property
    def responses(self) -> responses.ResponsesWithStreamingResponse:
        from .resources.responses import ResponsesWithStreamingResponse

        return ResponsesWithStreamingResponse(self._client.responses)

    @cached_property
    def realtime(self) -> realtime.RealtimeWithStreamingResponse:
        from .resources.realtime import RealtimeWithStreamingResponse

        return RealtimeWithStreamingResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> conversations.ConversationsWithStreamingResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import ConversationsWithStreamingResponse

        return ConversationsWithStreamingResponse(self._client.conversations)

    @cached_property
    def evals(self) -> evals.EvalsWithStreamingResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import EvalsWithStreamingResponse

        return EvalsWithStreamingResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.ContainersWithStreamingResponse:
        from .resources.containers import ContainersWithStreamingResponse

        return ContainersWithStreamingResponse(self._client.containers)

    @cached_property
    def skills(self) -> skills.SkillsWithStreamingResponse:
        from .resources.skills import SkillsWithStreamingResponse

        return SkillsWithStreamingResponse(self._client.skills)

    @cached_property
    def videos(self) -> videos.VideosWithStreamingResponse:
        from .resources.videos import VideosWithStreamingResponse

        return VideosWithStreamingResponse(self._client.videos)


class AsyncOpenAIWithStreamedResponse:
    _client: AsyncOpenAI

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client

    @cached_property
    def completions(self) -> completions.AsyncCompletionsWithStreamingResponse:
        """
        Given a prompt, the model will return one or more predicted completions, and can also return the probabilities of alternative tokens at each position.
        """
        from .resources.completions import AsyncCompletionsWithStreamingResponse

        return AsyncCompletionsWithStreamingResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.AsyncChatWithStreamingResponse:
        from .resources.chat import AsyncChatWithStreamingResponse

        return AsyncChatWithStreamingResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsWithStreamingResponse:
        """
        Get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.
        """
        from .resources.embeddings import AsyncEmbeddingsWithStreamingResponse

        return AsyncEmbeddingsWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.AsyncFilesWithStreamingResponse:
        """
        Files are used to upload documents that can be used with features like Assistants and Fine-tuning.
        """
        from .resources.files import AsyncFilesWithStreamingResponse

        return AsyncFilesWithStreamingResponse(self._client.files)

    @cached_property
    def images(self) -> images.AsyncImagesWithStreamingResponse:
        """Given a prompt and/or an input image, the model will generate a new image."""
        from .resources.images import AsyncImagesWithStreamingResponse

        return AsyncImagesWithStreamingResponse(self._client.images)

    @cached_property
    def content_provenance_checks(self) -> content_provenance_checks.AsyncContentProvenanceChecksWithStreamingResponse:
        from .resources.content_provenance_checks import AsyncContentProvenanceChecksWithStreamingResponse

        return AsyncContentProvenanceChecksWithStreamingResponse(self._client.content_provenance_checks)

    @cached_property
    def audio(self) -> audio.AsyncAudioWithStreamingResponse:
        from .resources.audio import AsyncAudioWithStreamingResponse

        return AsyncAudioWithStreamingResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.AsyncModerationsWithStreamingResponse:
        """
        Given text and/or image inputs, classifies if those inputs are potentially harmful.
        """
        from .resources.moderations import AsyncModerationsWithStreamingResponse

        return AsyncModerationsWithStreamingResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.AsyncModelsWithStreamingResponse:
        """List and describe the various models available in the API."""
        from .resources.models import AsyncModelsWithStreamingResponse

        return AsyncModelsWithStreamingResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.AsyncFineTuningWithStreamingResponse:
        from .resources.fine_tuning import AsyncFineTuningWithStreamingResponse

        return AsyncFineTuningWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.AsyncVectorStoresWithStreamingResponse:
        from .resources.vector_stores import AsyncVectorStoresWithStreamingResponse

        return AsyncVectorStoresWithStreamingResponse(self._client.vector_stores)

    @cached_property
    def safety(self) -> safety.AsyncSafetyWithStreamingResponse:
        from .resources.safety import AsyncSafetyWithStreamingResponse

        return AsyncSafetyWithStreamingResponse(self._client.safety)

    @cached_property
    def beta(self) -> beta.AsyncBetaWithStreamingResponse:
        from .resources.beta import AsyncBetaWithStreamingResponse

        return AsyncBetaWithStreamingResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.AsyncBatchesWithStreamingResponse:
        """Create large batches of API requests to run asynchronously."""
        from .resources.batches import AsyncBatchesWithStreamingResponse

        return AsyncBatchesWithStreamingResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.AsyncUploadsWithStreamingResponse:
        """Use Uploads to upload large files in multiple parts."""
        from .resources.uploads import AsyncUploadsWithStreamingResponse

        return AsyncUploadsWithStreamingResponse(self._client.uploads)

    @cached_property
    def admin(self) -> admin.AsyncAdminWithStreamingResponse:
        from .resources.admin import AsyncAdminWithStreamingResponse

        return AsyncAdminWithStreamingResponse(self._client.admin)

    @cached_property
    def responses(self) -> responses.AsyncResponsesWithStreamingResponse:
        from .resources.responses import AsyncResponsesWithStreamingResponse

        return AsyncResponsesWithStreamingResponse(self._client.responses)

    @cached_property
    def realtime(self) -> realtime.AsyncRealtimeWithStreamingResponse:
        from .resources.realtime import AsyncRealtimeWithStreamingResponse

        return AsyncRealtimeWithStreamingResponse(self._client.realtime)

    @cached_property
    def conversations(self) -> conversations.AsyncConversationsWithStreamingResponse:
        """Manage conversations and conversation items."""
        from .resources.conversations import AsyncConversationsWithStreamingResponse

        return AsyncConversationsWithStreamingResponse(self._client.conversations)

    @cached_property
    def evals(self) -> evals.AsyncEvalsWithStreamingResponse:
        """Manage and run evals in the OpenAI platform."""
        from .resources.evals import AsyncEvalsWithStreamingResponse

        return AsyncEvalsWithStreamingResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.AsyncContainersWithStreamingResponse:
        from .resources.containers import AsyncContainersWithStreamingResponse

        return AsyncContainersWithStreamingResponse(self._client.containers)

    @cached_property
    def skills(self) -> skills.AsyncSkillsWithStreamingResponse:
        from .resources.skills import AsyncSkillsWithStreamingResponse

        return AsyncSkillsWithStreamingResponse(self._client.skills)

    @cached_property
    def videos(self) -> videos.AsyncVideosWithStreamingResponse:
        from .resources.videos import AsyncVideosWithStreamingResponse

        return AsyncVideosWithStreamingResponse(self._client.videos)


Client = OpenAI

AsyncClient = AsyncOpenAI
