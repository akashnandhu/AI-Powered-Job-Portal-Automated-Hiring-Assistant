import os
import re
import json

def clean_text(text: str) -> str:
    """Clean the text: remove bullets, symbols, and extra spaces, convert to lowercase."""
    if not text:
        return ""
    # Remove leading bullets, dashes, asterisks
    text = re.sub(r'^[•\-\*\.]\s*', '', text.strip())
    # Convert to lowercase
    text = text.lower()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text

def normalize_roles(role: str) -> str:
    """Map similar job titles to standard roles."""
    role = role.lower().strip()
    mapping = {
        "hospital pharmacist": "clinical pharmacist",
        "icu pharmacist": "critical care pharmacist",
        "retail pharmacist": "community pharmacist",
        "pharmacy store manager": "pharmacy manager",
        "chain pharmacy manager": "pharmacy manager"
    }
    return mapping.get(role, role)

def normalize_skills(skill: str) -> str:
    """Map similar skills into standard forms."""
    skill = skill.lower().strip()
    mapping = {
        "drug therapy": "pharmacotherapy",
        "patient advice": "patient counseling",
        "medication counseling": "patient counseling",
        "dispense medications": "medication dispensing",
        "maintain hospital drug inventory": "inventory management",
        "manage chronic diseases": "chronic disease management",
        "prevent medication errors": "medication safety"
    }
    for key, val in mapping.items():
        if key in skill:
            skill = skill.replace(key, val)
    return skill.strip()

def merge_bullet_points(lines: list) -> list:
    """Merge lines that belong to the same bullet point."""
    merged = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        # If line starts with a bullet or we have no items yet
        if re.match(r'^[•\-\*]', line_stripped) or not merged:
            merged.append(line_stripped)
        else:
            merged[-1] += " " + line_stripped
    return merged

def extract_skills(responsibilities: list) -> list:
    """Extract and normalize skills from responsibilities."""
    skills = []
    for resp in merge_bullet_points(responsibilities):
        cleaned = clean_text(resp)
        normalized = normalize_skills(cleaned)
        if normalized:
            skills.append(normalized)
    return list(dict.fromkeys(skills)) # Return unique skills while preserving order

def extract_education(qualifications: list) -> list:
    """Extract education requirements."""
    education = []
    for qual in merge_bullet_points(qualifications):
        cleaned = clean_text(qual)
        if "experience" not in cleaned:
            education.append(cleaned)
    return list(dict.fromkeys(education))

def extract_experience(qualifications: list) -> str:
    """Extract experience requirements if available."""
    for qual in merge_bullet_points(qualifications):
        cleaned = clean_text(qual)
        if "experience" in cleaned:
            return cleaned
    return "Not specified"

def build_jd_object(title, category, responsibilities, qualifications, work_settings):
    """Create a structured JSON object for a job."""
    return {
        "job_title": normalize_roles(title).title(),
        "category": category,
        "skills_required": extract_skills(responsibilities),
        "education_required": extract_education(qualifications),
        "experience_required": extract_experience(qualifications),
        "work_environment": [clean_text(w) for w in merge_bullet_points(work_settings) if clean_text(w)]
    }

def save_each_job_to_file(job, output_dir, title_counts):
    """Save job object to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    base_name = job["job_title"].lower()
    # Replace spaces with underscores and remove non-alphanumeric chars
    base_name = re.sub(r'\s+', '_', base_name)
    base_name = re.sub(r'[^\w_]', '', base_name)
    
    if base_name in title_counts:
        title_counts[base_name] += 1
        file_name = f"{base_name}_{title_counts[base_name]}.json"
    else:
        title_counts[base_name] = 0
        file_name = f"{base_name}.json"
        
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(job, f, indent=4)

def parse_jd_file(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    jobs = []
    current_job = {}
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match "1. Clinical Pharmacist"
        match_title = re.match(r'^(\d+)\.\s+(.+)', line)
        if match_title:
            if current_job and "title" in current_job:
                jobs.append(current_job)
            current_job = {
                "title": match_title.group(2).strip(),
                "overview": [],
                "responsibilities": [],
                "qualifications": [],
                "work_settings": []
            }
            current_section = "title_continuation"
            continue
            
        val_lower = line.lower()
        if "job overview" in val_lower:
            current_section = "overview"
            continue
        elif "key responsibilities" in val_lower:
            current_section = "responsibilities"
            continue
        elif "required qualifications" in val_lower:
            current_section = "qualifications"
            continue
        elif "work settings" in val_lower:
            current_section = "work_settings"
            continue
            
        if current_section == "title_continuation":
            current_job["title"] += " " + line.strip()
        elif current_section and current_job:
            current_job[current_section].append(line)
            
    if current_job and "title" in current_job:
        jobs.append(current_job)
        
    return jobs

def main():
    input_dir = "data/jobs_data"
    output_dir = "output/jd_files"
    combined_file = "output/jd_parsed_output.json"
    
    if not os.path.exists(input_dir):
        print(f"Error: Could not find input directory {input_dir}")
        return
        
    print(f"Reading job descriptions from {input_dir}...")
    
    raw_jobs = []
    # Process all txt files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_dir, filename)
            try:
                raw_jobs.extend(parse_jd_file(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                
    if not raw_jobs:
        print("No job descriptions were successfully parsed.")
        return
        
    parsed_jobs = []
    title_counts = {}
    
    for raw_job in raw_jobs:
        # Determine simple category
        title_l = raw_job["title"].lower()
        category = "Pharmacy"
        if "clinical" in title_l or "hospital" in title_l or "critical" in title_l or "care" in title_l:
            category = "Clinical/Hospital Pharmacy"
        elif "retail" in title_l or "community" in title_l or "store" in title_l:
            category = "Retail/Community Pharmacy"
        elif "industrial" in title_l or "production" in title_l or "manufacturing" in title_l:
            category = "Industrial/Manufacturing Pharmacy"
        elif "research" in title_l or "scientist" in title_l:
            category = "Research & Development"
        
        job_obj = build_jd_object(
            title=raw_job["title"],
            category=category,
            responsibilities=raw_job["responsibilities"],
            qualifications=raw_job["qualifications"],
            work_settings=raw_job["work_settings"]
        )
        parsed_jobs.append(job_obj)
        save_each_job_to_file(job_obj, output_dir, title_counts)
        
    # Save combined file
    os.makedirs(os.path.dirname(combined_file), exist_ok=True)
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(parsed_jobs, f, indent=4)
        
    print(f"Successfully processed {len(parsed_jobs)} job descriptions.")
    print(f"Files saved in {output_dir}/")
    print(f"Combined output saved as {combined_file}")

if __name__ == "__main__":
    main()
