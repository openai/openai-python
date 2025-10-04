# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from ..shared.reasoning_effort import ReasoningEffort
from ..responses.response_input_text import ResponseInputText
from ..responses.response_input_audio import ResponseInputAudio

__all__ = [
    "ScoreModelGrader",
    "Input",
    "InputContent",
    "InputContentOutputText",
    "InputContentInputImage",
    "SamplingParams",
]


class InputContentOutputText(BaseModel):
    text: str
    """The text output from the model."""

    type: Literal["output_text"]
    """The type of the output text. Always `output_text`."""


class InputContentInputImage(BaseModel):
    image_url: str
    """The URL of the image input."""

    type: Literal["input_image"]
    """The type of the image input. Always `input_image`."""

    detail: Optional[str] = None
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, or `auto`. Defaults to `auto`.
    """


InputContent: TypeAlias = Union[
    str, ResponseInputText, InputContentOutputText, InputContentInputImage, ResponseInputAudio, List[object]
]


class Input(BaseModel):
    content: InputContent
    """Inputs to the model - can contain template strings."""

    role: Literal["user", "assistant", "system", "developer"]
    """The role of the message input.

    One of `user`, `assistant`, `system`, or `developer`.
    """

    type: Optional[Literal["message"]] = None
    """The type of the message input. Always `message`."""


class SamplingParams(BaseModel):
    max_completions_tokens: Optional[int] = None
    """The maximum number of tokens the grader model may generate in its response."""

    reasoning_effort: Optional[ReasoningEffort] = None
    """
    Constrains effort on reasoning for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning). Currently
    supported values are `minimal`, `low`, `medium`, and `high`. Reducing reasoning
    effort can result in faster responses and fewer tokens used on reasoning in a
    response.
    """

    seed: Optional[int] = None
    """A seed value to initialize the randomness, during sampling."""

    temperature: Optional[float] = None
    """A higher temperature increases randomness in the outputs."""

    top_p: Optional[float] = None
    """An alternative to temperature for nucleus sampling; 1.0 includes all tokens."""


class ScoreModelGrader(BaseModel):
    input: List[Input]
    """The input text. This may include template strings."""

    model: str
    """The model to use for the evaluation."""

    name: str
    """The name of the grader."""

    type: Literal["score_model"]
    """The object type, which is always `score_model`."""

    range: Optional[List[float]] = None
    """The range of the score. Defaults to `[0, 1]`."""

    sampling_params: Optional[SamplingParams] = None
    """The sampling parameters for the model."""
