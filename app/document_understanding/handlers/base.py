from abc import ABC, abstractmethod
from pathlib import Path

from app.document_understanding.models.documents import (
    DocumentHandlerResult,
)
from app.document_understanding.ocr.base import (
    OCRProvider,
)


class DocumentHandler(ABC):

    def __init__(
        self,
        ocr: OCRProvider,
    ) -> None:

        self.ocr = ocr

    @abstractmethod
    def process(
        self,
        file_path: str | Path,
    ) -> DocumentHandlerResult:
        raise NotImplementedError