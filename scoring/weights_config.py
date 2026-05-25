import os
import json
import glob
import re

WEIGHTS_CONFIG = {
    "default": {
        "skill": 0.4,
        "experience": 0.2,
        "education": 0.1,
        "semantic": 0.3
    },
    "hr_interview": {
        "answer_relevance": 0.35,
        "communication": 0.25,
        "confidence": 0.20,
        "consistency": 0.20
    },
    "hr_interview_with_behavioral": {
        "answer_relevance": 0.30,
        "communication": 0.20,
        "confidence": 0.15,
        "consistency": 0.15,
        "behavioral_ai": 0.20
    },
    "Clinical": {
        "skill": 0.4,
        "experience": 0.1,
        "education": 0.1,
        "semantic": 0.4
    },
    "Industry": {
        "skill": 0.3,
        "experience": 0.4,
        "education": 0.1,
        "semantic": 0.2
    },
    "Research & Development": {
        "skill": 0.4,
        "experience": 0.1,
        "education": 0.3,
        "semantic": 0.2
    },
    "Academics": {
        "skill": 0.3,
        "experience": 0.2,
        "education": 0.3,
        "semantic": 0.2
    }
}

UNIFIED_WEIGHTS_CONFIG = {
    "default": {
        "ats_score": 0.20,
        "screening_score": 0.20,
        "technical_interview_score": 0.20,
        "machine_test_score": 0.20,
        "hr_interview_score": 0.20
    },
    "technical": {
        "ats_score": 0.15,
        "screening_score": 0.15,
        "technical_interview_score": 0.25,
        "machine_test_score": 0.35,
        "hr_interview_score": 0.10
    },
    "leadership": {
        "ats_score": 0.20,
        "screening_score": 0.15,
        "technical_interview_score": 0.15,
        "machine_test_score": 0.20,
        "hr_interview_score": 0.30
    },
    "customer_facing": {
        "ats_score": 0.15,
        "screening_score": 0.20,
        "technical_interview_score": 0.10,
        "machine_test_score": 0.15,
        "hr_interview_score": 0.40
    },
    "entry_level": {
        "ats_score": 0.20,
        "screening_score": 0.25,
        "technical_interview_score": 0.20,
        "machine_test_score": 0.20,
        "hr_interview_score": 0.15
    }
}

def get_weights_for_category(category):
    if not category:
        return WEIGHTS_CONFIG["default"]
    
    # Attempt substring matching for categories
    if "research" in category.lower() or "development" in category.lower():
        return WEIGHTS_CONFIG["Research & Development"]
    if "clinical" in category.lower() or "hospital" in category.lower():
        return WEIGHTS_CONFIG["Clinical"]
    if "industry" in category.lower() or "manufacturing" in category.lower() or "qa" in category.lower() or "qc" in category.lower():
        return WEIGHTS_CONFIG["Industry"]
    if "academic" in category.lower() or "professor" in category.lower():
        return WEIGHTS_CONFIG["Academics"]
        
    return WEIGHTS_CONFIG.get(category, WEIGHTS_CONFIG["default"])
