import re

from app.document_understanding.models.documents import (
    CancelledChequeData,
)


ACCOUNT_PATTERN = re.compile(
    r"(?<!\d)\d{9,18}(?!\d)"
)

IFSC_PATTERN = re.compile(
    r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    re.IGNORECASE,
)


def _extract_label_value(
    lines: list[str],
    labels: list[str],
) -> str | None:

    for index, line in enumerate(lines):
        for label in labels:

            match = re.match(
                rf"^\s*{re.escape(label)}"
                rf"\s*(?::|-)?\s*(.*)$",
                line,
                re.IGNORECASE,
            )

            if not match:
                continue

            # Value is on the same line.
            inline_value = match.group(1).strip()

            if inline_value:
                return inline_value

            # Otherwise, value is on the next non-empty line.
            if index + 1 < len(lines):
                next_value = lines[index + 1].strip()

                if next_value:
                    return next_value

    return None


def extract_cancelled_cheque(
    ocr_text: str,
) -> CancelledChequeData:

    lines = [
        line.strip()
        for line in ocr_text.splitlines()
        if line.strip()
    ]


    account_number = None

    for line in lines:

        match = re.match(
            r"^\s*(?:account\s+number|"
            r"account\s+no\.?|a/c\s+number|a/c\s+no\.?)"
            r"\s*[:\-]\s*(\d{9,18})",
            line,
            re.IGNORECASE,
        )

        if match:
            account_number = match.group(1)
            break

    if account_number is None:

        for line in lines:

            match = ACCOUNT_PATTERN.search(line)

            if match:
                account_number = match.group(0)
                break



    ifsc = None

    for line in lines:

        match = IFSC_PATTERN.search(line)

        if match:
            ifsc = match.group(0).upper()
            break


    bank_name = _extract_label_value(
        lines,
        ["Bank Name"],
    )



    branch = _extract_label_value(
        lines,
        ["Branch Name", "Branch"],
    )



    account_holder_name = _extract_label_value(
        lines,
        [
            "Account Holder Name",
            "Account Holder",
            "Customer Name",
        ],
    )

    return CancelledChequeData(
        account_number=account_number,
        ifsc=ifsc,
        bank_name=bank_name,
        branch=branch,
        account_holder_name=account_holder_name,
    )