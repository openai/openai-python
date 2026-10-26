from typing import Any, cast
from typing_extensions import Literal, Annotated

import httpx2
import pytest

from openai import OpenAI, BaseModel, AsyncOpenAI
from tests.respx2 import MockRouter
from openai._utils import PropertyInfo

from .conftest import base_url


class PipeUnionModel(BaseModel):
    value: int | str


class TextVariant(BaseModel):
    kind: Literal["text"]
    data: str


class NumberVariant(BaseModel):
    kind: Literal["number"]
    data: int


class PipeDiscriminatedModel(BaseModel):
    value: Annotated[TextVariant | NumberVariant, PropertyInfo(discriminator="kind")]


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("client,async_client", [(False, False)], indirect=True)
@pytest.mark.parametrize("response_model", [PipeUnionModel, PipeDiscriminatedModel])
@pytest.mark.respx2(base_url=base_url)
async def test_union_response_fallback(
    sync: bool,
    response_model: type[BaseModel],
    client: OpenAI,
    async_client: AsyncOpenAI,
    respx2_mock: MockRouter,
) -> None:
    discriminated = response_model is PipeDiscriminatedModel
    if discriminated:
        value: object = {"kind": "number", "data": "unexpected"}
    else:
        value = {}

    respx2_mock.get("/union").mock(return_value=httpx2.Response(200, json={"value": value}))

    # Repeated parsing must work with or without a populated discriminator cache.
    for _ in range(2):
        if sync:
            response = client.get("/union", cast_to=response_model)
        else:
            response = await async_client.get("/union", cast_to=response_model)

        result = cast(Any, response).value
        if discriminated:
            assert isinstance(result, NumberVariant)
            assert result.kind == "number"
            assert result.data == "unexpected"  # type: ignore[comparison-overlap]
        else:
            assert result == value
