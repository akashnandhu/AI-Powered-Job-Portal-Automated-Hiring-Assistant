import json
import logging
from typing import Dict, Any

from scoring.hiring_fit_calculator import HiringFitCalculator

class UnifiedScorer:
    """
    Unified Scorer Facade.
    Acts as a backward-compatible wrapper that delegates the calculation logic to the 
    HiringFitCalculator, CrossRoundEngine, and UnifiedCandidateScore deliverables.
    """
    def __init__(self):
        self.calculator = HiringFitCalculator()

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
    ) -> Dict[str, Any]:
        """
        Delegates to HiringFitCalculator and returns the UnifiedCandidateScore as a serialized dictionary.
        """
        score_object = self.calculator.calculate_hiring_fit(
            candidate_id=candidate_id,
            role_type=role_type,
            ats_score=ats_score,
            screening_score=screening_score,
            hr_interview_score=hr_interview_score,
            technical_interview_score=technical_interview_score,
            machine_test_score=machine_test_score,
            integrity_report=integrity_report
        )
        return score_object.to_dict()

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    scorer = UnifiedScorer()
    
    # Test 1: Senior Software Engineer (Technical Role with Machine Test)
    eng_result = scorer.calculate_hiring_fit(
        candidate_id="Cand_001",
        role_type="Senior Python Engineer",
        ats_score=92.5,
        screening_score=88.0,
        hr_interview_score=75.0,
        machine_test_score=89.5
    )
    
    # Test 2: Sales Director (Leadership Role without Machine Test)
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
