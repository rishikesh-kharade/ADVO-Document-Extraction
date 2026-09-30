from pathlib import Path

from app.document_understanding.models.documents import OCRResult
from app.document_understanding.ocr.paddle import PaddleOCRProvider


PAN_SAMPLE = Path("tests/data/Pan_Sample.jpg")


def test_paddle_ocr_provider_extracts_text() -> None:
    provider = PaddleOCRProvider()

    result = provider.extract_text(PAN_SAMPLE)

    assert isinstance(result, OCRResult)
    assert result.text
    assert len(result.text) > 20