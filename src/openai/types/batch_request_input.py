from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["BatchRequestInput"]


class BatchRequestInput(TypedDict, total=False):
    custom_id: Required[str]
    """A developer-provided per-request id that will be used to match outputs to inputs.

    Must be unique for each request in a batch.
    """

    method: Required[Literal["POST"]]
    """The HTTP method to be used for the request. Currently only `POST` is supported."""

    url: Required[str]
    """The OpenAI API relative URL to be used for the request.

    Currently `/v1/chat/completions`, `/v1/embeddings`, and `/v1/completions` are
    supported.
    """

    body: Required[object]
    """The body of the request."""
