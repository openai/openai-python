from openai._compat import parse_obj, get_model_fields
from openai.types.realtime.response_done_event import ResponseDoneEvent
from openai.types.beta.realtime.response_done_event import ResponseDoneEvent as BetaResponseDoneEvent
from openai.types.realtime.realtime_response_status import Error as RealtimeResponseStatusError
from openai.types.beta.realtime.realtime_response_status import Error as BetaRealtimeResponseStatusError

ERROR_MESSAGE = "We're currently processing too many requests - please try again later."


def test_realtime_response_status_error_declares_message() -> None:
    assert "message" in get_model_fields(RealtimeResponseStatusError)


def test_beta_realtime_response_status_error_declares_message() -> None:
    assert "message" in get_model_fields(BetaRealtimeResponseStatusError)


def test_realtime_response_done_failed_error_message() -> None:
    event = parse_obj(
        ResponseDoneEvent,
        {
            "type": "response.done",
            "event_id": "event_123",
            "response": {
                "object": "realtime.response",
                "id": "resp_123",
                "status": "failed",
                "status_details": {
                    "type": "failed",
                    "error": {
                        "type": "invalid_request_error",
                        "code": "inference_rate_limit_exceeded",
                        "message": ERROR_MESSAGE,
                    },
                },
                "output": [],
            },
        },
    )

    assert event.response.status_details is not None
    assert event.response.status_details.error is not None
    assert event.response.status_details.error.message == ERROR_MESSAGE


def test_beta_realtime_response_done_failed_error_message() -> None:
    event = parse_obj(
        BetaResponseDoneEvent,
        {
            "type": "response.done",
            "event_id": "event_123",
            "response": {
                "object": "realtime.response",
                "id": "resp_123",
                "status": "failed",
                "status_details": {
                    "type": "failed",
                    "error": {
                        "type": "invalid_request_error",
                        "code": "inference_rate_limit_exceeded",
                        "message": ERROR_MESSAGE,
                    },
                },
                "output": [],
            },
        },
    )

    assert event.response.status_details is not None
    assert event.response.status_details.error is not None
    assert event.response.status_details.error.message == ERROR_MESSAGE
