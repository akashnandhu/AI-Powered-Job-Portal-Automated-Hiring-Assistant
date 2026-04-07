def apply_fairness(resume_data, raw_score):
    adjustments = []
    final_score = raw_score
    
    skills = resume_data.get("skills", [])
    if isinstance(skills, list) and len(skills) > 30:
        penalty = 0.05
        final_score -= penalty
        adjustments.append(f"Penalty for potential keyword stuffing (-{penalty})")
        
    exp_years = resume_data.get("experience_years", 0)
    if exp_years > 15:
        adjustment = 0.05
        final_score -= adjustment
        adjustments.append(f"Capped experience advantage to ensure fairness (-{adjustment})")
    
    # Balance domain-specific scoring
    # A small normalizer, assuming domain specific might skew numbers
    final_score = max(0.0, min(1.0, final_score))
    
    return {
        "final_score": final_score,
        "adjustments": adjustments
    }

def normalize_score_array(scores_list, key="final_score"):
    if not scores_list:
        return []
        
    min_score = min(scores_list, key=lambda x: x.get(key, 0)).get(key, 0)
    max_score = max(scores_list, key=lambda x: x.get(key, 0)).get(key, 0)
    
    for item in scores_list:
        score = item.get(key, 0)
        if max_score > min_score:
            item["normalized_score"] = (score - min_score) / (max_score - min_score)
        else:
            item["normalized_score"] = 1.0 if max_score > 0 else 0.0
            
    return scores_list
