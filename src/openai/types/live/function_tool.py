# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["FunctionTool"]


class FunctionTool(BaseModel):
    """
    A function tool available to the Responses backend when the Live model delegates a task.
    """

    name: str
    """The name the delegated Responses model uses when calling this function."""

    type: Literal["function"]
    """The tool type. Always `function`."""

    description: Optional[str] = None
    """What the function does and when the delegated Responses model should call it."""

    parameters: Optional[Dict[str, object]] = None
    """A JSON Schema object describing the arguments accepted by the function."""

    strict: Optional[bool] = None
    """
    Whether the delegated Responses model must follow the function’s parameter
    schema exactly.
    """
