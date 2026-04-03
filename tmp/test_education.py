import json
from parsers.education_parser import parse_education_and_certifications
from scoring.education_scorer import calculate_education_score

def run_education_pipeline():
    # 1. Sample Resume Text
    sample_resume = """
    EDUCATION
    M.Pharm in Pharmaceutical Sciences
    University of Example | 2021
    
    B.Sc in Chemistry
    State College | 2019
    
    CERTIFICATIONS
    Machine Learning by Coursera 2022
    AWS Certified Solutions Architect 2023
    """
    
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
    import os
    os.makedirs('output', exist_ok=True)
    out_file = 'output/education_analysis.json'
    with open(out_file, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print(f"Education analysis saved to {out_file}")
    print(json.dumps(final_output, indent=2))

if __name__ == "__main__":
    run_education_pipeline()
