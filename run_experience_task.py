import os
import sys
import json
from datetime import datetime

# Add base directory to path so we can import internal modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from config import CANDIDATE_ID
from utils.text_cleaner import clean_text
from parsers.pdf_parser import parse_pdf
from section_classifier import ResumeSectionClassifier
from parsers.experience_parser import ExperienceParser
from scoring.experience_scorer import ExperienceScorer

def run_experience_analysis_task(target_job_title="Clinical Pharmacist"):
    print(f"--- Experience Analysis Task for Candidate: {CANDIDATE_ID} ---")
    
    # 1. Extraction & Cleaning
    resume_path = os.path.join(BASE_DIR, "data", "resumes", f"{CANDIDATE_ID}.pdf")
    if not os.path.exists(resume_path):
        print(f"Error: Resume not found at {resume_path}")
        return

    print(f"[1/5] Extracting & Cleaning text from {CANDIDATE_ID}.pdf...")
    raw_text = parse_pdf(resume_path)
    if not raw_text:
        print("Failed to extract text.")
        return
        
    cleaned_text = clean_text(raw_text)

    # 2. Section Classification
    print("[2/5] Identifying Experience Section...")
    classifier = ResumeSectionClassifier()
    sections = classifier.classify_sections(cleaned_text)
    exp_text = sections.get("work_experience", {}).get("content", "")
    
    if not exp_text:
        print("Warning: Could not isolate Experience Section. Analyzing entire text...")
        exp_text = raw_text

    # 3. Parsing Roles (Experience Parser)
    print("[3/5] Parsing individual roles, companies, and durations...")
    parser = ExperienceParser()
    extracted_exps = parser.parse(exp_text)
    
    if not extracted_exps:
        print("No structured experience entries found.")
        return

    # 4. Experience Scoring & Relevance (Scoring Module)
    # Includes: Total experience, Gaps, Overlaps, Role Similarity, and Relevance to JD
    print(f"[4/5] Computing timeline metrics and relevance to '{target_job_title}'...")
    scorer = ExperienceScorer()
    # We'll assume a requirement of 2 years (24 months) for demonstration
    analysis_result = scorer.score_experience(
        experiences=extracted_exps, 
        target_role=target_job_title, 
        target_required_months=24
    )

    # 5. Output Results
    print("[5/5] Finalizing structured experience object...")
    
    output_path = os.path.join(BASE_DIR, "output", "experience_analysis_report.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(analysis_result, f, indent=4)

    # --- Display Summary in Terminal ---
    print("\n" + "="*60)
    print("EXPERIENCE ANALYSIS SUMMARY")
    print("="*60)
    
    timeline = analysis_result['timeline']
    print(f"- Total Calculated Experience: {timeline['total_calc_months']} months (~{timeline['total_calc_months']/12:.1f} years)")
    print(f"- Detected Gaps: {len(timeline['gaps'])} totalling {timeline['gaps_months']} months")
    print(f"- Overlapping Roles: {len(timeline['overlaps'])}")
    print(f"- Average Role Relevance to JD: {analysis_result['overall_relevance_score']*100}%")
    print(f"- Meets Requirement (2yrs): {'YES' if analysis_result['meets_experience_requirement'] else 'NO'}")
    
    print("\n--- Detected Roles ---")
    for exp in analysis_result['parsed_experiences']:
        print(f"  • {exp['job_title']} at {exp['company']} ({exp['duration_months']} mo)")

    if timeline['gaps']:
        print("\n--- Experience Gaps ---")
        for gap in timeline['gaps']:
            print(f"  • Gap from {gap['from']} to {gap['to']} ({gap['duration_months']} months)")

    print(f"\nReport saved to: output/experience_analysis_report.json")
    print("="*60)

if __name__ == "__main__":
    # You can pass a specific job title to analyze relevance
    job_to_check = "Clinical Research Scientist"
    run_experience_analysis_task(job_to_check)
