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
