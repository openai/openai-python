from openai.types.beta import beta_response_steer_input as beta_steer
from openai.types.beta import beta_response_steer_input_param as beta_steer_param
from openai.types.responses import response_steer_input as steer
from openai.types.responses import response_steer_input_param as steer_param


def test_stable_steer_input_is_user_message_only() -> None:
    message = steer.ResponseSteerInputItemListMessage.model_validate({"role": "user", "content": "continue"})

    assert message.type is None
    assert steer.ResponseSteerInputItemList is steer.ResponseSteerInputItemListMessage
    assert set(steer_param.ResponseSteerInputItemListMessage.__required_keys__) == {"content", "role"}
    assert steer_param.ResponseSteerInputItemList is steer_param.ResponseSteerInputItemListMessage
    assert "ResponseSteerInputItemListFunctionCallOutput" not in steer.__all__
    assert "ResponseSteerInputItemListFunctionCallOutput" not in steer_param.__all__


def test_beta_steer_input_is_user_message_only() -> None:
    message = beta_steer.ResponseSteerInputItemListMessage.model_validate({"role": "user", "content": "continue"})

    assert message.type is None
    assert beta_steer.ResponseSteerInputItemList is beta_steer.ResponseSteerInputItemListMessage
    assert set(beta_steer_param.ResponseSteerInputItemListMessage.__required_keys__) == {"content", "role"}
    assert beta_steer_param.ResponseSteerInputItemList is beta_steer_param.ResponseSteerInputItemListMessage
    assert "ResponseSteerInputItemListFunctionCallOutput" not in beta_steer.__all__
    assert "ResponseSteerInputItemListFunctionCallOutput" not in beta_steer_param.__all__
