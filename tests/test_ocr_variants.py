from pathlib import Path

from PIL import Image

from app.ocr import create_ocr_variants
import pytesseract


def test_ocr_variants():

    image_path = Path("tests/data/sample.png")

    with Image.open(image_path) as image:

        variants = create_ocr_variants(image)

        output_dir = Path("tests/data/ocr_variants")

        output_dir.mkdir(parents=True, exist_ok=True,)

        for name, processed_image in variants.items():

            # Save image so we can inspect it

            output_path = (output_dir / f"{name}.png")
            processed_image.save(output_path)

            # Run OCR
            text = pytesseract.image_to_string(processed_image)
            print(f"\n===== {name.upper()} =====")

            print(text)

            # We don't fail the whole experiment
            # if one preprocessing method produces
            # no text.

            if not text.strip():
                print(f"[Warning] {name} produced no OCR text.")


def test_ocr_psm():

    image_path = Path("tests/data/sample.png")
    with Image.open(image_path) as image:
        variants = create_ocr_variants(image)

        # Use the preprocessing that worked
        image = variants["adaptive"]

        for psm in [3, 6, 11]:

            text = pytesseract.image_to_string(image, config=f"--psm {psm}",)
            print(f"\n=== ADAPTIVE + PSM {psm} ===")
            print(text)
