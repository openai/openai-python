from __future__ import annotations

import sys
import json
from typing import Any, Callable, Awaitable, cast
from datetime import date
from typing_extensions import Annotated, assert_type

import httpx2
import pytest
import pydantic
from pydantic import Field, BaseModel, ValidationError

from openai import OpenAI, AsyncOpenAI
from openai._compat import PYDANTIC_V1, model_parse
from openai.lib.beta.agents import FunctionTool, function_tool, pydantic_function_tool
from openai.lib.streaming.agents._types import ToolOutput
from tests.lib.streaming.agents.test_streams import Server, EventBody, call, idle, turn_event


class Item(BaseModel):
    sku: str


class Reservation(BaseModel):
    item: Item
    quantity: int = Field(gt=0)


class Catalog:
    """A local stand-in for a bound application method."""

    def __init__(self) -> None:
        self.reservations: list[tuple[str, int]] = []

    def reserve(self, item: Item, quantity: int, *, product: str = "notebook") -> dict[str, object]:
        """Reserve an item from this catalog."""
        self.reservations.append((item.sku, quantity))
        return {"receipt": "test-receipt", "product": product}


def test_bound_action_schema_defaults_and_nested_models() -> None:
    catalog = Catalog()
    tool = function_tool(catalog.reserve)
    assert tool.name == "reserve"
    assert tool.definition["type"] == "function"
    assert tool.definition["description"] == "Reserve an item from this catalog."
    assert set(tool.definition["parameters"]["properties"]) == {"item", "quantity", "product"}  # type: ignore
    assert "self" not in tool.definition["parameters"]["properties"]  # type: ignore
    assert json.loads(cast(str, tool({"item": {"sku": "test-sku"}, "quantity": 3}))) == {
        "receipt": "test-receipt",
        "product": "notebook",
    }
    assert catalog.reservations == [("test-sku", 3)]
    definition = tool.definition
    definition["name"] = "changed"
    assert tool.name == "reserve"


@pytest.mark.parametrize(
    "arguments", [{}, {"item": {}, "quantity": 1}, {"item": {"sku": "a"}, "quantity": 1, "secret": "bad"}]
)
def test_invalid_annotations_do_not_execute(arguments: dict[str, Any]) -> None:
    catalog = Catalog()
    tool = function_tool(catalog.reserve)
    with pytest.raises(ValidationError):
        tool(arguments)
    assert catalog.reservations == []


def test_explicit_model_and_alias() -> None:
    class Arguments(BaseModel):
        quantity: int = Field(gt=0, alias="quantity_units")

    seen: list[Arguments] = []

    def handler(arguments: Arguments) -> str:
        seen.append(arguments)
        return str(arguments.quantity)

    tool = pydantic_function_tool(Arguments, name="reserve", description="Reserve items", handler=handler)
    assert tool({"quantity_units": 2}) == "2"
    assert isinstance(seen[0], Arguments)
    assert "quantity_units" in tool.definition["parameters"]["properties"]  # type: ignore
    with pytest.raises(ValidationError):
        tool({"quantity_units": 0})
    assert len(seen) == 1


def test_unsupported_signatures() -> None:
    def unannotated(value: Any) -> Any:
        return value

    unannotated.__annotations__ = {}

    def variadic(*args: str) -> str:
        return str(args)

    def keywords(**kwargs: str) -> str:
        return str(kwargs)

    for function in (unannotated, variadic, keywords):
        with pytest.raises(TypeError):
            function_tool(function)


def test_positional_only_rejected() -> None:
    def handler(value: str, /) -> str:
        return value

    with pytest.raises(TypeError):
        function_tool(handler)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("invalid", [False, True])
async def test_bound_action_through_existing_dispatch(asynchronous: bool, invalid: bool) -> None:
    catalog = Catalog()
    tool = function_tool(catalog.reserve, name="search")
    server = Server()
    arguments = {"item": {} if invalid else {"sku": "test-sku"}, "quantity": 3}
    event = call(arguments)
    server.body = EventBody([turn_event("created"), event, event, turn_event("completed"), idle()])
    options = {"input": "Reserve items", "tool_handlers": {tool.name: tool}, "extra_headers": {"X-App": "example"}}
    transport = httpx2.MockTransport(server.handle)
    if asynchronous:
        async with AsyncOpenAI(api_key="synthetic", http_client=httpx2.AsyncClient(transport=transport)) as client:
            async with client.beta.agents.sessions.stream("session_test", **options) as stream:  # type: ignore
                await stream.until_done()
    else:
        with OpenAI(api_key="synthetic", http_client=httpx2.Client(transport=transport)) as client:
            with client.beta.agents.sessions.stream("session_test", **options) as stream:  # type: ignore
                stream.until_done()
    assert catalog.reservations == ([] if invalid else [("test-sku", 3)])
    results = server.inputs()[1:]
    assert len(results) == 1
    assert results[0]["success"] is not invalid
    assert all(request.headers["X-App"] == "example" for request in server.requests)
    if not invalid:
        assert results[0]["output"] == '{"receipt":"test-receipt","product":"notebook"}'


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_async_action_requires_async_dispatch(asynchronous: bool) -> None:
    seen: list[Reservation] = []

    async def handler(arguments: Reservation) -> str:
        seen.append(arguments)
        return "test-receipt"

    tool = pydantic_function_tool(Reservation, name="search", handler=handler)
    server = Server()
    server.body = EventBody(
        [
            turn_event("created"),
            call({"item": {"sku": "test-sku"}, "quantity": 3}),
            turn_event("completed"),
            idle(),
        ]
    )
    transport = httpx2.MockTransport(server.handle)
    if asynchronous:
        async with AsyncOpenAI(api_key="synthetic", http_client=httpx2.AsyncClient(transport=transport)) as client:
            async with client.beta.agents.sessions.stream(
                "session_test", input="Reserve an item", tool_handlers={tool.name: tool}
            ) as stream:
                await stream.until_done()
    else:
        with OpenAI(api_key="synthetic", http_client=httpx2.Client(transport=transport)) as client:
            with client.beta.agents.sessions.stream(
                "session_test", input="Reserve an item", tool_handlers=cast(Any, {tool.name: tool})
            ) as stream:
                stream.until_done()
    assert len(seen) == int(asynchronous)
    assert server.inputs()[1]["success"] is asynchronous


def test_only_input_annotations_are_resolved() -> None:
    def lookup(order_id: str) -> str:
        return order_id

    lookup.__annotations__["return"] = "TypeCheckingOnlyOrder"
    assert function_tool(lookup)({"order_id": "test-order"}) == "test-order"


def test_reserved_parameter_names_and_annotated_constraints() -> None:
    def action(schema: str, dict: int, json: Annotated[int, Field(gt=0)]) -> str:
        return f"{schema}:{dict}:{json}"

    tool = function_tool(action)
    assert tool({"schema": "reserve", "dict": 2, "json": 3}) == "reserve:2:3"
    assert set(cast(dict[str, Any], tool.definition["parameters"]["properties"])) == {"schema", "dict", "json"}
    with pytest.raises(ValidationError):
        tool({"schema": "reserve", "dict": 2, "json": 0})


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "output, expected",
    [
        (3, "3"),
        (True, "true"),
        ([1, 2], "[1,2]"),
        ([], "[]"),
        ([{"type": "receipt", "content": "paid"}], '[{"type":"receipt","content":"paid"}]'),
        ({"type": "input_text", "content": "business"}, '{"type":"input_text","content":"business"}'),
        ([{"type": "input_text", "text": "receipt"}], [{"type": "input_text", "text": "receipt"}]),
        (
            [{"type": "input_image", "image_url": "https://example.com/receipt.png"}],
            [{"type": "input_image", "image_url": "https://example.com/receipt.png"}],
        ),
    ],
)
async def test_json_outputs_and_content_parts_through_dispatch(
    asynchronous: bool, output: object, expected: object
) -> None:
    seen: list[bool] = []

    def action() -> object:
        seen.append(True)
        return output

    async def async_action() -> object:
        return action()

    server = Server()
    server.body = EventBody([turn_event("created"), call({}), turn_event("completed"), idle()])
    transport = httpx2.MockTransport(server.handle)
    if asynchronous:
        async_tool = function_tool(async_action, name="search")
        async with AsyncOpenAI(api_key="synthetic", http_client=httpx2.AsyncClient(transport=transport)) as client:
            async with client.beta.agents.sessions.stream(
                "session_test", input="Run action", tool_handlers={async_tool.name: async_tool}
            ) as stream:
                await stream.until_done()
    else:
        sync_tool = function_tool(action, name="search")
        with OpenAI(api_key="synthetic", http_client=httpx2.Client(transport=transport)) as client:
            with client.beta.agents.sessions.stream(
                "session_test", input="Run action", tool_handlers={sync_tool.name: sync_tool}
            ) as stream:
                stream.until_done()
    assert seen == [True]
    assert server.inputs()[1]["success"] is True
    assert server.inputs()[1]["output"] == expected


async def test_sync_function_returning_awaitable() -> None:
    async def result() -> list[int]:
        return [1, 2]

    def action() -> Awaitable[list[int]]:
        return result()

    assert await function_tool(action)({}) == "[1,2]"

    class Arguments(BaseModel):
        pass

    def explicit_action(arguments: Arguments) -> Awaitable[list[int]]:
        assert isinstance(arguments, Arguments)
        return result()

    assert await pydantic_function_tool(Arguments, handler=explicit_action)({}) == "[1,2]"


def test_bound_class_namespaces() -> None:
    class Catalog:
        class Product(BaseModel):
            name: str

        def lookup(self, product: Product) -> str:
            return product.name

        @classmethod
        def lookup_class(cls, product: Product) -> str:
            return product.name

    class InheritedCatalog(Catalog):
        pass

    class ShadowedCatalog(Catalog):
        class Product(BaseModel):  # pyright: ignore[reportIncompatibleVariableOverride]
            sku: int

    for callback in (
        Catalog().lookup,
        InheritedCatalog().lookup,
        Catalog.lookup_class,
        ShadowedCatalog().lookup,
        ShadowedCatalog.lookup_class,
    ):
        assert function_tool(callback)({"product": {"name": "notebook"}}) == "notebook"


def test_static_method_class_namespaces() -> None:
    from types import ModuleType
    from functools import wraps

    module = ModuleType("typed_static_action_module")
    exec(
        "from __future__ import annotations\n"
        "from pydantic import BaseModel\n"
        "class Container:\n"
        "    class Catalog:\n"
        "        class Product(BaseModel):\n            name: str\n"
        "        @staticmethod\n"
        "        def lookup(product: Product) -> str:\n            return product.name\n"
        "class InheritedCatalog(Container.Catalog):\n"
        "    class Product(BaseModel):\n        sku: int\n",
        module.__dict__,
    )

    @wraps(module.Container.Catalog.lookup)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return module.Container.Catalog.lookup(*args, **kwargs)

    for callback in (module.Container.Catalog.lookup, module.InheritedCatalog.lookup, wrapped):
        assert function_tool(callback)({"product": {"name": "notebook"}}) == "notebook"


def test_cross_module_decorator_annotations() -> None:
    from types import ModuleType
    from functools import wraps

    module = ModuleType("typed_action_module")
    exec(
        "from __future__ import annotations\n"
        "from pydantic import BaseModel\n"
        "class Product(BaseModel):\n    name: str\n"
        "def action(product: Product) -> str:\n    return product.name\n",
        module.__dict__,
    )

    @wraps(module.action)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return module.action(*args, **kwargs)

    assert function_tool(wrapped)({"product": {"name": "notebook"}}) == "notebook"


def test_model_output_is_json_object() -> None:
    class Receipt(BaseModel):
        receipt: str
        day: date

    def action() -> Receipt:
        return Receipt(receipt="test-receipt", day=date(2026, 9, 30))

    assert json.loads(cast(str, function_tool(action)({}))) == {"receipt": "test-receipt", "day": "2026-09-30"}


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_mapping_results_rejected(value: float) -> None:
    def action() -> dict[str, object]:
        return {"nested": {"quantity": value}}

    with pytest.raises(ValueError):
        function_tool(action)({})


def test_concrete_results_are_not_copied() -> None:
    from unittest.mock import patch

    business = [{"receipt": "test-receipt"}]

    def action() -> list[dict[str, str]]:
        return business

    with patch("openai.lib.beta.agents._tools.json.dumps", wraps=json.dumps) as dumps:
        assert function_tool(action)({}) == '[{"receipt":"test-receipt"}]'
        assert dumps.call_args.args[0] is business

    content = [{"type": "input_text", "text": "test-receipt"}]
    assert function_tool(lambda: content)({}) is content


def test_sync_rejection_closes_underlying_coroutine() -> None:
    from types import CoroutineType
    from typing import Coroutine

    coroutines: list[Coroutine[Any, Any, int]] = []

    async def result() -> int:
        pytest.fail("Async callback must not execute through OpenAI")
        return 1

    def action() -> Coroutine[Any, Any, int]:
        coroutine = result()
        coroutines.append(coroutine)
        return coroutine

    tool = function_tool(action, name="search")
    server = Server()
    server.body = EventBody([turn_event("created"), call({}), turn_event("completed"), idle()])
    with OpenAI(
        api_key="synthetic", http_client=httpx2.Client(transport=httpx2.MockTransport(server.handle))
    ) as client:
        with client.beta.agents.sessions.stream(
            "session_test", input="Run action", tool_handlers=cast(Any, {tool.name: tool})
        ) as stream:
            stream.until_done()
    assert len(coroutines) == 1
    assert cast("CoroutineType[Any, Any, int]", coroutines[0]).cr_frame is None
    assert server.inputs()[1]["success"] is False


def test_string_valued_model_output() -> None:
    model = pydantic.create_model("TextOutput", __root__=(str, ...)) if PYDANTIC_V1 else pydantic.RootModel[str]

    def action() -> BaseModel:
        return model_parse(model, "paid")

    assert function_tool(action)({}) == "paid"


def test_non_object_argument_model_rejected() -> None:
    model = (
        pydantic.create_model("ArrayInput", __root__=(list[str], ...)) if PYDANTIC_V1 else pydantic.RootModel[list[str]]
    )

    def action(arguments: BaseModel) -> str:
        pytest.fail(f"Invalid argument model should be rejected before invocation: {type(arguments)}")

    with pytest.raises(TypeError, match="object JSON schema"):
        pydantic_function_tool(model, handler=action)


async def test_function_tool_decorator_forms() -> None:
    seen: list[str] = []

    @function_tool(name="lookup_order", description="Find delivery status")
    def lookup(order_id: str) -> dict[str, str]:
        seen.append(order_id)
        return {"order_id": order_id}

    @function_tool()
    def default_lookup(order_id: str) -> str:
        """Look up an order."""
        return order_id

    @function_tool
    def bare_lookup(order_id: str) -> str:
        return order_id

    assert_type(lookup, FunctionTool[ToolOutput])
    assert_type(default_lookup, FunctionTool[ToolOutput])
    assert_type(bare_lookup, FunctionTool[ToolOutput])
    assert lookup.name == "lookup_order"
    assert lookup.definition["description"] == "Find delivery status"
    assert default_lookup.name == "default_lookup"
    assert default_lookup.definition["description"] == "Look up an order."
    assert json.loads(cast(str, lookup({"order_id": "A123"}))) == {"order_id": "A123"}
    assert default_lookup({"order_id": "A123"}) == "A123"
    assert bare_lookup({"order_id": "A123"}) == "A123"
    with pytest.raises(ValidationError):
        lookup({})
    assert seen == ["A123"]

    @function_tool(name="async_lookup", description="Async delivery status")
    async def async_lookup(order_id: str) -> str:
        return order_id

    @function_tool()
    async def default_async_lookup(order_id: str) -> str:
        return order_id

    @function_tool
    async def bare_async_lookup(order_id: str) -> str:
        return order_id

    assert_type(async_lookup, FunctionTool[Awaitable[ToolOutput]])
    assert_type(default_async_lookup, FunctionTool[Awaitable[ToolOutput]])
    assert_type(bare_async_lookup, FunctionTool[Awaitable[ToolOutput]])
    for tool in (async_lookup, default_async_lookup, bare_async_lookup):
        assert await tool({"order_id": "A123"}) == "A123"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_model_results_rejected(value: float) -> None:
    class Receipt(BaseModel):
        quantity: float

    def action() -> Receipt:
        return Receipt(quantity=value)

    with pytest.raises(ValueError):
        function_tool(action)({})


def test_object_root_argument_model() -> None:
    from openai._compat import model_json_schema

    model = (
        pydantic.create_model("ObjectInput", __root__=(Reservation, ...))
        if PYDANTIC_V1
        else pydantic.RootModel[Reservation]
    )
    seen: list[BaseModel] = []

    def action(arguments: BaseModel) -> str:
        seen.append(arguments)
        reserve = getattr(arguments, "__root__" if PYDANTIC_V1 else "root")
        assert isinstance(reserve, Reservation)
        assert reserve.item.sku == "test-sku"
        return "paid"

    tool = pydantic_function_tool(model, handler=action)
    assert tool.definition["parameters"] == model_json_schema(model)
    assert tool({"item": {"sku": "test-sku"}, "quantity": 3}) == "paid"
    with pytest.raises(ValidationError):
        tool({"item": {"sku": "test-sku"}, "quantity": -1})
    assert len(seen) == 1


@pytest.mark.parametrize("task", [False, True])
async def test_sync_rejection_cancels_scheduled_awaitable(task: bool) -> None:
    import asyncio

    seen: list[bool] = []
    awaitables: list[asyncio.Future[int]] = []

    async def result() -> int:
        seen.append(True)
        return 1

    def action() -> asyncio.Future[int]:
        future = asyncio.create_task(result()) if task else asyncio.get_running_loop().create_future()
        awaitables.append(future)
        return future

    tool = function_tool(action, name="search")
    server = Server()
    server.body = EventBody([turn_event("created"), call({}), turn_event("completed"), idle()])
    with OpenAI(
        api_key="synthetic", http_client=httpx2.Client(transport=httpx2.MockTransport(server.handle))
    ) as client:
        with client.beta.agents.sessions.stream(
            "session_test", input="Run action", tool_handlers=cast(Any, {tool.name: tool})
        ) as stream:
            stream.until_done()
    await asyncio.sleep(0)
    assert len(awaitables) == 1 and awaitables[0].cancelled()
    assert seen == []
    assert server.inputs()[1]["success"] is False


def test_root_schema_compositions_have_explicit_supported_boundary() -> None:
    model = (
        pydantic.create_model("RootUnion", __root__=(Reservation | Item, ...))
        if PYDANTIC_V1
        else pydantic.RootModel[Reservation | Item]
    )

    def action(_arguments: BaseModel) -> str:
        pytest.fail("Unsupported root compositions must not invoke the handler")

    with pytest.raises(TypeError, match="root-level compositions are unsupported"):
        pydantic_function_tool(model, handler=action)
    if PYDANTIC_V1:
        composed = pydantic.create_model("ComposedRoot", __root__=(Reservation, Field(..., description="Reservation")))
        with pytest.raises(TypeError, match="root-level compositions are unsupported"):
            pydantic_function_tool(composed, handler=action)

    wrapped = pydantic.create_model("WrappedUnion", value=(Reservation | Item, ...))
    tool = pydantic_function_tool(wrapped, handler=lambda _: "accepted")
    assert tool({"value": {"sku": "test-sku"}}) == "accepted"


@pytest.mark.parametrize("wrap_base", [False, True])
def test_wrapped_override_uses_defining_namespace(wrap_base: bool) -> None:
    from functools import wraps

    def maybe_wrap(function: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return function(*args, **kwargs)

        return wrapped if wrap_base else function

    class Catalog:
        class Product(BaseModel):
            name: str

        @maybe_wrap
        def lookup(self, product: Product) -> str:
            return product.name

    class Child(Catalog):
        class Product(BaseModel):  # pyright: ignore[reportIncompatibleVariableOverride]
            sku: int

        @wraps(Catalog.lookup)
        def lookup(self, product: Any) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
            return super().lookup(product)

    assert function_tool(Child().lookup)({"product": {"name": "notebook"}}) == "notebook"


@pytest.mark.parametrize("delete_original", [False, True])
def test_bound_alias_keeps_lexical_annotation_owner(delete_original: bool) -> None:
    class Catalog:
        class Product(BaseModel):
            name: str

        def lookup(self, product: Product) -> str:
            return product.name

        reserve = lookup

    class Child(Catalog):
        class Product(BaseModel):  # pyright: ignore[reportIncompatibleVariableOverride]
            sku: int

        alias = Catalog.lookup

    if delete_original:
        delattr(Catalog, "lookup")
    for callback in (Child().reserve, Child().alias):
        assert function_tool(callback)({"product": {"name": "notebook"}}) == "notebook"


def test_module_function_attached_as_method_uses_globals() -> None:
    from types import ModuleType

    module = ModuleType("attached_action_module")
    exec(
        "from __future__ import annotations\n"
        "from pydantic import BaseModel\n"
        "class Product(BaseModel):\n    name: str\n"
        "def lookup(self, product: Product) -> str:\n    return product.name\n",
        module.__dict__,
    )

    class Catalog:
        class Product(BaseModel):
            sku: int

        lookup = module.lookup

    assert function_tool(Catalog().lookup)({"product": {"name": "notebook"}}) == "notebook"


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 requires Python 3.12")
def test_function_and_class_type_parameter_annotations() -> None:
    from types import ModuleType

    module = ModuleType("generic_action_module")
    exec(
        "from __future__ import annotations\n"
        "def choose[T: str](value: T) -> T:\n    return value\n"
        "class Catalog[T: int]:\n"
        "    def count(self, value: T) -> T:\n        return value\n"
        "    def choose[T: str](self, value: T) -> T:\n        return value\n",
        module.__dict__,
    )
    assert function_tool(module.choose)({"value": "notebook"}) == "notebook"
    assert function_tool(module.Catalog().count)({"value": 3}) == "3"
    assert function_tool(module.Catalog().choose)({"value": "notebook"}) == "notebook"


def test_transplanted_method_keeps_module_visible_lexical_owner() -> None:
    from types import ModuleType

    module = ModuleType("transplanted_action_module")
    exec(
        "from __future__ import annotations\n"
        "from pydantic import BaseModel\n"
        "class Catalog:\n"
        "    class Product(BaseModel):\n        name: str\n"
        "    def lookup(self, product: Product) -> str:\n        return product.name\n",
        module.__dict__,
    )

    class Target:
        class Product(BaseModel):
            sku: int

        lookup = module.Catalog.lookup

    assert function_tool(Target().lookup)({"product": {"name": "notebook"}}) == "notebook"


@pytest.mark.parametrize(
    "record",
    [
        {"type": "input_text", "text": "paid", "receipt_id": "r1"},
        {"type": "input_image", "image_url": "https://example.com/receipt.png", "receipt_id": "r1"},
    ],
)
def test_content_shaped_business_records_preserve_extra_fields(record: dict[str, str]) -> None:
    tool = function_tool(lambda: [record])
    assert json.loads(cast(str, tool({}))) == [record]
