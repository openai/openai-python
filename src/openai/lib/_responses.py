from __future__ import annotations

from typing import Dict, Type, Optional, NamedTuple

from .._exceptions import (
    NotFoundError,
    APIStatusError,
    RateLimitError,
    BadRequestError,
    InternalServerError,
    PermissionDeniedError,
)
from .._legacy_response import LegacyAPIResponse
from ..types.responses.response import Response

__all__ = [
    "RESPONSE_ERROR_CODE_TO_EXCEPTION",
    "INCOMPLETE_DETAILS_REASON_TO_EXCEPTION",
    "exception_for_background_failure",
]


class _ErrorMapping(NamedTuple):
    """One entry in a background-failure mapping table.

    Bundles the SDK exception class (``None`` means "no exception should be
    raised for this code/reason") together with whether retrying the same
    request is expected to help, so the two facts can't drift apart.
    """

    exception_class: Optional[Type[APIStatusError]]
    retryable: bool


# `ResponseError.code` -> SDK exception. This is the entire signal a failed
# background run gives us (see `ResponseError` in
# `openai/types/responses/response_error.py`) -- there's no HTTP status to
# dispatch on, since the poll that surfaces this returns 200 OK.
#
# Unmapped codes (a value OpenAI ships before this table is updated) fall back
# to InternalServerError(retryable=True) in `exception_for_background_failure`
# -- an explicit "failed" status must never look like success.
RESPONSE_ERROR_CODE_TO_EXCEPTION: Dict[str, _ErrorMapping] = {
    "server_error": _ErrorMapping(InternalServerError, True),
    "rate_limit_exceeded": _ErrorMapping(RateLimitError, True),
    "vector_store_timeout": _ErrorMapping(InternalServerError, True),
    "data_residency_mismatch": _ErrorMapping(PermissionDeniedError, False),
    "invalid_prompt": _ErrorMapping(BadRequestError, False),
    "bio_policy": _ErrorMapping(BadRequestError, False),
    "invalid_image": _ErrorMapping(BadRequestError, False),
    "invalid_image_format": _ErrorMapping(BadRequestError, False),
    "invalid_base64_image": _ErrorMapping(BadRequestError, False),
    "invalid_image_url": _ErrorMapping(BadRequestError, False),
    "image_too_large": _ErrorMapping(BadRequestError, False),
    "image_too_small": _ErrorMapping(BadRequestError, False),
    "image_parse_error": _ErrorMapping(BadRequestError, False),
    "image_content_policy_violation": _ErrorMapping(BadRequestError, False),
    "invalid_image_mode": _ErrorMapping(BadRequestError, False),
    "image_file_too_large": _ErrorMapping(BadRequestError, False),
    "unsupported_image_media_type": _ErrorMapping(BadRequestError, False),
    "empty_image_file": _ErrorMapping(BadRequestError, False),
    "failed_to_download_image": _ErrorMapping(BadRequestError, False),
    "image_file_not_found": _ErrorMapping(NotFoundError, False),
}

# `IncompleteDetails.reason` -> SDK exception. Separate table from the one
# above: `status="incomplete"` is not automatically a failure (a run that hit
# `max_output_tokens` produced a structurally valid, complete-so-far result),
# so unlike `RESPONSE_ERROR_CODE_TO_EXCEPTION` there is no "unmapped ->
# fall back to an exception" behavior here -- an unrecognized or absent
# reason simply means we return None (don't raise).
INCOMPLETE_DETAILS_REASON_TO_EXCEPTION: Dict[str, _ErrorMapping] = {
    "max_output_tokens": _ErrorMapping(None, False),
    "content_filter": _ErrorMapping(BadRequestError, False),
}

_UNMAPPED_FAILURE = _ErrorMapping(InternalServerError, True)


def exception_for_background_failure(
    raw_response: LegacyAPIResponse[Response],
    response: Response,
) -> Optional[APIStatusError]:
    """Return the exception a failed/incomplete background Response should raise, or None.

    Background runs finish with a normal HTTP 200 even when the run itself
    failed, so the SDK's usual status-code-based error handling never
    triggers. `Responses.retrieve()` calls this once a run is no longer
    queued/in-progress, to translate `error.code` (or, for status=
    "incomplete", `incomplete_details.reason`) into the same exception class
    a synchronous request with an equivalent failure would have raised.

    The raised exception also carries a best-effort `.retryable` attribute
    (not declared on the base exception classes -- read it with
    `getattr(exc, "retryable", False)`). `RESPONSE_ERROR_CODE_TO_EXCEPTION`
    and `INCOMPLETE_DETAILS_REASON_TO_EXCEPTION` are the documented source of
    truth for this flag.

    Returns None if the response didn't fail, or "failed"/"incomplete" but
    without enough information to classify (e.g. no `error`/
    `incomplete_details` populated).
    """
    mapping: Optional[_ErrorMapping] = None
    message = "Background response run did not complete successfully."

    if response.status == "failed":
        if response.error is None:
            return None
        message = response.error.message
        mapping = RESPONSE_ERROR_CODE_TO_EXCEPTION.get(response.error.code, _UNMAPPED_FAILURE)
    elif response.status == "incomplete":
        reason = response.incomplete_details.reason if response.incomplete_details else None
        if reason is None:
            return None
        mapping = INCOMPLETE_DETAILS_REASON_TO_EXCEPTION.get(reason)
        message = f"Background response run was incomplete: {reason}"
    else:
        return None

    if mapping is None or mapping.exception_class is None:
        return None

    body = {"error": {"code": getattr(response.error, "code", None), "message": message}}
    exc = mapping.exception_class(message, response=raw_response.http_response, body=body)
    exc.retryable = mapping.retryable  # type: ignore[attr-defined]
    return exc
