from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class DocumentHandlerResult(BaseModel):
    extracted_data: dict | None = None
    validation: dict = {}
    ocr_text: str | None = None


class DocumentHandler(ABC):

    @abstractmethod
    def process(
        self,
        file_path: str | Path,
    ) -> DocumentHandlerResult:
        raise NotImplementedError