import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CognitiveScorer:
    """
    Evaluates candidate's cognitive reasoning, situational judgment, and problem-solving clarity.
    """
    def __init__(self):
        # Keywords indicating structured reasoning
        self.reasoning_markers = [
            "firstly", "secondly", "then", "therefore", "consequently", 
            "because", "logical", "step-by-step", "process", "estimate", 
            "assume", "calculation", "framework"
        ]
        
        # Keywords indicating problem-solving and situational awareness
        self.problem_solving_markers = [
            "immediate", "priority", "assess", "communicate", "plan", 
            "solution", "bug", "risk", "mitigate", "escalate", "document"
        ]

    def score_logical_reasoning(self, text: str) -> Dict[str, Any]:
        """
        Scores logical thinking ability based on structure and reasoning keywords.
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return {"score": 0.0, "explanation": "No response provided."}

        # 1. Check for structured reasoning markers
        marker_count = sum(1 for m in self.reasoning_markers if m in text_lower)
        
        # 2. Check for complexity (average word length and sentence structure)
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_len = len(words) / max(1, len(sentences))
        
        # Reasoning score heuristic
        # High score if they use markers and have structured sentences
        reasoning_score = min(1.0, (marker_count * 0.2) + (0.4 if avg_sentence_len > 12 else 0.2))
        
        return {
            "score": round(reasoning_score, 2),
            "explanation": "High logical structure" if reasoning_score > 0.8 else "Basic reasoning applied" if reasoning_score > 0.5 else "Reasoning lacks structure"
        }

    def score_situational_judgment(self, text: str) -> Dict[str, Any]:
        """
        Scores situational judgment based on action-oriented and risk-aware keywords.
        """
        text_lower = text.lower()
        if not text_lower.strip():
            return {"score": 0.0, "explanation": "No response provided."}

        # 1. Action markers
        action_count = sum(1 for m in self.problem_solving_markers if m in text_lower)
        
        # 2. Check for stakeholder communication (essential in situational judgment)
        stakeholder_keywords = ["manager", "client", "team", "stakeholder", "user"]
        communication_detected = any(s in text_lower for s in stakeholder_keywords)
        
        # Situational score heuristic
        judgment_score = min(1.0, (action_count * 0.15) + (0.25 if communication_detected else 0.0))
        
        return {
            "score": round(judgment_score, 2),
            "explanation": "Decisive and collaborative" if judgment_score > 0.8 else "Action-oriented but lacks detail" if judgment_score > 0.5 else "Lacks clear situational strategy"
        }

    def detect_problem_solving_clarity(self, text: str) -> Dict[str, Any]:
        """
        Measures how clearly the candidate explains their solution process.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return {"score": 0.0, "explanation": "No response provided."}

        # 1. Check for transitions (clarity of flow)
        transitions = ["then", "after", "result", "finally", "next"]
        transition_count = sum(1 for t in transitions if t in text.lower())
        
        # 2. Check for concrete details (nouns and verbs vs vague words)
        vague_words = ["thing", "stuff", "maybe", "something", "whatever"]
        vague_count = sum(1 for v in vague_words if v in text.lower())
        
        clarity_score = min(1.0, (transition_count * 0.2) + 0.4 - (vague_count * 0.1))
        
        return {
            "score": round(max(0.0, clarity_score), 2),
            "explanation": "Highly clear solution path" if clarity_score > 0.7 else "Vague solution steps" if clarity_score < 0.4 else "Moderate clarity"
        }

    def evaluate_cognitive_aspect(self, category: str, text: str) -> Dict[str, Any]:
        """
        Aggregated evaluation for cognitive/situational questions.
        """
        if category == "Cognitive Reasoning":
            logical = self.score_logical_reasoning(text)
            clarity = self.detect_problem_solving_clarity(text)
            overall = (logical["score"] * 0.7 + clarity["score"] * 0.3)
            return {
                "category": category,
                "overall_score": round(overall, 2),
                "breakdown": {
                    "logical_thinking": logical,
                    "problem_solving_clarity": clarity
                }
            }
        elif category == "Situational Judgment":
            judgment = self.score_situational_judgment(text)
            clarity = self.detect_problem_solving_clarity(text)
            overall = (judgment["score"] * 0.7 + clarity["score"] * 0.3)
            return {
                "category": category,
                "overall_score": round(overall, 2),
                "breakdown": {
                    "situational_judgment": judgment,
                    "problem_solving_clarity": clarity
                }
            }
        
        return {"error": "Invalid category for cognitive evaluation"}

if __name__ == "__main__":
    scorer = CognitiveScorer()
    sample_text = "Firstly, I would assess the risk. Then, I'd communicate with the client. Therefore, the project stays on track."
    print(scorer.evaluate_cognitive_aspect("Situational Judgment", sample_text))
