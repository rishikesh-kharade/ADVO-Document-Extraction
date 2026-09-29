from pathlib import Path

from app.document_understanding.classification.classification_result import (
    ClassificationResult,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)


class FakePanClassifier:

    def classify(self, file_path):
        return ClassificationResult(
            document_type="PAN_CARD",
            supported=True,
        )


def test_service_uses_pan_handler():

    image_path = Path(
        "tests/data/Pan_Sample.jpg"
    )

    service = DocumentProcessingService(
        classifier=FakePanClassifier(),
    )

    result = service.process_document(
        image_path,
    )

    print("\n==============================")
    print("SERVICE RESULT")
    print("==============================")
    print(result)

    assert result["success"] is True

    assert (
        result["document"]["document_type"]
        == "PAN_CARD"
    )

    assert (
        result["document"]["supported"]
        is True
    )

    assert result["extracted_data"] is not None

    assert (
        result["extracted_data"]["pan_number"]
        is not None
    )

    assert (
        result["extracted_data"]["name"]
        is not None
    )

    assert (
        result["validation"]["valid"]
        is True
    )