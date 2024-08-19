from __future__ import annotations

from enum import Enum

from pydantic import Field, BaseModel
from inline_snapshot import snapshot

import openai
from openai._compat import PYDANTIC_V2

from .schema_types.query import Query


def test_most_types() -> None:
    if PYDANTIC_V2:
        assert openai.pydantic_function_tool(Query)["function"] == snapshot(
            {
                "name": "Query",
                "strict": True,
                "parameters": {
                    "$defs": {
                        "Column": {
                            "enum": [
                                "id",
                                "status",
                                "expected_delivery_date",
                                "delivered_at",
                                "shipped_at",
                                "ordered_at",
                                "canceled_at",
                            ],
                            "title": "Column",
                            "type": "string",
                        },
                        "Condition": {
                            "properties": {
                                "column": {"title": "Column", "type": "string"},
                                "operator": {"$ref": "#/$defs/Operator"},
                                "value": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {"type": "integer"},
                                        {"$ref": "#/$defs/DynamicValue"},
                                    ],
                                    "title": "Value",
                                },
                            },
                            "required": ["column", "operator", "value"],
                            "title": "Condition",
                            "type": "object",
                            "additionalProperties": False,
                        },
                        "DynamicValue": {
                            "properties": {"column_name": {"title": "Column Name", "type": "string"}},
                            "required": ["column_name"],
                            "title": "DynamicValue",
                            "type": "object",
                            "additionalProperties": False,
                        },
                        "Operator": {"enum": ["=", ">", "<", "<=", ">=", "!="], "title": "Operator", "type": "string"},
                        "OrderBy": {"enum": ["asc", "desc"], "title": "OrderBy", "type": "string"},
                        "Table": {"enum": ["orders", "customers", "products"], "title": "Table", "type": "string"},
                    },
                    "properties": {
                        "name": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Name"},
                        "table_name": {"$ref": "#/$defs/Table"},
                        "columns": {
                            "items": {"$ref": "#/$defs/Column"},
                            "title": "Columns",
                            "type": "array",
                        },
                        "conditions": {
                            "items": {"$ref": "#/$defs/Condition"},
                            "title": "Conditions",
                            "type": "array",
                        },
                        "order_by": {"$ref": "#/$defs/OrderBy"},
                    },
                    "required": ["name", "table_name", "columns", "conditions", "order_by"],
                    "title": "Query",
                    "type": "object",
                    "additionalProperties": False,
                },
            }
        )
    else:
        assert openai.pydantic_function_tool(Query)["function"] == snapshot(
            {
                "name": "Query",
                "strict": True,
                "parameters": {
                    "title": "Query",
                    "type": "object",
                    "properties": {
                        "name": {"title": "Name", "type": "string"},
                        "table_name": {"$ref": "#/definitions/Table"},
                        "columns": {"type": "array", "items": {"$ref": "#/definitions/Column"}},
                        "conditions": {
                            "title": "Conditions",
                            "type": "array",
                            "items": {"$ref": "#/definitions/Condition"},
                        },
                        "order_by": {"$ref": "#/definitions/OrderBy"},
                    },
                    "required": ["name", "table_name", "columns", "conditions", "order_by"],
                    "definitions": {
                        "Table": {
                            "title": "Table",
                            "description": "An enumeration.",
                            "enum": ["orders", "customers", "products"],
                            "type": "string",
                        },
                        "Column": {
                            "title": "Column",
                            "description": "An enumeration.",
                            "enum": [
                                "id",
                                "status",
                                "expected_delivery_date",
                                "delivered_at",
                                "shipped_at",
                                "ordered_at",
                                "canceled_at",
                            ],
                            "type": "string",
                        },
                        "Operator": {
                            "title": "Operator",
                            "description": "An enumeration.",
                            "enum": ["=", ">", "<", "<=", ">=", "!="],
                            "type": "string",
                        },
                        "DynamicValue": {
                            "title": "DynamicValue",
                            "type": "object",
                            "properties": {"column_name": {"title": "Column Name", "type": "string"}},
                            "required": ["column_name"],
                            "additionalProperties": False,
                        },
                        "Condition": {
                            "title": "Condition",
                            "type": "object",
                            "properties": {
                                "column": {"title": "Column", "type": "string"},
                                "operator": {"$ref": "#/definitions/Operator"},
                                "value": {
                                    "title": "Value",
                                    "anyOf": [
                                        {"type": "string"},
                                        {"type": "integer"},
                                        {"$ref": "#/definitions/DynamicValue"},
                                    ],
                                },
                            },
                            "required": ["column", "operator", "value"],
                            "additionalProperties": False,
                        },
                        "OrderBy": {
                            "title": "OrderBy",
                            "description": "An enumeration.",
                            "enum": ["asc", "desc"],
                            "type": "string",
                        },
                    },
                    "additionalProperties": False,
                },
            }
        )


class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"


class ColorDetection(BaseModel):
    color: Color = Field(description="The detected color")
    hex_color_code: str = Field(description="The hex color code of the detected color")


def test_enums() -> None:
    if PYDANTIC_V2:
        assert openai.pydantic_function_tool(ColorDetection)["function"] == snapshot(
            {
                "name": "ColorDetection",
                "strict": True,
                "parameters": {
                    "$defs": {"Color": {"enum": ["red", "blue", "green"], "title": "Color", "type": "string"}},
                    "properties": {
                        "color": {
                            "description": "The detected color",
                            "enum": ["red", "blue", "green"],
                            "title": "Color",
                            "type": "string",
                        },
                        "hex_color_code": {
                            "description": "The hex color code of the detected color",
                            "title": "Hex Color Code",
                            "type": "string",
                        },
                    },
                    "required": ["color", "hex_color_code"],
                    "title": "ColorDetection",
                    "type": "object",
                    "additionalProperties": False,
                },
            }
        )
    else:
        assert openai.pydantic_function_tool(ColorDetection)["function"] == snapshot(
            {
                "name": "ColorDetection",
                "strict": True,
                "parameters": {
                    "properties": {
                        "color": {
                            "description": "The detected color",
                            "title": "Color",
                            "enum": ["red", "blue", "green"],
                        },
                        "hex_color_code": {
                            "description": "The hex color code of the detected color",
                            "title": "Hex Color Code",
                            "type": "string",
                        },
                    },
                    "required": ["color", "hex_color_code"],
                    "title": "ColorDetection",
                    "definitions": {
                        "Color": {"title": "Color", "description": "An enumeration.", "enum": ["red", "blue", "green"]}
                    },
                    "type": "object",
                    "additionalProperties": False,
                },
            }
        )
