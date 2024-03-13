# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

from ..shared import FunctionDefinition
from ..._models import BaseModel

__all__ = ["FunctionTool"]


class FunctionTool(BaseModel):
    function: FunctionDefinition

    type: Literal["function"]
    """The type of tool being defined: `function`"""
