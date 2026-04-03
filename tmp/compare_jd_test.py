import json
import os
import re
from parsers.experience_parser import ExperienceParser
from scoring.experience_scorer import ExperienceScorer

def extract_months_from_jd_exp(exp_str):
    if not exp_str or exp_str.lower() in ["not specified", "none", "n/a"]:
        return 0
    # Search for numbers followed by years or months
    year_match = re.search(r'(\d+)\s*(?:\+)?\s*(?:year|yrs|y)', exp_str, re.IGNORECASE)
    if year_match:
        return int(year_match.group(1)) * 12
        
    mo_match = re.search(r'(\d+)\s*(?:\+)?\s*(?:month|mo)', exp_str, re.IGNORECASE)
    if mo_match:
        return int(mo_match.group(1))
        
    return 0

def test_against_jd():
    # 1. Load the JD
    jd_path = "output/jd_files/ai_in_drug_discovery_researcher.json"
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_data = json.load(f)
        
    target_role = jd_data.get("job_title", "")
    target_exp_str = jd_data.get("experience_required", "")
    target_months = extract_months_from_jd_exp(target_exp_str)
    
    print(f"--- Loaded Job Description ---")
    print(f"Job Title: {target_role}")
    print(f"Required Exp string: '{target_exp_str}' -> {target_months} months")
    
    # 2. Sample Candidate Experience (Simulating a parsed resume)
    candidate_text = """
    Senior AI Researcher at Bioinformatics Ltd
    Jan 2019 - Present
    Developed deep learning models for molecular structure prediction. Let a team of 3 data scientists.
    
    Data Scientist at Healthcare Analytics Inc
    Jun 2016 - Dec 2018
    Applied machine learning to patient datasets.
    
    Research Intern, Generic Pharma Labs
    Jan 2015 - May 2016
    Assisted in computational modeling.
    """
    print("\n--- Parsing Candidate Experience ---")
    parser = ExperienceParser()
    experiences = parser.parse(candidate_text)
    
    # 3. Score against the JD
    print("\n--- Scoring Relevance to JD ---")
    scorer = ExperienceScorer()
    result = scorer.score_experience(
        experiences=experiences, 
        target_role=target_role, 
        target_required_months=target_months
    )
    
    # Save the output to a file so the user can see it!
    output_test_file = "output/experience_analysis.json"
    with open(output_test_file, "w", encoding="utf-8") as f:
        json.dump({
            "target_job": jd_data,
            "candidate_analysis": result
        }, f, indent=4)
        
    print(json.dumps(result, indent=2))
    print(f"\n[Success] Full comparison JSON saved to {output_test_file}")

if __name__ == '__main__':
    test_against_jd()
