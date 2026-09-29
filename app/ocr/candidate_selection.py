import re

from app.ocr.tesseract import OCRCandidate
from app.extractors import extract_pan
from app.validators import validate_pan_number

def is_plausible_person_name(name: str | None) -> bool:
    """
    Check whether OCR-extracted text has the basic structure
    expected from a person's name.

    This is a structural OCR-quality check, not identity verification.
    """
    if not name:
        return False

    name = name.strip()

    if not name:
        return False

    words = re.findall(r"[A-Za-z]+", name)

    if len(words) < 2:
        return False

    if any(len(word) < 2 for word in words):
        return False

    return True


def select_best_candidate(
        candidate: list[OCRCandidate],
) -> OCRCandidate:
    if not candidate:
        raise ValueError("No OCR candidate available")

    return max(candidate, key=lambda candidate: candidate.score)


def evaluate_pan_candidate(
    candidate: OCRCandidate,
) -> float:
    """
    Calculate a document-aware score for a PAN OCR candidate.

    The score combines the generic OCR score with PAN-specific
    structural checks.
    """
    extracted = extract_pan(candidate.text)

    score = candidate.score

    if extracted.pan_number:
        score += 10

        if validate_pan_number(extracted.pan_number):
            score += 20

    if is_plausible_person_name(extracted.name):
        score += 10

    if is_plausible_person_name(extracted.father_name):
        score += 5

    if extracted.dob:
        score += 5

    return min(score, 100.0)

def select_best_pan_candidate(
    candidates: list[OCRCandidate],
) -> OCRCandidate:
    """
    Select the PAN OCR candidate with the highest
    document-aware score.
    """

    if not candidates:
        raise ValueError("No PAN OCR candidates available")

    return max(
        candidates,
        key=evaluate_pan_candidate,
    )


