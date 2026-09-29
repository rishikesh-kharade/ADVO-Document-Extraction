from pathlib import Path
import mimetypes

from google import genai
from google.genai import types

from app.config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_THINKING_LEVEL,
)
from app.document_understanding.models.documents import (
    OCRResult,
)
from app.document_understanding.ocr.base import (
    OCRProvider,
)


from app.document_understanding.ocr.prompts import GEMINI_OCR_PROMPT


class GeminiOCR(OCRProvider):

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

    def _build_file_part(
        self,
        file_path: Path,
    ) -> types.Part:

        mime_type, _ = mimetypes.guess_type(
            file_path.name
        )

        if not mime_type:
            raise ValueError(
                f"Could not determine MIME type: "
                f"{file_path}"
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

        file_part = self._build_file_part(
            path
        )

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

        text = getattr(
            response,
            "text",
            None,
        )

        if not text:
            raise ValueError(
                "Gemini OCR returned no text."
            )

        return OCRResult(
            text=text.strip()
        )