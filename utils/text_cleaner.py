import re

# Compile regex patterns for performance optimization
HEADERS_MAP = [
    (re.compile(r'(\b(?:SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|TECHNICAL COMPETENCIES)\b)', re.IGNORECASE), '\n### SKILLS\n'),
    (re.compile(r'(\b(?:EDUCATION|ACADEMIC BACKGROUND|SCHOLASTIC RECORD)\b)', re.IGNORECASE), '\n### EDUCATION\n'),
    (re.compile(r'(\b(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY)\b)', re.IGNORECASE), '\n### EXPERIENCE\n'),
    (re.compile(r'(\b(?:PROJECTS|ACADEMIC PROJECTS|PERSONAL PROJECTS)\b)', re.IGNORECASE), '\n### PROJECTS\n'),
    (re.compile(r'(\b(?:CERTIFICATIONS|CREDENTIALS|AWARDS)\b)', re.IGNORECASE), '\n### CERTIFICATIONS\n'),
    (re.compile(r'(\b(?:SUMMARY|PROFILE|OBJECTIVE)\b)', re.IGNORECASE), '\n### SUMMARY\n'),
    (re.compile(r'(\b(?:CONTACT|PERSONAL INFO|CONTACT INFORMATION)\b)', re.IGNORECASE), '\n### PERSONAL INFO\n'),
]

RE_SPACES = re.compile(r'[ \t]+')
RE_BULLET_START = re.compile(r'(?m)^[\s\u2022\u00B7\u25CF\-\*\+]\s+')
RE_BULLET_INLINE = re.compile(r'[\u2022\u00B7\u25CF]\s*')
RE_NEWLINES = re.compile(r'\n{3,}')
RE_NOISY_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\u200b]') # Control chars, zero-width spaces

def clean_text(text):
    """
    Cleans raw text extracted from resumes.
    - Normalizes whitespace
    - Removes excessive noise and symbols
    - Standardizes headings
    """
    if not text:
        return ""
        
    # 0. Remove noisy invisible/control characters
    text = RE_NOISY_CHARS.sub('', text)

    # 1. Standardize headers
    for pattern, replacement in HEADERS_MAP:
        text = pattern.sub(replacement, text)

    # 2. Normalize whitespace (ensure single spaces between words)
    text = RE_SPACES.sub(' ', text)

    # 3. Handle list markers (bullet points)
    text = RE_BULLET_START.sub('- ', text)
    text = RE_BULLET_INLINE.sub('- ', text)

    # 4. Remove excessive newlines (keep max 2 for section spacing)
    text = RE_NEWLINES.sub('\n\n', text)

    return text.strip()
