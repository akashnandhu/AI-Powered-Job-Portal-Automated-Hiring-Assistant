import logging
from typing import Dict, Any

class RiskEngine:
    """
    Enforces integrity holds and scoring caps based on candidate risk profiles.
    Acts as the final safeguard before automated hiring decisions are made.
    """
    def __init__(self):
        self.logger = logging.getLogger("RiskEngine")
        # Define maximum allowed scores when a candidate is flagged as RED (High Risk)
        self.red_flag_hr_score_cap = 40.0
        self.red_flag_unified_score_cap = 45.0
        
    def evaluate_risk_integration(self, integrity_report: Dict[str, Any], hr_interview_score: float) -> Dict[str, Any]:
        """
        Takes the IntegrityScorer output and current HR score, applying caps if necessary.
        Returns the risk payload to be integrated into the UnifiedScorer.
        """
        risk_tag = integrity_report.get("risk_tag", "GREEN")
        adjusted_hr_score = hr_interview_score
        is_hold = False
        
        if risk_tag == "RED":
            # Cap HR Interview Score
            if hr_interview_score > self.red_flag_hr_score_cap:
                adjusted_hr_score = self.red_flag_hr_score_cap
                self.logger.warning(f"RED Risk Tag: HR Interview score capped at {self.red_flag_hr_score_cap}%.")
            is_hold = True
            
        elif risk_tag == "YELLOW":
            self.logger.info("YELLOW Risk Tag: Proceeding with caution. Manual audit recommended.")
            
        return {
            "risk_tag": risk_tag,
            "original_hr_score": hr_interview_score,
            "adjusted_hr_score": adjusted_hr_score,
            "hold_automated_decision": is_hold,
            "integrity_insights": integrity_report.get("insights", [])
        }
        
    def apply_unified_score_cap(self, unified_score: float, is_hold: bool) -> tuple[float, str]:
        """
        Applies a hard cap to the final unified hiring fit score if the candidate is on hold,
        and overrides the readiness band.
        """
        if is_hold:
            capped_score = min(unified_score, self.red_flag_unified_score_cap)
            band = "HOLD (Integrity Check Failed; Manual Audit Required)"
            self.logger.warning(f"Integrity Hold Active: Unified score capped at {capped_score}% with HOLD band.")
            return capped_score, band
            
        return unified_score, None
