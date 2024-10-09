# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.
from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

import asyncio
from typing import List, Dict, Any
import logging

from . import resources, _exceptions
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
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import OpenAIError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "resources",
    "OpenAI",
    "AsyncOpenAI",
    "Client",
    "AsyncClient",
]

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OpenAI(SyncAPIClient):
    completions: resources.Completions
    chat: resources.Chat
    embeddings: resources.Embeddings
    files: resources.Files
    images: resources.Images
    audio: resources.Audio
    moderations: resources.Moderations
    models: resources.Models
    fine_tuning: resources.FineTuning
    beta: resources.Beta
    batches: resources.Batches
    uploads: resources.Uploads
    with_raw_response: OpenAIWithRawResponse
    with_streaming_response: OpenAIWithStreamedResponse

    # client options
    api_key: str
    organization: str | None
    project: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
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
        """Construct a new synchronous openai client instance.

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

        self.completions = resources.Completions(self)
        self.chat = resources.Chat(self)
        self.embeddings = resources.Embeddings(self)
        self.files = resources.Files(self)
        self.images = resources.Images(self)
        self.audio = resources.Audio(self)
        self.moderations = resources.Moderations(self)
        self.models = resources.Models(self)
        self.fine_tuning = resources.FineTuning(self)
        self.beta = resources.Beta(self)
        self.batches = resources.Batches(self)
        self.uploads = resources.Uploads(self)
        self.with_raw_response = OpenAIWithRawResponse(self)
        self.with_streaming_response = OpenAIWithStreamedResponse(self)

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
    completions: resources.AsyncCompletions
    chat: resources.AsyncChat
    embeddings: resources.AsyncEmbeddings
    files: resources.AsyncFiles
    images: resources.AsyncImages
    audio: resources.AsyncAudio
    moderations: resources.AsyncModerations
    models: resources.AsyncModels
    fine_tuning: resources.AsyncFineTuning
    beta: resources.AsyncBeta
    batches: resources.AsyncBatches
    uploads: resources.AsyncUploads
    with_raw_response: AsyncOpenAIWithRawResponse
    with_streaming_response: AsyncOpenAIWithStreamedResponse

    # client options
    api_key: str
    organization: str | None
    project: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
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
        """Construct a new async openai client instance.

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

        self.completions = resources.AsyncCompletions(self)
        self.chat = resources.AsyncChat(self)
        self.embeddings = resources.AsyncEmbeddings(self)
        self.files = resources.AsyncFiles(self)
        self.images = resources.AsyncImages(self)
        self.audio = resources.AsyncAudio(self)
        self.moderations = resources.AsyncModerations(self)
        self.models = resources.AsyncModels(self)
        self.fine_tuning = resources.AsyncFineTuning(self)
        self.beta = resources.AsyncBeta(self)
        self.batches = resources.AsyncBatches(self)
        self.uploads = resources.AsyncUploads(self)
        self.with_raw_response = AsyncOpenAIWithRawResponse(self)
        self.with_streaming_response = AsyncOpenAIWithStreamedResponse(self)

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

    # Start Aynsc #
    async def acreate_completions(self, prompts: List[str], model: str, max_tokens: int, batch_size: int) -> List[str]:
        try:
            logger.debug(f"Creating batch completions for {len(prompts)} prompts.")
            results: List[str] = await self._batch_request(  # Specify the type of results
                self._async_completions_task,
                items=prompts,
                model=model,
                max_tokens=max_tokens,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during completions request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during completions request: {e}")
            raise

    async def acreate_chat(self, messages: List[Dict[str, Any]], model: str, max_tokens: int, batch_size: int) -> List[str]:
        try:
            logger.debug(f"Creating batch chat completions for {len(messages)} messages.")
            results: List[str] = await self._batch_request(  # Specify the type of results
                self._async_chat_task,
                items=messages,
                model=model,
                max_tokens=max_tokens,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during chat request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during chat request: {e}")
            raise

    async def _async_completions_task(self, prompt: str, model: str, max_tokens: int):
        try:
            logger.debug(f"Requesting completions for prompt: {prompt}")
            response = await self.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens
            )
            return response.choices[0].text.strip()
        except OpenAIError as e:
            logger.error(f"OpenAI API error for completions task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in completions task: {e}")
            raise

    async def _async_chat_task(self, message: Any, model: str, max_tokens: int) -> str:
        try:
            logger.debug(f"Requesting chat completions for message: {message['content']}")
            response: Any = await self.chat.create( # type: ignore
                model=model,
                messages=[message],
                max_tokens=max_tokens
            )
            return response.choices[0].message["content"].strip()
        except OpenAIError as e:
            logger.error(f"OpenAI API error for chat task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat task: {e}")
            raise

        # Embeddings Section #
    async def acreate_embeddings(self, inputs: List[str], model: str, batch_size: int) -> List[dict]: # type: ignore
        try:
            logger.debug(f"Creating embeddings for {len(inputs)} inputs.")
            results = await self._batch_request(
                self._async_embeddings_task, # type: ignore
                items=inputs,
                model=model,
                max_tokens=None,  # Embeddings don't use tokens, adjust appropriately
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during embeddings request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during embeddings request: {e}")
            raise

    async def _async_embeddings_task(self, input_text: str, model: str, *_):
        try:
            response = await self.embeddings.create(
                model=model,
                input=input_text
            )
            return response['data']  # Return embedding results
        except OpenAIError as e:
            logger.error(f"OpenAI API error for embeddings task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in embeddings task: {e}")
            raise
    # End Embeddings Section #

        # Files Section #
    async def aupload_files(self, file_paths: List[str], purpose: str, batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Uploading {len(file_paths)} files.")
            results = await self._batch_request(
                self._async_upload_task,
                items=file_paths,
                model=purpose,  # Purpose acts as the model equivalent here
                max_tokens=None,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file upload: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise

    async def _async_upload_task(self, file_path: str, purpose: str, *_):
        try:
            with open(file_path, 'rb') as file:
                response = await self.files.create(
                    file=file,
                    purpose=purpose
                )
            return response
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file upload task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in file upload task: {e}")
            raise
    # End Files Section #

        # Images Section #
    async def agenerate_images(self, prompts: List[str], model: str, n: int, batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Generating images for {len(prompts)} prompts.")
            results = await self._batch_request(
                self._async_image_task,
                items=prompts,
                model=model,
                max_tokens=None,  # Image generation does not depend on tokens
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during image generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during image generation: {e}")
            raise

    async def _async_image_task(self, prompt: str, model: str, *_):
        try:
            response = await self.images.create(
                model=model,
                prompt=prompt,
                n=1
            )
            return response['data']  # Return generated image data
        except OpenAIError as e:
            logger.error(f"OpenAI API error during image generation task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in image generation task: {e}")
            raise
    # End Images Section #

        # Audio Section #
    async def atranscribe_audio(self, audio_files: List[str], model: str, batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Transcribing {len(audio_files)} audio files.")
            results = await self._batch_request(
                self._async_audio_task,
                items=audio_files,
                model=model,
                max_tokens=None,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during audio transcription: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during audio transcription: {e}")
            raise

    async def _async_audio_task(self, audio_file: str, model: str, *_):
        try:
            with open(audio_file, 'rb') as file:
                response = await self.audio.transcribe(
                    model=model,
                    file=file
                )
            return response['text']  # Return the transcribed text
        except OpenAIError as e:
            logger.error(f"OpenAI API error during audio transcription task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in audio transcription task: {e}")
            raise
    # End Audio Section #

    # Moderations Section #
    async def acheck_moderation(self, inputs: List[str], model: str, batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Checking moderation for {len(inputs)} inputs.")
            results = await self._batch_request(
                self._async_moderation_task,
                items=inputs,
                model=model,
                max_tokens=None,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during moderation check: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during moderation check: {e}")
            raise

    async def _async_moderation_task(self, input_text: str, model: str, *_):
        try:
            response = await self.moderations.create(
                input=input_text
            )
            return response['results']  # Return moderation results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during moderation task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in moderation task: {e}")
            raise
    # End Moderations Section #

        # Models Section #
    async def alist_models(self, batch_size: int) -> List[dict]:
        try:
            logger.debug("Listing all models.")
            response = await self._batch_request(
                self._async_list_models_task,
                items=[],
                model=None,
                max_tokens=None,
                batch_size=batch_size
            )
            return response  # Return the list of models
        except OpenAIError as e:
            logger.error(f"OpenAI API error during model listing: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during model listing: {e}")
            raise

    async def _async_list_models_task(self, *_):
        try:
            response = await self.models.list()
            return response['data']
        except OpenAIError as e:
            logger.error(f"OpenAI API error during model listing task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in model listing task: {e}")
            raise
    # End Models Section #

    # FineTuning Section #
    # Fine-tune multiple models in batches using _batch_request
    async def afine_tune_batch(self, fine_tune_requests: List[dict], batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Creating fine-tune jobs in batches of {batch_size}.")
            results: List[dict] = await self._batch_request(
                self._create_fine_tune_task,
                items=fine_tune_requests,
                model=None,  # Model is defined per fine-tune request
                max_tokens=None,  # Not used in fine-tune
                batch_size=batch_size
            )
            return results  # Return the combined results from batch fine-tuning
        except OpenAIError as e:
            logger.error(f"OpenAI API error during batch fine-tuning: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during batch fine-tuning: {e}")
            raise

    # Helper function to create individual fine-tune jobs
    async def _create_fine_tune_task(self, fine_tune_request: dict, *_):
        try:
            logger.debug(f"Fine-tuning model: {fine_tune_request['model']} with dataset: {fine_tune_request['dataset_id']}")
            response = await self.fine_tuning.create(
                model=fine_tune_request['model'],
                dataset=fine_tune_request['dataset_id'],
                hyperparams=fine_tune_request.get('hyperparams', {})
            )
            return response  # Return the fine-tuning job details
        except OpenAIError as e:
            logger.error(f"OpenAI API error during fine-tune task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during fine-tune task: {e}")
            raise

    # List fine-tune jobs using _batch_request if needed
    async def alist_fine_tune_jobs(self, batch_size: int = 1) -> List[dict]:
        try:
            logger.debug("Listing all fine-tune jobs in batches.")
            results: List[dict] = await self._batch_request(
                self._list_fine_tune_jobs_task,
                items=[{}],  # Just a placeholder list for batch handling
                model=None,
                max_tokens=None,
                batch_size=batch_size
            )
            return results[0]['data'] if results else []  # Return the list of fine-tune jobs
        except OpenAIError as e:
            logger.error(f"OpenAI API error during fine-tune job listing: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during fine-tune job listing: {e}")
            raise

    # Helper function to list all fine-tune jobs
    async def _list_fine_tune_jobs_task(self, *_):
        try:
            logger.debug("Listing all fine-tune jobs.")
            response = await self.fine_tuning.list()
            return response  # Return the list of fine-tune jobs
        except OpenAIError as e:
            logger.error(f"OpenAI API error during fine-tune job listing: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during fine-tune job listing: {e}")
            raise

    # Retrieve multiple fine-tune jobs using _batch_request
    async def aretrieve_fine_tune_jobs(self, fine_tune_ids: List[str], batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Retrieving fine-tune jobs in batches of {batch_size}.")
            results: List[dict] = await self._batch_request(
                self._retrieve_fine_tune_task,
                items=fine_tune_ids,
                model=None,
                max_tokens=None,
                batch_size=batch_size
            )
            return results  # Return the retrieved fine-tune job details
        except OpenAIError as e:
            logger.error(f"OpenAI API error during batch fine-tune job retrieval: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during batch fine-tune job retrieval: {e}")
            raise

    # Helper function to retrieve a single fine-tune job
    async def _retrieve_fine_tune_task(self, fine_tune_id: str, *_):
        try:
            logger.debug(f"Retrieving fine-tune job with ID: {fine_tune_id}")
            response = await self.fine_tuning.retrieve(fine_tune_id)
            return response  # Return the fine-tune job details
        except OpenAIError as e:
            logger.error(f"OpenAI API error during fine-tune job retrieval: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during fine-tune job retrieval: {e}")
            raise

    # Cancel multiple fine-tune jobs using _batch_request
    async def acancel_fine_tune_jobs(self, fine_tune_ids: List[str], batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Cancelling fine-tune jobs in batches of {batch_size}.")
            results: List[dict] = await self._batch_request(
                self._cancel_fine_tune_task,
                items=fine_tune_ids,
                model=None,
                max_tokens=None,
                batch_size=batch_size
            )
            return results  # Return the cancellation details
        except OpenAIError as e:
            logger.error(f"OpenAI API error during batch fine-tune job cancellation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during batch fine-tune job cancellation: {e}")
            raise

    # Helper function to cancel a single fine-tune job
    async def _cancel_fine_tune_task(self, fine_tune_id: str, *_):
        try:
            logger.debug(f"Cancelling fine-tune job with ID: {fine_tune_id}")
            response = await self.fine_tuning.cancel(fine_tune_id)
            return response  # Return the cancellation details
        except OpenAIError as e:
            logger.error(f"OpenAI API error during fine-tune job cancellation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during fine-tune job cancellation: {e}")
            raise

    # End FineTuning Section #

    # Beta Section #
    async def acreate_beta_feature(self, data: dict) -> dict:
        try:
            logger.debug("Requesting a beta feature.")
            response = await self.beta.create(data)
            return response  # Return the response of the beta feature request
        except OpenAIError as e:
            logger.error(f"OpenAI API error during beta feature request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during beta feature request: {e}")
            raise
    # End Beta Section #

    # Batches Section #
    
    # Batch process tasks using _batch_request
    async def abatch_process(self, tasks: List[dict], model: str, batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Processing {len(tasks)} batch tasks in chunks of {batch_size}.")
            results: List[dict] = await self._batch_request(
                self._process_task,  # Use the task processor
                items=tasks,
                model=model,
                max_tokens=None,  # max_tokens is defined per task
                batch_size=batch_size
            )
            return results  # Return the combined results from batch processing
        except OpenAIError as e:
            logger.error(f"OpenAI API error during batch processing: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during batch processing: {e}")
            raise

    # Helper task processing function
    async def _process_task(self, task: dict, model: str, *_):
        try:
            logger.debug(f"Processing task: {task}")
            response = await self.completions.create(
                model=model,
                prompt=task['prompt'],
                max_tokens=task.get('max_tokens', 100)
            )
            return response  # Return the task response
        except OpenAIError as e:
            logger.error(f"OpenAI API error during task processing: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during task processing: {e}")
            raise
    # End Batches Section #

    # Uploads Section #
    
    # Upload multiple files using batching
    async def aupload_files(self, file_paths: List[str], purpose: str, batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Uploading {len(file_paths)} files.")
            results = await self._batch_request(
                self._async_upload_task,
                items=file_paths,
                model=purpose,  # Purpose acts as the model equivalent here
                max_tokens=None,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file uploads: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file uploads: {e}")
            raise

    async def _async_upload_task(self, file_path: str, purpose: str, *_):
        try:
            with open(file_path, 'rb') as file:
                response = await self.uploads.create(
                    file=file,
                    purpose=purpose
                )
            return response  # Return the upload response
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file upload: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file upload task: {e}")
            raise

    # List uploaded files using batch requests (if applicable in large datasets)
    async def alist_files(self, batch_size: int = 50) -> List[dict]:
        try:
            logger.debug("Listing all uploaded files.")
            # We assume batching may be necessary when listing many files
            response = await self._batch_request(
                self._async_list_files_task,
                items=[],  # No items necessary here since we're just listing
                model=None,  # No specific model needed
                max_tokens=None,
                batch_size=batch_size
            )
            return response
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file listing: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file listing: {e}")
            raise

    async def _async_list_files_task(self, *_):
        try:
            response = await self.uploads.list()
            return response['data']  # Return the list of uploaded files
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file listing task: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file listing task: {e}")
            raise

    # Retrieve multiple files using batching
    async def aretrieve_files(self, file_ids: List[str], batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Retrieving {len(file_ids)} files.")
            results = await self._batch_request(
                self._async_retrieve_file_task,
                items=file_ids,
                model=None,  # No specific model needed
                max_tokens=None,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file retrievals: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file retrievals: {e}")
            raise

    async def _async_retrieve_file_task(self, file_id: str, *_):
        try:
            response = await self.uploads.retrieve(file_id)
            return response  # Return the file details
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file retrieval: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file retrieval task: {e}")
            raise

    # Delete multiple files using batching
    async def adelete_files(self, file_ids: List[str], batch_size: int) -> List[dict]:
        try:
            logger.debug(f"Deleting {len(file_ids)} files.")
            results = await self._batch_request(
                self._async_delete_file_task,
                items=file_ids,
                model=None,  # No specific model needed
                max_tokens=None,
                batch_size=batch_size
            )
            return results
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file deletions: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file deletions: {e}")
            raise

    async def _async_delete_file_task(self, file_id: str, *_):
        try:
            response = await self.uploads.delete(file_id)
            return response  # Return the deletion confirmation
        except OpenAIError as e:
            logger.error(f"OpenAI API error during file deletion: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file deletion task: {e}")
            raise
    # End Uploads Section #

    # Example for integrating raw and streaming response #
    async def afetch_with_raw_response(self, input: str, model: str):
        response = await self.embeddings.create(
            model=model,
            input=input,
            with_raw_response=True
        )
        return response

    async def afetch_with_streaming_response(self, input: str, model: str):
        response = await self.embeddings.create(
            model=model,
            input=input,
            with_streaming_response=True
        )
        return response

    async def _batch_request(self, async_task: Any, items: List[Any], model: str, max_tokens: int, batch_size: int) -> List[str]:
        batched_results: List[str] = []
        try:
            logger.debug(f"Processing batch requests in chunks of {batch_size}.")
            for i in range(0, len(items), batch_size):
                batch_items = items[i:i+batch_size]
                logger.debug(f"Processing batch: {batch_items}")
                batch_results = await asyncio.gather(
                    *[async_task(item, model, max_tokens) for item in batch_items]
                )
                batched_results.extend(batch_results)
        except OpenAIError as e:
            logger.error(f"OpenAI API error during batch request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during batch request: {e}")
            raise

        logger.debug(f"Batch processing completed with {len(batched_results)} results.")
        return batched_results

    @staticmethod
    def run(main_func: Any):
        try:
            logger.debug("Running async main function.")
            asyncio.run(main_func())
        except Exception as e:
            logger.error(f"Error running async function: {e}")
            raise
    # End Aysnc Here #

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
    def __init__(self, client: OpenAI) -> None:
        self.completions = resources.CompletionsWithRawResponse(client.completions)
        self.chat = resources.ChatWithRawResponse(client.chat)
        self.embeddings = resources.EmbeddingsWithRawResponse(client.embeddings)
        self.files = resources.FilesWithRawResponse(client.files)
        self.images = resources.ImagesWithRawResponse(client.images)
        self.audio = resources.AudioWithRawResponse(client.audio)
        self.moderations = resources.ModerationsWithRawResponse(client.moderations)
        self.models = resources.ModelsWithRawResponse(client.models)
        self.fine_tuning = resources.FineTuningWithRawResponse(client.fine_tuning)
        self.beta = resources.BetaWithRawResponse(client.beta)
        self.batches = resources.BatchesWithRawResponse(client.batches)
        self.uploads = resources.UploadsWithRawResponse(client.uploads)


class AsyncOpenAIWithRawResponse:
    def __init__(self, client: AsyncOpenAI) -> None:
        self.completions = resources.AsyncCompletionsWithRawResponse(client.completions)
        self.chat = resources.AsyncChatWithRawResponse(client.chat)
        self.embeddings = resources.AsyncEmbeddingsWithRawResponse(client.embeddings)
        self.files = resources.AsyncFilesWithRawResponse(client.files)
        self.images = resources.AsyncImagesWithRawResponse(client.images)
        self.audio = resources.AsyncAudioWithRawResponse(client.audio)
        self.moderations = resources.AsyncModerationsWithRawResponse(client.moderations)
        self.models = resources.AsyncModelsWithRawResponse(client.models)
        self.fine_tuning = resources.AsyncFineTuningWithRawResponse(client.fine_tuning)
        self.beta = resources.AsyncBetaWithRawResponse(client.beta)
        self.batches = resources.AsyncBatchesWithRawResponse(client.batches)
        self.uploads = resources.AsyncUploadsWithRawResponse(client.uploads)


class OpenAIWithStreamedResponse:
    def __init__(self, client: OpenAI) -> None:
        self.completions = resources.CompletionsWithStreamingResponse(client.completions)
        self.chat = resources.ChatWithStreamingResponse(client.chat)
        self.embeddings = resources.EmbeddingsWithStreamingResponse(client.embeddings)
        self.files = resources.FilesWithStreamingResponse(client.files)
        self.images = resources.ImagesWithStreamingResponse(client.images)
        self.audio = resources.AudioWithStreamingResponse(client.audio)
        self.moderations = resources.ModerationsWithStreamingResponse(client.moderations)
        self.models = resources.ModelsWithStreamingResponse(client.models)
        self.fine_tuning = resources.FineTuningWithStreamingResponse(client.fine_tuning)
        self.beta = resources.BetaWithStreamingResponse(client.beta)
        self.batches = resources.BatchesWithStreamingResponse(client.batches)
        self.uploads = resources.UploadsWithStreamingResponse(client.uploads)


class AsyncOpenAIWithStreamedResponse:
    def __init__(self, client: AsyncOpenAI) -> None:
        self.completions = resources.AsyncCompletionsWithStreamingResponse(client.completions)
        self.chat = resources.AsyncChatWithStreamingResponse(client.chat)
        self.embeddings = resources.AsyncEmbeddingsWithStreamingResponse(client.embeddings)
        self.files = resources.AsyncFilesWithStreamingResponse(client.files)
        self.images = resources.AsyncImagesWithStreamingResponse(client.images)
        self.audio = resources.AsyncAudioWithStreamingResponse(client.audio)
        self.moderations = resources.AsyncModerationsWithStreamingResponse(client.moderations)
        self.models = resources.AsyncModelsWithStreamingResponse(client.models)
        self.fine_tuning = resources.AsyncFineTuningWithStreamingResponse(client.fine_tuning)
        self.beta = resources.AsyncBetaWithStreamingResponse(client.beta)
        self.batches = resources.AsyncBatchesWithStreamingResponse(client.batches)
        self.uploads = resources.AsyncUploadsWithStreamingResponse(client.uploads)


Client = OpenAI

AsyncClient = AsyncOpenAI
