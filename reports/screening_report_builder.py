import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from screening_ai.scoring_engine import ScreeningScoreResult, QuestionScoreBreakdown
except ImportError:
    # Fallback/mock imports in case of path issues
    from pydantic import BaseModel
    class ParameterScore(BaseModel):
        score: float
        explanation: str
    class QuestionScoreBreakdown(BaseModel):
        question_id: str
        question_text: str
        category: str
        candidate_response: str
        clarity: ParameterScore
        relevance: ParameterScore
        completeness: ParameterScore
        consistency: ParameterScore
        normalized_score: float
        scoring_importance: str
    class ScreeningScoreResult(BaseModel):
        candidate_id: str
        per_question_scores: List[QuestionScoreBreakdown]
        total_raw_score: float
        total_normalized_score: float
        overall_explanation: str

logger = logging.getLogger(__name__)

class ScreeningReportBuilder:
    """
    Builder class to generate a recruiter-friendly screening report from AI evaluations.
    """

    def __init__(self):
        self.report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def analyze_responses(self, score_result: ScreeningScoreResult) -> Dict[str, Any]:
        """
        Analyzes the per-question scores to extract summaries and highlights.
        """
        salary_expectation = "Not provided"
        availability = "Not provided"
        skill_confirmations = []
        
        strengths = []
        risks = []
        missing_data = []
        key_answers = []

        for q in score_result.per_question_scores:
            cat = q.category.lower()
            resp = q.candidate_response.strip()
            
            # Key Answers
            key_answers.append({
                "question": q.question_text,
                "category": q.category,
                "answer": resp if resp else "No answer provided",
                "score": q.normalized_score,
                "importance": q.scoring_importance
            })

            # Missing Data Check
            if not resp or q.normalized_score < 0.2:
                missing_data.append(q.question_text)
                continue

            # Highlights extraction
            if cat == "salary":
                salary_expectation = resp
            elif cat == "notice period" or "availability" in q.question_text.lower():
                availability = resp
            elif cat == "skills":
                skill_confirmations.append({
                    "skill_topic": q.question_text,
                    "response": resp,
                    "confidence_score": q.normalized_score
                })

            # Strengths and Risks
            if q.normalized_score >= 0.8:
                strengths.append(f"**{q.category}**: Strong articulation and relevance. ({q.normalized_score * 100}%)")
            elif q.normalized_score <= 0.5:
                risks.append(f"**{q.category}**: Vague or inconsistent response to '{q.question_text}'. (Score: {q.normalized_score * 100}%)")

        return {
            "highlights": {
                "salary_expectation": salary_expectation,
                "availability": availability,
                "skill_confirmations": skill_confirmations
            },
            "summaries": {
                "strengths": strengths if strengths else ["No major strengths identified."],
                "risks": risks if risks else ["No major risks identified."],
                "missing_data": missing_data if missing_data else ["All mandatory fields captured."],
                "key_answers": key_answers
            }
        }

    def generate_markdown_report(self, candidate_name: str, score_result: ScreeningScoreResult) -> str:
        """
        Generates a visually structured, recruiter-ready Markdown report.
        """
        analysis = self.analyze_responses(score_result)
        highs = analysis["highlights"]
        sums = analysis["summaries"]
        
        score_percent = int(score_result.total_normalized_score * 100)
        score_badge = "🟢 Strong" if score_percent >= 75 else "🟡 Average" if score_percent >= 50 else "🔴 Weak"

        md = f"""# AI Candidate Screening Report

**Candidate Name**: {candidate_name}
**Candidate ID**: `{score_result.candidate_id}`
**Date of Screening**: {self.report_date}
**Overall AI Assessment Score**: {score_percent}% {score_badge}

> **AI Summary**: {score_result.overall_explanation}

---

## 🎯 Quick Highlights

| Metric | Details |
|--------|---------|
| **Salary Expectation** | {highs['salary_expectation']} |
| **Availability / Notice** | {highs['availability']} |

**Skill Confirmations**:
"""
        if highs['skill_confirmations']:
            for s in highs['skill_confirmations']:
                md += f"- **Topic**: {s['skill_topic']}\n  - *Response*: {s['response']}\n  - *Score*: {s['confidence_score']*100}%\n"
        else:
            md += "- No specific technical skills assessed or confirmed.\n"

        md += f"""
---

## 📊 Summary Insights

### ✅ Strengths
"""
        for st in sums['strengths']:
            md += f"- {st}\n"

        md += "\n### ⚠️ Potential Risks\n"
        for rk in sums['risks']:
            md += f"- {rk}\n"

        md += "\n### ❓ Missing / Vague Data\n"
        for md_item in sums['missing_data']:
            md += f"- {md_item}\n"

        md += """
---

## 💬 Key Answers & Breakdown

"""
        for ans in sums['key_answers']:
            score_mark = "🟢" if ans['score'] >= 0.8 else "🟡" if ans['score'] >= 0.5 else "🔴"
            md += f"""### {ans['category']} (Importance: {ans['importance'].capitalize()})
**Q: {ans['question']}**
> A: {ans['answer']}

*AI Evaluation Score*: {ans['score']*100}% {score_mark}

"""

        md += "\n---\n*Report generated automatically by the AI Screening Assistant.*\n"
        return md

    def export_report(self, candidate_name: str, score_result: ScreeningScoreResult, output_path: str):
        """
        Exports the markdown report to a file.
        """
        md_content = self.generate_markdown_report(candidate_name, score_result)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        logger.info(f"Report exported successfully to {output_path}")
        return md_content
