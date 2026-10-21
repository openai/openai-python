from __future__ import annotations

import os
import re
import inspect
import threading
from typing import TYPE_CHECKING, Any, Callable, Awaitable, cast
from dataclasses import field, dataclass
from typing_extensions import override

import anyio
import httpx2
import anyio.to_thread

from .._models import FinalRequestOptions
from .._provider import _Provider, _create_provider, _ProviderRuntime
from .._exceptions import OpenAIError, APITimeoutError

if TYPE_CHECKING:
    from google.auth.credentials import Credentials
else:
    # Keep runtime type introspection available without importing the optional dependency.
    Credentials = Any

VertexTokenProvider = Callable[[], str | Awaitable[str]]
_CLOUD_PLATFORM_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)


@dataclass(frozen=True)
class _VertexDefinition:
    base_url: httpx2.URL
    token_provider: VertexTokenProvider | None = field(repr=False)
    credentials: Credentials | None = field(repr=False)
    name: str = field(default="vertex", init=False)

    def configure(self) -> _ProviderRuntime:
        # ADC discovery/refresh belongs to this client. google-auth caches until expiry.
        lock = threading.Lock()
        credentials: Credentials | None = None

        def adc_headers(request: httpx2.Request) -> dict[str, str]:
            nonlocal credentials
            limits = request.extensions.get("timeout", {})
            pool_timeout = limits.get("pool")
            acquired = lock.acquire() if pool_timeout is None else lock.acquire(timeout=max(0, pool_timeout))
            if not acquired:
                raise APITimeoutError(request=request)
            try:
                try:
                    import requests
                    import google.auth
                    import google.auth.credentials
                    from google.auth.exceptions import TransportError
                    from google.auth.transport.requests import Request
                except ImportError as exc:
                    raise OpenAIError(
                        "Install openai[vertex] to use Google credentials, or supply token_provider."
                    ) from exc
                # No retained Session: client close/cancellation never leaves a Google transport open.
                with requests.Session() as session:

                    class BoundedRequest(Request):
                        @override
                        def __call__(self, *args: Any, **kwargs: Any) -> Any:
                            # Requests accepts separate connect/read limits, including None.
                            kwargs["timeout"] = (limits.get("connect"), limits.get("read"))
                            try:
                                return super().__call__(*args, **kwargs)  # type: ignore[no-untyped-call]
                            except TransportError as exc:
                                if isinstance(exc.__cause__, requests.exceptions.Timeout):
                                    raise APITimeoutError(request=request) from None
                                raise

                    bounded_transport = BoundedRequest(session)
                    if credentials is None:
                        if self.credentials is None:
                            # google-auth does not type its request or returned credentials.
                            discover = cast(
                                "Callable[..., tuple[Credentials, str | None]]", cast(Any, google.auth).default
                            )
                            credentials, _ = discover(scopes=_CLOUD_PLATFORM_SCOPES, request=bounded_transport)
                        else:
                            scope_credentials = cast(
                                "Callable[..., Credentials]", cast(Any, google.auth.credentials).with_scopes_if_required
                            )
                            credentials = scope_credentials(self.credentials, scopes=_CLOUD_PLATFORM_SCOPES)
                    headers: dict[str, str] = {}
                    credentials.before_request(bounded_transport, request.method, str(request.url), headers)  # type: ignore[no-untyped-call]
                    return headers
            except (OpenAIError, APITimeoutError):
                raise
            except Exception:
                # Credential exceptions can include request bodies or private keys.
                raise OpenAIError(
                    "Vertex Google authentication failed. Check ADC, project access and credential expiry."
                ) from None
            finally:
                lock.release()

        def transform(options: FinalRequestOptions) -> FinalRequestOptions:
            # Prevent even a user-configured http client from following redirects with credentials.
            options.follow_redirects = False
            return options

        def prepare(request: httpx2.Request) -> None:
            origin = (request.url.scheme, request.url.host, request.url.port)
            configured = (self.base_url.scheme, self.base_url.host, self.base_url.port)
            if origin != configured:
                raise OpenAIError("Refusing to send Vertex credentials outside the configured origin.")
            if any(
                header in request.headers
                for header in ("authorization", "api-key", "openai-organization", "openai-project")
            ):
                raise OpenAIError(
                    "Vertex owns authentication; remove OpenAI project/organization and custom Authorization or api-key headers."
                )

        def set_token(request: httpx2.Request, token: object) -> None:
            if not isinstance(token, str) or not token.strip() or any(ord(c) < 33 or ord(c) > 126 for c in token):
                raise OpenAIError(
                    "Vertex token provider must return a nonempty bearer token suitable for an HTTP header."
                )
            request.headers["Authorization"] = f"Bearer {token}"

        def prepare_sync(request: httpx2.Request) -> None:
            prepare(request)
            if self.token_provider is None:
                request.headers.update(adc_headers(request))
            else:
                try:
                    token = self.token_provider()
                except Exception:
                    raise OpenAIError("Vertex token provider failed.") from None
                if inspect.isawaitable(token):
                    if inspect.iscoroutine(token):
                        token.close()
                    raise OpenAIError("Use AsyncOpenAI with an async Vertex token provider.")
                set_token(request, token)

        async def prepare_async(request: httpx2.Request) -> None:
            prepare(request)
            try:
                if self.token_provider is None:
                    headers = await anyio.to_thread.run_sync(adc_headers, request, abandon_on_cancel=True)
                    request.headers.update(headers)
                else:
                    with anyio.fail_after(request.extensions.get("timeout", {}).get("read")) as scope:
                        token = self.token_provider()
                        if inspect.isawaitable(token):
                            token = await token
                        # Blocking callbacks cannot be interrupted by an async cancel scope.
                        if anyio.current_time() >= scope.deadline:
                            raise APITimeoutError(request=request)
                        set_token(request, token)
            except TimeoutError:
                raise APITimeoutError(request=request) from None
            except OpenAIError:
                raise
            except Exception:
                raise OpenAIError("Vertex token provider failed.") from None

        return _ProviderRuntime(
            name=self.name,
            base_url=self.base_url,
            transform_request=transform,
            prepare_request=prepare_sync,
            prepare_async_request=prepare_async,
        )


def vertex(
    *,
    project: str | None = None,
    location: str | None = None,
    base_url: str | httpx2.URL | None = None,
    token_provider: VertexTokenProvider | None = None,
    credentials: Credentials | None = None,
) -> _Provider:
    """Configure normal OpenAI Responses calls for Vertex. ADC is lazy and requires openai[vertex].

    Project and location fall back to GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION.
    An explicit base_url is the complete API root before /responses and takes precedence.
    On AsyncOpenAI, token_provider runs on the event loop and must not block it.
    """
    if token_provider is not None and credentials is not None:
        raise OpenAIError("Set only one of credentials and token_provider.")
    if base_url is None:
        project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = location or os.environ.get("GOOGLE_CLOUD_LOCATION")
        # Legacy domain-scoped projects include dots and a colon; exclude dot path segments.
        if not project or not re.fullmatch(r"[a-zA-Z0-9_-][a-zA-Z0-9_.:-]*", project):
            raise OpenAIError("Vertex requires a project ID (project or GOOGLE_CLOUD_PROJECT).")
        if not location or not re.fullmatch(r"[a-z0-9-]+", location):
            raise OpenAIError("Vertex requires a location (location or GOOGLE_CLOUD_LOCATION).")
        host = "aiplatform.googleapis.com" if location == "global" else f"{location}-aiplatform.googleapis.com"
        base_url = f"https://{host}/v1/projects/{project}/locations/{location}/publishers/openai/v1"
    url = httpx2.URL(base_url)
    if url.scheme not in ("http", "https") or not url.host or url.username or url.password or url.query or url.fragment:
        raise OpenAIError("Vertex base_url must be an HTTP(S) API root without credentials, query or fragment.")
    host = url.host.rstrip(".")
    if url.scheme != "https" and (host == "googleapis.com" or host.endswith(".googleapis.com")):
        raise OpenAIError("Google Vertex endpoints require HTTPS.")
    return _create_provider(_VertexDefinition(base_url=url, token_provider=token_provider, credentials=credentials))


__all__ = ["vertex", "VertexTokenProvider"]
