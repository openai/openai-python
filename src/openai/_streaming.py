#!/usr/bin/env -S poetry run python

import asyncio
from openai import OpenAI, AsyncOpenAI

# Set up OpenAI client
def setup_client(async_mode=False):
    return AsyncOpenAI() if async_mode else OpenAI()

# Function to interact with OpenAI API
async def interact_with_openai(client, model, prompt, max_tokens, temperature):
    response = await client.completions.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )

    # Print the first response
    first = await response.__anext__()
    print(f"got response data: {first.model_dump_json(indent=2)}")

    # Print all subsequent responses
    async for data in response:
        print(data.model_dump_json())

# Main function for synchronous interaction
def sync_main():
    client = setup_client()
    asyncio.run(interact_with_openai(client, "text-davinci-002", "1,2,3,", 5, 0))

# Main function for asynchronous interaction
async def async_main():
    client = setup_client(async_mode=True)
    await interact_with_openai(client, "text-davinci-002", "1,2,3,", 5, 0)

# Run the script
sync_main()  # Synchronous interaction
asyncio.run(async_main())  # Asynchronous interaction
