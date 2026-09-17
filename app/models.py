from typing import Optional

from pydantic import BaseModel

class PanCardData(BaseModel):
    pan_number: Optional[str] = None
    name: Optional[str] = None
    father_name: Optional[str] = None
    dob: Optional[str] = None

class AadhaarData(BaseModel):
    aadhar_number: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None

class BankPassbookData(BaseModel):
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    bank_name: Optional[str] = None
    branch: Optional[str] = None
    account_holder_name: Optional[str] = None

class CancelledChequeData(BaseModel):
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    bank_name: Optional[str] = None
    account_holder_name: Optional[str] = None