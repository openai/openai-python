from openai.types.beta import beta_response_steer_input_param as beta_steer_param
from openai.types.responses import response_steer_input_param as steer_param


def test_stable_steer_params_match_wire_contract() -> None:
    message = steer_param.ResponseSteerInputItemListMessage

    assert set(message.__annotations__) == {"content", "role", "type"}
    assert set(message.__required_keys__) == {"content", "role"}
    assert steer_param.ResponseSteerInputItemList is message
    assert "ResponseSteerInputItemListFunctionCallOutput" not in steer_param.__all__


def test_beta_steer_params_match_wire_contract() -> None:
    message = beta_steer_param.ResponseSteerInputItemListMessage

    assert set(message.__annotations__) == {"content", "role", "type"}
    assert set(message.__required_keys__) == {"content", "role"}
    assert beta_steer_param.ResponseSteerInputItemList is message
    assert "ResponseSteerInputItemListFunctionCallOutput" not in beta_steer_param.__all__
