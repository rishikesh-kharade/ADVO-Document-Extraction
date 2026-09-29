from pathlib import Path

from app.document_understanding.classification.gemini_classifier import (
    GeminiDocumentClassifier,
)
from app.document_understanding.handlers.registry import (
    get_handler,
)
from app.ocr.tesseract import TesseractOCR


class DocumentProcessingService:

    def __init__(
        self,
        classifier=None,
        ocr=None,
    ) -> None:

        self.classifier = (
            classifier
            or GeminiDocumentClassifier()
        )

        self.ocr = (
            ocr
            or TesseractOCR()
        )

    def process_document(
        self,
        file_path: str | Path,
    ):

        # 1. Classify
        classification = self.classifier.classify(
            file_path,
        )

        # 2. Unsupported document
        if not classification.supported:

            return {
                "success": False,
                "document": classification.model_dump(),
                "message": (
                    "This document type is currently "
                    "not supported."
                ),
            }

        # 3. Find document handler
        handler = get_handler(
            classification.document_type,
            ocr=self.ocr,
        )

        # 4. Supported by registry but no handler
        if handler is None:

            return {
                "success": False,
                "document": classification.model_dump(),
                "message": (
                    "Document type is supported but "
                    "processing is not implemented yet."
                ),
            }

        # 5. Document-specific processing
        result = handler.process(
            file_path,
        )

        # 6. Standard API response
        return {
            "success": True,
            "document": classification.model_dump(),
            "extracted_data": result.extracted_data,
            "validation": result.validation,
            "ocr_text": result.ocr_text,
        }