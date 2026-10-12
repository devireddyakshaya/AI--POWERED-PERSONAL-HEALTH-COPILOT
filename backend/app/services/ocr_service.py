"""
OCR and document text extraction service for MediMitra AI.
Extracts selectable text from PDFs via PyMuPDF and handles images via pytesseract,
with resilient pure-python fallback for scanned documents and demo images.
"""
import io
import os
import re
from typing import Dict, Any, List, Tuple
from PIL import Image

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from backend.app.config import TESSERACT_CMD

if PYTESSERACT_AVAILABLE and TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


class OCRService:
    @staticmethod
    def extract_from_file(file_bytes: bytes, file_name: str, content_type: str) -> Dict[str, Any]:
        """
        Extract text and metadata from uploaded PDF or image file.
        Returns:
            {
                "raw_text": str,
                "page_count": int,
                "confidence_score": float,
                "pages": List[Dict[str, Any]],
                "trust_warnings": List[str]
            }
        """
        lower_name = file_name.lower()
        trust_warnings = []
        pages_data = []

        if lower_name.endswith(".pdf") or "pdf" in content_type.lower():
            extracted = OCRService._extract_pdf(file_bytes)
        elif any(lower_name.endswith(ext) for ext in [".jpg", ".jpeg", ".png"]) or "image" in content_type.lower():
            extracted = OCRService._extract_image(file_bytes)
        else:
            # Attempt general text decode
            try:
                text = file_bytes.decode("utf-8", errors="ignore")
                extracted = {
                    "raw_text": text,
                    "page_count": 1,
                    "confidence_score": 0.88,
                    "pages": [{"page_number": 1, "text": text}]
                }
            except Exception as e:
                extracted = {
                    "raw_text": "",
                    "page_count": 0,
                    "confidence_score": 0.0,
                    "pages": []
                }
                trust_warnings.append(f"Unsupported or corrupted file format: {str(e)}")

        raw_text = extracted.get("raw_text", "").strip()
        confidence = extracted.get("confidence_score", 0.90)

        # Smart Report Trust Check heuristics
        if not raw_text or len(raw_text) < 30:
            trust_warnings.append("Document scan contains very little readable text. Please verify extracted results.")
            confidence = min(confidence, 0.40)
        elif confidence < 0.65:
            trust_warnings.append("Low OCR confidence detected. Scanned text might have distorted characters.")

        extracted["trust_warnings"] = trust_warnings
        return extracted

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> Dict[str, Any]:
        """Extracts text from PDF using PyMuPDF; falls back to OCR if pages are purely images."""
        if not PYMUPDF_AVAILABLE:
            # Fallback if fitz is not installed
            try:
                # Basic string scan for plain text streams
                text = file_bytes.decode("latin1", errors="ignore")
                clean_text = " ".join(re.findall(r"[A-Za-z0-9\.\,\:\;\-\%\/]{2,}", text))
                return {
                    "raw_text": clean_text[:4000],
                    "page_count": 1,
                    "confidence_score": 0.70,
                    "pages": [{"page_number": 1, "text": clean_text[:4000]}]
                }
            except Exception:
                return {"raw_text": "", "page_count": 0, "confidence_score": 0.0, "pages": []}

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
            all_text_parts = []
            pages_list = []
            has_scanned_page = False

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_text = page.get_text("text").strip()

                # If selectable text is missing, attempt image extraction from page
                if len(page_text) < 30:
                    has_scanned_page = True
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    img_result = OCRService._extract_image(img_bytes)
                    page_text = img_result.get("raw_text", "")

                pages_list.append({
                    "page_number": page_idx + 1,
                    "text": page_text
                })
                all_text_parts.append(page_text)

            full_text = "\n\n--- Page Break ---\n\n".join(all_text_parts)
            confidence = 0.85 if has_scanned_page else 0.98

            return {
                "raw_text": full_text,
                "page_count": total_pages,
                "confidence_score": confidence,
                "pages": pages_list
            }
        except Exception as e:
            return {
                "raw_text": f"Error parsing PDF document: {str(e)}",
                "page_count": 1,
                "confidence_score": 0.30,
                "pages": []
            }

    @staticmethod
    def _extract_image(file_bytes: bytes) -> Dict[str, Any]:
        """Extract text from image using Tesseract OCR, with resilient rule-based fallback."""
        try:
            image = Image.open(io.BytesIO(file_bytes))
        except Exception as e:
            return {
                "raw_text": f"Invalid image file: {str(e)}",
                "page_count": 1,
                "confidence_score": 0.10,
                "pages": []
            }

        extracted_text = ""
        confidence = 0.80

        if PYTESSERACT_AVAILABLE:
            try:
                # Attempt OCR with tesseract
                extracted_text = pytesseract.image_to_string(image)
                confidence = 0.88 if len(extracted_text) > 50 else 0.50
            except Exception:
                # Tesseract executable might not be in PATH on Windows
                extracted_text = ""

        # If Tesseract didn't return text (e.g., binary not installed on machine),
        # check if image has embedded metadata or text payload
        if not extracted_text.strip():
            # Check image info or EXIF
            exif_text = " ".join([str(v) for v in image.info.values() if isinstance(v, str)])
            if exif_text:
                extracted_text = exif_text
                confidence = 0.75
            else:
                extracted_text = (
                    "Image scanned document processed. Note: Tesseract OCR engine was not detected in PATH, "
                    "or image resolution was insufficient. Please review and manually verify extracted values."
                )
                confidence = 0.60

        return {
            "raw_text": extracted_text,
            "page_count": 1,
            "confidence_score": confidence,
            "pages": [{"page_number": 1, "text": extracted_text}]
        }
