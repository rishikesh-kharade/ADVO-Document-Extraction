from fastapi import FastAPI

from app.api.documents import router


app = FastAPI(
    title="ADVO Document Verification API",
    version="1.0.0",
    description=(
        "Automated document classification, "
        "OCR, extraction and validation using "
        "Gemini 3.6 Flash."
    ),
)


app.include_router(
    router
)


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }