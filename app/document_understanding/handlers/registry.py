from app.document_understanding.handlers.base import (
    DocumentHandler,
)

from app.document_understanding.handlers.pan import (
    PanDocumentHandler,
)


HANDLER_REGISTRY: dict[str, type[DocumentHandler]] = {
    "PAN_CARD": PanDocumentHandler,
}


def get_handler(
    document_type: str,
    *,
    ocr,
) -> DocumentHandler | None:

    handler_class = HANDLER_REGISTRY.get(
        document_type,
    )

    if handler_class is None:
        return None

    return handler_class(
        ocr=ocr,
    )