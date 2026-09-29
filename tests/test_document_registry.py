from app.document_understanding.classification.document_registry import (
    DOCUMENT_REGISTRY,
get_document_definition
)


def test_supported_documents_are_registered():
    assert "PAN_CARD" in DOCUMENT_REGISTRY
    assert "AADHAAR_CARD" in DOCUMENT_REGISTRY
    assert "BANK_PASSBOOK" in DOCUMENT_REGISTRY
    assert "CANCELLED_CHEQUE" in DOCUMENT_REGISTRY


def test_supported_documents_are_marked_supported():
    assert DOCUMENT_REGISTRY["PAN_CARD"].supported is True
    assert DOCUMENT_REGISTRY["AADHAAR_CARD"].supported is True
    assert DOCUMENT_REGISTRY["BANK_PASSBOOK"].supported is True
    assert DOCUMENT_REGISTRY["CANCELLED_CHEQUE"].supported is True


def test_get_document_definition():
    document = get_document_definition("PAN_CARD")

    assert document is not None
    assert document.name == "PAN_CARD"
    assert document.supported is True