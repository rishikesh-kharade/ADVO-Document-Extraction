from app.config.settings import TESSERACT_PATH

from app.ocr.preprocessing import (
preprocess_image, create_ocr_variants,
)

from app.ocr.tesseract import TesseractOCR



def extract_text_from_image(image_path: str, variant_name: str = "adaptive", psm_mode: int = 6, rotate_180: bool = False,) -> str:
    ocr = TesseractOCR(tesseract_path=TESSERACT_PATH,)

    return ocr.extract_text_from_file(image_path = image_path, variant_name = variant_name, psm_mode = psm_mode, rotate_180 = rotate_180,)

__all__ = ["TesseractOCR",
           "preprocess_image",
           "create_ocr_variants",
           "extract_text_from_image",
           ]