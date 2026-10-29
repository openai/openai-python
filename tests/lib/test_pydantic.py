from __future__ import annotations

import json
from enum import Enum
from typing_extensions import Annotated

import pytest
from pydantic import Field, BaseModel
from inline_snapshot import snapshot

import openai
from openai._compat import PYDANTIC_V1
from openai.lib._pydantic import to_strict_json_schema

from .schema_types.query import Query


def test_most_types() -> None:
    if not PYDANTIC_V1:
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
    if not PYDANTIC_V1:
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


def test_recursive_field_description() -> None:
    class Node(BaseModel):
        label: str
        child: Node | None = Field(default=None, description="A child node")

    tool = openai.pydantic_function_tool(Node)
    schema = json.loads(json.dumps(tool))["function"]["parameters"]
    node = schema["definitions" if PYDANTIC_V1 else "$defs"]["Node"]
    child = node["properties"]["child"]

    assert node["required"] == ["label", "child"]
    assert node["additionalProperties"] is False
    assert child["description"] == "A child node"
    assert "default" not in child
    assert child["anyOf"][0] == {"$ref": "#/definitions/Node" if PYDANTIC_V1 else "#/$defs/Node"}


@pytest.mark.skipif(PYDANTIC_V1, reason="Pydantic v1 does not emit annotations on list items")
def test_recursive_annotated_ref() -> None:
    class Node(BaseModel):
        label: str
        children: list[Annotated["Node", Field(description="A child node")]]
        alternatives: list[Annotated["Node", Field(description="An alternative node")]]

    tool = openai.pydantic_function_tool(Node)
    schema = json.loads(json.dumps(tool))["function"]["parameters"]
    node = schema["$defs"]["Node"]

    assert schema["type"] == "object"
    assert schema["required"] == node["required"] == ["label", "children", "alternatives"]
    assert schema["additionalProperties"] is node["additionalProperties"] is False
    assert "description" not in node
    assert node["properties"]["children"]["items"] == {
        "description": "A child node",
        "anyOf": [{"$ref": "#/$defs/Node"}],
    }
    assert node["properties"]["alternatives"]["items"] == {
        "description": "An alternative node",
        "anyOf": [{"$ref": "#/$defs/Node"}],
    }


@pytest.mark.skipif(PYDANTIC_V1, reason="Pydantic v1 does not emit annotations on list items")
def test_mutually_recursive_annotated_refs() -> None:
    class Branch(BaseModel):
        leaves: list[Annotated["Leaf", Field(description="A leaf")]]

    class Leaf(BaseModel):
        branches: list[Annotated[Branch, Field(description="A branch")]]

    Branch.model_rebuild()

    class Tree(BaseModel):
        branch: Branch = Field(description="The root branch")

    tool = openai.pydantic_function_tool(Tree)
    schema = json.loads(json.dumps(tool))["function"]["parameters"]
    branch = schema["properties"]["branch"]
    leaf = branch["properties"]["leaves"]["items"]

    assert branch["description"] == "The root branch"
    assert branch["required"] == ["leaves"]
    assert branch["additionalProperties"] is False
    assert leaf["description"] == "A leaf"
    assert leaf["required"] == ["branches"]
    assert leaf["additionalProperties"] is False
    assert leaf["properties"]["branches"]["items"] == {
        "description": "A branch",
        "anyOf": [{"$ref": "#/$defs/Branch"}],
    }
    assert schema["$defs"]["Branch"]["additionalProperties"] is False
    assert schema["$defs"]["Leaf"]["additionalProperties"] is False


class Star(BaseModel):
    name: str = Field(description="The name of the star.")


class Galaxy(BaseModel):
    name: str = Field(description="The name of the galaxy.")
    largest_star: Star = Field(description="The largest star in the galaxy.")


class Universe(BaseModel):
    name: str = Field(description="The name of the universe.")
    galaxy: Galaxy = Field(description="A galaxy in the universe.")


def test_nested_inline_ref_expansion() -> None:
    if not PYDANTIC_V1:
        assert to_strict_json_schema(Universe) == snapshot(
            {
                "title": "Universe",
                "type": "object",
                "$defs": {
                    "Star": {
                        "title": "Star",
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "title": "Name",
                                "description": "The name of the star.",
                            }
                        },
                        "required": ["name"],
                        "additionalProperties": False,
                    },
                    "Galaxy": {
                        "title": "Galaxy",
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "title": "Name",
                                "description": "The name of the galaxy.",
                            },
                            "largest_star": {
                                "title": "Star",
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "title": "Name",
                                        "description": "The name of the star.",
                                    }
                                },
                                "required": ["name"],
                                "description": "The largest star in the galaxy.",
                                "additionalProperties": False,
                            },
                        },
                        "required": ["name", "largest_star"],
                        "additionalProperties": False,
                    },
                },
                "properties": {
                    "name": {
                        "type": "string",
                        "title": "Name",
                        "description": "The name of the universe.",
                    },
                    "galaxy": {
                        "title": "Galaxy",
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "title": "Name",
                                "description": "The name of the galaxy.",
                            },
                            "largest_star": {
                                "title": "Star",
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "title": "Name",
                                        "description": "The name of the star.",
                                    }
                                },
                                "required": ["name"],
                                "description": "The largest star in the galaxy.",
                                "additionalProperties": False,
                            },
                        },
                        "required": ["name", "largest_star"],
                        "description": "A galaxy in the universe.",
                        "additionalProperties": False,
                    },
                },
                "required": ["name", "galaxy"],
                "additionalProperties": False,
            }
        )
    else:
        assert to_strict_json_schema(Universe) == snapshot(
            {
                "title": "Universe",
                "type": "object",
                "definitions": {
                    "Star": {
                        "title": "Star",
                        "type": "object",
                        "properties": {
                            "name": {"title": "Name", "description": "The name of the star.", "type": "string"}
                        },
                        "required": ["name"],
                        "additionalProperties": False,
                    },
                    "Galaxy": {
                        "title": "Galaxy",
                        "type": "object",
                        "properties": {
                            "name": {"title": "Name", "description": "The name of the galaxy.", "type": "string"},
                            "largest_star": {
                                "title": "Largest Star",
                                "description": "The largest star in the galaxy.",
                                "type": "object",
                                "properties": {
                                    "name": {"title": "Name", "description": "The name of the star.", "type": "string"}
                                },
                                "required": ["name"],
                                "additionalProperties": False,
                            },
                        },
                        "required": ["name", "largest_star"],
                        "additionalProperties": False,
                    },
                },
                "properties": {
                    "name": {
                        "title": "Name",
                        "description": "The name of the universe.",
                        "type": "string",
                    },
                    "galaxy": {
                        "title": "Galaxy",
                        "description": "A galaxy in the universe.",
                        "type": "object",
                        "properties": {
                            "name": {
                                "title": "Name",
                                "description": "The name of the galaxy.",
                                "type": "string",
                            },
                            "largest_star": {
                                "title": "Largest Star",
                                "description": "The largest star in the galaxy.",
                                "type": "object",
                                "properties": {
                                    "name": {"title": "Name", "description": "The name of the star.", "type": "string"}
                                },
                                "required": ["name"],
                                "additionalProperties": False,
                            },
                        },
                        "required": ["name", "largest_star"],
                        "additionalProperties": False,
                    },
                },
                "required": ["name", "galaxy"],
                "additionalProperties": False,
            }
        )
