"""
Regression tests for the __api_exclude__ handling in async_transform.

The sync _transform_recursive path correctly passes
    exclude=getattr(data, "__api_exclude__", None)
to model_dump() when serialising a pydantic BaseModel value.

The async _async_transform_recursive path previously omitted that kwarg,
causing fields listed in __api_exclude__ to leak into the outgoing API
payload.

ParsedResponse (openai/types/responses/parsed_response.py) is the canonical
production consumer: it marks parsed_arguments with __api_exclude__ so the
client-side parsed data is never sent back to the API server.

Note: this file intentionally does NOT use `from __future__ import annotations`
so that TypedDict field annotations are evaluated eagerly and resolve cleanly
inside get_type_hints().
"""

import asyncio
from typing import TypedDict

import pytest

from openai._compat import PYDANTIC_V1
from openai._models import BaseModel
from openai._utils import async_transform, transform


# Skip the whole module when running against Pydantic v1 because __api_exclude__
# is only used with Pydantic v2 model_dump().
pytestmark = pytest.mark.skipif(PYDANTIC_V1, reason="__api_exclude__ requires Pydantic v2")


class _PublicAndPrivateModel(BaseModel):
    """A model with one field that should reach the API and one that must not."""

    public_field: str
    internal_field: str
    __api_exclude__ = {"internal_field"}


class _OuterPayload(TypedDict):
    nested: _PublicAndPrivateModel


@pytest.mark.asyncio
async def test_async_transform_excludes_api_excluded_fields() -> None:
    """async_transform must not include __api_exclude__ fields in the serialised output.

    Before the fix, _async_transform_recursive called
        model_dump(data, exclude_unset=True, mode="json")
    without the ``exclude`` kwarg, so internal_field leaked into the payload.
    """
    model = _PublicAndPrivateModel(public_field="hello", internal_field="secret")
    data = {"nested": model}

    result = await async_transform(data, expected_type=_OuterPayload)

    nested = result.get("nested", {})
    assert nested.get("public_field") == "hello", (
        f"public_field must appear in the serialised payload; got: {result}"
    )
    assert "internal_field" not in nested, (
        "internal_field is listed in __api_exclude__ and must NOT appear in the "
        f"serialised payload; got: {result}"
    )


def test_sync_transform_excludes_api_excluded_fields() -> None:
    """Sanity-check: the sync path must also exclude __api_exclude__ fields."""
    model = _PublicAndPrivateModel(public_field="hello", internal_field="secret")
    data = {"nested": model}

    result = transform(data, expected_type=_OuterPayload)

    nested = result.get("nested", {})
    assert nested.get("public_field") == "hello"
    assert "internal_field" not in nested, (
        f"internal_field must not be present in sync transform output; got: {result}"
    )


@pytest.mark.asyncio
async def test_async_transform_pydantic_model_without_api_exclude() -> None:
    """Models without __api_exclude__ must be serialised normally."""

    class _PlainModel(BaseModel):
        foo: str
        bar: str

    class _PlainOuter(TypedDict):
        data: _PlainModel

    model = _PlainModel(foo="a", bar="b")
    result = await async_transform({"data": model}, expected_type=_PlainOuter)
    nested = result.get("data", {})
    assert nested.get("foo") == "a"
    assert nested.get("bar") == "b"
