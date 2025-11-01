#!/usr/bin/env python3
"""
HTTP/2 Performance Benchmark

This script demonstrates the performance improvements of HTTP/2
for high-concurrency workloads with the OpenAI API.

Requirements:
    pip install openai[http2]

Usage:
    python examples/http2_benchmark.py
"""

import time
import asyncio

from openai import AsyncOpenAI


async def benchmark_requests(client: AsyncOpenAI, num_requests: int) -> float:
    """Make multiple concurrent requests and measure time"""
    start = time.time()

    tasks = [
        client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": f"Say the number {i}"}], max_tokens=5
        )
        for i in range(num_requests)
    ]

    await asyncio.gather(*tasks)
    elapsed = time.time() - start

    return elapsed


async def main():
    print("=" * 70)
    print("HTTP/2 vs HTTP/1.1 Performance Benchmark")
    print("=" * 70)
    print()
    print("This benchmark compares the performance of HTTP/1.1 and HTTP/2")
    print("for concurrent API requests.")
    print()

    test_cases = [10, 25, 50, 100]

    for num_requests in test_cases:
        print(f"Testing with {num_requests} concurrent requests:")
        print("-" * 70)

        # HTTP/1.1 benchmark
        print("  HTTP/1.1: ", end="", flush=True)
        async with AsyncOpenAI(http2=False) as client_http1:
            http1_time = await benchmark_requests(client_http1, num_requests)
        print(f"{http1_time:.2f}s")

        # HTTP/2 benchmark
        print("  HTTP/2:   ", end="", flush=True)
        async with AsyncOpenAI(http2=True) as client_http2:
            http2_time = await benchmark_requests(client_http2, num_requests)
        print(f"{http2_time:.2f}s")

        # Calculate improvement
        if http1_time > 0:
            improvement = ((http1_time - http2_time) / http1_time) * 100
            speedup = http1_time / http2_time if http2_time > 0 else 0
            print(f"  Improvement: {improvement:.1f}% faster ({speedup:.2f}x speedup)")
        print()

    print("=" * 70)
    print("Benchmark complete!")
    print()
    print("Key Takeaways:")
    print("- HTTP/2 shows greatest improvements with high concurrency (50+ requests)")
    print("- Multiplexing reduces connection overhead significantly")
    print("- Lower latency and better resource utilization")
    print()
    print("To enable HTTP/2 in your application:")
    print("  client = AsyncOpenAI(http2=True)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("1. Installed HTTP/2 support: pip install openai[http2]")
        print("2. Set OPENAI_API_KEY environment variable")
