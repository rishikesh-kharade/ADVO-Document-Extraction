from pathlib import Path
from unittest.mock import MagicMock, patch

from app.document_understanding.classification.gemini_classifier import (
    GeminiClassificationResponse,
    GeminiDocumentClassifier,
)
from app.document_understanding.models.documents import DocumentType


def create_test_file(tmp_path: Path, filename: str) -> Path:
    file_path = tmp_path / filename
    file_path.write_bytes(b"fake document content")
    return file_path


def test_gemini_classifier_returns_pan(tmp_path):
    file_path = create_test_file(tmp_path, "sample_pan.jpg")

    mock_response = MagicMock()
    mock_response.parsed = GeminiClassificationResponse(
        document_type=DocumentType.PAN_CARD
    )

    with patch(
        "app.document_understanding.classification.gemini_classifier.genai.Client"
    ) as mock_client:

        mock_client.return_value.models.generate_content.return_value = (
            mock_response
        )

        classifier = GeminiDocumentClassifier()
        result = classifier.classify(file_path)

    assert result.document_type == DocumentType.PAN_CARD
    assert result.supported is True


def test_gemini_classifier_returns_aadhaar(tmp_path):
    file_path = create_test_file(tmp_path, "sample_aadhaar.jpg")

    mock_response = MagicMock()
    mock_response.parsed = GeminiClassificationResponse(
        document_type=DocumentType.AADHAAR_CARD
    )

    with patch(
        "app.document_understanding.classification.gemini_classifier.genai.Client"
    ) as mock_client:

        mock_client.return_value.models.generate_content.return_value = (
            mock_response
        )

        classifier = GeminiDocumentClassifier()
        result = classifier.classify(file_path)

    assert result.document_type == DocumentType.AADHAAR_CARD
    assert result.supported is True


def test_gemini_classifier_returns_unknown(tmp_path):
    file_path = create_test_file(tmp_path, "unknown.jpg")

    mock_response = MagicMock()
    mock_response.parsed = GeminiClassificationResponse(
        document_type=DocumentType.UNKNOWN
    )

    with patch(
        "app.document_understanding.classification.gemini_classifier.genai.Client"
    ) as mock_client:

        mock_client.return_value.models.generate_content.return_value = (
            mock_response
        )

        classifier = GeminiDocumentClassifier()
        result = classifier.classify(file_path)

    assert result.document_type == DocumentType.UNKNOWN
    assert result.supported is False