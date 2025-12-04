# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..shared.reasoning_effort import ReasoningEffort
from ..responses.response_input_text_param import ResponseInputTextParam
from ..responses.response_input_audio_param import ResponseInputAudioParam

__all__ = [
    "ScoreModelGraderParam",
    "Input",
    "InputContent",
    "InputContentOutputText",
    "InputContentInputImage",
    "SamplingParams",
]


class InputContentOutputText(TypedDict, total=False):
    text: Required[str]
    """The text output from the model."""

    type: Required[Literal["output_text"]]
    """The type of the output text. Always `output_text`."""


class InputContentInputImage(TypedDict, total=False):
    image_url: Required[str]
    """The URL of the image input."""

    type: Required[Literal["input_image"]]
    """The type of the image input. Always `input_image`."""

    detail: str
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, or `auto`. Defaults to `auto`.
    """


InputContent: TypeAlias = Union[
    str,
    ResponseInputTextParam,
    InputContentOutputText,
    InputContentInputImage,
    ResponseInputAudioParam,
    Iterable[object],
]


class Input(TypedDict, total=False):
    content: Required[InputContent]
    """Inputs to the model - can contain template strings."""

    role: Required[Literal["user", "assistant", "system", "developer"]]
    """The role of the message input.

    One of `user`, `assistant`, `system`, or `developer`.
    """

    type: Literal["message"]
    """The type of the message input. Always `message`."""


class SamplingParams(TypedDict, total=False):
    max_completions_tokens: Optional[int]
    """The maximum number of tokens the grader model may generate in its response."""

    reasoning_effort: Optional[ReasoningEffort]
    """
    Constrains effort on reasoning for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning). Currently
    supported values are `none`, `minimal`, `low`, `medium`, `high`, and `xhigh`.
    Reducing reasoning effort can result in faster responses and fewer tokens used
    on reasoning in a response.

    - `gpt-5.1` defaults to `none`, which does not perform reasoning. The supported
      reasoning values for `gpt-5.1` are `none`, `low`, `medium`, and `high`. Tool
      calls are supported for all reasoning values in gpt-5.1.
    - All models before `gpt-5.1` default to `medium` reasoning effort, and do not
      support `none`.
    - The `gpt-5-pro` model defaults to (and only supports) `high` reasoning effort.
    - `xhigh` is currently only supported for `gpt-5.1-codex-max`.
    """

    seed: Optional[int]
    """A seed value to initialize the randomness, during sampling."""

    temperature: Optional[float]
    """A higher temperature increases randomness in the outputs."""

    top_p: Optional[float]
    """An alternative to temperature for nucleus sampling; 1.0 includes all tokens."""


class ScoreModelGraderParam(TypedDict, total=False):
    input: Required[Iterable[Input]]
    """The input text. This may include template strings."""

    model: Required[str]
    """The model to use for the evaluation."""

    name: Required[str]
    """The name of the grader."""

    type: Required[Literal["score_model"]]
    """The object type, which is always `score_model`."""

    range: Iterable[float]
    """The range of the score. Defaults to `[0, 1]`."""

    sampling_params: SamplingParams
    """The sampling parameters for the model."""
