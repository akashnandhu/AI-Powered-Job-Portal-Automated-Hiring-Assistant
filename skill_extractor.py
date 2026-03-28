import re
from collections import defaultdict
import logging
from skills_dict import SKILL_CATEGORIES, SYNONYMS, STACKS

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

class SkillExtractor:
    def __init__(self, use_nlp=False):
        self.use_nlp = use_nlp
        self.nlp = None
        
        if self.use_nlp and HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logging.warning("spaCy model 'en_core_web_sm' not found. Ensure you run `python -m spacy download en_core_web_sm`. Falling back to regex rules.")
                self.use_nlp = False
        elif self.use_nlp and not HAS_SPACY:
            logging.warning("spaCy library not installed for NLP enhancement. Continuing with regex rules.")

        self._build_inverted_index()
        
    def _build_inverted_index(self):
        """Builds a flattened mapping of lowercase keywords directly to their canonical naming and category"""
        self.master_dict = {}
        for category, skills in SKILL_CATEGORIES.items():
            for skill in skills:
                self.master_dict[skill.lower()] = {"canonical": skill, "category": category}
                
        for syn, canonical in SYNONYMS.items():
            # Find the true category
            target_category = "technical" # Base default fallback
            for cat, skills in SKILL_CATEGORIES.items():
                if canonical in skills:
                    target_category = cat
                    break
            self.master_dict[syn.lower()] = {"canonical": canonical, "category": target_category}

    def add_skill(self, skill_name, category="technical"):
        """Programmatic injection to rapidly scale the skill vocabulary."""
        self.master_dict[skill_name.lower()] = {"canonical": skill_name, "category": category}

    def _expand_stacks(self, text):
        """Expand tech stack acronyms (e.g. MERN) explicitly into the string match pool."""
        lower_text = text.lower()
        expanded_skills = []
        for stack, skills in STACKS.items():
            if re.search(r'\b' + re.escape(stack) + r'\b', lower_text):
                expanded_skills.extend(skills)
        return expanded_skills

    def extract_skills(self, text):
        """Extract exact mappings and normalize them over the entire provided text scope."""
        results = {
            "technical_skills": set(),
            "non_technical_skills": set(),
            "confidence": {}
        }
        
        if not text:
            return { "technical_skills": [], "non_technical_skills": [], "confidence": {} }
            
        # 1. Expand stack keywords into actual skills
        stack_skills = self._expand_stacks(text)
        for ss in stack_skills:
            category = self.master_dict.get(ss.lower(), {}).get("category", "technical")
            if category == "technical":
                results["technical_skills"].add(ss)
            else:
                results["non_technical_skills"].add(ss)
            results["confidence"][ss] = 0.95 # Explicit stack unpacking yields high confidence
            
        lower_text = text.lower()
        # Sort by length descending to match composite longer strings before short acronyms
        sorted_keywords = sorted(self.master_dict.keys(), key=len, reverse=True)
        
        # 2. Match exact and synonyms safely bypassing case
        for kw in sorted_keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            # To handle spelling variations (very basic leniency on dashes etc)
            pattern_lenient = r'\b' + re.escape(kw).replace(r'\ ', r'[\s\-]?') + r'\b'
            
            matches = re.findall(pattern_lenient, lower_text)
            
            if matches:
                 canonical = self.master_dict[kw]["canonical"]
                 category = self.master_dict[kw]["category"]
                 
                 # Perfect strict match yields higher confidence than lenient regex allowance
                 strict_matches = re.findall(pattern, lower_text)
                 conf = 0.95 if strict_matches else 0.85
                 
                 target_set = results["technical_skills"] if category == "technical" else results["non_technical_skills"]
                 target_set.add(canonical)
                     
                 # Maintain only the highest captured confidence metric
                 if canonical not in results["confidence"] or conf > results["confidence"][canonical]:
                     results["confidence"][canonical] = conf
                     
        # Structure the final output, deduplicated inherently by Sets and alphabetically sorted
        return {
            "technical_skills": sorted(list(results["technical_skills"])),
            "non_technical_skills": sorted(list(results["non_technical_skills"])),
            "confidence": results["confidence"]
        }
