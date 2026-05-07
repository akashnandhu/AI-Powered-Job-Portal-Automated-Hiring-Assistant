import re
import math

class CommunicationScorer:
    """
    Evaluates candidate communication skills objectively based on text transcripts.
    Metrics: Fluency, Grammar, Vocabulary, Clarity, Fillers, and Structure.
    """
    def __init__(self):
        self.filler_words = {"um", "uh", "like", "you know", "actually", "basically", "literally", "right", "so", "well", "kinda", "sorta"}
        
    def analyze_fluency(self, text):
        """Measures sentence continuity and length."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0.0
            
        avg_words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Ideal avg words per sentence around 10-25
        if 10 <= avg_words_per_sentence <= 25:
            fluency_score = 1.0
        else:
            # Penalty for being outside the ideal range
            fluency_score = max(0.0, 1.0 - abs(avg_words_per_sentence - 17.5) / 17.5)
            
        return fluency_score
        
    def analyze_grammar_quality(self, text):
        """Mock grammar score based on heuristic rules like capitalization and repeated words."""
        words = text.split()
        if not words: 
            return 0.0
        
        errors = 0
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Penalize sentences that don't start with a capital letter
        for s in sentences:
            if s and not s[0].isupper():
                errors += 1
                
        # Detect repeated words (e.g., "the the")
        repeated_word_pattern = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE)
        errors += len(repeated_word_pattern.findall(text))
        
        error_rate = errors / max(len(sentences), 1)
        grammar_score = max(0.0, 1.0 - (error_rate * 0.2))
        return grammar_score
        
    def analyze_vocabulary_range(self, text):
        """Measures Type-Token Ratio (unique words / total words)."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words: 
            return 0.0
        
        unique_words = set(words)
        type_token_ratio = len(unique_words) / len(words)
        
        # Typical TTR is around 0.4 to 0.6 for spoken text
        vocab_score = min(1.0, type_token_ratio / 0.5)
        return vocab_score
        
    def analyze_clarity(self, text):
        """Measures clarity using a proxy of Automated Readability Index (ARI)."""
        words = len(re.findall(r'\b\w+\b', text))
        sentences = max(1, len(re.split(r'[.!?]+', text)) - 1)
        characters = len(re.sub(r'\s+', '', text))
        
        if words == 0: 
            return 0.0
        
        ari = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
        
        # Ideal ARI for clear spoken explanation is around 5 to 12
        if 5 <= ari <= 12:
            clarity_score = 1.0
        else:
            clarity_score = max(0.0, 1.0 - abs(ari - 8.5) / 10.0)
            
        return clarity_score

    def detect_filler_words(self, text):
        """Detects and penalizes common filler words."""
        text_lower = text.lower()
        total_words = len(re.findall(r'\b\w+\b', text_lower))
        if total_words == 0: 
            return 0.0, []
        
        found_fillers = []
        for filler in self.filler_words:
            # Handle multi-word fillers like "you know"
            count = len(re.findall(r'\b' + filler + r'\b', text_lower))
            if count > 0:
                found_fillers.extend([filler] * count)
                
        filler_ratio = len(found_fillers) / total_words
        # Penalty increases as ratio goes up, max penalty if > 10% fillers
        filler_score = max(0.0, 1.0 - (filler_ratio / 0.1))
        
        return filler_score, found_fillers
        
    def measure_answer_structure(self, text):
        """Checks for logical transition words indicating good structure."""
        structural_markers = [
            "first", "second", "third", "finally", "however", "therefore", 
            "in conclusion", "to summarize", "for example", "such as", 
            "on the other hand", "because", "since", "furthermore"
        ]
        text_lower = text.lower()
        
        markers_found = sum(1 for marker in structural_markers if marker in text_lower)
        
        # Expect at least 2 markers for a well-structured answer
        structure_score = min(1.0, markers_found / 2.0) 
        return structure_score
        
    def evaluate(self, text):
        """Returns the final communication score and breakdowns."""
        fluency = self.analyze_fluency(text)
        grammar = self.analyze_grammar_quality(text)
        vocabulary = self.analyze_vocabulary_range(text)
        clarity = self.analyze_clarity(text)
        filler_score, fillers = self.detect_filler_words(text)
        structure = self.measure_answer_structure(text)
        
        # Weights for the final score
        weights = {
            "fluency": 0.20,
            "grammar": 0.15,
            "vocabulary": 0.15,
            "clarity": 0.20,
            "fillers": 0.15,
            "structure": 0.15
        }
        
        raw_score = (
            fluency * weights["fluency"] +
            grammar * weights["grammar"] +
            vocabulary * weights["vocabulary"] +
            clarity * weights["clarity"] +
            filler_score * weights["fillers"] +
            structure * weights["structure"]
        )
        
        # Bias Reduction / Normalization: 
        # Map 0-1.0 to a 40-100 scale. Ensures baseline effort receives partial score.
        normalized_score = 40 + (raw_score * 60)
        
        return {
            "overall_score": round(normalized_score, 2),
            "metrics": {
                "fluency": round(fluency * 100, 2),
                "grammar": round(grammar * 100, 2),
                "vocabulary": round(vocabulary * 100, 2),
                "clarity": round(clarity * 100, 2),
                "filler_score": round(filler_score * 100, 2),
                "structure": round(structure * 100, 2)
            },
            "insights": {
                "filler_words_detected": fillers,
                "total_fillers": len(fillers),
                "raw_score": round(raw_score, 3)
            }
        }

if __name__ == "__main__":
    # Sample Test
    scorer = CommunicationScorer()
    sample_text = "Well, I think that literally, basically, the system works because it has a lot of features. First, it does AI screening. Second, it does scoring. Um, it is a good system."
    result = scorer.evaluate(sample_text)
    import json
    print(json.dumps(result, indent=4))
