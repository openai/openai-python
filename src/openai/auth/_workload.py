from __future__ import annotations

import time
import threading
from typing import Any, Callable, TypedDict, cast
from pathlib import Path
from typing_extensions import Literal, NotRequired

import httpx

from .._exceptions import OAuthError, OpenAIError, SubjectTokenProviderError
from .._utils._sync import to_thread

TOKEN_EXCHANGE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"
DEFAULT_TOKEN_EXCHANGE_URL = "https://auth.openai.com/oauth/token"
DEFAULT_REFRESH_BUFFER_SECONDS = 1200

SUBJECT_TOKEN_TYPES = {
    "jwt": "urn:ietf:params:oauth:token-type:jwt",
    "id": "urn:ietf:params:oauth:token-type:id_token",
}


class SubjectTokenProvider(TypedDict):
    token_type: Literal["jwt", "id"]
    get_token: Callable[[], str]


class WorkloadIdentity(TypedDict):
    """A unique string that identifies the client."""

    client_id: str

    """Identity provider resource id in WIFAPI."""
    identity_provider_id: str

    """Service account id to bind the verified external identity to."""
    service_account_id: str

    """The provider configuration for obtaining the subject token."""
    provider: SubjectTokenProvider

    """Optional buffer time in seconds to refresh the OpenAI token before it expires. Defaults to 1200 seconds (20 minutes)."""
    refresh_buffer_seconds: NotRequired[float]


def k8s_service_account_token_provider(
    token_file_path: str | Path = "/var/run/secrets/kubernetes.io/serviceaccount/token",
) -> SubjectTokenProvider:
    """
    Get a subject token provider for Kubernetes clusters with Workload Identity configured.

    Cloud providers typically mount the subject token as a file in the container.

    Args:
        token_file_path: path to the mounted service account token file. Defaults to `/var/run/secrets/kubernetes.io/serviceaccount/token`.
    """

    def get_token() -> str:
        try:
            with open(token_file_path, "r") as f:
                token = f.read().strip()
                if not token:
                    raise SubjectTokenProviderError(f"The token file at {token_file_path} is empty.")
                return token
        except Exception as e:
            raise SubjectTokenProviderError(f"Failed to read the token file at {token_file_path}: {e}") from e

    return {"token_type": "jwt", "get_token": get_token}


def azure_managed_identity_token_provider(
    resource: str = "https://management.azure.com/",
    *,
    object_id: str | None = None,
    client_id: str | None = None,
    msi_res_id: str | None = None,
    api_version: str = "2018-02-01",
    timeout: float = 10.0,
    http_client: httpx.Client | None = None,
) -> SubjectTokenProvider:
    """
    Get a subject token provider for Azure Managed Identities.

    See: https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/how-to-use-vm-token#get-a-token-using-http

    Args:
        resource: the resource URI to request a token for. Defaults to `https://management.azure.com/` (Azure Resource Manager).
        object_id: the object ID of the managed identity to use, when multiple are assigned.
        client_id: the client ID of the managed identity to use, when multiple are assigned.
        msi_res_id: the ARM resource ID of the managed identity to use, when multiple are assigned.
        api_version: the Azure IMDS API version. Defaults to `2018-02-01`.
        timeout: the request timeout in seconds. Defaults to 10.0.
        http_client: optional httpx.Client instance to use for requests. If not provided, a new client will be created for each request.
    """

    def get_token() -> str:
        try:
            url = "http://169.254.169.254/metadata/identity/oauth2/token"
            params: dict[str, str] = {"api-version": api_version, "resource": resource}
            if object_id is not None:
                params["object_id"] = object_id
            if client_id is not None:
                params["client_id"] = client_id
            if msi_res_id is not None:
                params["msi_res_id"] = msi_res_id

            if http_client is not None:
                response = http_client.get(url, params=params, headers={"Metadata": "true"}, timeout=timeout)
            else:
                with httpx.Client() as client:
                    response = client.get(url, params=params, headers={"Metadata": "true"}, timeout=timeout)

            if response.is_error:
                raise SubjectTokenProviderError(
                    f"Failed to fetch Azure subject token from IMDS: HTTP {response.status_code}",
                    response=response,
                )
            data = response.json()
            token = data.get("access_token")
            if not token:
                raise SubjectTokenProviderError(
                    "Azure IMDS response did not include an access_token", response=response
                )
            return cast(str, token)
        except Exception as e:
            raise SubjectTokenProviderError(f"Failed to fetch Azure subject token from IMDS: {e}") from e

    return {"token_type": "jwt", "get_token": get_token}


def gcp_id_token_provider(
    audience: str = "https://api.openai.com/v1",
    *,
    timeout: float = 10.0,
    http_client: httpx.Client | None = None,
) -> SubjectTokenProvider:
    """
    Get a subject token provider for GCP VM instances using the instance metadata server.

    See: https://cloud.google.com/compute/docs/instances/verifying-instance-identity

    Args:
        audience: the unique URI agreed upon by both the instance and the system verifying
            the instance's identity. Defaults to `https://api.openai.com/v1`.
        timeout: the request timeout in seconds. Defaults to 10.0.
        http_client: optional httpx.Client instance to use for requests. If not provided, a new client will be created for each request.
    """

    def get_token() -> str:
        try:
            url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity"
            params = {"audience": audience}

            if http_client is not None:
                response = http_client.get(url, params=params, headers={"Metadata-Flavor": "Google"}, timeout=timeout)
            else:
                with httpx.Client() as client:
                    response = client.get(url, params=params, headers={"Metadata-Flavor": "Google"}, timeout=timeout)

            if response.is_error:
                raise SubjectTokenProviderError(
                    f"Failed to fetch GCP subject token from metadata server: HTTP {response.status_code}",
                    response=response,
                )
            token = response.text.strip()
            if not token:
                raise SubjectTokenProviderError("GCP metadata server returned an empty token", response=response)
            return token
        except Exception as e:
            raise SubjectTokenProviderError(f"Failed to fetch GCP subject token from metadata server: {e}") from e

    return {"token_type": "id", "get_token": get_token}


class WorkloadIdentityAuth:
    def __init__(
        self,
        *,
        workload_identity: WorkloadIdentity,
        token_exchange_url: str = DEFAULT_TOKEN_EXCHANGE_URL,
    ):
        self.workload_identity = workload_identity
        self.token_exchange_url = token_exchange_url

        self._cached_token: str | None = None
        self._cached_token_expires_at_monotonic: float | None = None
        self._cached_token_refresh_at_monotonic: float | None = None
        self._refreshing: bool = False
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

    def get_token(self) -> str:
        with self._lock:
            while self._refreshing and self._token_unusable():
                self._condition.wait()

            if not self._token_unusable() and not self._needs_refresh():
                return cast(str, self._cached_token)

            if self._refreshing:
                while self._refreshing:
                    self._condition.wait()
                token = self._cached_token  # type: ignore[unreachable]
                if self._token_unusable():
                    raise RuntimeError("Token is unusable after refresh completed")
                return cast(str, token)

            self._refreshing = True

        try:
            self._perform_refresh()
            with self._lock:
                if self._token_unusable():
                    raise RuntimeError("Token is unusable after refresh completed")
                return cast(str, self._cached_token)
        finally:
            with self._lock:
                self._refreshing = False
                self._condition.notify_all()

    async def get_token_async(self) -> str:
        return await to_thread(self.get_token)

    def invalidate_token(self) -> None:
        with self._lock:
            self._cached_token = None
            self._cached_token_expires_at_monotonic = None
            self._cached_token_refresh_at_monotonic = None

    def _perform_refresh(self) -> None:
        token_data = self._fetch_token_from_exchange()
        now = time.monotonic()
        expires_in = token_data["expires_in"]

        with self._lock:
            self._cached_token = token_data["access_token"]
            self._cached_token_expires_at_monotonic = now + expires_in
            self._cached_token_refresh_at_monotonic = now + self._refresh_delay_seconds(expires_in)

    def _fetch_token_from_exchange(self) -> dict[str, Any]:
        subject_token = self._get_subject_token()

        token_type = self.workload_identity["provider"]["token_type"]
        subject_token_type = SUBJECT_TOKEN_TYPES.get(token_type)
        if subject_token_type is None:
            raise OpenAIError(
                f"Unsupported token type: {token_type!r}. Supported types: {', '.join(SUBJECT_TOKEN_TYPES.keys())}"
            )

        with httpx.Client() as client:
            response = client.post(
                self.token_exchange_url,
                json={
                    "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
                    "client_id": self.workload_identity["client_id"],
                    "subject_token": subject_token,
                    "subject_token_type": subject_token_type,
                    "identity_provider_id": self.workload_identity["identity_provider_id"],
                    "service_account_id": self.workload_identity["service_account_id"],
                },
                timeout=10.0,
            )
            return self._handle_token_response(response)

    def _handle_token_response(self, response: httpx.Response) -> dict[str, Any]:
        try:
            body = response.json() if response.content else None
        except ValueError:
            body = None

        if response.status_code in (400, 401, 403):
            raise OAuthError(response=response, body=body)

        if response.is_success:
            if body is None:
                raise OpenAIError("Token exchange succeeded but response body was empty")
            access_token = body.get("access_token")
            expires_in = body.get("expires_in")
            if not isinstance(access_token, str) or not access_token:
                raise OpenAIError("Token exchange response did not include a valid access_token")
            if not isinstance(expires_in, (int, float)):
                raise OpenAIError("Token exchange response did not include a valid expires_in")
            return {"access_token": access_token, "expires_in": float(expires_in)}

        raise OpenAIError(
            f"Token exchange failed with status {response.status_code}",
        )

    def _get_subject_token(self) -> str:
        provider = self.workload_identity["provider"]
        subject_token = provider["get_token"]()
        if not subject_token:
            raise OpenAIError("The workload identity provider returned an empty subject token")
        return subject_token

    def _token_unusable(self) -> bool:
        return self._cached_token is None or self._token_expired()

    def _token_expired(self) -> bool:
        if self._cached_token_expires_at_monotonic is None:
            return True
        return time.monotonic() >= self._cached_token_expires_at_monotonic

    def _needs_refresh(self) -> bool:
        if self._cached_token_refresh_at_monotonic is None:
            return False
        return time.monotonic() >= self._cached_token_refresh_at_monotonic

    def _refresh_delay_seconds(self, expires_in: float) -> float:
        configured_buffer = self.workload_identity.get("refresh_buffer_seconds", DEFAULT_REFRESH_BUFFER_SECONDS)
        effective_buffer = min(configured_buffer, expires_in / 2)
        return max(expires_in - effective_buffer, 0.0)
