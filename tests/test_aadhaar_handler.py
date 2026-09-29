from pathlib import Path

from app.document_understanding.handlers.aadhaar import (
    AadhaarDocumentHandler,
)
from app.document_understanding.models.documents import OCRResult


class FakeOCR:
    def extract_text(self, file_path: str | Path) -> OCRResult:
        return OCRResult(
            text="""
            Government of India

            1234 5678 9017
            ROHIT KUMAR
            Date of Birth: 15/08/1990
            Male
            Address: 123 Main Street, Bengaluru, Karnataka
            """
        )


def test_aadhaar_handler():
    handler = AadhaarDocumentHandler(
        ocr=FakeOCR(),
    )

    result = handler.process(
        Path("tests/data/aadhaar_xerox_sample.webp"),
    )

    assert result.extracted_data is not None

    assert (
        result.extracted_data["aadhar_number"]
        == "123456789017"
    )

    assert (
        result.extracted_data["name"]
        == "ROHIT KUMAR"
    )

    assert (
        result.extracted_data["dob"]
        == "15/08/1990"
    )

    assert result.validation.valid is True