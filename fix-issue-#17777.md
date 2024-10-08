# ISSUE FIX - #1777 openai.AsyncOpenAI not safe when shared across async tests 

The `AsyncOpenAI` class provides an asynchronous interface for interacting with the OpenAI API. This class allows you to batch requests for both completions and chat models using asyncio, improving the processing time when dealing with larger sets of prompts or messages.

## ISSUE LINK:
https://github.com/openai/openai-python/issues/1777

## BUG FIX: 
Resolve an alternative for httpx, using abstraction making the coding experience user friendly.

## Usage
s
Here’s an example of how to use `AsyncOpenAI` to process multiple prompts and chat messages asynchronously.

### Initialization

To get started, you need to initialize the `AsyncOpenAI` client by passing your OpenAI API key. This can be done by reading the API key from an environment variable like so:

```python
import os
from openai import AsyncOpenAI

# Initialize the OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Async completions Example

You can use the `acreate_completions` method to asynchronously send a batch of prompts and retrieve completions results. The following example shows how to send a batch of prompts using the GPT-3.5 Turbo model.

```python
async def main():
    prompts = [
        "Tell me a joke",
        "Write a short poem",
        "Explain async programming"
    ]

    # Send the prompts asynchronously with a batch size of 2
    completions_results = await client.acreate_completions(prompts, "gpt-3.5-turbo", max_tokens=50, batch_size=2)
    print(completions_results)
```

### Async Chat completions Example

You can also handle chat completions using the `acreate_chat` method. This method accepts a list of message dictionaries that mimic a conversation format (`role: user`, `content: message`).

```python
async def main():
    messages = [
        {"role": "user", "content": "What's the weather like today?"},
        {"role": "user", "content": "Tell me a story"}
    ]

    # Send the messages asynchronously with a batch size of 2
    chat_results = await client.acreate_chat(messages, "gpt-3.5-turbo", max_tokens=50, batch_size=2)
    print(chat_results)
```

### Running the Async Function

To run the async code, use the `run` method of `AsyncOpenAI` to execute your `main` function:

```python
# Run the async main function
AsyncOpenAI.run(main)
```

### Full Example

```python
import os
from openai import AsyncOpenAI

# Initialize the OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
```

## Key Features

- **Batching**: You can set the batch size to optimize the number of requests sent in parallel.
- **Async Processing**: This SDK leverages Python’s asyncio library to handle large numbers of requests concurrently, reducing latency when handling multiple requests.
- **Flexible API**: Supports both completions and chat completions, with models like GPT-3.5 Turbo.

## Parameters

- `prompts` (for completions): A list of text prompts to send to the model.
- `messages` (for chat completions): A list of dictionaries containing `role` and `content` to simulate a conversation.
- `model`: The OpenAI model to use (e.g., `gpt-3.5-turbo`).
- `max_tokens`: Maximum number of tokens to generate in the response.
- `batch_size`: The number of items to process in parallel.

## Error Handling

Make sure to handle exceptions and errors when dealing with API requests. If the API request fails or times out, you can catch the error and log it appropriately.

Example:

```python
try:
    # Make your async API call
except openai.error.OpenAIError as e:
    print(f"An error occurred: {e}")
```