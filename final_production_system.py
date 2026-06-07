# -------------------------------
# Unified Score Normalization
# -------------------------------
def normalize_score(value):
    try:
        value = float(value)
    except:
        return 0.0
    return max(0.0, min(value, 100.0))

# -------------------------------
# Consistency Smoothing
# -------------------------------
def smooth_scores(scores):
    values = [normalize_score(v) for v in scores.values()]
    if not values:
        return scores
    avg = sum(values) / len(values)
    smoothed = {}
    for k, v in scores.items():
        v = normalize_score(v)
        smoothed[k] = round((v * 0.7) + (avg * 0.3), 2)
    return smoothed

# -------------------------------
# Final Decision (Stable + Clear)
# -------------------------------
def final_decision(score):
    if score >= 80:
        return "Selected"
    elif score >= 60:
        return "Hold / Review"
    return "Rejected"

# -------------------------------
# Production Pipeline
# -------------------------------
def production_pipeline(candidate_id, scores):
    scores = smooth_scores(scores)
    if not scores:
        final_score = 0.0
    else:
        final_score = round(sum(scores.values()) / len(scores), 2)
    decision = final_decision(final_score)
    return {
        "candidate_id": candidate_id,
        "scores": scores,
        "final_score": final_score,
        "decision": decision,
        "status": "production_ready"
    }
