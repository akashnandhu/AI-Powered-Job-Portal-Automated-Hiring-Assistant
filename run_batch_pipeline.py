import os
import sys
import json
import importlib
import time
from utils.file_handler import get_resume_files
import config

from section_classifier import generate_labels
from scoring.unified_candidate_score import UnifiedCandidateScore
from scoring.cross_round_engine import CrossRoundEngine
from scoring.decision_engine import DecisionEngine
from reports.comprehensive_report_generator import ComprehensiveReportGenerator

def set_candidate_config(candidate_id):
    with open("config.py", "w") as f:
        f.write(f'import os\n\nCANDIDATE_ID = "{candidate_id}"\n')

def run_pipeline():
    resumes_dir = os.path.join("data", "resumes")
    processed_dir = os.path.join("data", "processed")
    labels_dir = os.path.join("data", "labels")
    
    if not os.path.exists(resumes_dir):
        print("No resumes found.")
        return

    resumes = [f for f in os.listdir(resumes_dir) if f.endswith(".pdf")]
    
    cross_engine = CrossRoundEngine(role_weights={
        "ats_score": 0.20,
        "screening_score": 0.20,
        "hr_interview_score": 0.25,
        "technical_interview_score": 0.35
    })
    decision_engine = DecisionEngine(selected_threshold=70.0, reject_threshold=60.0)
    report_gen = ComprehensiveReportGenerator(output_dir="reports/batch_pipeline")
    
    final_results = []
    combined_shortlisting = []
    
    for resume in resumes:
        candidate_id = resume.replace(".pdf", "")
        print(f"\n{'='*60}")
        print(f"PROCESSING CANDIDATE: {candidate_id}")
        print(f"{'='*60}")
        
        # 1. Update config
        set_candidate_config(candidate_id)
        
        # 2. Run Extraction (main.py equivalent)
        print("[1] Extracting text from PDF...")
        # running main logic directly
        from parsers.pdf_parser import parse_pdf
        from utils.text_cleaner import clean_text
        
        pdf_path = os.path.join(resumes_dir, resume)
        raw_text = parse_pdf(pdf_path)
        if not raw_text:
            print(f"Failed to parse {resume}")
            continue
            
        cleaned_text = clean_text(raw_text)
        os.makedirs(processed_dir, exist_ok=True)
        out_txt = os.path.join(processed_dir, f"{candidate_id}_cleaned.txt")
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
            
        # 3. Generate Labels
        print("[2] Generating Section Labels (Education, Skills, Experience)...")
        generate_labels(processed_dir, labels_dir)
        
        # 3.5 Extract Skills
        print("[2.5] Extracting Skills...")
        os.system(f"{sys.executable} test_skills.py")
        
        # 4. ATS Scoring
        print("[3] Running ATS Scoring against Job Descriptions...")
        os.system(f"{sys.executable} scoring/run_ats.py")
        
        # Load ATS Score
        ats_scores_path = os.path.join("outputs", "ats_scores.json")
        ats_score = 0
        best_role = "General Candidate"
        if os.path.exists(ats_scores_path):
            with open(ats_scores_path, "r") as f:
                ats_data = json.load(f)
                jobs = ats_data.get("results", [])
                if jobs:
                    best_role = jobs[0]["job_title"]
                    # scoring/run_ats.py outputs final_score out of 100
                    ats_score = jobs[0]["final_score"]
                    
        print(f"    -> Best Matched Role: {best_role}")
        print(f"    -> ATS Score: {ats_score:.2f}")
        
        # 5. Simulate AI Screening, HR, Technical Rounds based on ATS score to show flow
        # In a real scenario, this would call actual agent scripts.
        # We'll generate realistic scores based on the ATS score's strength.
        print("[4] Executing AI Screening & Interview Rounds...")
        mock_screening = min(ats_score + 5, 100) if ats_score > 60 else max(ats_score - 10, 0)
        mock_hr = min(ats_score + 8, 100) if ats_score > 60 else ats_score
        mock_tech = ats_score
        
        scores_dict = {
            "ats_round": ats_score,
            "screening_round": mock_screening,
            "hr_interview_round": mock_hr,
            "technical_interview_round": mock_tech
        }
        
        # 6. Aggregation and Decision
        print("[5] Calculating Final Unified Score...")
        unified_score, breakdown = cross_engine.aggregate_and_normalize(scores_dict)
        
        candidate_obj = UnifiedCandidateScore(
            candidate_id=candidate_id,
            role_evaluated_for=best_role,
            final_hiring_fit_score=unified_score,
            readiness_band="Calculated Dynamically",
            risk_tag="GREEN",
            weight_system_used="Standard Role",
            cross_round_breakdown=breakdown,
            integrity_insights=[],
            technical_interview_integrated=True
        )
        
        decision = decision_engine.evaluate(candidate_obj)
        print(f"    -> Final AI Decision: {decision.decision} (Confidence: {decision.confidence_score}%)")
        print(f"    -> Reason: {decision.reasoning[0] if decision.reasoning else 'No reason provided'}")
        
        # 8. Run Shortlisting Engine
        print("[7] Generating Shortlisting Engine Outputs...")
        os.system(f"{sys.executable} ranking/shortlisting_engine.py")
        
        # Read the generated final_shortlisting.json and append to combined array
        shortlisting_path = os.path.join("outputs", "final_shortlisting.json")
        if os.path.exists(shortlisting_path):
            with open(shortlisting_path, "r") as f:
                candidate_shortlisting = json.load(f)
                combined_shortlisting.append(candidate_shortlisting)
                
        # Rename outputs to preserve per-candidate files (except final_shortlisting)
        import shutil
        for file_name in ["ats_scores.json", "ranked_jobs.json", "top_5_matches.json", "final_report.txt"]:
            src = os.path.join("outputs", file_name)
            dst = os.path.join("outputs", f"{file_name.split('.')[0]}_{candidate_id}.{file_name.split('.')[1]}")
            if os.path.exists(src):
                shutil.copy(src, dst)
        
        final_results.append({
            "Candidate": candidate_id,
            "Role": best_role,
            "ATS Score": round(ats_score, 2),
            "Final Score": round(unified_score, 2),
            "Decision": decision.decision
        })
        
    # After the loop, save the combined shortlisting file
    combined_path = os.path.join("outputs", "combined_final_shortlisting.json")
    with open(combined_path, "w") as f:
        json.dump(combined_shortlisting, f, indent=4)
    print(f"\nSaved combined shortlisting data to: {combined_path}")
        time.sleep(1)

    print("\n==================================================")
    print("             BATCH PIPELINE SUMMARY               ")
    print("==================================================")
    for res in final_results:
        print(f"- {res['Candidate']} | Role: {res['Role']} | ATS: {res['ATS Score']} | Final: {res['Final Score']} | STATUS: {res['Decision']}")

if __name__ == "__main__":
    run_pipeline()
