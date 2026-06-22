import fitz  # PyMuPDF
import os
from PIL import Image
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a text-based PDF"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def is_scanned_pdf(file_bytes: bytes) -> bool:
    """Check if PDF is scanned (image-based) or text-based"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    # If less than 50 characters extracted, it's likely a scanned PDF
    return len(text.strip()) < 50


def pdf_to_images(file_bytes: bytes) -> list:
    """Convert PDF pages to images for Claude Vision"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    images = []
    for page in doc:
        # Render page at 2x resolution for better quality
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)
    doc.close()
    return images
