from pathlib import Path

import pytesseract

from app.config.settings import TESSERACT_PATH
from app.document_understanding.models.documents import OCRResult
from app.document_understanding.ocr.base import (
    OCRProvider,
    OCRProcessingError,
)


class TesseractOCRProvider(OCRProvider):
    """OCR provider backed by Tesseract OCR."""

    def __init__(
        self,
        tesseract_path: str = TESSERACT_PATH,
    ) -> None:
        self.tesseract_path = tesseract_path

        if not Path(tesseract_path).exists():
            raise FileNotFoundError(
                f"Tesseract executable not found: "
                f"{tesseract_path}"
            )

        pytesseract.pytesseract.tesseract_cmd = (
            tesseract_path
        )

    def extract_text(
        self,
        file_path: str | Path,
    ) -> OCRResult:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        try:
            text = pytesseract.image_to_string(
                str(path)
            )
        except Exception as exc:
            raise OCRProcessingError(
                "Tesseract OCR failed while processing "
                "the document."
            ) from exc

        if not text or not text.strip():
            raise OCRProcessingError(
                "Tesseract OCR could not extract "
                "readable text from the document."
            )

        return OCRResult(
            text=text.strip()
        )