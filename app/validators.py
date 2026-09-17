import re

from app.extractors import PAN_PATTERN, AADHAAR_PATTERN

PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")

def validate_pan_number(pan_number: str | None) -> bool:
    """
    Validate PAN number format.

    Expected format:
    5 letters + 4 digits + 1 letter

    Example:
    ABCDE1234F
    """

    if not pan_number:
        return False

    pan_number = pan_number.strip().upper()
    return bool(PAN_PATTERN.fullmatch(pan_number))

AADHAAR_PATTERN = re.compile(r"^\d{12}$")

def validate_aadhaar_format(aadhaar_number: str | None) -> bool:
    """
    Validate Aadhaar number format.

    Aadhaar must contain exactly 12 digits.
    """

    if not aadhaar_number:
        return False

    aadhaar_number = aadhaar_number.strip()

    return bool(AADHAAR_PATTERN.fullmatch(aadhaar_number))


# Verhoeff algorithm tables
VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]


def validate_aadhaar_verhoeff(aadhar_number: str | None) -> bool:
    """
    Validate a 12-digit number using the Verhoeff checksum.
    """

    if not aadhar_number:
        return False

    number = aadhar_number.strip()

    if not number.isdigit():
        return False

    if len(number) != 12:
        return False

    checksum = 0

    for position, digit in enumerate(reversed(number)):
        checksum = VERHOEFF_D[
            checksum
        ][
            VERHOEFF_P[position % 8][int(digit)]
        ]

    return checksum == 0


ACCOUNT_PATTERN = re.compile(r"^\d{9,18}$")

IFSC_PATTERN = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")

def validate_account_number(account_number: str | None) -> bool:
    """
    Validate bank account number format.

    Expected:
    9 to 18 digits.
    """

    if not account_number:
        return False

    account_number = account_number.strip()

    return bool(ACCOUNT_PATTERN.fullmatch(account_number))


def validate_ifsc(ifsc: str | None) -> bool:
    """
    Validate IFSC format.

    Expected:
    4 letters + 0 + 6 letters/numbers.

    Example:
    SBIN0001234
    """

    if not ifsc:
        return False

    ifsc = ifsc.strip().upper()

    return bool(IFSC_PATTERN.fullmatch(ifsc))