import re

def clean_text(text):
    """
    Cleans raw text extracted from resumes.
    - Normalizes whitespace
    - Removes excessive noise and symbols
    - Standardizes headings
    """
    if not text:
        return ""

    # 1. Standardize headers. 
    # Try to identify lines that are likely section headers (all caps or camel case in short lines)
    headers = {
        r'(\b(?:SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|TECHNICAL COMPETENCIES)\b)': '\n### SKILLS\n',
        r'(\b(?:EDUCATION|ACADEMIC BACKGROUND|SCHOLASTIC RECORD)\b)': '\n### EDUCATION\n',
        r'(\b(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY)\b)': '\n### EXPERIENCE\n',
        r'(\b(?:PROJECTS|ACADEMIC PROJECTS|PERSONAL PROJECTS)\b)': '\n### PROJECTS\n',
        r'(\b(?:CERTIFICATIONS|CREDENTIALS|AWARDS)\b)': '\n### CERTIFICATIONS\n',
        r'(\b(?:SUMMARY|PROFILE|OBJECTIVE)\b)': '\n### SUMMARY\n',
        r'(\b(?:CONTACT|PERSONAL INFO|CONTACT INFORMATION)\b)': '\n### PERSONAL INFO\n',
    }

    # Use regex to replace headers with standardized markdown ones. 
    # Use flags to catch different case styles
    for pattern, replacement in headers.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 2. Normalize whitespace (ensure single spaces between words)
    text = re.sub(r'[ \t]+', ' ', text)

    # 3. Handle list markers (bullet points)
    # Convert various bullet point styles (e.g., •, ·, ●, -, *, +) to standard "- "
    # Note: Only at start of line (or after newline/space)
    text = re.sub(r'(?m)^[\s\u2022\u00B7\u25CF\-\*\+]\s+', '- ', text)
    text = re.sub(r'[\u2022\u00B7\u25CF]\s*', '- ', text)

    # 4. Remove excessive newlines (keep max 2 for section spacing)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 5. Clean up weird characters (mostly non-printable or symbols)
    # text = "".join(ch for ch in text if ch.isprintable() or ch in "\n\r\t")

    return text.strip()
