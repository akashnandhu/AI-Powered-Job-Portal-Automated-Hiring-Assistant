import json
import os
from datetime import datetime
from typing import Dict, List

class RecruiterInsightsGenerator:
    """
    Converts AI HR interview analysis into recruiter-ready insights.
    """
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _extract_strengths(self, results: Dict) -> List[str]:
        strengths = []
        breakdown = results.get("score_breakdown", {})
        q_analysis = results.get("question_level_analysis", [])
        
        if breakdown.get("communication", 0) >= 80:
            strengths.append("Excellent communication skills and clear articulation.")
        if breakdown.get("confidence", 0) >= 80:
            strengths.append("Demonstrates high behavioral confidence during responses.")
        if breakdown.get("answer_relevance", 0) >= 85:
            strengths.append("Provides highly relevant and focused answers to questions.")
            
        # Check specific answers for length and detail
        detailed_answers = [q for q in q_analysis if q.get("answer_length", 0) >= 15 and q["scores"]["relevance"] >= 80]
        if q_analysis and len(detailed_answers) >= len(q_analysis) / 2:
            strengths.append("Consistently provides detailed and thoughtful responses.")
            
        if not strengths:
            strengths.append("Meets basic baseline requirements.")
            
        return strengths
        
    def _extract_weaknesses(self, results: Dict) -> List[str]:
        weaknesses = []
        breakdown = results.get("score_breakdown", {})
        q_analysis = results.get("question_level_analysis", [])
        
        if breakdown.get("communication", 0) < 60:
            weaknesses.append("Communication could be improved; observed some filler words or hesitations.")
        if breakdown.get("confidence", 0) < 60:
            weaknesses.append("Appears hesitant or lacks confidence in certain responses.")
        if breakdown.get("answer_relevance", 0) < 60:
            weaknesses.append("Answers occasionally stray from the core question.")
            
        short_answers = [q for q in q_analysis if q.get("answer_length", 0) < 8]
        if q_analysis and len(short_answers) >= len(q_analysis) / 2:
            weaknesses.append("Tends to provide overly brief responses lacking depth.")
            
        if not weaknesses:
            weaknesses.append("No major weaknesses observed.")
            
        return weaknesses
        
    def _extract_cultural_fit(self, results: Dict) -> List[str]:
        fit_indicators = []
        breakdown = results.get("score_breakdown", {})
        
        if breakdown.get("consistency", 0) >= 75:
            fit_indicators.append("Displays steady and reliable behavior, aligning well with team environments.")
        else:
            fit_indicators.append("Shows variable behavioral patterns which may require adaptability support.")
            
        if breakdown.get("confidence", 0) >= 70:
            fit_indicators.append("Proactive and confident, likely to take initiative.")
        else:
            fit_indicators.append("May prefer structured environments with clear guidance.")
            
        return fit_indicators
        
    def _extract_risk_flags(self, results: Dict) -> List[str]:
        flags = []
        breakdown = results.get("score_breakdown", {})
        consistency_details = results.get("consistency_details", {})
        q_analysis = results.get("question_level_analysis", [])
        
        if breakdown.get("consistency", 0) < 50:
            flags.append("HIGH RISK: Significant behavioral inconsistencies detected.")
            
        if consistency_details.get("sentiment_consistency", 100) < 50:
            flags.append("WARNING: Erratic mood or sentiment swings during the interview.")
            
        # Check for stress indicators
        stress_flags = 0
        for q in q_analysis:
            if q.get("insights", {}).get("confidence_issues"):
                stress_flags += 1
                
        if q_analysis and stress_flags >= len(q_analysis) / 2:
            flags.append(f"WARNING: High stress indicators detected in {stress_flags} responses.")
            
        if not flags:
            flags.append("No significant risk flags detected.")
            
        return flags

    def _generate_natural_language_summary(self, results: Dict, band: str, strengths: List[str], weaknesses: List[str], flags: List[str]) -> str:
        final_score = results.get("final_hr_score", 0)
        
        summary = f"The candidate achieved an overall HR performance score of {final_score}/100, placing them in the '{band}' category. "
        
        if any("HIGH RISK" in flag or "WARNING" in flag for flag in flags):
            summary += "While they have demonstrated some capabilities, there are notable risk flags that require recruiter attention. "
        elif band in ["Excellent", "Good"]:
            summary += "They demonstrated strong communication and behavioral consistency throughout the interview. "
            
        if strengths and strengths[0] != "Meets basic baseline requirements.":
            summary += f"Key strengths include: {strengths[0].lower()} "
            
        if weaknesses and weaknesses[0] != "No major weaknesses observed.":
            summary += f"However, an area for potential improvement is: {weaknesses[0].lower()}"
            
        return summary
        
    def generate_recruiter_report(self, candidate_name: str, evaluation_results: Dict):
        final_score = evaluation_results.get("final_hr_score", 0)
        
        if final_score >= 85:
            band = "Excellent"
        elif final_score >= 70:
            band = "Good"
        elif final_score >= 50:
            band = "Needs Improvement"
        else:
            band = "Poor"
            
        strengths = self._extract_strengths(evaluation_results)
        weaknesses = self._extract_weaknesses(evaluation_results)
        cultural_fit = self._extract_cultural_fit(evaluation_results)
        risk_flags = self._extract_risk_flags(evaluation_results)
        
        nl_summary = self._generate_natural_language_summary(evaluation_results, band, strengths, weaknesses, risk_flags)
        
        # Inconsistencies highlight
        consistency_details = evaluation_results.get("consistency_details", {})
        inconsistencies = []
        if consistency_details.get("length_consistency", 100) < 60:
            inconsistencies.append(f"Answer length consistency is low ({consistency_details.get('length_consistency')}%). Responses varied significantly in detail.")
        if consistency_details.get("sentiment_consistency", 100) < 60:
            inconsistencies.append(f"Sentiment consistency is low ({consistency_details.get('sentiment_consistency')}%). Observed varying tonal shifts across answers.")
            
        if not inconsistencies:
            inconsistencies.append("The candidate maintained a highly consistent profile throughout the interview.")

        # Markdown Content
        md_content = f"""# Recruiter Insights Report
**Candidate Name:** {candidate_name}
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Overall HR Band:** {band} ({final_score}/100)

---

## 1. Natural-Language Summary
{nl_summary}

---

## 2. Candidate Strengths
"""
        for s in strengths:
            md_content += f"- {s}\n"
            
        md_content += "\n## 3. Areas for Improvement (Weaknesses)\n"
        for w in weaknesses:
            md_content += f"- {w}\n"
            
        md_content += "\n## 4. Cultural Fit Indicators\n"
        for c in cultural_fit:
            md_content += f"- {c}\n"
            
        md_content += "\n## 5. Risk Flags\n"
        for r in risk_flags:
            md_content += f"- {r}\n"
            
        md_content += "\n## 6. Highlighted Inconsistencies\n"
        for i in inconsistencies:
            md_content += f"- {i}\n"
            
        md_content += "\n---\n*Report generated by AI Interview Insights Generator*"

        report_path_md = os.path.join(self.output_dir, f"RECRUITER_INSIGHTS_{candidate_name.replace(' ', '_').upper()}.md")
        with open(report_path_md, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        # JSON output
        report_data = {
            "candidate_name": candidate_name,
            "overall_score": final_score,
            "band": band,
            "natural_language_summary": nl_summary,
            "structured_summary": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "cultural_fit_indicators": cultural_fit,
                "risk_flags": risk_flags
            },
            "highlighted_inconsistencies": inconsistencies
        }
        
        report_path_json = os.path.join(self.output_dir, f"RECRUITER_INSIGHTS_{candidate_name.replace(' ', '_').upper()}.json")
        with open(report_path_json, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)
            
        return report_path_md, report_path_json

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scoring.hr_interview_scorer import HRInterviewScorer
    
    scorer = HRInterviewScorer()
    
    # Simulating a good candidate
    good_qa = [
        {
            "question": "Please introduce yourself and your background.",
            "answer": "Hi, I'm Akash AA. I'm a Data Science student with experience in Python, machine learning, and building web applications using Django."
        },
        {
            "question": "What is your experience with Machine Learning?",
            "answer": "I'm currently interning at Scope India, where I've built models using Linear Regression and Decision Trees."
        },
        {
            "question": "What are your salary expectations for this role?",
            "answer": "I'm open to industry standard packages for entry-level data science roles."
        },
        {
            "question": "Do you have experience with Cloud platforms?",
            "answer": "I haven't used cloud platforms extensively yet, mostly focused on local development. However, I am a fast learner and eager to pick it up."
        }
    ]
    good_results = scorer.evaluate_interview(good_qa)
    
    generator = RecruiterInsightsGenerator(output_dir="reports")
    md1, json1 = generator.generate_recruiter_report("AKASH AA", good_results)
    
    print("Generation complete.")
    print(f"Generated Reports: {md1}, {json1}")
