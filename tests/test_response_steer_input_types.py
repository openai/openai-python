from typing import get_origin, get_type_hints

from typing_extensions import Required

from openai.types.beta import beta_response_steer_input_param as beta_steer_param
from openai.types.responses import response_steer_input_param as steer_param


def _assert_message_contract(message: type) -> None:
    hints = get_type_hints(message, include_extras=True)

    assert set(hints) == {"content", "role", "type"}
    assert get_origin(hints["content"]) is Required
    assert get_origin(hints["role"]) is Required
    assert get_origin(hints["type"]) is not Required


def test_stable_steer_params_match_wire_contract() -> None:
    message = steer_param.ResponseSteerInputItemListMessage

    _assert_message_contract(message)
    assert steer_param.ResponseSteerInputItemList is message
    assert "ResponseSteerInputItemListFunctionCallOutput" not in steer_param.__all__


def test_beta_steer_params_match_wire_contract() -> None:
    message = beta_steer_param.ResponseSteerInputItemListMessage

    _assert_message_contract(message)
    assert beta_steer_param.ResponseSteerInputItemList is message
    assert "ResponseSteerInputItemListFunctionCallOutput" not in beta_steer_param.__all__
