from __future__ import annotations

import re
import math
import time
import threading
import email.utils
from typing import Any, Iterator, NoReturn, cast
from weakref import ReferenceType, ref
from contextlib import contextmanager
from contextvars import ContextVar
from typing_extensions import TypeIs, override

import anyio
import httpx2

from .._utils import is_dict
from .._httpx2 import timeout_exceptions, normalize_httpx_url, _loaded_legacy_httpx
from ._workload import (
    TOKEN_EXCHANGE_GRANT_TYPE,
    WorkloadIdentity,
    X509WorkloadIdentity,
    _WorkloadIdentityAuth,
)
from .._constants import MAX_RETRY_DELAY, INITIAL_RETRY_DELAY, MAX_RETRY_AFTER_DELAY
from .._exceptions import OAuthError, OpenAIError, APITimeoutError, APIConnectionError

MTLS_API_BASE_URL = "https://mtls.api.openai.com/v1"
_X509_TOKEN_EXCHANGE_URL = "https://mtls.auth.openai.com/oauth/token"
_X509_SUBJECT_TOKEN_TYPE = "urn:openai:params:oauth:token-type:x509"
_MAX_EXCHANGE_RETRIES = 2
_REPLAY_POSITION_EXTENSION = "openai_x509_replay_position"
_REPLAY_FILE_POSITIONS_EXTENSION = "openai_x509_replay_file_positions"
_ALLOWED_IDENTITY_FIELDS = {"type", "identity_provider_id", "service_account_id", "refresh_buffer_seconds"}
_BEARER_ACCESS_TOKEN = re.compile(r"[A-Za-z0-9._~+/-]+=*")
_MTLS_REGIONAL_BASE_URLS = {
    "global": MTLS_API_BASE_URL,
    "us": "https://mtls-us.api.openai.com/v1",
    "eu": "https://mtls-eu.api.openai.com/v1",
}
_OPENAI_MTLS_HOSTS = {httpx2.URL(url).host for url in _MTLS_REGIONAL_BASE_URLS.values()}
_EXCHANGE_REQUEST_TIMEOUT: ContextVar[dict[str, float | None] | None] = ContextVar(
    "openai_x509_exchange_request_timeout", default=None
)
_API_TRANSPORT_SCOPE: ContextVar[tuple[httpx2.Request, httpx2.URL, str | None] | None] = ContextVar(
    "openai_x509_api_transport_scope", default=None
)
_API_TRANSPORT_SCOPE_EXTENSION = "openai_x509_api_transport_scope"
_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION = "openai_x509_unprotected_transport_scope"
_ACTIVE_API_TRANSPORT_SCOPES: dict[object, tuple[httpx2.Request, httpx2.URL, str | None]] = {}
_ACTIVE_UNPROTECTED_TRANSPORT_SCOPES: dict[object, tuple[httpx2.Request, httpx2.URL, str | None]] = {}
_ACTIVE_API_TRANSPORT_SCOPES_LOCK = threading.RLock()
_UNPROTECTED_TRANSPORT_SCOPE: ContextVar[object | None] = ContextVar(
    "openai_x509_unprotected_transport_scope", default=None
)


@contextmanager
def non_x509_request_scope(request: httpx2.Request) -> Iterator[None]:
    marker = object()
    had_previous_marker = _UNPROTECTED_TRANSPORT_SCOPE_EXTENSION in request.extensions
    previous_marker = request.extensions.get(_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION)
    request.extensions[_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION] = marker
    with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
        _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES[marker] = (
            request,
            request.url,
            request.headers.get("Authorization"),
        )
    protected_scope = _API_TRANSPORT_SCOPE.set(None)
    unprotected_scope = _UNPROTECTED_TRANSPORT_SCOPE.set(marker)
    try:
        yield
    finally:
        _UNPROTECTED_TRANSPORT_SCOPE.reset(unprotected_scope)
        _API_TRANSPORT_SCOPE.reset(protected_scope)
        with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
            _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES.pop(marker, None)
        if had_previous_marker:
            request.extensions[_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION] = previous_marker
        else:
            request.extensions.pop(_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION, None)


def _is_unprotected_transport_request(request: httpx2.Request) -> bool:
    marker = request.extensions.get(_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION)
    contextual_marker = _UNPROTECTED_TRANSPORT_SCOPE.get()
    with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
        if type(marker) is object and marker in _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES:
            return True
        return contextual_marker is not None and contextual_marker in _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES


def _request_transport_scope(request: httpx2.Request) -> tuple[httpx2.Request, httpx2.URL, str | None] | None:
    marker = request.extensions.get(_API_TRANSPORT_SCOPE_EXTENSION)
    if type(marker) is object:
        with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
            marked_scope = _ACTIVE_API_TRANSPORT_SCOPES.get(marker)
        if marked_scope is not None:
            return marked_scope

    if _is_unprotected_transport_request(request):
        return None

    return _API_TRANSPORT_SCOPE.get()


class _TransientTokenExchangeError(Exception):
    def __init__(self, error: OpenAIError) -> None:
        self.error = error


def validate_x509_api_url(url: httpx2.URL | str, *, expected_origin: httpx2.URL | None = None) -> None:
    normalized_url = normalize_httpx_url(url)
    if normalized_url.scheme != "https" or not normalized_url.host:
        raise OpenAIError("X.509 workload identity requires an absolute HTTPS API URL")

    if normalized_url.username or normalized_url.password:
        raise OpenAIError("X.509 workload identity API URLs cannot contain user credentials")

    if expected_origin is not None and (normalized_url.host, normalized_url.port) != (
        expected_origin.host,
        expected_origin.port,
    ):
        raise OpenAIError("X.509 workload identity requests must use the configured API origin")


def validate_x509_api_credentials(request: httpx2.Request) -> None:
    if any(
        header.lower().replace("_", "-") in ("api-key", "x-api-key", "proxy-authorization")
        for header in request.headers
    ):
        raise OpenAIError("X.509 workload identity requests cannot include API-key or proxy credentials")


def validate_x509_request_authority(request: httpx2.Request) -> None:
    host_headers = request.headers.get_list("host")
    if (
        len(host_headers) != 1
        or any(delimiter in host_headers[0] for delimiter in "/?#@\\")
        or any(header.startswith(":") for header in request.headers)
    ):
        raise OpenAIError("X.509 workload identity requests require exactly one valid Host authority")

    try:
        host_url = httpx2.URL(f"https://{host_headers[0]}")
    except httpx2.InvalidURL as error:
        raise OpenAIError("X.509 workload identity requests require a valid Host authority") from error

    if (
        host_url.username
        or host_url.password
        or host_url.path != "/"
        or host_url.query
        or host_url.fragment
        or (host_url.host, host_url.port) != (request.url.host, request.url.port)
    ):
        raise OpenAIError("X.509 workload identity Host authority must match the request URL")


def _validate_transport_request(
    request: httpx2.Request,
    *,
    expected_origin: httpx2.URL,
    expected_authorization: str | None,
    token_exchange: bool,
) -> None:
    validate_x509_api_url(request.url, expected_origin=expected_origin)
    validate_x509_request_authority(request)

    target = request.extensions.get("target")
    if target is not None and target != request.url.raw_path:
        raise OpenAIError("X.509 workload identity request target must match the request URL")

    sni_hostname = request.extensions.get("sni_hostname")
    if request.url.host in _OPENAI_MTLS_HOSTS and sni_hostname is not None:
        if not isinstance(sni_hostname, str) or sni_hostname.lower() != request.url.host.lower():
            raise OpenAIError("X.509 workload identity TLS hostname must match the OpenAI mTLS origin")

    if token_exchange:
        if str(request.url) != _X509_TOKEN_EXCHANGE_URL:
            raise OpenAIError("X.509 token exchange requests must use the pinned authentication URL")
        if any(
            header.lower().replace("_", "-")
            in ("authorization", "proxy-authorization", "cookie", "x-api-key", "api-key")
            for header in request.headers
        ):
            raise OpenAIError("X.509 token exchange requests cannot include API credentials")
    else:
        validate_x509_api_credentials(request)
        if request.headers.get("Authorization") != expected_authorization:
            raise OpenAIError("X.509 workload identity authorization cannot be changed by HTTP request hooks")


class _SyncX509ForwardingTransport(httpx2.BaseTransport):
    def __init__(
        self,
        *,
        http_client: httpx2.Client,
        expected_origin: httpx2.URL,
        expected_authorization: str | None,
        token_exchange: bool,
    ) -> None:
        self._http_client = http_client
        self._expected_origin = expected_origin
        self._expected_authorization = expected_authorization
        self._token_exchange = token_exchange

    @override
    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        _validate_transport_request(
            request,
            expected_origin=self._expected_origin,
            expected_authorization=self._expected_authorization,
            token_exchange=self._token_exchange,
        )
        if self._http_client.is_closed:
            raise RuntimeError("Cannot send a request, as the client has been closed.")
        transport = self._http_client._transport_for_url(request.url)
        if self._token_exchange:
            with non_x509_request_scope(request):
                return transport.handle_request(request)
        return transport.handle_request(request)

    @override
    def close(self) -> None:
        # The caller owns the selected connection pool and proxy transports.
        return None


class _AsyncX509ForwardingTransport(httpx2.AsyncBaseTransport):
    def __init__(
        self,
        *,
        http_client: httpx2.AsyncClient,
        expected_origin: httpx2.URL,
        expected_authorization: str | None,
        token_exchange: bool,
    ) -> None:
        self._http_client = http_client
        self._expected_origin = expected_origin
        self._expected_authorization = expected_authorization
        self._token_exchange = token_exchange

    @override
    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        _validate_transport_request(
            request,
            expected_origin=self._expected_origin,
            expected_authorization=self._expected_authorization,
            token_exchange=self._token_exchange,
        )
        if self._http_client.is_closed:
            raise RuntimeError("Cannot send a request, as the client has been closed.")
        transport = self._http_client._transport_for_url(request.url)
        if self._token_exchange:
            with non_x509_request_scope(request):
                return await transport.handle_async_request(request)
        return await transport.handle_async_request(request)

    @override
    async def aclose(self) -> None:
        # The caller owns the selected connection pool and proxy transports.
        return None


class _SyncX509ScopedTransport(httpx2.BaseTransport):
    def __init__(self, transport: httpx2.BaseTransport, owner: _X509ClientTransportScope) -> None:
        self._transport = transport
        self._owner = owner

    @override
    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        scope = self._owner.request_scope(request)
        if scope is not None:
            _validate_transport_request(
                request,
                expected_origin=scope[1],
                expected_authorization=scope[2],
                token_exchange=False,
            )
        return self._transport.handle_request(request)

    @override
    def close(self) -> None:
        self._transport.close()


class _AsyncX509ScopedTransport(httpx2.AsyncBaseTransport):
    def __init__(self, transport: httpx2.AsyncBaseTransport, owner: _X509ClientTransportScope) -> None:
        self._transport = transport
        self._owner = owner

    @override
    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        scope = self._owner.request_scope(request)
        if scope is not None:
            _validate_transport_request(
                request,
                expected_origin=scope[1],
                expected_authorization=scope[2],
                token_exchange=False,
            )
        return await self._transport.handle_async_request(request)

    @override
    async def aclose(self) -> None:
        await self._transport.aclose()


class _FinalizingRequestHooks(list[Any]):
    def __init__(self, hooks: list[Any], finalizer: Any) -> None:
        super().__init__(hooks)
        self._finalizer = finalizer

    @override
    def __iter__(self) -> Iterator[Any]:
        finalizer = self._finalizer
        yield finalizer
        index = 0
        while index < len(self):
            hook = self[index]
            index += 1
            yield hook
        yield finalizer


class _X509ClientTransportScope:
    def __init__(self, http_client: httpx2.Client | httpx2.AsyncClient, *, is_async: bool) -> None:
        self._http_client_ref = ref(http_client)
        self._is_async = is_async
        self._lock = threading.RLock()
        self._active_requests = 0
        self._request_scopes: dict[object, tuple[httpx2.Request, httpx2.URL, str | None]] = {}
        self._bound_requests: dict[int, tuple[httpx2.Request, object]] = {}
        self._scope_request_bindings: dict[object, set[int]] = {}
        self._original_transport: Any = None
        self._original_mounts: dict[Any, Any] = {}
        self._original_request_hooks: list[Any] = []

    def _wrap(self, transport: Any) -> Any:
        if self._is_async:
            return _AsyncX509ScopedTransport(transport, self)
        return _SyncX509ScopedTransport(transport, self)

    def request_scope(self, request: httpx2.Request) -> tuple[httpx2.Request, httpx2.URL, str | None] | None:
        with self._lock:
            bound_request = self._bound_requests.get(id(request))
            if bound_request is not None and bound_request[0] is request:
                bound_scope = self._request_scopes.get(bound_request[1])
                if bound_scope is not None:
                    return bound_scope

        scope = _request_transport_scope(request)
        if scope is not None:
            marker = request.extensions.get(_API_TRANSPORT_SCOPE_EXTENSION)
            with self._lock:
                if type(marker) is object and marker in self._request_scopes:
                    self._bind_request(request, marker)
            return scope
        if _is_unprotected_transport_request(request):
            return None

        with self._lock:
            if not self._request_scopes:
                return None
            same_origin = [
                (marker, active_scope)
                for marker, active_scope in self._request_scopes.items()
                if (request.url.host, request.url.port) == (active_scope[1].host, active_scope[1].port)
            ]
            candidates = same_origin if same_origin else list(self._request_scopes.items())
            marker, active_scope = next(
                (
                    (active_marker, candidate)
                    for active_marker, candidate in candidates
                    if request.headers.get("Authorization") == candidate[2]
                ),
                candidates[0],
            )
            self._bind_request(request, marker)
            return active_scope

    def _bind_request(self, request: httpx2.Request, marker: object) -> None:
        identifier = id(request)
        self._bound_requests[identifier] = (request, marker)
        self._scope_request_bindings.setdefault(marker, set()).add(identifier)

    def _validate_sync_request(self, request: httpx2.Request) -> None:
        scope = self.request_scope(request)
        if scope is not None:
            _validate_transport_request(
                request,
                expected_origin=scope[1],
                expected_authorization=scope[2],
                token_exchange=False,
            )

    async def _validate_async_request(self, request: httpx2.Request) -> None:
        self._validate_sync_request(request)

    @contextmanager
    def activate(
        self, request: httpx2.Request, expected_origin: httpx2.URL, expected_authorization: str | None
    ) -> Iterator[None]:
        http_client = self._http_client_ref()
        if http_client is None:
            raise RuntimeError("Cannot send a request after the HTTP client has been released.")
        with self._lock:
            if self._active_requests == 0:
                self._original_transport = http_client._transport
                self._original_mounts = http_client._mounts
                http_client._transport = self._wrap(self._original_transport)
                http_client._mounts = {
                    pattern: self._wrap(transport) if transport is not None else None
                    for pattern, transport in self._original_mounts.items()
                }
                self._original_request_hooks = http_client.event_hooks["request"]
                validator = self._validate_async_request if self._is_async else self._validate_sync_request
                http_client.event_hooks["request"] = _FinalizingRequestHooks(self._original_request_hooks, validator)
            self._active_requests += 1

        marker = object()
        had_previous_marker = _API_TRANSPORT_SCOPE_EXTENSION in request.extensions
        previous_marker = request.extensions.get(_API_TRANSPORT_SCOPE_EXTENSION)
        request.extensions[_API_TRANSPORT_SCOPE_EXTENSION] = marker
        request_scope = (request, expected_origin, expected_authorization)
        with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
            _ACTIVE_API_TRANSPORT_SCOPES[marker] = request_scope
        with self._lock:
            self._request_scopes[marker] = request_scope
        scope = _API_TRANSPORT_SCOPE.set(request_scope)
        unprotected_scope = _UNPROTECTED_TRANSPORT_SCOPE.set(None)
        try:
            yield
        finally:
            with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
                _ACTIVE_API_TRANSPORT_SCOPES.pop(marker, None)
            if had_previous_marker:
                request.extensions[_API_TRANSPORT_SCOPE_EXTENSION] = previous_marker
            else:
                request.extensions.pop(_API_TRANSPORT_SCOPE_EXTENSION, None)
            _UNPROTECTED_TRANSPORT_SCOPE.reset(unprotected_scope)
            _API_TRANSPORT_SCOPE.reset(scope)
            with self._lock:
                for identifier in self._scope_request_bindings.pop(marker, set()):
                    self._bound_requests.pop(identifier, None)
                self._request_scopes.pop(marker, None)
                self._active_requests -= 1
                if self._active_requests == 0:
                    http_client._transport = self._original_transport
                    http_client._mounts = self._original_mounts
                    scoped_hooks = http_client.event_hooks["request"]
                    self._original_request_hooks[:] = (
                        scoped_hooks.copy() if isinstance(scoped_hooks, _FinalizingRequestHooks) else list(scoped_hooks)
                    )
                    http_client.event_hooks["request"] = self._original_request_hooks
                    self._original_transport = None
                    self._original_mounts = {}
                    self._original_request_hooks = []


_TRANSPORT_SCOPES: dict[int, tuple[ReferenceType[Any], _X509ClientTransportScope]] = {}
_TRANSPORT_SCOPES_LOCK = threading.RLock()


def _release_transport_scope(client_id: int, reference: ReferenceType[Any]) -> None:
    with _TRANSPORT_SCOPES_LOCK:
        entry = _TRANSPORT_SCOPES.get(client_id)
        if entry is not None and entry[0] is reference:
            _TRANSPORT_SCOPES.pop(client_id, None)


def _client_transport_scope(
    http_client: httpx2.Client | httpx2.AsyncClient, *, is_async: bool
) -> _X509ClientTransportScope:
    client_id = id(http_client)
    with _TRANSPORT_SCOPES_LOCK:
        existing = _TRANSPORT_SCOPES.get(client_id)
        if existing is not None and existing[0]() is http_client:
            return existing[1]

        def release(reference: ReferenceType[Any]) -> None:
            _release_transport_scope(client_id, reference)

        scope = _X509ClientTransportScope(http_client, is_async=is_async)
        _TRANSPORT_SCOPES[client_id] = (ref(http_client, release), scope)
        return scope


def _scoped_sync_client(
    http_client: httpx2.Client,
    *,
    expected_origin: httpx2.URL,
    expected_authorization: str | None = None,
    token_exchange: bool = False,
) -> httpx2.Client:
    transport = _SyncX509ForwardingTransport(
        http_client=http_client,
        expected_origin=expected_origin,
        expected_authorization=expected_authorization,
        token_exchange=token_exchange,
    )
    legacy_httpx = _loaded_legacy_httpx()
    client_type = httpx2.Client
    if legacy_httpx is not None and not isinstance(cast(object, http_client), httpx2.Client):
        client_type = legacy_httpx.Client
    return client_type(transport=transport, timeout=http_client.timeout, event_hooks=None, trust_env=False)


def _scoped_async_client(
    http_client: httpx2.AsyncClient,
    *,
    expected_origin: httpx2.URL,
    expected_authorization: str | None = None,
    token_exchange: bool = False,
) -> httpx2.AsyncClient:
    transport = _AsyncX509ForwardingTransport(
        http_client=http_client,
        expected_origin=expected_origin,
        expected_authorization=expected_authorization,
        token_exchange=token_exchange,
    )
    legacy_httpx = _loaded_legacy_httpx()
    client_type = httpx2.AsyncClient
    if legacy_httpx is not None and not isinstance(cast(object, http_client), httpx2.AsyncClient):
        client_type = legacy_httpx.AsyncClient
    return client_type(transport=transport, timeout=http_client.timeout, event_hooks=None, trust_env=False)


def _as_finite_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        value = float(value)
    except OverflowError:
        return None
    return value if math.isfinite(value) else None


def is_x509_workload_identity(
    identity: WorkloadIdentity | X509WorkloadIdentity | None,
) -> TypeIs[X509WorkloadIdentity]:
    return identity is not None and identity.get("type") == "x509"


def x509_data_residency_base_url(
    base_url: httpx2.URL | str | None,
    data_residency: str | None,
    workload_identity: WorkloadIdentity | X509WorkloadIdentity | None,
) -> httpx2.URL | str | None:
    if data_residency is None or not is_x509_workload_identity(workload_identity):
        return base_url
    if data_residency not in _MTLS_REGIONAL_BASE_URLS:
        raise OpenAIError("X.509 workload identity requires a supported regional mTLS endpoint")
    return _MTLS_REGIONAL_BASE_URLS[data_residency]


def x509_safe_environment_headers(
    headers: dict[str, str], workload_identity: X509WorkloadIdentity | None
) -> dict[str, str]:
    if workload_identity is None:
        return headers
    return {name: value for name, value in headers.items() if name.lower() != "authorization"}


def _validate_identity(identity: X509WorkloadIdentity) -> None:
    if "provider" in identity or "client_id" in identity:
        raise OpenAIError("X.509 workload identity does not accept a subject-token provider or client ID")

    if set(identity) - _ALLOWED_IDENTITY_FIELDS:
        raise OpenAIError("X.509 workload identity accepts only identity IDs and an optional refresh buffer")

    if any(
        not isinstance(identity.get(field), str) or not identity.get(field)
        for field in (
            "identity_provider_id",
            "service_account_id",
        )
    ):
        raise OpenAIError("X.509 workload identity requires identity-provider and service-account IDs")

    refresh_buffer = cast(object, identity.get("refresh_buffer_seconds"))
    if refresh_buffer is not None:
        refresh_buffer_value = _as_finite_float(refresh_buffer)
        if refresh_buffer_value is None or refresh_buffer_value < 0:
            raise OpenAIError("X.509 workload identity requires a finite, non-negative refresh buffer")


def _exchange_payload(identity: X509WorkloadIdentity) -> dict[str, str]:
    return {
        "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
        "subject_token_type": _X509_SUBJECT_TOKEN_TYPE,
        "identity_provider_id": identity["identity_provider_id"],
        "service_account_id": identity["service_account_id"],
    }


def _token_exchange_request(
    identity: X509WorkloadIdentity,
    *,
    http_client: httpx2.Client | httpx2.AsyncClient,
) -> httpx2.Request:
    request_type = httpx2.Request
    legacy_httpx = _loaded_legacy_httpx()
    if legacy_httpx is not None and not isinstance(cast(object, http_client), (httpx2.Client, httpx2.AsyncClient)):
        request_type = cast(type[httpx2.Request], cast(Any, legacy_httpx).Request)

    configured_timeout = _EXCHANGE_REQUEST_TIMEOUT.get()
    timeout = {
        phase: min(value, 10.0) if value is not None else 10.0
        for phase, value in (configured_timeout or httpx2.Timeout(10.0).as_dict()).items()
    }
    return request_type(
        "POST",
        _X509_TOKEN_EXCHANGE_URL,
        json=_exchange_payload(identity),
        extensions={"timeout": timeout},
    )


def _retry_delay(response: httpx2.Response | None, attempt: int) -> float | None:
    if response is not None:
        should_retry = response.headers.get("x-should-retry")
        if response.status_code in (400, 401, 403) or should_retry == "false":
            return None
        if should_retry != "true" and response.status_code not in (408, 409, 429) and response.status_code < 500:
            return None

        retry_after_ms = response.headers.get("retry-after-ms")
        retry_after = response.headers.get("retry-after")
        if retry_after_ms is not None:
            try:
                millisecond_delay = float(retry_after_ms) / 1000
            except ValueError:
                pass
            else:
                if math.isfinite(millisecond_delay) and 0 <= millisecond_delay <= MAX_RETRY_AFTER_DELAY:
                    return millisecond_delay
                if millisecond_delay > MAX_RETRY_AFTER_DELAY:
                    return None
        if retry_after is not None:
            try:
                delay = float(retry_after)
            except ValueError:
                try:
                    parsed = email.utils.parsedate_tz(retry_after)
                    delay = float(email.utils.mktime_tz(parsed) - time.time()) if parsed is not None else -1
                except (OverflowError, OSError, ValueError):
                    delay = -1

            if math.isfinite(delay) and 0 <= delay <= MAX_RETRY_AFTER_DELAY:
                return delay
            if delay > MAX_RETRY_AFTER_DELAY:
                return None

    return float(min(INITIAL_RETRY_DELAY * 2**attempt, MAX_RETRY_DELAY))


def _is_replayable_request(request: httpx2.Request) -> bool:
    if isinstance(getattr(request, "_content", None), bytes):
        return True

    stream = request.stream
    fields = getattr(stream, "fields", None)
    if isinstance(fields, list):
        file_positions: list[tuple[object, int]] = []
        for field in cast(list[object], fields):
            file = getattr(field, "file", None)
            if file is None or isinstance(file, (str, bytes)):
                continue
            seekable = getattr(file, "seekable", None)
            seek = getattr(file, "seek", None)
            tell = getattr(file, "tell", None)
            try:
                if not callable(seekable) or not seekable() or not callable(seek) or not callable(tell):
                    return False
                position = tell()
            except (OSError, ValueError):
                return False
            if not isinstance(position, int):
                return False
            file_positions.append((file, position))
        request.extensions[_REPLAY_FILE_POSITIONS_EXTENSION] = file_positions
        return True

    source = getattr(stream, "_stream", stream)
    seekable = getattr(source, "seekable", None)
    seek = getattr(source, "seek", None)
    tell = getattr(source, "tell", None)
    try:
        if not callable(seekable) or not seekable() or not callable(seek) or not callable(tell):
            return False
        request.extensions[_REPLAY_POSITION_EXTENSION] = tell()
    except (OSError, ValueError):
        return False
    return True


def _transport_errors() -> tuple[type[Exception], ...]:
    legacy_httpx = _loaded_legacy_httpx()
    if legacy_httpx is None:
        return (httpx2.TransportError,)
    legacy_transport_error = cast(type[Exception], getattr(legacy_httpx, "TransportError", httpx2.TransportError))
    return (httpx2.TransportError, legacy_transport_error)


def _raise_transport_error(error: Exception) -> NoReturn:
    request = cast(httpx2.Request | None, getattr(error, "request", None))
    if request is None:
        raise OpenAIError("X.509 token exchange connection failed") from error
    if isinstance(error, timeout_exceptions()):
        raise APITimeoutError(request=request) from error
    raise APIConnectionError(request=request) from error


class _X509WorkloadIdentityAuth(_WorkloadIdentityAuth[X509WorkloadIdentity]):
    def __init__(self, *, workload_identity: X509WorkloadIdentity, max_retries: int) -> None:
        _validate_identity(workload_identity)
        super().__init__(workload_identity=workload_identity, token_exchange_url=_X509_TOKEN_EXCHANGE_URL)
        self._max_exchange_retries = min(max(max_retries, 0), _MAX_EXCHANGE_RETRIES)
        self._follow_redirects = False

    @override
    def _handle_token_response(self, response: httpx2.Response) -> dict[str, Any]:
        if response.status_code not in (400, 401, 403):
            token_data = super()._handle_token_response(response)
            response_body = response.json()
            token_type = response_body.get("token_type")
            if "token_type" in response_body and (not isinstance(token_type, str) or token_type.lower() != "bearer"):
                raise OpenAIError("X.509 token exchange response must use the Bearer token type")
            if _BEARER_ACCESS_TOKEN.fullmatch(token_data["access_token"]) is None:
                raise OpenAIError("X.509 token exchange response did not include a valid Bearer access_token")
            return token_data

        try:
            response_body = response.json() if response.content else None
        except ValueError:
            response_body = None

        oauth_error = response_body.get("error") if is_dict(response_body) else None
        safe_body = {"error": oauth_error} if isinstance(oauth_error, str) else None
        raise OAuthError(response=response, body=safe_body)

    @override
    def _validate_expires_in(self, expires_in: object) -> float:
        expires_in_value = _as_finite_float(expires_in)
        if expires_in_value is None or expires_in_value <= 0:
            raise OpenAIError("X.509 token exchange response did not include a positive, finite expires_in")
        return expires_in_value

    @override
    def _can_retry_request(self, request: httpx2.Request) -> bool:
        return _is_replayable_request(request)

    @override
    def _prepare_retry_request(self, request: httpx2.Request) -> None:
        file_positions = request.extensions.get(_REPLAY_FILE_POSITIONS_EXTENSION)
        if isinstance(file_positions, list):
            for file, file_position in cast(list[tuple[object, int]], file_positions):
                seek = getattr(file, "seek", None)
                if callable(seek):
                    seek(file_position)
            return

        position = request.extensions.get(_REPLAY_POSITION_EXTENSION)
        if not isinstance(position, int):
            return
        source = getattr(request.stream, "_stream", request.stream)
        seek = getattr(source, "seek", None)
        if callable(seek):
            seek(position)

    def _usable_token_after_transient_failure(self) -> str | None:
        with self._lock:
            if self._token_unusable():
                return None
            self._cached_token_refresh_at_monotonic = time.monotonic() + INITIAL_RETRY_DELAY
            return self._cached_token

    def _handle_exchange_response(self, response: httpx2.Response) -> dict[str, Any]:
        try:
            return self._handle_token_response(response)
        except OpenAIError as error:
            if response.status_code in (408, 409, 429) or response.status_code >= 500:
                raise _TransientTokenExchangeError(error) from error
            raise


class SyncX509WorkloadIdentityAuth(_X509WorkloadIdentityAuth):
    _http_client: httpx2.Client

    def __init__(
        self, *, workload_identity: X509WorkloadIdentity, http_client: httpx2.Client, max_retries: int
    ) -> None:
        super().__init__(workload_identity=workload_identity, max_retries=max_retries)
        self._http_client = http_client

    def send_api_request(
        self,
        request: httpx2.Request,
        *,
        expected_origin: httpx2.URL,
        expected_authorization: str | None,
        stream: bool,
        **kwargs: Any,
    ) -> httpx2.Response:
        if self._http_client.is_closed:
            raise RuntimeError("Cannot send a request, as the client has been closed.")
        with _client_transport_scope(self._http_client, is_async=False).activate(
            request, expected_origin, expected_authorization
        ):
            kwargs.setdefault("auth", None)
            return self._http_client.send(request, stream=stream, **kwargs)

    def get_token_for_request(self, request: httpx2.Request) -> str:
        timeout_token = _EXCHANGE_REQUEST_TIMEOUT.set(request.extensions.get("timeout"))
        try:
            try:
                return self.get_token()
            except (APIConnectionError, _TransientTokenExchangeError) as error:
                token = self._usable_token_after_transient_failure()
                if token is None:
                    if isinstance(error, _TransientTokenExchangeError):
                        raise error.error from None
                    raise
                return token
        finally:
            _EXCHANGE_REQUEST_TIMEOUT.reset(timeout_token)

    @override
    def _fetch_token_from_exchange(self) -> dict[str, Any]:
        for attempt in range(self._max_exchange_retries + 1):
            try:
                with _scoped_sync_client(
                    self._http_client,
                    expected_origin=httpx2.URL(_X509_TOKEN_EXCHANGE_URL),
                    token_exchange=True,
                ) as scoped_client:
                    response = scoped_client.send(
                        _token_exchange_request(self.workload_identity, http_client=self._http_client),
                        auth=None,
                        follow_redirects=False,
                    )
            except _transport_errors() as error:
                if attempt >= self._max_exchange_retries:
                    _raise_transport_error(error)
                delay = _retry_delay(None, attempt)
            else:
                delay = _retry_delay(response, attempt)
                if attempt >= self._max_exchange_retries or delay is None:
                    return self._handle_exchange_response(response)

            if delay is not None:
                time.sleep(delay)

        raise AssertionError("X.509 token exchange retry loop exhausted unexpectedly")


class AsyncX509WorkloadIdentityAuth(_X509WorkloadIdentityAuth):
    _http_client: httpx2.AsyncClient

    def __init__(
        self, *, workload_identity: X509WorkloadIdentity, http_client: httpx2.AsyncClient, max_retries: int
    ) -> None:
        super().__init__(workload_identity=workload_identity, max_retries=max_retries)
        self._http_client = http_client
        self._async_lock = anyio.Lock()

    async def send_api_request(
        self,
        request: httpx2.Request,
        *,
        expected_origin: httpx2.URL,
        expected_authorization: str | None,
        stream: bool,
        **kwargs: Any,
    ) -> httpx2.Response:
        if self._http_client.is_closed:
            raise RuntimeError("Cannot send a request, as the client has been closed.")
        with _client_transport_scope(self._http_client, is_async=True).activate(
            request, expected_origin, expected_authorization
        ):
            kwargs.setdefault("auth", None)
            return await self._http_client.send(request, stream=stream, **kwargs)

    async def get_token_for_request(self, request: httpx2.Request) -> str:
        timeout_token = _EXCHANGE_REQUEST_TIMEOUT.set(request.extensions.get("timeout"))
        try:
            try:
                return await self.get_token_async()
            except (APIConnectionError, _TransientTokenExchangeError) as error:
                token = self._usable_token_after_transient_failure()
                if token is None:
                    if isinstance(error, _TransientTokenExchangeError):
                        raise error.error from None
                    raise
                return token
        finally:
            _EXCHANGE_REQUEST_TIMEOUT.reset(timeout_token)

    @override
    async def get_token_async(self) -> str:
        async with self._async_lock:
            with self._lock:
                if not self._token_unusable() and not self._needs_refresh():
                    return cast(str, self._cached_token)

            token_data = await self._fetch_token_from_exchange_async()
            self._store_token(token_data)
            with self._lock:
                return cast(str, self._cached_token)

    async def _fetch_token_from_exchange_async(self) -> dict[str, Any]:
        for attempt in range(self._max_exchange_retries + 1):
            try:
                async with _scoped_async_client(
                    self._http_client,
                    expected_origin=httpx2.URL(_X509_TOKEN_EXCHANGE_URL),
                    token_exchange=True,
                ) as scoped_client:
                    response = await scoped_client.send(
                        _token_exchange_request(self.workload_identity, http_client=self._http_client),
                        auth=None,
                        follow_redirects=False,
                    )
            except _transport_errors() as error:
                if attempt >= self._max_exchange_retries:
                    _raise_transport_error(error)
                delay = _retry_delay(None, attempt)
            else:
                delay = _retry_delay(response, attempt)
                if attempt >= self._max_exchange_retries or delay is None:
                    return self._handle_exchange_response(response)

            if delay is not None:
                await anyio.sleep(delay)

        raise AssertionError("X.509 token exchange retry loop exhausted unexpectedly")


def can_share_x509_auth(
    current: object,
    replacement: object,
    *,
    current_origin: httpx2.URL,
    replacement_origin: httpx2.URL,
) -> bool:
    auth_types = (SyncX509WorkloadIdentityAuth, AsyncX509WorkloadIdentityAuth)
    if not isinstance(current, auth_types) or not isinstance(replacement, auth_types):
        return False
    return (
        type(current) is type(replacement)
        and current.workload_identity == replacement.workload_identity
        and current._http_client is replacement._http_client
        and current_origin == replacement_origin
        and current._max_exchange_retries == replacement._max_exchange_retries
    )
