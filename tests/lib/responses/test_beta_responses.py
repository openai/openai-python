from __future__ import annotations

from typing import Any

from openai._models import construct_type_unchecked
from openai.types.beta import BetaResponse


def _message(
    *texts: str,
    agent_name: str | None = None,
    phase: str | None = None,
) -> dict[str, Any]:
    message: dict[str, Any] = {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [
            {
                "type": "output_text",
                "annotations": [],
                "logprobs": [],
                "text": text,
            }
            for text in texts
        ],
    }
    if agent_name is not None:
        message["agent"] = {"agent_name": agent_name}
    if phase is not None:
        message["phase"] = phase
    return message


def _response(*output: dict[str, Any]) -> BetaResponse:
    return construct_type_unchecked(type_=BetaResponse, value={"output": list(output)})


def test_output_text_uses_last_root_final_message_for_multi_agent_response() -> None:
    response = _response(
        _message("old answer", agent_name="/root", phase="final_answer"),
        _message("child answer", agent_name="/root/reviewer", phase="final_answer"),
        _message("root commentary", agent_name="/root", phase="commentary"),
        _message("final ", "answer", agent_name="/root", phase="final_answer"),
    )

    assert response.output_text == "final answer"


def test_output_text_is_empty_without_root_final_message_for_multi_agent_response() -> None:
    response = _response(
        _message("child answer", agent_name="/root/reviewer", phase="final_answer"),
        _message("root commentary", agent_name="/root", phase="commentary"),
    )

    assert response.output_text == ""


def test_output_text_aggregates_non_multi_agent_response() -> None:
    response = _response(_message("first "), _message("second"))

    assert response.output_text == "first second"
