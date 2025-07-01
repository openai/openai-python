from __future__ import annotations

from typing import Any, Mapping, Generator
from typing_extensions import override

import oci
import httpx
import requests
from oci.config import DEFAULT_PROFILE, DEFAULT_LOCATION

from .._client import (
    NOT_GIVEN,
    DEFAULT_MAX_RETRIES,
    OpenAI,
    Timeout,
    NotGiven,
    AsyncOpenAI,
)
from .._base_client import DefaultHttpxClient, DefaultAsyncHttpxClient

OciAuthSigner = type[oci.signer.AbstractBaseSigner]


class OciOpenAI(OpenAI):
    """
    A custom OpenAI client implementation for Oracle Cloud Infrastructure (OCI) Generative AI service.

    This class extends the OpenAI client to work with OCI's Generative AI service endpoints,
    handling authentication and request signing specific to OCI.

    Attributes:
        service_endpoint (str): The OCI service endpoint URL
        auth (httpx.Auth): Authentication handler for OCI
        compartment_id (str): OCI compartment ID for resource isolation
        timeout (float | Timeout | None | NotGiven): Request timeout configuration
        max_retries (int): Maximum number of retry attempts for failed requests
        default_headers (Mapping[str, str] | None): Default HTTP headers
        default_query (Mapping[str, object] | None): Default query parameters
    """

    def __init__(
        self,
        *,
        service_endpoint: str,
        auth: httpx.Auth,
        compartment_id: str,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            api_key="<NOTUSED>",
            base_url=f"{service_endpoint}/20231130/actions/v1",
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=DefaultHttpxClient(
                auth=auth,
                headers={
                    "CompartmentId": compartment_id,
                },
            ),
        )


class AsyncOciOpenAI(AsyncOpenAI):
    """
    An async custom OpenAI client implementation for Oracle Cloud Infrastructure (OCI) Generative AI service.

    This class extends the AsyncOpenAI client to work with OCI's Generative AI service endpoints,
    handling authentication and request signing specific to OCI with async/await support.

    Attributes:
        service_endpoint (str): The OCI service endpoint URL
        auth (httpx.Auth): Authentication handler for OCI
        compartment_id (str): OCI compartment ID for resource isolation
        timeout (float | Timeout | None | NotGiven): Request timeout configuration
        max_retries (int): Maximum number of retry attempts for failed requests
        default_headers (Mapping[str, str] | None): Default HTTP headers
        default_query (Mapping[str, object] | None): Default query parameters
    """

    def __init__(
        self,
        *,
        service_endpoint: str,
        auth: httpx.Auth,
        compartment_id: str,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            api_key="<NOTUSED>",
            base_url=f"{service_endpoint}/20231130/actions/v1",
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=DefaultAsyncHttpxClient(
                auth=auth,
                headers={
                    "CompartmentId": compartment_id,
                },
            ),
        )


class HttpxOciAuth(httpx.Auth):
    """
    Custom HTTPX authentication class that implements OCI request signing.

    This class handles the authentication flow for HTTPX requests by signing them
    using the OCI Signer, which adds the necessary authentication headers for OCI API calls.

    Attributes:
        signer (oci.signer.Signer): The OCI signer instance used for request signing
    """

    def __init__(self, signer: OciAuthSigner):
        self.signer = signer

    @override
    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        req = requests.Request(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            data=request.content,
        )
        prepared_request = req.prepare()

        # Sign the request using the OCI Signer
        self.signer.do_request_sign(prepared_request)  # type: ignore

        # Update the original HTTPX request with the signed headers
        request.headers.update(prepared_request.headers)

        yield request


class OciSessionAuth(HttpxOciAuth):
    """
    OCI authentication implementation using session-based authentication.

    This class implements OCI authentication using a session token and private key
    loaded from the OCI configuration file. It's suitable for interactive user sessions.

    Attributes:
        signer (oci.auth.signers.SecurityTokenSigner): OCI signer using session token
    """

    def __init__(self, config_file: str = DEFAULT_LOCATION, profile_name: str = DEFAULT_PROFILE):
        config = oci.config.from_file(config_file, profile_name)
        token = self._load_token(config)
        private_key = oci.signer.load_private_key_from_file(config["key_file"])  # type: ignore
        self.signer = oci.auth.signers.SecurityTokenSigner(token, private_key)

    def _load_token(self, config: Mapping[str, Any]) -> str:
        token_file = config["security_token_file"]
        with open(token_file, "r") as f:
            return f.read().strip()


class OciResourcePrincipleAuth(HttpxOciAuth):
    """
    OCI authentication implementation using Resource Principal authentication.

    This class implements OCI authentication using Resource Principal credentials,
    which is suitable for services running within OCI that need to access other OCI services.
    """

    def __init__(self):
        self.signer = oci.auth.signers.get_resource_principals_signer()  # type: ignore


class OciInstancePrincipleAuth(HttpxOciAuth):
    """
    OCI authentication implementation using Instance Principal authentication.

    This class implements OCI authentication using Instance Principal credentials,
    which is suitable for compute instances that need to access OCI services.
    """

    def __init__(self, **kwargs: Mapping[str, Any]):
        self.signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner(**kwargs)


class OciUserPrincipleAuth(HttpxOciAuth):
    """
    OCI authentication implementation using user principle authentication.

        This class implements OCI authentication using API Key credentials loaded from
    the OCI configuration file. It's suitable for programmatic access to OCI services.

    Attributes:
        signer (oci.signer.Signer): OCI signer configured with API key credentials
    """

    def __init__(self, config_file: str = DEFAULT_LOCATION, profile_name: str = DEFAULT_PROFILE):
        config = oci.config.from_file(config_file, profile_name)
        oci.config.validate_config(config)  # type: ignore

        self.signer = oci.signer.Signer(
            tenancy=config["tenancy"],
            user=config["user"],
            fingerprint=config["fingerprint"],
            private_key_file_location=config.get("key_file"),
            pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase"),  # type: ignore
            private_key_content=config.get("key_content"),
        )
