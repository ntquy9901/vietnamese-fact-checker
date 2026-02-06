from pydantic import BaseModel
from typing import List, Optional

class ClaimRequest(BaseModel):
    claim: str

class Evidence(BaseModel):
    text: str
    url: str
    title: Optional[str] = None

class ClaimResponse(BaseModel):
    claim: str
    verdict: str  # SUPPORTED, REFUTED, NOT_ENOUGH_INFO, ERROR
    confidence: float
    rationale: str
    evidence: List[Evidence]
    evidence_count: int
    processing_time: float
    method: str
    error: Optional[str] = None
    sources: List[str] = []

class HealthResponse(BaseModel):
    status: str
    method: str
    components: dict
