from openai.types.beta.beta_response_steer_failed_event import BetaResponseSteerFailedEvent
from openai.types.beta.beta_response_steer_input import (
    ResponseSteerInputItemListMessage as BetaResponseSteerInputItemListMessage,
)
from openai.types.responses.response_steer_failed_event import ResponseSteerFailedEvent
from openai.types.responses.response_steer_input import ResponseSteerInputItemListMessage


def _failed_event_payload() -> dict[str, object]:
    return {
        "error": {
            "code": "invalid_input",
            "message": "Invalid steering input",
            "type": "invalid_request_error",
        },
        "sequence_number": 1,
        "steer": {
            "input": [{"role": "user", "content": "continue"}],
            "previous_response_id": "resp_test",
        },
        "type": "response.steer.failed",
    }


def test_failed_steer_event_parses_message_without_type() -> None:
    event = ResponseSteerFailedEvent.model_validate(_failed_event_payload())

    assert isinstance(event.steer.input, list)
    message = event.steer.input[0]
    assert isinstance(message, ResponseSteerInputItemListMessage)
    assert message.role == "user"
    assert message.type is None


def test_beta_failed_steer_event_parses_message_without_type() -> None:
    event = BetaResponseSteerFailedEvent.model_validate(_failed_event_payload())

    assert isinstance(event.steer.input, list)
    message = event.steer.input[0]
    assert isinstance(message, BetaResponseSteerInputItemListMessage)
    assert message.role == "user"
    assert message.type is None
