# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .eval_jsonl_file_id_source_param import EvalJSONLFileIDSourceParam
from .eval_jsonl_file_content_source_param import EvalJSONLFileContentSourceParam

__all__ = ["CreateEvalJSONLRunDataSourceParam", "Source"]

Source: TypeAlias = Union[EvalJSONLFileContentSourceParam, EvalJSONLFileIDSourceParam]


class CreateEvalJSONLRunDataSourceParam(TypedDict, total=False):
    source: Required[Source]

    type: Required[Literal["jsonl"]]
    """The type of data source. Always `jsonl`."""
