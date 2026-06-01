THRESHOLDS = {
    "priority": 85,
    "shortlist": 70,
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
