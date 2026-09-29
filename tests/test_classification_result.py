from app.document_understanding.classification.classification_result import (
    ClassificationResult,
)


def test_supported_pan_card():
    result = ClassificationResult(
        document_type = "PAN_CARD",
        supported=True,
    )

    assert result.document_type == "PAN_CARD"
    assert result.supported is True


def test_unsupported_document():
    result = ClassificationResult(
        document_type= "PASSPORT",
        supported=False,
    )

    assert result.document_type == "PASSPORT"
    assert result.supported is False

def test_unknown_document():
    result = ClassificationResult(
        document_type= "UNKNOWN",
        supported=False,
    )

    assert result.document_type == "UNKNOWN"
    assert result.supported is False