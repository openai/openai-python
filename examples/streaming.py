#!/usr/bin/env -S poetry run python

import asyncio

from openai import OpenAI, AsyncOpenAI

# This script assumes you have the OPENAI_API_KEY environment variable set to a valid OpenAI API key.
#
# You can run this script from the root directory like so:
# `python examples/streaming.py`


def sync_main() -> None:
    client = OpenAI()
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="1,2,3,",
        max_tokens=5,
        temperature=0,
        stream=True,
    )

    # You can manually control iteration over the response
    first = next(response)
    print(f"got response data: {first.model_dump_json(indent=2)}")

    # Or you could automatically iterate through all of data.
    # Note that the for loop will not exit until *all* of the data has been processed.
    for data in response:
        print(data.model_dump_json())


async def async_main() -> None:
    client = AsyncOpenAI()
    response = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="1,2,3,",
        max_tokens=5,
        temperature=0,
        stream=True,
    )

    # You can manually control iteration over the response.
    # In Python 3.10+ you can also use the `await anext(response)` builtin instead
    first = await response.__anext__()
    print(f"got response data: {first.model_dump_json(indent=2)}")

    # Or you could automatically iterate through all of data.
    # Note that the for loop will not exit until *all* of the data has been processed.
    async for data in response:
        print(data.model_dump_json())


sync_main()

asyncio.run(async_main())
