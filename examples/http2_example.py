#!/usr/bin/env python3
"""
Simple HTTP/2 Usage Example

This example demonstrates how to enable HTTP/2 for improved performance.

Requirements:
    pip install openai[http2]

Usage:
    export OPENAI_API_KEY="your-api-key"
    python examples/http2_example.py
"""

import asyncio

from openai import AsyncOpenAI


async def process_batch_with_http2():
    """Process multiple requests concurrently using HTTP/2"""

    # Enable HTTP/2 for better performance
    async with AsyncOpenAI(http2=True) as client:
        print("Processing 50 concurrent requests with HTTP/2...")

        # Create 50 concurrent completion requests
        tasks = [
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Give me a fun fact about number {i}",
                    }
                ],
                max_tokens=50,
            )
            for i in range(1, 51)
        ]

        # Execute all requests concurrently
        completions = await asyncio.gather(*tasks)

        # Print first 5 results
        print("\nFirst 5 responses:")
        for i, completion in enumerate(completions[:5], 1):
            content = completion.choices[0].message.content
            print(f"{i}. {content[:100]}...")

        print(f"\n✓ Successfully processed {len(completions)} requests")


async def embedding_generation_with_http2():
    """Generate embeddings for multiple texts using HTTP/2"""

    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is transforming technology",
        "Python is a versatile programming language",
        "HTTP/2 enables request multiplexing",
        "Async programming improves concurrency",
    ]

    async with AsyncOpenAI(http2=True) as client:
        print("\nGenerating embeddings with HTTP/2...")

        # Create embedding requests concurrently
        tasks = [client.embeddings.create(model="text-embedding-3-small", input=text) for text in texts]

        embeddings = await asyncio.gather(*tasks)

        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"  Dimension: {len(embeddings[0].data[0].embedding)}")


async def main():
    print("=" * 70)
    print("HTTP/2 Usage Examples")
    print("=" * 70)

    try:
        # Example 1: Batch completions
        await process_batch_with_http2()

        # Example 2: Embedding generation
        await embedding_generation_with_http2()

        print("\n" + "=" * 70)
        print("Examples complete!")
        print("\nKey takeaway: HTTP/2 makes concurrent requests much faster!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("1. Installed HTTP/2 support: pip install openai[http2]")
        print("2. Set OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    asyncio.run(main())
