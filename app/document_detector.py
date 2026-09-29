import re

from enum import Enum


class DocumentType(str, Enum):
    PAN = "PAN"
    AADHAAR = "AADHAAR"
    PASSBOOK = "PASSBOOK"
    CANCELLED_CHEQUE = "CANCELLED_CHEQUE"
    UNKNOWN = "UNKNOWN"

class DocumentDetector:
    def detect(self, text: str) -> DocumentType:
        if not text or not text.strip():
            return DocumentType.UNKNOWN

        text = self._normalize(text)

        scores = {
            DocumentType.PAN: self._score_pan(text),
            DocumentType.AADHAAR: self._score_aadhaar(text),
            DocumentType.PASSBOOK: self._score_passbook(text),
            DocumentType.CANCELLED_CHEQUE: self._score_cancelled_cheque(text),
        }

        document_type, score = max(scores.items(), key=lambda item: item[1])

        if score < 30:
            return DocumentType.UNKNOWN

        return document_type

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.upper()).strip()

    @staticmethod
    def _score_pan(text: str) -> int:
        score = 0

        if "PERMANENT ACCOUNT NUMBER" in text:
            score += 40

        if "INCOME TAX DEPARTMENT" in text:
            score += 20

        pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
        if re.search(pan_pattern, text):
            score += 40

        return score

    @staticmethod
    def _score_aadhaar(text: str) -> int:
        score = 0

        if "AADHAAR" in text:
            score += 40

        if "GOVERNMENT OF INDIA" in text:
            score += 20

        if "UNIQUE IDENTIFICATION" in text:
            score += 20

        aadhaar_pattern = r"\b\d{4}\s?\d{4}\s?\d{4}\b"
        if re.search(aadhaar_pattern, text):
            score += 30

        return score

    @staticmethod
    def _score_passbook(text: str) -> int:
        score = 0

        keywords = [
            "CUSTOMER NAME",
            "ACCOUNT NUMBER",
            "ACCOUNT NO",
            "BRANCH",
            "IFSC",
            "PASSBOOK",
        ]

        for keyword in keywords:
            if keyword in text:
                score += 15

        return score

    @staticmethod
    def _score_cancelled_cheque(text: str) -> int:
        score = 0

        keywords = [
            "CANCELLED",
            "CANCELLED CHEQUE",
            "A/C",
            "ACCOUNT NUMBER",
            "ACCOUNT NO",
            "IFSC",
        ]

        for keyword in keywords:
            if keyword in text:
                score += 15

        return score