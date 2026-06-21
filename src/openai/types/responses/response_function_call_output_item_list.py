# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from .response_function_call_output_item import ResponseFunctionCallOutputItem, Compaction

__all__ = ["ResponseFunctionCallOutputItemList"]

ResponseFunctionCallOutputItemList: TypeAlias = List[Union[ResponseFunctionCallOutputItem, Compaction]]
