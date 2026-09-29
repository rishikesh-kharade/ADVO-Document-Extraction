from dataclasses import dataclass

from app.document_understanding.models.documents import DocumentType


@dataclass(frozen=True)
class DocumentDefinition:
    document_type: DocumentType
    name: str
    supported: bool


DOCUMENT_REGISTRY: dict[DocumentType, DocumentDefinition] = {
    DocumentType.PAN_CARD: DocumentDefinition(
        document_type=DocumentType.PAN_CARD,
        name="PAN Card",
        supported=True,
    ),
    DocumentType.AADHAAR_CARD: DocumentDefinition(
        document_type=DocumentType.AADHAAR_CARD,
        name="Aadhaar Card",
        supported=True,
    ),
    DocumentType.BANK_PASSBOOK: DocumentDefinition(
        document_type=DocumentType.BANK_PASSBOOK,
        name="Bank Passbook",
        supported=True,
    ),
    DocumentType.CANCELLED_CHEQUE: DocumentDefinition(
        document_type=DocumentType.CANCELLED_CHEQUE,
        name="Cancelled Cheque",
        supported=True,
    ),
}


def get_document_definition(
    document_type: DocumentType,
) -> DocumentDefinition | None:
    return DOCUMENT_REGISTRY.get(document_type)