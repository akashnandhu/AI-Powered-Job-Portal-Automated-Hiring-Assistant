import re
from typing import Dict, List, Any

# Normalization Mappings
DEGREE_MAPPING = {
    "b.tech": "Bachelor of Technology",
    "btech": "Bachelor of Technology",
    "b.e": "Bachelor of Engineering",
    "b.e.": "Bachelor of Engineering",
    "bsc": "Bachelor of Science",
    "b.sc": "Bachelor of Science",
    "bachelor": "Bachelor",
    "m.pharm": "Master of Pharmacy",
    "mpharm": "Master of Pharmacy",
    "m.tech": "Master of Technology",
    "mtech": "Master of Technology",
    "msc": "Master of Science",
    "m.sc": "Master of Science",
    "master": "Master",
    "phd": "Doctor of Philosophy",
    "ph.d": "Doctor of Philosophy",
    "doctorate": "Doctor of Philosophy"
}

CERTIFICATION_MAPPING = {
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "aws": "Amazon Web Services",
    "gcp": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "data science": "Data Science"
}

CERT_CATEGORIES = {
    "AI/ML": ["machine learning", "artificial intelligence", "ml", "ai", "deep learning", "dl", "nlp", "natural language processing", "computer vision"],
    "Data Science": ["data science", "data analytics", "data mining", "pandas", "numpy", "scikit-learn", "statistics", "tableau", "power bi"],
    "Bioinformatics": ["bioinformatics", "computational biology", "genomics", "cheminformatics", "pharmacogenomics"],
    "Cloud": ["aws", "amazon web services", "gcp", "google cloud", "azure", "cloud computing", "docker", "kubernetes"]
}


def normalize_degree(degree_raw: str) -> str:
    """Normalize degree names based on predefined mappings."""
    if not degree_raw:
        return ""
    degree_lower = degree_raw.lower().strip()
    # Check if exact match exists
    if degree_lower in DEGREE_MAPPING:
        return DEGREE_MAPPING[degree_lower]
    # Check if mapping key is a substring
    for key, value in DEGREE_MAPPING.items():
        if key in degree_lower.split() or key.replace(".", "") in degree_lower.replace(".", "").split():
            return value
    return degree_raw.title()


def normalize_certification(cert_raw: str) -> str:
    """Normalize certification names based on predefined mappings."""
    if not cert_raw:
        return ""
    
    cert_lower = cert_raw.lower().strip()
    words = cert_lower.split()
    normalized_words = [CERTIFICATION_MAPPING.get(w, w) for w in words]
    return " ".join(normalized_words).title()


def categorize_certification(cert_name: str) -> str:
    """Assign a category to a certification based on keywords."""
    cert_lower = cert_name.lower()
    for category, keywords in CERT_CATEGORIES.items():
        if any(kw in cert_lower for kw in keywords):
            return category
    return "Others"


def _extract_year(text: str) -> str:
    """Extract a 4-digit year from text."""
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    if years:
        return sorted(years)[-1]  # Return the latest year if multiple
    return ""


def parse_education_section(text: str) -> List[Dict[str, str]]:
    """
    Extract education elements (degree, field, institution, year) from text.
    Relies on basic keyword and regex matching.
    """
    education_entries = []
    
    # Common degree patterns
    degree_pattern = re.compile(
        r'(?i)\b(B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|B\.?Sc|M\.?Sc|B\.?A\.?|M\.?A\.?|Ph\.?D|Bachelor.*?|Master.*?|Doctorate|M\.?Pharm|B\.?Pharm)\b[\s]*([^,\n]*)(?:,|\n| at)?'
    )
    
    # Simple split by newlines for context
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        degree_match = degree_pattern.search(line)
        if degree_match:
            raw_degree = degree_match.group(1).strip()
            # Try to grab the trailing text on the same line or next line for more info
            context = line + " " + (lines[i+1] if i + 1 < len(lines) else "")
            
            # Identify field of study (heuristics)
            field = ""
            field_match = re.search(r'(?i)(?:in|of)\s+([a-zA-Z\s]+?)(?=\s+(?:University|College|Institute|School|Academy|$|\||,|-))', context)
            if field_match:
                field = field_match.group(1).strip()
            
            # If no 'in [Field]', try right after degree
            if not field and degree_match.group(2):
                possible_field = degree_match.group(2).strip()
                if "in " in possible_field.lower():
                    field = possible_field.lower().split("in ")[1].split('|')[0].strip().title()
                elif len(possible_field) > 2:
                    field = possible_field.split('|')[0].strip().title()

            # Clean field
            field = re.sub(r'[^a-zA-Z\s]', '', field).strip()

            # Identify year
            year = _extract_year(context)
            
            # Identify institution (heuristics)
            institution = ""
            inst_match = re.search(r'(?i)([a-zA-Z\s]+(?:University|College|Institute|School|Academy)[a-zA-Z\s]*)', context)
            if inst_match:
                institution = inst_match.group(1).strip()
            
            education_entries.append({
                "degree": raw_degree,
                "normalized_degree": normalize_degree(raw_degree),
                "field": field,
                "institution": institution,
                "graduation_year": year
            })
            
    return education_entries


def parse_certifications_section(text: str) -> List[Dict[str, str]]:
    """
    Extract certification elements from text.
    Assumes each independent relevant line might be a certification.
    """
    cert_entries = []
    
    # Common issuer patterns
    issuers = ["AWS", "Google", "Coursera", "Udemy", "edX", "Microsoft", "IBM", "DeepLearning.AI", "Stanford", "Cisco", "Oracle"]
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
            
        # Ignore common non-cert headings
        if line.lower() in ["certifications", "certificates", "courses"]:
            continue
            
        # Extract year if present
        year = _extract_year(line)
        
        # Infer issuer
        issuer = ""
        for iss in issuers:
            if iss.lower() in line.lower():
                issuer = iss
                break
                
        # Clean line to represent cert name (heuristics)
        # remove year and common separator
        clean_name = line
        if year:
            clean_name = clean_name.replace(year, "")
        if issuer:
            # We don't necessarily remove issuer as it might be part of the title, e.g., "AWS Certified..."
            pass
            
        # Remove extra punctuation
        clean_name = re.sub(r'[~\-\|,]s*', ' ', clean_name).strip()
        clean_name = re.sub(r'\s+', ' ', clean_name)
        
        normalized_name = normalize_certification(clean_name)
        category = categorize_certification(normalized_name)
        
        if normalized_name:
            cert_entries.append({
                "name": clean_name,
                "issuer": issuer,
                "year": year,
                "category": category
            })
            
    return cert_entries


def parse_education_and_certifications(resume_text: str) -> Dict[str, Any]:
    """
    Main function to extract education and certifications from full resume text.
    It expects full text or pre-segmented text focusing on these sections.
    """
    
    # Ideally, the text should be sectioned before calling this.
    # If not, we attempt to find sections here using simple headers.
    
    edu_text = ""
    cert_text = ""
    
    current_section = None
    for line in resume_text.split('\n'):
        header_check = line.strip().lower()
        if re.match(r'^(education|academic background|academics)', header_check):
            current_section = "education"
            continue
        elif re.match(r'^(certifications|certificates|courses|licenses)', header_check):
            current_section = "certifications"
            continue
        elif re.match(r'^(experience|work history|skills|projects|summary|objective)', header_check):
            current_section = "other"
            
        if current_section == "education":
            edu_text += line + "\n"
        elif current_section == "certifications":
            cert_text += line + "\n"
            
    # Fallback to full text if headers act weird and both are empty
    if not edu_text and not cert_text:
        edu_text = resume_text
        cert_text = resume_text

    education = parse_education_section(edu_text)
    certifications = parse_certifications_section(cert_text)
    
    return {
        "education": education,
        "certifications": certifications
    }
