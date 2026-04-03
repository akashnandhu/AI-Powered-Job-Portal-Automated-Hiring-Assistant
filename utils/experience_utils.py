import re
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

def parse_date(date_str):
    """
    Parses a date string into a datetime object.
    Handles 'Present', 'Current', 'Now' as current datetime.
    """
    if not date_str:
        return None
        
    date_str = str(date_str).strip().lower()
    if date_str in ["present", "current", "now", "till date", "to date"]:
        return datetime.now()
    
    try:
        # Default to the first day of the month/year if not specified
        return parser.parse(date_str, default=datetime(2000, 1, 1))
    except Exception:
        return None

def calculate_duration_months(start_date, end_date):
    """Calculates duration between two datetime objects in months."""
    if not start_date or not end_date:
        return 0
    delta = relativedelta(end_date, start_date)
    return max(0, delta.years * 12 + delta.months)

def clean_company_name(text):
    """Normalizes company names for comparison."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\b(inc|llc|corp|corporation|ltd|limited|co|company)\b\.?', '', text)
    text = re.sub(r'[^a-z0-9]', '', text)
    return text.strip()

def clean_job_title(text):
    """Normalizes job titles for comparison."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return ' '.join(text.split())
