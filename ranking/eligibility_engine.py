import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

class EligibilityEngine:
    def __init__(self, candidate_id=None):
        self.candidate_id = candidate_id
        self.rules = {}
        self.ats_results = []
        self.candidate_skills = []
        self.candidate_experience_years = 0
        self.candidate_location = "Remote" # Mocked for now
        self.candidate_availability = "immediate" # Mocked for now
        
        self.load_configs()
        self.load_data()

    def load_configs(self):
        config_path = os.path.join(BASE_DIR, "ranking", "eligibility_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.rules = json.load(f)
        else:
            print(f"Warning: {config_path} not found. Using empty rules.")

    def load_data(self):
        # Load ATS results
        ats_file = os.path.join(BASE_DIR, "outputs", "ats_scores.json")
        if os.path.exists(ats_file):
            with open(ats_file, "r") as f:
                data = json.load(f)
                self.ats_results = data.get("results", [])
                if not self.candidate_id:
                    self.candidate_id = data.get("candidate_id")
        
        if not self.candidate_id:
            return

        # Load skills
        skill_file = os.path.join(BASE_DIR, "reports", f"skills_output_{self.candidate_id}.json")
        if os.path.exists(skill_file):
            with open(skill_file, "r") as f:
                data = json.load(f)
                self.candidate_skills = [s.lower() for s in (data.get("technical_skills", []) + data.get("non_technical_skills", []))]

        # Load experience
        exp_file = os.path.join(BASE_DIR, "output", "experience_analysis.json")
        if os.path.exists(exp_file):
            with open(exp_file, "r") as f:
                data = json.load(f)
                months = data.get("candidate_analysis", {}).get("timeline", {}).get("total_calc_months", 0)
                self.candidate_experience_years = months / 12.0

    def evaluate_eligibility(self):
        eligibility_results = []
        
        default_rules = self.rules.get("default_rules", {})
        job_specific_rules = self.rules.get("job_specific_rules", {})
        
        for job in self.ats_results:
            job_title = job.get("job_title")
            ats_score = job.get("final_score", 0)
            
            # Get rules for this job or use defaults
            rules = job_specific_rules.get(job_title, default_rules)
            
            # Merge with defaults for missing keys
            current_rules = default_rules.copy()
            current_rules.update(rules)
            
            reasons = []
            is_eligible = True
            is_review = False
            
            # 1. ATS Score Check
            min_score = current_rules.get("min_ats_score", 60)
            if ats_score < min_score:
                if ats_score >= min_score * 0.8:
                    is_review = True
                    reasons.append(f"ATS score {ats_score}% is slightly below minimum {min_score}%")
                else:
                    is_eligible = False
                    reasons.append(f"ATS score {ats_score}% is below minimum {min_score}%")
            
            # 2. Mandatory Skills Check
            mandatory_skills = current_rules.get("mandatory_skills", [])
            missing_skills = []
            for m_skill in mandatory_skills:
                m_skill_lower = m_skill.lower()
                # Check if mandatory skill is in candidate skills (exact or substring)
                found = False
                for c_skill in self.candidate_skills:
                    if m_skill_lower in c_skill or c_skill in m_skill_lower:
                        found = True
                        break
                if not found:
                    missing_skills.append(m_skill)
            
            if missing_skills:
                is_eligible = False
                reasons.append(f"Missing mandatory skills: {', '.join(missing_skills)}")
                
            # 3. Experience Range Check
            min_exp = current_rules.get("min_experience_years", 0)
            max_exp = current_rules.get("max_experience_years", 50)
            if self.candidate_experience_years < min_exp:
                if self.candidate_experience_years >= min_exp * 0.9:
                    is_review = True
                    reasons.append(f"Experience {self.candidate_experience_years:.1f}y is slightly below minimum {min_exp}y")
                else:
                    is_eligible = False
                    reasons.append(f"Experience {self.candidate_experience_years:.1f}y is below minimum {min_exp}y")
            elif self.candidate_experience_years > max_exp:
                is_review = True
                reasons.append(f"Experience {self.candidate_experience_years:.1f}y exceeds maximum {max_exp}y (Overqualified?)")
            
            # 4. Location Constraint
            loc_constraint = current_rules.get("location_constraint")
            if loc_constraint and loc_constraint.lower() != self.candidate_location.lower():
                # If job allows Remote and candidate is Remote, it's fine
                if not (loc_constraint.lower() == "remote" and self.candidate_location.lower() == "remote"):
                    is_review = True
                    reasons.append(f"Location mismatch: Job prefers {loc_constraint}, Candidate is {self.candidate_location}")

            # 5. Availability Check
            # Availability levels: immediate > 15 days > 30 days > 60 days
            avail_levels = {"immediate": 0, "within 15 days": 1, "within 30 days": 2, "within 60 days": 3}
            avail_required = current_rules.get("availability_required")
            
            if avail_required and avail_required in avail_levels:
                cand_avail_val = avail_levels.get(self.candidate_availability, 0)
                req_avail_val = avail_levels.get(avail_required, 0)
                
                if cand_avail_val > req_avail_val:
                    is_review = True
                    reasons.append(f"Availability mismatch: Job requires {avail_required}, Candidate is {self.candidate_availability}")

            # Final Tagging
            if not is_eligible:
                status = "Rejected"
            elif is_review:
                status = "Review"
            else:
                status = "Eligible"
                
            eligibility_results.append({
                "job_title": job_title,
                "status": status,
                "score": ats_score,
                "reasons": reasons,
                "rules_applied": current_rules
            })
            
        return eligibility_results

    def save_results(self, results):
        output_file = os.path.join(BASE_DIR, "outputs", "candidate_eligibility.json")
        data = {
            "candidate_id": self.candidate_id,
            "overall_summary": {
                "eligible_count": len([r for r in results if r["status"] == "Eligible"]),
                "review_count": len([r for r in results if r["status"] == "Review"]),
                "rejected_count": len([r for r in results if r["status"] == "Rejected"])
            },
            "eligibility_decisions": results
        }
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        return output_file

if __name__ == "__main__":
    engine = EligibilityEngine()
    results = engine.evaluate_eligibility()
    out = engine.save_results(results)
    print(f"Eligibility decisions saved to {out}")
    print(f"Total Eligible: {len([r for r in results if r['status'] == 'Eligible'])}")
    print(f"Total Review: {len([r for r in results if r['status'] == 'Review'])}")
    print(f"Total Rejected: {len([r for r in results if r['status'] == 'Rejected'])}")
