import pdfplumber
import os

def parse_pdf(file_path):
    """
    Extracts text from a PDF file using pdfplumber.
    Handles multi-page PDFs, tables, and attempts to preserve layout.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text_content = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # 1. Extract tables as readable text
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            # Filter None values and join row items
                            row_text = " | ".join([str(item) for item in row if item is not None])
                            text_content.append(row_text)
                
                # 2. Extract regular text
                # extract_text usually skips tables if they are well-formatted, 
                # but might duplicate text if extracted above. 
                # However, for resumes, extract_text is generally more reliable for layout.
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if page_text:
                    text_content.append(page_text)
                    
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
        return None

    return "\n".join(text_content)
