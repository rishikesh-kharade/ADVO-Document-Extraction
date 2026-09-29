from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentDefinition:
    name: str
    supported: bool


DOCUMENT_REGISTRY = {
    "PAN_CARD": DocumentDefinition(
        name="PAN_CARD",
        supported=True,
    ),
    "AADHAAR_CARD": DocumentDefinition(
        name="AADHAAR_CARD",
        supported=True,
    ),
    "BANK_PASSBOOK": DocumentDefinition(
        name="BANK_PASSBOOK",
        supported=True,
    ),
    "CANCELLED_CHEQUE": DocumentDefinition(
        name="CANCELLED_CHEQUE",
        supported=True,
    ),
}


def get_document_definition(document_type: str) -> DocumentDefinition | None:
    return DOCUMENT_REGISTRY.get(document_type)