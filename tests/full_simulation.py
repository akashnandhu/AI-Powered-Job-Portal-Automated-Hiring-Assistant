import random
import os
import sys

# Ensure Python can find the 'scoring' module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from scoring.cross_round_engine import CrossRoundEngine
from scoring.decision_engine import DecisionEngine
from scoring.unified_candidate_score import UnifiedCandidateScore

def simulate_candidate():
    return {
        "ats_round": random.randint(60, 90),
        "screening_round": random.randint(60, 85),
        "hr_interview_round": random.randint(65, 90),
        "technical_interview_round": random.randint(60, 95),
        "machine_test_round": random.randint(60, 95)
    }

def run_full_simulation(n=50):
    print(f"--- Running Full Randomized AI Simulation for {n} Candidates ---")
    
    # Initialize the real Zecpath engines
    weights = {
        "ats_score": 0.15,
        "screening_score": 0.15,
        "hr_interview_score": 0.20,
        "technical_interview_score": 0.30,
        "machine_test_score": 0.20
    }
    cross_round_engine = CrossRoundEngine(role_weights=weights)
    decision_engine = DecisionEngine(selected_threshold=78.0, reject_threshold=60.0)
    
    results = []
    
    for i in range(n):
        scores = simulate_candidate()
        
        # Use real CrossRoundEngine to aggregate
        unified_score, breakdown = cross_round_engine.aggregate_and_normalize(scores)
        
        # Mocking integrity flags randomly (5% chance of RED, 10% chance of YELLOW)
        risk_roll = random.random()
        risk_tag = "RED" if risk_roll < 0.05 else "YELLOW" if risk_roll < 0.15 else "GREEN"
        
        # Build candidate object
        candidate_score = UnifiedCandidateScore(
            candidate_id=f"SIM-CAND-{i+1:03d}",
            role_evaluated_for="Simulated Role",
            final_hiring_fit_score=unified_score,
            readiness_band="Calculated",
            risk_tag=risk_tag,
            weight_system_used="Simulation Default",
            cross_round_breakdown=breakdown,
            integrity_insights=["Randomized simulation flags"] if risk_tag != "GREEN" else []
        )
        
        # Use real DecisionEngine
        decision_result = decision_engine.evaluate(candidate_score)
        
        results.append({
            "candidate_id": candidate_score.candidate_id,
            "unified_score": round(unified_score, 2),
            "risk_tag": risk_tag,
            "decision": decision_result.decision,
            "confidence": decision_result.confidence_score
        })
        
    return results

if __name__ == "__main__":
    simulation_results = run_full_simulation(50)
    
    # Analyze outcomes
    selected = sum(1 for r in simulation_results if r['decision'] == "Selected")
    rejected = sum(1 for r in simulation_results if r['decision'] == "Rejected")
    hold = sum(1 for r in simulation_results if r['decision'] == "Hold / Review")
    
    print("\n[+] Simulation Complete.")
    print(f"Total Selected: {selected}")
    print(f"Total Rejected: {rejected}")
    print(f"Total Hold / Review: {hold}")
    
    print("\nSample Results (First 5):")
    for r in simulation_results[:5]:
        print(f"  {r['candidate_id']} | Score: {r['unified_score']} | Risk: {r['risk_tag']} | Decision: {r['decision']} ({r['confidence']}%)")
