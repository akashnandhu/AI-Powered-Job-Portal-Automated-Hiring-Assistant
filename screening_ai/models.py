from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ScreeningQuestion(BaseModel):
    """
    AI conversation-ready question object for HR screening calls.
    """
    question_id: str = Field(..., description="Unique identifier for the question")
    category: Literal[
        "Introduction",
        "Education",
        "Experience",
        "Skills",
        "Location",
        "Salary",
        "Notice period"
    ] = Field(..., description="Category of the screening question")
    template: str = Field(..., description="The actual question text, with optional format variables")
    expected_answer_type: Literal["boolean", "numeric", "text", "date", "list"] = Field(
        ..., description="The data type expected as the answer"
    )
    is_mandatory: bool = Field(..., description="Whether this question is mandatory to ask")
    scoring_importance: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Importance of the question for candidate evaluation"
    )
    applicable_roles: List[str] = Field(
        default=[], description="List of roles this question applies to. If empty, implies all roles."
    )
    intent: Optional[str] = Field(
        default=None, description="The AI intent behind the question, useful for LLM context"
    )


class QuestionBank(BaseModel):
    """
    Container for the screening question dataset.
    """
    questions: List[ScreeningQuestion] = Field(..., description="List of screening questions")

    def get_mandatory_questions(self) -> List[ScreeningQuestion]:
        return [q for q in self.questions if q.is_mandatory]

    def get_questions_by_category(self, category: str) -> List[ScreeningQuestion]:
        return [q for q in self.questions if q.category == category]
    
    def get_questions_for_role(self, role: str) -> List[ScreeningQuestion]:
        """
        Returns questions that apply broadly (empty list) or explicitly to the role.
        """
        return [q for q in self.questions if not q.applicable_roles or role in q.applicable_roles]

