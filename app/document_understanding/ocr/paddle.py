from pathlib import Path

from paddleocr import PaddleOCR

from app.document_understanding.models.documents import OCRResult
from app.document_understanding.ocr.base import OCRProvider, OCRProcessingError


class PaddleOCRProvider(OCRProvider):
    """Local OCR provider backed by PaddleOCR."""

    def __init__(
        self,
        lang: str = "hi",
    ) -> None:
        self.lang = lang
        self._ocr: PaddleOCR | None = None

    @property
    def ocr(self) -> PaddleOCR:
        """Create the PaddleOCR engine only when OCR is actually needed."""
        if self._ocr is None:
            self._ocr = PaddleOCR(
                lang=self.lang,
            )

        return self._ocr

    def extract_text(
        self,
        file_path: str | Path,
    ) -> OCRResult:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        result = self.ocr.predict(str(path))

        texts: list[str] = []

        for page_result in result:
            rec_texts = page_result.get("rec_texts", [])

            for text in rec_texts:
                if text and text.strip():
                    texts.append(text.strip())

        text = "\n".join(texts)

        if not text:
            raise OCRProcessingError(
                "PaddleOCR could not extract readable text from the document."
            )

        return OCRResult(
            text=text
        )