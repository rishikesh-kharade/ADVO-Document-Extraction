from pathlib import Path

from app.document_understanding.extractors.passbook import (
    extract_passbook,
)
from app.document_understanding.handlers.base import (
    DocumentHandler,
)
from app.document_understanding.models.documents import (
    DocumentHandlerResult,
    ValidationResult,
)
from app.document_understanding.validators.passbook import (
    validate_account_number,
    validate_ifsc,
)


class PassbookDocumentHandler(
    DocumentHandler
):

    def process(
        self,
        file_path: str | Path,
    ) -> DocumentHandlerResult:

        ocr_result = self.ocr.extract_text(
            file_path
        )

        document = extract_passbook(
            ocr_result.text
        )

        account_valid = (
            validate_account_number(
                document.account_number
            )
        )

        ifsc_valid = validate_ifsc(
            document.ifsc
        )

        overall_valid = (
            account_valid
            and ifsc_valid
        )

        validation = ValidationResult(
            valid=overall_valid,
            fields={
                "account_number": account_valid,
                "ifsc": ifsc_valid,
            },
        )

        return DocumentHandlerResult(
            extracted_data=document.model_dump(),
            validation=validation,
            ocr_text=ocr_result.text,
        )