import os
import json
import time

from scoring.unified_candidate_score import UnifiedCandidateScore
from scoring.cross_round_engine import CrossRoundEngine
from scoring.decision_engine import DecisionEngine
from reports.comprehensive_report_generator import ComprehensiveReportGenerator
from utils.logger import obs

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def run_realistic_demo():
    print("=========================================================")
    print("   ZECPATH AI E2E REALISTIC DEMO SIMULATION ")
    print("=========================================================")
    
    dataset_dir = os.path.join(os.path.dirname(__file__), "data", "e2e_demo_dataset")
    jd_data = load_json(os.path.join(dataset_dir, "job_description.json"))
    candidates = load_json(os.path.join(dataset_dir, "candidates.json"))
    
    print(f"\n[TARGET JOB]: {jd_data['job_title']} ({jd_data['department']})")
    print(f"Required Skills: {', '.join(jd_data['skills_required'])}")
    
    # Initialize Core Engines
    weights = {
        "ats_score": 0.15,
        "screening_score": 0.20,
        "hr_interview_score": 0.25,
        "technical_interview_score": 0.40
    }
    cross_round_engine = CrossRoundEngine(role_weights=weights)
    decision_engine = DecisionEngine(selected_threshold=75.0, reject_threshold=60.0)
    report_gen = ComprehensiveReportGenerator(output_dir="reports/realistic_demo")
    
    results_summary = []
    
    for c in candidates:
        candidate_start = time.time()
        print(f"\n[+] Analyzing Profile: {c['name']} [{c['id']}]")
        print(f"    - Resume Profile: {c['resume_summary']}")
        
        # Step A: Cross-Round Aggregation
        unified_score, breakdown = cross_round_engine.aggregate_and_normalize(c['scores'])
        print(f"    - Mathematical AI Score: {unified_score:.2f}%")
        
        # Simulated Feature Extraction (Transcripts)
        fraud = bool(c['integrity_flags'])
        if fraud:
            print(f"    - ⚠️ SYSTEM ALERTS: {len(c['integrity_flags'])} anomalies detected (Screening integrity degraded)")
            
        # Step B: Build Unified Component
        candidate_score = UnifiedCandidateScore(
            candidate_id=c['id'],
            role_evaluated_for=jd_data['job_title'],
            final_hiring_fit_score=unified_score,
            readiness_band="Calculated Dynamically",
            risk_tag=c['risk_tag'],
            weight_system_used="Senior Engineering Standard",
            cross_round_breakdown=breakdown,
            integrity_insights=c['integrity_flags'],
            technical_interview_integrated=True
        )
        
        # Step C: AI Decision Engine Overrides
        decision_result = decision_engine.evaluate(candidate_score)
        print(f"    - Final AI Ruling: {decision_result.decision}")
        print(f"    - Confidence   : {decision_result.confidence_score}%")
        for reason in decision_result.reasoning:
            print(f"      > {reason}")
            
        # Step D: Human Match Validation
        human = c['human_judgment']
        match = ("Hire" in human and "Selected" in decision_result.decision) or \
                ("Reject" in human and "Reject" in decision_result.decision) or \
                ("Hold" in human and "Hold" in decision_result.decision)
                
        # Observability Trace Output
        latency_ms = round((time.time() - candidate_start) * 1000, 2)
        obs.log_api_request(
            endpoint=f"/api/v1/demo/evaluate/{c['id']}",
            method="POST",
            response_time_ms=latency_ms,
            status_code=200
        )
        
        # Produce Final Markdown Artifact
        md_file, json_file = report_gen.generate_report(candidate_score, decision_result)
        
        results_summary.append({
            "name": c['name'],
            "ai_decision": decision_result.decision,
            "human": human,
            "latency": f"{latency_ms}ms"
        })
        time.sleep(1)
        
    print("\n=========================================================")
    print("   DEMONSTRATION RESULTS ")
    print("=========================================================")
    print(f"{'CANDIDATE':<20} | {'AI DECISION':<15} | {'HUMAN JUDGMENT':<20} | {'TEL LNCY'}")
    print("-" * 75)
    for res in results_summary:
        print(f"{res['name']:<20} | {res['ai_decision']:<15} | {res['human']:<20} | {res['latency']}")

if __name__ == "__main__":
    run_realistic_demo()
