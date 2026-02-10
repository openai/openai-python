from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .completion import Completion
from .responses.response import Response
from .chat.chat_completion import ChatCompletion
from .create_embedding_response import CreateEmbeddingResponse
from .moderation_create_response import ModerationCreateResponse

__all__ = ["BatchRequestOutput", "BatchRequestOutputResponse", "BatchRequestOutputError", "BatchResponseBody"]


# Union of all possible response body types for batch request outputs
BatchResponseBody = Union[
    ChatCompletion,
    Completion,
    CreateEmbeddingResponse,
    ModerationCreateResponse,
    Response,
]


class BatchRequestOutputError(BaseModel):
    """For requests that failed with a non-HTTP error, this will contain more information on the cause of the failure."""

    code: Literal["batch_expired", "batch_cancelled", "request_timeout"]
    """A machine-readable error code.

    Possible values:
    - `batch_expired`: The request could not be executed before the
      completion window ended.
    - `batch_cancelled`: The batch was cancelled before this request
      executed.
    - `request_timeout`: The underlying call to the model timed out.
    """

    message: str
    """A human-readable error message."""


class BatchRequestOutputResponse(BaseModel):
    """The response object for a successfully executed batch request."""

    status_code: int
    """The HTTP status code of the response."""

    request_id: str
    """An unique identifier for the OpenAI API request.

    Please include this request ID when contacting support.
    """

    body: BatchResponseBody
    """The JSON body of the response.

    The structure depends on the endpoint that was called:
    - `/v1/chat/completions` -> `ChatCompletion`
    - `/v1/completions` -> `Completion`
    - `/v1/embeddings` -> `CreateEmbeddingResponse`
    - `/v1/moderations` -> `ModerationCreateResponse`
    - `/v1/responses` -> `Response`
    """


class BatchRequestOutput(BaseModel):
    """The per-line object of the batch output and error files.

    Each line in a batch output JSONL file represents the result of a single
    request from the batch input file. The output file contains successfully
    executed requests, while the error file contains requests that failed.
    """

    id: str
    """The unique ID of the batch request."""

    custom_id: str
    """A developer-provided per-request id that will be used to match outputs to inputs.

    This matches the `custom_id` from the corresponding `BatchRequestInput`.
    """

    response: Optional[BatchRequestOutputResponse] = None
    """The response object if the request was successfully executed.

    Contains the HTTP status code, request ID, and the JSON body of the response.
    """

    error: Optional[BatchRequestOutputError] = None
    """The error object if the request failed with a non-HTTP error.

    Contains a machine-readable error code and a human-readable error message.
    """
