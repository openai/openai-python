# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union

from .function_tool_param import FunctionToolParam
from .retrieval_tool_param import RetrievalToolParam
from .code_interpreter_tool_param import CodeInterpreterToolParam

__all__ = ["AssistantToolParam"]

AssistantToolParam = Union[CodeInterpreterToolParam, RetrievalToolParam, FunctionToolParam]
