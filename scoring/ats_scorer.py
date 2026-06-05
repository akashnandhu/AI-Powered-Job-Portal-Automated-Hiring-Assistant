import os
import sys
import json
import glob
import re
import math
import time
from functools import lru_cache
from scoring.weights_config import get_weights_for_category

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from config import CANDIDATE_ID
from utils.logger import obs


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JD_DIR = os.path.join(BASE_DIR, "output", "jd_files")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FINAL_OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

class ATSScorer:
    def __init__(self, candidate_id=None, resume_data=None):
        self.candidate_id = candidate_id or CANDIDATE_ID
        self.candidate_skills = []
        self.candidate_confidences = {}
        self.candidate_exp_months = 0
        self.candidate_education = []
        self.semantic_scores = {}
        
        if resume_data:
            self.load_from_dict(resume_data)
        else:
            self.load_candidate_data()

    def load_from_dict(self, resume_data):
        self.candidate_skills = resume_data.get("skills", [])
        self.candidate_confidences = resume_data.get("confidences", {})
        self.candidate_exp_months = resume_data.get("exp_months", 0)
        self.candidate_education = resume_data.get("education", [])
        self.semantic_scores = resume_data.get("semantic_scores", {})

    def load_candidate_data(self):
        # 1. Load Skills
        skill_file = os.path.join(REPORTS_DIR, f"skills_output_{self.candidate_id}.json")
        if not os.path.exists(skill_file):
            raise FileNotFoundError(f"Error: Critical skills file {skill_file} not found for candidate. Run skill extractor first.")
            
        with open(skill_file, "r") as f:
            data = json.load(f)
            self.candidate_skills = data.get("technical_skills", []) + data.get("non_technical_skills", [])
            self.candidate_confidences = data.get("confidence", {})

        # 2. Load Experience
        exp_file = os.path.join(OUTPUT_DIR, "experience_analysis.json")
        if os.path.exists(exp_file):
            with open(exp_file, "r") as f:
                data = json.load(f)
                analysis = data.get("candidate_analysis", {})
                timeline = analysis.get("timeline", {})
                self.candidate_exp_months = timeline.get("total_calc_months", 0)

        # 3. Load Education
        edu_file = os.path.join(OUTPUT_DIR, "education_analysis.json")
        if os.path.exists(edu_file):
            with open(edu_file, "r") as f:
                data = json.load(f)
                parsed = data.get("parsed_data", {})
                self.candidate_education = parsed.get("education", [])

        # 4. Load Semantic Scores
        sem_file = os.path.join(OUTPUT_DIR, "semantic_scores.json")
        if not os.path.exists(sem_file):
            sem_file = os.path.join(FINAL_OUTPUT_DIR, "semantic_scores.json")
        
        if os.path.exists(sem_file):
            with open(sem_file, "r") as f:
                self.semantic_scores = json.load(f)
        else:
            print("Warning: semantic_scores.json missing. Fallback to 0.5 semantic score.")
            self.semantic_scores = {}

    def extract_jd_skills(self, jd_data):
        text_elements = jd_data.get("skills_required", []) + \
                        jd_data.get("education_required", []) + \
                        [jd_data.get("experience_required", "")]
        text = " ".join([str(t) for t in text_elements if t])
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return set(words)

    def compute_skill_score(self, jd_data):
        jd_words = self.extract_jd_skills(jd_data)
        if not jd_words:
            return 0.5, ["No explicit skills extracted from JD."]

        synonym_mapping = {
            "pharma": "pharmaceutical",
            "clinical research": "clinical trials",
            "ml": "machine learning",
            "ai": "artificial intelligence"
        }

        matched_skills = []
        base_score = 0.0

        # Also add mapped values to jd_words for robust matching
        jd_words_expanded = set(jd_words)
        for w in jd_words:
            for k, v in synonym_mapping.items():
                if w == v:
                    jd_words_expanded.add(k)
                elif w == k:
                    jd_words_expanded.add(v)

        for skill in self.candidate_skills:
            skill_lower = skill.lower()
            skill_mapped = synonym_mapping.get(skill_lower, skill_lower)
            skill_tokens = skill_mapped.split()
            
            # If the skill or its parts appear in JD
            if any(t in jd_words_expanded for t in skill_tokens):
                matched_skills.append(skill)
                # Use confidence score
                base_score += self.candidate_confidences.get(skill, 0.8)

        # Normalization: Assume a typical role demands about 5-10 key skills
        expected_skills = max(5, int(len(jd_words) / 10))
        score = base_score / expected_skills if expected_skills > 0 else 0

        insights = []
        # Bonus and Penalties
        if len(matched_skills) < expected_skills * 0.3:
            # Penalize missing critical skills
            score *= 0.85
            insights.append("Missing critical skills penalty applied (-15%).")
        elif len(matched_skills) >= expected_skills:
            # Boost for extra relevant skills
            score *= 1.10
            insights.append("Boost applied for possessing extra relevant skills (+10%).")
            
        score = min(1.0, max(0.0, score))
        if matched_skills:
            insights.append(f"Strong skill match ({len(matched_skills)} matched).")
        return score, insights

    def compute_experience_score(self, jd_data):
        req_str = jd_data.get("experience_required", "").lower()
        
        # Extract years from string
        years_match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\s*years?', req_str)
        if years_match:
            min_years = float(years_match.group(1))
            req_years = min_years
        else:
            # If JD does not specify years -> assume 2-5 years baseline (take 3.5 average)
            req_years = 3.5

        candidate_years = self.candidate_exp_months / 12.0
        
        if req_years == 0:
            score = 1.0  # Freshers welcome
        else:
            score = min(1.0, candidate_years / req_years)

        insights = []
        if score >= 1.0:
            insights.append(f"Exceeds expected experience ({candidate_years:.1f} vs {req_years} years).")
        elif score >= 0.7:
            insights.append("Moderate experience alignment.")
        else:
            insights.append("Slightly under-experienced for the role.")
            
        return score, insights

    def compute_education_score(self, jd_data):
        score = 0.3
        insights = ["Basic education alignment (0.3)."]
        
        for edu in self.candidate_education:
            degree = edu.get("degree", "").lower()
            field = edu.get("field", "").lower()
            norm = edu.get("normalized_degree", "").lower()
            
            # PharmD / M.Pharm -> 1.0
            if "pharmd" in degree or "m.pharm" in degree or "master of pharmacy" in norm:
                score = max(score, 1.0)
                insights = ["Outstanding education match (PharmD/M.Pharm -> 1.0)."]
            # Related -> 0.7 (e.g., B.Pharm, Science, Chemistry)
            elif "pharm" in degree or "science" in field or "chemistry" in field or "biology" in field:
                score = max(score, 0.7)
                insights = ["Good education match (Related Field -> 0.7)."]

        return score, insights

    @lru_cache(maxsize=1000)
    def compute_semantic_score(self, jd_filename):
        # Ensure we check the filename mapping
        # E.g. ai_in_drug_discovery_researcher.json vs ai_in_drug_discovery_researcher
        base_name = jd_filename.replace(".json", "")
        
        # Default to 0.5 if completely missing
        score = self.semantic_scores.get(jd_filename, self.semantic_scores.get(base_name, 0.5))
        
        # Scale up the raw cosine similarity slightly as raw embeddings often max out around 0.6-0.7
        score = min(1.0, score * 1.5)
            
        insights = []
        if score > 0.8:
            insights.append("High semantic similarity based on overall profile.")
        elif score > 0.6:
            insights.append("Moderate semantic similarity.")
        
        return score, insights

    def score_single_jd(self, jd_data, filename="memory_jd.json"):
        job_title = jd_data.get("job_title", filename.replace(".json", "").replace("_", " ").title())
        category = jd_data.get("category", "")
        
        # Sub-scores
        skill_score, skill_ins = self.compute_skill_score(jd_data)
        exp_score, exp_ins = self.compute_experience_score(jd_data)
        edu_score, edu_ins = self.compute_education_score(jd_data)
        sem_score, sem_ins = self.compute_semantic_score(filename)
        
        # Bias Reduction - Implement Combined Scoring
        skill_w = 0.3
        exp_w = 0.2
        sem_w = 0.5
        
        available_weights = 0.0
        computed_score = 0.0
        
        if skill_score is not None:
            computed_score += skill_score * skill_w
            available_weights += skill_w
        if exp_score is not None:
            computed_score += exp_score * exp_w
            available_weights += exp_w
        if sem_score is not None:
            computed_score += sem_score * sem_w
            available_weights += sem_w
            
        # Normalize to 1.0 if some weights were missing
        final_score_raw = computed_score / available_weights if available_weights > 0 else 0
        final_percentage = round(final_score_raw * 100, 2)
        
        # Only include valid insights
        all_insights = [i for p in [skill_ins, exp_ins, edu_ins, sem_ins] for i in p if i]
        
        return {
            "job_title": job_title,
            "jd_filename": filename,
            "category": category,
            "final_score": final_percentage,
            "breakdown": {
                "skill": round(skill_score, 2),
                "experience": round(exp_score, 2),
                "education": round(edu_score, 2),
                "semantic": round(sem_score, 2)
            },
            "insights": all_insights[:3]  # top 3 insights
        }

    def score_all_jobs(self):
        start_time = time.time()
        results = []
        
        jd_files = glob.glob(os.path.join(JD_DIR, "*.json"))
        
        for jd_file in jd_files:
            filename = os.path.basename(jd_file)
            try:
                with open(jd_file, "r") as f:
                    jd_data = json.load(f)
            except Exception as e:
                obs.log_error("ATSScorer", f"Failed to load JD file {filename}: {str(e)}")
                continue
                
            res = self.score_single_jd(jd_data, filename)
            results.append(res)
            
            obs.log_model_inference(
                model_name="ATSScorer",
                candidate_id=self.candidate_id,
                output_score=res["final_score"],
                latency_ms=round((time.time() - start_time) * 1000, 2),
                metadata={"job_title": res["job_title"], "jd_filename": res["jd_filename"]}
            )
            
        latency = time.time() - start_time
        print(f"[API Optimization] Batch Processing Latency: {round(latency * 1000, 2)} ms for {len(results)} jobs.")
        
        return results

if __name__ == "__main__":
    scorer = ATSScorer()
    results = scorer.score_all_jobs()
    print(f"Scored {len(results)} jobs. Top score: {max([r['final_score'] for r in results]) if results else 0}")
