# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_tool import BetaTool
from .beta_response_error import BetaResponseError
from .beta_response_usage import BetaResponseUsage
from .beta_response_prompt import BetaResponsePrompt
from .beta_response_status import BetaResponseStatus
from .beta_tool_choice_mcp import BetaToolChoiceMcp
from .beta_tool_choice_shell import BetaToolChoiceShell
from .beta_tool_choice_types import BetaToolChoiceTypes
from .beta_tool_choice_custom import BetaToolChoiceCustom
from .beta_response_input_item import BetaResponseInputItem
from .beta_tool_choice_allowed import BetaToolChoiceAllowed
from .beta_tool_choice_options import BetaToolChoiceOptions
from .beta_response_output_item import BetaResponseOutputItem
from .beta_response_text_config import BetaResponseTextConfig
from .beta_tool_choice_function import BetaToolChoiceFunction
from .beta_response_output_message import BetaResponseOutputMessage
from .beta_tool_choice_apply_patch import BetaToolChoiceApplyPatch

__all__ = [
    "BetaResponse",
    "IncompleteDetails",
    "ToolChoice",
    "ToolChoiceBetaSpecificProgrammaticToolCallingParam",
    "Conversation",
    "Moderation",
    "ModerationInput",
    "ModerationInputModerationResult",
    "ModerationInputError",
    "ModerationOutput",
    "ModerationOutputModerationResult",
    "ModerationOutputError",
    "PromptCacheOptions",
    "Reasoning",
]


class IncompleteDetails(BaseModel):
    """Details about why the response is incomplete."""

    reason: Optional[Literal["max_output_tokens", "content_filter"]] = None
    """The reason why the response is incomplete."""


class ToolChoiceBetaSpecificProgrammaticToolCallingParam(BaseModel):
    type: Literal["programmatic_tool_calling"]
    """The tool to call. Always `programmatic_tool_calling`."""


ToolChoice: TypeAlias = Union[
    BetaToolChoiceOptions,
    BetaToolChoiceAllowed,
    BetaToolChoiceTypes,
    BetaToolChoiceFunction,
    BetaToolChoiceMcp,
    BetaToolChoiceCustom,
    ToolChoiceBetaSpecificProgrammaticToolCallingParam,
    BetaToolChoiceApplyPatch,
    BetaToolChoiceShell,
]


class Conversation(BaseModel):
    """The conversation that this response belonged to.

    Input items and output items from this response were automatically added to this conversation.
    """

    id: str
    """The unique ID of the conversation that this response was associated with."""


class ModerationInputModerationResult(BaseModel):
    """A moderation result produced for the response input or output."""

    categories: Dict[str, bool]
    """
    A dictionary of moderation categories to booleans, True if the input is flagged
    under this category.
    """

    category_applied_input_types: Dict[str, List[Literal["text", "image"]]]
    """Which modalities of input are reflected by the score for each category."""

    category_scores: Dict[str, float]
    """A dictionary of moderation categories to scores."""

    flagged: bool
    """A boolean indicating whether the content was flagged by any category."""

    model: str
    """The moderation model that produced this result."""

    type: Literal["moderation_result"]
    """
    The object type, which was always `moderation_result` for successful moderation
    results.
    """


class ModerationInputError(BaseModel):
    """An error produced while attempting moderation for the response input or output."""

    code: str
    """The error code."""

    message: str
    """The error message."""

    type: Literal["error"]
    """The object type, which was always `error` for moderation failures."""


ModerationInput: TypeAlias = Annotated[
    Union[ModerationInputModerationResult, ModerationInputError], PropertyInfo(discriminator="type")
]


class ModerationOutputModerationResult(BaseModel):
    """A moderation result produced for the response input or output."""

    categories: Dict[str, bool]
    """
    A dictionary of moderation categories to booleans, True if the input is flagged
    under this category.
    """

    category_applied_input_types: Dict[str, List[Literal["text", "image"]]]
    """Which modalities of input are reflected by the score for each category."""

    category_scores: Dict[str, float]
    """A dictionary of moderation categories to scores."""

    flagged: bool
    """A boolean indicating whether the content was flagged by any category."""

    model: str
    """The moderation model that produced this result."""

    type: Literal["moderation_result"]
    """
    The object type, which was always `moderation_result` for successful moderation
    results.
    """


class ModerationOutputError(BaseModel):
    """An error produced while attempting moderation for the response input or output."""

    code: str
    """The error code."""

    message: str
    """The error message."""

    type: Literal["error"]
    """The object type, which was always `error` for moderation failures."""


ModerationOutput: TypeAlias = Annotated[
    Union[ModerationOutputModerationResult, ModerationOutputError], PropertyInfo(discriminator="type")
]


class Moderation(BaseModel):
    """
    Moderation results for the response input and output, if moderated completions were requested.
    """

    input: ModerationInput
    """Moderation for the response input."""

    output: ModerationOutput
    """Moderation for the response output."""


class PromptCacheOptions(BaseModel):
    """The prompt-caching options that were applied to the response.

    Supported for `gpt-5.6` and later models.
    """

    mode: Literal["implicit", "explicit"]
    """Whether implicit prompt-cache breakpoints were enabled."""

    ttl: Literal["30m"]
    """The minimum lifetime applied to each cache breakpoint."""


class Reasoning(BaseModel):
    """**gpt-5 and o-series models only**

    Configuration options for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning).
    """

    context: Optional[Literal["auto", "current_turn", "all_turns"]] = None
    """
    Controls which reasoning items are rendered back to the model on later turns. If
    omitted or set to `auto`, the model determines the context mode. The `gpt-5.6`
    model family defaults to `all_turns`; earlier models default to `current_turn`.

    When returned on a response, this is the effective reasoning context mode used
    for the response.
    """

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]] = None
    """Constrains effort on reasoning for reasoning models.

    Currently supported values are `none`, `minimal`, `low`, `medium`, `high`,
    `xhigh`, and `max`. Reducing reasoning effort can result in faster responses and
    fewer tokens used on reasoning in a response. Not all reasoning models support
    every value. See the
    [reasoning guide](https://platform.openai.com/docs/guides/reasoning) for
    model-specific support.
    """

    generate_summary: Optional[Literal["auto", "concise", "detailed"]] = None
    """**Deprecated:** use `summary` instead.

    A summary of the reasoning performed by the model. This can be useful for
    debugging and understanding the model's reasoning process. One of `auto`,
    `concise`, or `detailed`.
    """

    mode: Union[str, Literal["standard", "pro"], None] = None
    """Controls the reasoning execution mode for the request.

    When returned on a response, this is the effective execution mode.
    """

    summary: Optional[Literal["auto", "concise", "detailed"]] = None
    """A summary of the reasoning performed by the model.

    This can be useful for debugging and understanding the model's reasoning
    process. One of `auto`, `concise`, or `detailed`.

    `concise` is supported for `computer-use-preview` models and all reasoning
    models after `gpt-5`.
    """


class BetaResponse(BaseModel):
    id: str
    """Unique identifier for this Response."""

    created_at: float
    """Unix timestamp (in seconds) of when this Response was created."""

    error: Optional[BetaResponseError] = None
    """An error object returned when the model fails to generate a Response."""

    incomplete_details: Optional[IncompleteDetails] = None
    """Details about why the response is incomplete."""

    instructions: Union[str, List[BetaResponseInputItem], None] = None
    """A system (or developer) message inserted into the model's context.

    When using along with `previous_response_id`, the instructions from a previous
    response will not be carried over to the next response. This makes it simple to
    swap out system (or developer) messages in new responses.
    """

    metadata: Optional[Dict[str, str]] = None
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    model: Union[
        Literal[
            "gpt-5.6-sol",
            "gpt-5.6-terra",
            "gpt-5.6-luna",
            "gpt-5.4",
            "gpt-5.4-mini",
            "gpt-5.4-nano",
            "gpt-5.4-mini-2026-03-17",
            "gpt-5.4-nano-2026-03-17",
            "gpt-5.3-chat-latest",
            "gpt-5.2",
            "gpt-5.2-2025-12-11",
            "gpt-5.2-chat-latest",
            "gpt-5.2-pro",
            "gpt-5.2-pro-2025-12-11",
            "gpt-5.1",
            "gpt-5.1-2025-11-13",
            "gpt-5.1-codex",
            "gpt-5.1-mini",
            "gpt-5.1-chat-latest",
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-5-2025-08-07",
            "gpt-5-mini-2025-08-07",
            "gpt-5-nano-2025-08-07",
            "gpt-5-chat-latest",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4.1-2025-04-14",
            "gpt-4.1-mini-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
            "o4-mini",
            "o4-mini-2025-04-16",
            "o3",
            "o3-2025-04-16",
            "o3-mini",
            "o3-mini-2025-01-31",
            "o1",
            "o1-2024-12-17",
            "o1-preview",
            "o1-preview-2024-09-12",
            "o1-mini",
            "o1-mini-2024-09-12",
            "gpt-4o",
            "gpt-4o-2024-11-20",
            "gpt-4o-2024-08-06",
            "gpt-4o-2024-05-13",
            "gpt-4o-audio-preview",
            "gpt-4o-audio-preview-2024-10-01",
            "gpt-4o-audio-preview-2024-12-17",
            "gpt-4o-audio-preview-2025-06-03",
            "gpt-4o-mini-audio-preview",
            "gpt-4o-mini-audio-preview-2024-12-17",
            "gpt-4o-search-preview",
            "gpt-4o-mini-search-preview",
            "gpt-4o-search-preview-2025-03-11",
            "gpt-4o-mini-search-preview-2025-03-11",
            "chatgpt-4o-latest",
            "codex-mini-latest",
            "gpt-4o-mini",
            "gpt-4o-mini-2024-07-18",
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09",
            "gpt-4-0125-preview",
            "gpt-4-turbo-preview",
            "gpt-4-1106-preview",
            "gpt-4-vision-preview",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-4-32k-0613",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-16k-0613",
            "o1-pro",
            "o1-pro-2025-03-19",
            "o3-pro",
            "o3-pro-2025-06-10",
            "o3-deep-research",
            "o3-deep-research-2025-06-26",
            "o4-mini-deep-research",
            "o4-mini-deep-research-2025-06-26",
            "computer-use-preview",
            "computer-use-preview-2025-03-11",
            "gpt-5-codex",
            "gpt-5-pro",
            "gpt-5-pro-2025-10-06",
            "gpt-5.1-codex-max",
        ],
        str,
    ]
    """Model ID used to generate the response, like `gpt-4o` or `o3`.

    OpenAI offers a wide range of models with different capabilities, performance
    characteristics, and price points. Refer to the
    [model guide](https://platform.openai.com/docs/models) to browse and compare
    available models.
    """

    object: Literal["response"]
    """The object type of this resource - always set to `response`."""

    output: List[BetaResponseOutputItem]
    """An array of content items generated by the model.

    - The length and order of items in the `output` array is dependent on the
      model's response.
    - Rather than accessing the first item in the `output` array and assuming it's
      an `assistant` message with the content generated by the model, you might
      consider using the `output_text` property where supported in SDKs.
    """

    parallel_tool_calls: bool
    """Whether to allow the model to run tool calls in parallel."""

    temperature: Optional[float] = None
    """What sampling temperature to use, between 0 and 2.

    Higher values like 0.8 will make the output more random, while lower values like
    0.2 will make it more focused and deterministic. We generally recommend altering
    this or `top_p` but not both.
    """

    tool_choice: ToolChoice
    """
    How the model should select which tool (or tools) to use when generating a
    response. See the `tools` parameter to see how to specify which tools the model
    can call.
    """

    tools: List[BetaTool]
    """An array of tools the model may call while generating a response.

    You can specify which tool to use by setting the `tool_choice` parameter.

    We support the following categories of tools:

    - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
      capabilities, like
      [web search](https://platform.openai.com/docs/guides/tools-web-search) or
      [file search](https://platform.openai.com/docs/guides/tools-file-search).
      Learn more about
      [built-in tools](https://platform.openai.com/docs/guides/tools).
    - **MCP Tools**: Integrations with third-party systems via custom MCP servers or
      predefined connectors such as Google Drive and SharePoint. Learn more about
      [MCP Tools](https://platform.openai.com/docs/guides/tools-connectors-mcp).
    - **Function calls (custom tools)**: Functions that are defined by you, enabling
      the model to call your own code with strongly typed arguments and outputs.
      Learn more about
      [function calling](https://platform.openai.com/docs/guides/function-calling).
      You can also use custom tools to call your own code.
    """

    top_p: Optional[float] = None
    """
    An alternative to sampling with temperature, called nucleus sampling, where the
    model considers the results of the tokens with top_p probability mass. So 0.1
    means only the tokens comprising the top 10% probability mass are considered.

    We generally recommend altering this or `temperature` but not both.
    """

    background: Optional[bool] = None
    """
    Whether to run the model response in the background.
    [Learn more](https://platform.openai.com/docs/guides/background).
    """

    completed_at: Optional[float] = None
    """
    Unix timestamp (in seconds) of when this Response was completed. Only present
    when the status is `completed`.
    """

    conversation: Optional[Conversation] = None
    """The conversation that this response belonged to.

    Input items and output items from this response were automatically added to this
    conversation.
    """

    max_output_tokens: Optional[int] = None
    """
    An upper bound for the number of tokens that can be generated for a response,
    including visible output tokens and
    [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).
    """

    max_tool_calls: Optional[int] = None
    """
    The maximum number of total calls to built-in tools that can be processed in a
    response. This maximum number applies across all built-in tool calls, not per
    individual tool. Any further attempts to call a tool by the model will be
    ignored.
    """

    moderation: Optional[Moderation] = None
    """
    Moderation results for the response input and output, if moderated completions
    were requested.
    """

    previous_response_id: Optional[str] = None
    """The unique ID of the previous response to the model.

    Use this to create multi-turn conversations. Learn more about
    [conversation state](https://platform.openai.com/docs/guides/conversation-state).
    Cannot be used in conjunction with `conversation`.
    """

    prompt: Optional[BetaResponsePrompt] = None
    """
    Reference to a prompt template and its variables.
    [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).
    """

    prompt_cache_key: Optional[str] = None
    """
    Used by OpenAI to cache responses for similar requests to optimize your cache
    hit rates. Replaces the `user` field.
    [Learn more](https://platform.openai.com/docs/guides/prompt-caching).
    """

    prompt_cache_options: Optional[PromptCacheOptions] = None
    """The prompt-caching options that were applied to the response.

    Supported for `gpt-5.6` and later models.
    """

    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] = None
    """Deprecated. Use `prompt_cache_options.ttl` instead.

    The retention policy for the prompt cache. Set to `24h` to enable extended
    prompt caching, which keeps cached prefixes active for longer, up to a maximum
    of 24 hours.
    [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).
    This field expresses a maximum retention policy, while
    `prompt_cache_options.ttl` expresses a minimum cache lifetime. The two fields
    are independent and do not interact. For `gpt-5.5`, `gpt-5.5-pro`, and future
    models, only `24h` is supported.

    For older models that support both `in_memory` and `24h`, the default depends on
    your organization's data retention policy:

    - Organizations without ZDR enabled default to `24h`.
    - Organizations with ZDR enabled default to `in_memory` when
      `prompt_cache_retention` is not specified.
    """

    reasoning: Optional[Reasoning] = None
    """**gpt-5 and o-series models only**

    Configuration options for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning).
    """

    safety_identifier: Optional[str] = None
    """
    A stable identifier used to help detect users of your application that may be
    violating OpenAI's usage policies. The IDs should be a string that uniquely
    identifies each user, with a maximum length of 64 characters. We recommend
    hashing their username or email address, in order to avoid sending us any
    identifying information.
    [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).
    """

    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] = None
    """Specifies the processing type used for serving the request.

    - If set to 'auto', then the request will be processed with the service tier
      configured in the Project settings. Unless otherwise configured, the Project
      will use 'default'.
    - If set to 'default', then the request will be processed with the standard
      pricing and performance for the selected model.
    - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
      '[priority](https://openai.com/api-priority-processing/)', then the request
      will be processed with the corresponding service tier.
    - When not set, the default behavior is 'auto'.

    When the `service_tier` parameter is set, the response body will include the
    `service_tier` value based on the processing mode actually used to serve the
    request. This response value may be different from the value set in the
    parameter.
    """

    status: Optional[BetaResponseStatus] = None
    """The status of the response generation.

    One of `completed`, `failed`, `in_progress`, `cancelled`, `queued`, or
    `incomplete`.
    """

    text: Optional[BetaResponseTextConfig] = None
    """Configuration options for a text response from the model.

    Can be plain text or structured JSON data. Learn more:

    - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
    - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
    """

    top_logprobs: Optional[int] = None
    """
    An integer between 0 and 20 specifying the maximum number of most likely tokens
    to return at each token position, each with an associated log probability. In
    some cases, the number of returned tokens may be fewer than requested.
    """

    truncation: Optional[Literal["auto", "disabled"]] = None
    """The truncation strategy to use for the model response.

    - `auto`: If the input to this Response exceeds the model's context window size,
      the model will truncate the response to fit the context window by dropping
      items from the beginning of the conversation.
    - `disabled` (default): If the input size will exceed the context window size
      for a model, the request will fail with a 400 error.
    """

    usage: Optional[BetaResponseUsage] = None
    """
    Represents token usage details including input tokens, output tokens, a
    breakdown of output tokens, and the total tokens used.
    """

    user: Optional[str] = None
    """This field is being replaced by `safety_identifier` and `prompt_cache_key`.

    Use `prompt_cache_key` instead to maintain caching optimizations. A stable
    identifier for your end-users. Used to boost cache hit rates by better bucketing
    similar requests and to help OpenAI detect and prevent abuse.
    [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).
    """

    @property
    def output_text(self) -> str:
        """Convenience property that returns the response's output text.

        For multi-agent responses, this returns text from the last root
        `final_answer` message. Otherwise, it aggregates all `output_text` content
        blocks from the `output` list.
        """
        has_agent_metadata = False
        final_root_message: Optional[BetaResponseOutputMessage] = None

        for output in self.output:
            if output.type != "message" or output.agent is None:
                continue

            has_agent_metadata = True
            if output.agent.agent_name == "/root" and output.phase == "final_answer":
                final_root_message = output

        if has_agent_metadata and final_root_message is None:
            return ""

        texts: List[str] = []
        for output in self.output:
            if output.type != "message":
                continue
            if has_agent_metadata and output is not final_root_message:
                continue

            for content in output.content:
                if content.type == "output_text":
                    texts.append(content.text)

        return "".join(texts)
