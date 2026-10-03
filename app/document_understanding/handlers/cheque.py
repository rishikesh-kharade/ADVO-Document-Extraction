from pathlib import Path

from app.document_understanding.extractors.cheque import (
    extract_cheque,
)
from app.document_understanding.handlers.base import (
    DocumentHandler,
)
from app.document_understanding.models.documents import (
    DocumentHandlerResult,
    ValidationResult,
)
from app.document_understanding.validators.cheque import (
    validate_cheque_fields,
)


class ChequeDocumentHandler(
    DocumentHandler
):

    def process(
        self,
        file_path: str | Path,
    ) -> DocumentHandlerResult:

        ocr_result = self.ocr.extract_text(
            file_path
        )

        document = extract_cheque(
            ocr_result.text
        )

        validation_fields = (
            validate_cheque_fields(
                document
            )
        )

        overall_valid = (
                validation_fields["account_number"]
                and validation_fields["ifsc"]
                and validation_fields["bank_name"]
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