# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseFormatTextPython"]


class ResponseFormatTextPython(BaseModel):
    """Configure the model to generate valid Python code.

    See the
    [custom grammars guide](https://developers.openai.com/api/docs/guides/function-calling#context-free-grammars) for more details.
    """

    type: Literal["python"]
    """The type of response format being defined. Always `python`."""
