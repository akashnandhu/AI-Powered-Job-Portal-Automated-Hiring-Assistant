import json
import logging
from typing import List, Dict

from scoring.communication_scorer import CommunicationScorer
from scoring.confidence_analyzer import ConfidenceAnalyzer
from scoring.weights_config import WEIGHTS_CONFIG

class HRInterviewScorer:
    """
    Combines HR responses and communication signals into a structured score.
    Parameters:
    - Answer Relevance
    - Communication Score
    - Confidence Score
    - Consistency
    """
    def __init__(self):
        self.communication_scorer = CommunicationScorer()
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.weights = WEIGHTS_CONFIG.get("hr_interview", {
            "answer_relevance": 0.35,
            "communication": 0.25,
            "confidence": 0.20,
            "consistency": 0.20
        })

    def analyze_answer_relevance(self, question: str, answer: str) -> float:
        """
        Mock implementation for Answer Relevance.
        In a real system, this would use semantic similarity (e.g., sentence-transformers)
        between the question intent and the answer content.
        """
        if not answer.strip():
            return 0.0

        q_words = set(question.lower().split())
        a_words = set(answer.lower().split())

        # Improved heuristic: Ensure we don't just reward length.
        # We require some overlap or a reasonable length to get a passing score.
        overlap = len(q_words.intersection(a_words))
        length_ratio = min(1.0, len(a_words) / 12.0)
        
        if overlap == 0 and len(a_words) < 5:
            # Short and completely no overlap = very low relevance
            relevance_score = 0.2 * length_ratio
        else:
            base_score = length_ratio * 0.40  # 40% based on length
            overlap_score = min(1.0, overlap / 3.0) * 0.60  # 60% based on overlap
            relevance_score = base_score + overlap_score

        # For standard HR questions, candidates rarely repeat the question words.
        # Ensure a reasonable minimum if it's a substantive answer.
        if len(a_words) >= 10 and relevance_score < 0.70:
            relevance_score = 0.70 + (overlap * 0.05)
            
        return min(100.0, round(relevance_score * 100, 2))

    def analyze_consistency(self, answers: List[str]) -> Dict:
        """
        Analyzes consistency across all answers in the interview.
        Checks for length variation, sentiment consistency, and repeated contradictions.
        """
        if not answers:
            return {"score": 0.0, "details": "No answers provided."}

        if len(answers) == 1:
            return {"score": 100.0, "details": "Only one answer, assumed perfectly consistent."}

        # Check length consistency
        lengths = [len(a.split()) for a in answers]
        avg_length = sum(lengths) / len(lengths)
        length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev_length = length_variance ** 0.5
        
        # Penalty for erratic answer lengths
        # Use a softer penalty to prevent extreme drops
        length_consistency_score = max(0.0, 1.0 - (std_dev_length / max(1, avg_length * 1.5)))
        
        # Check sentiment consistency
        sentiments = [self.confidence_analyzer.analyze_sentiment(a)["score"] for a in answers]
        avg_sentiment = sum(sentiments) / len(sentiments)
        sentiment_variance = sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)
        std_dev_sentiment = sentiment_variance ** 0.5
        
        # Penalty for erratic mood swings
        sentiment_consistency_score = max(0.0, 1.0 - std_dev_sentiment)

        final_consistency = (length_consistency_score * 0.5 + sentiment_consistency_score * 0.5) * 100
        
        return {
            "score": round(final_consistency, 2),
            "details": {
                "length_consistency": round(length_consistency_score * 100, 2),
                "sentiment_consistency": round(sentiment_consistency_score * 100, 2)
            }
        }

    def evaluate_interview(self, qa_pairs: List[Dict[str, str]]) -> Dict:
        """
        Evaluates the entire HR interview.
        Normalizes across different interview lengths by averaging question-level scores.
        """
        if not qa_pairs:
            return {"error": "No interview data provided."}

        num_questions = len(qa_pairs)
        
        total_relevance = 0.0
        total_communication = 0.0
        total_confidence = 0.0
        
        question_breakdowns = []
        all_answers = []

        for index, pair in enumerate(qa_pairs):
            question = pair.get("question", "")
            answer = pair.get("answer", "")
            all_answers.append(answer)
            
            # Question-level metrics
            relevance = self.analyze_answer_relevance(question, answer)
            comm_result = self.communication_scorer.evaluate(answer)
            conf_result = self.confidence_analyzer.evaluate(answer)
            
            total_relevance += relevance
            total_communication += comm_result["overall_score"]
            total_confidence += conf_result["behavioral_confidence_score"]
            
            question_breakdowns.append({
                "question_index": index + 1,
                "question": question,
                "answer_length": len(answer.split()),
                "scores": {
                    "relevance": relevance,
                    "communication": comm_result["overall_score"],
                    "confidence": conf_result["behavioral_confidence_score"]
                },
                "insights": {
                    "communication_issues": comm_result["insights"]["filler_words_detected"],
                    "confidence_issues": conf_result["insights"]["stress_indicators"]
                }
            })

        # Average out scores across interview length (Normalization)
        avg_relevance = total_relevance / num_questions
        avg_communication = total_communication / num_questions
        avg_confidence = total_confidence / num_questions

        # Interview-level metric
        consistency_result = self.analyze_consistency(all_answers)
        avg_consistency = consistency_result["score"]

        # Calculate Final HR Score
        final_score = (
            avg_relevance * self.weights["answer_relevance"] +
            avg_communication * self.weights["communication"] +
            avg_confidence * self.weights["confidence"] +
            avg_consistency * self.weights["consistency"]
        )

        return {
            "final_hr_score": round(final_score, 2),
            "score_breakdown": {
                "answer_relevance": round(avg_relevance, 2),
                "communication": round(avg_communication, 2),
                "confidence": round(avg_confidence, 2),
                "consistency": round(avg_consistency, 2)
            },
            "weights_used": self.weights,
            "consistency_details": consistency_result["details"],
            "question_level_analysis": question_breakdowns
        }

if __name__ == "__main__":
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
    result = scorer.evaluate_interview(sample_qa)
    print(json.dumps(result, indent=4))
