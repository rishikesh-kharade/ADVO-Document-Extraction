from pathlib import Path

from app.document_understanding.extractors.cancelled_cheque import (
    extract_cancelled_cheque,
)
from app.document_understanding.handlers.base import (
    DocumentHandler,
)
from app.document_understanding.models.documents import (
    DocumentHandlerResult,
    ValidationResult,
)
from app.document_understanding.validators.cancelled_cheque import (
    validate_cancelled_cheque_fields,
)


class CancelledChequeDocumentHandler(
    DocumentHandler
):

    def process(
        self,
        file_path: str | Path,
    ) -> DocumentHandlerResult:

        ocr_result = self.ocr.extract_text(
            file_path
        )

        document = extract_cancelled_cheque(
            ocr_result.text
        )

        validation_fields = (
            validate_cancelled_cheque_fields(
                document
            )
        )

        overall_valid = all(
            validation_fields.values()
        )

        validation = ValidationResult(
            valid=overall_valid,
            fields=validation_fields,
        )

        return DocumentHandlerResult(
            extracted_data=document.model_dump(),
            validation=validation,
            ocr_text=ocr_result.text,
        )