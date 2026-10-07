from app.config.settings import OCR_PROVIDER
from app.document_understanding.ocr.base import OCRProvider


def get_ocr_provider() -> OCRProvider:
    if OCR_PROVIDER == "gemini":
        from app.document_understanding.ocr.gemini import (
            GeminiOCRProvider,
        )

        return GeminiOCRProvider()

    if OCR_PROVIDER == "paddle":
        from app.document_understanding.ocr.paddle import (
            PaddleOCRProvider,
        )

        return PaddleOCRProvider()

    if OCR_PROVIDER == "tesseract":
        from app.document_understanding.ocr.tesseract import (
            TesseractOCRProvider,
        )

        return TesseractOCRProvider()

    raise ValueError(
        f"Unsupported OCR_PROVIDER: {OCR_PROVIDER!r}. "
        "Expected one of: gemini, paddle, tesseract."
    )