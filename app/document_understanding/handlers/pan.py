from pathlib import Path

from app.extractors import extract_pan
from app.ocr.candidate_selection import select_best_pan_candidate
from app.ocr.tesseract import TesseractOCR
from app.validators import validate_pan_number

from app.document_understanding.handlers.base import (
    DocumentHandler,
    DocumentHandlerResult,
)


class PanDocumentHandler(DocumentHandler):

    def __init__(self, ocr: TesseractOCR) -> None:
        self.ocr = ocr

    def process(
        self,
        file_path: str | Path,
    ) -> DocumentHandlerResult:

        # 1. Common OCR engine
        candidates = self.ocr.extract_candidates_from_file(
            file_path,
        )

        # 2. PAN-specific candidate selection
        best_candidate = select_best_pan_candidate(
            candidates,
        )

        # 3. PAN-specific extraction
        document = extract_pan(
            best_candidate.text,
        )

        # 4. PAN-specific validation
        pan_number_valid = validate_pan_number(
            document.pan_number,
        )

        return DocumentHandlerResult(
            extracted_data=document.model_dump(),
            validation={
                "pan_number": pan_number_valid,
                "valid": pan_number_valid,
            },
            ocr_text=best_candidate.text,
        )