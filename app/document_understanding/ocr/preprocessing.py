from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps


class OCRPreprocessor:
    """Common image preprocessing for OCR."""

    TARGET_WIDTH = 1800
    MAX_SCALE = 3

    def preprocess(self, file_path: str | Path) -> Path:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        image = Image.open(path)

        # Normalize image mode for OCR.
        image = image.convert("RGB")

        # Improve contrast without aggressive thresholding.
        image = ImageOps.autocontrast(image)

        # Upscale smaller images.
        width, height = image.size

        if width < self.TARGET_WIDTH:
            scale = min(
                self.TARGET_WIDTH / width,
                self.MAX_SCALE,
            )

            new_size = (
                int(width * scale),
                int(height * scale),
            )

            image = image.resize(
                new_size,
                Image.Resampling.LANCZOS,
            )

        # Light sharpening.
        image = ImageEnhance.Sharpness(image).enhance(1.2)

        output_path = path.with_name(
            f"{path.stem}_ocr_preprocessed.png"
        )

        image.save(output_path, format="PNG")

        return output_path