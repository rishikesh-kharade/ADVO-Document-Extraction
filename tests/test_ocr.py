from pathlib import Path

from PIL import Image

from app.ocr import extract_text_from_image, preprocess_image

def test_ocr_image():

    image_path =  "tests/data/sample.png"

    # Open original image
    with Image.open(image_path) as image:
        print("\nORIGINAL SIZE:")
        print(image.size)

        #Apply preprocessing
        processed = preprocess_image(image)

        print("\nPREPROCESSED SIZE:")
        print(processed.size)

        #Save processed image so we can inspect it
        output_path = Path("tests/data/processed_sample.png")
        processed.save(output_path)

        print("\nPROCESSED IMAGE:")
        print(output_path)

    # Run OCR
    text = extract_text_from_image(image_path)

    print("\nOCR RESULT:")
    print(text)

    assert isinstance(text, str)
    assert len(text.strip()) > 0