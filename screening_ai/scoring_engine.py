import logging
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Deliverable 1 & 2: Per-question score breakdown & Parameters
# -------------------------------------------------------------------

class ParameterScore(BaseModel):
    """Explainable scoring for a specific parameter."""
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized score between 0 and 1")
    explanation: str = Field(..., description="Explanation for the given score")

class QuestionScoreBreakdown(BaseModel):
    """Breakdown of scores for a single screening question."""
    question_id: str
    question_text: str
    category: str
    candidate_response: str
    
    # Core scoring parameters
    clarity: ParameterScore
    relevance: ParameterScore
    completeness: ParameterScore
    consistency: ParameterScore
    
    normalized_score: float = Field(..., ge=0.0, le=1.0, description="Weighted average of parameters")
    scoring_importance: Literal["low", "medium", "high", "critical"] = "medium"

# -------------------------------------------------------------------
# Deliverable 3: Final screening score object
# -------------------------------------------------------------------

class ScreeningScoreResult(BaseModel):
    """Final aggregated score object for the entire screening."""
    candidate_id: str
    per_question_scores: List[QuestionScoreBreakdown]
    total_raw_score: float = Field(..., description="Sum of weighted scores")
    total_normalized_score: float = Field(..., ge=0.0, le=1.0, description="Final score normalized between 0 and 1")
    overall_explanation: str = Field(..., description="Aggregated explanation of the candidate's performance")

# -------------------------------------------------------------------
# Main Deliverable: Screening Scoring Engine
# -------------------------------------------------------------------

class ScreeningScoringEngine:
    """
    Engine to objectively evaluate candidate screening responses based on 
    Clarity, Relevance, Completeness, and Consistency.
    """
    def __init__(self):
        # Weights for normalization based on importance of the question
        self.importance_weights = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "critical": 2.0
        }
        
        # Weights for the four evaluation parameters
        self.parameter_weights = {
            "clarity": 0.2,
            "relevance": 0.3,
            "completeness": 0.3,
            "consistency": 0.2
        }

    def _evaluate_clarity(self, text: str) -> ParameterScore:
        """
        Evaluate clarity based on heuristics (e.g., word count, filler words).
        """
        if not text.strip():
            return ParameterScore(score=0.0, explanation="No response provided.")
            
        words = text.split()
        if len(words) < 3:
            return ParameterScore(score=0.4, explanation="Response is too brief, lacking clear articulation.")
            
        filler_words = ["um", "uh", "like", "you know", "basically", "kinda"]
        text_lower = text.lower()
        filler_count = sum(1 for f in filler_words if f in text_lower)
        
        if filler_count > 3:
            return ParameterScore(score=0.6, explanation="Contains multiple filler words which reduces clarity.")
        elif filler_count > 0:
            return ParameterScore(score=0.8, explanation="Clear response with minor hesitations or fillers.")
            
        return ParameterScore(score=1.0, explanation="Very clear and articulate response without filler words.")

    def _evaluate_relevance(self, text: str, category: str, is_off_topic: bool = False) -> ParameterScore:
        """
        Evaluate relevance based on intent and category context.
        """
        if not text.strip():
            return ParameterScore(score=0.0, explanation="No response provided.")
            
        if is_off_topic:
            return ParameterScore(score=0.0, explanation="Response is completely off-topic.")
            
        # Heuristic relevance logic based on category
        text_lower = text.lower()
        if category.lower() == "salary" and not any(char.isdigit() for char in text_lower) and "dollar" not in text_lower:
            return ParameterScore(score=0.3, explanation="Response does not contain numeric or salary-related information.")
            
        if category.lower() == "experience" and "year" not in text_lower and "month" not in text_lower and "work" not in text_lower:
            return ParameterScore(score=0.6, explanation="Response lacks explicit experience markers (like years/months).")

        return ParameterScore(score=1.0, explanation="Response is directly relevant to the question context.")

    def _evaluate_completeness(self, text: str, is_vague: bool = False) -> ParameterScore:
        """
        Evaluate completeness based on vagueness and level of detail.
        """
        if not text.strip():
            return ParameterScore(score=0.0, explanation="No response provided.")
            
        if is_vague:
            return ParameterScore(score=0.3, explanation="Response is too vague to be considered complete.")
            
        words = text.split()
        if len(words) < 5:
            return ParameterScore(score=0.5, explanation="Response is a partial answer and lacks detail.")
            
        return ParameterScore(score=1.0, explanation="Response provides complete and actionable information.")

    def _evaluate_consistency(self, text: str) -> ParameterScore:
        """
        Evaluate consistency (internal logic, lack of contradictions).
        """
        if not text.strip():
            return ParameterScore(score=0.0, explanation="No response provided.")
            
        # In a real system, consistency checks across multiple answers.
        # Here we provide a heuristic internal consistency score.
        text_lower = text.lower()
        if "yes" in text_lower and "no" in text_lower:
            return ParameterScore(score=0.5, explanation="Response contains potential contradictions (e.g., both yes and no).")
            
        return ParameterScore(score=1.0, explanation="Response is internally consistent and logical.")

    def score_single_question(
        self,
        question_id: str,
        question_text: str,
        category: str,
        candidate_response: str,
        importance: Literal["low", "medium", "high", "critical"] = "medium",
        is_off_topic: bool = False,
        is_vague: bool = False
    ) -> QuestionScoreBreakdown:
        """
        Builds the per-question scoring logic.
        """
        clarity = self._evaluate_clarity(candidate_response)
        relevance = self._evaluate_relevance(candidate_response, category, is_off_topic)
        completeness = self._evaluate_completeness(candidate_response, is_vague)
        consistency = self._evaluate_consistency(candidate_response)
        
        # Normalize score for this question (0.0 to 1.0)
        normalized_score = (
            clarity.score * self.parameter_weights["clarity"] +
            relevance.score * self.parameter_weights["relevance"] +
            completeness.score * self.parameter_weights["completeness"] +
            consistency.score * self.parameter_weights["consistency"]
        )
        
        return QuestionScoreBreakdown(
            question_id=question_id,
            question_text=question_text,
            category=category,
            candidate_response=candidate_response,
            clarity=clarity,
            relevance=relevance,
            completeness=completeness,
            consistency=consistency,
            normalized_score=round(normalized_score, 2),
            scoring_importance=importance
        )

    def evaluate_screening(self, candidate_id: str, responses: List[Dict]) -> ScreeningScoreResult:
        """
        Aggregates the total screening score.
        
        Expected format of 'responses' dict items:
        {
            "question_id": "q1",
            "question_text": "...",
            "category": "Experience",
            "candidate_response": "...",
            "importance": "high",       # Optional
            "is_off_topic": False,      # Optional
            "is_vague": False           # Optional
        }
        """
        per_question_scores = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for resp in responses:
            importance = resp.get("importance", "medium")
            q_score = self.score_single_question(
                question_id=resp["question_id"],
                question_text=resp["question_text"],
                category=resp["category"],
                candidate_response=resp["candidate_response"],
                importance=importance,
                is_off_topic=resp.get("is_off_topic", False),
                is_vague=resp.get("is_vague", False)
            )
            per_question_scores.append(q_score)
            
            weight = self.importance_weights.get(importance, 1.0)
            total_weighted_score += q_score.normalized_score * weight
            total_weight += weight
            
        # Normalize final score between 0 and 1
        final_normalized_score = 0.0
        if total_weight > 0:
            final_normalized_score = total_weighted_score / total_weight
            
        # Determine overall explanation based on aggregated performance
        if final_normalized_score >= 0.8:
            explanation = "Candidate provided highly clear, relevant, complete, and consistent responses overall."
        elif final_normalized_score >= 0.6:
            explanation = "Candidate provided satisfactory responses but lacked detail, relevance, or clarity in some specific areas."
        else:
            explanation = "Candidate responses were weak, vague, off-topic, or inconsistent across multiple important questions."
            
        return ScreeningScoreResult(
            candidate_id=candidate_id,
            per_question_scores=per_question_scores,
            total_raw_score=round(total_weighted_score, 2),
            total_normalized_score=round(final_normalized_score, 2),
            overall_explanation=explanation
        )
