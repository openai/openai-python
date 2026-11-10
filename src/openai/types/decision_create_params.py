# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_input_text_param import DecisionInputTextParam
from .decision_input_image_param import DecisionInputImageParam
from .decision_input_part_union_param import DecisionInputPartUnionParam
from .shared_params.decision_question_input_part import DecisionQuestionInputPart

__all__ = [
    "DecisionCreateParams",
    "InputUnionMember1",
    "InputUnionMember1DecisionInputUserMessage",
    "InputUnionMember1DecisionInputDeveloperMessage",
    "InputUnionMember1DecisionInputSystemMessage",
    "InputUnionMember1DecisionInputAssistantMessage",
    "InputDecisionInputAssistantMessageContentDecisionInputAssistantContentParts",
    "InputDecisionInputAssistantMessageContentDecisionInputAssistantContentPartDecisionInputOutputText",
    "InputDecisionInputAssistantMessageContentDecisionInputAssistantContentPartDecisionInputRefusal",
    "InputUnionMember1DecisionInputFunctionCall",
    "InputUnionMember1DecisionInputFunctionCallOutput",
    "InputUnionMember1FunctionCallOutputOutputParts",
    "InputUnionMember1DecisionInputCustomToolCall",
    "InputUnionMember1DecisionInputCustomToolCallOutput",
    "InputUnionMember1CustomToolCallOutputOutputParts",
    "Question",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamChoiceChoice",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
    "PromptCacheOptions",
]


class DecisionCreateParams(TypedDict, total=False):
    input: Required[Union[str, Iterable[InputUnionMember1]]]
    """The input to evaluate for every question.

    Provide a text string or an ordered array of messages, function calls and
    outputs, or custom tool calls and outputs. Each tool output must identify a
    matching call by call ID.
    """

    model: Required[str]
    """The model to use. Only `gpt-6-luna` is supported."""

    questions: Required[Iterable[Question]]
    """Ask 1–400 questions about the input.

    Each question can be a predicate, choice, or score. Answers come back in the
    same order.
    """

    prompt_cache_key: Optional[str]
    """Partition prompt cache reuse by caller-provided key."""

    prompt_cache_options: Optional[PromptCacheOptions]
    """Options for prompt caching.

    Supported for `gpt-5.6` and later models. By default, OpenAI automatically
    chooses one implicit cache breakpoint. You can add explicit breakpoints to
    content blocks with `prompt_cache_breakpoint`. Each request can write up to four
    breakpoints. For cache matching, OpenAI considers up to the latest 80
    breakpoints in the conversation, without a content-block lookback limit. Set
    `mode` to `explicit` to disable the implicit breakpoint. The `ttl` defaults to
    `30m`, which is currently the only supported value. See the
    [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
    for current details.
    """

    safety_identifier: Optional[str]
    """Opaque caller-provided end-user identifier, scoped by the verified org.

    Match Responses' limit; this is never the authenticated user identity.
    """


class InputUnionMember1DecisionInputUserMessage(TypedDict, total=False):
    """A user message containing input text, images, or JSON."""

    content: Required[Union[str, Iterable[DecisionInputPartUnionParam]]]
    """A text string or an ordered list of text, image, and JSON parts."""

    role: Required[Literal["user"]]

    type: Literal["message"]


class InputUnionMember1DecisionInputDeveloperMessage(TypedDict, total=False):
    """A developer message containing input text."""

    content: Required[Union[str, Iterable[DecisionInputTextParam]]]
    """A text string or an ordered list of input text parts."""

    role: Required[Literal["developer"]]

    type: Literal["message"]


class InputUnionMember1DecisionInputSystemMessage(TypedDict, total=False):
    """A system message containing input text."""

    content: Required[Union[str, Iterable[DecisionInputTextParam]]]
    """A text string or an ordered list of input text parts."""

    role: Required[Literal["system"]]

    type: Literal["message"]


class InputDecisionInputAssistantMessageContentDecisionInputAssistantContentPartDecisionInputOutputText(
    TypedDict, total=False
):
    text: Required[str]

    type: Required[Literal["output_text"]]


class InputDecisionInputAssistantMessageContentDecisionInputAssistantContentPartDecisionInputRefusal(
    TypedDict, total=False
):
    refusal: Required[str]

    type: Required[Literal["refusal"]]


InputDecisionInputAssistantMessageContentDecisionInputAssistantContentParts: TypeAlias = Union[
    InputDecisionInputAssistantMessageContentDecisionInputAssistantContentPartDecisionInputOutputText,
    InputDecisionInputAssistantMessageContentDecisionInputAssistantContentPartDecisionInputRefusal,
]


class InputUnionMember1DecisionInputAssistantMessage(TypedDict, total=False):
    """An assistant message containing output text or refusals."""

    content: Required[Union[str, Iterable[InputDecisionInputAssistantMessageContentDecisionInputAssistantContentParts]]]
    """A text string or an ordered list of output text and refusal parts."""

    role: Required[Literal["assistant"]]

    phase: Optional[Literal["commentary", "final_answer"]]
    """The phase of an assistant message."""

    type: Literal["message"]


class InputUnionMember1DecisionInputFunctionCall(TypedDict, total=False):
    arguments: Required[str]

    call_id: Required[str]

    name: Required[str]

    type: Required[Literal["function_call"]]

    id: Optional[str]

    namespace: Optional[str]

    status: Optional[Literal["in_progress", "completed", "incomplete"]]


InputUnionMember1FunctionCallOutputOutputParts: TypeAlias = Union[DecisionInputTextParam, DecisionInputImageParam]


class InputUnionMember1DecisionInputFunctionCallOutput(TypedDict, total=False):
    call_id: Required[str]

    output: Required[Union[str, Iterable[InputUnionMember1FunctionCallOutputOutputParts]]]
    """Text evidence or an ordered list of text and image parts."""

    type: Required[Literal["function_call_output"]]

    id: Optional[str]

    status: Optional[Literal["in_progress", "completed", "incomplete"]]


class InputUnionMember1DecisionInputCustomToolCall(TypedDict, total=False):
    call_id: Required[str]

    input: Required[str]

    name: Required[str]

    type: Required[Literal["custom_tool_call"]]

    id: Optional[str]

    namespace: Optional[str]

    status: Optional[Literal["in_progress", "completed", "incomplete"]]


InputUnionMember1CustomToolCallOutputOutputParts: TypeAlias = Union[DecisionInputTextParam, DecisionInputImageParam]


class InputUnionMember1DecisionInputCustomToolCallOutput(TypedDict, total=False):
    call_id: Required[str]

    output: Required[Union[str, Iterable[InputUnionMember1CustomToolCallOutputOutputParts]]]
    """Text evidence or an ordered list of text and image parts."""

    type: Required[Literal["custom_tool_call_output"]]

    id: Optional[str]

    status: Optional[Literal["in_progress", "completed", "incomplete"]]


InputUnionMember1: TypeAlias = Union[
    InputUnionMember1DecisionInputUserMessage,
    InputUnionMember1DecisionInputDeveloperMessage,
    InputUnionMember1DecisionInputSystemMessage,
    InputUnionMember1DecisionInputAssistantMessage,
    InputUnionMember1DecisionInputFunctionCall,
    InputUnionMember1DecisionInputFunctionCallOutput,
    InputUnionMember1DecisionInputCustomToolCall,
    InputUnionMember1DecisionInputCustomToolCallOutput,
]


class QuestionQuestionParamPredicate(TypedDict, total=False):
    """Estimate how likely it is that a statement about the input is true."""

    instructions: Required[Union[str, Iterable[DecisionQuestionInputPart]]]

    type: Required[Literal["predicate"]]
    """The type of the object. Always `predicate`."""

    name: str


class QuestionQuestionParamChoiceChoice(TypedDict, total=False):
    value: Required[Union[str, bool]]
    """
    Choice values are typed: a string and a boolean with the same text are distinct.
    """

    description: str


class QuestionQuestionParamChoice(TypedDict, total=False):
    """Choose from the supplied options based on the input."""

    choices: Required[Iterable[QuestionQuestionParamChoiceChoice]]
    """Provide between 2 and 255 choices. Each choice must be unique."""

    instructions: Required[Union[str, Iterable[DecisionQuestionInputPart]]]

    type: Required[Literal["choice"]]
    """The type of the object. Always `choice`."""

    name: str


class QuestionQuestionParamScoreLevel(TypedDict, total=False):
    label: Required[str]

    description: str


class QuestionQuestionParamScore(TypedDict, total=False):
    """Rate the input against the supplied ordered levels."""

    instructions: Required[Union[str, Iterable[DecisionQuestionInputPart]]]

    levels: Required[Iterable[QuestionQuestionParamScoreLevel]]

    type: Required[Literal["score"]]
    """The type of the object. Always `score`."""

    name: str


Question: TypeAlias = Union[QuestionQuestionParamPredicate, QuestionQuestionParamChoice, QuestionQuestionParamScore]


class PromptCacheOptions(TypedDict, total=False):
    """Options for prompt caching.

    Supported for `gpt-5.6` and later models. By default, OpenAI automatically chooses one implicit cache breakpoint. You can add explicit breakpoints to content blocks with `prompt_cache_breakpoint`. Each request can write up to four breakpoints. For cache matching, OpenAI considers up to the latest 80 breakpoints in the conversation, without a content-block lookback limit. Set `mode` to `explicit` to disable the implicit breakpoint. The `ttl` defaults to `30m`, which is currently the only supported value. See the [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) for current details.
    """

    mode: Optional[Literal["implicit", "explicit"]]
    """Controls whether OpenAI automatically creates an implicit cache breakpoint.

    Defaults to `implicit`. With `implicit`, OpenAI creates one implicit breakpoint
    and writes up to the latest three explicit breakpoints in the request. With
    `explicit`, OpenAI does not create an implicit breakpoint and writes up to the
    latest four explicit breakpoints. If there are no explicit breakpoints, the
    request does not use prompt caching.
    """

    ttl: Literal["30m"]
    """
    The minimum lifetime applied to every implicit and explicit cache breakpoint
    written by the request. Defaults to `30m`, which is currently the only supported
    value. The backend may retain cache entries for longer.
    """
