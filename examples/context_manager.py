"""
Example showing how to use the OpenAIContext for better resource management.
This context manager ensures proper cleanup of resources and provides a more
Pythonic way to use the OpenAI client.
"""

import os
import asyncio
from typing import Optional
from openai import AsyncOpenAI, OpenAI


class OpenAIContext:
    """A context manager for the OpenAI client that ensures proper resource cleanup."""
    
    def __init__(self, api_key: Optional[str] = None, async_mode: bool = True):
        """
        Initialize the context manager.
        
        Args:
            api_key: Optional API key. If not provided, will use OPENAI_API_KEY environment variable
            async_mode: Whether to use async client (True) or sync client (False)
        """
        self.client = None
        self.api_key = api_key
        self.async_mode = async_mode

    async def __aenter__(self):
        """Async context entry - creates and returns an AsyncOpenAI client."""
        self.client = AsyncOpenAI(api_key=self.api_key)
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context exit - ensures proper client cleanup."""
        if self.client:
            await self.client.close()
    
    def __enter__(self):
        """Sync context entry - creates and returns an OpenAI client."""
        if self.async_mode:
            raise RuntimeError("Cannot use sync context manager with async_mode=True")
        self.client = OpenAI(api_key=self.api_key)
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context exit - ensures proper client cleanup."""
        if self.client:
            self.client.close()


async def async_example(api_key: Optional[str] = None):
    """Example of using the async context manager."""
    async with OpenAIContext(api_key=api_key) as client:
        response = await client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": "Hello! How are you?"
            }],
            model="gpt-4",
            max_tokens=50
        )
        print("Async response:", response.choices[0].message.content)


def sync_example(api_key: Optional[str] = None):
    """Example of using the sync context manager."""
    with OpenAIContext(async_mode=False, api_key=api_key) as client:
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": "Hello! How are you?"
            }],
            model="gpt-4",
            max_tokens=50
        )
        print("Sync response:", response.choices[0].message.content)


if __name__ == "__main__":
    # The API key can be provided in several ways:
    # 1. Environment variable: export OPENAI_API_KEY='your-api-key'
    # 2. Passed directly to the functions
    # 3. Passed to OpenAIContext when instantiating
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set your OpenAI API key using one of these methods:")
        print("1. Export environment variable: export OPENAI_API_KEY='your-api-key'")
        print("2. Pass the API key directly to the functions")
        exit(1)
    
    print("Running async example...")
    asyncio.run(async_example(api_key))
    
    print("\nRunning sync example...")
    sync_example(api_key)
