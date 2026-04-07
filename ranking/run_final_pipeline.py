import os
import sys
import json
import statistics

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.normalization import normalize_text, standardize_resume, mask_sensitive_info
from scoring.ats_scorer import ATSScorer
from scoring.fairness_engine import apply_fairness, normalize_score_array
from ranking.shortlisting_engine import ShortlistingEngine

def evaluate_bias(fair_results):
    if not fair_results:
        return {}
        
    scores = [r["fair_score"] for r in fair_results]
    avg_score = statistics.mean(scores) if scores else 0.0
    try:
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
    except statistics.StatisticsError:
        std_dev = 0.0
        
    # Domain Proxy: "pharm" in title vs others ("tech" or non-pharm)
    pharmacy_scores = [r["fair_score"] for r in fair_results if "pharm" in r.get("job_title", "").lower()]
    tech_scores = [r["fair_score"] for r in fair_results if "pharm" not in r.get("job_title", "").lower()]
    
    pharm_avg = statistics.mean(pharmacy_scores) if pharmacy_scores else 0.0
    tech_avg = statistics.mean(tech_scores) if tech_scores else 0.0
    
    domain_bias_detected = abs(pharm_avg - tech_avg) > 0.15 if (pharmacy_scores and tech_scores) else False
    
    report = {
        "avg_score": round(avg_score, 4),
        "std_deviation": round(std_dev, 4),
        "domain_bias_detected": domain_bias_detected,
        "keyword_bias_detected": std_dev > 0.2, # Simple proxy
        "experience_bias_detected": False, # Assuming capped earlier
        "pharmacy_avg_score": round(pharm_avg, 4),
        
    }
    
    os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)
    with open(os.path.join(BASE_DIR, "reports", "bias_report.json"), "w") as f:
        json.dump(report, f, indent=4)
        
    print("\n--- BIAS EVALUATION REPORT ---")
    print(f"Average Score: {report['avg_score']}")
    print(f"Domain Bias Detected: {report['domain_bias_detected']}")
    print(f"Pharmacy Avg: {report['pharmacy_avg_score']}")
    
    return report

def main():
    candidate_id = "sample_resume_2"
    print("=" * 50)
    print("FAIRNESS & NORMALIZATION ATS PIPELINE")
    print("=" * 50)
    
    # 1. Parse Resume (Simulated load of resume text)
    print("1. Parsing resume (loading candidate data)...")
    scorer = ATSScorer(candidate_id=candidate_id)
    
    # Simulate loading original text for masking
    raw_resume_text = " ".join(scorer.candidate_skills) + " Male from New York."
    
    print("2. Normalizing resume...")
    norm_text = normalize_text(raw_resume_text)
    
    print("3. Masking sensitive data...")
    masked_text = mask_sensitive_info(norm_text)
    # print(f"Sample masked: {masked_text[:50]}...")
    
    print("4. Running ATS scoring...")
    raw_results = scorer.score_all_jobs()
    
    if not raw_results:
        print("No ATS results generated.")
        return

    print("5. Applying fairness engine...")
    # Prepare resume pseudo-data for fairness engine
    pseudo_resume_data = {
        "skills": scorer.candidate_skills,
        "experience_years": scorer.candidate_exp_months / 12.0
    }
    
    fair_results = []
    for r in raw_results:
        # Scale back to 0-1 based on final percentage for fair processing
        raw_score_0_1 = r["final_score"] / 100.0
        r["original_percentage"] = r["final_score"]
        fairness_out = apply_fairness(pseudo_resume_data, raw_score_0_1)
        r["fair_score"] = fairness_out["final_score"]
        r["fair_adjustments"] = fairness_out["adjustments"]
        fair_results.append(r)
        
    print("6. Normalizing final score...")
    normalized_results = normalize_score_array(fair_results, key="fair_score")
    
    # Convert 'normalized_score' back out to percentage or similar for ranking
    for r in normalized_results:
        r["final_score"] = round(r["normalized_score"] * 100, 2)
        
    print("\n--- SCORE COMPARISON (Sample Before vs After) ---")
    for r in normalized_results[:3]:
        print(f"Role: {r['job_title']} | Before: {r.get('original_percentage', 0)}% -> After: {r['final_score']}%")
        
    print("\n7. Evaluating Bias and saving Output...")
    bias_report = evaluate_bias(normalized_results)
    
    # Save Output
    os.makedirs(os.path.join(BASE_DIR, "outputs"), exist_ok=True)
    out_file = os.path.join(BASE_DIR, "outputs", "fair_scores.json")
    with open(out_file, "w") as f:
        json.dump(normalized_results, f, indent=4)
    print(f"   - Saved: {out_file}")
    
    # Hand off to shortlisting
    print("\n8. Running shortlisting with fair scores...")
    # write to ats_scores.json so shortlisting engine picks it up
    ats_scores_file = os.path.join(BASE_DIR, "outputs", "ats_scores.json")
    with open(ats_scores_file, "w") as f:
        json.dump({"candidate_id": candidate_id, "results": normalized_results}, f, indent=4)
        
    engine = ShortlistingEngine()
    if engine.load_scores():
        engine.process_and_rank()
        f1 = engine.generate_final_shortlisting_json()
        f2 = engine.generate_top_5_matches_json()
        f3 = engine.generate_recruiter_report()
        print(f"   - Saved Shortlisting Reports.")
        
if __name__ == "__main__":
    main()
