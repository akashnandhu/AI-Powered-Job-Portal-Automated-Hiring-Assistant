import json
import os
from datetime import datetime

class HRReportGenerator:
    """
    Generates an explainable markdown report for Candidate HR Score.
    """
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, candidate_name: str, evaluation_results: dict):
        report_path = os.path.join(self.output_dir, "HR_INTERVIEW_EVALUATION_REPORT.md")
        
        final_score = evaluation_results.get("final_hr_score", 0)
        breakdown = evaluation_results.get("score_breakdown", {})
        weights = evaluation_results.get("weights_used", {})
        consistency_details = evaluation_results.get("consistency_details", {})
        q_analysis = evaluation_results.get("question_level_analysis", [])
        
        # Determine performance band
        if final_score >= 85:
            band = "Excellent"
        elif final_score >= 70:
            band = "Good"
        elif final_score >= 50:
            band = "Needs Improvement"
        else:
            band = "Poor"

        md_content = f"""# HR Interview Evaluation Report
**Candidate Name:** {candidate_name}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. Overall HR Score: {final_score}/100 ({band})

The final score is a weighted aggregation of communication, behavioral confidence, answer relevance, and consistency metrics.

---

## 2. Explainable Scoring Breakdown

| Parameter | Score (0-100) | Weightage | Contribution to Final |
| :--- | :--- | :--- | :--- |
| **Answer Relevance** | {breakdown.get('answer_relevance', 0)} | {weights.get('answer_relevance', 0) * 100}% | {round(breakdown.get('answer_relevance', 0) * weights.get('answer_relevance', 0), 2)} |
| **Communication Score** | {breakdown.get('communication', 0)} | {weights.get('communication', 0) * 100}% | {round(breakdown.get('communication', 0) * weights.get('communication', 0), 2)} |
| **Confidence Score** | {breakdown.get('confidence', 0)} | {weights.get('confidence', 0) * 100}% | {round(breakdown.get('confidence', 0) * weights.get('confidence', 0), 2)} |
| **Consistency** | {breakdown.get('consistency', 0)} | {weights.get('consistency', 0) * 100}% | {round(breakdown.get('consistency', 0) * weights.get('consistency', 0), 2)} |
| **Total** | | **100%** | **{final_score}** |

---

## 3. Consistency Insights
- **Length Consistency:** {consistency_details.get('length_consistency', 'N/A')}/100 
- **Sentiment Consistency:** {consistency_details.get('sentiment_consistency', 'N/A')}/100

*(Note: Higher scores indicate steady behavior, while lower scores indicate erratic patterns or contradictions.)*

---

## 4. Question-Level Breakdown (Normalized Across Interview)

"""
        for q in q_analysis:
            md_content += f"### Q{q['question_index']}: {q['question']}\n"
            md_content += f"- **Answer Length:** {q['answer_length']} words\n"
            md_content += f"- **Relevance:** {q['scores']['relevance']}/100\n"
            md_content += f"- **Communication:** {q['scores']['communication']}/100\n"
            md_content += f"- **Confidence:** {q['scores']['confidence']}/100\n"
            
            comm_issues = q['insights'].get('communication_issues', [])
            if comm_issues:
                md_content += f"- *Filler Words Detected:* {', '.join(set(comm_issues))}\n"
                
            conf_issues = q['insights'].get('confidence_issues', [])
            if conf_issues:
                md_content += f"- *Stress Indicators Detected:* {', '.join(conf_issues)}\n"
            md_content += "\n"

        md_content += """---
*System generated evaluation by AI HR Scoring Engine.*
"""
        
        with open(report_path, "w") as f:
            f.write(md_content)
            
        # Also save as JSON
        json_path = os.path.join(self.output_dir, "HR_INTERVIEW_EVALUATION_REPORT.json")
        json_report_data = {
            "candidate_name": candidate_name,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "evaluation_results": evaluation_results,
            "performance_band": band
        }
        with open(json_path, "w") as f:
            json.dump(json_report_data, f, indent=4)
            
        return report_path, json_path

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scoring.hr_interview_scorer import HRInterviewScorer
    
    # Sample Test Run
    scorer = HRInterviewScorer()
    sample_qa = [
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
            "answer": "I haven't used cloud platforms extensively yet, mostly focused on local development."
        }
    ]
    results = scorer.evaluate_interview(sample_qa)
    generator = HRReportGenerator(output_dir="reports")
    report_file, json_file = generator.generate_report("AKASH AA", results)
    print(f"Generated sample HR report at: {report_file}")
    print(f"Generated sample HR JSON report at: {json_file}")
