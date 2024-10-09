#!/usr/bin/env -S poetry run python

from openai import AsyncOpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = AsyncOpenAI()

async def main():
    # Test completions
    prompts = ["Tell me a joke", "Write a short poem", "Explain async programming"]
    completions_results = await client.acreate_completions(prompts, "gpt-3.5-turbo", max_tokens=50, batch_size=2)
    print(completions_results)

    # Test chat completions
    messages = [
        {"role": "user", "content": "What's the weather like today?"},
        {"role": "user", "content": "Tell me a story"}
    ]
    chat_results = await client.acreate_chat(messages, "gpt-3.5-turbo", max_tokens=50, batch_size=2)
    print(chat_results)

# Run the async main function
AsyncOpenAI.run(main)
