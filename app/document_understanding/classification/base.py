from abc import ABC, abstractmethod
from pathlib import Path

from app.document_understanding.models.documents import (
    ClassificationResult,
)


class DocumentClassifier(ABC):

    @abstractmethod
    def classify(
        self,
        file_path: str | Path,
    ) -> ClassificationResult:
        raise NotImplementedError