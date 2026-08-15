from __future__ import annotations

import math
import time
import email.utils
from typing import Any, NoReturn, cast
from typing_extensions import TypeIs, override

import anyio
import httpx2

from .._utils import is_dict
from .._httpx2 import timeout_exceptions, _loaded_legacy_httpx
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
_ALLOWED_IDENTITY_FIELDS = {"type", "identity_provider_id", "service_account_id", "refresh_buffer_seconds"}


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
    if refresh_buffer is not None and (
        isinstance(refresh_buffer, bool)
        or not isinstance(refresh_buffer, (int, float))
        or not math.isfinite(refresh_buffer)
        or refresh_buffer < 0
    ):
        raise OpenAIError("X.509 workload identity requires a finite, non-negative refresh buffer")


def _exchange_payload(identity: X509WorkloadIdentity) -> dict[str, str]:
    return {
        "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
        "subject_token_type": _X509_SUBJECT_TOKEN_TYPE,
        "identity_provider_id": identity["identity_provider_id"],
        "service_account_id": identity["service_account_id"],
    }


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
        for field in cast(list[object], fields):
            file = getattr(field, "file", None)
            if file is None or isinstance(file, (str, bytes)):
                continue
            seekable = getattr(file, "seekable", None)
            if not callable(seekable) or not seekable():
                return False
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
            return super()._handle_token_response(response)

        try:
            response_body = response.json() if response.content else None
        except ValueError:
            response_body = None

        oauth_error = response_body.get("error") if is_dict(response_body) else None
        safe_body = {"error": oauth_error} if isinstance(oauth_error, str) else None
        raise OAuthError(response=response, body=safe_body)

    @override
    def _validate_expires_in(self, expires_in: object) -> float:
        if isinstance(expires_in, bool) or not isinstance(expires_in, (int, float)):
            raise OpenAIError("X.509 token exchange response did not include a positive, finite expires_in")
        if not math.isfinite(expires_in) or expires_in <= 0:
            raise OpenAIError("X.509 token exchange response did not include a positive, finite expires_in")
        return float(expires_in)

    @override
    def _can_retry_request(self, request: httpx2.Request) -> bool:
        return _is_replayable_request(request)

    @override
    def _prepare_retry_request(self, request: httpx2.Request) -> None:
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

    @override
    def _fetch_token_from_exchange(self) -> dict[str, Any]:
        for attempt in range(self._max_exchange_retries + 1):
            try:
                response = self._http_client.post(
                    _X509_TOKEN_EXCHANGE_URL,
                    json=_exchange_payload(self.workload_identity),
                    auth=lambda request: request,
                    timeout=10.0,
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
                response = await self._http_client.post(
                    _X509_TOKEN_EXCHANGE_URL,
                    json=_exchange_payload(self.workload_identity),
                    auth=lambda request: request,
                    timeout=10.0,
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
