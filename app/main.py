from fastapi import FastAPI

from app.api.routes.documents import router as documents_router


app = FastAPI(
    title="ADVO Document Verification API",
    description="Automated Document Verification and Onboarding System",
    version="1.0.0",
)


app.include_router(documents_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ADVO Document Verification API",
    }