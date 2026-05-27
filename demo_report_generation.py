import os
from scoring.unified_candidate_score import UnifiedCandidateScore, RoundContribution
from scoring.decision_engine import DecisionEngine
from reports.comprehensive_report_generator import ComprehensiveReportGenerator

def main():
    print("--- Running Automated Hiring Report Generation Demo ---")
    
    # Initialize the Decision Engine & Report Generator
    engine = DecisionEngine(selected_threshold=75.0, reject_threshold=55.0)
    report_gen = ComprehensiveReportGenerator(output_dir="reports/candidates")
    
    # Scenario 1: Strong Candidate (Selected)
    candidate_1 = UnifiedCandidateScore(
        candidate_id="CAND-001",
        role_evaluated_for="Software Engineer",
        final_hiring_fit_score=88.5,
        readiness_band="Exceptional Fit (Fast-Track Offer)",
        risk_tag="GREEN",
        weight_system_used="Technical",
        cross_round_breakdown={
            "ats_round": RoundContribution(90.0, "10%", 9.0),
            "screening_round": RoundContribution(85.0, "20%", 17.0),
            "hr_interview_round": RoundContribution(88.0, "20%", 17.6),
            "technical_interview_round": RoundContribution(92.0, "50%", 46.0)
        },
        integrity_insights=[],
        technical_interview_integrated=True
    )
    
    # Scenario 2: Borderline Candidate with Integrity Issues (Hold / Review)
    candidate_2 = UnifiedCandidateScore(
        candidate_id="CAND-002",
        role_evaluated_for="Product Manager",
        final_hiring_fit_score=78.0,
        readiness_band="Strong Fit (Proceed to Offer)",
        risk_tag="YELLOW", 
        weight_system_used="Leadership",
        cross_round_breakdown={
            "ats_round": RoundContribution(80.0, "15%", 12.0),
            "screening_round": RoundContribution(75.0, "25%", 18.75),
            "hr_interview_round": RoundContribution(70.0, "60%", 42.0)
        },
        integrity_insights=["Inconsistent eye contact detected", "Vague answers regarding previous employment timeline"],
    )
    
    # Scenario 3: High Risk Candidate (Rejected)
    candidate_3 = UnifiedCandidateScore(
        candidate_id="CAND-003",
        role_evaluated_for="Data Analyst",
        final_hiring_fit_score=45.0, 
        readiness_band="HOLD (Integrity Check Failed; Manual Audit Required)",
        risk_tag="RED",
        weight_system_used="Technical",
        cross_round_breakdown={
            "ats_round": RoundContribution(60.0, "10%", 6.0),
            "screening_round": RoundContribution(40.0, "20%", 8.0),
            "hr_interview_round": RoundContribution(45.0, "70%", 31.5)
        },
        integrity_insights=["Multiple voices detected in background", "Tab switching out of assessment window 15 times"],
    )
    
    candidates = [candidate_1, candidate_2, candidate_3]
    
    for idx, candidate in enumerate(candidates, 1):
        print(f"\nEvaluating Candidate {idx} ({candidate.candidate_id})...")
        decision_result = engine.evaluate(candidate)
        
        # Generate full recruiter report
        md_file, json_file = report_gen.generate_report(candidate, decision_result)
        print(f"Generated Markdown Report: {md_file}")
        print(f"Generated JSON Report: {json_file}")
        
    print("\nSuccessfully processed all candidates and generated comprehensive reports.")
        
if __name__ == "__main__":
    main()
