import json
from curlconverter import CurlConverter
from llmtest.model import ParsedRequest


def parse_curl_command(curl_string: str) -> ParsedRequest:
    """
    Parses a curl command string and returns a ParsedRequest object.
    """
    try:
        curl_converter = CurlConverter(curl_string)
        parsed_data = curl_converter.convert()

        method = parsed_data.get("method", "GET").upper()
        url = parsed_data.get("url", "")
        headers = parsed_data.get("headers", {})

        body = None
        if "data" in parsed_data:
            body_str = parsed_data["data"]
            # If the body is a string, it might be JSON.
            # Try to parse it if the content-type suggests so.
            content_type = headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError:
                    # If it's not valid JSON, keep it as a string.
                    body = body_str
            else:
                body = body_str
        elif "json" in parsed_data:
            # The converter might also directly provide a json key
            body = parsed_data["json"]

        return ParsedRequest(
            method=method,
            url=url,
            headers=headers,
            body=body
        )
    except Exception as e:
        # Here you might want to log the error or handle it more gracefully
        raise ValueError(f"Failed to parse curl command: {e}") from e
