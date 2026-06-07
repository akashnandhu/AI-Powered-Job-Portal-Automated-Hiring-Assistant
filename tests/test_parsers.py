import pytest
from utils.text_cleaner import clean_text
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
import os

def test_clean_text_noise_removal():
    """
    Test noise removal and whitespace normalization in text cleaner.
    """
    raw_text = "This is a   raw   text with many    spaces.\n\n\n\n- Skill 1\n- Skill 2"
    cleaned = clean_text(raw_text)
    assert "  " not in cleaned
    assert "###" not in cleaned # No headers in this sample
    assert cleaned.count("\n\n") == 1 # Extra newlines removed to max 2 for section spacing

def test_clean_text_header_standardization():
    """
    Test if common headers are correctly standardized to markdown style.
    """
    raw_text = "Work Experience: Software Engineer at Google. Skills: Python, AWS."
    cleaned = clean_text(raw_text)
    assert "### EXPERIENCE" in cleaned
    assert "### SKILLS" in cleaned

def test_clean_text_bullet_points():
    """
    Test if standardizing various bullet point styles works.
    """
    raw_text = "• Python\n· AWS\n* SQL\n- Docker"
    cleaned = clean_text(raw_text)
    assert cleaned.count("- ") == 4

def test_pdf_parser_missing_file():
    """
    Test behavior when PDF file is missing.
    """
    with pytest.raises(FileNotFoundError):
        parse_pdf("non_existent_file.pdf")

def test_docx_parser_missing_file():
    """
    Test behavior when DOCX file is missing.
    """
    with pytest.raises(FileNotFoundError):
        parse_docx("non_existent_file.docx")
