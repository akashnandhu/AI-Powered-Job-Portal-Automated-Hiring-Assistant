import os
import sys
import json
import logging
from skill_extractor import SkillExtractor
from section_classifier import ResumeSectionClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from config import CANDIDATE_ID



logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_extraction():
    # Directories
    processed_dir = os.path.join("data", "processed")
    reports_dir = "reports"
    
    # Ensure reports directory exists
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        logging.info(f"Created directory: {reports_dir}")
        
    if not os.path.exists(processed_dir):
        logging.error(f"Error: {processed_dir} directory not found.")
        return

    # Instantiate modular components
    classifier = ResumeSectionClassifier()
    extractor = SkillExtractor(use_nlp=False) 
    
    filename = f"{CANDIDATE_ID}_cleaned.txt"
    filepath = os.path.join(processed_dir, filename)
    
    if not os.path.exists(filepath):
        logging.error(f"Error: {filepath} not found. Please run main.py first.")
        return
        
    resume_name = CANDIDATE_ID
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    logging.info(f"\n{'='*60}")
    logging.info(f"--- Extracting Skills for: {filename} ---")
    logging.info(f"{'='*60}")
    
    # Step 1: Use day 8 section classifier logic
    sections = classifier.classify_sections(text)
    
    # Step 2: Extract skills globally
    skills_payload = extractor.extract_skills(text)
    
    # Step 3: Extract skills strictly from the 'skills' section header if found
    skills_section_payload = extractor.extract_skills(sections["skills"]["content"])
    
    # Step 4: Boost confidence for explicit 'Skills' section matches
    for precise_skill in skills_section_payload["technical_skills"] + skills_section_payload["non_technical_skills"]:
        if precise_skill in skills_payload["confidence"]:
            # Max out confidence at 0.99 for validated locations
            skills_payload["confidence"][precise_skill] = min(0.99, skills_payload["confidence"][precise_skill] + 0.10)
    
    # Step 5: Format the final structured JSON structure
    final_output = {
        "candidate_id": resume_name,
        "resume_name": filename,
        "technical_skills": skills_payload["technical_skills"],
        "non_technical_skills": skills_payload["non_technical_skills"],
        "confidence": skills_payload["confidence"]
    }
    
    json_output = json.dumps(final_output, indent=4)
    
    # Print output directly to terminal
    print(json_output)
    
    # Step 6: Save strictly to the targeted reports directory
    output_filename = f"skills_output_{resume_name}.json"
    output_filepath = os.path.join(reports_dir, output_filename)
    
    with open(output_filepath, 'w', encoding='utf-8') as out_f:
        out_f.write(json_output)
        
    logging.info(f"\n[SUCCESS] Saved extracted data to: {output_filepath}")

if __name__ == "__main__":
    test_extraction()
