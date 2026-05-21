import asyncio
from typing import List

import rich
from pydantic import BaseModel

from openai._client import AsyncOpenAI


class Step(BaseModel):
    explanation: str
    output: str


class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str


async def main() -> None:
    client = AsyncOpenAI()
    id = None

    async with await client.responses.create(
        input="solve 8x + 31 = 2",
        model="gpt-4o-2024-08-06",
        background=True,
        stream=True,
    ) as stream:
        async for event in stream:
            if event.type == "response.created":
                id = event.response.id
            if "output_text" in event.type:
                rich.print(event)
            if event.sequence_number == 10:
                break

    print("Interrupted. Continuing...")

    assert id is not None
    async with await client.responses.retrieve(
        response_id=id,
        stream=True,
        starting_after=10,
    ) as stream:
        async for event in stream:
            if "output_text" in event.type:
                rich.print(event)


if __name__ == "__main__":
    asyncio.run(main())
