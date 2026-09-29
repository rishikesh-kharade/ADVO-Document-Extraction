import os

import pytest

from app.document_understanding.ocr.gemini import GeminiOCR


@pytest.mark.integration
def test_gemini_ocr_real_pan():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not configured.")

    ocr = GeminiOCR()

    image_path = "tests/data/Pan_Sample.jpg"

    result = ocr.extract_text(image_path)

    print("\n===== GEMINI OCR RESULT =====")
    print(result.text)
    print("=============================\n")

    assert result.text
    assert len(result.text.strip()) > 20