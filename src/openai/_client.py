from __future__ import annotations
import os
import asyncio
from typing import Union, Mapping
import httpx

from . import resources, _exceptions
from ._qs import Querystring
from ._types import NOT_GIVEN, Omit, Timeout, NotGiven, Transport, ProxiesTypes, RequestOptions
from ._utils import is_given, is_mapping
from ._version import __version__
from ._streaming import Stream as Stream
from ._streaming import AsyncStream as AsyncStream
from ._exceptions import OpenAIError, APIStatusError
from ._base_client import DEFAULT_MAX_RETRIES, SyncAPIClient, AsyncAPIClient

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "resources", "OpenAI", "AsyncOpenAI", "Client", "AsyncClient"]


class OpenAI(SyncAPIClient):
    completions, chat, edits, embeddings, files, images, audio, moderations, models, fine_tuning, fine_tunes, beta, with_raw_response = (
        resources.Completions,
        resources.Chat,
        resources.Edits,
        resources.Embeddings,
        resources.Files,
        resources.Images,
        resources.Audio,
        resources.Moderations,
        resources.Models,
        resources.FineTuning,
        resources.FineTunes,
        resources.Beta,
        OpenAIWithRawResponse,
    )

    api_key: str
    organization: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise OpenAIError("API key must be provided or set in the OPENAI_API_KEY environment variable")
        self.api_key = api_key

        if organization is None:
            organization = os.environ.get("OPENAI_ORG_ID")
        self.organization = organization

        base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

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

        self._default_stream_cls = Stream
        self._initialize_resources()

    def _initialize_resources(self) -> None:
        for resource in (
            "completions", "chat", "edits", "embeddings", "files", "images", "audio",
            "moderations", "models", "fine_tuning", "fine_tunes", "beta", "with_raw_response"
        ):
            setattr(self, resource, getattr(resources, resource)(self))

    @property
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    @property
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "OpenAI-Organization": self.organization if self.organization is not None else Omit(),
            **self._custom_headers,
        }

    def copy(
        self,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
    ) -> OpenAI:
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            organization=organization or self.organization,
            base_url=base_url or str(self.base_url),
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
        )

    with_options = copy

    def __del__(self) -> None:
        if not hasattr(self, "_has_custom_http_client") or not hasattr(self, "close"):
            return

        if self._has_custom_http_client:
            return

        self.close()

    def _make_status_error(
        self,
        err_msg: str,
        body: object,
        response: httpx.Response,
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
        return APIStatusError(err_msg, response=response,
