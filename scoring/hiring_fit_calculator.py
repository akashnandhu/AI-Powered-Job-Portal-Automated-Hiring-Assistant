from typing import Dict, Any, Tuple
from scoring.unified_candidate_score import UnifiedCandidateScore
from scoring.cross_round_engine import CrossRoundEngine
from scoring.risk_engine import RiskEngine
from scoring.weights_config import UNIFIED_WEIGHTS_CONFIG

class HiringFitCalculator:
    """
    Hiring Fit Calculator.
    Orchestrates the cross-round aggregation, enforces integrity capping rules, 
    evaluates readiness bands, and outputs the Unified Candidate Score Object.
    """
    def __init__(self):
        self.weights_config = UNIFIED_WEIGHTS_CONFIG
        self.risk_engine = RiskEngine()

    def get_role_weights(self, role_type: str) -> Tuple[Dict[str, float], str]:
        """Fetches the appropriate weight distribution and category name based on role type."""
        role_key = role_type.lower().strip()
        
        if "engineer" in role_key or "developer" in role_key or "data" in role_key or "technical" in role_key:
            return self.weights_config["technical"], "Technical"
        elif "manager" in role_key or "lead" in role_key or "director" in role_key or "head" in role_key:
            return self.weights_config["leadership"], "Leadership"
        elif "sales" in role_key or "support" in role_key or "customer" in role_key or "marketing" in role_key:
            return self.weights_config["customer_facing"], "Customer Facing"
        elif "intern" in role_key or "junior" in role_key or "entry" in role_key or "trainee" in role_key:
            return self.weights_config["entry_level"], "Entry Level"
            
        return self.weights_config.get(role_key, self.weights_config["default"]), "Default"

    def determine_readiness_band(self, unified_score: float) -> str:
        """Determines the operational band for hiring automation."""
        if unified_score >= 85:
            return "Exceptional Fit (Fast-Track Offer)"
        elif unified_score >= 70:
            return "Strong Fit (Proceed to Offer)"
        elif unified_score >= 55:
            return "Borderline Fit (Needs Team Review)"
        return "Poor Fit (Reject)"

    def calculate_hiring_fit(
        self, 
        candidate_id: str, 
        role_type: str, 
        ats_score: float, 
        screening_score: float, 
        hr_interview_score: float,
        technical_interview_score: float = None,
        machine_test_score: float = None,
        integrity_report: Dict[str, Any] = None
    ) -> UnifiedCandidateScore:
        """
        Executes the full unified pipeline logic to generate a final hiring fit score.
        """
        # 1. Apply Risk Engine Integrity Integration (Hold blocks and cheating caps)
        if integrity_report:
            risk_payload = self.risk_engine.evaluate_risk_integration(integrity_report, hr_interview_score)
            hr_interview_score = risk_payload["adjusted_hr_score"]
            is_hold = risk_payload["hold_automated_decision"]
            risk_tag = risk_payload["risk_tag"]
            insights = risk_payload.get("integrity_insights", [])
        else:
            is_hold = False
            risk_tag = "GREEN"
            insights = []

        # 2. Get role-based weights mapping
        role_weights, weight_system_name = self.get_role_weights(role_type)
        
        # 3. Consolidate available valid scores to run through Cross-Round Engine
        available_scores = {}
        if ats_score is not None:
            available_scores["ats_round"] = ats_score
        if screening_score is not None:
            available_scores["screening_round"] = screening_score
        if hr_interview_score is not None:
            available_scores["hr_interview_round"] = hr_interview_score
        if technical_interview_score is not None:
            available_scores["technical_interview_round"] = technical_interview_score
        if machine_test_score is not None:
            available_scores["machine_test_round"] = machine_test_score

        # 4. Invoke the Cross-Round Aggregation Engine
        engine = CrossRoundEngine(role_weights)
        unified_score, cross_round_breakdown = engine.aggregate_and_normalize(available_scores)
        
        # 5. Calculate readiness band
        band = self.determine_readiness_band(unified_score)
        
        # 6. Apply hard limits if the user cheated
        if is_hold:
            unified_score, band = self.risk_engine.apply_unified_score_cap(unified_score, is_hold)

        # 7. Construct and return the Unified Candidate Score Object
        return UnifiedCandidateScore(
            candidate_id=candidate_id,
            role_evaluated_for=role_type,
            final_hiring_fit_score=unified_score,
            readiness_band=band,
            risk_tag=risk_tag,
            weight_system_used=weight_system_name,
            cross_round_breakdown=cross_round_breakdown,
            integrity_insights=insights,
            machine_test_integrated=(machine_test_score is not None),
            technical_interview_integrated=(technical_interview_score is not None)
        )
