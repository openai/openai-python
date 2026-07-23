from __future__ import annotations

from pydantic import BaseModel
import pytest

from openai.types.beta.realtime import RealtimeResponseStatus as BetaRealtimeResponseStatus
from openai.types.realtime import RealtimeResponseStatus as RealtimeResponseStatus


@pytest.mark.parametrize(
    "status_cls",
    [BetaRealtimeResponseStatus, RealtimeResponseStatus],
    ids=["beta", "realtime"],
)
def test_realtime_response_status_error_message(status_cls: type[BaseModel]) -> None:
    status = status_cls.model_validate(
        {
            "error": {
                "code": "bad_request",
                "message": "The model could not process the request.",
                "type": "invalid_request_error",
            },
            "type": "failed",
        }
    )

    assert status.error is not None
    assert status.error.code == "bad_request"
    assert status.error.message == "The model could not process the request."
    assert status.error.type == "invalid_request_error"
    assert status.type == "failed"
