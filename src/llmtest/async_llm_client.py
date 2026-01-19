"""Async LLM client with connection pooling and parallel request support."""
import os
import asyncio
from typing import List, Dict, Optional
import httpx

API_BASE_URL = "https://openrouter.ai/api/v1"
CHAT_COMPLETIONS_ENDPOINT = f"{API_BASE_URL}/chat/completions"

# Global client instance for connection pooling
_async_client: Optional[httpx.AsyncClient] = None


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


async def get_async_client() -> httpx.AsyncClient:
    """Get or create a shared async HTTP client with connection pooling."""
    global _async_client

    if _async_client is None:
        # Create client with connection pooling and sensible defaults
        limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100,
            keepalive_expiry=30.0
        )

        timeout = httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=5.0
        )

        _async_client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            http2=True  # Enable HTTP/2 for better performance
        )

    return _async_client


async def close_async_client():
    """Close the shared async client. Should be called on shutdown."""
    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None


async def query_llm_async(
    messages: List[Dict[str, str]],
    model: str,
    semaphore: Optional[asyncio.Semaphore] = None
) -> str:
    """
    Asynchronously queries the specified LLM model via the OpenRouter API.

    Args:
        messages: A list of message dictionaries (e.g., [{"role": "user", "content": ...}]).
        model: The name of the model to query.
        semaphore: Optional semaphore for rate limiting concurrent requests.

    Returns:
        The content of the LLM's response.

    Raises:
        ValueError: If the OPENROUTER_API_KEY environment variable is not set.
        LLMClientError: For API or network errors.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("The OPENROUTER_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages
    }

    # Use semaphore if provided for rate limiting
    async def _make_request():
        client = await get_async_client()
        try:
            response = await client.post(
                CHAT_COMPLETIONS_ENDPOINT,
                headers=headers,
                json=data
            )
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx

            response_json = response.json()
            if "choices" in response_json and len(response_json["choices"]) > 0:
                content = response_json["choices"][0].get("message", {}).get("content")
                if content:
                    return content.strip()

            raise LLMClientError(f"Received an unexpected response format from the API: {response.text}")

        except httpx.HTTPStatusError as e:
            raise LLMClientError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}") from e
        except httpx.RequestError as e:
            raise LLMClientError(f"A network error occurred: {e}") from e
        except Exception as e:
            raise LLMClientError(f"An unexpected error occurred: {e}") from e

    if semaphore:
        async with semaphore:
            return await _make_request()
    else:
        return await _make_request()


async def query_llm_batch(
    messages_list: List[List[Dict[str, str]]],
    model: str,
    max_concurrent: int = 10
) -> List[str]:
    """
    Query multiple LLM requests in parallel with concurrency control.

    Args:
        messages_list: List of message lists to query.
        model: The name of the model to query.
        max_concurrent: Maximum number of concurrent requests (default: 10).

    Returns:
        List of response strings in the same order as input.

    Raises:
        ValueError: If the OPENROUTER_API_KEY environment variable is not set.
        LLMClientError: For API or network errors (will not stop other requests).
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = [
        query_llm_async(messages, model, semaphore)
        for messages in messages_list
    ]

    # Use gather with return_exceptions=True to prevent one failure from stopping all
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert exceptions to error strings or re-raise if needed
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # You can choose to raise here or return an error marker
            raise LLMClientError(f"Request {i} failed: {result}") from result
        processed_results.append(result)

    return processed_results


# Synchronous wrapper for backward compatibility
def query_llm_sync_wrapper(messages: List[Dict[str, str]], model: str) -> str:
    """
    Synchronous wrapper around async query for backward compatibility.
    Creates a new event loop if needed.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running, create one
        return asyncio.run(_query_with_cleanup(messages, model))
    else:
        # Event loop already running (e.g., in Jupyter)
        # We need to use asyncio.create_task or run in executor
        raise RuntimeError(
            "Cannot use sync wrapper from async context. "
            "Use query_llm_async() directly instead."
        )


async def _query_with_cleanup(messages: List[Dict[str, str]], model: str) -> str:
    """Helper to query and cleanup client."""
    try:
        return await query_llm_async(messages, model)
    finally:
        await close_async_client()


if __name__ == '__main__':
    # Example usage for testing the async client
    import time

    async def test_async_client():
        """Test the async client with parallel requests."""
        if not os.environ.get("OPENROUTER_API_KEY"):
            print("Skipping live test: OPENROUTER_API_KEY not set.")
            return

        test_model = "z-ai/glm-4.5-air:free"

        # Create multiple test messages
        messages_list = [
            [{"role": "user", "content": f"What is {i} + {i}? Respond with just the number."}]
            for i in range(1, 6)
        ]

        print(f"Testing parallel requests with {len(messages_list)} queries...")
        start = time.time()

        try:
            # Test parallel batch query
            results = await query_llm_batch(messages_list, test_model, max_concurrent=5)
            elapsed = time.time() - start

            print(f"\nCompleted {len(results)} requests in {elapsed:.2f} seconds")
            print(f"Average time per request: {elapsed/len(results):.2f} seconds")
            print("\nResults:")
            for i, result in enumerate(results, 1):
                print(f"  Query {i}: {result}")

        finally:
            await close_async_client()

    # Run the async test
    asyncio.run(test_async_client())
