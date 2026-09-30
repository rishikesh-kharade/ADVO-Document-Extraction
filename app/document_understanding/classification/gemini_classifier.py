from pathlib import Path
import mimetypes

from pydantic import BaseModel
from google import genai
from google.genai import types

from app.config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_THINKING_LEVEL,
)
from app.document_understanding.classification.base import (
    DocumentClassifier,
)
from app.document_understanding.classification.prompts import (
    DOCUMENT_CLASSIFICATION_PROMPT,
)
from app.document_understanding.models.documents import (
    ClassificationResult,
    DocumentType,
)
from app.document_understanding.registry import (
    get_document_definition,
)


class GeminiClassificationResponse(BaseModel):
    document_type: DocumentType


def _get_mime_type(file_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(file_path.name)

    if mime_type:
        return mime_type

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
    }

    mime_type = mime_types.get(file_path.suffix.lower())

    if not mime_type:
        raise ValueError(
            f"Could not determine MIME type: {file_path}"
        )

    return mime_type

class GeminiDocumentClassifier(
    DocumentClassifier
):

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

        mime_type = _get_mime_type(file_path)

        return types.Part.from_bytes(
            data=file_path.read_bytes(),
            mime_type=mime_type,
        )

    def classify(
        self,
        file_path: str | Path,
    ) -> ClassificationResult:

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
                DOCUMENT_CLASSIFICATION_PROMPT,
                file_part,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=(
                    GeminiClassificationResponse
                ),
                thinking_config=(
                    types.ThinkingConfig(
                        thinking_level=(
                            GEMINI_THINKING_LEVEL
                        )
                    )
                ),
            ),
        )

        parsed = getattr(
            response,
            "parsed",
            None,
        )

        if parsed is not None:
            result = (
                parsed
                if isinstance(
                    parsed,
                    GeminiClassificationResponse,
                )
                else GeminiClassificationResponse.model_validate(
                    parsed
                )
            )
        else:
            result = (
                GeminiClassificationResponse.model_validate_json(
                    response.text
                )
            )

        definition = get_document_definition(
            result.document_type
        )

        supported = (
            definition is not None
            and definition.supported
        )

        return ClassificationResult(
            document_type=result.document_type,
            supported=supported,
        )