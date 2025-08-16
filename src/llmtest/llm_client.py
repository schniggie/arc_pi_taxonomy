import os
import requests

API_BASE_URL = "https://openrouter.ai/api/v1"
CHAT_COMPLETIONS_ENDPOINT = f"{API_BASE_URL}/chat/completions"

class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass

def query_llm(prompt: str, model: str) -> str:
    """
    Queries the specified LLM model via the OpenRouter API.

    Args:
        prompt: The prompt to send to the LLM.
        model: The name of the model to query.

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
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(CHAT_COMPLETIONS_ENDPOINT, headers=headers, json=data, timeout=60)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            content = response_json["choices"][0].get("message", {}).get("content")
            if content:
                return content.strip()

        raise LLMClientError(f"Received an unexpected response format from the API: {response.text}")

    except requests.RequestException as e:
        raise LLMClientError(f"A network error occurred: {e}") from e
    except Exception as e:
        # Catch any other unexpected errors, including JSON decoding errors
        raise LLMClientError(f"An unexpected error occurred: {e}") from e


if __name__ == '__main__':
    # Example usage for testing the client
    # To run this, you must have the OPENROUTER_API_KEY environment variable set.
    # e.g., OPENROUTER_API_KEY="..." python3 src/llmtest/llm_client.py

    test_prompt = "What is the capital of France? Respond with just the name of the city."
    test_model = "z-ai/glm-4.5-air:free"

    print(f"Querying model '{test_model}' with prompt: '{test_prompt}'")

    try:
        # Note: This will make a real API call if the key is set.
        # In a real test suite, you would mock `requests.post`.
        api_key_present = os.environ.get("OPENROUTER_API_KEY")
        if not api_key_present:
            print("\nSkipping live test: OPENROUTER_API_KEY not set.")
            print("To run a live test, set the environment variable.")
        else:
            response_content = query_llm(test_prompt, test_model)
            print(f"\nResponse from LLM: '{response_content}'")
            assert "paris" in response_content.lower()
            print("\nAssertion passed: Response contains 'paris'.")

    except (ValueError, LLMClientError) as e:
        print(f"\nAn error occurred: {e}")
