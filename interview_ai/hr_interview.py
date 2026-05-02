import json
from typing import List, Dict, Optional
import os

class ResponseCapture:
    def __init__(self, question_id: str, candidate_transcript: str):
        self.question_id = question_id
        self.candidate_transcript = candidate_transcript
        self.extracted_intents: List[str] = []
        self.sentiment: str = "neutral"
        self.completeness_score: float = 0.0

    def to_dict(self):
        return {
            "question_id": self.question_id,
            "candidate_transcript": self.candidate_transcript,
            "extracted_intents": self.extracted_intents,
            "sentiment": self.sentiment,
            "completeness_score": self.completeness_score
        }

class InterviewState:
    def __init__(self, session_id: str, candidate_id: str):
        self.session_id = session_id
        self.candidate_id = candidate_id
        self.current_phase: str = "introduction"
        self.current_question_id: Optional[str] = None
        self.asked_questions: List[str] = []
        self.responses: List[ResponseCapture] = []
        self.follow_up_eligibility: bool = False
        self.turn_count: int = 0
        
        self.candidate_experience: str = "fresher" # default
        self.candidate_role: str = "non-technical" # default

    def set_candidate_profile(self, experience: str, role: str):
        self.candidate_experience = experience
        self.candidate_role = role

    def add_response(self, response: ResponseCapture):
        self.responses.append(response)
        
    def advance_phase(self, new_phase: str):
        self.current_phase = new_phase

class RoleBasedQuestionGenerator:
    def __init__(self, question_bank_path: str):
        self.question_bank: List[Dict] = []
        self._load_question_bank(question_bank_path)

    def _load_question_bank(self, filepath: str):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.question_bank = data.get("questions", [])

    def get_next_question(self, state: InterviewState, category: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieves the next appropriate question based on the candidate's experience,
        role type, and the requested category. Avoids asking the same question twice.
        """
        for q in self.question_bank:
            if q["id"] in state.asked_questions:
                continue
                
            if category and q["category"] != category:
                continue
                
            if state.candidate_experience not in q["target_experience"]:
                continue
                
            if state.candidate_role not in q["target_role"]:
                continue
                
            # Found a match
            return q
            
        return None

# Example usage/tester
if __name__ == "__main__":
    bank_path = os.path.join(os.path.dirname(__file__), "hr_question_bank.json")
    generator = RoleBasedQuestionGenerator(bank_path)
    
    state = InterviewState("session_001", "cand_123")
    state.set_candidate_profile("experienced", "technical")
    
    # Phase 1: Introduction
    q1 = generator.get_next_question(state, category="Self-introduction")
    if q1:
        print(f"[{state.current_phase.upper()}] Q: {q1['text']}")
        state.asked_questions.append(q1["id"])
        
    # Phase 2: Core HR
    state.advance_phase("core_hr")
    q2 = generator.get_next_question(state, category="Teamwork & culture fit")
    if q2:
        print(f"[{state.current_phase.upper()}] Q: {q2['text']}")
        state.asked_questions.append(q2["id"])

    # Phase 3: Role-based
    state.advance_phase("role_based_evaluation")
    q3 = generator.get_next_question(state, category="Role-based evaluation")
    if q3:
        print(f"[{state.current_phase.upper()}] Q: {q3['text']}")
        state.asked_questions.append(q3["id"])
