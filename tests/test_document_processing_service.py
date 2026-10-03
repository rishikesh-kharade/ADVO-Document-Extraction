from pathlib import Path

from app.document_understanding.models.documents import (
    ClassificationResult,
    DocumentProcessingResponse,
    DocumentType,
    OCRResult,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)


class FakeClassifier:
    def __init__(self, result: ClassificationResult):
        self.result = result
        self.called_with = None

    def classify(self, file_path: str | Path) -> ClassificationResult:
        self.called_with = file_path
        return self.result


class FakeOCR:
    def extract_text(self, file_path: str | Path) -> OCRResult:
        return OCRResult(
            text="fake OCR text"
        )


def test_service_returns_unsupported_document_without_handler():
    classifier = FakeClassifier(
        ClassificationResult(
            document_type=DocumentType.UNSUPPORTED,
            supported=False,
        )
    )

    service = DocumentProcessingService(
        classifier=classifier,
        ocr=FakeOCR(),
    )

    result = service.process_document(
        "fake-document.jpg"
    )

    assert isinstance(
        result,
        DocumentProcessingResponse,
    )

    assert result.success is False
    assert result.supported is False
    assert result.document_type == DocumentType.UNSUPPORTED
    assert result.extracted_data is None
    assert result.validation is None


def test_service_routes_supported_pan_to_handler():
    classifier = FakeClassifier(
        ClassificationResult(
            document_type=DocumentType.PAN_CARD,
            supported=True,
        )
    )

    service = DocumentProcessingService(
        classifier=classifier,
        ocr=FakeOCR(),
    )

    result = service.process_document(
        "fake-pan.jpg"
    )

    assert isinstance(
        result,
        DocumentProcessingResponse,
    )

    assert result.success is True
    assert result.supported is True
    assert result.document_type == DocumentType.PAN_CARD
    assert result.extracted_data is not None
    assert result.validation is not None
    assert result.ocr_text == "fake OCR text"


def test_service_routes_supported_aadhaar_to_handler():
    classifier = FakeClassifier(
        ClassificationResult(
            document_type=DocumentType.AADHAAR_CARD,
            supported=True,
        )
    )

    service = DocumentProcessingService(
        classifier=classifier,
        ocr=FakeOCR(),
    )

    result = service.process_document(
        "fake-aadhaar.jpg"
    )

    assert result.success is True
    assert result.supported is True
    assert result.document_type == DocumentType.AADHAAR_CARD
    assert result.extracted_data is not None
    assert result.validation is not None


def test_service_routes_supported_passbook_to_handler():
    classifier = FakeClassifier(
        ClassificationResult(
            document_type=DocumentType.BANK_PASSBOOK,
            supported=True,
        )
    )

    service = DocumentProcessingService(
        classifier=classifier,
        ocr=FakeOCR(),
    )

    result = service.process_document(
        "fake-passbook.jpg"
    )

    assert result.success is True
    assert result.supported is True
    assert result.document_type == DocumentType.BANK_PASSBOOK
    assert result.extracted_data is not None
    assert result.validation is not None


def test_service_routes_supported_cheque_to_handler():
    classifier = FakeClassifier(
        ClassificationResult(
            document_type=DocumentType.CHEQUE,
            supported=True,
        )
    )

    service = DocumentProcessingService(
        classifier=classifier,
        ocr=FakeOCR(),
    )

    result = service.process_document(
        "fake-cheque.jpg"
    )

    assert result.success is True
    assert result.supported is True
    assert result.document_type == DocumentType.CHEQUE
    assert result.extracted_data is not None
    assert result.validation is not None