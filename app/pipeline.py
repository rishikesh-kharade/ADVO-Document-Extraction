from app.extractors import (
    extract_aadhaar,
    extract_bank_passbook,
    extract_pan,
    extract_cancelled_cheque
)
from app.ocr import extract_text_from_image
from app.validators import (
    validate_aadhaar_format,
    validate_aadhaar_verhoeff,
    validate_account_number,
    validate_ifsc,
    validate_pan_number,
)


def process_pan_document(image_path: str) -> dict:
    """
    Process a PAN image from OCR through extraction and validation.
    """

    ocr_text = extract_text_from_image(image_path)
    document = extract_pan(ocr_text)

    return {
        "document": document,
        "is_valid": validate_pan_number(
            document.pan_number
        ),
        "ocr_text": ocr_text,
    }


def process_aadhaar_document(image_path: str) -> dict:
    """
    Process an Aadhaar image from OCR through extraction and validation.
    """

    ocr_text = extract_text_from_image(image_path)
    document = extract_aadhaar(ocr_text)

    is_format_valid = validate_aadhaar_format(
        document.aadhar_number
    )

    is_checksum_valid = validate_aadhaar_verhoeff(
        document.aadhar_number
    )

    return {
        "document": document,
        "is_format_valid": is_format_valid,
        "is_checksum_valid": is_checksum_valid,
        "is_valid": (
            is_format_valid
            and is_checksum_valid
        ),
        "ocr_text": ocr_text,
    }


def process_bank_passbook_document(
    image_path: str,
) -> dict:
    """
    Process an upright passbook image through OCR and validation.
    """

    ocr_text = extract_text_from_image(
        image_path,
        variant_name="adaptive",
        psm_mode=3,
    )

    document = extract_bank_passbook(ocr_text)

    is_account_number_valid = validate_account_number(
        document.account_number
    )

    is_ifsc_valid = validate_ifsc(document.ifsc)

    return {
        "document": document,
        "is_account_number_valid": (
            is_account_number_valid
        ),
        "is_ifsc_valid": is_ifsc_valid,
        "is_valid": (
            is_account_number_valid
            and is_ifsc_valid
        ),
        "ocr_text": ocr_text,
    }

def process_cancelled_cheque_document(
    image_path: str,
) -> dict:
    """
    Process a cancelled-cheque image through OCR and validation.
    """

    ocr_text = extract_text_from_image(image_path)
    document = extract_cancelled_cheque(ocr_text)

    is_account_number_valid = validate_account_number(
        document.account_number
    )

    is_ifsc_valid = validate_ifsc(document.ifsc)

    return {
        "document": document,
        "is_account_number_valid": (
            is_account_number_valid
        ),
        "is_ifsc_valid": is_ifsc_valid,
        "is_valid": (
            is_account_number_valid
            and is_ifsc_valid
        ),
        "ocr_text": ocr_text,
    }