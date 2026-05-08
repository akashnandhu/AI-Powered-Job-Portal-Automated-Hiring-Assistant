import re

class ConfidenceAnalyzer:
    """
    Assesses candidate confidence and emotional signals based on text transcripts.
    Detects hesitation, sentiment, contradictions, and stress indicators to generate a behavioral confidence score.
    """
    def __init__(self):
        self.uncertainty_phrases = {
            "i guess", "maybe", "i'm not sure", "im not sure", "perhaps", 
            "probably", "might be", "kind of", "sort of", "i suppose", 
            "to some extent", "i think", "possibly", "i don't know"
        }
        
        # Simple sentiment lexicons
        self.positive_words = {
            "confident", "successful", "achieved", "solved", "managed", "led",
            "great", "excellent", "effective", "improved", "strong", "positive",
            "certain", "absolutely", "definitely", "ensure"
        }
        
        self.negative_words = {
            "failed", "bad", "terrible", "struggled", "unable", "cannot", "hard",
            "difficult", "unfortunately", "worst", "mistake", "wrong"
        }
        
        self.stress_indicators = {
            "nervous", "anxious", "worried", "stressed", "overwhelmed", "panic", "confused"
        }
        
        self.contradiction_phrases = {
            "yes but", "although", "however i didn't", "always except",
            "on the other hand", "but actually", "even though"
        }

    def detect_hesitation(self, text):
        """
        Detects hesitation patterns: long pauses, repeated words, and uncertainty phrases.
        """
        text_lower = text.lower()
        
        # 1. Long pauses (Detecting ellipses or explicit pause markers)
        pause_count = len(re.findall(r'\.\.\.|\[pause\]', text_lower))
        
        # 2. Repeated words (e.g., "I I", "the the")
        repeated_word_pattern = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE)
        repeated_words = len(repeated_word_pattern.findall(text))
        
        # 3. Uncertainty phrases
        uncertainty_count = 0
        found_uncertainties = []
        for phrase in self.uncertainty_phrases:
            count = text_lower.count(phrase)
            if count > 0:
                uncertainty_count += count
                found_uncertainties.append(phrase)
                
        # Total hesitation penalty (lower is better, scaled later)
        hesitation_score = min(1.0, (pause_count * 0.5 + repeated_words * 0.5 + uncertainty_count * 1.0) / 5.0)
        
        return {
            "score": max(0.0, 1.0 - hesitation_score),
            "details": {
                "pauses": pause_count,
                "repeated_words": repeated_words,
                "uncertainty_phrases": found_uncertainties
            }
        }

    def analyze_sentiment(self, text):
        """
        Basic lexical sentiment analysis to determine the underlying emotional tone.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return {"score": 0.5, "sentiment": "neutral"}
            
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        # Calculate a polarity score between -1.0 and +1.0
        total_opinion_words = pos_count + neg_count
        if total_opinion_words == 0:
            polarity = 0.0
        else:
            polarity = (pos_count - neg_count) / total_opinion_words
            
        # Map to 0.0 - 1.0 scale (0.5 is neutral)
        sentiment_score = (polarity + 1.0) / 2.0
        
        sentiment_label = "positive" if polarity > 0.1 else ("negative" if polarity < -0.1 else "neutral")
        
        return {
            "score": sentiment_score,
            "sentiment": sentiment_label,
            "positive_words": pos_count,
            "negative_words": neg_count
        }

    def detect_contradictions(self, text):
        """
        Identifies logical contradictions or extreme backtracking in the response.
        """
        text_lower = text.lower()
        contradiction_count = 0
        found_contradictions = []
        
        for phrase in self.contradiction_phrases:
            count = text_lower.count(phrase)
            if count > 0:
                contradiction_count += count
                found_contradictions.append(phrase)
                
        # High penalty for contradictions
        score = max(0.0, 1.0 - (contradiction_count * 0.4))
        
        return {
            "score": score,
            "details": found_contradictions
        }

    def measure_stress(self, text):
        """
        Measures stress indicators like explicit nervous words or highly fragmented speech.
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return {"score": 1.0, "details": []}
            
        stress_words_found = [w for w in words if w in self.stress_indicators]
        
        # High fragmentation: lots of commas or dashes relative to words can indicate nervous pacing
        punctuation_count = len(re.findall(r'[,;\-]', text))
        fragmentation_ratio = punctuation_count / max(len(words), 1)
        
        # If > 15% punctuation to words, flag as fragmented
        is_fragmented = fragmentation_ratio > 0.15
        
        stress_penalty = (len(stress_words_found) * 0.3) + (0.2 if is_fragmented else 0.0)
        score = max(0.0, 1.0 - stress_penalty)
        
        return {
            "score": score,
            "stress_words": stress_words_found,
            "highly_fragmented": is_fragmented
        }

    def evaluate(self, text):
        """
        Aggregates individual signals into a final Behavioral Confidence Score (0-100).
        """
        hesitation = self.detect_hesitation(text)
        sentiment = self.analyze_sentiment(text)
        contradiction = self.detect_contradictions(text)
        stress = self.measure_stress(text)
        
        # Weighted aggregate for Confidence
        # High confidence = low hesitation + positive sentiment + no contradictions + low stress
        weights = {
            "hesitation": 0.40,
            "sentiment": 0.20,
            "contradiction": 0.20,
            "stress": 0.20
        }
        
        raw_score = (
            hesitation["score"] * weights["hesitation"] +
            sentiment["score"] * weights["sentiment"] +
            contradiction["score"] * weights["contradiction"] +
            stress["score"] * weights["stress"]
        )
        
        # Normalize and map to 0-100
        # A perfectly neutral response without errors gets around 70-80.
        final_confidence_score = round(raw_score * 100, 2)
        
        return {
            "behavioral_confidence_score": final_confidence_score,
            "metrics": {
                "hesitation_score": round(hesitation["score"] * 100, 2),
                "sentiment_score": round(sentiment["score"] * 100, 2),
                "contradiction_score": round(contradiction["score"] * 100, 2),
                "stress_score": round(stress["score"] * 100, 2)
            },
            "insights": {
                "hesitation_details": hesitation["details"],
                "sentiment_label": sentiment["sentiment"],
                "contradictions_found": contradiction["details"],
                "stress_indicators": stress["stress_words"]
            }
        }

if __name__ == "__main__":
    analyzer = ConfidenceAnalyzer()
    sample_text = "I I think... I'm not sure, maybe we could do it. Yes but it failed previously. I was very nervous."
    result = analyzer.evaluate(sample_text)
    import json
    print(json.dumps(result, indent=4))
