from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class RetrievedChunk:
    citation_id: str
    chunk_id: int
    country_code: str
    visa_id: str
    visa_name: str
    section: str
    doc_path: str
    text: str
    distance: float
    similarity: float


@dataclass
class EligibilityResponse:
    eligibility_status: str
    explanation: str
    requirements_met: List[str] = field(default_factory=list)
    missing_requirements: List[str] = field(default_factory=list)
    required_documents: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    important_notes: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    citations: List[Dict[str, Any]] = field(default_factory=list)
    grounded: bool = True
    raw_model_output: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
