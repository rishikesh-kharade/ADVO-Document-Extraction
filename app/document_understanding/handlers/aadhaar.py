from pathlib import Path

from app.document_understanding.extractors.aadhaar import (
    extract_aadhaar,
)
from app.document_understanding.handlers.base import (
    DocumentHandler,
)
from app.document_understanding.models.documents import (
    DocumentHandlerResult,
    ValidationResult,
)
from app.document_understanding.validators.aadhaar import (
    validate_aadhaar_format,
    validate_aadhaar_verhoeff,
)


class AadhaarDocumentHandler(
    DocumentHandler
):

    def process(
        self,
        file_path: str | Path,
    ) -> DocumentHandlerResult:

        ocr_result = self.ocr.extract_text(
            file_path
        )

        document = extract_aadhaar(
            ocr_result.text
        )

        format_valid = (
            validate_aadhaar_format(
                document.aadhar_number
            )
        )

        checksum_valid = (
            validate_aadhaar_verhoeff(
                document.aadhar_number
            )
        )

        overall_valid = (
            format_valid
            and checksum_valid
        )

        validation = ValidationResult(
            valid=overall_valid,
            fields={
                "aadhar_number": {
                    "format": format_valid,
                    "checksum": checksum_valid,
                    "valid": overall_valid,
                }
            },
        )

        return DocumentHandlerResult(
            extracted_data=document.model_dump(),
            validation=validation,
            ocr_text=ocr_result.text,
        )