from __future__ import annotations

from decimal import Decimal
from enum import Enum

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


class InsuranceQuote(BaseModel):
    """Test model with Decimal field to verify pattern keyword is stripped"""
    premium: Decimal = Field(description="The insurance premium amount")
    coverage_amount: float = Field(description="The coverage amount")
    customer_name: str = Field(description="The customer's name")


def test_decimal_field_strips_pattern() -> None:
    """
    Test that Decimal fields do not include unsupported 'pattern' keyword.

    Pydantic generates a regex pattern for Decimal fields by default, but this
    is not supported by OpenAI's structured outputs in strict mode. This test
    verifies that the pattern keyword is properly stripped from the schema.

    Fixes issue #2718
    """
    if not PYDANTIC_V1:
        schema = to_strict_json_schema(InsuranceQuote)

        # Verify the schema structure exists
        assert "properties" in schema
        assert "premium" in schema["properties"]

        # Get the premium field schema
        premium_schema = schema["properties"]["premium"]

        # Verify it's an anyOf with number/string/null options
        assert "anyOf" in premium_schema

        # Check all variants in the anyOf for 'pattern' keyword
        # Pattern should NOT be present after our fix
        for variant in premium_schema["anyOf"]:
            assert "pattern" not in variant, (
                "Pattern keyword should be stripped from Decimal field schema. "
                "Found pattern in variant: " + str(variant)
            )

        # Verify the schema matches expected structure (without pattern)
        assert schema == snapshot(
            {
                "title": "InsuranceQuote",
                "type": "object",
                "properties": {
                    "premium": {
                        "anyOf": [
                            {"type": "number"},
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "description": "The insurance premium amount",
                        "title": "Premium",
                    },
                    "coverage_amount": {
                        "description": "The coverage amount",
                        "title": "Coverage Amount",
                        "type": "number",
                    },
                    "customer_name": {
                        "description": "The customer's name",
                        "title": "Customer Name",
                        "type": "string",
                    },
                },
                "required": ["premium", "coverage_amount", "customer_name"],
                "additionalProperties": False,
            }
        )


class ProductPricing(BaseModel):
    """Test model with Dict[str, Decimal] to verify pattern is stripped from additionalProperties"""
    prices: dict[str, Decimal] = Field(description="Product prices by region")
    product_name: str = Field(description="The product name")


def test_dict_decimal_strips_pattern_in_additional_properties() -> None:
    """
    Test that Dict[str, Decimal] fields strip pattern from additionalProperties.

    When Pydantic generates schemas for typed dictionaries (Dict[str, Decimal]),
    it uses additionalProperties with a Decimal schema that includes a regex
    pattern. This test verifies that pattern keywords are stripped from nested
    schemas within additionalProperties.

    Addresses Codex review feedback on PR #2733
    """
    if not PYDANTIC_V1:
        schema = to_strict_json_schema(ProductPricing)

        # Verify the schema structure exists
        assert "properties" in schema
        assert "prices" in schema["properties"]

        # Get the prices field schema
        prices_schema = schema["properties"]["prices"]

        # Should be an object with additionalProperties
        assert prices_schema.get("type") == "object"
        assert "additionalProperties" in prices_schema

        # Get the additionalProperties schema (Decimal schema)
        add_props = prices_schema["additionalProperties"]
        assert "anyOf" in add_props

        # Check all variants in anyOf for 'pattern' keyword
        # Pattern should NOT be present after our fix
        for variant in add_props["anyOf"]:
            assert "pattern" not in variant, (
                "Pattern keyword should be stripped from additionalProperties Decimal schema. "
                "Found pattern in variant: " + str(variant)
            )

        # Verify the full schema matches expected structure
        assert schema == snapshot(
            {
                "description": "Test model with Dict[str, Decimal] to verify pattern is stripped from additionalProperties",
                "properties": {
                    "prices": {
                        "additionalProperties": {
                            "anyOf": [
                                {"type": "number"},
                                {"type": "string"},
                            ]
                        },
                        "description": "Product prices by region",
                        "title": "Prices",
                        "type": "object",
                    },
                    "product_name": {
                        "description": "The product name",
                        "title": "Product Name",
                        "type": "string",
                    },
                },
                "required": ["prices", "product_name"],
                "title": "ProductPricing",
                "type": "object",
                "additionalProperties": False,
            }
        )
