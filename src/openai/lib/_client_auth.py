"""Handwritten authentication hooks for the generated client facade."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, TypeVar, Callable, Awaitable
from importlib import import_module
from typing_extensions import Unpack

import httpx2

from ..auth import WorkloadIdentity, X509WorkloadIdentity
from .._types import (
    Headers,
    Timeout,
    NotGiven,
    HttpxSendArgs,
    not_given,
)
from .._models import SecurityOptions, FinalRequestOptions
from .._provider import _Provider, _ProviderRuntime
from .._base_client import DEFAULT_MAX_RETRIES
from .._data_residency import DataResidency

if TYPE_CHECKING:
    import openai._client as _sdk_client
else:
    _sdk_client = import_module(".._client", __package__)

_SyncClientT = TypeVar("_SyncClientT", bound="_sdk_client.OpenAI")

_AsyncClientT = TypeVar("_AsyncClientT", bound="_sdk_client.AsyncOpenAI")

__all__ = ["_has_header", "_has_omitted_header"]


def _has_header(headers: Headers, header: str) -> bool:
    header = header.lower()
    return any((key.lower() == header for key in headers))


def _has_omitted_header(headers: Headers, header: str) -> bool:
    header = header.lower()
    return any((key.lower() == header and isinstance(value, _sdk_client.Omit) for key, value in headers.items()))


def syncbase_url(self: _sdk_client.OpenAI) -> httpx2.URL:
    return self._base_url


def syncbase_url_set(self: _sdk_client.OpenAI, url: httpx2.URL | str) -> None:
    normalized_url = _sdk_client.normalize_httpx_url(url)
    if _sdk_client.is_x509_workload_identity(self.workload_identity):
        _sdk_client.validate_x509_api_url(normalized_url)
    self._base_url = self._enforce_trailing_slash(normalized_url)
    self._base_url_was_default = False
    self._data_residency = None


def sync__init__(
    _owner: type[_sdk_client.OpenAI],
    /,
    self: _sdk_client.OpenAI,
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
    base_url = _sdk_client.resolve_data_residency(
        data_residency, base_url, provider=provider, websocket_base_url=websocket_base_url
    )
    base_url = _sdk_client.x509_data_residency_base_url(base_url, data_residency, workload_identity)
    provider_runtime: _ProviderRuntime | None = None
    if provider is not None:
        provider_name = _sdk_client._provider_name(provider)
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
            formatted = ", ".join((f"`{name}`" for name in conflicts))
            raise _sdk_client.OpenAIError(
                f"`provider` cannot be combined with top-level {formatted}. Move provider authentication and routing options into `{provider_name}(...)`."
            )
        provider_runtime = _sdk_client._configure_provider(provider)
    self._provider = provider
    self._provider_runtime = provider_runtime
    if (
        api_key is not None
        and api_key != _sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
        and (workload_identity is not None)
    ):
        raise _sdk_client.OpenAIError("The `api_key` and `workload_identity` arguments are mutually exclusive")
    if _sdk_client.is_x509_workload_identity(workload_identity):
        workload_identity = workload_identity.copy()
    self.workload_identity = workload_identity if provider_runtime is None else None
    if provider_runtime is not None:
        self.api_key = ""
        self._api_key_provider = None
        self._workload_identity_auth = None
    elif workload_identity is not None:
        self.api_key = _sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
        self._api_key_provider = None
        self._workload_identity_auth = None
    else:
        if api_key is None:
            api_key = _sdk_client.os.environ.get("OPENAI_API_KEY")
        if callable(api_key):
            self.api_key = ""
            # Preserve callable-first handling, including callable str subclasses.
            self._api_key_provider = api_key  # ty: ignore[invalid-assignment]
        else:
            self.api_key = api_key or ""
            self._api_key_provider = None
        self._workload_identity_auth = None
    if admin_api_key is None and provider_runtime is None:
        admin_api_key = _sdk_client.os.environ.get("OPENAI_ADMIN_KEY")
    self.admin_api_key = admin_api_key if provider_runtime is None else None
    if (
        provider_runtime is None
        and _enforce_credentials
        and (not self.api_key)
        and (self._api_key_provider is None)
        and (workload_identity is None)
        and (self.admin_api_key is None)
    ):
        raise _sdk_client.OpenAIError(
            "Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable."
        )
    if organization is None and provider_runtime is None:
        organization = _sdk_client.os.environ.get("OPENAI_ORG_ID")
    self.organization = organization
    if project is None and provider_runtime is None:
        project = _sdk_client.os.environ.get("OPENAI_PROJECT_ID")
    self.project = project
    if webhook_secret is None:
        webhook_secret = _sdk_client.os.environ.get("OPENAI_WEBHOOK_SECRET")
    self.webhook_secret = webhook_secret
    self.websocket_base_url = websocket_base_url
    if _sdk_client.is_x509_workload_identity(workload_identity):
        x509_identity = workload_identity
        subject_token_identity = None
    elif workload_identity is None:
        x509_identity = None
        subject_token_identity = None
    elif "provider" in workload_identity:
        x509_identity = None
        subject_token_identity = workload_identity
    else:
        raise _sdk_client.OpenAIError(
            "Invalid `workload_identity` configuration: expected an X.509 or subject-token identity"
        )
    if provider_runtime is not None:
        base_url = provider_runtime.base_url
    elif base_url is None:
        base_url = _sdk_client.os.environ.get("OPENAI_BASE_URL")
    self._base_url_was_default = provider_runtime is None and base_url is None
    self._data_residency = data_residency
    if base_url is None:
        base_url = _sdk_client.MTLS_API_BASE_URL if x509_identity is not None else "https://api.openai.com/v1"
    if x509_identity is not None:
        _sdk_client.validate_x509_api_url(base_url)
    self._ambient_authorizations = frozenset()
    custom_headers_env = _sdk_client.os.environ.get("OPENAI_CUSTOM_HEADERS") if provider_runtime is None else None
    if custom_headers_env is not None:
        parsed: dict[str, str] = {}
        for line in custom_headers_env.split("\n"):
            colon = line.find(":")
            if colon >= 0:
                parsed[line[:colon].strip()] = line[colon + 1 :].strip()
        explicit_headers: Mapping[str, str] = default_headers if _sdk_client.is_mapping_t(default_headers) else {}
        explicit_authorization = any((name.lower() == "authorization" for name in explicit_headers))
        if explicit_authorization:
            parsed = {name: value for name, value in parsed.items() if name.lower() != "authorization"}
        elif x509_identity is None:
            self._ambient_authorizations = frozenset(
                (value for name, value in parsed.items() if name.lower() == "authorization")
            )
        default_headers = {**_sdk_client.x509_safe_environment_headers(parsed, x509_identity), **explicit_headers}
    super(_owner, self).__init__(
        version=_sdk_client.__version__,
        base_url=base_url,
        max_retries=max_retries,
        timeout=timeout,
        http_client=http_client,
        custom_headers=default_headers,
        custom_query=default_query,
        _strict_response_validation=_strict_response_validation,
    )
    if x509_identity is not None:
        self._workload_identity_auth = _sdk_client.SyncX509WorkloadIdentityAuth(
            workload_identity=x509_identity.copy(), http_client=self._client, max_retries=max_retries
        )
    elif subject_token_identity is not None:
        self._workload_identity_auth = _sdk_client.WorkloadIdentityAuth(
            workload_identity=subject_token_identity, _use_httpx2=_sdk_client.is_httpx2_sync_client(self._client)
        )
    self._default_stream_cls = _sdk_client.Stream


def sync_send_with_auth_retry(
    _owner: type[_sdk_client.OpenAI],
    /,
    self: _sdk_client.OpenAI,
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
        if isinstance(x509_auth, _sdk_client.SyncX509WorkloadIdentityAuth):
            if x509_auth.workload_identity != self.workload_identity:
                raise _sdk_client.OpenAIError("X.509 workload identity cannot be changed after client construction")
            _sdk_client.validate_x509_api_url(request.url, expected_origin=self.base_url)
            _sdk_client.validate_x509_request_authority(request)
            _sdk_client.validate_x509_api_credentials(request)
        if x509_auth._follow_redirects is not None:
            kwargs["follow_redirects"] = x509_auth._follow_redirects
        authorization = request.headers.get("Authorization")
        if authorization == f"Bearer {_sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}":
            used_access_token = (
                x509_auth.get_token_for_request(request)
                if isinstance(x509_auth, _sdk_client.SyncX509WorkloadIdentityAuth)
                else x509_auth.get_token()
            )
            request.headers["Authorization"] = f"Bearer {used_access_token}"
            request_is_replayable = x509_auth._can_retry_request(request)
    if isinstance(x509_auth, _sdk_client.SyncX509WorkloadIdentityAuth):
        response = x509_auth.send_api_request(
            request,
            expected_origin=self.base_url,
            expected_authorization=request.headers.get("Authorization"),
            stream=stream,
            **kwargs,
        )
    else:
        response = super(_owner, self)._send_request(request, stream=stream, **kwargs)
    if response.status_code != 401 or self._workload_identity_auth is None or used_access_token is None:
        return response
    self._workload_identity_auth.invalidate_token(used_access_token)
    if retried or not request_is_replayable:
        return response
    response.close()
    self._workload_identity_auth._prepare_retry_request(request)
    request.headers["Authorization"] = f"Bearer {_sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}"
    return self._send_with_auth_retry(request, stream=stream, retried=True, **kwargs)


def sync_send_request(
    self: _sdk_client.OpenAI, request: httpx2.Request, *, stream: bool, **kwargs: Unpack[HttpxSendArgs]
) -> httpx2.Response:
    response = self._send_with_auth_retry(request, stream=stream, **kwargs)
    if self._provider_runtime is not None and self._provider_runtime.normalize_response is not None:
        response = self._provider_runtime.normalize_response(response)
    return response


def sync_auth_headers(self: _sdk_client.OpenAI, security: SecurityOptions) -> dict[str, str]:
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


def sync_bearer_auth(self: _sdk_client.OpenAI) -> dict[str, str]:
    api_key = self.api_key
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def syncauth_headers(self: _sdk_client.OpenAI) -> dict[str, str]:
    if self._provider_runtime is not None:
        return {}
    api_key = self.api_key
    if not api_key or api_key == _sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def sync_validate_headers(self: _sdk_client.OpenAI, headers: Headers, custom_headers: Headers) -> None:
    if self._provider_runtime is not None:
        return
    if _sdk_client._has_header(headers, "Authorization") or _sdk_client._has_omitted_header(
        custom_headers, "Authorization"
    ):
        return
    raise TypeError(
        "Could not resolve authentication method. Expected either api_key or admin_api_key to be set. Or for the `Authorization` header to be explicitly omitted."
    )


def sync_prepare_options(
    _owner: type[_sdk_client.OpenAI], /, self: _sdk_client.OpenAI, options: FinalRequestOptions
) -> FinalRequestOptions:
    if options.url.startswith(("ws://", "wss://")) and (
        self._provider_runtime is not None or self.workload_identity is not None
    ):
        raise _sdk_client.OpenAIError("This authentication method is not supported by WebSocket connections")
    if self._provider_runtime is not None:
        if self._provider_runtime.transform_request is not None:
            options = self._provider_runtime.transform_request(options)
    elif self._api_key_provider is not None and options.security.get("bearer_auth", False):
        self._refresh_api_key()
    return super(_owner, self)._prepare_options(options)


def sync_prepare_request(self: _sdk_client.OpenAI, request: httpx2.Request) -> None:
    if self._provider_runtime is not None and self._provider_runtime.prepare_request is not None:
        self._provider_runtime.prepare_request(request)


def sync_custom_auth(
    _owner: type[_sdk_client.OpenAI], /, self: _sdk_client.OpenAI, security: SecurityOptions
) -> httpx2.Auth | None:
    if self._provider_runtime is not None or isinstance(
        self._workload_identity_auth, _sdk_client.SyncX509WorkloadIdentityAuth
    ):
        return _sdk_client.httpx2.Auth()
    return super(_owner, self)._custom_auth(security)


def sync_refresh_api_key(self: _sdk_client.OpenAI) -> str:
    if self._api_key_provider is not None:
        self.api_key = self._api_key_provider()
    return self.api_key


def synccopy(
    self: _SyncClientT,
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
) -> _SyncClientT:
    """
    Create a new client instance re-using the same options given to the current client with optional overriding.
    `data_residency` replaces the inherited HTTP and WebSocket endpoints, without changing this client.
    """
    if default_headers is not None and set_default_headers is not None:
        raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")
    if default_query is not None and set_default_query is not None:
        raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")
    provider_changed = not isinstance(provider, _sdk_client.NotGiven) and provider is not self._provider
    inherited_organization = None if provider_changed else self.organization
    inherited_project = None if provider_changed else self.project
    headers: Mapping[str, str] = {} if provider_changed else self._custom_headers
    if (
        _sdk_client.is_x509_workload_identity(workload_identity)
        and (not _sdk_client.is_x509_workload_identity(self.workload_identity))
        and self._ambient_authorizations
    ):
        headers = {
            name: value
            for name, value in headers.items()
            if name.lower() != "authorization" or value not in self._ambient_authorizations
        }
    if default_headers is not None:
        if any((name.lower() == "authorization" for name in default_headers)):
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
    next_provider = self._provider if isinstance(provider, _sdk_client.NotGiven) else provider
    explicit_base_url = base_url is not None and (not isinstance(base_url, _sdk_client.NotGiven))
    next_workload_identity = workload_identity if workload_identity is not None else self.workload_identity
    if api_key is not None and workload_identity is None:
        next_workload_identity = None
    current_x509 = _sdk_client.is_x509_workload_identity(self.workload_identity)
    next_x509 = _sdk_client.is_x509_workload_identity(next_workload_identity)
    mode_changed = current_x509 != next_x509
    effective_data_residency = data_residency
    if effective_data_residency is None and mode_changed and (not explicit_base_url):
        effective_data_residency = self._data_residency
    base_url = _sdk_client.resolve_data_residency(
        effective_data_residency,
        _sdk_client.not_given if base_url is None and data_residency is None else base_url,
        provider=next_provider,
        websocket_base_url=websocket_base_url,
    )
    base_url = _sdk_client.x509_data_residency_base_url(base_url, effective_data_residency, next_workload_identity)
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
        preserve_default_base_url = base_url is None and (not mode_changed) and self._base_url_was_default
        auth_options = {
            "api_key": api_key if workload_identity is not None else api_key or self._api_key_provider or self.api_key,
            "admin_api_key": admin_api_key or self.admin_api_key,
            "workload_identity": next_workload_identity,
            "base_url": base_url or inherited_base_url,
        }
    copied = self.__class__(
        organization=organization or inherited_organization,
        project=project or inherited_project,
        webhook_secret=webhook_secret or self.webhook_secret,
        websocket_base_url=None if data_residency is not None else websocket_base_url or self.websocket_base_url,
        timeout=self.timeout if isinstance(timeout, _sdk_client.NotGiven) else timeout,
        http_client=http_client,
        max_retries=max_retries if _sdk_client.is_given(max_retries) else self.max_retries,
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
        (name.lower() == "authorization" for name in overridden_authorizations)
    )
    if (
        self._ambient_authorizations
        and (not explicit_authorization_override)
        and any(
            (
                name.lower() == "authorization" and value in self._ambient_authorizations
                for name, value in copied._custom_headers.items()
            )
        )
    ):
        copied._ambient_authorizations = self._ambient_authorizations
    if data_residency is not None:
        copied._data_residency = data_residency
    elif not explicit_base_url and (not provider_changed):
        copied._data_residency = self._data_residency
    return copied


def asyncbase_url(self: _sdk_client.AsyncOpenAI) -> httpx2.URL:
    return self._base_url


def asyncbase_url_set(self: _sdk_client.AsyncOpenAI, url: httpx2.URL | str) -> None:
    normalized_url = _sdk_client.normalize_httpx_url(url)
    if _sdk_client.is_x509_workload_identity(self.workload_identity):
        _sdk_client.validate_x509_api_url(normalized_url)
    self._base_url = self._enforce_trailing_slash(normalized_url)
    self._base_url_was_default = False
    self._data_residency = None


def async__init__(
    _owner: type[_sdk_client.AsyncOpenAI],
    /,
    self: _sdk_client.AsyncOpenAI,
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
    base_url = _sdk_client.resolve_data_residency(
        data_residency, base_url, provider=provider, websocket_base_url=websocket_base_url
    )
    base_url = _sdk_client.x509_data_residency_base_url(base_url, data_residency, workload_identity)
    provider_runtime: _ProviderRuntime | None = None
    if provider is not None:
        provider_name = _sdk_client._provider_name(provider)
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
            formatted = ", ".join((f"`{name}`" for name in conflicts))
            raise _sdk_client.OpenAIError(
                f"`provider` cannot be combined with top-level {formatted}. Move provider authentication and routing options into `{provider_name}(...)`."
            )
        provider_runtime = _sdk_client._configure_provider(provider)
    self._provider = provider
    self._provider_runtime = provider_runtime
    if (
        api_key is not None
        and api_key != _sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
        and (workload_identity is not None)
    ):
        raise _sdk_client.OpenAIError("The `api_key` and `workload_identity` arguments are mutually exclusive")
    if _sdk_client.is_x509_workload_identity(workload_identity):
        workload_identity = workload_identity.copy()
    self.workload_identity = workload_identity if provider_runtime is None else None
    if provider_runtime is not None:
        self.api_key = ""
        self._api_key_provider = None
        self._workload_identity_auth = None
    elif workload_identity is not None:
        self.api_key = _sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
        self._api_key_provider = None
        self._workload_identity_auth = None
    else:
        if api_key is None:
            api_key = _sdk_client.os.environ.get("OPENAI_API_KEY")
        if callable(api_key):
            self.api_key = ""
            # Preserve callable-first handling, including callable str subclasses.
            self._api_key_provider = api_key  # ty: ignore[invalid-assignment]
        else:
            self.api_key = api_key or ""
            self._api_key_provider = None
        self._workload_identity_auth = None
    if admin_api_key is None and provider_runtime is None:
        admin_api_key = _sdk_client.os.environ.get("OPENAI_ADMIN_KEY")
    self.admin_api_key = admin_api_key if provider_runtime is None else None
    if (
        provider_runtime is None
        and _enforce_credentials
        and (not self.api_key)
        and (self._api_key_provider is None)
        and (workload_identity is None)
        and (self.admin_api_key is None)
    ):
        raise _sdk_client.OpenAIError(
            "Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable."
        )
    if organization is None and provider_runtime is None:
        organization = _sdk_client.os.environ.get("OPENAI_ORG_ID")
    self.organization = organization
    if project is None and provider_runtime is None:
        project = _sdk_client.os.environ.get("OPENAI_PROJECT_ID")
    self.project = project
    if webhook_secret is None:
        webhook_secret = _sdk_client.os.environ.get("OPENAI_WEBHOOK_SECRET")
    self.webhook_secret = webhook_secret
    self.websocket_base_url = websocket_base_url
    if _sdk_client.is_x509_workload_identity(workload_identity):
        x509_identity = workload_identity
        subject_token_identity = None
    elif workload_identity is None:
        x509_identity = None
        subject_token_identity = None
    elif "provider" in workload_identity:
        x509_identity = None
        subject_token_identity = workload_identity
    else:
        raise _sdk_client.OpenAIError(
            "Invalid `workload_identity` configuration: expected an X.509 or subject-token identity"
        )
    if provider_runtime is not None:
        base_url = provider_runtime.base_url
    elif base_url is None:
        base_url = _sdk_client.os.environ.get("OPENAI_BASE_URL")
    self._base_url_was_default = provider_runtime is None and base_url is None
    self._data_residency = data_residency
    if base_url is None:
        base_url = _sdk_client.MTLS_API_BASE_URL if x509_identity is not None else "https://api.openai.com/v1"
    if x509_identity is not None:
        _sdk_client.validate_x509_api_url(base_url)
    self._ambient_authorizations = frozenset()
    custom_headers_env = _sdk_client.os.environ.get("OPENAI_CUSTOM_HEADERS") if provider_runtime is None else None
    if custom_headers_env is not None:
        parsed: dict[str, str] = {}
        for line in custom_headers_env.split("\n"):
            colon = line.find(":")
            if colon >= 0:
                parsed[line[:colon].strip()] = line[colon + 1 :].strip()
        explicit_headers: Mapping[str, str] = default_headers if _sdk_client.is_mapping_t(default_headers) else {}
        explicit_authorization = any((name.lower() == "authorization" for name in explicit_headers))
        if explicit_authorization:
            parsed = {name: value for name, value in parsed.items() if name.lower() != "authorization"}
        elif x509_identity is None:
            self._ambient_authorizations = frozenset(
                (value for name, value in parsed.items() if name.lower() == "authorization")
            )
        default_headers = {**_sdk_client.x509_safe_environment_headers(parsed, x509_identity), **explicit_headers}
    super(_owner, self).__init__(
        version=_sdk_client.__version__,
        base_url=base_url,
        max_retries=max_retries,
        timeout=timeout,
        http_client=http_client,
        custom_headers=default_headers,
        custom_query=default_query,
        _strict_response_validation=_strict_response_validation,
    )
    if x509_identity is not None:
        self._workload_identity_auth = _sdk_client.AsyncX509WorkloadIdentityAuth(
            workload_identity=x509_identity.copy(), http_client=self._client, max_retries=max_retries
        )
    elif subject_token_identity is not None:
        self._workload_identity_auth = _sdk_client.WorkloadIdentityAuth(
            workload_identity=subject_token_identity, _use_httpx2=_sdk_client.is_httpx2_async_client(self._client)
        )
    self._default_stream_cls = _sdk_client.AsyncStream


async def async_send_with_auth_retry(
    _owner: type[_sdk_client.AsyncOpenAI],
    /,
    self: _sdk_client.AsyncOpenAI,
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
        if isinstance(x509_auth, _sdk_client.AsyncX509WorkloadIdentityAuth):
            if x509_auth.workload_identity != self.workload_identity:
                raise _sdk_client.OpenAIError("X.509 workload identity cannot be changed after client construction")
            _sdk_client.validate_x509_api_url(request.url, expected_origin=self.base_url)
            _sdk_client.validate_x509_request_authority(request)
            _sdk_client.validate_x509_api_credentials(request)
        if x509_auth._follow_redirects is not None:
            kwargs["follow_redirects"] = x509_auth._follow_redirects
        authorization = request.headers.get("Authorization")
        if authorization == f"Bearer {_sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}":
            used_access_token = (
                await x509_auth.get_token_for_request(request)
                if isinstance(x509_auth, _sdk_client.AsyncX509WorkloadIdentityAuth)
                else await x509_auth.get_token_async()
            )
            request.headers["Authorization"] = f"Bearer {used_access_token}"
            request_is_replayable = x509_auth._can_retry_request(request)
    if isinstance(x509_auth, _sdk_client.AsyncX509WorkloadIdentityAuth):
        response = await x509_auth.send_api_request(
            request,
            expected_origin=self.base_url,
            expected_authorization=request.headers.get("Authorization"),
            stream=stream,
            **kwargs,
        )
    else:
        response = await super(_owner, self)._send_request(request, stream=stream, **kwargs)
    if response.status_code != 401 or self._workload_identity_auth is None or used_access_token is None:
        return response
    self._workload_identity_auth.invalidate_token(used_access_token)
    if retried or not request_is_replayable:
        return response
    await response.aclose()
    self._workload_identity_auth._prepare_retry_request(request)
    request.headers["Authorization"] = f"Bearer {_sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}"
    return await self._send_with_auth_retry(request, stream=stream, retried=True, **kwargs)


async def async_send_request(
    self: _sdk_client.AsyncOpenAI, request: httpx2.Request, *, stream: bool, **kwargs: Unpack[HttpxSendArgs]
) -> httpx2.Response:
    response = await self._send_with_auth_retry(request, stream=stream, **kwargs)
    if self._provider_runtime is not None:
        if self._provider_runtime.normalize_async_response is not None:
            response = await self._provider_runtime.normalize_async_response(response)
        elif self._provider_runtime.normalize_response is not None:
            response = self._provider_runtime.normalize_response(response)
    return response


def async_auth_headers(self: _sdk_client.AsyncOpenAI, security: SecurityOptions) -> dict[str, str]:
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


def async_bearer_auth(self: _sdk_client.AsyncOpenAI) -> dict[str, str]:
    api_key = self.api_key
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def asyncauth_headers(self: _sdk_client.AsyncOpenAI) -> dict[str, str]:
    if self._provider_runtime is not None:
        return {}
    api_key = self.api_key
    if not api_key or api_key == _sdk_client.WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def async_validate_headers(self: _sdk_client.AsyncOpenAI, headers: Headers, custom_headers: Headers) -> None:
    if self._provider_runtime is not None:
        return
    if _sdk_client._has_header(headers, "Authorization") or _sdk_client._has_omitted_header(
        custom_headers, "Authorization"
    ):
        return
    raise TypeError(
        "Could not resolve authentication method. Expected either api_key or admin_api_key to be set. Or for the `Authorization` header to be explicitly omitted."
    )


async def async_prepare_options(
    _owner: type[_sdk_client.AsyncOpenAI], /, self: _sdk_client.AsyncOpenAI, options: FinalRequestOptions
) -> FinalRequestOptions:
    if options.url.startswith(("ws://", "wss://")) and (
        self._provider_runtime is not None or self.workload_identity is not None
    ):
        raise _sdk_client.OpenAIError("This authentication method is not supported by WebSocket connections")
    if self._provider_runtime is not None:
        if self._provider_runtime.transform_async_request is not None:
            options = await self._provider_runtime.transform_async_request(options)
        elif self._provider_runtime.transform_request is not None:
            options = self._provider_runtime.transform_request(options)
    elif self._api_key_provider is not None and options.security.get("bearer_auth", False):
        await self._refresh_api_key()
    return await super(_owner, self)._prepare_options(options)


async def async_prepare_request(self: _sdk_client.AsyncOpenAI, request: httpx2.Request) -> None:
    if self._provider_runtime is None:
        return
    if self._provider_runtime.prepare_async_request is not None:
        await self._provider_runtime.prepare_async_request(request)
    elif self._provider_runtime.prepare_request is not None:
        self._provider_runtime.prepare_request(request)


def asynccustom_auth(_owner: type[_sdk_client.AsyncOpenAI], /, self: _sdk_client.AsyncOpenAI) -> httpx2.Auth | None:
    if self._provider_runtime is not None or isinstance(
        self._workload_identity_auth, _sdk_client.AsyncX509WorkloadIdentityAuth
    ):
        return _sdk_client.httpx2.Auth()
    return super(_owner, self).custom_auth


async def async_refresh_api_key(self: _sdk_client.AsyncOpenAI) -> str:
    if self._api_key_provider is not None:
        self.api_key = await self._api_key_provider()
    return self.api_key


def asynccopy(
    self: _AsyncClientT,
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
) -> _AsyncClientT:
    """
    Create a new client instance re-using the same options given to the current client with optional overriding.
    `data_residency` replaces the inherited HTTP and WebSocket endpoints, without changing this client.
    """
    if default_headers is not None and set_default_headers is not None:
        raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")
    if default_query is not None and set_default_query is not None:
        raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")
    provider_changed = not isinstance(provider, _sdk_client.NotGiven) and provider is not self._provider
    inherited_organization = None if provider_changed else self.organization
    inherited_project = None if provider_changed else self.project
    headers: Mapping[str, str] = {} if provider_changed else self._custom_headers
    if (
        _sdk_client.is_x509_workload_identity(workload_identity)
        and (not _sdk_client.is_x509_workload_identity(self.workload_identity))
        and self._ambient_authorizations
    ):
        headers = {
            name: value
            for name, value in headers.items()
            if name.lower() != "authorization" or value not in self._ambient_authorizations
        }
    if default_headers is not None:
        if any((name.lower() == "authorization" for name in default_headers)):
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
    next_provider = self._provider if isinstance(provider, _sdk_client.NotGiven) else provider
    explicit_base_url = base_url is not None and (not isinstance(base_url, _sdk_client.NotGiven))
    next_workload_identity = workload_identity if workload_identity is not None else self.workload_identity
    if api_key is not None and workload_identity is None:
        next_workload_identity = None
    current_x509 = _sdk_client.is_x509_workload_identity(self.workload_identity)
    next_x509 = _sdk_client.is_x509_workload_identity(next_workload_identity)
    mode_changed = current_x509 != next_x509
    effective_data_residency = data_residency
    if effective_data_residency is None and mode_changed and (not explicit_base_url):
        effective_data_residency = self._data_residency
    base_url = _sdk_client.resolve_data_residency(
        effective_data_residency,
        _sdk_client.not_given if base_url is None and data_residency is None else base_url,
        provider=next_provider,
        websocket_base_url=websocket_base_url,
    )
    base_url = _sdk_client.x509_data_residency_base_url(base_url, effective_data_residency, next_workload_identity)
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
        preserve_default_base_url = base_url is None and (not mode_changed) and self._base_url_was_default
        auth_options = {
            "api_key": api_key if workload_identity is not None else api_key or self._api_key_provider or self.api_key,
            "admin_api_key": admin_api_key or self.admin_api_key,
            "workload_identity": next_workload_identity,
            "base_url": base_url or inherited_base_url,
        }
    copied = self.__class__(
        organization=organization or inherited_organization,
        project=project or inherited_project,
        webhook_secret=webhook_secret or self.webhook_secret,
        websocket_base_url=None if data_residency is not None else websocket_base_url or self.websocket_base_url,
        timeout=self.timeout if isinstance(timeout, _sdk_client.NotGiven) else timeout,
        http_client=http_client,
        max_retries=max_retries if _sdk_client.is_given(max_retries) else self.max_retries,
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
        (name.lower() == "authorization" for name in overridden_authorizations)
    )
    if (
        self._ambient_authorizations
        and (not explicit_authorization_override)
        and any(
            (
                name.lower() == "authorization" and value in self._ambient_authorizations
                for name, value in copied._custom_headers.items()
            )
        )
    ):
        copied._ambient_authorizations = self._ambient_authorizations
    if data_residency is not None:
        copied._data_residency = data_residency
    elif not explicit_base_url and (not provider_changed):
        copied._data_residency = self._data_residency
    return copied
