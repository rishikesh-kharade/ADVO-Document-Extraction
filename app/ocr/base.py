from abc import ABC, abstractmethod
from PIL import Image


class OCRProvider(ABC):

    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Extract text from an image."""
        raise NotImplementedError

