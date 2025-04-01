from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, List, Iterable, cast
from typing_extensions import TypeVar, assert_never

import pydantic

from .._tools import ResponsesPydanticFunctionTool
from ..._types import NotGiven
from ..._utils import is_given
from ..._compat import PYDANTIC_V2, model_parse_json
from ..._models import construct_type_unchecked
from .._pydantic import is_basemodel_type, is_dataclass_like_type
from ._completions import solve_response_format_t, type_to_response_format_param
from ...types.responses import (
    Response,
    ToolParam,
    ParsedContent,
    ParsedResponse,
    FunctionToolParam,
    ParsedResponseOutputItem,
    ParsedResponseOutputText,
    ResponseFunctionToolCall,
    ParsedResponseOutputMessage,
    ResponseFormatTextConfigParam,
    ParsedResponseFunctionToolCall,
)
from ...types.chat.completion_create_params import ResponseFormat

TextFormatT = TypeVar(
    "TextFormatT",
    # if it isn't given then we don't do any parsing
    default=None,
)


def type_to_text_format_param(type_: type) -> ResponseFormatTextConfigParam:
    response_format_dict = type_to_response_format_param(type_)
    assert is_given(response_format_dict)
    response_format_dict = cast(ResponseFormat, response_format_dict)  # pyright: ignore[reportUnnecessaryCast]
    assert response_format_dict["type"] == "json_schema"
    assert "schema" in response_format_dict["json_schema"]

    return {
        "type": "json_schema",
        "strict": True,
        "name": response_format_dict["json_schema"]["name"],
        "schema": response_format_dict["json_schema"]["schema"],
    }


def parse_response(
    *,
    text_format: type[TextFormatT] | NotGiven,
    input_tools: Iterable[ToolParam] | NotGiven | None,
    response: Response | ParsedResponse[object],
) -> ParsedResponse[TextFormatT]:
    solved_t = solve_response_format_t(text_format)
    output_list: List[ParsedResponseOutputItem[TextFormatT]] = []

    for output in response.output:
        if output.type == "message":
            content_list: List[ParsedContent[TextFormatT]] = []
            for item in output.content:
                if item.type != "output_text":
                    content_list.append(item)
                    continue

                content_list.append(
                    construct_type_unchecked(
                        type_=cast(Any, ParsedResponseOutputText)[solved_t],
                        value={
                            **item.to_dict(),
                            "parsed": parse_text(item.text, text_format=text_format),
                        },
                    )
                )

            output_list.append(
                construct_type_unchecked(
                    type_=cast(Any, ParsedResponseOutputMessage)[solved_t],
                    value={
                        **output.to_dict(),
                        "content": content_list,
                    },
                )
            )
        elif output.type == "function_call":
            output_list.append(
                construct_type_unchecked(
                    type_=ParsedResponseFunctionToolCall,
                    value={
                        **output.to_dict(),
                        "parsed_arguments": parse_function_tool_arguments(
                            input_tools=input_tools, function_call=output
                        ),
                    },
                )
            )
        elif (
            output.type == "computer_call"
            or output.type == "file_search_call"
            or output.type == "web_search_call"
            or output.type == "reasoning"
        ):
            output_list.append(output)
        elif TYPE_CHECKING:  # type: ignore
            assert_never(output)
        else:
            output_list.append(output)

    return cast(
        ParsedResponse[TextFormatT],
        construct_type_unchecked(
            type_=cast(Any, ParsedResponse)[solved_t],
            value={
                **response.to_dict(),
                "output": output_list,
            },
        ),
    )


def parse_text(text: str, text_format: type[TextFormatT] | NotGiven) -> TextFormatT | None:
    if not is_given(text_format):
        return None

    if is_basemodel_type(text_format):
        return cast(TextFormatT, model_parse_json(text_format, text))

    if is_dataclass_like_type(text_format):
        if not PYDANTIC_V2:
            raise TypeError(f"Non BaseModel types are only supported with Pydantic v2 - {text_format}")

        return pydantic.TypeAdapter(text_format).validate_json(text)

    raise TypeError(f"Unable to automatically parse response format type {text_format}")


def get_input_tool_by_name(*, input_tools: Iterable[ToolParam], name: str) -> FunctionToolParam | None:
    for tool in input_tools:
        if tool["type"] == "function" and tool.get("name") == name:
            return tool

    return None


def parse_function_tool_arguments(
    *,
    input_tools: Iterable[ToolParam] | NotGiven | None,
    function_call: ParsedResponseFunctionToolCall | ResponseFunctionToolCall,
) -> object:
    if input_tools is None or not is_given(input_tools):
        return None

    input_tool = get_input_tool_by_name(input_tools=input_tools, name=function_call.name)
    if not input_tool:
        return None

    tool = cast(object, input_tool)
    if isinstance(tool, ResponsesPydanticFunctionTool):
        return model_parse_json(tool.model, function_call.arguments)

    if not input_tool.get("strict"):
        return None

    return json.loads(function_call.arguments)
