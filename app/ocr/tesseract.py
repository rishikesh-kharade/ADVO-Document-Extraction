from app.config.settings import TESSERACT_PATH
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
import pytesseract

from app.ocr.base import OCRProvider
from app.ocr.preprocessing import create_ocr_variants
from app.ocr.scoring import score_ocr_text, rank_ocr_candidates


@dataclass
class OCRCandidate:
    variant_name: str
    psm_mode: int
    text: str
    score: float

class TesseractOCR(OCRProvider):

    def __init__(self, tesseract_path: str = TESSERACT_PATH):
        self.tesseract_path = tesseract_path
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def extract_text(self, image: Image.Image, variant_name: str = "adaptive", psm_mode: int = 6, rotate_180: bool = False,) -> str:

        if rotate_180:
            image = image.rotate(180, expand=True)

        variants = create_ocr_variants(image)

        if variant_name not in variants:
            raise ValueError(
                f"Unknown OCR variant: {variant_name}"
            )

        selected_image = variants[variant_name]

        return pytesseract.image_to_string(selected_image, config=f"--psm {psm_mode}",)

    def extract_candidates(
            self,
            image: Image.Image,
            variant_names: tuple[str, ...] = (
                    "grayscale",
                    "otsu",
                    "adaptive",
            ),
            psm_modes: tuple[int, ...] = (
                    3,
                    6,
                    11,
            ),
            rotate_180: bool = False,
    ) -> list[OCRCandidate]:

        if rotate_180:
            image = image.rotate(180, expand=True)

        variants = create_ocr_variants(image)

        candidates = []

        for variant_name in variant_names:

            if variant_name not in variants:
                raise ValueError(
                    f"Unknown OCR variant: {variant_name}"
                )

            selected_image = variants[variant_name]

            for psm_mode in psm_modes:
                text = pytesseract.image_to_string(
                    selected_image,
                    config=f"--psm {psm_mode}",
                )

                candidates.append(
                    OCRCandidate(
                        variant_name=variant_name,
                        psm_mode=psm_mode,
                        text=text,
                        score=score_ocr_text(text),
                    )
                )

        return candidates

    def extract_best_candidate(
            self,
            image = Image.Image,
            variant_names: tuple[str, ...] = (
                    "grayscale",
                    "otsu",
                    "adaptive",
            ),
            psm_modes: tuple[int, ...] =( 3,6,11,),
            rotate_180: bool=False,
    ) -> OCRCandidate:
        candidates = self.extract_candidates(
            image = image,
            variant_names = variant_names,
            psm_modes = psm_modes,
            rotate_180 = rotate_180,
        )

        ranked_candidates = rank_ocr_candidates(candidates)

        return ranked_candidates[0]

    def extract_text_from_file(self, image_path: str, variant_name: str = "adaptive", psm_mode: int = 6, rotate_180: bool = False,) -> str:

            path = Path(image_path)

            if not path.exists():
                raise FileNotFoundError(
                    f"Image not found: {image_path}"
                )

            with Image.open(path) as image:
                return self.extract_text(image = image, variant_name = variant_name, psm_mode = psm_mode, rotate_180 = rotate_180)


    def extract_candidates_from_file(
            self,
            image_path: str,
            variant_names: tuple[str, ...] =("grayscale","otsu", "adaptive",),
            psm_modes: tuple[int, ...] =( 3,6,11,),
            rotate_180: bool=False,) -> list[OCRCandidate]:
            path = Path(image_path)

            if not path.exists():
               raise FileNotFoundError(
                   f"Image not found: {image_path}"
               )

            with Image.open(path) as image:
                return self.extract_candidates(
                    image = image,
                    variant_names = variant_names,
                    psm_modes = psm_modes,
                    rotate_180 = rotate_180,
                )


