# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo
from ..beta_tool_param import BetaToolParam
from ..beta_tool_choice_options import BetaToolChoiceOptions
from ..beta_tool_choice_mcp_param import BetaToolChoiceMcpParam
from ..beta_tool_choice_shell_param import BetaToolChoiceShellParam
from ..beta_tool_choice_types_param import BetaToolChoiceTypesParam
from ..beta_tool_choice_custom_param import BetaToolChoiceCustomParam
from ..beta_response_input_item_param import BetaResponseInputItemParam
from ..beta_tool_choice_allowed_param import BetaToolChoiceAllowedParam
from ..beta_tool_choice_function_param import BetaToolChoiceFunctionParam
from ..beta_tool_choice_apply_patch_param import BetaToolChoiceApplyPatchParam
from ..beta_response_conversation_param_param import BetaResponseConversationParamParam
from ..beta_response_format_text_config_param import BetaResponseFormatTextConfigParam

__all__ = [
    "InputTokenCountParams",
    "Conversation",
    "Reasoning",
    "Text",
    "ToolChoice",
    "ToolChoiceBetaSpecificProgrammaticToolCallingParam",
]


class InputTokenCountParams(TypedDict, total=False):
    conversation: Optional[Conversation]
    """The conversation that this response belongs to.

    Items from this conversation are prepended to `input_items` for this response
    request. Input items and output items from this response are automatically added
    to this conversation after this response completes.
    """

    input: Union[str, Iterable[BetaResponseInputItemParam], None]
    """Text, image, or file inputs to the model, used to generate a response"""

    instructions: Optional[str]
    """
    A system (or developer) message inserted into the model's context. When used
    along with `previous_response_id`, the instructions from a previous response
    will not be carried over to the next response. This makes it simple to swap out
    system (or developer) messages in new responses.
    """

    model: Optional[str]
    """Model ID used to generate the response, like `gpt-4o` or `o3`.

    OpenAI offers a wide range of models with different capabilities, performance
    characteristics, and price points. Refer to the
    [model guide](https://platform.openai.com/docs/models) to browse and compare
    available models.
    """

    parallel_tool_calls: Optional[bool]
    """Whether to allow the model to run tool calls in parallel."""

    personality: Union[str, Literal["friendly", "pragmatic"]]
    """A model-owned style preset to apply to this request.

    Omit this parameter to use the model's default style. Supported values may
    expand over time. Values must be at most 64 characters.
    """

    previous_response_id: Optional[str]
    """The unique ID of the previous response to the model.

    Use this to create multi-turn conversations. Learn more about
    [conversation state](https://platform.openai.com/docs/guides/conversation-state).
    Cannot be used in conjunction with `conversation`.
    """

    reasoning: Optional[Reasoning]
    """
    **gpt-5 and o-series models only** Configuration options for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning).
    """

    text: Optional[Text]
    """Configuration options for a text response from the model.

    Can be plain text or structured JSON data. Learn more:

    - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
    - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
    """

    tool_choice: Optional[ToolChoice]
    """Controls which tool the model should use, if any."""

    tools: Optional[Iterable[BetaToolParam]]
    """An array of tools the model may call while generating a response.

    You can specify which tool to use by setting the `tool_choice` parameter.
    """

    truncation: Literal["auto", "disabled"]
    """The truncation strategy to use for the model response.

    - `auto`: If the input to this Response exceeds the model's context window size,
      the model will truncate the response to fit the context window by dropping
      items from the beginning of the conversation. - `disabled` (default): If the
      input size will exceed the context window size for a model, the request will
      fail with a 400 error.
    """

    betas: Annotated[List[Literal["responses_multi_agent=v1"]], PropertyInfo(alias="openai-beta")]


Conversation: TypeAlias = Union[str, BetaResponseConversationParamParam]


class Reasoning(TypedDict, total=False):
    """
    **gpt-5 and o-series models only** Configuration options for [reasoning models](https://platform.openai.com/docs/guides/reasoning).
    """

    context: Optional[Literal["auto", "current_turn", "all_turns"]]
    """
    Controls which reasoning items are rendered back to the model on later turns. If
    omitted or set to `auto`, the model determines the context mode. The `gpt-5.6`
    model family defaults to `all_turns`; earlier models default to `current_turn`.

    When returned on a response, this is the effective reasoning context mode used
    for the response.
    """

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]]
    """Constrains effort on reasoning for reasoning models.

    Currently supported values are `none`, `minimal`, `low`, `medium`, `high`,
    `xhigh`, and `max`. Reducing reasoning effort can result in faster responses and
    fewer tokens used on reasoning in a response. Not all reasoning models support
    every value. See the
    [reasoning guide](https://platform.openai.com/docs/guides/reasoning) for
    model-specific support.
    """

    generate_summary: Optional[Literal["auto", "concise", "detailed"]]
    """**Deprecated:** use `summary` instead.

    A summary of the reasoning performed by the model. This can be useful for
    debugging and understanding the model's reasoning process. One of `auto`,
    `concise`, or `detailed`.
    """

    mode: Union[str, Literal["standard", "pro"]]
    """Controls the reasoning execution mode for the request.

    When returned on a response, this is the effective execution mode.
    """

    summary: Optional[Literal["auto", "concise", "detailed"]]
    """A summary of the reasoning performed by the model.

    This can be useful for debugging and understanding the model's reasoning
    process. One of `auto`, `concise`, or `detailed`.

    `concise` is supported for `computer-use-preview` models and all reasoning
    models after `gpt-5`.
    """


class Text(TypedDict, total=False):
    """Configuration options for a text response from the model.

    Can be plain
    text or structured JSON data. Learn more:
    - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
    - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
    """

    format: BetaResponseFormatTextConfigParam
    """An object specifying the format that the model must output.

    Configuring `{ "type": "json_schema" }` enables Structured Outputs, which
    ensures the model will match your supplied JSON schema. Learn more in the
    [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

    The default format is `{ "type": "text" }` with no additional options.

    **Not recommended for gpt-4o and newer models:**

    Setting to `{ "type": "json_object" }` enables the older JSON mode, which
    ensures the message the model generates is valid JSON. Using `json_schema` is
    preferred for models that support it.
    """

    verbosity: Optional[Literal["low", "medium", "high"]]
    """Constrains the verbosity of the model's response.

    Lower values will result in more concise responses, while higher values will
    result in more verbose responses. Currently supported values are `low`,
    `medium`, and `high`. The default is `medium`.
    """


class ToolChoiceBetaSpecificProgrammaticToolCallingParam(TypedDict, total=False):
    type: Required[Literal["programmatic_tool_calling"]]
    """The tool to call. Always `programmatic_tool_calling`."""


ToolChoice: TypeAlias = Union[
    BetaToolChoiceOptions,
    BetaToolChoiceAllowedParam,
    BetaToolChoiceTypesParam,
    BetaToolChoiceFunctionParam,
    BetaToolChoiceMcpParam,
    BetaToolChoiceCustomParam,
    ToolChoiceBetaSpecificProgrammaticToolCallingParam,
    BetaToolChoiceApplyPatchParam,
    BetaToolChoiceShellParam,
]
