from app.document_understanding.models.documents import DocumentType
from app.document_understanding.registry import (
    DOCUMENT_REGISTRY,
    get_document_definition,
)


def test_supported_documents_are_registered():
    expected_documents = {
        DocumentType.PAN_CARD,
        DocumentType.AADHAAR_CARD,
        DocumentType.BANK_PASSBOOK,
        DocumentType.CANCELLED_CHEQUE,
    }

    assert expected_documents.issubset(
        DOCUMENT_REGISTRY.keys()
    )


def test_supported_documents_are_marked_supported():
    supported_documents = {
        DocumentType.PAN_CARD,
        DocumentType.AADHAAR_CARD,
        DocumentType.BANK_PASSBOOK,
        DocumentType.CANCELLED_CHEQUE,
    }

    for document_type in supported_documents:
        definition = get_document_definition(
            document_type
        )

        assert definition is not None
        assert definition.document_type == document_type
        assert definition.supported is True


def test_get_document_definition():
    definition = get_document_definition(
        DocumentType.PAN_CARD
    )

    assert definition is not None
    assert definition.document_type == DocumentType.PAN_CARD
    assert definition.name == "PAN Card"
    assert definition.supported is True


def test_unsupported_document_is_not_registered():
    assert (
        get_document_definition(
            DocumentType.UNKNOWN
        )
        is None
    )

    assert (
        get_document_definition(
            DocumentType.UNSUPPORTED
        )
        is None
    )