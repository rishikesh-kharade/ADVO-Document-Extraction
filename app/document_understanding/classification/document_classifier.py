from abc import ABC, abstractmethod
from pathlib import Path

from .classification_result import ClassificationResult


class DocumentClassifier(ABC):
    @abstractmethod
    def classify(
        self,
        image_path: str | Path,
    ) -> ClassificationResult:
        raise NotImplementedError