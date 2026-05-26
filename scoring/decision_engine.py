from typing import Dict, Any, List
from dataclasses import dataclass
from scoring.unified_candidate_score import UnifiedCandidateScore

@dataclass
class HiringDecision:
    """
    Candidate Decision Output Format.
    Represents the final hiring outcome and the explanation behind it.
    """
    candidate_id: str
    decision: str  # Categories: "Selected", "Hold / Review", "Rejected"
    confidence_score: float  # Scale from 0.0 to 100.0
    reasoning: List[str]
    risk_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "decision": self.decision,
            "confidence_score": round(self.confidence_score, 2),
            "reasoning": self.reasoning,
            "risk_factors": self.risk_factors
        }

class DecisionEngine:
    """
    Decision-making AI for automated hiring outcomes.
    Implements rule-based + score-based hybrid logic to determine final candidate status,
    confidence levels, and explainable insights.
    """
    def __init__(self, selected_threshold: float = 75.0, reject_threshold: float = 55.0):
        self.selected_threshold = selected_threshold
        self.reject_threshold = reject_threshold
        
    def evaluate(self, candidate_score: UnifiedCandidateScore) -> HiringDecision:
        """
        Evaluates a candidate based on their unified score and risk factors
        to produce a final hiring decision.
        """
        decision = "Hold / Review"
        confidence_score = 0.0
        reasoning = []
        risk_factors = []
        
        # 1. Analyze Risk Factors (Integrity & Behavior)
        if candidate_score.risk_tag == "RED":
            risk_factors.append("Critical: High Integrity Risk Detected")
        elif candidate_score.risk_tag == "YELLOW":
            risk_factors.append("Warning: Moderate Integrity Risk Detected")
            
        if candidate_score.integrity_insights:
            risk_factors.extend(candidate_score.integrity_insights)
            
        # 2. Rule + Score Hybrid Logic
        score = candidate_score.final_hiring_fit_score
        
        # Rule 1: Severe Risk override (Hard Rule)
        if candidate_score.risk_tag == "RED":
            decision = "Rejected"
            reasoning.append(f"Candidate automatically rejected due to severe integrity/behavioral violations (Risk Tag: RED).")
            confidence_score = 95.0 # High confidence due to explicit severe violation
            
        # Rule 2: Strong Performers (Score Threshold)
        elif score >= self.selected_threshold:
            if candidate_score.risk_tag == "GREEN":
                decision = "Selected"
                reasoning.append(f"Strong overall performance with a unified score of {score:.2f}%, exceeding the selection threshold of {self.selected_threshold}%.")
                # Confidence scales with score above threshold
                confidence_score = min(80.0 + (score - self.selected_threshold), 99.0)
            else:
                decision = "Hold / Review"
                reasoning.append(f"Achieved a qualifying score ({score:.2f}%) but placed on hold for manual review due to identified risk factors.")
                confidence_score = 85.0
                
        # Rule 3: Poor Performers (Score Threshold)
        elif score < self.reject_threshold:
            decision = "Rejected"
            reasoning.append(f"Unified score ({score:.2f}%) falls below the minimum viable requirement of {self.reject_threshold}%.")
            confidence_score = min(80.0 + (self.reject_threshold - score), 99.0)
            
        # Rule 4: Borderline Performers (Hybrid / Ambiguous)
        else:
            decision = "Hold / Review"
            reasoning.append(f"Score ({score:.2f}%) is in the borderline range; further team review or subsequent rounds recommended.")
            confidence_score = 75.0
            
        # 3. Enhanced Explainability Based on Round Breakdown
        if candidate_score.cross_round_breakdown:
            strong_rounds = []
            weak_rounds = []
            for round_name, contribution in candidate_score.cross_round_breakdown.items():
                if contribution.raw_score >= 80:
                    strong_rounds.append(round_name.replace("_round", "").replace("_", " ").title())
                elif contribution.raw_score < 50:
                    weak_rounds.append(round_name.replace("_round", "").replace("_", " ").title())
                    
            if strong_rounds and decision == "Selected":
                reasoning.append(f"Demonstrated exceptional performance in: {', '.join(strong_rounds)}.")
            if weak_rounds:
                if decision == "Rejected":
                    reasoning.append(f"Significant poor performance observed in: {', '.join(weak_rounds)}.")
                else:
                    reasoning.append(f"Areas of concern identified requiring further evaluation: {', '.join(weak_rounds)}.")
                    
        return HiringDecision(
            candidate_id=candidate_score.candidate_id,
            decision=decision,
            confidence_score=confidence_score,
            reasoning=reasoning,
            risk_factors=risk_factors
        )
