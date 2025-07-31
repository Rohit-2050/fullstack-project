import os
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime
import logging

# Set paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\murug\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Users\murug\poppler-24.08.0\Library\bin"

#Setup logging
os.makedirs("output_logs", exist_ok=True)
logging.basicConfig(
    filename="output_logs/log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def extract_with_pdfplumber(file_path):
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content
        return text.strip()
    except Exception as e:
        logging.warning(f"pdfplumber failed: {e}")
        return ""

def extract_with_pymupdf(file_path):
    try:
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        logging.warning(f"PyMuPDF failed: {e}")
        return ""

def extract_with_ocr(file_path):
    try:
        text = ""
        images = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)
        for image in images:
            text += pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logging.warning(f"OCR failed: {e}")
        return ""

def save_output(text, method):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"output_logs/extract_{method}_{timestamp}.txt"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)
    # logging.info(f"Saved extracted text using {method} to {file_name}")

def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from a PDF resume using multiple methods.
    Returns extracted text or an empty string.
    """
    # logging.info(f"Starting extraction for {file_path}")

    

    # Try method 1: PyMuPDF
    text = extract_with_pymupdf(file_path)
    if text:
        logging.info("Extraction successful using PyMuPDF.")
        save_output(text, "pymupdf")
        return text
    
    # Try method 2: pdfplumber
    text = extract_with_pdfplumber(file_path)
    if text:
        logging.info("Extraction successful using pdfplumber.")
        save_output(text, "pdfplumber")
        return text

    # Try method 3: OCR
    text = extract_with_ocr(file_path)
    if text:
        logging.info("Extraction successful using OCR.")
        save_output(text, "ocr")
        return text

    logging.error(" All extraction methods failed.")
    return ""











