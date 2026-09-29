import cv2
import numpy as np
from PIL import Image, ImageChops


def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")

    background = Image.new("RGB", image.size, image.getpixel ((0,0)),
    )

    difference = ImageChops.difference(image, background,)

    bbox = difference.getbbox()

    if bbox:
        image = image.crop(bbox)

    target_width = 1800

    if image.width < target_width:
        scale = target_width / image.width
        new_height = int(image.height * scale)

        image = image.resize((target_width, new_height), Image.Resampling.LANCZOS,)

    return image

def create_ocr_variants(image: Image.Image, ) -> dict[str, Image.Image]:

    image = preprocess_image(image)

    image_array = np.array(image)

    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY,)

    grayscale = gray

    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,)

    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return {
        "grayscale": Image.fromarray(grayscale),
        "otsu": Image.fromarray(otsu),
        "adaptive": Image.fromarray(adaptive),
    }