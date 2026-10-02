import logging
from pathlib import Path

from google.genai.errors import ServerError

from app.document_understanding.classification.base import DocumentClassifier
from app.document_understanding.classification.gemini_classifier import (
    GeminiDocumentClassifier,
)
from app.document_understanding.handlers.registry import get_handler
from app.document_understanding.models.documents import (
    DocumentProcessingResponse,
)
from app.document_understanding.ocr.base import OCRProvider, OCRProcessingError
from app.document_understanding.ocr.factory import get_ocr_provider


logger = logging.getLogger(__name__)


class DocumentProcessingUnavailableError(Exception):
    """
    Raised when an external document-processing dependency
    is temporarily unavailable.
    """


class DocumentProcessingService:

    def __init__(
        self,
        classifier: DocumentClassifier | None = None,
        ocr: OCRProvider | None = None,
    ) -> None:
        self.classifier = classifier or GeminiDocumentClassifier()
        self.ocr = ocr or get_ocr_provider()

    def process_document(
        self,
        file_path: str | Path,
    ) -> DocumentProcessingResponse:

        try:
            classification = self.classifier.classify(file_path)

        except ServerError as exc:
            logger.exception(
                "Gemini classification service error."
            )

            raise DocumentProcessingUnavailableError(
                "The document processing service is temporarily unavailable."
            ) from exc

        if not classification.supported:
            return DocumentProcessingResponse(
                success=False,
                document_type=classification.document_type,
                supported=False,
                message="Document type is not currently supported.",
            )

        handler = get_handler(
            classification.document_type,
            ocr=self.ocr,
        )

        if handler is None:
            return DocumentProcessingResponse(
                success=False,
                document_type=classification.document_type,
                supported=True,
                message=(
                    "Document type is supported, "
                    "but no handler is registered."
                ),
            )

        try:
            result = handler.process(file_path)
        except OCRProcessingError as exc:
            logger.warning(
                "OCR could not extract readable text from document: %s",
                file_path,
            )

            return DocumentProcessingResponse(
                success=False,
                document_type=classification.document_type,
                supported=True,
                message=str(exc),
            )



        return DocumentProcessingResponse(
            success=True,
            document_type=classification.document_type,
            supported=True,
            extracted_data=result.extracted_data,
            validation=result.validation,
            ocr_text=result.ocr_text,
        )