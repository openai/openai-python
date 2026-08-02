# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaFunctionTool"]


class BetaFunctionTool(BaseModel):
    """Defines a function in your own code the model can choose to call.

    Learn more about [function calling](https://platform.openai.com/docs/guides/function-calling).
    """

    name: str
    """The name of the function to call."""

    parameters: Optional[Dict[str, object]] = None
    """A JSON schema object describing the parameters of the function."""

    strict: Optional[bool] = None
    """Whether strict parameter validation is enforced for this function tool."""

    type: Literal["function"]
    """The type of the function tool. Always `function`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]] = None
    """The tool invocation context(s)."""

    defer_loading: Optional[bool] = None
    """Whether this function is deferred and loaded via tool search."""

    description: Optional[str] = None
    """A description of the function.

    Used by the model to determine whether or not to call the function.
    """

    output_schema: Optional[Dict[str, object]] = None
    """
    A JSON schema object describing the JSON value encoded in string outputs for
    this function.
    """
