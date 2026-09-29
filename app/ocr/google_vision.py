from pathlib import Path

from google.cloud import vision

from app.ocr.base import OCRProvider


class GoogleVisionOCR(OCRProvider):
    """
    Google Cloud Vision OCR provider.

    Uses DOCUMENT_TEXT_DETECTION for document-oriented OCR.
    """

    def __init__(self) -> None:
        self.client = vision.ImageAnnotatorClient()

    def extract_text_from_file(
        self,
        image_path: str | Path,
    ) -> str:
        image_path = Path(image_path)

        content = image_path.read_bytes()

        image = vision.Image(
            content=content,
        )

        response = self.client.document_text_detection(
            image=image,
        )

        if response.error.message:
            raise RuntimeError(
                response.error.message
            )

        if response.full_text_annotation:
            return (
                response
                .full_text_annotation
                .text
            )

        return ""