from app.document_understanding.models.documents import (
    CancelledChequeData,
)
from app.document_understanding.validators.passbook import (
    validate_account_number,
    validate_ifsc,
)


def validate_cancelled_cheque_fields(
    document: CancelledChequeData,
) -> dict[str, bool]:

    return {
        "account_number": (
            validate_account_number(
                document.account_number
            )
        ),
        "ifsc": validate_ifsc(
            document.ifsc
        ),
        "bank_name": bool(
            document.bank_name
        ),
        "account_holder_name": bool(
            document.account_holder_name
        ),
    }