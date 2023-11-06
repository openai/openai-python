# File generated from our OpenAPI spec by Stainless.

import builtins
from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Assistant", "Tool", "ToolCodeInterpreter", "ToolRetrieval", "ToolFunction", "ToolFunctionFunction"]


class ToolCodeInterpreter(BaseModel):
    type: Literal["code_interpreter"]
    """The type of tool being defined: `code_interpreter`"""


class ToolRetrieval(BaseModel):
    type: Literal["retrieval"]
    """The type of tool being defined: `retrieval`"""


class ToolFunctionFunction(BaseModel):
    description: str
    """
    A description of what the function does, used by the model to choose when and
    how to call the function.
    """

    name: str
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    parameters: Dict[str, builtins.object]
    """The parameters the functions accepts, described as a JSON Schema object.

    See the [guide](https://platform.openai.com/docs/guides/gpt/function-calling)
    for examples, and the
    [JSON Schema reference](https://json-schema.org/understanding-json-schema/) for
    documentation about the format.

    To describe a function that accepts no parameters, provide the value
    `{"type": "object", "properties": {}}`.
    """


class ToolFunction(BaseModel):
    function: ToolFunctionFunction
    """The function definition."""

    type: Literal["function"]
    """The type of tool being defined: `function`"""


Tool = Union[ToolCodeInterpreter, ToolRetrieval, ToolFunction]


class Assistant(BaseModel):
    id: str
    """The identifier, which can be referenced in API endpoints."""

    created_at: int
    """The Unix timestamp (in seconds) for when the assistant was created."""

    description: Optional[str]
    """The description of the assistant. The maximum length is 512 characters."""

    file_ids: List[str]
    """
    A list of [file](https://platform.openai.com/docs/api-reference/files) IDs
    attached to this assistant. There can be a maximum of 20 files attached to the
    assistant. Files are ordered by their creation date in ascending order.
    """

    instructions: Optional[str]
    """The system instructions that the assistant uses.

    The maximum length is 32768 characters.
    """

    metadata: Optional[builtins.object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """

    model: str
    """ID of the model to use.

    You can use the
    [List models](https://platform.openai.com/docs/api-reference/models/list) API to
    see all of your available models, or see our
    [Model overview](https://platform.openai.com/docs/models/overview) for
    descriptions of them.
    """

    name: Optional[str]
    """The name of the assistant. The maximum length is 256 characters."""

    object: Literal["assistant"]
    """The object type, which is always `assistant`."""

    tools: List[Tool]
    """A list of tool enabled on the assistant.

    There can be a maximum of 128 tools per assistant. Tools can be of types
    `code_interpreter`, `retrieval`, or `function`.
    """
