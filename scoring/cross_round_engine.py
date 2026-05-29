import math
from typing import Dict, Any, Tuple
from scoring.unified_candidate_score import RoundContribution

class CrossRoundEngine:
    """
    Cross-Round Aggregation Engine.
    Dynamically normalizes and aggregates scores across ATS, Screening, HR, Technical, and Machine Tests.
    """
    def __init__(self, role_weights: Dict[str, float]):
        self.role_weights = role_weights

    def aggregate_and_normalize(self, available_scores: Dict[str, float]) -> Tuple[float, Dict[str, RoundContribution]]:
        """
        Calculates the sum of available base weights and normalizes them cleanly so they scale to 1.0 (100%).
        Returns the unified aggregated score and the cross-round breakdown dictionary.
        """
        # Map rounds to their specific weights in the configuration
        round_weight_map = {
            "ats_round": "ats_score",
            "screening_round": "screening_score",
            "technical_interview_round": "technical_interview_score",
            "machine_test_round": "machine_test_score",
            "hr_interview_round": "hr_interview_score"
        }
        
        # Determine total available weight sum based on what rounds the candidate actually completed
        sum_weights = sum(
            self.role_weights.get(round_weight_map[round_name], 0.0) 
            for round_name in available_scores.keys()
        )
        
        if sum_weights <= 0:
            sum_weights = 1.0  # Safe fallback to prevent division by zero
            
        unified_score = 0.0
        cross_round_breakdown = {}
        
        # Calculate dynamic normalized contributions
        for round_name, score in available_scores.items():
            base_weight = self.role_weights.get(round_weight_map[round_name], 0.0)
            normalized_weight = base_weight / sum_weights
            weighted_contribution = score * normalized_weight
            
            unified_score += weighted_contribution
            
            cross_round_breakdown[round_name] = RoundContribution(
                raw_score=score,
                weight_applied=f"{int(normalized_weight * 100)}%",
                weighted_contribution=weighted_contribution
            )
            
        # Check variance across rounds to improve consistency
        if len(available_scores) > 1:
            scores = list(available_scores.values())
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            std_dev = math.sqrt(variance)
            
            # Apply inconsistency penalty for high variance
            if std_dev > 15.0:
                penalty = min(5.0, (std_dev - 15.0) * 0.2)
                unified_score -= penalty
                
        unified_score = max(0.0, min(100.0, unified_score))
            
        return unified_score, cross_round_breakdown
