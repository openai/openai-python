# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    is_mapping,
    get_async_library,
)
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import OpenAIError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import (
        beta,
        chat,
        audio,
        evals,
        files,
        images,
        models,
        batches,
        uploads,
        responses,
        containers,
        embeddings,
        completions,
        fine_tuning,
        moderations,
        vector_stores,
    )
    from .resources.files import Files, AsyncFiles
    from .resources.images import Images, AsyncImages
    from .resources.models import Models, AsyncModels
    from .resources.batches import Batches, AsyncBatches
    from .resources.beta.beta import Beta, AsyncBeta
    from .resources.chat.chat import Chat, AsyncChat
    from .resources.embeddings import Embeddings, AsyncEmbeddings
    from .resources.audio.audio import Audio, AsyncAudio
    from .resources.completions import Completions, AsyncCompletions
    from .resources.evals.evals import Evals, AsyncEvals
    from .resources.moderations import Moderations, AsyncModerations
    from .resources.uploads.uploads import Uploads, AsyncUploads
    from .resources.responses.responses import Responses, AsyncResponses
    from .resources.containers.containers import Containers, AsyncContainers
    from .resources.fine_tuning.fine_tuning import FineTuning, AsyncFineTuning
    from .resources.vector_stores.vector_stores import VectorStores, AsyncVectorStores

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "OpenAI", "AsyncOpenAI", "Client", "AsyncClient"]


class OpenAI(SyncAPIClient):
    # client options
    api_key: str
    organization: str | None
    project: str | None

    websocket_base_url: str | httpx.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous OpenAI client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `OPENAI_API_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable"
            )
        self.api_key = api_key

        if organization is None:
            organization = os.environ.get("OPENAI_ORG_ID")
        self.organization = organization

        if project is None:
            project = os.environ.get("OPENAI_PROJECT_ID")
        self.project = project

        self.websocket_base_url = websocket_base_url

        if base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url is None:
            base_url = f"https://api.openai.com/v1"

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

    @cached_property
    def completions(self) -> Completions:
        from .resources.completions import Completions

        return Completions(self)

    @cached_property
    def chat(self) -> Chat:
        from .resources.chat import Chat

        return Chat(self)

    @cached_property
    def embeddings(self) -> Embeddings:
        from .resources.embeddings import Embeddings

        return Embeddings(self)

    @cached_property
    def files(self) -> Files:
        from .resources.files import Files

        return Files(self)

    @cached_property
    def images(self) -> Images:
        from .resources.images import Images

        return Images(self)

    @cached_property
    def audio(self) -> Audio:
        from .resources.audio import Audio

        return Audio(self)

    @cached_property
    def moderations(self) -> Moderations:
        from .resources.moderations import Moderations

        return Moderations(self)

    @cached_property
    def models(self) -> Models:
        from .resources.models import Models

        return Models(self)

    @cached_property
    def fine_tuning(self) -> FineTuning:
        from .resources.fine_tuning import FineTuning

        return FineTuning(self)

    @cached_property
    def vector_stores(self) -> VectorStores:
        from .resources.vector_stores import VectorStores

        return VectorStores(self)

    @cached_property
    def beta(self) -> Beta:
        from .resources.beta import Beta

        return Beta(self)

    @cached_property
    def batches(self) -> Batches:
        from .resources.batches import Batches

        return Batches(self)

    @cached_property
    def uploads(self) -> Uploads:
        from .resources.uploads import Uploads

        return Uploads(self)

    @cached_property
    def responses(self) -> Responses:
        from .resources.responses import Responses

        return Responses(self)

    @cached_property
    def evals(self) -> Evals:
        from .resources.evals import Evals

        return Evals(self)

    @cached_property
    def containers(self) -> Containers:
        from .resources.containers import Containers

        return Containers(self)

    @cached_property
    def with_raw_response(self) -> OpenAIWithRawResponse:
        return OpenAIWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAIWithStreamedResponse:
        return OpenAIWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            "OpenAI-Organization": self.organization if self.organization is not None else Omit(),
            "OpenAI-Project": self.project if self.project is not None else Omit(),
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
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
            project=project or self.project,
            websocket_base_url=websocket_base_url or self.websocket_base_url,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
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
        return APIStatusError(err_msg, response=response, body=data)


class AsyncOpenAI(AsyncAPIClient):
    # client options
    api_key: str
    organization: str | None
    project: str | None

    websocket_base_url: str | httpx.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncOpenAI client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `OPENAI_API_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable"
            )
        self.api_key = api_key

        if organization is None:
            organization = os.environ.get("OPENAI_ORG_ID")
        self.organization = organization

        if project is None:
            project = os.environ.get("OPENAI_PROJECT_ID")
        self.project = project

        self.websocket_base_url = websocket_base_url

        if base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url is None:
            base_url = f"https://api.openai.com/v1"

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

        self._default_stream_cls = AsyncStream

    @cached_property
    def completions(self) -> AsyncCompletions:
        from .resources.completions import AsyncCompletions

        return AsyncCompletions(self)

    @cached_property
    def chat(self) -> AsyncChat:
        from .resources.chat import AsyncChat

        return AsyncChat(self)

    @cached_property
    def embeddings(self) -> AsyncEmbeddings:
        from .resources.embeddings import AsyncEmbeddings

        return AsyncEmbeddings(self)

    @cached_property
    def files(self) -> AsyncFiles:
        from .resources.files import AsyncFiles

        return AsyncFiles(self)

    @cached_property
    def images(self) -> AsyncImages:
        from .resources.images import AsyncImages

        return AsyncImages(self)

    @cached_property
    def audio(self) -> AsyncAudio:
        from .resources.audio import AsyncAudio

        return AsyncAudio(self)

    @cached_property
    def moderations(self) -> AsyncModerations:
        from .resources.moderations import AsyncModerations

        return AsyncModerations(self)

    @cached_property
    def models(self) -> AsyncModels:
        from .resources.models import AsyncModels

        return AsyncModels(self)

    @cached_property
    def fine_tuning(self) -> AsyncFineTuning:
        from .resources.fine_tuning import AsyncFineTuning

        return AsyncFineTuning(self)

    @cached_property
    def vector_stores(self) -> AsyncVectorStores:
        from .resources.vector_stores import AsyncVectorStores

        return AsyncVectorStores(self)

    @cached_property
    def beta(self) -> AsyncBeta:
        from .resources.beta import AsyncBeta

        return AsyncBeta(self)

    @cached_property
    def batches(self) -> AsyncBatches:
        from .resources.batches import AsyncBatches

        return AsyncBatches(self)

    @cached_property
    def uploads(self) -> AsyncUploads:
        from .resources.uploads import AsyncUploads

        return AsyncUploads(self)

    @cached_property
    def responses(self) -> AsyncResponses:
        from .resources.responses import AsyncResponses

        return AsyncResponses(self)

    @cached_property
    def evals(self) -> AsyncEvals:
        from .resources.evals import AsyncEvals

        return AsyncEvals(self)

    @cached_property
    def containers(self) -> AsyncContainers:
        from .resources.containers import AsyncContainers

        return AsyncContainers(self)

    @cached_property
    def with_raw_response(self) -> AsyncOpenAIWithRawResponse:
        return AsyncOpenAIWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAIWithStreamedResponse:
        return AsyncOpenAIWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            "OpenAI-Organization": self.organization if self.organization is not None else Omit(),
            "OpenAI-Project": self.project if self.project is not None else Omit(),
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
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
            project=project or self.project,
            websocket_base_url=websocket_base_url or self.websocket_base_url,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
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
        return APIStatusError(err_msg, response=response, body=data)


class OpenAIWithRawResponse:
    _client: OpenAI

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    @cached_property
    def completions(self) -> completions.CompletionsWithRawResponse:
        from .resources.completions import CompletionsWithRawResponse

        return CompletionsWithRawResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.ChatWithRawResponse:
        from .resources.chat import ChatWithRawResponse

        return ChatWithRawResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsWithRawResponse:
        from .resources.embeddings import EmbeddingsWithRawResponse

        return EmbeddingsWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.FilesWithRawResponse:
        from .resources.files import FilesWithRawResponse

        return FilesWithRawResponse(self._client.files)

    @cached_property
    def images(self) -> images.ImagesWithRawResponse:
        from .resources.images import ImagesWithRawResponse

        return ImagesWithRawResponse(self._client.images)

    @cached_property
    def audio(self) -> audio.AudioWithRawResponse:
        from .resources.audio import AudioWithRawResponse

        return AudioWithRawResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.ModerationsWithRawResponse:
        from .resources.moderations import ModerationsWithRawResponse

        return ModerationsWithRawResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.ModelsWithRawResponse:
        from .resources.models import ModelsWithRawResponse

        return ModelsWithRawResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.FineTuningWithRawResponse:
        from .resources.fine_tuning import FineTuningWithRawResponse

        return FineTuningWithRawResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.VectorStoresWithRawResponse:
        from .resources.vector_stores import VectorStoresWithRawResponse

        return VectorStoresWithRawResponse(self._client.vector_stores)

    @cached_property
    def beta(self) -> beta.BetaWithRawResponse:
        from .resources.beta import BetaWithRawResponse

        return BetaWithRawResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.BatchesWithRawResponse:
        from .resources.batches import BatchesWithRawResponse

        return BatchesWithRawResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.UploadsWithRawResponse:
        from .resources.uploads import UploadsWithRawResponse

        return UploadsWithRawResponse(self._client.uploads)

    @cached_property
    def responses(self) -> responses.ResponsesWithRawResponse:
        from .resources.responses import ResponsesWithRawResponse

        return ResponsesWithRawResponse(self._client.responses)

    @cached_property
    def evals(self) -> evals.EvalsWithRawResponse:
        from .resources.evals import EvalsWithRawResponse

        return EvalsWithRawResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.ContainersWithRawResponse:
        from .resources.containers import ContainersWithRawResponse

        return ContainersWithRawResponse(self._client.containers)


class AsyncOpenAIWithRawResponse:
    _client: AsyncOpenAI

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client

    @cached_property
    def completions(self) -> completions.AsyncCompletionsWithRawResponse:
        from .resources.completions import AsyncCompletionsWithRawResponse

        return AsyncCompletionsWithRawResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.AsyncChatWithRawResponse:
        from .resources.chat import AsyncChatWithRawResponse

        return AsyncChatWithRawResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsWithRawResponse:
        from .resources.embeddings import AsyncEmbeddingsWithRawResponse

        return AsyncEmbeddingsWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.AsyncFilesWithRawResponse:
        from .resources.files import AsyncFilesWithRawResponse

        return AsyncFilesWithRawResponse(self._client.files)

    @cached_property
    def images(self) -> images.AsyncImagesWithRawResponse:
        from .resources.images import AsyncImagesWithRawResponse

        return AsyncImagesWithRawResponse(self._client.images)

    @cached_property
    def audio(self) -> audio.AsyncAudioWithRawResponse:
        from .resources.audio import AsyncAudioWithRawResponse

        return AsyncAudioWithRawResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.AsyncModerationsWithRawResponse:
        from .resources.moderations import AsyncModerationsWithRawResponse

        return AsyncModerationsWithRawResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.AsyncModelsWithRawResponse:
        from .resources.models import AsyncModelsWithRawResponse

        return AsyncModelsWithRawResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.AsyncFineTuningWithRawResponse:
        from .resources.fine_tuning import AsyncFineTuningWithRawResponse

        return AsyncFineTuningWithRawResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.AsyncVectorStoresWithRawResponse:
        from .resources.vector_stores import AsyncVectorStoresWithRawResponse

        return AsyncVectorStoresWithRawResponse(self._client.vector_stores)

    @cached_property
    def beta(self) -> beta.AsyncBetaWithRawResponse:
        from .resources.beta import AsyncBetaWithRawResponse

        return AsyncBetaWithRawResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.AsyncBatchesWithRawResponse:
        from .resources.batches import AsyncBatchesWithRawResponse

        return AsyncBatchesWithRawResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.AsyncUploadsWithRawResponse:
        from .resources.uploads import AsyncUploadsWithRawResponse

        return AsyncUploadsWithRawResponse(self._client.uploads)

    @cached_property
    def responses(self) -> responses.AsyncResponsesWithRawResponse:
        from .resources.responses import AsyncResponsesWithRawResponse

        return AsyncResponsesWithRawResponse(self._client.responses)

    @cached_property
    def evals(self) -> evals.AsyncEvalsWithRawResponse:
        from .resources.evals import AsyncEvalsWithRawResponse

        return AsyncEvalsWithRawResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.AsyncContainersWithRawResponse:
        from .resources.containers import AsyncContainersWithRawResponse

        return AsyncContainersWithRawResponse(self._client.containers)


class OpenAIWithStreamedResponse:
    _client: OpenAI

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    @cached_property
    def completions(self) -> completions.CompletionsWithStreamingResponse:
        from .resources.completions import CompletionsWithStreamingResponse

        return CompletionsWithStreamingResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.ChatWithStreamingResponse:
        from .resources.chat import ChatWithStreamingResponse

        return ChatWithStreamingResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsWithStreamingResponse:
        from .resources.embeddings import EmbeddingsWithStreamingResponse

        return EmbeddingsWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.FilesWithStreamingResponse:
        from .resources.files import FilesWithStreamingResponse

        return FilesWithStreamingResponse(self._client.files)

    @cached_property
    def images(self) -> images.ImagesWithStreamingResponse:
        from .resources.images import ImagesWithStreamingResponse

        return ImagesWithStreamingResponse(self._client.images)

    @cached_property
    def audio(self) -> audio.AudioWithStreamingResponse:
        from .resources.audio import AudioWithStreamingResponse

        return AudioWithStreamingResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.ModerationsWithStreamingResponse:
        from .resources.moderations import ModerationsWithStreamingResponse

        return ModerationsWithStreamingResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.ModelsWithStreamingResponse:
        from .resources.models import ModelsWithStreamingResponse

        return ModelsWithStreamingResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.FineTuningWithStreamingResponse:
        from .resources.fine_tuning import FineTuningWithStreamingResponse

        return FineTuningWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.VectorStoresWithStreamingResponse:
        from .resources.vector_stores import VectorStoresWithStreamingResponse

        return VectorStoresWithStreamingResponse(self._client.vector_stores)

    @cached_property
    def beta(self) -> beta.BetaWithStreamingResponse:
        from .resources.beta import BetaWithStreamingResponse

        return BetaWithStreamingResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.BatchesWithStreamingResponse:
        from .resources.batches import BatchesWithStreamingResponse

        return BatchesWithStreamingResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.UploadsWithStreamingResponse:
        from .resources.uploads import UploadsWithStreamingResponse

        return UploadsWithStreamingResponse(self._client.uploads)

    @cached_property
    def responses(self) -> responses.ResponsesWithStreamingResponse:
        from .resources.responses import ResponsesWithStreamingResponse

        return ResponsesWithStreamingResponse(self._client.responses)

    @cached_property
    def evals(self) -> evals.EvalsWithStreamingResponse:
        from .resources.evals import EvalsWithStreamingResponse

        return EvalsWithStreamingResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.ContainersWithStreamingResponse:
        from .resources.containers import ContainersWithStreamingResponse

        return ContainersWithStreamingResponse(self._client.containers)


class AsyncOpenAIWithStreamedResponse:
    _client: AsyncOpenAI

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client

    @cached_property
    def completions(self) -> completions.AsyncCompletionsWithStreamingResponse:
        from .resources.completions import AsyncCompletionsWithStreamingResponse

        return AsyncCompletionsWithStreamingResponse(self._client.completions)

    @cached_property
    def chat(self) -> chat.AsyncChatWithStreamingResponse:
        from .resources.chat import AsyncChatWithStreamingResponse

        return AsyncChatWithStreamingResponse(self._client.chat)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsWithStreamingResponse:
        from .resources.embeddings import AsyncEmbeddingsWithStreamingResponse

        return AsyncEmbeddingsWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.AsyncFilesWithStreamingResponse:
        from .resources.files import AsyncFilesWithStreamingResponse

        return AsyncFilesWithStreamingResponse(self._client.files)

    @cached_property
    def images(self) -> images.AsyncImagesWithStreamingResponse:
        from .resources.images import AsyncImagesWithStreamingResponse

        return AsyncImagesWithStreamingResponse(self._client.images)

    @cached_property
    def audio(self) -> audio.AsyncAudioWithStreamingResponse:
        from .resources.audio import AsyncAudioWithStreamingResponse

        return AsyncAudioWithStreamingResponse(self._client.audio)

    @cached_property
    def moderations(self) -> moderations.AsyncModerationsWithStreamingResponse:
        from .resources.moderations import AsyncModerationsWithStreamingResponse

        return AsyncModerationsWithStreamingResponse(self._client.moderations)

    @cached_property
    def models(self) -> models.AsyncModelsWithStreamingResponse:
        from .resources.models import AsyncModelsWithStreamingResponse

        return AsyncModelsWithStreamingResponse(self._client.models)

    @cached_property
    def fine_tuning(self) -> fine_tuning.AsyncFineTuningWithStreamingResponse:
        from .resources.fine_tuning import AsyncFineTuningWithStreamingResponse

        return AsyncFineTuningWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def vector_stores(self) -> vector_stores.AsyncVectorStoresWithStreamingResponse:
        from .resources.vector_stores import AsyncVectorStoresWithStreamingResponse

        return AsyncVectorStoresWithStreamingResponse(self._client.vector_stores)

    @cached_property
    def beta(self) -> beta.AsyncBetaWithStreamingResponse:
        from .resources.beta import AsyncBetaWithStreamingResponse

        return AsyncBetaWithStreamingResponse(self._client.beta)

    @cached_property
    def batches(self) -> batches.AsyncBatchesWithStreamingResponse:
        from .resources.batches import AsyncBatchesWithStreamingResponse

        return AsyncBatchesWithStreamingResponse(self._client.batches)

    @cached_property
    def uploads(self) -> uploads.AsyncUploadsWithStreamingResponse:
        from .resources.uploads import AsyncUploadsWithStreamingResponse

        return AsyncUploadsWithStreamingResponse(self._client.uploads)

    @cached_property
    def responses(self) -> responses.AsyncResponsesWithStreamingResponse:
        from .resources.responses import AsyncResponsesWithStreamingResponse

        return AsyncResponsesWithStreamingResponse(self._client.responses)

    @cached_property
    def evals(self) -> evals.AsyncEvalsWithStreamingResponse:
        from .resources.evals import AsyncEvalsWithStreamingResponse

        return AsyncEvalsWithStreamingResponse(self._client.evals)

    @cached_property
    def containers(self) -> containers.AsyncContainersWithStreamingResponse:
        from .resources.containers import AsyncContainersWithStreamingResponse

        return AsyncContainersWithStreamingResponse(self._client.containers)


Client = OpenAI

AsyncClient = AsyncOpenAI
