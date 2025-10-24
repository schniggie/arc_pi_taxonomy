"""
Tests for the new FUZZ-based curl parser functionality.
"""
import pytest
from llmtest.curl_parser import FuzzCurlParser, parse_curl_with_fuzz, CurlParseError
from llmtest.model import ParsedRequest


class TestFuzzCurlParser:
    """Test suite for FUZZ-based curl parsing."""

    def test_json_body_fuzz(self):
        """Test FUZZ detection in JSON request body."""
        curl_cmd = '''curl -X POST https://api.openai.com/v1/chat/completions \\
          -H "Content-Type: application/json" \\
          -H "Authorization: Bearer sk-1234" \\
          -d '{"messages": [{"role": "user", "content": "FUZZ"}], "model": "gpt-4"}'
        '''

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].location_type == "body"
        assert fuzz_locations[0].key == "messages[0].content"
        assert fuzz_locations[0].original_value == "FUZZ"

        # Test injection
        injected = parser.inject_payload(parsed_request, "INJECTED_PAYLOAD")
        assert injected.body["messages"][0]["content"] == "INJECTED_PAYLOAD"

    def test_header_fuzz(self):
        """Test FUZZ detection in headers."""
        curl_cmd = '''curl -X POST https://api.example.com/auth \\
          -H "Authorization: Bearer FUZZ" \\
          -H "Content-Type: application/json" \\
          -d '{"username": "admin"}'
        '''

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].location_type == "header"
        assert fuzz_locations[0].key == "Authorization"
        assert fuzz_locations[0].original_value == "Bearer FUZZ"

        # Test injection
        injected = parser.inject_payload(parsed_request, "secret-token")
        assert injected.headers["Authorization"] == "Bearer secret-token"

    def test_url_parameter_fuzz(self):
        """Test FUZZ detection in URL parameters."""
        curl_cmd = 'curl -X GET "https://api.example.com/search?q=FUZZ&limit=10"'

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].location_type == "url_param"
        assert fuzz_locations[0].key == "q"
        assert fuzz_locations[0].original_value == "FUZZ"

        # Test injection
        injected = parser.inject_payload(parsed_request, "malicious query")
        assert "q=malicious%20query" in injected.url or "q=malicious query" in injected.url

    def test_form_data_fuzz(self):
        """Test FUZZ detection in form data."""
        curl_cmd = '''curl -X POST https://api.example.com/login \\
          -H "Content-Type: application/x-www-form-urlencoded" \\
          -d "username=admin&password=FUZZ"
        '''

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].location_type == "body"
        assert "password" in fuzz_locations[0].key
        assert fuzz_locations[0].original_value == "FUZZ"

        # Test injection
        injected = parser.inject_payload(parsed_request, "secret123")
        assert "password=secret123" in injected.body

    def test_multiple_fuzz_locations(self):
        """Test handling of multiple FUZZ locations."""
        curl_cmd = '''curl -X POST https://api.example.com/test \\
          -H "Authorization: Bearer FUZZ" \\
          -d '{"message": "FUZZ", "user": "admin"}'
        '''

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 2

        # Should find both header and body FUZZ
        location_types = [loc.location_type for loc in fuzz_locations]
        assert "header" in location_types
        assert "body" in location_types

    def test_no_fuzz_keyword_error(self):
        """Test that missing FUZZ keyword raises an error."""
        curl_cmd = '''curl -X POST https://api.example.com/test \\
          -H "Content-Type: application/json" \\
          -d '{"message": "hello", "user": "admin"}'
        '''

        parser = FuzzCurlParser()
        with pytest.raises(CurlParseError, match="No 'FUZZ' keywords found"):
            parser.parse_curl_with_fuzz(curl_cmd)

    def test_complex_nested_json_fuzz(self):
        """Test FUZZ detection in deeply nested JSON."""
        curl_cmd = '''curl -X POST https://api.example.com/complex \\
          -H "Content-Type: application/json" \\
          -d '{
            "data": {
              "messages": [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "FUZZ"}
              ],
              "settings": {
                "temperature": 0.7,
                "model": "gpt-4"
              }
            }
          }'
        '''

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].location_type == "body"
        assert "messages[1].content" in fuzz_locations[0].key

        # Test injection preserves structure
        injected = parser.inject_payload(parsed_request, "INJECTED")
        assert injected.body["data"]["messages"][1]["content"] == "INJECTED"
        assert injected.body["data"]["settings"]["temperature"] == 0.7

    def test_real_world_browser_export(self):
        """Test with realistic browser-exported curl commands."""
        # Simulate a real curl command copied from Chrome DevTools
        curl_cmd = '''curl 'https://api.openai.com/v1/chat/completions' \\
          -H 'accept: application/json' \\
          -H 'accept-language: en-US,en;q=0.9' \\
          -H 'authorization: Bearer FUZZ' \\
          -H 'content-type: application/json' \\
          -H 'origin: https://chat.openai.com' \\
          -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' \\
          --data-raw '{"model":"gpt-4","messages":[{"role":"user","content":"Hello"}],"stream":false}'
        '''

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].location_type == "header"
        assert fuzz_locations[0].key == "authorization"

        # Verify all headers are preserved
        assert "user-agent" in parsed_request.headers
        assert "origin" in parsed_request.headers
        assert parsed_request.headers["content-type"] == "application/json"

    def test_graphql_fuzz(self):
        """Test FUZZ in GraphQL queries."""
        curl_cmd = '''curl -X POST https://api.github.com/graphql \\
          -H "Authorization: token FUZZ" \\
          -H "Content-Type: application/json" \\
          -d '{"query": "query { viewer { login } }"}'
        '''

        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)

        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].location_type == "header"
        assert fuzz_locations[0].key == "Authorization"

        # Test injection works
        injected = parser.inject_payload(parsed_request, "ghp_secret_token")
        assert injected.headers["Authorization"] == "token ghp_secret_token"

    def test_malformed_curl_command(self):
        """Test handling of malformed curl commands."""
        malformed_curl = "this is not a curl command FUZZ"

        parser = FuzzCurlParser()
        with pytest.raises(CurlParseError):
            parser.parse_curl_with_fuzz(malformed_curl)

    def test_convenience_function(self):
        """Test the convenience function parse_curl_with_fuzz."""
        curl_cmd = 'curl -X POST https://api.test.com -d "data=FUZZ"'

        parsed_request, fuzz_locations = parse_curl_with_fuzz(curl_cmd)

        assert isinstance(parsed_request, ParsedRequest)
        assert len(fuzz_locations) == 1
        assert fuzz_locations[0].original_value == "FUZZ"


class TestBackwardCompatibility:
    """Test that existing functionality still works."""

    def test_legacy_parse_curl_command(self):
        """Test that the legacy function still works for non-FUZZ commands."""
        from llmtest.parsing import parse_curl_command

        curl_cmd = '''curl -X POST https://api.example.com/test \\
          -H "Content-Type: application/json" \\
          -d '{"message": "hello"}'
        '''

        # Should not raise an error
        parsed = parse_curl_command(curl_cmd)
        assert isinstance(parsed, ParsedRequest)
        assert parsed.method == "POST"
        assert parsed.url == "https://api.example.com/test"


if __name__ == '__main__':
    # Run a quick test
    curl_cmd = '''curl -X POST https://api.openai.com/v1/chat/completions \\
      -H "Authorization: Bearer FUZZ" \\
      -d '{"messages": [{"role": "user", "content": "test"}]}'
    '''

    try:
        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)
        print(f"✓ Successfully parsed curl command")
        print(f"✓ Found {len(fuzz_locations)} FUZZ locations")
        for loc in fuzz_locations:
            print(f"  - {loc.location_type}: {loc.key}")

        # Test injection
        injected = parser.inject_payload(parsed_request, "sk-test123")
        print(f"✓ Injection successful")
        print(f"✓ Authorization header: {injected.headers.get('Authorization')}")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()