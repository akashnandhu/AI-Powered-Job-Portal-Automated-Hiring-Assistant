import re

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_experience(exp):
    try:
        if isinstance(exp, str):
            # Extract number if possible
            match = re.search(r'\d+(\.\d+)?', exp)
            if match:
                return float(match.group())
        return float(exp)
    except (ValueError, TypeError):
        return 0.0

def standardize_resume(resume_data):
    return {
        "skills": resume_data.get("skills", []),
        "experience_years": normalize_experience(resume_data.get("experience_years", resume_data.get("experience", 0))),
        "education": resume_data.get("education", ""),
        "projects": resume_data.get("projects", []),
        "certifications": resume_data.get("certifications", [])
    }

def mask_sensitive_info(text):
    if not isinstance(text, str):
        return text
    
    # Generic simple rule-based masking (Bias Reduction)
    # Mask common gender terms
    text = re.sub(r'\b(he|him|his|she|her|hers|male|female|man|woman|boy|girl)\b', '[GENDER]', text, flags=re.IGNORECASE)
    
    # Mask common demographic bias terms (age, race, religion, marital status, nationality)
    text = re.sub(r'\b(age|race|religion|married|single|divorced|ethnicity|nationality|dob|date of birth|white|black|asian|hispanic)\b', '[DEMOGRAPHIC]', text, flags=re.IGNORECASE)
    
    # Mask locations (We'll assume basic things like city names or country if we could, 
    # but for simplicity we will mask common location prefixes/keywords for illustration)
    text = re.sub(r'\b(?:in|at|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', r' \g<0> [LOCATION]', text) # placeholder logic

    # We will assume names are handled by removing standard name fields, 
    # but let's do a basic regex looking for email patterns to mask those too:
    text = re.sub(r'\S+@\S+', '[CONTACT]', text)
    
    return text
