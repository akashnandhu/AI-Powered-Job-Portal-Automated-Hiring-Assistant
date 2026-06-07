import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from scoring.unified_candidate_score import UnifiedCandidateScore
from scoring.decision_engine import HiringDecision

class ComprehensiveReportGenerator:
    """
    Generates a full candidate AI profile report combining insights from all rounds.
    Output is in an export-ready Markdown format and JSON format for APIs.
    """
    def __init__(self, output_dir="reports/candidates"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _extract_strengths(self, candidate_score: UnifiedCandidateScore) -> List[str]:
        strengths = []
        breakdown = candidate_score.cross_round_breakdown
        
        for round_name, contribution in breakdown.items():
            if contribution.raw_score >= 85:
                friendly_name = round_name.replace("_round", "").replace("_", " ").title()
                strengths.append(f"⭐ **Exceptional performance** in {friendly_name} ({contribution.raw_score}%).")
                
        if candidate_score.final_hiring_fit_score >= 80:
            strengths.append("📈 **High Overall Consistency** across multiple evaluation metrics.")
            
        if not strengths:
            strengths.append("Meets baseline expectations for the role.")
            
        return strengths
        
    def _extract_weaknesses(self, candidate_score: UnifiedCandidateScore) -> List[str]:
        weaknesses = []
        breakdown = candidate_score.cross_round_breakdown
        
        for round_name, contribution in breakdown.items():
            if contribution.raw_score < 60:
                friendly_name = round_name.replace("_round", "").replace("_", " ").title()
                weaknesses.append(f"📉 **Area of Concern** in {friendly_name} ({contribution.raw_score}%).")
                
        if not weaknesses:
            weaknesses.append("✅ **No significant weaknesses** identified across standard metrics.")
            
        return weaknesses

    def generate_report(self, candidate_score: UnifiedCandidateScore, decision: HiringDecision, additional_insights: Optional[Dict] = None) -> tuple[str, str]:
        """
        Generates the comprehensive report in MD and JSON formats.
        """
        candidate_id = candidate_score.candidate_id
        role = candidate_score.role_evaluated_for
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Strengths & Weaknesses
        strengths = self._extract_strengths(candidate_score)
        weaknesses = self._extract_weaknesses(candidate_score)
        
        # 2. Risk Indicators
        risk_tag = candidate_score.risk_tag
        risk_flags = decision.risk_factors if decision.risk_factors else ["No significant behavioral or integrity risks detected."]
        
        # 3. Recommendations
        final_recommendation = decision.decision
        confidence = decision.confidence_score
        reasoning = decision.reasoning
        
        # Build JSON Output
        report_data = {
            "success": True,
            "data": {
                "candidate_id": candidate_id,
                "final_score": candidate_score.final_hiring_fit_score,
                "decision": final_recommendation,
                "summary": {
                    "strengths": strengths,
                    "weaknesses": weaknesses,
                    "risks": risk_flags
                },
                "confidence": "High" if confidence > 85 else "Medium" if confidence > 65 else "Low",
                "recommendation": "Proceed with offer" if final_recommendation == "Selected" else "Quarantine / Human Auditor" if final_recommendation == "Quarantined" else "Hold for Review"
            },
            "meta": {
                "latency_ms": 120,
                "version": "v1.0"
            }
        }
        
        json_path = os.path.join(self.output_dir, f"{candidate_id}_COMPREHENSIVE_REPORT.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)
            
        # Build Markdown Output
        quick_take = "Strong positive signal." if final_recommendation == "Selected" else "Exercise caution; review flags." if final_recommendation in ["Hold / Review", "Quarantined"] else "Clear negative signal."
        
        md_content = f"""# 📄 Zecpath AI Executive Evaluation Report
> **Candidate ID:** `{candidate_id}`  |  **Role:** `{role}`  |  **Date Generated:** `{timestamp}`

---

## 🎯 **Final AI Ruling: {final_recommendation.upper()}**
- **Confidence Level:** `{confidence}%`
- **Readiness Band:** `{candidate_score.readiness_band}`
- **Overall Aggregated Score:** `{candidate_score.final_hiring_fit_score:.2f} / 100`

> **Recruiter Quick Take:** *{quick_take}*

### 📌 AI Decision Reasoning
"""
        for reason in reasoning:
            md_content += f"- {reason}\n"
            
        md_content += "\n---\n\n## 📊 Performance Breakdown\n"
        md_content += f"> **Evaluation Profile Configuration:** `{candidate_score.weight_system_used}`\n\n"
        md_content += "| Evaluation Stage | Raw Score | Overall Weight Contribution |\n"
        md_content += "|------------------|-----------|-----------------------------|\n"
        
        for round_name, contribution in candidate_score.cross_round_breakdown.items():
            friendly_name = round_name.replace("_round", "").replace("_", " ").title()
            md_content += f"| **{friendly_name}** | {contribution.raw_score:.2f}% | {contribution.weight_applied} |\n"
            
        md_content += "\n---\n\n## 💡 Key Highlights\n### ✅ Recognized Strengths\n"
        for s in strengths:
            md_content += f"- {s}\n"
            
        md_content += "\n### ⚠️ Improvement Areas\n"
        for w in weaknesses:
            md_content += f"- {w}\n"
            
        md_content += "\n---\n\n## 🛡️ Trust & Integrity Validation\n"
        
        risk_color = "🔴" if risk_tag == "RED" else "🟡" if risk_tag == "YELLOW" else "🟢"
        md_content += f"> **Risk System Status:** {risk_color} `{risk_tag}`\n\n"
        for r in risk_flags:
            md_content += f"- {r}\n"
            
        md_content += "\n---\n*Securely generated by the Zecpath DecisionEngine API*"
        
        md_path = os.path.join(self.output_dir, f"{candidate_id}_COMPREHENSIVE_REPORT.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        return md_path, json_path

if __name__ == "__main__":
    from scoring.unified_candidate_score import RoundContribution
    
    candidate = UnifiedCandidateScore(
        candidate_id="CAND-DEMO",
        role_evaluated_for="Data Scientist",
        final_hiring_fit_score=89.5,
        readiness_band="Exceptional Fit (Fast-Track Offer)",
        risk_tag="GREEN",
        weight_system_used="Technical",
        cross_round_breakdown={
            "ats_round": RoundContribution(95.0, "10%", 9.5),
            "screening_round": RoundContribution(85.0, "20%", 17.0),
            "hr_interview_round": RoundContribution(88.0, "20%", 17.6),
            "technical_performance": RoundContribution(92.0, "50%", 46.0)
        }
    )
    
    decision = HiringDecision(
        candidate_id="CAND-DEMO",
        decision="Selected",
        confidence_score=94.5,
        reasoning=[
            "Strong overall performance with a unified score of 89.50%, exceeding the selection threshold.",
            "Demonstrated exceptional performance in Ats, Technical Performance."
        ],
        risk_factors=[]
    )
    
    generator = ComprehensiveReportGenerator(output_dir="reports/candidates")
    md_file, json_file = generator.generate_report(candidate, decision)
    print(f"Generated test reports:\nMD: {md_file}\nJSON: {json_file}")
