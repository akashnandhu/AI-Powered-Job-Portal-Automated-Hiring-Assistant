import re
import logging
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)



class SentimentAnalysis(BaseModel):
    """Sentiment scoring module."""
    score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score from -1.0 (Negative) to 1.0 (Positive)")
    label: Literal["positive", "neutral", "negative"] = Field(..., description="Categorical sentiment label")
    positive_words_detected: int
    negative_words_detected: int

class ConfidenceAnalysis(BaseModel):
    """Confidence analysis logic."""
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence level (0 to 1)")
    hesitation_count: int = Field(..., description="Number of hesitation fillers (um, uh, like)")
    uncertainty_count: int = Field(..., description="Number of uncertain phrases (maybe, I guess, not sure)")
    contradiction_detected: bool = Field(..., description="True if potential contradictions are found")

class BehavioralIndicators(BaseModel):
    """Behavioral indicators metrics."""
    response_length_words: int
    estimated_pace_wpm: Optional[float] = Field(None, description="Words per minute (if duration is provided)")
    communication_style: List[str] = Field(..., description="Tags like 'Concise', 'Rambling', 'Hesitant', 'Confident'")
    
class BehavioralReport(BaseModel):
    """Behavioral indicators report."""
    response_text: str
    sentiment: SentimentAnalysis
    confidence: ConfidenceAnalysis
    indicators: BehavioralIndicators
    overall_assessment: str = Field(..., description="Summary of the candidate's communication quality")

# -------------------------------------------------------------------
# Analysis Engine
# -------------------------------------------------------------------

class BehavioralAnalyzer:
    """
    Analyzes communication quality and behavioral indicators.
    """
    def __init__(self):
        # Lexicons for heuristic analysis
        self.hesitation_fillers = ["um", "uh", "like", "you know", "basically", "kinda", "sorta", "well", "hmm"]
        self.uncertainty_phrases = ["maybe", "not sure", "i guess", "probably", "might", "could be", "i think", "possibly"]
        self.positive_words = ["excellent", "great", "good", "success", "achieve", "proud", "glad", "excited", "love", "passion", "innovative", "lead"]
        self.negative_words = ["bad", "terrible", "fail", "hate", "worst", "unfortunately", "sad", "disappointed", "struggle", "difficult", "hard"]
        self.contradiction_pairs = [("yes", "no"), ("always", "never"), ("love", "hate")]

    def _analyze_sentiment(self, text_lower: str) -> SentimentAnalysis:
        words = re.findall(r'\b\w+\b', text_lower)
        
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        # Simple sentiment calculation
        total_sentiment_words = pos_count + neg_count
        if total_sentiment_words == 0:
            score = 0.0
            label = "neutral"
        else:
            score = (pos_count - neg_count) / max(total_sentiment_words, 1) # Range [-1.0, 1.0]
            
            if score > 0.2:
                label = "positive"
            elif score < -0.2:
                label = "negative"
            else:
                label = "neutral"
                
        return SentimentAnalysis(
            score=round(score, 2),
            label=label,
            positive_words_detected=pos_count,
            negative_words_detected=neg_count
        )

    def _analyze_confidence(self, text_lower: str) -> ConfidenceAnalysis:
        # Detect hesitations
        hesitation_count = sum(text_lower.count(filler) for filler in self.hesitation_fillers)
        
        # Detect uncertainty
        uncertainty_count = sum(text_lower.count(phrase) for phrase in self.uncertainty_phrases)
        
        # Detect contradictions (naive approach in the same sentence/response)
        words = set(re.findall(r'\b\w+\b', text_lower))
        contradiction = False
        for p1, p2 in self.contradiction_pairs:
            if p1 in words and p2 in words:
                contradiction = True
                break
                
        # Base confidence is 1.0, penalized by hesitations, uncertainty, and contradictions
        penalty = (hesitation_count * 0.05) + (uncertainty_count * 0.1) + (0.2 if contradiction else 0.0)
        confidence_score = max(0.0, 1.0 - penalty)
        
        return ConfidenceAnalysis(
            confidence_score=round(confidence_score, 2),
            hesitation_count=hesitation_count,
            uncertainty_count=uncertainty_count,
            contradiction_detected=contradiction
        )

    def _determine_indicators(self, words_count: int, duration_seconds: Optional[float], confidence: ConfidenceAnalysis) -> BehavioralIndicators:
        pace_wpm = None
        style_tags = []
        
        if duration_seconds and duration_seconds > 0:
            pace_wpm = (words_count / duration_seconds) * 60
            
            # Normal speaking rate is ~130-160 wpm
            if pace_wpm > 170:
                style_tags.append("Fast-paced")
            elif pace_wpm < 110:
                style_tags.append("Slow-paced")
                
        if words_count < 10:
            style_tags.append("Terse")
        elif words_count > 100:
            style_tags.append("Detailed")
            
        if confidence.hesitation_count > 3:
            style_tags.append("Hesitant")
            
        if confidence.confidence_score >= 0.8:
            style_tags.append("Confident")
        elif confidence.confidence_score < 0.5:
            style_tags.append("Unsure")
            
        if not style_tags:
            style_tags.append("Standard")
            
        return BehavioralIndicators(
            response_length_words=words_count,
            estimated_pace_wpm=round(pace_wpm, 1) if pace_wpm else None,
            communication_style=style_tags
        )

    def analyze_response(self, text: str, duration_seconds: Optional[float] = None) -> BehavioralReport:
        """
        Runs the full behavioral and communication analysis on a given response.
        """
        text_lower = text.lower()
        words = text.split()
        words_count = len(words)
        
        sentiment = self._analyze_sentiment(text_lower)
        confidence = self._analyze_confidence(text_lower)
        indicators = self._determine_indicators(words_count, duration_seconds, confidence)
        
        # Generate an overall assessment summary
        assessment = f"The candidate communicated with a {sentiment.label} tone. "
        if confidence.confidence_score >= 0.8:
            assessment += "They appeared highly confident with minimal hesitation. "
        elif confidence.confidence_score < 0.5:
            assessment += "There were notable signs of uncertainty and hesitation. "
        else:
            assessment += "Confidence was moderate, with some filler usage. "
            
        if "Fast-paced" in indicators.communication_style:
            assessment += "The speech pace was faster than average."
        elif "Slow-paced" in indicators.communication_style:
            assessment += "The speech pace was slow and deliberate."
            
        return BehavioralReport(
            response_text=text,
            sentiment=sentiment,
            confidence=confidence,
            indicators=indicators,
            overall_assessment=assessment.strip()
        )
