import base64
from pathlib import Path
from pydantic import ValidationError

from google import genai

from app.config.settings import GEMINI_API_KEY, GEMINI_MODEL
from app.document_understanding.classification.document_classifier import (
    DocumentClassifier,
)
from app.document_understanding.classification.classification_result import (
    ClassificationResult,
)
from app.document_understanding.classification.document_registry import (
    DOCUMENT_REGISTRY,
    get_document_definition,
)
from app.document_understanding.classification.gemini_response import (
    GeminiClassificationResponse,
)
from app.document_understanding.classification.prompts import (
DOCUMENT_CLASSIFICATION_PROMPT,
)


class GeminiDocumentClassifier(DocumentClassifier):

    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def classify(
        self,
        image_path: str | Path,
    ) -> ClassificationResult:

        image_path = Path(image_path)

        image_bytes = image_path.read_bytes()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = DOCUMENT_CLASSIFICATION_PROMPT

        interaction = self.client.interactions.create(
            model=self.model,
            input=[
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image",
                    "data": image_base64,
                    "mime_type": self._get_mime_type(image_path),
                },
            ],
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": GeminiClassificationResponse.model_json_schema(),
            },
        )

        try:
            gemini_result = GeminiClassificationResponse.model_validate_json(
                interaction.output_text
            )
        except ValidationError:
            return ClassificationResult(
                document_type= "UNKNOWN",
                supported=False,
            )

        document_type = gemini_result.document_type.strip().upper()

        if not document_type:
            return ClassificationResult(
                document_type="UNKNOWN",
                supported=False,
            )

        if document_type == "UNKNOWN":
            return ClassificationResult(
                document_type="UNKNOWN",
                supported=False,
            )

        definition = get_document_definition(document_type)

        return ClassificationResult(
            document_type=document_type,
            supported=definition.supported if definition else False,
        )

    @staticmethod
    def _get_mime_type(image_path: Path) -> str:
        image_bytes = image_path.read_bytes()

        # JPEG signature: FF D8 FF
        if image_bytes.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"

        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        if image_bytes.startswith(
                b"\x89PNG\r\n\x1a\n"
        ):
            return "image/png"

        # WEBP files start with RIFF and contain WEBP at byte 8
        if (
                image_bytes.startswith(b"RIFF")
                and image_bytes[8:12] == b"WEBP"
        ):
            return "image/webp"

        # Fall back to the file extension.
        suffix = image_path.suffix.lower()

        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }

        return mime_types.get(
            suffix,
            "application/octet-stream",
        )