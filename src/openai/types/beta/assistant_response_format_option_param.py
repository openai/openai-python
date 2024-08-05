# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypeAlias

from .assistant_response_format_param import AssistantResponseFormatParam

__all__ = ["AssistantResponseFormatOptionParam"]

AssistantResponseFormatOptionParam: TypeAlias = Union[Literal["none", "auto"], AssistantResponseFormatParam]
