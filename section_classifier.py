import os
import re
import json
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class ResumeSectionClassifier:
    def __init__(self):
        # Configurable keywords for varied headings
        self.keywords = {
            "work_experience": ["experience", "employment", "work history", "career", "professional experience"],
            "education": ["education", "academic", "qualifications", "degree"],
            "skills": ["skills", "technologies", "tech stack", "core competencies"],
            "projects": ["projects", "personal projects", "academic projects"],
            "certifications": ["certifications", "certificates", "courses", "licenses"]
        }
        
    def _clean_text(self, text):
        """Clean extracted text by removing extra spaces and bad symbols."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip('- \t\n\r')
        return text

    def _get_section_name(self, line):
        """Identify if a line is a heading and return the standardized section name."""
        clean_line = line.lower().strip()
        # Remove markdown heading symbols like ###
        clean_line = re.sub(r'^#+\s*', '', clean_line)
        
        for section, keywords in self.keywords.items():
            if any(kw == clean_line for kw in keywords) or \
               any(clean_line.startswith(kw) for kw in keywords):
                return section
        return None

    def _smart_detection(self, blocks):
        """If headings are missing, infer sections based on content patterns."""
        inferred = defaultdict(list)
        
        for block in blocks:
            text = " ".join(block)
            lower_text = text.lower()
            
            # Simple heuristic patterns
            if re.search(r'\b(bachelor|b\.s|master|m\.s|phd|university|college|degree)\b', lower_text):
                inferred['education'].extend(block)
            elif re.search(r'\b(developed|built|managed|led|worked at|engineer|manager)\b', lower_text) and \
                 re.search(r'\b(20[0-9]{2}|19[0-9]{2}|present|ongoing)\b', lower_text):
                inferred['work_experience'].extend(block)
            elif re.search(r'\b(certified|certification|course|aws|gcp|azure)\b', lower_text) and "course" in lower_text:
                inferred['certifications'].extend(block)
            elif "," in text and len(block) <= 3:
                # Often skills are comma separated short lines
                inferred['skills'].extend(block)
            else:
                # Default to experience if it looks like bullet points with action verbs
                if "-" in text or "•" in text:
                    inferred['work_experience'].extend(block)
                    
        return inferred

    def classify_sections(self, text):
        """Detect, label, and evaluate resume sections from processed text."""
        lines = text.split('\n')
        sections = {
            "skills": "",
            "work_experience": "",
            "education": "",
            "projects": "",
            "certifications": ""
        }
        confidence = {k: 0.0 for k in sections.keys()}
        
        current_section = None
        current_content = []
        blocks_no_heading = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            detected_heading = self._get_section_name(line)
            
            if detected_heading:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] += " " + " ".join(current_content)
                    confidence[current_section] = 0.9 # High confidence for explicit headings
                elif not current_section and current_content:
                    blocks_no_heading.append(current_content)
                    
                current_section = detected_heading
                current_content = []
            else:
                current_content.append(line)
                
        # Save last section
        if current_section and current_content:
            sections[current_section] += " " + " ".join(current_content)
            confidence[current_section] = 0.9
        elif not current_section and current_content:
            blocks_no_heading.append(current_content)
            
        # Apply smart detection for any leftover blocks missing a heading
        if blocks_no_heading:
            inferred = self._smart_detection(blocks_no_heading)
            for k, v in inferred.items():
                if not sections.get(k):  # only fill if empty
                    sections[k] = " ".join(v)
                    confidence[k] = 0.6  # lower confidence for inferred
                    
        # Clean up output formatting
        output = {}
        for k in sections.keys():
            content = self._clean_text(sections[k])
            output[k] = {
                "content": content,
                "confidence": confidence[k] if content else 0.0
            }
            
        return output

def generate_labels(processed_dir, labels_dir):
    """
    Helper function to generate labels from processed resumes.
    Reads from data/processed/*.txt and writes true format to data/labels/*.json
    """
    if not os.path.exists(labels_dir):
        os.makedirs(labels_dir)
        
    classifier = ResumeSectionClassifier()
    
    for filename in os.listdir(processed_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(processed_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            predictions = classifier.classify_sections(text)
            
            # Formulating structure specifically requested
            output_data = {
                "skills": predictions["skills"]["content"],
                "work_experience": predictions["work_experience"]["content"],
                "education": predictions["education"]["content"],
                "projects": predictions["projects"]["content"],
                "certifications": predictions["certifications"]["content"]
            }
            
            base_name = filename.replace("_cleaned.txt", "") # align names
            label_file = os.path.join(labels_dir, f"{base_name}.json")
            
            with open(label_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4)
                
            logging.info(f"Generated label for {filename} -> {label_file}")

if __name__ == "__main__":
    processed_dir = os.path.join("data", "processed")
    labels_dir = os.path.join("data", "labels")
    logging.info("Running Auto Label Generator...")
    generate_labels(processed_dir, labels_dir)
    logging.info("Auto label generation complete.")
