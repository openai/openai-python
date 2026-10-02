import pytest

from openai._compat import parse_obj
from openai.types.realtime.realtime_response_status import RealtimeResponseStatus
from openai.types.beta.realtime.realtime_response_status import (
    RealtimeResponseStatus as BetaRealtimeResponseStatus,
)


@pytest.mark.parametrize("status_model", [RealtimeResponseStatus, BetaRealtimeResponseStatus])
def test_realtime_response_error_message_is_preserved_and_optional(status_model) -> None:
    status = parse_obj(status_model, {"error": {"message": "The response failed."}})
    assert status.error is not None
    assert status.error.message == "The response failed."

    status_without_message = parse_obj(status_model, {"error": {}})
    assert status_without_message.error is not None
    assert status_without_message.error.message is None
