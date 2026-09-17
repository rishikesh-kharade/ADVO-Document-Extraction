from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops
import pytesseract


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")

    background = Image.new(
        "RGB",
        image.size,
        image.getpixel((0, 0)),
    )

    difference = ImageChops.difference(image, background)
    bbox = difference.getbbox()

    if bbox:
        image = image.crop(bbox)

    target_width = 1800

    if image.width < target_width:
        scale = target_width / image.width
        new_height = int(image.height * scale)

        image = image.resize(
            (target_width, new_height),
            Image.Resampling.LANCZOS,
        )

    return image


def create_ocr_variants(image: Image.Image) -> dict[str, Image.Image]:
    image = preprocess_image(image)

    image_array = np.array(image)

    gray = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2GRAY,
    )

    _, otsu = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return {
        "grayscale": Image.fromarray(gray),
        "otsu": Image.fromarray(otsu),
        "adaptive": Image.fromarray(adaptive),
    }


def extract_text_from_image(
    image_path: str,
    variant_name: str = "grayscale",
    psm_mode: int = 3,
    rotate_180: bool = False,
) -> str:
    """
    Extract text using a selected preprocessing variant and layout mode.

    Defaults preserve the proven PAN and Aadhaar configuration.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    with Image.open(path) as image:
        if rotate_180:
            image = image.transpose(
                Image.Transpose.ROTATE_180
            )

        variants = create_ocr_variants(image)

        if variant_name not in variants:
            raise ValueError(
                f"Unknown OCR variant: {variant_name}"
            )

        return pytesseract.image_to_string(
            variants[variant_name],
            config=f"--oem 3 --psm {psm_mode}",
        )