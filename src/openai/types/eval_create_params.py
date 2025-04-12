# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .shared_params.metadata import Metadata
from .eval_string_check_grader_param import EvalStringCheckGraderParam
from .eval_text_similarity_grader_param import EvalTextSimilarityGraderParam

__all__ = [
    "EvalCreateParams",
    "DataSourceConfig",
    "DataSourceConfigCustom",
    "DataSourceConfigStoredCompletions",
    "TestingCriterion",
    "TestingCriterionLabelModel",
    "TestingCriterionLabelModelInput",
    "TestingCriterionLabelModelInputSimpleInputMessage",
    "TestingCriterionLabelModelInputInputMessage",
    "TestingCriterionLabelModelInputInputMessageContent",
    "TestingCriterionLabelModelInputOutputMessage",
    "TestingCriterionLabelModelInputOutputMessageContent",
]


class EvalCreateParams(TypedDict, total=False):
    data_source_config: Required[DataSourceConfig]
    """The configuration for the data source used for the evaluation runs."""

    testing_criteria: Required[Iterable[TestingCriterion]]
    """A list of graders for all eval runs in this group."""

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    name: str
    """The name of the evaluation."""

    share_with_openai: bool
    """Indicates whether the evaluation is shared with OpenAI."""


class DataSourceConfigCustom(TypedDict, total=False):
    item_schema: Required[Dict[str, object]]
    """The json schema for the run data source items."""

    type: Required[Literal["custom"]]
    """The type of data source. Always `custom`."""

    include_sample_schema: bool
    """Whether to include the sample schema in the data source."""


class DataSourceConfigStoredCompletions(TypedDict, total=False):
    type: Required[Literal["stored_completions"]]
    """The type of data source. Always `stored_completions`."""

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """


DataSourceConfig: TypeAlias = Union[DataSourceConfigCustom, DataSourceConfigStoredCompletions]


class TestingCriterionLabelModelInputSimpleInputMessage(TypedDict, total=False):
    content: Required[str]
    """The content of the message."""

    role: Required[str]
    """The role of the message (e.g. "system", "assistant", "user")."""


class TestingCriterionLabelModelInputInputMessageContent(TypedDict, total=False):
    text: Required[str]
    """The text content."""

    type: Required[Literal["input_text"]]
    """The type of content, which is always `input_text`."""


class TestingCriterionLabelModelInputInputMessage(TypedDict, total=False):
    content: Required[TestingCriterionLabelModelInputInputMessageContent]

    role: Required[Literal["user", "system", "developer"]]
    """The role of the message. One of `user`, `system`, or `developer`."""

    type: Required[Literal["message"]]
    """The type of item, which is always `message`."""


class TestingCriterionLabelModelInputOutputMessageContent(TypedDict, total=False):
    text: Required[str]
    """The text content."""

    type: Required[Literal["output_text"]]
    """The type of content, which is always `output_text`."""


class TestingCriterionLabelModelInputOutputMessage(TypedDict, total=False):
    content: Required[TestingCriterionLabelModelInputOutputMessageContent]

    role: Required[Literal["assistant"]]
    """The role of the message. Must be `assistant` for output."""

    type: Required[Literal["message"]]
    """The type of item, which is always `message`."""


TestingCriterionLabelModelInput: TypeAlias = Union[
    TestingCriterionLabelModelInputSimpleInputMessage,
    TestingCriterionLabelModelInputInputMessage,
    TestingCriterionLabelModelInputOutputMessage,
]


class TestingCriterionLabelModel(TypedDict, total=False):
    input: Required[Iterable[TestingCriterionLabelModelInput]]

    labels: Required[List[str]]
    """The labels to classify to each item in the evaluation."""

    model: Required[str]
    """The model to use for the evaluation. Must support structured outputs."""

    name: Required[str]
    """The name of the grader."""

    passing_labels: Required[List[str]]
    """The labels that indicate a passing result. Must be a subset of labels."""

    type: Required[Literal["label_model"]]
    """The object type, which is always `label_model`."""


TestingCriterion: TypeAlias = Union[
    TestingCriterionLabelModel, EvalStringCheckGraderParam, EvalTextSimilarityGraderParam
]
