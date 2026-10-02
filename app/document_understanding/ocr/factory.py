from app.config.settings import OCR_PROVIDER
from app.document_understanding.ocr.base import OCRProvider
from app.document_understanding.ocr.gemini import GeminiOCRProvider
from app.document_understanding.ocr.paddle import PaddleOCRProvider
from app.document_understanding.ocr.tesseract import TesseractOCRProvider


def get_ocr_provider() -> OCRProvider:
    if OCR_PROVIDER == "gemini":
        return GeminiOCRProvider()

    if OCR_PROVIDER == "paddle":
        return PaddleOCRProvider()

    if OCR_PROVIDER == "tesseract":
        return TesseractOCRProvider()

    raise ValueError(
        f"Unsupported OCR_PROVIDER: {OCR_PROVIDER!r}. "
        "Expected one of: gemini, paddle, tesseract."
    )