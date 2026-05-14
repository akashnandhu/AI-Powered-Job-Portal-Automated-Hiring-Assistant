import json
import logging
from typing import Dict, Any

from scoring.weights_config import UNIFIED_WEIGHTS_CONFIG

class UnifiedScorer:
    """
    Combines all previous rounds (ATS, Screening, HR Interview) into a unified hiring intelligence score.
    Applies role-based weight adjustments to calculate final hiring fit.
    """
    def __init__(self):
        self.weights = UNIFIED_WEIGHTS_CONFIG

    def get_role_weights(self, role_type: str) -> Dict[str, float]:
        """
        Fetches the appropriate weight distribution based on the role type.
        """
        role_key = role_type.lower().strip()
        
        # Simple keyword matching for roles
        if "engineer" in role_key or "developer" in role_key or "data" in role_key or "technical" in role_key:
            return self.weights["technical"]
        elif "manager" in role_key or "lead" in role_key or "director" in role_key or "head" in role_key:
            return self.weights["leadership"]
        elif "sales" in role_key or "support" in role_key or "customer" in role_key or "marketing" in role_key:
            return self.weights["customer_facing"]
        elif "intern" in role_key or "junior" in role_key or "entry" in role_key or "trainee" in role_key:
            return self.weights["entry_level"]
            
        return self.weights.get(role_key, self.weights["default"])

    def calculate_hiring_fit(
        self, 
        candidate_id: str, 
        role_type: str, 
        ats_score: float, 
        screening_score: float, 
        hr_interview_score: float
    ) -> Dict[str, Any]:
        """
        Calculates the unified hiring fit score.
        """
        # 1. Get role-based weights
        role_weights = self.get_role_weights(role_type)
        
        # 2. Apply weights
        ats_weighted = ats_score * role_weights["ats_score"]
        screening_weighted = screening_score * role_weights["screening_score"]
        hr_weighted = hr_interview_score * role_weights["hr_interview_score"]
        
        # 3. Calculate Final Unified Score (Hiring Fit Percentage)
        unified_score = ats_weighted + screening_weighted + hr_weighted
        
        # 4. Determine Readiness Band
        if unified_score >= 85:
            band = "Exceptional Fit (Fast-Track Offer)"
        elif unified_score >= 70:
            band = "Strong Fit (Proceed to Offer)"
        elif unified_score >= 55:
            band = "Borderline Fit (Needs Team Review)"
        else:
            band = "Poor Fit (Reject)"

        # 5. Build Unified Candidate Score Object
        unified_object = {
            "candidate_id": candidate_id,
            "role_evaluated_for": role_type,
            "final_hiring_fit_score": round(unified_score, 2),
            "readiness_band": band,
            "cross_round_breakdown": {
                "ats_round": {
                    "raw_score": round(ats_score, 2),
                    "weight_applied": f"{int(role_weights['ats_score'] * 100)}%",
                    "weighted_contribution": round(ats_weighted, 2)
                },
                "screening_round": {
                    "raw_score": round(screening_score, 2),
                    "weight_applied": f"{int(role_weights['screening_score'] * 100)}%",
                    "weighted_contribution": round(screening_weighted, 2)
                },
                "hr_interview_round": {
                    "raw_score": round(hr_interview_score, 2),
                    "weight_applied": f"{int(role_weights['hr_interview_score'] * 100)}%",
                    "weighted_contribution": round(hr_weighted, 2)
                }
            },
            "weight_system_used": "Technical" if role_weights == self.weights["technical"] else (
                "Leadership" if role_weights == self.weights["leadership"] else (
                    "Customer Facing" if role_weights == self.weights["customer_facing"] else (
                        "Entry Level" if role_weights == self.weights["entry_level"] else "Default"
                    )
                )
            )
        }
        
        return unified_object

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    scorer = UnifiedScorer()
    
    # Test 1: Senior Software Engineer (Technical Role)
    # Expected: High focus on ATS & Screening, lower on HR Interview
    eng_result = scorer.calculate_hiring_fit(
        candidate_id="Cand_001",
        role_type="Senior Python Engineer",
        ats_score=92.5,
        screening_score=88.0,
        hr_interview_score=75.0
    )
    
    # Test 2: Sales Director (Leadership/Customer Facing Role)
    # Expected: High focus on HR Interview
    sales_result = scorer.calculate_hiring_fit(
        candidate_id="Cand_002",
        role_type="Sales Director",
        ats_score=70.0,
        screening_score=75.0,
        hr_interview_score=95.0
    )
    
    print("--- Unified Hiring Fit Calculator Test ---")
    print(json.dumps(eng_result, indent=4))
    print("\n")
    print(json.dumps(sales_result, indent=4))
