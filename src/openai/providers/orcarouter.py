from __future__ import annotations

import os
import inspect
from typing import Callable, Awaitable, cast
from dataclasses import field, dataclass

import httpx2

from .._types import NOT_GIVEN, NotGiven
from .._httpx2 import normalize_httpx_url
from .._provider import _Provider, _create_provider, _ProviderRuntime
from .._exceptions import OpenAIError

OrcaRouterTokenProvider = Callable[[], "str | Awaitable[str]"]

_ORCAROUTER_BASE_URL = "https://api.orcarouter.ai/v1"


def _normalize_base_url(base_url: str | httpx2.URL) -> httpx2.URL:
    return normalize_httpx_url(base_url)


def _same_origin(left: httpx2.URL, right: httpx2.URL) -> bool:
    return (left.scheme, left.host, left.port) == (right.scheme, right.host, right.port)


def _assert_provider_owns_authorization(request: httpx2.Request) -> None:
    if "Authorization" in request.headers:
        raise OpenAIError("OrcaRouter provider authentication cannot be combined with a custom `Authorization` header.")


class _OrcaRouterBearerAuth:
    def __init__(self, token_provider: OrcaRouterTokenProvider, *, base_url: httpx2.URL) -> None:
        self._token_provider = token_provider
        self._base_url = base_url

    def _validate_request(self, request: httpx2.Request) -> None:
        _assert_provider_owns_authorization(request)
        if not _same_origin(request.url, self._base_url):
            raise OpenAIError(
                "Refusing to authenticate an OrcaRouter request for an origin other than the configured provider URL."
            )

    def _resolve_token(self) -> str:
        try:
            token = cast(object, self._token_provider())
        except OpenAIError:
            raise
        except Exception as exc:
            raise OpenAIError("Failed to resolve a bearer credential for OrcaRouter.") from exc

        if inspect.isawaitable(token):
            close = getattr(token, "close", None)
            if callable(close):
                close()
            raise OpenAIError("An async OrcaRouter token provider requires `AsyncOpenAI`.")
        if not isinstance(token, str) or not token.strip():
            raise OpenAIError("The OrcaRouter bearer credential provider must return a non-empty string.")
        return token

    async def _resolve_token_async(self) -> str:
        try:
            token = cast(object, self._token_provider())
            if inspect.isawaitable(token):
                token = await token
        except OpenAIError:
            raise
        except Exception as exc:
            raise OpenAIError("Failed to resolve a bearer credential for OrcaRouter.") from exc

        if not isinstance(token, str) or not token.strip():
            raise OpenAIError("The OrcaRouter bearer credential provider must return a non-empty string.")
        return token

    def prepare_request(self, request: httpx2.Request) -> None:
        self._validate_request(request)
        request.headers["Authorization"] = f"Bearer {self._resolve_token()}"

    async def prepare_async_request(self, request: httpx2.Request) -> None:
        self._validate_request(request)
        request.headers["Authorization"] = f"Bearer {await self._resolve_token_async()}"


@dataclass(frozen=True)
class _OrcaRouterProviderDefinition:
    configured_base_url: httpx2.URL | None
    api_key: str | None = field(default=None, repr=False)
    token_provider: OrcaRouterTokenProvider | None = field(default=None, repr=False, compare=False)
    use_environment_key: bool = False
    name: str = field(default="orcarouter", init=False)

    def configure(self) -> _ProviderRuntime:
        def environment_key() -> str:
            token = os.environ.get("ORCAROUTER_API_KEY")
            if not token:
                raise OpenAIError(
                    "Could not find credentials for OrcaRouter. Pass `api_key` to `orcarouter(...)`, "
                    "provide a `token_provider`, or set the `ORCAROUTER_API_KEY` environment variable."
                )
            return token

        if self.api_key is not None:
            bearer_provider: OrcaRouterTokenProvider = lambda: cast(str, self.api_key)
        elif self.token_provider is not None:
            bearer_provider = self.token_provider
        elif self.use_environment_key:
            if not os.environ.get("ORCAROUTER_API_KEY"):
                raise OpenAIError(
                    "Could not find credentials for OrcaRouter. Pass `api_key` to `orcarouter(...)`, "
                    "provide a `token_provider`, or set the `ORCAROUTER_API_KEY` environment variable."
                )
            bearer_provider = environment_key
        else:
            raise OpenAIError(
                "Could not find credentials for OrcaRouter. Pass `api_key` to `orcarouter(...)`, "
                "provide a `token_provider`, or set the `ORCAROUTER_API_KEY` environment variable."
            )

        base_url = self.configured_base_url or httpx2.URL(_ORCAROUTER_BASE_URL)
        auth = _OrcaRouterBearerAuth(bearer_provider, base_url=base_url)

        return _ProviderRuntime(
            name=self.name,
            base_url=base_url,
            prepare_request=auth.prepare_request,
            prepare_async_request=auth.prepare_async_request,
        )


def orcarouter(
    *,
    base_url: str | httpx2.URL | None | NotGiven = NOT_GIVEN,
    api_key: str | None | NotGiven = NOT_GIVEN,
    token_provider: OrcaRouterTokenProvider | None = None,
) -> _Provider:
    """Configure the standard OpenAI client for OrcaRouter.

    OrcaRouter is an OpenAI-compatible model routing gateway. It exposes
    OpenAI, Anthropic, Google, and other models behind a single endpoint,
    alongside named routers such as ``orcarouter/auto``.

    By default the provider reads the API key from the ``ORCAROUTER_API_KEY``
    environment variable and uses the ``https://api.orcarouter.ai/v1``
    endpoint. Pass ``base_url`` to ``orcarouter(...)`` or set
    ``ORCAROUTER_BASE_URL`` to override it.
    """

    explicit_api_key = not isinstance(api_key, NotGiven) and api_key is not None
    if explicit_api_key and (not isinstance(api_key, str) or not api_key.strip()):
        raise OpenAIError("The OrcaRouter API key must not be empty.")
    if explicit_api_key and token_provider is not None:
        raise OpenAIError("The `api_key` and `token_provider` options are mutually exclusive. Configure only one.")

    skip_environment_key = not isinstance(api_key, NotGiven) and api_key is None

    configured_base_url: httpx2.URL | None
    if isinstance(base_url, NotGiven):
        environment_base_url = os.environ.get("ORCAROUTER_BASE_URL")
        configured_base_url = _normalize_base_url(environment_base_url) if environment_base_url else None
    elif base_url is None:
        configured_base_url = None
    else:
        if isinstance(base_url, str) and not base_url.strip():
            raise OpenAIError("The OrcaRouter `base_url` must not be empty.")
        configured_base_url = _normalize_base_url(base_url)

    use_environment_key = not explicit_api_key and not skip_environment_key

    return _create_provider(
        _OrcaRouterProviderDefinition(
            configured_base_url=configured_base_url,
            api_key=cast("str | None", api_key) if explicit_api_key else None,
            token_provider=token_provider,
            use_environment_key=use_environment_key,
        )
    )


__all__ = ["orcarouter", "OrcaRouterTokenProvider"]
