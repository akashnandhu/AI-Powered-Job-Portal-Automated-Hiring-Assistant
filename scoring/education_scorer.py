from typing import Dict, Any, List

def calculate_education_score(parsed_education: List[Dict[str, str]], jd_education: Dict[str, str]) -> Dict[str, Any]:
    """
    Score the extracted education against the job description requirements.
    
    Weights: 50% Degree, 50% Field
    
    Degree scoring:
    - PhD = 1.0
    - Master = 0.8
    - Bachelor = 0.6
    
    Field scoring:
    - Exact match = 1.0
    - Related = 0.7
    - Unrelated = 0.2
    
    Args:
        parsed_education (List[Dict[str, str]]): List of education entries from resume.
        jd_education (Dict[str, str]): Required education specs, e.g., 
                                       {"degree": "Master", "field": "Computer Science"}
                                       
    Returns:
        Dict: Scoring details including relevance score and reasoning.
    """
    
    if not parsed_education:
        return {
            "education_relevance_score": 0.0,
            "meets_requirement": False,
            "reason": "No education information found in the resume."
        }
        
    req_degree = (jd_education.get("degree") or "").lower()
    req_field = (jd_education.get("field") or "").lower()
    
    best_score = 0.0
    best_match_reason = ""
    meets_req = False
    
    # Weights
    DEGREE_WEIGHT = 0.5
    FIELD_WEIGHT = 0.5
    
    for edu in parsed_education:
        candidate_degree = edu.get("normalized_degree", "").lower()
        candidate_field = edu.get("field", "").lower()
        
        # Calculate Degree Score
        degree_score = 0.0
        if "phd" in candidate_degree or "doctor of philosophy" in candidate_degree:
            degree_score = 1.0
        elif "master" in candidate_degree:
            degree_score = 0.8
        elif "bachelor" in candidate_degree:
            degree_score = 0.6
            
        # Optional: scale relative to required degree
        if req_degree:
            if "phd" in req_degree and degree_score < 1.0:
                degree_score -= 0.3  # Penalty for not meeting minimum
            elif "master" in req_degree and degree_score < 0.8:
                degree_score -= 0.3
            # If candidate exceeds requirement (e.g., has PhD, needs Bachelor), score is high
            
        # Prevent negative score
        degree_score = max(0.0, degree_score)
        
        # Calculate Field Score
        field_score = 0.2  # Base/Unrelated
        if req_field:
            if req_field in candidate_field or candidate_field in req_field:
                field_score = 1.0  # Exact/Substring match
            else:
                # Identify related fields (simple heuristic)
                related_map = {
                    "computer science": ["it", "information technology", "software engineering", "computer engineering", "ai"],
                    "pharmaceutical sciences": ["pharmacy", "pharmacology", "biotech", "biology", "chemistry"]
                }
                
                related_fields = [f for key in related_map if key in req_field for f in related_map[key]]
                if any(rf in candidate_field for rf in related_fields):
                    field_score = 0.7
                elif not candidate_field: # No explicit field matched
                    field_score = 0.4
        else:
            # If no particular field required by JD, assume any field is okay
            field_score = 1.0
            
        total_score = (degree_score * DEGREE_WEIGHT) + (field_score * FIELD_WEIGHT)
        
        # Evaluate Best Score
        if total_score > best_score:
            best_score = total_score
            degree_str = candidate_degree.title() if candidate_degree else "Degree"
            field_str = f" in {candidate_field.title()}" if candidate_field else ""
            
            # Determine logic for meet requirement
            if (degree_score >= 0.6) and (field_score >= 0.7):
                meets_req = True
                best_match_reason = f"{degree_str}{field_str} matches job requirement."
            else:
                meets_req = False
                best_match_reason = f"Candidate has {degree_str}{field_str}, which partially matches or falls short of the '{req_degree.title()} in {req_field.title()}' requirement."

    # If it's still missing reason but we have evaluated
    if not best_match_reason:
        best_match_reason = "Education found but does not closely match the specific job requirements."
        
    return {
        "education_relevance_score": round(best_score, 2),
        "meets_requirement": meets_req,
        "reason": best_match_reason
    }
