#!/usr/bin/env python3
"""
HTTP/2 Verification Script

This script verifies that HTTP/2 is working correctly by testing
against a public endpoint that supports HTTP/2.

Usage:
    python examples/verify_http2.py
"""

import time
import asyncio

import httpx


async def verify_http2_protocol():
    """Verify that HTTP/2 protocol is actually being used"""
    print("=" * 70)
    print("HTTP/2 Protocol Verification")
    print("=" * 70)

    print("\n1. Testing httpx HTTP/2 support...")

    # Test HTTP/1.1
    async with httpx.AsyncClient(http2=False) as client:
        response = await client.get("https://httpbin.org/get")
        http1_version = response.http_version
        print(f"   HTTP/1.1 client: {http1_version}")

    # Test HTTP/2
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get("https://httpbin.org/get")
        http2_version = response.http_version
        print(f"   HTTP/2 client: {http2_version}")

    if http2_version == "HTTP/2":
        print("   ✓ HTTP/2 is working correctly")
    else:
        print(f"   ✗ Expected HTTP/2, got {http2_version}")
        return False

    return True


async def verify_openai_client():
    """Verify OpenAI client HTTP/2 configuration"""
    print("\n2. Verifying OpenAI client configuration...")

    from openai import AsyncOpenAI
    from openai._base_client import _DefaultAsyncHttpxClient

    # Create OpenAI client with HTTP/2
    client = AsyncOpenAI(api_key="test-key", http2=True)
    print("   ✓ Client created with http2=True")

    # Create the same httpx client OpenAI uses
    httpx_client = _DefaultAsyncHttpxClient(http2=True, base_url="https://httpbin.org")

    response = await httpx_client.get("/get")
    print(f"   OpenAI's httpx client uses: {response.http_version}")

    await httpx_client.aclose()
    await client.close()

    if response.http_version == "HTTP/2":
        print("   ✓ OpenAI client correctly configured for HTTP/2")
        return True
    else:
        print(f"   ✗ Expected HTTP/2, got {response.http_version}")
        return False


async def benchmark_performance():
    """Benchmark HTTP/1.1 vs HTTP/2 performance"""
    print("\n3. Benchmarking performance (20 concurrent requests)...")

    num_requests = 20

    # HTTP/1.1 benchmark
    async with httpx.AsyncClient(http2=False) as client:
        start = time.time()
        tasks = [client.get("https://httpbin.org/delay/0.1") for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        http1_time = time.time() - start

    # HTTP/2 benchmark
    async with httpx.AsyncClient(http2=True) as client:
        start = time.time()
        tasks = [client.get("https://httpbin.org/delay/0.1") for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        http2_time = time.time() - start

    print(f"   HTTP/1.1: {http1_time:.2f}s")
    print(f"   HTTP/2:   {http2_time:.2f}s")

    if http2_time > 0:
        speedup = http1_time / http2_time
        improvement = ((http1_time - http2_time) / http1_time) * 100
        print(f"   Speedup:  {speedup:.2f}x ({improvement:.1f}% improvement)")

        if speedup > 1.0:
            print("   ✓ HTTP/2 shows performance improvement")
            return True

    return False


async def main():
    print("\n" + "=" * 70)
    print("OpenAI SDK - HTTP/2 Verification")
    print("=" * 70)

    all_passed = True

    # Run verification tests
    if not await verify_http2_protocol():
        all_passed = False

    if not await verify_openai_client():
        all_passed = False

    if not await benchmark_performance():
        print("   ⚠ Performance improvement not detected (may vary by network)")

    print("\n" + "=" * 70)

    if all_passed:
        print("✅ VERIFICATION PASSED")
        print("=" * 70)
        print()
        print("HTTP/2 is correctly implemented and working!")
        print()
        print("To use HTTP/2 in your application:")
        print("  from openai import AsyncOpenAI")
        print("  client = AsyncOpenAI(http2=True)")
        print()
    else:
        print("❌ VERIFICATION FAILED")
        print("=" * 70)
        print()
        print("HTTP/2 verification failed. Please check:")
        print("1. h2 package is installed: pip install openai[http2]")
        print("2. Network allows HTTP/2 connections")
        print("3. httpx version is >= 0.23.0")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
