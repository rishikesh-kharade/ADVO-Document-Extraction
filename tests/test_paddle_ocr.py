import pytest

from app.document_understanding.ocr.paddle import PaddleOCRProvider


@pytest.mark.integration
def test_paddle_ocr_real_pan():
    ocr = PaddleOCRProvider()

    image_path = "tests/data/aadhaar_sample.jpg"

    result = ocr.extract_text(image_path)

    print("\n===== PADDLE OCR RESULT =====")
    print(result.text)
    print("=============================\n")

    assert result.text
    assert len(result.text.strip()) > 20