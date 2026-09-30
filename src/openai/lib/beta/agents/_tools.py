from __future__ import annotations

import inspect
from copy import deepcopy
from types import SimpleNamespace
from typing import Any, Generic, TypeVar, Callable, get_type_hints

import pydantic

from ...._compat import PYDANTIC_V1, model_parse, model_json_schema
from ....types.beta.agent_tool_param import AgentToolConfigParamFunction

_ModelT = TypeVar("_ModelT", bound=pydantic.BaseModel)
_OutputT = TypeVar("_OutputT", covariant=True)


class FunctionTool(Generic[_OutputT]):
    """A beta Agents function definition and its local, validated handler.

    Pass ``definition`` in the agent's tools and register this object as
    ``tool_handlers={tool.name: tool}`` on ``sessions.stream``. Arguments are
    validated with Pydantic before invoking the application callback.
    """

    def __init__(
        self,
        model: type[_ModelT],
        handler: Callable[[_ModelT], _OutputT],
        *,
        name: str,
        description: str,
    ) -> None:
        if not name:
            raise ValueError("Tool name must not be empty")
        self._definition: AgentToolConfigParamFunction = {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": model_json_schema(model),
        }

        def invoke(arguments: dict[str, Any]) -> _OutputT:
            return handler(model_parse(model, arguments))

        self._invoke = invoke

    @property
    def name(self) -> str:
        return self._definition["name"]

    @property
    def definition(self) -> AgentToolConfigParamFunction:
        """The flat hosted tool definition, without the local callback."""
        return deepcopy(self._definition)

    def __call__(self, arguments: dict[str, Any]) -> _OutputT:
        return self._invoke(arguments)


def pydantic_function_tool(
    model: type[_ModelT],
    *,
    handler: Callable[[_ModelT], _OutputT],
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[_OutputT]:
    """Bind an explicit Pydantic argument model to a beta Agents callback.

    The callback receives a validated model instance and can be synchronous or
    asynchronous. Use asynchronous callbacks with ``AsyncOpenAI``.
    """
    return FunctionTool(
        model,
        handler,
        name=model.__name__ if name is None else name,
        description=(model.__doc__ or "") if description is None else description,
    )


def function_tool(
    function: Callable[..., _OutputT],
    *,
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[_OutputT]:
    """Adapt an annotated function or bound method into a beta Agents tool.

    Every argument must have a Pydantic-compatible annotation. Positional-only
    arguments, variadic arguments, and names starting with an underscore are
    unsupported; use an explicit Pydantic model for these signatures. Defaults
    and nested models are preserved. Bind application dependencies with closures
    or bound methods so they do not appear in the tool's arguments.
    """
    signature = inspect.signature(function)
    # Return annotations may be TYPE_CHECKING-only imports; tools only need inputs.
    annotations = get_type_hints(
        SimpleNamespace(
            __annotations__={
                name: parameter.annotation
                for name, parameter in signature.parameters.items()
                if parameter.annotation is not inspect.Parameter.empty
            }
        ),
        globalns=getattr(function, "__globals__", None),
        include_extras=True,
    )
    fields: dict[str, Any] = {}
    aliases: dict[str, str] = {}
    for parameter in signature.parameters.values():
        if parameter.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            raise TypeError(f"Unsupported tool parameter: {parameter.name}")
        if parameter.name.startswith("_") or parameter.name not in annotations:
            raise TypeError(f"Tool parameter needs a public name and type annotation: {parameter.name}")
        default = ... if parameter.default is inspect.Parameter.empty else parameter.default
        field = f"argument_{len(fields)}"
        aliases[field] = parameter.name
        fields[field] = (annotations[parameter.name], default)

    # Use each supported Pydantic version's native validation and schema handling.
    if PYDANTIC_V1:
        config: Any = type("Config", (), {"extra": "forbid", "alias_generator": staticmethod(aliases.__getitem__)})
    else:
        config = pydantic.ConfigDict(extra="forbid", alias_generator=aliases.__getitem__)
    model = pydantic.create_model("ToolArguments", __config__=config, **fields)

    def invoke(arguments: pydantic.BaseModel) -> _OutputT:
        # getattr retains nested model instances; model_dump would turn them into dicts.
        return function(**{name: getattr(arguments, field) for field, name in aliases.items()})

    return pydantic_function_tool(
        model,
        handler=invoke,
        name=function.__name__ if name is None else name,
        description=(inspect.getdoc(function) or "") if description is None else description,
    )
