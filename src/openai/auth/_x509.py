from __future__ import annotations

import re
import math
import time
import importlib
import threading
import email.utils
from typing import Any, Iterable, Iterator, NoReturn, SupportsIndex, cast
from weakref import ReferenceType, ref
from functools import wraps
from contextlib import ExitStack, contextmanager
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
_ACTIVE_AUXILIARY_TRANSPORT_MARKERS: set[object] = set()
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
            current_authorization = request.headers.get("Authorization")
            originating_request = _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES[marker][0]
            if (
                marker in _ACTIVE_AUXILIARY_TRANSPORT_MARKERS or request is not originating_request
            ) and current_authorization is not None:
                for _, _, active_authorization in _ACTIVE_API_TRANSPORT_SCOPES.values():
                    if active_authorization is None:
                        continue
                    access_token = active_authorization.removeprefix("Bearer ")
                    if access_token in current_authorization:
                        return False
            return True
        request_authorization = request.headers.get("Authorization")
        for auxiliary_marker in _ACTIVE_AUXILIARY_TRANSPORT_MARKERS:
            auxiliary_scope = _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES.get(auxiliary_marker)
            if auxiliary_scope is None:
                continue
            auxiliary_request, auxiliary_url, auxiliary_authorization = auxiliary_scope
            if (
                request.method != auxiliary_request.method
                or request.url != auxiliary_url
                or request_authorization != auxiliary_authorization
            ):
                continue
            if request_authorization is not None:
                for _, _, active_authorization in _ACTIVE_API_TRANSPORT_SCOPES.values():
                    if active_authorization is not None:
                        access_token = active_authorization.removeprefix("Bearer ")
                        if access_token in request_authorization:
                            return False
            request.extensions[_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION] = auxiliary_marker
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
        self._hooks = hooks
        self._finalizer = finalizer

    def _synchronize(self) -> None:
        super().clear()
        super().extend(self._hooks)

    @override
    def __len__(self) -> int:
        return len(self._hooks)

    @override
    def __repr__(self) -> str:
        return repr(self._hooks)

    @override
    def __str__(self) -> str:
        return str(self._hooks)

    @override
    def __eq__(self, other: object) -> bool:
        return self._hooks == (other._hooks if isinstance(other, _FinalizingRequestHooks) else other)

    @override
    def __ne__(self, other: object) -> bool:
        return not self == other

    @override
    def __lt__(self, other: Any) -> bool:
        return self._hooks < (other._hooks if isinstance(other, _FinalizingRequestHooks) else other)

    @override
    def __le__(self, other: Any) -> bool:
        return self._hooks <= (other._hooks if isinstance(other, _FinalizingRequestHooks) else other)

    @override
    def __gt__(self, other: Any) -> bool:
        return self._hooks > (other._hooks if isinstance(other, _FinalizingRequestHooks) else other)

    @override
    def __ge__(self, other: Any) -> bool:
        return self._hooks >= (other._hooks if isinstance(other, _FinalizingRequestHooks) else other)

    @override
    def __getitem__(self, index: Any) -> Any:
        return self._hooks[index]

    @override
    def __setitem__(self, index: Any, value: Any) -> None:
        if isinstance(index, slice) and isinstance(value, _FinalizingRequestHooks):
            value = value._hooks.copy()
        self._hooks[index] = value
        self._synchronize()

    @override
    def __delitem__(self, index: Any) -> None:
        del self._hooks[index]
        self._synchronize()

    @override
    def __contains__(self, hook: object) -> bool:
        return hook in self._hooks

    @override
    def __add__(self, hooks: list[Any]) -> list[Any]:
        return self._hooks + (hooks._hooks if isinstance(hooks, _FinalizingRequestHooks) else hooks)

    def __radd__(self, hooks: list[Any]) -> list[Any]:
        return hooks + self._hooks

    @override
    def __mul__(self, count: SupportsIndex) -> list[Any]:
        return self._hooks * count

    @override
    def __rmul__(self, count: SupportsIndex) -> list[Any]:
        return count * self._hooks

    @override
    def __iadd__(self, hooks: Iterable[Any]) -> _FinalizingRequestHooks:
        self._hooks.extend(hooks._hooks.copy() if isinstance(hooks, _FinalizingRequestHooks) else hooks)
        self._synchronize()
        return self

    @override
    def __imul__(self, count: SupportsIndex) -> _FinalizingRequestHooks:
        self._hooks *= count
        self._synchronize()
        return self

    @override
    def append(self, hook: Any) -> None:
        self._hooks.append(hook)
        self._synchronize()

    @override
    def clear(self) -> None:
        self._hooks.clear()
        self._synchronize()

    @override
    def count(self, hook: Any) -> int:
        return self._hooks.count(hook)

    @override
    def extend(self, hooks: Iterable[Any]) -> None:
        self._hooks.extend(hooks._hooks.copy() if isinstance(hooks, _FinalizingRequestHooks) else hooks)
        self._synchronize()

    @override
    def index(self, hook: Any, *args: Any) -> int:
        return self._hooks.index(hook, *args)

    @override
    def insert(self, index: SupportsIndex, hook: Any) -> None:
        self._hooks.insert(index, hook)
        self._synchronize()

    @override
    def pop(self, index: SupportsIndex = -1) -> Any:
        hook = self._hooks.pop(index)
        self._synchronize()
        return hook

    @override
    def remove(self, hook: Any) -> None:
        self._hooks.remove(hook)
        self._synchronize()

    @override
    def reverse(self) -> None:
        self._hooks.reverse()
        self._synchronize()

    @override
    def sort(self, *, key: Any = None, reverse: bool = False) -> None:
        self._hooks.sort(key=key, reverse=reverse)
        self._synchronize()

    @override
    def copy(self) -> list[Any]:
        return self._hooks.copy()

    @override
    def __reversed__(self) -> Iterator[Any]:
        return reversed(self._hooks)

    @override
    def __iter__(self) -> Iterator[Any]:
        finalizer = self._finalizer
        yield finalizer
        index = 0
        while index < len(self._hooks):
            hook = self._hooks[index]
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
        self._original_build_request: Any = None
        self._had_build_request_attribute = False
        self._auxiliary_request_markers: set[object] = set()

    def _build_auxiliary_request(self, *args: Any, **kwargs: Any) -> httpx2.Request:
        request = cast(httpx2.Request, self._original_build_request(*args, **kwargs))
        active_scope = _API_TRANSPORT_SCOPE.get()
        if active_scope is None or request is active_scope[0]:
            return request

        authorization = request.headers.get("Authorization")
        if authorization is not None:
            with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
                for _, _, expected_authorization in _ACTIVE_API_TRANSPORT_SCOPES.values():
                    if expected_authorization is not None:
                        access_token = expected_authorization.removeprefix("Bearer ")
                        if access_token in authorization:
                            return request

        marker = object()
        request.extensions[_UNPROTECTED_TRANSPORT_SCOPE_EXTENSION] = marker
        with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
            _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES[marker] = (request, request.url, authorization)
            _ACTIVE_AUXILIARY_TRANSPORT_MARKERS.add(marker)
        with self._lock:
            self._auxiliary_request_markers.add(marker)
        return request

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
            request_authorization = request.headers.get("Authorization")
            matching_authorization = [
                (marker, active_scope)
                for marker, active_scope in self._request_scopes.items()
                if request_authorization is not None
                and active_scope[2] is not None
                and (
                    request_authorization == active_scope[2]
                    or (
                        active_scope[2].startswith("Bearer ")
                        and active_scope[2][len("Bearer ") :] in request_authorization
                    )
                )
            ]
            if not matching_authorization:
                return None
            exact_authorization = [
                (marker, active_scope)
                for marker, active_scope in matching_authorization
                if request_authorization == active_scope[2]
            ]
            if exact_authorization:
                matching_authorization = exact_authorization
            if len({(active_scope[1].host, active_scope[1].port) for _, active_scope in matching_authorization}) > 1:
                raise OpenAIError("X.509 workload identity request cannot be associated with a single API origin")
            same_origin = [
                (marker, active_scope)
                for marker, active_scope in matching_authorization
                if (request.url.host, request.url.port) == (active_scope[1].host, active_scope[1].port)
            ]
            marker, active_scope = (same_origin if same_origin else matching_authorization)[0]
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
                self._had_build_request_attribute = "build_request" in vars(http_client)
                self._original_build_request = http_client.build_request
                vars(http_client)["build_request"] = self._build_auxiliary_request
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
            auxiliary_markers: set[object] = set()
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
                    if self._had_build_request_attribute:
                        vars(http_client)["build_request"] = self._original_build_request
                    else:
                        vars(http_client).pop("build_request", None)
                    auxiliary_markers = self._auxiliary_request_markers
                    self._auxiliary_request_markers = set()
                    self._original_transport = None
                    self._original_mounts = {}
                    self._original_request_hooks = []
                    self._original_build_request = None
            if auxiliary_markers:
                with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
                    for auxiliary_marker in auxiliary_markers:
                        _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES.pop(auxiliary_marker, None)
                        _ACTIVE_AUXILIARY_TRANSPORT_MARKERS.discard(auxiliary_marker)


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


_CLIENT_SEND_GUARD_LOCK = threading.RLock()
_CLIENT_SEND_GUARD_STATE = {"users": 0}
_ORIGINAL_CLIENT_DISPATCH_METHODS: dict[type[Any], tuple[Any, Any, Any, Any]] = {}


def _active_request_transport_scope(request: httpx2.Request) -> tuple[httpx2.Request, httpx2.URL, str | None] | None:
    request_scope = _request_transport_scope(request)
    if _is_unprotected_transport_request(request):
        return None

    authorization = request.headers.get("Authorization")
    if request_scope is not None:
        marker = request.extensions.get(_API_TRANSPORT_SCOPE_EXTENSION)
        with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
            marked_scope = type(marker) is object and marker in _ACTIVE_API_TRANSPORT_SCOPES
        protected_authorization = request_scope[2]
        if (
            request is request_scope[0]
            or marked_scope
            or (
                authorization is not None
                and protected_authorization is not None
                and (
                    authorization == protected_authorization
                    or (
                        protected_authorization.startswith("Bearer ")
                        and protected_authorization[len("Bearer ") :] in authorization
                    )
                )
            )
        ):
            return request_scope

    if authorization is None:
        return None
    with _ACTIVE_API_TRANSPORT_SCOPES_LOCK:
        matching_scopes = [
            scope
            for scope in _ACTIVE_API_TRANSPORT_SCOPES.values()
            if scope[2] is not None
            and (
                authorization == scope[2]
                or (scope[2].startswith("Bearer ") and scope[2][len("Bearer ") :] in authorization)
            )
        ]
    if not matching_scopes:
        return None
    exact_scopes = [scope for scope in matching_scopes if authorization == scope[2]]
    if exact_scopes:
        matching_scopes = exact_scopes
    if len({(scope[1].host, scope[1].port) for scope in matching_scopes}) > 1:
        raise OpenAIError("X.509 workload identity request cannot be associated with a single API origin")
    same_origin = [
        scope for scope in matching_scopes if (request.url.host, request.url.port) == (scope[1].host, scope[1].port)
    ]
    return (same_origin if same_origin else matching_scopes)[0]


def _validate_guarded_client_dispatch(request: httpx2.Request) -> None:
    request_scope = _active_request_transport_scope(request)
    if request_scope is not None:
        _validate_transport_request(
            request,
            expected_origin=request_scope[1],
            expected_authorization=request_scope[2],
            token_exchange=False,
        )


@contextmanager
def _guarded_client_redirects(http_client: Any, request: httpx2.Request, *, is_async: bool) -> Iterator[None]:
    request_scope = _active_request_transport_scope(request)
    if request_scope is None:
        yield
        return

    client_scope = _client_transport_scope(http_client, is_async=is_async)
    marker = request.extensions.get(_API_TRANSPORT_SCOPE_EXTENSION)
    with client_scope._lock:
        already_scoped = type(marker) is object and marker in client_scope._request_scopes
    if already_scoped:
        yield
        return

    with client_scope.activate(request, request_scope[1], request_scope[2]):
        yield


def _guard_client_dispatch_method(client_type: type[Any], *, is_async: bool) -> None:
    original_dispatch = client_type._send_single_request
    original_redirects = client_type._send_handling_redirects
    if is_async:

        @wraps(original_dispatch)
        async def guarded_async_dispatch(client: Any, request: httpx2.Request, *args: Any, **kwargs: Any) -> Any:
            _validate_guarded_client_dispatch(request)
            return await original_dispatch(client, request, *args, **kwargs)

        guarded_dispatch: Any = guarded_async_dispatch

        @wraps(original_redirects)
        async def guarded_async_redirects(client: Any, request: httpx2.Request, *args: Any, **kwargs: Any) -> Any:
            with _guarded_client_redirects(client, request, is_async=True):
                return await original_redirects(client, request, *args, **kwargs)

        guarded_redirects: Any = guarded_async_redirects
    else:

        @wraps(original_dispatch)
        def guarded_sync_dispatch(client: Any, request: httpx2.Request, *args: Any, **kwargs: Any) -> Any:
            _validate_guarded_client_dispatch(request)
            return original_dispatch(client, request, *args, **kwargs)

        guarded_dispatch = guarded_sync_dispatch

        @wraps(original_redirects)
        def guarded_sync_redirects(client: Any, request: httpx2.Request, *args: Any, **kwargs: Any) -> Any:
            with _guarded_client_redirects(client, request, is_async=False):
                return original_redirects(client, request, *args, **kwargs)

        guarded_redirects = guarded_sync_redirects

    _ORIGINAL_CLIENT_DISPATCH_METHODS[client_type] = (
        original_dispatch,
        guarded_dispatch,
        original_redirects,
        guarded_redirects,
    )
    client_type._send_single_request = guarded_dispatch
    client_type._send_handling_redirects = guarded_redirects


@contextmanager
def _active_client_send_guards() -> Iterator[None]:
    with _CLIENT_SEND_GUARD_LOCK:
        if _CLIENT_SEND_GUARD_STATE["users"] == 0:
            client_types: list[tuple[type[Any], bool]] = [(httpx2.Client, False), (httpx2.AsyncClient, True)]
            legacy_httpx = _loaded_legacy_httpx()
            if legacy_httpx is None:
                try:
                    importlib.import_module("httpx")
                except ModuleNotFoundError as error:
                    if error.name != "httpx":
                        raise
                else:
                    legacy_httpx = _loaded_legacy_httpx()
            if legacy_httpx is not None:
                client_types.extend([(legacy_httpx.Client, False), (legacy_httpx.AsyncClient, True)])
            for client_type, is_async in client_types:
                if client_type not in _ORIGINAL_CLIENT_DISPATCH_METHODS:
                    _guard_client_dispatch_method(client_type, is_async=is_async)
        _CLIENT_SEND_GUARD_STATE["users"] += 1

    try:
        yield
    finally:
        with _CLIENT_SEND_GUARD_LOCK:
            _CLIENT_SEND_GUARD_STATE["users"] -= 1
            if _CLIENT_SEND_GUARD_STATE["users"] == 0:
                for client_type, methods in _ORIGINAL_CLIENT_DISPATCH_METHODS.items():
                    original_dispatch, guarded_dispatch, original_redirects, guarded_redirects = methods
                    if client_type._send_single_request is guarded_dispatch:
                        client_type._send_single_request = original_dispatch
                    if client_type._send_handling_redirects is guarded_redirects:
                        client_type._send_handling_redirects = original_redirects
                _ORIGINAL_CLIENT_DISPATCH_METHODS.clear()


@contextmanager
def _active_client_transport_scopes(
    http_client: httpx2.Client | httpx2.AsyncClient,
    request: httpx2.Request,
    expected_origin: httpx2.URL,
    expected_authorization: str | None,
    *,
    is_async: bool,
) -> Iterator[None]:
    client_types: tuple[type[Any], ...] = (httpx2.AsyncClient if is_async else httpx2.Client,)
    legacy_httpx = _loaded_legacy_httpx()
    if legacy_httpx is not None:
        client_types += (legacy_httpx.AsyncClient if is_async else legacy_httpx.Client,)
    pending = [http_client]
    visited: set[int] = set()
    with ExitStack() as scopes:
        scopes.enter_context(_active_client_send_guards())
        while pending:
            current = pending.pop()
            if id(current) in visited:
                continue
            visited.add(id(current))
            scopes.enter_context(
                _client_transport_scope(current, is_async=is_async).activate(
                    request, expected_origin, expected_authorization
                )
            )
            values = list(vars(current).values())
            for owner in type(current).__mro__:
                slots = owner.__dict__.get("__slots__", ())
                if isinstance(slots, str):
                    slots = (slots,)
                for slot in slots:
                    if slot in ("__dict__", "__weakref__"):
                        continue
                    if slot.startswith("__") and not slot.endswith("__"):
                        slot = f"_{owner.__name__.lstrip('_')}{slot}"
                    values.append(getattr(current, slot, None))

            inspected: set[int] = set()
            while values:
                value = values.pop()
                if id(value) in inspected:
                    continue
                inspected.add(id(value))
                if isinstance(value, client_types):
                    pending.append(value)
                elif isinstance(value, dict):
                    values.extend(cast(dict[object, object], value).values())
                elif isinstance(value, (list, tuple, set, frozenset)):
                    values.extend(cast(list[object] | tuple[object, ...] | set[object] | frozenset[object], value))
        yield


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

    @override
    def _perform_refresh(self) -> None:
        try:
            super()._perform_refresh()
        except (APIConnectionError, _TransientTokenExchangeError):
            if self._usable_token_after_transient_failure() is None:
                raise

    def _handle_exchange_response(self, response: httpx2.Response) -> dict[str, Any]:
        try:
            return self._handle_token_response(response)
        except OpenAIError as error:
            if (
                response.status_code in (408, 409, 429)
                or response.status_code >= 500
                or (response.status_code not in (400, 401, 403) and response.headers.get("x-should-retry") == "true")
            ):
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
        with _active_client_transport_scopes(
            self._http_client, request, expected_origin, expected_authorization, is_async=False
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
        with _active_client_transport_scopes(
            self._http_client, request, expected_origin, expected_authorization, is_async=True
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

            try:
                token_data = await self._fetch_token_from_exchange_async()
            except (APIConnectionError, _TransientTokenExchangeError):
                token = self._usable_token_after_transient_failure()
                if token is None:
                    raise
                return token
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
