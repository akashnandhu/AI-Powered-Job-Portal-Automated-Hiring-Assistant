import random
from typing import Dict, List, Optional, Tuple
from .hr_interview import ResponseCapture, InterviewState

class FollowUpEngine:
    def __init__(self, max_follow_ups_per_question: int = 2):
        self.max_follow_ups_per_question = max_follow_ups_per_question

    def evaluate_response(self, response: ResponseCapture, expected_intents: List[str]) -> Tuple[float, List[str]]:
        """
        Simulates evaluating a response to determine its completeness and missing intents.
        In a real scenario, an LLM would extract intents and score completeness.
        """
        words = response.candidate_transcript.split()
        
        # Robust mock: completeness factors in both length and intent coverage.
        base_completeness = min(1.0, len(words) / 40.0)
        
        found_intents = getattr(response, "extracted_intents", [])
        if not found_intents and expected_intents:
             # Mock finding some intents if the answer is decently long
             if len(words) > 15:
                 found_intents = expected_intents[:1]
        
        intent_coverage = len(found_intents) / len(expected_intents) if expected_intents else 1.0
        
        # Combined completeness score
        completeness = (base_completeness * 0.4) + (intent_coverage * 0.6)
        
        missing_intents = [intent for intent in expected_intents if intent not in found_intents]
        
        response.extracted_intents = found_intents
        response.completeness_score = round(completeness, 2)
        
        return completeness, missing_intents

    def determine_follow_up_type(self, completeness: float, missing_intents: List[str]) -> str:
        """
        Decision tree logic to determine the type of follow-up required.
        """
        if completeness < 0.4:
            return "clarification"
        elif missing_intents and len(missing_intents) > 0:
            return "example_based"
        elif completeness >= 0.4 and completeness < 0.7:
            return "deepening_probe"
        else:
            return "scenario_based"

    def generate_follow_up(self, response: ResponseCapture, base_question: Dict, state: InterviewState) -> Optional[str]:
        """
        Generates the actual follow-up question string based on the response analysis.
        Returns None if no follow-up is needed or if max follow-ups reached.
        """
        # 1. Prevent repetitive questioning
        follow_up_count = sum(1 for q_id in state.asked_questions if q_id.startswith(f"FU_{base_question['id']}"))
        
        if follow_up_count >= self.max_follow_ups_per_question:
            return None # Limit reached, move on
            
        if not base_question.get("follow_up_eligible", True):
            return None # Not eligible
            
        # 2. Evaluate
        completeness, missing_intents = self.evaluate_response(response, base_question.get("expected_intents", []))
        
        # 3. Decision Tree mapping
        follow_up_type = self.determine_follow_up_type(completeness, missing_intents)
        
        # 4. State tracking - record the follow up intent to prevent same angle
        new_fu_id = f"FU_{base_question['id']}_{follow_up_count + 1}"
        state.asked_questions.append(new_fu_id)
        
        # 5. Generate prompt based on type
        return self._build_prompt_string(follow_up_type, missing_intents)

    def _build_prompt_string(self, prompt_type: str, missing_intents: List[str]) -> str:
        """
        Constructs the textual follow up. In production, this might trigger an LLM prompt.
        """
        if prompt_type == "clarification":
            return "Could you elaborate a bit more on that? I'd love to hear some additional details."
        elif prompt_type == "example_based":
            intent_target = missing_intents[0] if missing_intents else "your previous point"
            intent_target = intent_target.replace("_", " ")
            return f"That's interesting. Can you provide a specific real-world example related to {intent_target}?"
        elif prompt_type == "deepening_probe":
            return "Why did you choose to take that specific approach over other potential options?"
        elif prompt_type == "scenario_based":
            return "That sounds like a solid approach. How would your strategy change if you had half the time to complete it?"
        
        return "Can you tell me more?"
