import pytest
from llmtest.parsing import parse_curl_command

def test_parse_simple_curl():
    """Test parsing a simple POST curl command."""
    curl_string = "curl -X POST https://example.com -H 'Content-Type: application/json' -d '{\"key\": \"value\"}'"

    parsed = parse_curl_command(curl_string)
    assert parsed.method == "POST"
    assert parsed.url == "https://example.com"
    assert parsed.headers["Content-Type"] == "application/json"
    assert parsed.body == {"key": "value"}

def test_parse_get_request():
    """Test parsing a simple GET request."""
    curl_string = "curl https://example.com/items"

    parsed = parse_curl_command(curl_string)
    assert parsed.url == "https://example.com/items"
    assert parsed.method == "GET"

def test_parse_complex_headers():
    """Test parsing curl with multiple headers."""
    curl_string = '''curl -X POST https://api.example.com \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer token123" \\
      -H "User-Agent: TestApp/1.0" \\
      -d '{"message": "hello"}'
    '''

    parsed = parse_curl_command(curl_string)
    assert parsed.method == "POST"
    assert parsed.headers["Content-Type"] == "application/json"
    assert parsed.headers["Authorization"] == "Bearer token123"
    assert parsed.headers["User-Agent"] == "TestApp/1.0"
    assert parsed.body["message"] == "hello"

def test_parse_form_data():
    """Test parsing curl with form data."""
    curl_string = '''curl -X POST https://example.com/login \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      -d "username=admin&password=secret"
    '''

    parsed = parse_curl_command(curl_string)
    assert parsed.method == "POST"
    assert parsed.body == "username=admin&password=secret"

def test_parse_with_query_parameters():
    """Test parsing curl with URL query parameters."""
    curl_string = 'curl "https://api.example.com/search?q=test&limit=10"'

    parsed = parse_curl_command(curl_string)
    assert parsed.method == "GET"
    assert "q=test" in parsed.url
    assert "limit=10" in parsed.url

def test_invalid_curl_string():
    """Test that invalid curl commands raise ValueError."""
    curl_string = "this is not a curl command"

    with pytest.raises(ValueError, match="Failed to parse curl command"):
        parse_curl_command(curl_string)

def test_empty_curl_string():
    """Test that empty curl commands raise ValueError."""
    with pytest.raises(ValueError):
        parse_curl_command("")

def test_backward_compatibility():
    """Test that legacy parsing still works for existing use cases."""
    # This should work even without FUZZ keywords
    curl_string = '''curl -X POST https://api.openai.com/v1/chat/completions \\
      -H "Authorization: Bearer sk-1234" \\
      -d '{"messages": [{"role": "user", "content": "Hello"}]}'
    '''

    parsed = parse_curl_command(curl_string)
    assert parsed.method == "POST"
    assert "openai.com" in parsed.url
    assert "Authorization" in parsed.headers
    assert isinstance(parsed.body, dict)
    assert "messages" in parsed.body
