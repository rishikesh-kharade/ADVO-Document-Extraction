from pathlib import Path

from app.document_understanding.handlers.pan import (
    PanDocumentHandler,
)
from app.ocr.tesseract import TesseractOCR


def test_pan_handler():

    image_path = Path(
        "tests/data/Pan_Sample.jpg"
    )

    ocr = TesseractOCR()

    handler = PanDocumentHandler(
        ocr=ocr,
    )

    result = handler.process(
        image_path,
    )

    print("\n==============================")
    print("PAN HANDLER RESULT")
    print("==============================")
    print(result.model_dump())

    assert result.extracted_data is not None

    assert (
        result.extracted_data["pan_number"]
        is not None
    )

    assert (
        result.extracted_data["name"]
        is not None
    )

    assert (
        result.extracted_data["father_name"]
        is not None
    )

    assert (
        result.extracted_data["dob"]
        is not None
    )

    assert result.validation["valid"] is True