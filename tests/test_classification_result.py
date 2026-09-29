from app.document_understanding.models.documents import (
    ClassificationResult,
    DocumentType,
)


def test_supported_pan_card():
    result = ClassificationResult(
        document_type=DocumentType.PAN_CARD,
        supported=True,
    )

    assert result.document_type == DocumentType.PAN_CARD
    assert result.supported is True


def test_unsupported_document():
    result = ClassificationResult(
        document_type=DocumentType.UNSUPPORTED,
        supported=False,
    )

    assert result.document_type == DocumentType.UNSUPPORTED
    assert result.supported is False


def test_unknown_document():
    result = ClassificationResult(
        document_type=DocumentType.UNKNOWN,
        supported=False,
    )

    assert result.document_type == DocumentType.UNKNOWN
    assert result.supported is False