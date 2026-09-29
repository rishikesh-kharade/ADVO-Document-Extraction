from pathlib import Path

from app.document_understanding.handlers.pan import PanDocumentHandler
from app.document_understanding.models.documents import (
    OCRResult,
)


class FakeOCR:
    def extract_text(self, file_path: str | Path) -> OCRResult:
        return OCRResult(
            text="""
            INCOME TAX DEPARTMENT

            Permanent Account Number Card

            ABCDE1234F

            Name
            ROHIT KUMAR

            Father's Name
            SURESH KUMAR

            Date of Birth
            15/08/1990

            Date of Issue
            20/05/2024
            """
        )


def test_pan_handler():
    handler = PanDocumentHandler(
        ocr=FakeOCR(),
    )

    result = handler.process(
        Path("tests/data/Pan_Sample.jpg"),
    )

    assert result.extracted_data is not None

    assert result.extracted_data["pan_number"] == "ABCDE1234F"
    assert result.extracted_data["name"] == "ROHIT KUMAR"
    assert result.extracted_data["father_name"] == "SURESH KUMAR"
    assert result.extracted_data["dob"] == "15/08/1990"

    assert result.validation.valid is True