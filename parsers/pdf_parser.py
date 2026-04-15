import os
import logging

def parse_pdf(file_path):
    """
    Extracts text from a PDF file.
    Optimized for speed using PyMuPDF (fitz), with fallback to pdfplumber.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text_content = []

    # 1. Try PyMuPDF (Fastest, best for production)
    try:
        import fitz  # PyMuPDF
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                if text:
                    text_content.append(text)
        return "\n".join(text_content)
    except ImportError:
        logging.warning("PyMuPDF (fitz) not installed. Falling back to pdfplumber (slower).")
    except Exception as e:
        logging.warning(f"PyMuPDF failed {file_path}: {e}. Trying pdfplumber...")

    # 2. Fallback to pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            # Optimize: do not extract tables explicitly unless necessary for speed.
            # Using extract_text is generally sufficient for standard resumes.
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if page_text:
                    text_content.append(page_text)
                    
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
        return None

    return "\n".join(text_content)
