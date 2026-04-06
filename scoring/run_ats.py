import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import CANDIDATE_ID
from scoring.ats_scorer import ATSScorer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

def main():
    print("=" * 50)
    print("Starting Comprehensive ATS Scoring Pipeline")
    print("=" * 50)
    
    # 1. Initialize the Scorer
    print(f"Loading candidate data and initialing scorer for {CANDIDATE_ID}...")
    try:
        scorer = ATSScorer(candidate_id=CANDIDATE_ID)
    except FileNotFoundError as e:
        print(e)
        return
    
    # 2. Run Batch Scoring for all 87 JDs
    print("Batch scoring all job descriptions...")
    results = scorer.score_all_jobs()
    
    if not results:
        print("No results generated. Check if JD files exist in output/jd_files/.")
        return

    # 3. Sort Results by final_score DESC
    ranked_results = sorted(results, key=lambda x: x["final_score"], reverse=True)
    
    # 4. Save to outputs/ats_scores.json
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    ats_scores_file = os.path.join(OUTPUTS_DIR, "ats_scores.json")
    ats_output = {
        "candidate_id": scorer.candidate_id,
        "results": ranked_results
    }
    with open(ats_scores_file, "w") as f:
        json.dump(ats_output, f, indent=4)
        
    print(f"Exported all scores to: {ats_scores_file}")

    # 5. Save top roles to outputs/ranked_jobs.json
    # Optionally combine with existing ranked_jobs logic, but we'll overwrite or update
    ranked_jobs_file = os.path.join(OUTPUTS_DIR, "ranked_jobs.json")
    with open(ranked_jobs_file, "w") as f:
        json.dump(ats_output, f, indent=4)  # Overwriting for simplicity per requirements
        
    print(f"Exported ranked list to: {ranked_jobs_file}")

    # 6. Print Top 5 roles
    print("\n" + "=" * 50)
    print(f"TOP 5 MATCHING ROLES FOR CANDIDATE")
    print("=" * 50)
    
    for i, res in enumerate(ranked_results[:5]):
        print(f"{i+1}. {res['job_title']} ({res['category']})")
        print(f"   Score: {res['final_score']}%")
        b = res['breakdown']
        print(f"   Breakdown: Skill: {b['skill']:.2f} | Exp: {b['experience']:.2f} | Edu: {b['education']:.2f} | Sem: {b['semantic']:.2f}")
        for insight in res['insights']:
            print(f"   - {insight}")
        print("-" * 50)

if __name__ == "__main__":
    main()
