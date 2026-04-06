import os
import sys
import json
from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from config import CANDIDATE_ID

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
    print("Parsing JDs...")
    from jd_parser import parse_jd_file
    jd_dir = r"data/jobs_data"
    all_jds = []
    
    if os.path.exists(jd_dir):
        for filename in os.listdir(jd_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(jd_dir, filename)
                parsed_list = parse_jd_file(file_path)
                if parsed_list:
                    for pj in parsed_list:
                        pj['job_id'] = filename.replace('.txt', '')
                        all_jds.append(pj)
    else:
        print(f"Directory {jd_dir} not found.")
        return

    print(f"Loaded {len(all_jds)} JDs.")

    # 2. Resume Parsing
    resume_path = os.path.join("data", "labels", f"{CANDIDATE_ID}.json")
    print(f"Loading resume from {resume_path}...")
    if not os.path.exists(resume_path):
        print(f"Resume {resume_path} not found.")
        return
        
    with open(resume_path, "r", encoding="utf-8") as f:
        resume_data = json.load(f)
        
    resume_skills = resume_data.get("skills", "")
    resume_experience = resume_data.get("work_experience", "")
    resume_projects = resume_data.get("projects", "")
    resume_education = resume_data.get("education", "")

    # Precompute resume embeddings
    emb_r_skills = model.encode(resume_skills, convert_to_tensor=True) if resume_skills else None
    emb_r_exp = model.encode(resume_experience, convert_to_tensor=True) if resume_experience else None
    emb_r_proj = model.encode(resume_projects, convert_to_tensor=True) if resume_projects else None
    emb_r_edu = model.encode(resume_education, convert_to_tensor=True) if resume_education else None

    def sim(emb_r, text_jd):
        if emb_r is None or not text_jd.strip():
            return 0.0
        # Normalize long JD text by truncation warning or just let the model handle it.
        # all-MiniLM-L6-v2 max seq length is 256. 
        emb_j = model.encode(text_jd, convert_to_tensor=True)
        return max(0.0, min(1.0, util.cos_sim(emb_r, emb_j).item()))

    ranked_jobs = []

    print("Scoring JDs against the Resume...")
    for idx, jd in enumerate(all_jds):
        jd_title = jd.get("title", "")
        jd_id = jd.get("job_id", "")
        jd_overview = " ".join(jd.get("overview", []))
        jd_resp = " ".join(jd.get("responsibilities", []))
        jd_qual = " ".join(jd.get("qualifications", []))
        
        # 4. Section-wise Match
        score_skills = sim(emb_r_skills, jd_resp)      # resume.skills ↔ jd.responsibilities
        score_exp = sim(emb_r_exp, jd_overview)          # resume.experience ↔ jd.overview
        score_proj = sim(emb_r_proj, jd_resp)          # resume.projects ↔ jd.responsibilities
        score_edu = sim(emb_r_edu, jd_qual)            # resume.education ↔ jd.qualifications
        
        # 5. Weighted Scoring
        final_score = (
            (score_skills * 0.40) +
            (score_exp * 0.30) +
            (score_proj * 0.20) +
            (score_edu * 0.10)
        )
        
        ranked_jobs.append({
            "job_title": jd_title,
            "job_id": jd_id,
            "score": round(final_score, 4),
            "match_level": get_match_level(final_score),
            "section_scores": {
                "skills": round(score_skills, 4),
                "experience": round(score_exp, 4),
                "projects": round(score_proj, 4),
                "education": round(score_edu, 4)
            }
        })
        
    # 8. Batch Matching
    ranked_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    # 10. Save Output
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ranked_jobs.json")
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ranked_jobs, f, indent=4)
        
    sem_scores_path = os.path.join(out_dir, "semantic_scores.json")
    sem_scores = {jd["job_id"]: jd["score"] for jd in ranked_jobs}
    
    with open(sem_scores_path, "w", encoding="utf-8") as f:
        json.dump(sem_scores, f, indent=4)
        
    print(f"Matching complete. Results saved to {out_path} and {sem_scores_path}.")
    if ranked_jobs:
        print(f"Top Match: {ranked_jobs[0]['job_title']} with score {ranked_jobs[0]['score']}")

if __name__ == "__main__":
    main()
