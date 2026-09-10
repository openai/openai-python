from __future__ import annotations

from typing import Any, cast

import pytest
import pydantic

from openai import OpenAI, AsyncOpenAI


class TestCompletions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_disallows_pydantic(self, client: OpenAI) -> None:
        class MyModel(pydantic.BaseModel):
            a: str

        with pytest.raises(TypeError, match=r"You tried to pass a `BaseModel` class"):
            client.chat.completions.create(
                messages=[
                    {
                        "content": "string",
                        "role": "system",
                    }
                ],
                model="gpt-4o",
                response_format=cast(Any, MyModel),
            )


class TestAsyncCompletions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_disallows_pydantic(self, async_client: AsyncOpenAI) -> None:
        class MyModel(pydantic.BaseModel):
            a: str

        with pytest.raises(TypeError, match=r"You tried to pass a `BaseModel` class"):
            await async_client.chat.completions.create(
                messages=[
                    {
                        "content": "string",
                        "role": "system",
                    }
                ],
                model="gpt-4o",
                response_format=cast(Any, MyModel),
            )
