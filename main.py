import os
from utils.logger import get_logger
from utils.text_cleaner import clean_text
from utils.file_handler import get_resume_files, save_cleaned_output, ensure_dirs
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx

# Initialize logger
logger = get_logger("extraction_engine")

# Configuration
INPUT_DIR = "data/resumes"
OUTPUT_DIR = "data/processed"
LOGS_DIR = "logs"

def run_pipeline():
    """
    Orchestrates the resume text extraction pipeline:
    Extract → Clean → Save
    """
    # 1. Ensure required directories exist
    ensure_dirs([INPUT_DIR, OUTPUT_DIR, LOGS_DIR])
    logger.info("Pipeline started. Checking for resumes...")

    # 2. Get all resume files
    resumes = get_resume_files(INPUT_DIR)
    if not resumes:
        logger.warning(f"No resumes found in {INPUT_DIR}. Please add some.")
        return

    logger.info(f"Found {len(resumes)} resumes to process.")

    # 3. Process each resume
    for resume in resumes:
        file_path = os.path.join(INPUT_DIR, resume)
        logger.info(f"Processing: {resume}")
        
        try:
            # a. Determine parser based on extension
            if resume.lower().endswith('.pdf'):
                raw_text = parse_pdf(file_path)
            elif resume.lower().endswith('.docx'):
                raw_text = parse_docx(file_path)
            else:
                logger.error(f"Unsupported file format: {resume}")
                continue

            if not raw_text:
                logger.error(f"Failed to extract text from: {resume}")
                continue

            # b. Clean text
            cleaned_text = clean_text(raw_text)
            
            # c. Save output
            output_path = save_cleaned_output(cleaned_text, resume, OUTPUT_DIR)
            logger.info(f"Successfully processed {resume}. Saved to: {output_path}")

        except Exception as e:
            logger.error(f"Error processing {resume}: {str(e)}")

    logger.info("Pipeline execution completed.")

if __name__ == "__main__":
    run_pipeline()
    print("Extraction complete. Check logs/extraction.log for details.")
