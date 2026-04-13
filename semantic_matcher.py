import os
import sys
import json
import torch
from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from config import CANDIDATE_ID
from jd_parser import parse_jd_file

# Define score levels
def get_match_level(score):
    if score >= 0.75:
        return "Strong Match"
    elif score >= 0.5:
        return "Moderate Match"
    else:
        return "Weak Match"

def main():
    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 1. JD Parsing
    print("Parsing Job Descriptions...")
    jd_dir = os.path.join(BASE_DIR, "data", "jobs_data")
    all_jds = []
    
    if os.path.exists(jd_dir):
        for filename in os.listdir(jd_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(jd_dir, filename)
                try:
                    parsed_list = parse_jd_file(file_path)
                    if parsed_list:
                        for pj in parsed_list:
                            pj['job_id'] = filename.replace('.txt', '')
                            all_jds.append(pj)
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
    else:
        print(f"Directory {jd_dir} not found.")
        return

    if not all_jds:
        print("No JDs were loaded. Exiting.")
        return

    print(f"Loaded {len(all_jds)} Job Descriptions.")

    # 2. Resume Parsing
    resume_path = os.path.join(BASE_DIR, "data", "labels", f"{CANDIDATE_ID}.json")
    print(f"Loading resume from {resume_path}...")
    if not os.path.exists(resume_path):
        print(f"Resume {resume_path} not found.")
        return
        
    try:
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
    except Exception as e:
        print(f"Error reading resume file: {e}")
        return
        
    resume_sections = {
        "skills": resume_data.get("skills", ""),
        "experience": resume_data.get("work_experience", ""),
        "projects": resume_data.get("projects", ""),
        "education": resume_data.get("education", "")
    }

    # Precompute resume embeddings
    print("Encoding resume sections...")
    resume_embs = {}
    for section, text in resume_sections.items():
        if text:
            resume_embs[section] = model.encode(text, convert_to_tensor=True)
        else:
            resume_embs[section] = None

    # 3. Batch Encode JDs
    print("Encoding all JD sections in batch...")
    jd_overviews = [" ".join(jd.get("overview", [])) for jd in all_jds]
    jd_resps = [" ".join(jd.get("responsibilities", [])) for jd in all_jds]
    jd_quals = [" ".join(jd.get("qualifications", [])) for jd in all_jds]

    # Batch encode to save time
    emb_j_overviews = model.encode(jd_overviews, convert_to_tensor=True, show_progress_bar=True)
    emb_j_resps = model.encode(jd_resps, convert_to_tensor=True, show_progress_bar=True)
    emb_j_quals = model.encode(jd_quals, convert_to_tensor=True, show_progress_bar=True)

    ranked_jobs = []

    print("Scoring JDs against the Resume...")
    for i, jd in enumerate(all_jds):
        # Section-wise Similarity calculation using precomputed embeddings
        def get_sim(emb_r, emb_jd):
            if emb_r is None or emb_jd is None:
                return 0.0
            return max(0.0, min(1.0, util.cos_sim(emb_r, emb_jd).item()))

        score_skills = get_sim(resume_embs["skills"], emb_j_resps[i])
        score_exp = get_sim(resume_embs["experience"], emb_j_overviews[i])
        score_proj = get_sim(resume_embs["projects"], emb_j_resps[i])
        score_edu = get_sim(resume_embs["education"], emb_j_quals[i])
        
        # Weighted Scoring
        final_score = (
            (score_skills * 0.40) +
            (score_exp * 0.30) +
            (score_proj * 0.20) +
            (score_edu * 0.10)
        )
        
        ranked_jobs.append({
            "job_title": jd.get("title", ""),
            "job_id": jd.get("job_id", ""),
            "score": round(float(final_score), 4),
            "match_level": get_match_level(final_score),
            "section_scores": {
                "skills": round(float(score_skills), 4),
                "experience": round(float(score_exp), 4),
                "projects": round(float(score_proj), 4),
                "education": round(float(score_edu), 4)
            }
        })
        
    # Rank by score
    ranked_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    # 4. Save Outputs
    out_dir = os.path.join(BASE_DIR, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    ranked_path = os.path.join(out_dir, "ranked_jobs.json")
    with open(ranked_path, "w", encoding="utf-8") as f:
        json.dump(ranked_jobs, f, indent=4)
        
    scores_path = os.path.join(out_dir, "semantic_scores.json")
    sem_scores = {jd["job_id"]: jd["score"] for jd in ranked_jobs}
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(sem_scores, f, indent=4)
        
    print(f"\nMatching complete.")
    print(f"Results saved to: {ranked_path}")
    print(f"Scores saved to: {scores_path}")
    
    if ranked_jobs:
        top = ranked_jobs[0]
        print(f"\nTop Match: {top['job_title']} (ID: {top['job_id']})")
        print(f"Score: {top['score']} ({top['match_level']})")

if __name__ == "__main__":
    main()

