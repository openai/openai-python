# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .shared_params.metadata import Metadata
from .graders.python_grader_param import PythonGraderParam
from .graders.score_model_grader_param import ScoreModelGraderParam
from .graders.string_check_grader_param import StringCheckGraderParam
from .responses.response_input_text_param import ResponseInputTextParam
from .graders.text_similarity_grader_param import TextSimilarityGraderParam

__all__ = [
    "EvalCreateParams",
    "DataSourceConfig",
    "DataSourceConfigCustom",
    "DataSourceConfigStoredCompletions",
    "TestingCriterion",
    "TestingCriterionLabelModel",
    "TestingCriterionLabelModelInput",
    "TestingCriterionLabelModelInputSimpleInputMessage",
    "TestingCriterionLabelModelInputEvalItem",
    "TestingCriterionLabelModelInputEvalItemContent",
    "TestingCriterionLabelModelInputEvalItemContentOutputText",
    "TestingCriterionTextSimilarity",
    "TestingCriterionPython",
    "TestingCriterionScoreModel",
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


class DataSourceConfigCustom(TypedDict, total=False):
    item_schema: Required[Dict[str, object]]
    """The json schema for each row in the data source."""

    type: Required[Literal["custom"]]
    """The type of data source. Always `custom`."""

    include_sample_schema: bool
    """
    Whether the eval should expect you to populate the sample namespace (ie, by
    generating responses off of your data source)
    """


class DataSourceConfigStoredCompletions(TypedDict, total=False):
    type: Required[Literal["stored_completions"]]
    """The type of data source. Always `stored_completions`."""

    metadata: Dict[str, object]
    """Metadata filters for the stored completions data source."""


DataSourceConfig: TypeAlias = Union[DataSourceConfigCustom, DataSourceConfigStoredCompletions]


class TestingCriterionLabelModelInputSimpleInputMessage(TypedDict, total=False):
    content: Required[str]
    """The content of the message."""

    role: Required[str]
    """The role of the message (e.g. "system", "assistant", "user")."""


class TestingCriterionLabelModelInputEvalItemContentOutputText(TypedDict, total=False):
    text: Required[str]
    """The text output from the model."""

    type: Required[Literal["output_text"]]
    """The type of the output text. Always `output_text`."""


TestingCriterionLabelModelInputEvalItemContent: TypeAlias = Union[
    str, ResponseInputTextParam, TestingCriterionLabelModelInputEvalItemContentOutputText
]


class TestingCriterionLabelModelInputEvalItem(TypedDict, total=False):
    content: Required[TestingCriterionLabelModelInputEvalItemContent]
    """Text inputs to the model - can contain template strings."""

    role: Required[Literal["user", "assistant", "system", "developer"]]
    """The role of the message input.

    One of `user`, `assistant`, `system`, or `developer`.
    """

    type: Literal["message"]
    """The type of the message input. Always `message`."""


TestingCriterionLabelModelInput: TypeAlias = Union[
    TestingCriterionLabelModelInputSimpleInputMessage, TestingCriterionLabelModelInputEvalItem
]


class TestingCriterionLabelModel(TypedDict, total=False):
    input: Required[Iterable[TestingCriterionLabelModelInput]]
    """A list of chat messages forming the prompt or context.

    May include variable references to the "item" namespace, ie {{item.name}}.
    """

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


class TestingCriterionTextSimilarity(TextSimilarityGraderParam, total=False):
    __test__ = False
    pass_threshold: Required[float]
    """The threshold for the score."""


class TestingCriterionPython(PythonGraderParam, total=False):
    __test__ = False
    pass_threshold: float
    """The threshold for the score."""


class TestingCriterionScoreModel(ScoreModelGraderParam, total=False):
    __test__ = False
    pass_threshold: float
    """The threshold for the score."""


TestingCriterion: TypeAlias = Union[
    TestingCriterionLabelModel,
    StringCheckGraderParam,
    TestingCriterionTextSimilarity,
    TestingCriterionPython,
    TestingCriterionScoreModel,
]
