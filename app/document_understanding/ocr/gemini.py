from pathlib import Path
import mimetypes

from google import genai
from google.genai import types

from app.config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_THINKING_LEVEL,
)
from app.document_understanding.models.documents import OCRResult
from app.document_understanding.ocr.base import (
    OCRProvider,
    OCRProcessingError,
)


GEMINI_OCR_PROMPT = """
You are the OCR engine for an automated document
verification system.

Read the supplied document image or PDF and transcribe
ALL visible text.

CRITICAL RULES:

1. Extract everything that is visibly readable.
2. Do not guess.
3. Do not invent missing information.
4. Do not correct OCR-like spelling into a guessed value.
5. Preserve numbers exactly as visible.
6. Preserve dates exactly as visible.
7. Preserve names exactly as visible.
8. Preserve account numbers, IFSC codes, PAN numbers,
   Aadhaar numbers, enrollment numbers and mobile numbers.
9. Preserve labels and their values.
10. Preserve address lines and their order.
11. Preserve line breaks where reasonably possible.
12. Include document titles and headings.
13. Include text in English and Indian languages when visible.
14. Include text from all visible sections of the document.
15. Do not summarize.
16. Do not classify the document.
17. Do not return structured business fields.
18. Return ONLY the OCR transcription.

For poor-quality, rotated, photocopied or partially blurred
documents, extract whatever is genuinely readable.

Never fill unreadable text by assumption.
"""


class GeminiOCRProvider(OCRProvider):
    """OCR provider backed by Gemini."""

    def __init__(
        self,
        api_key: str = GEMINI_API_KEY,
        model: str = GEMINI_MODEL,
    ) -> None:
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    @staticmethod
    def _get_mime_type(file_path: Path) -> str:
        mime_type, _ = mimetypes.guess_type(
            file_path.name
        )

        if mime_type:
            return mime_type

        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".heic": "image/heic",
            ".heif": "image/heif",
            ".pdf": "application/pdf",
        }

        mime_type = mime_types.get(
            file_path.suffix.lower()
        )

        if not mime_type:
            raise OCRProcessingError(
                f"Could not determine MIME type for: "
                f"{file_path}"
            )

        return mime_type

    def _build_file_part(
        self,
        file_path: Path,
    ) -> types.Part:
        mime_type = self._get_mime_type(
            file_path
        )

        return types.Part.from_bytes(
            data=file_path.read_bytes(),
            mime_type=mime_type,
        )

    def extract_text(
        self,
        file_path: str | Path,
    ) -> OCRResult:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        file_part = self._build_file_part(path)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    GEMINI_OCR_PROMPT,
                    file_part,
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=16000,
                    thinking_config=(
                        types.ThinkingConfig(
                            thinking_level=(
                                GEMINI_THINKING_LEVEL
                            )
                        )
                    ),
                ),
            )
        except Exception as exc:
            print(
                f"Gemini OCR error: "
                f"{type(exc).__name__}: {exc}"
            )
            raise OCRProcessingError(
                f"Gemini OCR failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        text = getattr(
            response,
            "text",
            None,
        )

        if not text or not text.strip():
            raise OCRProcessingError(
                "Gemini OCR returned no readable text."
            )

        return OCRResult(
            text=text.strip()
        )