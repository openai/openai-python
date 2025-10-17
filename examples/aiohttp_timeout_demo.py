#!/usr/bin/env python3

import asyncio
import os
import time
from typing import Optional

from openai import AsyncOpenAI, DefaultAioHttpClient
from openai._exceptions import APITimeoutError, APIStatusError


async def basic_aiohttp_example():
    """Test basic aiohttp connectivity."""
    print("Basic aiohttp backend example")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    async with AsyncOpenAI(
        api_key=api_key,
        http_client=DefaultAioHttpClient(),
        timeout=30.0,
        max_retries=2
    ) as client:
        try:
            models = await client.models.list()
            print(f"Connected successfully! Found {len(models.data)} models.")
            
        except APITimeoutError as e:
            print(f"Request timed out: {e}")
        except APIStatusError as e:
            print(f"API error: {e.status_code} - {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def concurrent_requests_example():
    """Test concurrent requests."""
    print("\nConcurrent requests example")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    async with AsyncOpenAI(
        api_key=api_key,
        http_client=DefaultAioHttpClient(),
        timeout=60.0,
        max_retries=3
    ) as client:
        tasks = [client.models.list() for _ in range(3)]
        
        try:
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            print(f"Completed {len(tasks)} concurrent requests in {end_time - start_time:.2f}s")
            print(f"Successful: {successful}, Failed: {failed}")
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Request {i} error: {result}")
                    
        except Exception as e:
            print(f"Concurrent requests failed: {e}")


async def timeout_handling_example():
    """Test timeout handling."""
    print("\nTimeout handling example")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    async with AsyncOpenAI(
        api_key=api_key,
        http_client=DefaultAioHttpClient(),
        timeout=1.0,
        max_retries=0
    ) as client:
        try:
            print("Making request with 1-second timeout...")
            await client.models.list()
            print("Request completed within timeout")
            
        except APITimeoutError:
            print("Timeout properly caught and handled")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def production_ready_example():
    """Test production-ready error handling."""
    print("\nProduction-ready example")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    async def make_request_with_retries(client: AsyncOpenAI, max_attempts: int = 3) -> Optional[dict]:
        for attempt in range(max_attempts):
            try:
                response = await client.models.list()
                return {"success": True, "data": response.data}
                
            except APITimeoutError as e:
                print(f"Attempt {attempt + 1}: Timeout - {e}")
                if attempt < max_attempts - 1:
                    wait_time = 2 ** attempt
                    print(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    return {"success": False, "error": "Max retries exceeded", "type": "timeout"}
                    
            except APIStatusError as e:
                if e.status_code == 429:
                    wait_time = 2 ** attempt
                    print(f"Attempt {attempt + 1}: Rate limited - waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    return {"success": False, "error": str(e), "type": "api_error"}
                    
            except Exception as e:
                return {"success": False, "error": str(e), "type": "unexpected"}
        
        return {"success": False, "error": "Max attempts exceeded", "type": "unknown"}
    
    async with AsyncOpenAI(
        api_key=api_key,
        http_client=DefaultAioHttpClient(),
        timeout=30.0,
        max_retries=0
    ) as client:
        result = await make_request_with_retries(client)
        
        if result["success"]:
            print(f"Production request successful! Found {len(result['data'])} models.")
        else:
            print(f"Production request failed: {result['error']} ({result['type']})")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("OpenAI aiohttp Backend Examples (httpx-aiohttp 0.1.9)")
    print("=" * 60)
    print("This demonstrates the timeout fixes in httpx-aiohttp 0.1.9")
    print("")
    
    try:
        import httpx_aiohttp
        print("httpx-aiohttp is installed")
    except ImportError:
        print("httpx-aiohttp not installed. Install with: pip install openai[aiohttp]")
        return
    
    await basic_aiohttp_example()
    await concurrent_requests_example()
    await timeout_handling_example()
    await production_ready_example()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("The httpx-aiohttp 0.1.9 upgrade fixes production timeout issues.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
