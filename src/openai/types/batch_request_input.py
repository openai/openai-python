from __future__ import annotations

from typing import Any, Dict, Union
from typing_extensions import Literal, Required, TypedDict

from .embedding_create_params import EmbeddingCreateParams
from .completion_create_params import CompletionCreateParams
from .moderation_create_params import ModerationCreateParams
from .chat.completion_create_params import CompletionCreateParams as ChatCompletionCreateParams
from .responses.response_create_params import ResponseCreateParams

__all__ = ["BatchRequestInput"]


# Union of all possible request body types for batch requests
BatchRequestBody = Union[
    ChatCompletionCreateParams,
    CompletionCreateParams,
    EmbeddingCreateParams,
    ModerationCreateParams,
    ResponseCreateParams,
    Dict[str, Any],  # Fallback for any additional types
]


class BatchRequestInput(TypedDict, total=False):
    """The per-line object of the batch input file.

    Each line in a batch input JSONL file represents a single request that will be
    processed as part of the batch. The file can contain up to 50,000 requests and
    can be up to 200 MB in size.
    """

    custom_id: Required[str]
    """A developer-provided per-request id that will be used to match outputs to inputs.

    Must be unique for each request in a batch.
    """

    method: Required[Literal["POST"]]
    """The HTTP method to be used for the request.

    Currently only `POST` is supported.
    """

    url: Required[str]
    """The OpenAI API relative URL to be used for the request.

    Currently `/v1/responses`, `/v1/chat/completions`, `/v1/embeddings`,
    `/v1/completions`, and `/v1/moderations` are supported.
    """

    body: Required[BatchRequestBody]
    """The request body for the API endpoint specified in `url`.

    The structure of the body must match the expected parameters for the endpoint.
    For example, if `url` is `/v1/chat/completions`, the body should be a
    `ChatCompletionCreateParams` object.
    """
