"""Tests for async modules."""
import pytest
import asyncio
import os
from llmtest.async_llm_client import query_llm_async, get_async_client, close_async_client


@pytest.mark.skipif(
    not os.environ.get("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set"
)
@pytest.mark.asyncio
async def test_async_llm_client():
    """Test async LLM client basic functionality."""
    messages = [{"role": "user", "content": "What is 2+2? Respond with just the number."}]
    model = "z-ai/glm-4.5-air:free"

    try:
        result = await query_llm_async(messages, model)
        assert result is not None
        assert len(result) > 0
        assert "4" in result
    finally:
        await close_async_client()


@pytest.mark.skipif(
    not os.environ.get("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set"
)
def test_async_client_connection_pooling():
    """Test that async client uses connection pooling."""
    async def _test():
        client1 = await get_async_client()
        client2 = await get_async_client()

        # Should return the same instance
        assert client1 is client2

        await close_async_client()

    asyncio.run(_test())


def test_async_modules_import():
    """Test that async modules can be imported."""
    from llmtest.async_llm_client import query_llm_async, query_llm_batch
    from llmtest.async_payloads import generate_payloads_async, generate_payloads_sync
    from llmtest.async_evaluation import evaluate_response_async, evaluate_responses_batch_async

    # Just verify imports work
    assert query_llm_async is not None
    assert query_llm_batch is not None
    assert generate_payloads_async is not None
    assert generate_payloads_sync is not None
    assert evaluate_response_async is not None
    assert evaluate_responses_batch_async is not None


if __name__ == '__main__':
    pytest.main([__file__, "-v", "-s"])
