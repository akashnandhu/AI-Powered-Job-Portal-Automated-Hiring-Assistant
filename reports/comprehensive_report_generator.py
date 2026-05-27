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
                strengths.append(f"Exceptional performance in {friendly_name} ({contribution.raw_score}%).")
                
        if candidate_score.final_hiring_fit_score >= 80:
            strengths.append("High overall consistency across multiple evaluation stages.")
            
        if not strengths:
            strengths.append("Meets baseline expectations for the role.")
            
        return strengths
        
    def _extract_weaknesses(self, candidate_score: UnifiedCandidateScore) -> List[str]:
        weaknesses = []
        breakdown = candidate_score.cross_round_breakdown
        
        for round_name, contribution in breakdown.items():
            if contribution.raw_score < 60:
                friendly_name = round_name.replace("_round", "").replace("_", " ").title()
                weaknesses.append(f"Below average performance in {friendly_name} ({contribution.raw_score}%).")
                
        if not weaknesses:
            weaknesses.append("No significant weaknesses identified across standard evaluation metrics.")
            
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
            "metadata": {
                "candidate_id": candidate_id,
                "role": role,
                "generated_at": timestamp
            },
            "final_recommendation": {
                "decision": final_recommendation,
                "confidence_score": confidence,
                "readiness_band": candidate_score.readiness_band,
                "reasoning": reasoning
            },
            "performance_summary": {
                "overall_score": candidate_score.final_hiring_fit_score,
                "weight_system_used": candidate_score.weight_system_used,
                "round_breakdown": {
                    k: v.raw_score for k, v in candidate_score.cross_round_breakdown.items()
                }
            },
            "highlights": {
                "strengths": strengths,
                "weaknesses": weaknesses
            },
            "behavioral_and_integrity": {
                "risk_tag": risk_tag,
                "flags": risk_flags
            }
        }
        
        json_path = os.path.join(self.output_dir, f"{candidate_id}_COMPREHENSIVE_REPORT.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)
            
        # Build Markdown Output
        md_content = f"""# 📄 AI Candidate Evaluation Report
**Candidate ID:** `{candidate_id}`  
**Role:** {role}  
**Date Generated:** {timestamp}  

---

## 🎯 Final Recommendation: {final_recommendation}
- **Confidence Level:** {confidence}%
- **Readiness Band:** {candidate_score.readiness_band}
- **Overall Score:** {candidate_score.final_hiring_fit_score:.2f} / 100

### Executive Summary
"""
        for reason in reasoning:
            md_content += f"- {reason}\n"
            
        md_content += "\n---\n\n## 📊 Performance Breakdown\n"
        md_content += f"**Evaluation Profile:** {candidate_score.weight_system_used}\n\n"
        
        for round_name, contribution in candidate_score.cross_round_breakdown.items():
            friendly_name = round_name.replace("_round", "").replace("_", " ").title()
            md_content += f"- **{friendly_name}:** {contribution.raw_score:.2f}% *(Weight: {contribution.weight_applied})*\n"
            
        md_content += "\n---\n\n## 💡 Key Highlights\n### ✅ Strengths\n"
        for s in strengths:
            md_content += f"- {s}\n"
            
        md_content += "\n### ⚠️ Areas for Improvement (Weaknesses)\n"
        for w in weaknesses:
            md_content += f"- {w}\n"
            
        md_content += "\n---\n\n## 🛡️ Behavioral & Integrity Flags\n"
        md_content += f"**Risk Indicator:** `{risk_tag}`\n\n"
        for r in risk_flags:
            md_content += f"- {r}\n"
            
        md_content += "\n---\n*Report generated by AI-Powered Automated Hiring Assistant*"
        
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
