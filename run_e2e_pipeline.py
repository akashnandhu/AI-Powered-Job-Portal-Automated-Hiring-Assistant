import os
import json
import time

from scoring.unified_candidate_score import UnifiedCandidateScore, RoundContribution
from scoring.cross_round_engine import CrossRoundEngine
from scoring.decision_engine import DecisionEngine
from reports.comprehensive_report_generator import ComprehensiveReportGenerator
from utils.logger import obs

def main():
    print("==================================================")
    print("   ZECPATH AI E2E PIPELINE VALIDATION TEST        ")
    print("==================================================")
    
    # 1. Initialize Pipeline Engines
    print("[1] Initializing Core Engines...")
    weights = {
        "ats_score": 0.15,
        "screening_score": 0.20,
        "hr_interview_score": 0.25,
        "technical_interview_score": 0.40
    }
    cross_round_engine = CrossRoundEngine(role_weights=weights)
    decision_engine = DecisionEngine(selected_threshold=78.0, reject_threshold=60.0)
    report_gen = ComprehensiveReportGenerator(output_dir="reports/e2e_validation")
    
    # 2. Define Mock Candidates (AI vs Human Judgment Comparison)
    candidates = [
        {
            "id": "E2E-001",
            "name": "Alice Developer",
            "role": "Backend Engineer",
            "human_judgment": "Strong Hire",
            "scores": {
                "ats_round": 92.0,
                "screening_round": 88.0,
                "hr_interview_round": 85.0,
                "technical_interview_round": 95.0
            },
            "integrity_flags": [],
            "risk_tag": "GREEN"
        },
        {
            "id": "E2E-002",
            "name": "Bob Scripter",
            "role": "Backend Engineer",
            "human_judgment": "Reject (Inconsistent/Cheating Suspected)",
            "scores": {
                "ats_round": 95.0,
                "screening_round": 55.0,  # Huge drop
                "hr_interview_round": 50.0,
                "technical_interview_round": 45.0
            },
            "integrity_flags": ["Tab switching detected in technical round"],
            "risk_tag": "RED"
        },
        {
            "id": "E2E-003",
            "name": "Charlie Communicator",
            "role": "Backend Engineer",
            "human_judgment": "Borderline / Hold",
            "scores": {
                "ats_round": 75.0,
                "screening_round": 80.0,
                "hr_interview_round": 88.0,
                "technical_interview_round": 65.0 # Low technical score
            },
            "integrity_flags": [],
            "risk_tag": "GREEN"
        }
    ]
    
    results_summary = []
    
    for c in candidates:
        candidate_start = time.time()
        print(f"\n[+] Processing Candidate: {c['name']} ({c['id']})")
        
        # Step A: Cross-Round Aggregation
        unified_score, breakdown = cross_round_engine.aggregate_and_normalize(c['scores'])
        print(f"    - Aggregated AI Score: {unified_score:.2f}")
        
        # Step B: Build Unified Object
        candidate_score = UnifiedCandidateScore(
            candidate_id=c['id'],
            role_evaluated_for=c['role'],
            final_hiring_fit_score=unified_score,
            readiness_band="Calculated Dynamically", # Just a placeholder
            risk_tag=c['risk_tag'],
            weight_system_used="Backend Standard",
            cross_round_breakdown=breakdown,
            integrity_insights=c['integrity_flags'],
            technical_interview_integrated=True
        )
        
        # Step C: AI Decision Making
        decision_result = decision_engine.evaluate(candidate_score)
        print(f"    - AI Final Decision: {decision_result.decision} (Confidence: {decision_result.confidence_score}%)")
        
        # Step D: Compare vs Human
        human_decision = c['human_judgment']
        match = False
        if "Hire" in human_decision and decision_result.decision == "Selected": match = True
        if "Reject" in human_decision and decision_result.decision == "Rejected": match = True
        if "Hold" in human_decision and decision_result.decision == "Hold / Review": match = True
        
        print(f"    - Human Judgment: {human_decision}")
        print(f"    - AI vs Human Alignment: {'MATCH' if match else 'MISMATCH'}")
        
        # Step E: Generate Final Report
        md_file, json_file = report_gen.generate_report(candidate_score, decision_result)
        
        results_summary.append({
            "candidate": c['id'],
            "unified_score": round(unified_score, 2),
            "ai_decision": decision_result.decision,
            "human_decision": human_decision,
            "alignment": match
        })
        
        # [AI Observability]: Track API Pipeline and End-to-End Latency
        latency_ms = round((time.time() - candidate_start) * 1000, 2)
        obs.log_api_request(
            endpoint=f"/api/v1/hiring/evaluate/{c['id']}",
            method="POST",
            response_time_ms=latency_ms,
            status_code=200
        )
        
        time.sleep(0.5)

    print("\n==================================================")
    print("   E2E PIPELINE VALIDATION COMPLETE               ")
    print("==================================================")
    
    print("\nValidation Summary:")
    for r in results_summary:
        print(f"{r['candidate']} | AI: {r['ai_decision']} | Human: {r['human_decision']} | Match: {r['alignment']}")
        
if __name__ == "__main__":
    main()
