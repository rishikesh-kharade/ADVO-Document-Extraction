DOCUMENT_CLASSIFICATION_PROMPT = """
Identify the document type in this image.

Return the actual document type you see in the image.

Examples of document types include:
- PAN_CARD
- AADHAAR_CARD
- BANK_PASSBOOK
- CANCELLED_CHEQUE
- PASSPORT
- DRIVING_LICENSE
- VOTER_ID
- Any other clearly identifiable document type

If the document cannot be identified with reasonable confidence, return:
UNKNOWN

Return only the document type using the provided JSON schema.

Do not identify any individual fields or personal information.
"""