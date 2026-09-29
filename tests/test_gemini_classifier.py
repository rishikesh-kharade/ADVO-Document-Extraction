from unittest.mock import MagicMock, patch

from app.document_understanding.classification.gemini_classifier import (
    GeminiDocumentClassifier,
)

from app.document_understanding.classification.gemini_response import (
    GeminiClassificationResponse,
)

@patch(
    "app.document_understanding.classification.gemini_classifier.Path.read_bytes"
)
@patch(
    "app.document_understanding.classification.gemini_classifier.genai.Client"
)
def test_gemini_classifies_pan_card(mock_client, mock_read_bytes):
    mock_read_bytes.return_value = b"fake-image-data"

    mock_interaction = MagicMock()
    mock_interaction.output_text = '{"document_type": "PAN_CARD"}'

    mock_client.return_value.interactions.create.return_value = (
        mock_interaction
    )

    with patch(
        "app.document_understanding.classification.gemini_classifier.GEMINI_API_KEY",
        "test-api-key",
    ):
        classifier = GeminiDocumentClassifier()

    result = classifier.classify("dummy.jpg")

    assert result.document_type == "PAN_CARD"
    assert result.supported is True


def test_gemini_classification_response():
    response = GeminiClassificationResponse(
        document_type="PAN_CARD"
    )

    assert response.document_type == "PAN_CARD"