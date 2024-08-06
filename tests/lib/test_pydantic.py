from __future__ import annotations

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
                    "required": ["table_name", "columns", "conditions", "order_by"],
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
                        "table_name": {"$ref": "#/definitions/Table"},
                        "columns": {"type": "array", "items": {"$ref": "#/definitions/Column"}},
                        "conditions": {
                            "title": "Conditions",
                            "type": "array",
                            "items": {"$ref": "#/definitions/Condition"},
                        },
                        "order_by": {"$ref": "#/definitions/OrderBy"},
                    },
                    "required": ["table_name", "columns", "conditions", "order_by"],
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
