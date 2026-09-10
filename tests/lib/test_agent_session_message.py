from typing import List, Optional
from typing_extensions import Literal

import pytest

from openai.types.beta import AgentSessionMessage
from openai.types.beta.agent_session_message_content import (
    AgentSessionMessageContent,
    MessageContentResourceInputText,
    MessageContentResourceInputImage,
    MessageContentResourceOutputText,
)


@pytest.mark.parametrize("phase", [None, "commentary", "final_answer"])
def test_output_text_joins_blocks(phase: Optional[Literal["commentary", "final_answer"]]) -> None:
    message = AgentSessionMessage(
        content=[
            MessageContentResourceOutputText(type="output_text", text="Hello "),
            MessageContentResourceOutputText(type="output_text", text=""),
            MessageContentResourceOutputText(type="output_text", text="world!"),
        ],
        phase=phase,
        role="assistant",
        status="completed",
        turn_id="turn_test",
        type="message",
    )

    assert message.output_text == "Hello world!"


@pytest.mark.parametrize(
    "content",
    [
        [],
        [MessageContentResourceInputText(type="input_text", text="User input")],
        [
            MessageContentResourceInputText(type="input_text", text="Describe this image"),
            MessageContentResourceInputImage(type="input_image", image_url="https://example.com/image.png"),
        ],
    ],
)
def test_output_text_without_output_blocks(content: List[AgentSessionMessageContent]) -> None:
    message = AgentSessionMessage(
        content=content,
        role="user",
        status="completed",
        turn_id="turn_test",
        type="message",
    )

    assert message.output_text == ""


def test_output_text_ignores_other_content_types() -> None:
    message = AgentSessionMessage(
        content=[
            MessageContentResourceOutputText(type="output_text", text="First"),
            MessageContentResourceInputText(type="input_text", text="Not output"),
            MessageContentResourceInputImage(type="input_image", image_url="https://example.com/image.png"),
            MessageContentResourceOutputText(type="output_text", text=" second"),
        ],
        role="assistant",
        status="completed",
        turn_id="turn_test",
        type="message",
    )

    assert message.output_text == "First second"


def test_output_text_reads_do_not_change_serialization() -> None:
    message = AgentSessionMessage(
        content=[MessageContentResourceOutputText(type="output_text", text="Answer")],
        role="assistant",
        status="completed",
        turn_id="turn_test",
        type="message",
    )
    original_dict = message.to_dict()
    original_json = message.to_json()

    assert message.output_text == "Answer"
    assert message.output_text == "Answer"
    assert message.to_dict() == original_dict
    assert message.to_json() == original_json
    assert "output_text" not in message.to_dict()

    message.content.append(MessageContentResourceOutputText(type="output_text", text=" updated"))
    assert message.output_text == "Answer updated"
