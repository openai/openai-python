from __future__ import annotations

import re
import math
import time
import email.utils
from typing import Any, NoReturn, cast
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
        return self._http_client._transport_for_url(request.url).handle_request(request)

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
        return await self._http_client._transport_for_url(request.url).handle_async_request(request)

    @override
    async def aclose(self) -> None:
        # The caller owns the selected connection pool and proxy transports.
        return None


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
    scoped_client = client_type(
        transport=transport,
        timeout=http_client.timeout,
        event_hooks=None if token_exchange else http_client.event_hooks,
        trust_env=False,
    )
    if not token_exchange:
        scoped_client._cookies = http_client.cookies
    return scoped_client


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
    scoped_client = client_type(
        transport=transport,
        timeout=http_client.timeout,
        event_hooks=None if token_exchange else http_client.event_hooks,
        trust_env=False,
    )
    if not token_exchange:
        scoped_client._cookies = http_client.cookies
    return scoped_client


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


def _validate_identity(identity: X509WorkloadIdentity) -> None:
    if "provider" in identity or "client_id" in identity:
        raise OpenAIError("X.509 workload identity does not accept a subject-token provider or client ID")

    if set(identity) - _ALLOWED_IDENTITY_FIELDS:
        raise OpenAIError("X.509 workload identity accepts only identity IDs and an optional refresh buffer")

    if not identity.get("identity_provider_id") or not identity.get("service_account_id"):
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

    return request_type(
        "POST",
        _X509_TOKEN_EXCHANGE_URL,
        json=_exchange_payload(identity),
        extensions={"timeout": httpx2.Timeout(10.0).as_dict()},
    )


def _retry_delay(response: httpx2.Response | None, attempt: int) -> float | None:
    if response is not None:
        if response.status_code not in (408, 409, 429) and response.status_code < 500:
            return None

        retry_after = response.headers.get("retry-after")
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
            if not callable(seekable) or not seekable() or not callable(seek) or not callable(tell):
                return False
            position = tell()
            if not isinstance(position, int):
                return False
            file_positions.append((file, position))
        request.extensions[_REPLAY_FILE_POSITIONS_EXTENSION] = file_positions
        return True

    source = getattr(stream, "_stream", stream)
    seekable = getattr(source, "seekable", None)
    seek = getattr(source, "seek", None)
    tell = getattr(source, "tell", None)
    if not callable(seekable) or not seekable() or not callable(seek) or not callable(tell):
        return False
    request.extensions[_REPLAY_POSITION_EXTENSION] = tell()
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


class SyncX509WorkloadIdentityAuth(_X509WorkloadIdentityAuth):
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
        with _scoped_sync_client(
            self._http_client,
            expected_origin=expected_origin,
            expected_authorization=expected_authorization,
        ) as scoped_client:
            return scoped_client.send(request, stream=stream, **kwargs)

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
                    return self._handle_token_response(response)

            if delay is not None:
                time.sleep(delay)

        raise AssertionError("X.509 token exchange retry loop exhausted unexpectedly")


class AsyncX509WorkloadIdentityAuth(_X509WorkloadIdentityAuth):
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
        async with _scoped_async_client(
            self._http_client,
            expected_origin=expected_origin,
            expected_authorization=expected_authorization,
        ) as scoped_client:
            return await scoped_client.send(request, stream=stream, **kwargs)

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
                    return self._handle_token_response(response)

            if delay is not None:
                await anyio.sleep(delay)

        raise AssertionError("X.509 token exchange retry loop exhausted unexpectedly")
