# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "AssistantCreateParams",
    "Tool",
    "ToolAssistantToolsCode",
    "ToolAssistantToolsRetrieval",
    "ToolAssistantToolsFunction",
    "ToolAssistantToolsFunctionFunction",
]


class AssistantCreateParams(TypedDict, total=False):
    model: Required[str]
    """ID of the model to use.

    You can use the
    [List models](https://platform.openai.com/docs/api-reference/models/list) API to
    see all of your available models, or see our
    [Model overview](https://platform.openai.com/docs/models/overview) for
    descriptions of them.
    """

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

    metadata: Optional[object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """

    name: Optional[str]
    """The name of the assistant. The maximum length is 256 characters."""

    tools: List[Tool]
    """A list of tool enabled on the assistant.

    There can be a maximum of 128 tools per assistant. Tools can be of types
    `code_interpreter`, `retrieval`, or `function`.
    """


class ToolAssistantToolsCode(TypedDict, total=False):
    type: Required[Literal["code_interpreter"]]
    """The type of tool being defined: `code_interpreter`"""


class ToolAssistantToolsRetrieval(TypedDict, total=False):
    type: Required[Literal["retrieval"]]
    """The type of tool being defined: `retrieval`"""


class ToolAssistantToolsFunctionFunction(TypedDict, total=False):
    description: Required[str]
    """
    A description of what the function does, used by the model to choose when and
    how to call the function.
    """

    name: Required[str]
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    parameters: Required[Dict[str, object]]
    """The parameters the functions accepts, described as a JSON Schema object.

    See the [guide](https://platform.openai.com/docs/guides/gpt/function-calling)
    for examples, and the
    [JSON Schema reference](https://json-schema.org/understanding-json-schema/) for
    documentation about the format.

    To describe a function that accepts no parameters, provide the value
    `{"type": "object", "properties": {}}`.
    """


class ToolAssistantToolsFunction(TypedDict, total=False):
    function: Required[ToolAssistantToolsFunctionFunction]
    """The function definition."""

    type: Required[Literal["function"]]
    """The type of tool being defined: `function`"""


Tool = Union[ToolAssistantToolsCode, ToolAssistantToolsRetrieval, ToolAssistantToolsFunction]
