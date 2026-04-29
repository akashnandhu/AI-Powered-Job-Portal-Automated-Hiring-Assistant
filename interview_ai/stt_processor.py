import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class STTService:
    """
    Speech-to-Text integration wrapper.
    In a real-world scenario, this would wrap APIs like OpenAI Whisper, Google Cloud Speech-to-Text,
    or AWS Transcribe.
    """
    def __init__(self, provider: str = "whisper"):
        self.provider = provider
        logger.info(f"Initialized STTService using provider: {self.provider}")

    def transcribe(self, audio_file_path: str) -> Dict:
        """
        Simulates transcription of an audio file, returning segments with timestamps.
        """
        # Mock STT response with segments to simulate silence detection
        return {
            "text": "Uh, I have five years of experience in Python. And, like, I also know... um, React but-",
            "confidence": 0.85,
            "background_noise_level": 0.2, # Simulated noise level (0.0 to 1.0)
            "segments": [
                {"start": 0.0, "end": 2.5, "text": "Uh, I have five years of experience in Python."},
                # Simulated silence of 2.5 seconds here
                {"start": 5.0, "end": 7.0, "text": "And, like, I also know..."},
                # Simulated silence of 1.0 second
                {"start": 8.0, "end": 9.5, "text": "um, React but-"}
            ]
        }

    def detect_silence(self, segments: List[Dict], silence_threshold: float = 2.0) -> List[Dict]:
        """
        Detects periods of silence between speech segments.
        Returns a list of silence events.
        """
        silences = []
        for i in range(1, len(segments)):
            prev_segment = segments[i - 1]
            curr_segment = segments[i]
            gap = curr_segment["start"] - prev_segment["end"]
            
            if gap >= silence_threshold:
                silences.append({
                    "start": prev_segment["end"],
                    "end": curr_segment["start"],
                    "duration": gap
                })
        return silences

class TranscriptNormalizer:
    """
    Transcript normalization module responsible for cleaning and structuring
    raw voice inputs for downstream AI analysis.
    """
    def __init__(self):
        # Common filler words to remove
        self.filler_words = [r'\buh\b', r'\bum\b', r'\blike\b', r'\byou know\b', r'\bso\b', r'\bah\b', r'\ber\b', r'\bhm+\b', r'\buhm\b']
        self.filler_pattern = re.compile(r'\b(?:' + '|'.join([w.replace(r'\b', '') for w in self.filler_words]) + r')\b', re.IGNORECASE)

    def remove_filler_words(self, text: str) -> str:
        """Removes filler words and cleans up resulting duplicate spaces/punctuation."""
        if not text:
            return text
        
        cleaned_text = self.filler_pattern.sub('', text)
        
        # Clean up commas left hanging (e.g. "And, , I")
        cleaned_text = re.sub(r',\s*,', ',', cleaned_text)
        # Clean up orphaned commas like "to, use" or "for, two" when filler was removed between them
        cleaned_text = re.sub(r'\b(to|for|with|of|in|on|at|by|from|about)\s*,', r'\1', cleaned_text, flags=re.IGNORECASE)
        # Clean up spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        # Clean leading commas
        cleaned_text = re.sub(r'^,\s*', '', cleaned_text)
        # Clean up " , " -> " "
        cleaned_text = re.sub(r'\s+,\s+', ' ', cleaned_text)
        
        return cleaned_text

    def handle_interrupted_speech(self, text: str) -> str:
        """
        Handles interrupted speech and partial answers.
        Replaces trailing dashes or hanging conjunctions with ellipses.
        """
        if not text:
            return text
            
        # Replace trailing hyphens/dashes
        text = re.sub(r'[-–—]+\s*$', '...', text)
        
        # Replace trailing conjunctions or prepositions with ellipsis
        hanging_words_pattern = r'\b(and|but|or|so|because|with|for|well)\s*[,]*\s*$'
        if re.search(hanging_words_pattern, text, re.IGNORECASE):
            text = re.sub(hanging_words_pattern, r'\1...', text, flags=re.IGNORECASE)
            
        return text

    def correct_punctuation(self, text: str) -> str:
        """Corrects basic punctuation anomalies."""
        if not text:
            return text
            
        # Remove space before punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        # Ensure space after punctuation (unless it's part of an ellipsis or number)
        text = re.sub(r'([.,!?])(?=[a-zA-Z])', r'\1 ', text)
        
        # Deduplicate periods (but preserve ellipses)
        text = re.sub(r'(?<!\.)\.\.(?!\.)', '.', text)
        
        # Add trailing period if missing and not ending in ellipsis, ?, or !
        if text and text[-1] not in ['.', '!', '?', '-'] and not text.endswith('...'):
            text += '.'
            
        return text

    def normalize_case(self, text: str) -> str:
        """
        Normalizes capitalization, ensuring sentences start with a capital letter.
        """
        if not text:
            return text
            
        # Split by sentence boundaries (period, exclamation, question mark followed by space)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        capitalized_sentences = []
        for s in sentences:
            if s:
                # Capitalize first letter while preserving the rest
                capitalized_sentences.append(s[0].upper() + s[1:])
                
        return ' '.join(capitalized_sentences)

    def process(self, raw_transcript: str) -> str:
        """
        Execute the full cleaning and normalization pipeline.
        """
        text = raw_transcript
        
        # 1. Interrupted speech detection (best done on raw text first to capture trailing dashes)
        text = self.handle_interrupted_speech(text)
        
        # 2. Remove filler words
        text = self.remove_filler_words(text)
        
        # 3. Punctuation correction
        text = self.correct_punctuation(text)
        
        # 4. Case normalization
        text = self.normalize_case(text)
        
        # 5. Final cleanup of any weird artifacts (e.g., " .")
        text = text.replace(' .', '.')
        
        return text

class CleanTranscriptProcessor:
    """
    Orchestrates the STT and Normalization pipeline.
    """
    def __init__(self, stt_provider: str = "whisper"):
        self.stt_service = STTService(provider=stt_provider)
        self.normalizer = TranscriptNormalizer()

    def process_audio(self, audio_file_path: str) -> Dict:
        """
        Full pipeline: Audio -> Raw Transcript -> Clean Transcript
        """
        stt_result = self.stt_service.transcribe(audio_file_path)
        raw_text = stt_result["text"]
        segments = stt_result.get("segments", [])
        
        silences = self.stt_service.detect_silence(segments)
        clean_text = self.normalizer.process(raw_text)
        
        # Audio Quality heuristics
        noise_level = stt_result.get("background_noise_level", 0.0)
        confidence = stt_result.get("confidence", 1.0)
        
        poor_audio = confidence < 0.6
        high_background_noise = noise_level > 0.7
        
        return {
            "raw_transcript": raw_text,
            "normalized_transcript": clean_text,
            "silences_detected": silences,
            "segments": segments,
            "poor_audio": poor_audio,
            "high_background_noise": high_background_noise
        }
