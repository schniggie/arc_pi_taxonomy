"""
Enhanced curl parser with FUZZ keyword support for flexible injection points.
"""
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import parse_qs, urlparse
import uncurl

from llmtest.model import ParsedRequest


class FuzzLocation:
    """Represents a FUZZ injection location in a curl command."""

    def __init__(self, location_type: str, key: str, original_value: str):
        self.location_type = location_type  # 'header', 'body', 'url_param', 'url_path'
        self.key = key  # header name, json key, param name, etc.
        self.original_value = original_value  # original value containing FUZZ


class CurlParseError(Exception):
    """Exception raised when curl parsing fails."""
    pass


class FuzzCurlParser:
    """
    Advanced curl parser that can detect FUZZ keywords and create injection-ready requests.
    """

    FUZZ_KEYWORD = "FUZZ"

    def __init__(self):
        self.fuzz_locations: List[FuzzLocation] = []

    def parse_curl_with_fuzz(self, curl_command: str) -> Tuple[ParsedRequest, List[FuzzLocation]]:
        """
        Parse a curl command and detect FUZZ injection points.

        Args:
            curl_command: The curl command string (potentially containing FUZZ keywords)

        Returns:
            Tuple of (ParsedRequest with FUZZ placeholders, List of FuzzLocation objects)

        Raises:
            CurlParseError: If curl parsing fails or no FUZZ keywords found
        """
        self.fuzz_locations = []

        try:
            # Use uncurl to parse the basic structure
            parsed = uncurl.parse_context(curl_command)
        except Exception as e:
            raise CurlParseError(f"Failed to parse curl command: {e}") from e

        # Extract basic request components
        method = parsed.method.upper()
        url = parsed.url
        headers = dict(parsed.headers) if parsed.headers else {}

        # Check for FUZZ in URL
        url, url_fuzz_found = self._extract_url_fuzz(url)

        # Check for FUZZ in headers
        headers, header_fuzz_found = self._extract_header_fuzz(headers)

        # Handle request body
        body = None
        body_fuzz_found = False

        if parsed.data:
            if isinstance(parsed.data, dict):
                # JSON data
                body, body_fuzz_found = self._extract_json_fuzz(parsed.data)
            else:
                # String data (could be form data, plain text, etc.)
                body, body_fuzz_found = self._extract_string_fuzz(parsed.data, headers.get('Content-Type', ''))

        # Validate that at least one FUZZ was found
        total_fuzz_found = url_fuzz_found + header_fuzz_found + body_fuzz_found
        if total_fuzz_found == 0:
            raise CurlParseError(f"No '{self.FUZZ_KEYWORD}' keywords found in curl command. "
                               f"Please mark injection points with '{self.FUZZ_KEYWORD}'.")

        if total_fuzz_found > 1:
            # For now, we'll support multiple FUZZ locations but warn the user
            # In future versions, we could support multiple simultaneous injections
            pass

        parsed_request = ParsedRequest(
            method=method,
            url=url,
            headers=headers,
            body=body
        )

        return parsed_request, self.fuzz_locations

    def _extract_url_fuzz(self, url: str) -> Tuple[str, int]:
        """Extract FUZZ from URL parameters and path."""
        fuzz_count = 0

        # Parse URL components
        parsed_url = urlparse(url)

        # Check URL path for FUZZ
        if self.FUZZ_KEYWORD in parsed_url.path:
            self.fuzz_locations.append(FuzzLocation('url_path', 'path', parsed_url.path))
            # Replace FUZZ with placeholder for now (will be injected later)
            url = url.replace(self.FUZZ_KEYWORD, "{{FUZZ_PLACEHOLDER}}")
            fuzz_count += 1

        # Check URL parameters for FUZZ
        if parsed_url.query:
            params = parse_qs(parsed_url.query, keep_blank_values=True)
            for param_name, param_values in params.items():
                for value in param_values:
                    if self.FUZZ_KEYWORD in value:
                        self.fuzz_locations.append(FuzzLocation('url_param', param_name, value))
                        # Replace in URL
                        url = url.replace(f"{param_name}={value}", f"{param_name}={{{{FUZZ_PLACEHOLDER}}}}")
                        fuzz_count += 1

        return url, fuzz_count

    def _extract_header_fuzz(self, headers: Dict[str, str]) -> Tuple[Dict[str, str], int]:
        """Extract FUZZ from headers."""
        fuzz_count = 0
        updated_headers = {}

        for header_name, header_value in headers.items():
            if self.FUZZ_KEYWORD in header_value:
                self.fuzz_locations.append(FuzzLocation('header', header_name, header_value))
                updated_headers[header_name] = header_value.replace(self.FUZZ_KEYWORD, "{{FUZZ_PLACEHOLDER}}")
                fuzz_count += 1
            else:
                updated_headers[header_name] = header_value

        return updated_headers, fuzz_count

    def _extract_json_fuzz(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Extract FUZZ from JSON data recursively."""
        fuzz_count = 0

        def process_json_recursive(obj: Any, path: str = "") -> Tuple[Any, int]:
            nonlocal fuzz_count
            local_count = 0

            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    processed_value, count = process_json_recursive(value, current_path)
                    result[key] = processed_value
                    local_count += count
                return result, local_count

            elif isinstance(obj, list):
                result = []
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    processed_item, count = process_json_recursive(item, current_path)
                    result.append(processed_item)
                    local_count += count
                return result, local_count

            elif isinstance(obj, str) and self.FUZZ_KEYWORD in obj:
                self.fuzz_locations.append(FuzzLocation('body', path, obj))
                local_count += 1
                return obj.replace(self.FUZZ_KEYWORD, "{{FUZZ_PLACEHOLDER}}"), local_count

            else:
                return obj, local_count

        processed_data, fuzz_count = process_json_recursive(data)
        return processed_data, fuzz_count

    def _extract_string_fuzz(self, data: str, content_type: str) -> Tuple[str, int]:
        """Extract FUZZ from string data (form data, plain text, etc.)."""
        fuzz_count = 0

        if self.FUZZ_KEYWORD in data:
            # For form data, try to parse it
            if 'application/x-www-form-urlencoded' in content_type:
                try:
                    params = parse_qs(data, keep_blank_values=True)
                    for param_name, param_values in params.items():
                        for value in param_values:
                            if self.FUZZ_KEYWORD in value:
                                self.fuzz_locations.append(FuzzLocation('body', f"form.{param_name}", value))
                                fuzz_count += 1
                except:
                    # If parsing fails, treat as plain text
                    self.fuzz_locations.append(FuzzLocation('body', 'raw', data))
                    fuzz_count += 1
            else:
                # Plain text or other format
                self.fuzz_locations.append(FuzzLocation('body', 'raw', data))
                fuzz_count += 1

            # Replace FUZZ in the data
            processed_data = data.replace(self.FUZZ_KEYWORD, "{{FUZZ_PLACEHOLDER}}")
            return processed_data, fuzz_count

        return data, fuzz_count

    def inject_payload(self, parsed_request: ParsedRequest, payload: str) -> ParsedRequest:
        """
        Inject a payload into the request at all FUZZ locations.

        Args:
            parsed_request: The parsed request with FUZZ placeholders
            payload: The payload to inject

        Returns:
            ParsedRequest with payload injected
        """
        # Deep copy to avoid modifying original
        import copy
        injected_request = copy.deepcopy(parsed_request)

        # Replace all FUZZ placeholders with the actual payload
        injected_request.url = injected_request.url.replace("{{FUZZ_PLACEHOLDER}}", payload)

        # Replace in headers
        for header_name, header_value in injected_request.headers.items():
            if "{{FUZZ_PLACEHOLDER}}" in header_value:
                injected_request.headers[header_name] = header_value.replace("{{FUZZ_PLACEHOLDER}}", payload)

        # Replace in body
        if injected_request.body:
            if isinstance(injected_request.body, dict):
                injected_request.body = self._inject_json_recursive(injected_request.body, payload)
            elif isinstance(injected_request.body, str):
                injected_request.body = injected_request.body.replace("{{FUZZ_PLACEHOLDER}}", payload)

        return injected_request

    def _inject_json_recursive(self, obj: Any, payload: str) -> Any:
        """Recursively inject payload into JSON structure."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                result[key] = self._inject_json_recursive(value, payload)
            return result
        elif isinstance(obj, list):
            return [self._inject_json_recursive(item, payload) for item in obj]
        elif isinstance(obj, str) and "{{FUZZ_PLACEHOLDER}}" in obj:
            return obj.replace("{{FUZZ_PLACEHOLDER}}", payload)
        else:
            return obj


def parse_curl_with_fuzz(curl_command: str) -> Tuple[ParsedRequest, List[FuzzLocation]]:
    """
    Convenience function to parse a curl command with FUZZ detection.

    Args:
        curl_command: The curl command string containing FUZZ keywords

    Returns:
        Tuple of (ParsedRequest, List of FuzzLocation objects)

    Raises:
        CurlParseError: If parsing fails or no FUZZ keywords found
    """
    parser = FuzzCurlParser()
    return parser.parse_curl_with_fuzz(curl_command)


# Backward compatibility function
def parse_curl_command(curl_string: str) -> ParsedRequest:
    """
    Legacy function for backward compatibility.
    This will try to parse without FUZZ and fall back to the old behavior.
    """
    try:
        # Try the new FUZZ-aware parser first
        parser = FuzzCurlParser()
        parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_string)
        return parsed_request
    except CurlParseError:
        # Fall back to basic parsing without FUZZ
        try:
            parsed = uncurl.parse_context(curl_string)

            headers = dict(parsed.headers) if parsed.headers else {}
            body = parsed.data if parsed.data else None

            return ParsedRequest(
                method=parsed.method.upper(),
                url=parsed.url,
                headers=headers,
                body=body
            )
        except Exception as e:
            raise ValueError(f"Failed to parse curl command: {e}") from e


if __name__ == '__main__':
    # Test examples
    test_cases = [
        # JSON body FUZZ
        '''curl -X POST https://api.example.com/chat \\
          -H "Content-Type: application/json" \\
          -H "Authorization: Bearer sk-1234" \\
          -d '{"messages": [{"role": "user", "content": "FUZZ"}], "model": "gpt-4"}'
        ''',

        # Header FUZZ
        '''curl -X POST https://api.example.com/auth \\
          -H "Authorization: Bearer FUZZ" \\
          -d '{"username": "admin"}'
        ''',

        # URL parameter FUZZ
        '''curl -X GET https://api.example.com/search?q=FUZZ&limit=10''',

        # Form data FUZZ
        '''curl -X POST https://api.example.com/login \\
          -H "Content-Type: application/x-www-form-urlencoded" \\
          -d "username=admin&password=FUZZ"
        '''
    ]

    parser = FuzzCurlParser()

    for i, curl_cmd in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Curl: {curl_cmd.strip()}")

        try:
            parsed_request, fuzz_locations = parser.parse_curl_with_fuzz(curl_cmd)
            print(f"✓ Parsed successfully")
            print(f"Method: {parsed_request.method}")
            print(f"URL: {parsed_request.url}")
            print(f"FUZZ locations found: {len(fuzz_locations)}")

            for loc in fuzz_locations:
                print(f"  - {loc.location_type}: {loc.key} = '{loc.original_value}'")

            # Test injection
            test_payload = "INJECTED_PAYLOAD"
            injected = parser.inject_payload(parsed_request, test_payload)
            print(f"After injection: {injected.url}")
            if injected.body:
                print(f"Body after injection: {injected.body}")

        except CurlParseError as e:
            print(f"✗ Parse failed: {e}")