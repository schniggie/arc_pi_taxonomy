from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum


class ParsedRequest(BaseModel):
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[Any] = None


class RequestTemplate(BaseModel):
    id: str
    raw_request: str
    parsed_request: ParsedRequest
    injection_point: str  # e.g., "body.messages[0].content"


class TestConfig(BaseModel):
    attack_intent: str
    goal_description: str
    max_payloads: int


class Payload(BaseModel):
    intent: str
    technique: str
    evasion: str
    content: str


class Verdict(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAIL = "fail"


class TestResult(BaseModel):
    payload: Payload
    request_sent: Dict[str, Any]  # A simplified version of the request that was sent
    response_excerpt: str
    verdict: Verdict
    confidence: float = Field(..., ge=0, le=1)
    attack_path: str  # e.g., "data_exfiltration/direct_prompting/no_evasion"
