from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    PAN_CARD = "PAN_CARD"
    AADHAAR_CARD = "AADHAAR_CARD"
    BANK_PASSBOOK = "BANK_PASSBOOK"
    CANCELLED_CHEQUE = "CANCELLED_CHEQUE"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"


class PanCardData(BaseModel):
    pan_number: str | None = None
    name: str | None = None
    father_name: str | None = None
    dob: str | None = None
    date_of_issue: str | None = None

    additional_fields: dict[str, str] = Field(
        default_factory=dict
    )


class AadhaarData(BaseModel):
    aadhar_number: str | None = None
    name: str | None = None
    dob: str | None = None
    gender: str | None = None
    address: str | None = None
    mobile_number: str | None = None
    enrollment_number: str | None = None

    additional_fields: dict[str, str] = Field(
        default_factory=dict
    )


class BankPassbookData(BaseModel):
    account_number: str | None = None
    ifsc: str | None = None
    bank_name: str | None = None
    branch: str | None = None
    account_holder_name: str | None = None

    additional_fields: dict[str, str] = Field(
        default_factory=dict
    )

class CancelledChequeData(BaseModel):
    account_number: str | None = None
    ifsc: str | None = None
    bank_name: str | None = None
    branch: str | None = None
    account_holder_name: str | None = None

    additional_fields: dict[str, str] = Field(
        default_factory=dict
    )


class ClassificationResult(BaseModel):
    document_type: DocumentType
    supported: bool


class OCRResult(BaseModel):
    text: str


class ValidationResult(BaseModel):
    valid: bool
    fields: dict[str, Any] = Field(
        default_factory=dict
    )


class DocumentHandlerResult(BaseModel):
    extracted_data: dict[str, Any] | None = None
    validation: ValidationResult
    ocr_text: str


class DocumentProcessingResponse(BaseModel):
    success: bool
    document_type: DocumentType
    supported: bool
    extracted_data: dict[str, Any] | None = None
    validation: ValidationResult | None = None
    ocr_text: str | None = None
    message: str | None = None