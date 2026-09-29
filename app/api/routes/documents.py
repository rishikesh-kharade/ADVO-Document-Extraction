from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, UploadFile

from app.services.document_processing_service import (
    DocumentProcessingService,
)


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


processing_service = DocumentProcessingService()


@router.get("/test")
def test_documents_route():
    return {
        "message": "Document API is working",
    }


@router.post("/process")
async def process_document(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix

    with NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temporary_file:
        content = await file.read()
        temporary_file.write(content)
        temporary_file_path = temporary_file.name

    try:
        result = processing_service.process_document(
            temporary_file_path
        )

        return result.model_dump()

    finally:
        Path(temporary_file_path).unlink(
            missing_ok=True
        )