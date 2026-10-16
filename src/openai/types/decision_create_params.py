# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_input_message_param import DecisionInputMessageParam

__all__ = [
    "DecisionCreateParams",
    "Question",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamChoiceChoice",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
    "PromptCacheOptions",
]


class DecisionCreateParams(TypedDict, total=False):
    input: Required[Union[str, Iterable[DecisionInputMessageParam]]]
    """The text or images to evaluate for every question.

    Provide a text string or user messages containing text and images. Images can be
    base64 data URLs or publicly accessible HTTP(S) URLs; at most 128 images are
    allowed across all messages in one request. Files, audio, tools, and item
    references are not supported.
    """

    model: Required[str]
    """The model to use. Only `gpt-6-luna` is supported."""

    questions: Required[Iterable[Question]]
    """Ask 1–200 questions about the input.

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


class QuestionQuestionParamPredicate(TypedDict, total=False):
    """Estimate how likely it is that a statement about the input is true."""

    instructions: Required[str]

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

    instructions: Required[str]

    type: Required[Literal["choice"]]
    """The type of the object. Always `choice`."""

    name: str


class QuestionQuestionParamScoreLevel(TypedDict, total=False):
    label: Required[str]

    description: str


class QuestionQuestionParamScore(TypedDict, total=False):
    """Rate the input against the supplied ordered levels."""

    instructions: Required[str]

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
