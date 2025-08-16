import pytest
from pydantic import ValidationError
from llmtest.model import ParsedRequest, TestResult, Verdict, Payload

def test_parsed_request_valid():
    data = {
        "method": "POST",
        "url": "https://example.com",
        "headers": {"Content-Type": "application/json"},
        "body": {"key": "value"}
    }
    req = ParsedRequest(**data)
    assert req.method == "POST"
    assert req.body == {"key": "value"}

def test_test_result_valid():
    payload = Payload(intent="a", technique="b", evasion="c", content="d")
    data = {
        "payload": payload,
        "request_sent": {},
        "response_excerpt": "...",
        "verdict": Verdict.SUCCESS,
        "confidence": 0.8,
        "attack_path": "a/b/c"
    }
    result = TestResult(**data)
    assert result.verdict == Verdict.SUCCESS
    assert result.confidence == 0.8

def test_test_result_invalid_confidence():
    payload = Payload(intent="a", technique="b", evasion="c", content="d")
    with pytest.raises(ValidationError):
        TestResult(
            payload=payload,
            request_sent={},
            response_excerpt="...",
            verdict=Verdict.FAIL,
            confidence=1.5,  # Out of bounds
            attack_path="a/b/c"
        )

    with pytest.raises(ValidationError):
        TestResult(
            payload=payload,
            request_sent={},
            response_excerpt="...",
            verdict=Verdict.FAIL,
            confidence=-0.5, # Out of bounds
            attack_path="a/b/c"
        )

def test_verdict_enum():
    assert Verdict.SUCCESS == "success"
    assert Verdict.FAIL == "fail"
    assert Verdict.PARTIAL == "partial"
