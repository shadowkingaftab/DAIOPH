"""
pdf_parser.py
-------------
Extracts text from PDF files, including text embedded in images via OCR.

Requirements:
  - PyPDF2       : Standard PDF text extraction
  - pdf2image    : Convert PDF pages to images for OCR
  - pytesseract  : OCR engine (requires Tesseract installed on system)
  - Pillow       : Image processing

If pdf2image or pytesseract are unavailable (e.g., on Streamlit Cloud),
the module falls back gracefully to text-only extraction.
"""

import os
import PyPDF2

# ── Optional OCR imports ──────────────────────────────────────────────────────
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    import pytesseract
    HAS_TESSERACT = True
except (ImportError, Exception):
    HAS_TESSERACT = False


def extract_text_from_pdf(pdf_path: str, chunk_size: int = 4000, enable_ocr: bool = True) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_path   : Path to the PDF file.
        chunk_size : Maximum characters to return (avoids memory issues with huge PDFs).
        enable_ocr : If True, attempts OCR on page images when direct text extraction yields nothing.

    Returns:
        Extracted text string (truncated to chunk_size characters).
    """
    text = ""

    # ── Step 1: Direct text extraction ────────────────────────────────────────
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[pdf_parser] PyPDF2 extraction error: {e}")

    # ── Step 2: OCR on images within the PDF ──────────────────────────────────
    if enable_ocr and HAS_PDF2IMAGE and HAS_TESSERACT:
        output_folder = "temp_pdf_images"
        os.makedirs(output_folder, exist_ok=True)
        try:
            images = convert_from_path(pdf_path, output_folder=output_folder, fmt="jpeg")
            for i, image in enumerate(images):
                ocr_text = pytesseract.image_to_string(image)
                if ocr_text.strip():
                    text += f"\n[Image {i+1} OCR Text]\n{ocr_text}\n"
        except Exception as e:
            print(f"[pdf_parser] OCR error (non-fatal): {e}")
        finally:
            # Clean up temp images
            try:
                for f in os.listdir(output_folder):
                    os.remove(os.path.join(output_folder, f))
                os.rmdir(output_folder)
            except Exception:
                pass
    elif enable_ocr and not HAS_PDF2IMAGE:
        print("[pdf_parser] pdf2image not installed — skipping image OCR.")
    elif enable_ocr and not HAS_TESSERACT:
        print("[pdf_parser] pytesseract not installed — skipping image OCR.")

    # ── Step 3: Truncate to avoid memory issues ───────────────────────────────
    return text[:chunk_size] if text else "No text could be extracted from this PDF."


def get_pdf_images(pdf_path: str):
    """
    Returns a list of PIL images from a PDF for preview purposes.
    Returns empty list if pdf2image is not available.
    """
    if not HAS_PDF2IMAGE:
        return []
    try:
        return convert_from_path(pdf_path)
    except Exception as e:
        print(f"[pdf_parser] Could not convert PDF to images: {e}")
        return []
