# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._models import BaseModel

__all__ = [
    "CodeInterpreterToolCall",
    "CodeInterpreter",
    "CodeInterpreterOutput",
    "CodeInterpreterOutputLogs",
    "CodeInterpreterOutputImage",
    "CodeInterpreterOutputImageImage",
]


class CodeInterpreterOutputLogs(BaseModel):
    logs: str
    """The text output from the Code Interpreter tool call."""

    type: Literal["logs"]
    """Always `logs`."""


class CodeInterpreterOutputImageImage(BaseModel):
    file_id: str
    """
    The [file](https://platform.openai.com/docs/api-reference/files) ID of the
    image.
    """


class CodeInterpreterOutputImage(BaseModel):
    image: CodeInterpreterOutputImageImage

    type: Literal["image"]
    """Always `image`."""


CodeInterpreterOutput: TypeAlias = Annotated[
    Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage], PropertyInfo(discriminator="type")
]


class CodeInterpreter(BaseModel):
    input: str
    """The input to the Code Interpreter tool call."""

    outputs: List[CodeInterpreterOutput]
    """The outputs from the Code Interpreter tool call.

    Code Interpreter can output one or more items, including text (`logs`) or images
    (`image`). Each of these are represented by a different object type.
    """


class CodeInterpreterToolCall(BaseModel):
    id: str
    """The ID of the tool call."""

    code_interpreter: CodeInterpreter
    """The Code Interpreter tool call definition."""

    type: Literal["code_interpreter"]
    """The type of tool call.

    This is always going to be `code_interpreter` for this type of tool call.
    """
