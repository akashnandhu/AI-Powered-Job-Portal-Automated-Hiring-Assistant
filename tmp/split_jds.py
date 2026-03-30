import os
import re

def sanitize_filename(name):
    # Remove the number and dot at the start if present
    name = re.sub(r'^\d+\.\s*', '', name)
    # Lowercase
    name = name.lower()
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove special characters (keep alphanumeric and underscores)
    name = re.sub(r'[^a-z0-9_]', '', name)
    # Remove duplicate underscores
    name = re.sub(r'_+', '_', name)
    # Trim underscores from ends
    name = name.strip('_')
    return name

def split_job_descriptions(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split using pattern: newline followed by number + dot + space
    # Or start of string followed by number + dot + space
    pattern = r'(?m)^(\d+\.\s+.*)'
    
    # We want to keep the headers, so we use finditer to get positions
    matches = list(re.finditer(pattern, content))
    
    jobs = []
    for i in range(len(matches)):
        start_idx = matches[i].start()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        job_content = content[start_idx:end_idx].strip()
        if job_content:
            jobs.append(job_content)

    filenames = []
    name_counts = {}

    for job in jobs:
        # First line is the title
        lines = job.split('\n')
        title_line = lines[0].strip()
        
        base_name = sanitize_filename(title_line)
        if not base_name:
            base_name = "job_description"
            
        # Handle duplicates
        final_name = base_name
        if final_name in name_counts:
            name_counts[final_name] += 1
            final_filename = f"{final_name}_{name_counts[final_name]}.txt"
        else:
            name_counts[final_name] = 0
            final_filename = f"{final_name}.txt"
            
        file_path = os.path.join(output_dir, final_filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(job)
        
        filenames.append(final_filename)

    print(f"Total number of files created: {len(filenames)}")
    print("List of filenames:")
    for fname in filenames:
        print(f"- {fname}")

if __name__ == "__main__":
    input_path = r"c:\Users\AKASH\OneDrive\Desktop\anti\data\jobs_data.txt\jd_sch.txt"
    output_path = r"c:\Users\AKASH\OneDrive\Desktop\anti\data\jobs_data"
    split_job_descriptions(input_path, output_path)
