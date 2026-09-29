from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config.settings import (
    ALLOWED_MIME_TYPES,
    MAX_UPLOAD_SIZE_MB,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
    DocumentProcessingUnavailableError,
)


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)

processing_service = DocumentProcessingService()


@router.get("/test")
async def test_endpoint():
    return {
        "message": "Document processing API is running."
    }


@router.post("/process",responses={
        503: {
            "description": "Document processing service temporarily unavailable."
        },
    },
             )
async def process_document(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required.",
        )

    if (
        file.content_type
        and file.content_type not in ALLOWED_MIME_TYPES
    ):
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type.",
        )

    content = await file.read()

    max_size = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds the maximum size of "
                f"{MAX_UPLOAD_SIZE_MB} MB."
            ),
        )

    suffix = Path(file.filename).suffix or ".bin"

    temporary_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = temporary_file.name

        try:
            result = processing_service.process_document(
                temporary_path
            )

        except DocumentProcessingUnavailableError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc),
            ) from exc

        return result.model_dump(mode="json")

    finally:
        if temporary_path:
            Path(temporary_path).unlink(
                missing_ok=True
            )