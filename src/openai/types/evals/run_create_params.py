# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, TypeAlias, TypedDict

from ..shared_params.metadata import Metadata
from .create_eval_jsonl_run_data_source_param import CreateEvalJSONLRunDataSourceParam
from .create_eval_completions_run_data_source_param import CreateEvalCompletionsRunDataSourceParam

__all__ = ["RunCreateParams", "DataSource"]


class RunCreateParams(TypedDict, total=False):
    data_source: Required[DataSource]
    """Details about the run's data source."""

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    name: str
    """The name of the run."""


DataSource: TypeAlias = Union[CreateEvalJSONLRunDataSourceParam, CreateEvalCompletionsRunDataSourceParam]
