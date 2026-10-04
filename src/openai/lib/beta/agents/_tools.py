from __future__ import annotations

import json
import asyncio
import inspect
from copy import deepcopy
from types import SimpleNamespace
from typing import Any, Generic, Mapping, TypeVar, Callable, Iterable, Awaitable, Generator, cast, get_type_hints
from functools import partial
from typing_extensions import Protocol, overload

import pydantic

from ._schema import model_schema
from ...._utils import is_dict
from ...._compat import PYDANTIC_V1, model_dump, model_json, model_parse
from ..._pydantic import resolve_ref
from ...streaming.agents._types import ToolOutput
from ....types.beta.agent_tool_param import AgentToolConfigParamFunction

_ModelT = TypeVar("_ModelT", bound=pydantic.BaseModel)
_OutputT = TypeVar("_OutputT", bound=ToolOutput | Awaitable[ToolOutput], covariant=True)


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
        parameters = model_schema(model)
        root = parameters
        seen: set[str] = set()
        while isinstance(ref := root.get("$ref"), str) and ref not in seen:
            seen.add(ref)
            resolved = resolve_ref(root=parameters, ref=ref)
            if not is_dict(resolved):
                break
            root = cast(dict[str, Any], resolved)
        if root.get("type") != "object":
            raise TypeError(
                "Tool argument models must have an object JSON schema; root-level compositions are unsupported"
            )
        self._definition: AgentToolConfigParamFunction = {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": parameters,
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


def _tool_output(output: object) -> ToolOutput:
    if isinstance(output, pydantic.BaseModel):
        output = json.loads(model_json(output)) if PYDANTIC_V1 else model_dump(output, mode="json")
    if output is None or isinstance(output, str):
        return output
    if isinstance(output, Mapping):
        if not isinstance(output, dict):
            output = dict(cast(Mapping[str, object], output))
    elif isinstance(output, Iterable) and not isinstance(output, (bytes, bytearray)):
        if not isinstance(output, (list, tuple)):
            output = list(cast(Iterable[object], output))
        if output and all(
            is_dict(part)
            and len(part) == 2
            and (
                (part.get("type") == "input_text" and isinstance(part.get("text"), str))
                or (part.get("type") == "input_image" and isinstance(part.get("image_url"), str))
            )
            for part in cast(Iterable[object], output)
        ):
            return cast(ToolOutput, output)
    return json.dumps(output, separators=(",", ":"), allow_nan=False)


class _AwaitableToolOutput:
    def __init__(self, output: Awaitable[object]) -> None:
        self._output = output

    def __await__(self) -> Generator[Any, None, ToolOutput]:
        output = yield from self._output.__await__()
        return _tool_output(output)

    def close(self) -> None:
        if inspect.iscoroutine(self._output):
            self._output.close()
        elif isinstance(self._output, asyncio.Future):
            self._output.cancel()


@overload
def pydantic_function_tool(  # type: ignore[overload-overlap]
    model: type[_ModelT],
    *,
    handler: Callable[[_ModelT], Awaitable[object]],
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[Awaitable[ToolOutput]]: ...


@overload
def pydantic_function_tool(
    model: type[_ModelT],
    *,
    handler: Callable[[_ModelT], object],
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[ToolOutput]: ...


def pydantic_function_tool(
    model: type[_ModelT],
    *,
    handler: Callable[[_ModelT], object],
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[Any]:
    """Bind an explicit Pydantic argument model to a beta Agents callback.

    The callback receives a validated model instance and can be synchronous or
    asynchronous. Use asynchronous callbacks with ``AsyncOpenAI``. Argument schemas
    must be objects or local references to objects. Root-level schema compositions
    (such as union models) are unsupported; wrap a union in an ordinary model field.
    """

    async def invoke_async(arguments: _ModelT) -> ToolOutput:
        return _tool_output(await cast(Awaitable[object], handler(arguments)))

    def invoke(arguments: _ModelT) -> ToolOutput | Awaitable[ToolOutput]:
        output = handler(arguments)
        if inspect.isawaitable(output):
            return _AwaitableToolOutput(output)
        return _tool_output(output)

    return FunctionTool(
        model,
        invoke_async if inspect.iscoroutinefunction(handler) else invoke,
        name=model.__name__ if name is None else name,
        description=(model.__doc__ or "") if description is None else description,
    )


class _FunctionToolDecorator(Protocol):
    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, function: Callable[..., Awaitable[object]]
    ) -> FunctionTool[Awaitable[ToolOutput]]: ...

    @overload
    def __call__(self, function: Callable[..., object]) -> FunctionTool[ToolOutput]: ...


@overload
def function_tool(  # type: ignore[overload-overlap]
    function: Callable[..., Awaitable[object]],
    *,
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[Awaitable[ToolOutput]]: ...


@overload
def function_tool(
    function: Callable[..., object],
    *,
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[ToolOutput]: ...


@overload
def function_tool(
    function: None = None,
    *,
    name: str | None = None,
    description: str | None = None,
) -> _FunctionToolDecorator: ...


def function_tool(
    function: Callable[..., object] | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
) -> FunctionTool[Any] | _FunctionToolDecorator:
    """Adapt an annotated function or bound method into a beta Agents tool.

    Use directly or as ``@function_tool`` / ``@function_tool(name="lookup")``.
    Every argument must have a Pydantic-compatible annotation. Positional-only
    arguments, variadic arguments, and names starting with an underscore are
    unsupported; use an explicit Pydantic model for these signatures. Defaults
    and nested models are preserved. Bind application dependencies with closures
    or bound methods so they do not appear in the tool's arguments. Use an explicit
    Pydantic model when postponed types only exist in an enclosing local scope.
    """
    if function is None:
        return cast(_FunctionToolDecorator, partial(function_tool, name=name, description=description))

    signature = inspect.signature(function)
    annotation_source = inspect.unwrap(function)
    localns: dict[str, Any] = {}
    owner = None
    source_function = getattr(annotation_source, "__func__", annotation_source)
    if inspect.ismethod(function):
        bound_owner = function.__self__ if inspect.isclass(function.__self__) else type(function.__self__)
        owner = next(
            (
                cls
                for cls in bound_owner.__mro__
                if cls.__module__ == source_function.__module__
                and cls.__qualname__ == source_function.__qualname__.rpartition(".")[0]
            ),
            None,
        )
    if owner is None:
        # Static and transplanted methods can retain a module-visible lexical owner.
        namespace = getattr(annotation_source, "__globals__", {})
        for part in getattr(annotation_source, "__qualname__", "").split(".")[:-1]:
            owner = namespace.get(part)
            if not inspect.isclass(owner):
                owner = None
                break
            namespace = vars(owner)
    if owner is not None:
        localns = {name: value for cls in reversed(owner.__mro__) for name, value in vars(cls).items()}
    # Return annotations may be TYPE_CHECKING-only imports; tools only need inputs.
    annotations = get_type_hints(
        SimpleNamespace(
            __type_params__=getattr(owner, "__type_params__", ()) + getattr(source_function, "__type_params__", ()),
            __annotations__={
                name: parameter.annotation
                for name, parameter in signature.parameters.items()
                if parameter.annotation is not inspect.Parameter.empty
            },
        ),
        globalns=getattr(annotation_source, "__globals__", None),
        localns=localns,
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

    def invoke(arguments: pydantic.BaseModel) -> object:
        # getattr retains nested model instances; model_dump would turn them into dicts.
        return function(**{name: getattr(arguments, field) for field, name in aliases.items()})

    async def invoke_async(arguments: pydantic.BaseModel) -> object:
        return await cast(Awaitable[object], invoke(arguments))

    return pydantic_function_tool(
        model,
        handler=invoke_async if inspect.iscoroutinefunction(function) else invoke,
        name=function.__name__ if name is None else name,
        description=(inspect.getdoc(function) or "") if description is None else description,
    )
