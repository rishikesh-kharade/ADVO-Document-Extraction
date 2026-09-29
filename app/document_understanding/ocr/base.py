from abc import ABC, abstractmethod
from pathlib import Path

from app.document_understanding.models.documents import (
    OCRResult,
)


class OCRProvider(ABC):

    @abstractmethod
    def extract_text(
        self,
        file_path: str | Path,
    ) -> OCRResult:
        raise NotImplementedError