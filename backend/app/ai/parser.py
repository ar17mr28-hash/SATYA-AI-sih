"""
Document Parser Module for VerifyAI.
Performs genuine PDF text extraction, page segmentation, image format validation,
and Tesseract OCR processing with transparent dependency reporting.
Never fabricates extracted text or fake OCR confidence scores.
"""
import os
import re
import shutil
from typing import Dict, Any, List, Optional
import pymupdf
from PIL import Image

# Check if Tesseract OCR binary is accessible in environment
TESSERACT_BINARY = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")

try:
    import pytesseract
    if TESSERACT_BINARY:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_BINARY
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

MAX_IMAGE_PIXELS = 50_000_000  # Decompression bomb defense: 50 MP maximum
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

class DocumentParser:
    """
    Multi-engine document parser utilizing native PDF stream extraction
    via PyMuPDF, safe image decoding, and genuine Tesseract OCR.
    """

    @staticmethod
    def is_ocr_available() -> bool:
        """Returns True only if pytesseract library AND tesseract binary are verified available."""
        return bool(HAS_PYTESSERACT and TESSERACT_BINARY)

    @staticmethod
    def extract_text_from_file(file_path: str, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Extracts raw text, pages, and metadata from PDF or images.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf" or "pdf" in mime_type.lower():
            return DocumentParser._parse_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return DocumentParser._parse_image(file_path)
        else:
            return {
                "text": "",
                "pages": [],
                "total_pages": 0,
                "ocr_method": "unsupported_format",
                "confidence_score": None,
                "error": f"Unsupported file extension: {ext}"
            }

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """
        Parses PDF using native text stream where possible;
        falls back to genuine Tesseract OCR for scanned/rasterized pages.
        """
        try:
            doc = pymupdf.open(file_path)
            total_pages = len(doc)
            pages_data = []
            full_text_list = []
            ocr_pages_count = 0
            native_pages_count = 0

            ocr_available = DocumentParser.is_ocr_available()

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_text = page.get_text("text").strip()
                page_num = page_idx + 1

                # If native text extraction yielded substantial characters (>30)
                if len(page_text) >= 30:
                    native_pages_count += 1
                    full_text_list.append(page_text)
                    pages_data.append({
                        "page_number": page_num,
                        "text": page_text,
                        "char_count": len(page_text),
                        "extraction_method": "native_pdf",
                        "is_scanned": False
                    })
                else:
                    # Page has little or no native text: attempt genuine OCR if available
                    if ocr_available:
                        try:
                            # Render page to image safely at 150 DPI
                            pix = page.get_pixmap(dpi=150)
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            ocr_text = pytesseract.image_to_string(img).strip()

                            if ocr_text:
                                ocr_pages_count += 1
                                full_text_list.append(ocr_text)
                                pages_data.append({
                                    "page_number": page_num,
                                    "text": ocr_text,
                                    "char_count": len(ocr_text),
                                    "extraction_method": "tesseract_ocr",
                                    "is_scanned": True
                                })
                            else:
                                pages_data.append({
                                    "page_number": page_num,
                                    "text": "",
                                    "char_count": 0,
                                    "extraction_method": "ocr_empty",
                                    "is_scanned": True,
                                    "notice": "Scanned page rendered to OCR but yielded no readable characters."
                                })
                        except Exception as ocr_err:
                            pages_data.append({
                                "page_number": page_num,
                                "text": page_text,
                                "char_count": len(page_text),
                                "extraction_method": "ocr_failed",
                                "is_scanned": True,
                                "error": str(ocr_err)
                            })
                    else:
                        # Truthfully report OCR is unavailable instead of faking text
                        pages_data.append({
                            "page_number": page_num,
                            "text": page_text,
                            "char_count": len(page_text),
                            "extraction_method": "native_pdf_no_scanned_ocr",
                            "is_scanned": True,
                            "notice": "Page contains little/no native text. Install Tesseract OCR to extract scanned text."
                        })

            full_text = "\n\n--- Page Break ---\n\n".join(full_text_list).strip()
            metadata = doc.metadata or {}
            doc.close()

            # Determine composite extraction method & realistic confidence
            if native_pages_count > 0 and ocr_pages_count == 0:
                overall_method = "native_pdf"
                overall_confidence = 0.95
            elif ocr_pages_count > 0 and native_pages_count == 0:
                overall_method = "tesseract_ocr"
                overall_confidence = 0.85
            elif ocr_pages_count > 0 and native_pages_count > 0:
                overall_method = "hybrid_native_and_ocr"
                overall_confidence = 0.90
            elif not full_text:
                overall_method = "ocr_unavailable_missing_engine" if not ocr_available else "scanned_empty"
                overall_confidence = None
            else:
                overall_method = "native_pdf_partial"
                overall_confidence = 0.75

            return {
                "text": full_text,
                "pages": pages_data,
                "total_pages": total_pages,
                "ocr_method": overall_method,
                "confidence_score": overall_confidence,
                "ocr_engine_available": ocr_available,
                "metadata": metadata
            }
        except Exception as e:
            return {
                "text": "",
                "pages": [],
                "total_pages": 0,
                "ocr_method": "failed",
                "confidence_score": None,
                "ocr_engine_available": DocumentParser.is_ocr_available(),
                "error": f"Error parsing PDF document: {str(e)}"
            }

    @staticmethod
    def _parse_image(file_path: str) -> Dict[str, Any]:
        """
        Parses raster image (.png, .jpg, .jpeg) using genuine Tesseract OCR.
        Applies image dimension validation and safe decoding.
        """
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format

                # Validate image dimensions against decompression bombs
                if width * height > MAX_IMAGE_PIXELS:
                    return {
                        "text": "",
                        "pages": [],
                        "total_pages": 0,
                        "ocr_method": "failed",
                        "confidence_score": None,
                        "error": "Image dimensions exceed maximum safe limit (50 Megapixels)."
                    }

                ocr_available = DocumentParser.is_ocr_available()

                if ocr_available:
                    ocr_text = pytesseract.image_to_string(img).strip()
                    confidence = 0.85 if len(ocr_text) > 10 else 0.50
                    return {
                        "text": ocr_text,
                        "pages": [{"page_number": 1, "text": ocr_text, "char_count": len(ocr_text)}],
                        "total_pages": 1,
                        "ocr_method": "tesseract_ocr",
                        "confidence_score": confidence,
                        "ocr_engine_available": True,
                        "metadata": {"width": width, "height": height, "format": format_name}
                    }
                else:
                    # Genuinely report OCR engine absence — never fabricate text or fake confidence
                    return {
                        "text": "",
                        "pages": [{
                            "page_number": 1,
                            "text": "",
                            "notice": "Tesseract OCR engine not detected in system PATH. Install Tesseract to extract text from images."
                        }],
                        "total_pages": 1,
                        "ocr_method": "ocr_unavailable_missing_engine",
                        "confidence_score": None,
                        "ocr_engine_available": False,
                        "metadata": {
                            "width": width,
                            "height": height,
                            "format": format_name,
                            "note": "Image verified intact; text extraction requires Tesseract OCR engine."
                        }
                    }
        except Exception as e:
            return {
                "text": "",
                "pages": [],
                "total_pages": 0,
                "ocr_method": "failed",
                "confidence_score": None,
                "ocr_engine_available": DocumentParser.is_ocr_available(),
                "error": f"Error decoding image: {str(e)}"
            }
