from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class EvidenceResult:
    source_type: str
    classification: str
    confidence: float | None
    indicators: list[str]
    details: dict[str, Any]

    def to_dict(self):
        return asdict(self)