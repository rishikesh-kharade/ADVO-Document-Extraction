from app.document_understanding.handlers.base import (
    DocumentHandler,
)
from app.document_understanding.handlers.pan import (
    PanDocumentHandler,
)
from app.document_understanding.handlers.aadhaar import (
    AadhaarDocumentHandler,
)
from app.document_understanding.handlers.passbook import (
    PassbookDocumentHandler,
)
from app.document_understanding.handlers.cheque import (
    ChequeDocumentHandler,
)
from app.document_understanding.models.documents import (
    DocumentType,
)
from app.document_understanding.ocr.base import (
    OCRProvider,
)


HANDLER_REGISTRY: dict[
    DocumentType,
    type[DocumentHandler],
] = {
    DocumentType.PAN_CARD: PanDocumentHandler,
    DocumentType.AADHAAR_CARD: AadhaarDocumentHandler,
    DocumentType.BANK_PASSBOOK: PassbookDocumentHandler,
    DocumentType.CHEQUE: ChequeDocumentHandler,
}


def get_handler(
    document_type: DocumentType,
    *,
    ocr: OCRProvider,
) -> DocumentHandler | None:

    handler_class = HANDLER_REGISTRY.get(
        document_type
    )

    if handler_class is None:
        return None

    return handler_class(
        ocr=ocr
    )