import os
import json
from ranking.threshold_config import get_category

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
ATS_SCORES_FILE = os.path.join(OUTPUTS_DIR, "ats_scores.json")

class ShortlistingEngine:
    def __init__(self):
        self.ats_data = {}
        self.results = []
        self.summary = {
            "total_jobs": 0,
            "priority": 0,
            "shortlisted": 0,
            "review": 0,
            "rejected": 0
        }

    def load_scores(self):
        if not os.path.exists(ATS_SCORES_FILE):
            print(f"Error: {ATS_SCORES_FILE} not found. Please run ATS scoring first.")
            return False
        
        with open(ATS_SCORES_FILE, "r") as f:
            try:
                self.ats_data = json.load(f)
                self.results = self.ats_data.get("results", [])
                return True
            except json.JSONDecodeError:
                print("Error: Could not decode ATS scores JSON.")
                return False

    def process_and_rank(self):
        # Sort by final score descending
        self.results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        
        self.summary["total_jobs"] = len(self.results)
        
        ranked_results = []
        for rank, res in enumerate(self.results, start=1):
            score = res.get("final_score", 0)
            category = get_category(score)
            
            # Update summary counts
            if category == "Priority Shortlisted":
                self.summary["priority"] += 1
            elif category == "Shortlisted":
                self.summary["shortlisted"] += 1
            elif category == "Review":
                self.summary["review"] += 1
            else:
                self.summary["rejected"] += 1
                
            formatted_res = {
                "rank": rank,
                "job_title": res.get("job_title", "Unknown Role"),
                "score": score,
                "category": category,
                "breakdown": res.get("breakdown", {}),
                "insights": res.get("insights", [])
            }
            ranked_results.append(formatted_res)
            
        self.results = ranked_results

    def generate_final_shortlisting_json(self):
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        out_file = os.path.join(OUTPUTS_DIR, "final_shortlisting.json")
        data = {
            "candidate_id": self.ats_data.get("candidate_id", "unknown"),
            "summary": self.summary,
            "ranked_results": self.results
        }
        with open(out_file, "w") as f:
            json.dump(data, f, indent=4)
        return out_file

    def generate_top_5_matches_json(self):
        out_file = os.path.join(OUTPUTS_DIR, "top_5_matches.json")
        top_5 = self.results[:5]
        with open(out_file, "w") as f:
            json.dump(top_5, f, indent=4)
        return out_file

    def generate_recruiter_report(self):
        out_file = os.path.join(OUTPUTS_DIR, "final_report.txt")
        
        lines = []
        lines.append("=" * 50)
        lines.append("CANDIDATE MATCH REPORT")
        lines.append("=" * 50)
        lines.append("")
        
        categories = ["Priority Shortlisted", "Shortlisted", "Review", "Rejected"]
        headers = ["TOP MATCHES (Priority):", "SHORTLISTED:", "REVIEW:", "REJECTED:"]
        
        for cat, header in zip(categories, headers):
            cat_results = [r for r in self.results if r["category"] == cat]
            if cat_results:
                lines.append(header)
                lines.append("-" * len(header))
                for res in cat_results:
                    lines.append(f"{res['rank']}. {res['job_title']} \u2013 {res['score']}%")
                    for insight in res.get("insights", []):
                        lines.append(f"   * {insight}")
                lines.append("")
        
        with open(out_file, "w", encoding='utf-8') as f:
            f.write("\n".join(lines))
            
        return out_file

if __name__ == "__main__":
    print("Running Shortlisting Engine...")
    engine = ShortlistingEngine()
    if engine.load_scores():
        engine.process_and_rank()
        f1 = engine.generate_final_shortlisting_json()
        f2 = engine.generate_top_5_matches_json()
        f3 = engine.generate_recruiter_report()
        print(f"Generated: {f1}")
        print(f"Generated: {f2}")
        print(f"Generated: {f3}")
    else:
        print("Failed to load scores.")
