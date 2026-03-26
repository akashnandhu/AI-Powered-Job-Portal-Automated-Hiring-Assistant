import os
import shutil

def get_resume_files(input_dir):
    """
    Lists all supported resume files in the input directory.
    Supported: .pdf, .docx
    """
    supported = ('.pdf', '.docx')
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        return []

    return [f for f in os.listdir(input_dir) if f.lower().endswith(supported)]

def save_cleaned_output(text, original_filename, output_dir):
    """
    Saves cleaned text as a .txt file in the output directory.
    Uses the original filename (without extension) as the base.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_name = os.path.splitext(original_filename)[0]
    output_path = os.path.join(output_dir, f"{base_name}_cleaned.txt")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return output_path

def ensure_dirs(dirs):
    """
    Ensures that all specified directories exist.
    """
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
