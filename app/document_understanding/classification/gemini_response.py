from pydantic import BaseModel


class GeminiClassificationResponse(BaseModel):
    document_type: str