THRESHOLDS = {
    "priority": 85,
    "shortlist": 75,
    "review": 50
}

def get_category(score):
    if score >= THRESHOLDS["priority"]:
        return "Priority Shortlisted"
    elif score >= THRESHOLDS["shortlist"]:
        return "Shortlisted"
    elif score >= THRESHOLDS["review"]:
        return "Review"
    else:
        return "Rejected"
