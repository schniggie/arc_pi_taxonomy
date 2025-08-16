import re
import json
import copy
from typing import Dict, Any, List
import requests
from llmtest.model import RequestTemplate, Payload, TestResult, Verdict

def set_value_at_path(data: Dict[str, Any], path: str, value: Any):
    """
    Sets a value in a nested dictionary/list structure based on a path string.
    e.g., path="body.messages[0].content"
    """
    keys = re.findall(r'[^.\[\]]+', path)
    current_element = data
    for i, key in enumerate(keys[:-1]):
        if key.isdigit():
            idx = int(key)
            if isinstance(current_element, list) and idx < len(current_element):
                current_element = current_element[idx]
            else:
                raise IndexError(f"Index {idx} out of bounds.")
        else:
            if isinstance(current_element, dict) and key in current_element:
                current_element = current_element[key]
            else:
                raise KeyError(f"Key '{key}' not found.")

    last_key = keys[-1]
    if last_key.isdigit():
        idx = int(last_key)
        if isinstance(current_element, list) and idx < len(current_element):
            current_element[idx] = value
        else:
            raise IndexError(f"Index {idx} for setting value is out of bounds.")
    else:
        if isinstance(current_element, dict):
            current_element[last_key] = value
        else:
            raise TypeError(f"Cannot set key '{last_key}' on a non-dictionary element.")


def execute_test(request_template: RequestTemplate, payload: Payload) -> requests.Response:
    """
    Injects a payload into a request template and executes the HTTP request.
    """
    # Deep copy to avoid modifying the original template's parsed request
    request_data = copy.deepcopy(request_template.parsed_request.model_dump())

    # Inject the payload
    try:
        set_value_at_path(request_data, request_template.injection_point, payload.content)
    except (KeyError, IndexError, TypeError) as e:
        # If injection fails, we can't proceed with this test.
        # We can return a mock response indicating failure or raise an exception.
        # For now, let's raise a specific error.
        raise ValueError(f"Failed to inject payload at '{request_template.injection_point}': {e}") from e

    # Prepare arguments for requests
    method = request_data['method']
    url = request_data['url']
    headers = request_data['headers']
    body = request_data.get('body')

    # `requests` expects `data` for form data and `json` for JSON
    data_arg = None
    json_arg = None
    if body:
        if isinstance(body, dict) or isinstance(body, list):
            json_arg = body
        else:
            data_arg = str(body).encode('utf-8') # requests prefers bytes for data

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_arg,
            data=data_arg,
            timeout=30  # Add a timeout
        )
        return response
    except requests.RequestException as e:
        # Handle network errors by creating a mock-like response object
        # This allows the evaluation step to process it as a failure.
        response = requests.Response()
        response.status_code = 599 # Custom status code for network errors
        response.reason = "Network Error"
        response._content = str(e).encode('utf-8')
        return response


if __name__ == '__main__':
    from unittest.mock import patch, MagicMock
    from llmtest.model import ParsedRequest

    # --- Test 1: Successful Injection and Execution ---
    print("--- Running Test 1: Successful Case ---")

    # 1. Create a sample request template
    template = RequestTemplate(
        id="test1",
        raw_request="curl ...",
        parsed_request=ParsedRequest(
            method="POST",
            url="https://api.example.com/v1/chat",
            headers={"Content-Type": "application/json", "Authorization": "Bearer ..."},
            body={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ]
            }
        ),
        injection_point="body.messages[1].content"
    )

    # 2. Create a sample payload
    pld = Payload(
        intent="test_intent",
        technique="test_technique",
        evasion="test_evasion",
        content="This is the injected payload."
    )

    # 3. Mock the requests.request call
    with patch('requests.request') as mock_request:
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "This is a mock response."}
        mock_response.text = json.dumps({"response": "This is a mock response."})
        mock_request.return_value = mock_response

        # 4. Execute the test
        result_response = execute_test(template, pld)

        # 5. Verify the result
        print(f"Mocked Response Status: {result_response.status_code}")
        print(f"Mocked Response Body: {result_response.json()}")

        # Verify that requests.request was called with the injected payload
        called_args, called_kwargs = mock_request.call_args
        injected_body = called_kwargs['json']
        print("Injected body in request:", injected_body)
        assert injected_body['messages'][1]['content'] == "This is the injected payload."
        print("Assertion successful: Payload was correctly injected.")

    # --- Test 2: Injection Failure ---
    print("\n--- Running Test 2: Injection Failure Case ---")
    invalid_template = template.model_copy(update={"injection_point": "body.messages[5].content"})
    try:
        execute_test(invalid_template, pld)
    except ValueError as e:
        print(f"Successfully caught expected error: {e}")
        assert "out of bounds" in str(e)
