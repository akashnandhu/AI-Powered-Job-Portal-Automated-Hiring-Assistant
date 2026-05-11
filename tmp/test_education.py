import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.education_parser import parse_education_and_certifications
from scoring.education_scorer import calculate_education_score
from parsers.pdf_parser import parse_pdf
from utils.text_cleaner import clean_text

def run_education_pipeline():
    # 1. Load sample_resume_2.pdf
    resume_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "resumes", "sample_resume_2.pdf")
    raw_text = parse_pdf(resume_path)
    sample_resume = clean_text(raw_text)
    
    # 2. Parse Education and Certifications
    parsed_data = parse_education_and_certifications(sample_resume)
    
    # 3. Sample JD Education Requirement
    jd_req = {
        "degree": "Master",
        "field": "Pharmaceutical Sciences"
    }
    
    # 4. Score Education
    scoring_result = calculate_education_score(parsed_data["education"], jd_req)
    
    # 5. Combine Output
    final_output = {
        "parsed_data": parsed_data,
        "scoring": scoring_result
    }
    
    # Save to output file
    os.makedirs('output', exist_ok=True)
    out_file = 'output/education_analysis.json'
    with open(out_file, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print(f"Education analysis saved to {out_file}")
    print(json.dumps(final_output, indent=2))

if __name__ == "__main__":
    run_education_pipeline()
