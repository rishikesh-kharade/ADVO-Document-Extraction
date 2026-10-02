from pathlib import Path

from paddleocr import PaddleOCR

from app.document_understanding.models.documents import OCRResult
from app.document_understanding.ocr.base import (
    OCRProvider,
    OCRProcessingError,
)
from app.document_understanding.ocr.preprocessing import OCRPreprocessor


class PaddleOCRProvider(OCRProvider):
    """Local OCR provider backed by PaddleOCR."""

    def __init__(self, lang: str = "hi") -> None:
        self.lang = lang
        self._ocr: PaddleOCR | None = None
        self._preprocessor = OCRPreprocessor()

    @property
    def ocr(self) -> PaddleOCR:
        """Create the PaddleOCR engine only when OCR is actually needed."""
        if self._ocr is None:
            self._ocr = PaddleOCR(lang=self.lang)

        return self._ocr

    def _run_ocr(self, file_path: Path) -> str:
        """Run PaddleOCR and return extracted text."""
        result = self.ocr.predict(str(file_path))

        texts: list[str] = []

        for page_result in result:
            rec_texts = page_result.get("rec_texts", [])

            for text in rec_texts:
                if text and text.strip():
                    texts.append(text.strip())

        return "\n".join(texts)

    def extract_text(self, file_path: str | Path) -> OCRResult:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        processed_path: Path | None = None

        try:
            # First attempt: normalized/upscaled image.
            processed_path = self._preprocessor.preprocess(path)

            text = self._run_ocr(processed_path)

            # Fallback: original image.
            if not text.strip():
                text = self._run_ocr(path)

            if not text.strip():
                raise OCRProcessingError(
                    "PaddleOCR could not extract readable text from the document."
                )

            return OCRResult(text=text)

        finally:
            # Do not leave generated preprocessing files behind.
            if processed_path and processed_path.exists():
                processed_path.unlink()