import os
import sys
from utils.logger import get_logger
from utils.text_cleaner import clean_text
from utils.file_handler import get_resume_files, save_cleaned_output, ensure_dirs
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from config import CANDIDATE_ID

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

    # 2. Get the specific resume file based on config
    target_resume = f"{CANDIDATE_ID}.pdf"
    file_path = os.path.join(INPUT_DIR, target_resume)
    
    if not os.path.exists(file_path):
        logger.error(f"Error: Required resume {file_path} not found. Please add it.")
        return

    logger.info(f"Processing candidate: {CANDIDATE_ID}")
    
    try:
        raw_text = parse_pdf(file_path)

        if not raw_text:
            logger.error(f"Failed to extract text from: {target_resume}")
            return

        # b. Clean text
        cleaned_text = clean_text(raw_text)
        
        # c. Save output with explicit name
        output_filename = f"{CANDIDATE_ID}_cleaned.txt"
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
            
        logger.info(f"Successfully processed {target_resume}. Saved to: {output_path}")

    except Exception as e:
        logger.error(f"Error processing {target_resume}: {str(e)}")

    logger.info("Pipeline execution completed.")

if __name__ == "__main__":
    run_pipeline()
    print("Extraction complete. Check logs/extraction.log for details.")
