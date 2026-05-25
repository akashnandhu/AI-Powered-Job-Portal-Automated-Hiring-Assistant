from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class RoundContribution:
    raw_score: float
    weight_applied: str
    weighted_contribution: float

@dataclass
class UnifiedCandidateScore:
    """
    Unified Candidate Score Object.
    Represents the final structured output of all aggregated evaluation stages.
    """
    candidate_id: str
    role_evaluated_for: str
    final_hiring_fit_score: float
    readiness_band: str
    risk_tag: str
    weight_system_used: str
    cross_round_breakdown: Dict[str, RoundContribution] = field(default_factory=dict)
    integrity_insights: List[str] = field(default_factory=list)
    machine_test_integrated: bool = False
    technical_interview_integrated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the object to a standard JSON-compatible dictionary."""
        return {
            "candidate_id": self.candidate_id,
            "role_evaluated_for": self.role_evaluated_for,
            "final_hiring_fit_score": round(self.final_hiring_fit_score, 2),
            "readiness_band": self.readiness_band,
            "risk_tag": self.risk_tag,
            "weight_system_used": self.weight_system_used,
            "cross_round_breakdown": {
                k: {
                    "raw_score": round(v.raw_score, 2),
                    "weight_applied": v.weight_applied,
                    "weighted_contribution": round(v.weighted_contribution, 2)
                } for k, v in self.cross_round_breakdown.items()
            },
            "integrity_insights": self.integrity_insights,
            "machine_test_integrated": self.machine_test_integrated,
            "technical_interview_integrated": self.technical_interview_integrated
        }
