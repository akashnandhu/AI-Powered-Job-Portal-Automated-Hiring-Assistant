import re
import json
import logging
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Deliverable 3: Structured Answer Format
# -------------------------------------------------------------------
class ExtractedEntities(BaseModel):
    """
    Semantic object capturing key data points extracted from the candidate's answer.
    """
    skills: List[str] = Field(default_factory=list, description="List of skills extracted from the answer")
    experience_years: Optional[float] = Field(None, description="Years of experience extracted")
    availability: Optional[str] = Field(None, description="Notice period or start date mentioned")
    salary_expectation: Optional[str] = Field(None, description="Expected compensation")

class StructuredAnswer(BaseModel):
    """
    The final structured response that makes the candidate's answer understandable by downstream AI logic.
    """
    raw_transcript: str = Field(..., description="Original raw transcript")
    cleaned_transcript: str = Field(..., description="Cleaned transcript")
    intent: Literal["direct_answer", "clarification_needed", "off_topic", "refusal_to_answer", "partial_answer", "unknown"] = Field(..., description="Detected intent of the candidate's response")
    is_off_topic: bool = Field(..., description="True if response is totally unrelated to the question")
    is_vague_or_missing: bool = Field(..., description="True if the response lacks concrete details or is missing")
    missing_answer: bool = Field(False, description="True if the response is completely empty or just silence")
    language_mixed: bool = Field(False, description="True if the response contains multiple languages or non-English")
    confusion_detected: bool = Field(False, description="True if the candidate expressed confusion")
    repeated_detected: bool = Field(False, description="True if the candidate repeated themselves")
    extracted_data: ExtractedEntities = Field(..., description="Structured entities extracted from the answer")
    confidence_score: float = Field(..., description="Confidence score of the extraction and classification")

# -------------------------------------------------------------------
# Deliverable 1 & 2: Answer Understanding Engine & Intent Classifier
# -------------------------------------------------------------------
class AnswerUnderstandingEngine:
    """
    Engine to interpret candidate answers, extract structured entities,
    and classify intent and relevance using heuristic NLP patterns.
    (In a production system, this module would wrap an LLM service).
    """
    def __init__(self):
        # Intent classification keywords
        self.off_topic_keywords = ["weather", "sports", "politics", "movie", "recipe", "baseball", "restaurant"]
        self.refusal_keywords = ["i don't know", "cannot answer", "skip this", "pass", "no idea", "i'm not sure", "skip"]
        self.clarification_keywords = ["can you repeat", "what do you mean", "could you clarify", "not sure i understand", "pardon", "confused", "i didn't catch that"]
        self.vague_keywords = ["some stuff", "things", "various things", "a little bit", "maybe", "depends", "probably"]
        self.repeated_keywords = ["as i said", "like i mentioned before", "i already told you", "again"]
        
    def classify_intent(self, text: str) -> Literal["direct_answer", "clarification_needed", "off_topic", "refusal_to_answer", "partial_answer", "unknown"]:
        """
        Classifies the core intent of the response.
        """
        text_lower = text.lower()
        
        # 1. Clarification Needed
        if any(k in text_lower for k in self.clarification_keywords) or (text_lower.endswith('?') and len(text_lower.split()) < 10):
            return "clarification_needed"
            
        # 2. Refusal
        if any(k in text_lower for k in self.refusal_keywords):
            return "refusal_to_answer"
            
        # 3. Off-Topic
        if any(k in text_lower for k in self.off_topic_keywords):
            return "off_topic"
            
        # 4. Partial Answer
        words = text_lower.split()
        if 0 < len(words) < 4:
            return "partial_answer"
            
        return "direct_answer"

    def detect_off_topic(self, text: str, question_category: str) -> bool:
        """
        Detects if the response is completely off-topic relative to the context.
        """
        intent = self.classify_intent(text)
        if intent == "off_topic":
            return True
            
        return False
        
    def detect_language_mixing(self, text: str) -> bool:
        """
        Basic heuristic to detect non-English words or language mixing.
        In production, this uses a language identification model (e.g., fastText or CLD3).
        """
        if not text.strip():
             return False
        # Simulating detection by looking for specific non-English markers or generic logic
        foreign_words = ["gracias", "bonjour", "hola", "merci", "namaste", "danke"]
        return any(word in text.lower() for word in foreign_words)

    def check_vague_or_missing(self, text: str) -> bool:
        """
        Identifies missing or overly vague answers.
        """
        if not text.strip():
            return True
        
        text_lower = text.lower()
        if any(k in text_lower for k in self.vague_keywords) and len(text.split()) < 25:
            return True
            
        return False

    def extract_entities(self, text: str) -> ExtractedEntities:
        """
        Extracts relevant fields: skills, experience, availability, salary.
        """
        entities = ExtractedEntities()
        text_lower = text.lower()
        
        # 1. Experience Extraction
        # Matches: "5 years of experience", "2.5 yrs experience", "10 years"
        exp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years|yrs?)(?:\s*of)?\s*(?:experience|working)?', text_lower)
        if exp_match:
            entities.experience_years = float(exp_match.group(1))
            
        # 2. Salary Extraction
        # Matches: "$100k", "120K", "$150,000"
        salary_match = re.search(r'(\$?\d{2,3}[kK]|\$?\d{1,3}(?:,\d{3})+)', text_lower)
        if salary_match:
            entities.salary_expectation = salary_match.group(1).upper()
            
        # 3. Availability Extraction
        # Matches: "immediately", "2 weeks notice", "30 days"
        avail_match = re.search(r'(immediate(?:ly)?|\d+\s*(?:days|weeks|months)\s*(?:notice)?)', text_lower)
        if avail_match:
            entities.availability = avail_match.group(1)
            
        # 4. Skills Extraction
        # Hardcoded taxonomy for demonstration purposes. In production, this matches a DB dictionary or uses NLP.
        known_skills = ['python', 'java', 'aws', 'sql', 'react', 'node.js', 'docker', 'kubernetes', 'machine learning', 'c++']
        extracted_skills = []
        for skill in known_skills:
            # Word boundary search to prevent matching "javascript" for "java"
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                # Standardize output casing
                extracted_skills.append(skill.title() if len(skill) > 3 else skill.upper())
        
        if extracted_skills:
            entities.skills = extracted_skills
            
        return entities

    def process_answer(self, raw_transcript: str, cleaned_transcript: str, question_category: str = "General") -> StructuredAnswer:
        """
        Main pipeline to process a transcript and return a structured semantic object.
        """
        # Run classifiers
        intent = self.classify_intent(cleaned_transcript)
        is_off_topic = self.detect_off_topic(cleaned_transcript, question_category)
        is_vague = self.check_vague_or_missing(cleaned_transcript)
        missing_answer = not cleaned_transcript.strip()
        language_mixed = self.detect_language_mixing(cleaned_transcript)
        confusion_detected = intent == "clarification_needed"
        
        text_lower = cleaned_transcript.lower()
        repeated_detected = any(k in text_lower for k in self.repeated_keywords)
        
        # Run extraction
        entities = self.extract_entities(cleaned_transcript)
        
        # Calculate confidence heuristic
        confidence = 0.95
        if is_vague or is_off_topic:
            confidence -= 0.3
        if intent != "direct_answer":
            confidence -= 0.2
        if intent == "partial_answer":
            confidence -= 0.15
            
        return StructuredAnswer(
            raw_transcript=raw_transcript,
            cleaned_transcript=cleaned_transcript,
            intent=intent,
            is_off_topic=is_off_topic,
            is_vague_or_missing=is_vague,
            missing_answer=missing_answer,
            language_mixed=language_mixed,
            confusion_detected=confusion_detected,
            repeated_detected=repeated_detected,
            extracted_data=entities,
            confidence_score=round(max(0.0, min(1.0, confidence)), 2)
        )
