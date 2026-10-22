from __future__ import annotations

from .._exceptions import ResponseFailedError, ResponseIncompleteError
from ..types.responses.response import Response

__all__ = ["raise_for_status"]

_RETRYABLE_ERROR_CODES = frozenset({"server_error", "rate_limit_exceeded", "vector_store_timeout"})


def raise_for_status(response: Response, *, raise_on_incomplete: bool = False) -> None:
    """Raise if `response` reached a final state other than `completed`.

    A background run reports its own failure inside a `200 OK` poll, so `retrieve()`
    returns it instead of raising. Call this to opt into an exception. `"cancelled"`
    is caller-initiated and does not raise.

    `status="incomplete"` only raises when `raise_on_incomplete` is set: the usual
    reason is `max_output_tokens`, which still leaves usable output on
    `response.output`.
    """
    if response.status == "failed":
        error = response.error
        if error is None:
            raise ResponseFailedError(
                "Response failed without an error code.",
                response=response,
                code=None,
                retryable=False,
            )

        raise ResponseFailedError(
            error.message,
            response=response,
            code=error.code,
            retryable=error.code in _RETRYABLE_ERROR_CODES,
        )

    if response.status == "incomplete" and raise_on_incomplete:
        reason = response.incomplete_details.reason if response.incomplete_details else None
        raise ResponseIncompleteError(
            f"Response was incomplete: {reason or 'no reason reported'}.",
            response=response,
            reason=reason,
            retryable=False,
        )
