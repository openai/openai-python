from enum import Enum
from typing import List, Union

import rich
from pydantic import BaseModel

import openai
from openai import OpenAI


class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"


class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"


class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="


class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class DynamicValue(BaseModel):
    column_name: str


class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]


class Query(BaseModel):
    table_name: Table
    columns: List[Column]
    conditions: List[Condition]
    order_by: OrderBy


client = OpenAI()

with client.responses.stream(
    model="gpt-4o-2024-08-06",
    input="look up all my orders in november of last year that were fulfilled but not delivered on time",
    tools=[
        openai.pydantic_function_tool(Query),
    ],
) as stream:
    for event in stream:
        rich.print(event)
