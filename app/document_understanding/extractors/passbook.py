import re

from app.document_understanding.models.documents import (
    BankPassbookData,
)

ACCOUNT_PATTERN = re.compile(
    r"(?<!\d)\d{9,18}(?!\d)"
)

IFSC_PATTERN = re.compile(
    r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    re.IGNORECASE,
)

CIF_PATTERN = re.compile(
    r"\b(?:CIF\s*(?:No|Number)?|Customer\s*ID)"
    r"\s*[:\-]?\s*(\d{8,20})\b",
    re.IGNORECASE,
)

MICR_PATTERN = re.compile(
    r"\bMICR\s*[:\-]?\s*(\d{9})\b",
    re.IGNORECASE,
)

KNOWN_BANKS = [
    "State Bank of India",
    "SBI",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Bank of Baroda",
    "Punjab National Bank",
    "Canara Bank",
    "Union Bank of India",
    "Bank of India",
    "Indian Bank",
    "Central Bank of India",
    "Indian Overseas Bank",
    "UCO Bank",
    "Bank of Maharashtra",
    "Kotak Mahindra Bank",
    "IDBI Bank",
    "Federal Bank",
    "IndusInd Bank",
    "Yes Bank",
    "South Indian Bank",
    "Karnataka Bank",
]


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

            value = match.group(1).strip()

            if value:
                return value

            if index + 1 < len(lines):
                next_value = lines[index + 1].strip()

                if next_value:
                    return next_value

    return None


def _extract_bank_name(lines: list[str]) -> str | None:
    """
    Extract the bank name even when OCR places other-language
    text on the same line.

    Example:
        भारतीय स्टेट बैंक State Bank of India

    -> State Bank of India
    """

    bank_name = _extract_label_value(
        lines,
        ["Bank Name"],
    )

    if bank_name:
        return bank_name

    for line in lines:
        normalized = re.sub(r"\s+", " ", line).strip()

        for bank in KNOWN_BANKS:
            if bank.casefold() in normalized.casefold():
                return bank

    return None


def _extract_account_number(
    lines: list[str],
) -> str | None:
    """
    Extract the account number.

    Supports both:
        Account No: 123456789012

    and:
        Account No
        123456789012
    """

    for index, line in enumerate(lines):
        match = re.match(
            r"^\s*(?:account\s+number|"
            r"account\s+no\.?|"
            r"a/c\s+number|"
            r"a/c\s+no\.?)"
            r"\s*[:\-]?\s*(\d{9,18})\b",
            line,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

        label_match = re.match(
            r"^\s*(?:account\s+number|"
            r"account\s+no\.?|"
            r"a/c\s+number|"
            r"a/c\s+no\.?)"
            r"\s*$",
            line,
            re.IGNORECASE,
        )

        if label_match and index + 1 < len(lines):
            next_line = lines[index + 1].strip()

            if re.fullmatch(
                r"\d{9,18}",
                next_line,
            ):
                return next_line

    return None


def _extract_ifsc(lines: list[str]) -> str | None:
    for line in lines:
        match = IFSC_PATTERN.search(line)

        if match:
            return match.group(0).upper()

    return None


def _extract_account_holder_name(
        lines: list[str],
) -> str | None:
    return _extract_label_value(
        lines,
        [
            "Account Holder Name",
            "Account Holder",
            "Customer Name",
        ],
    )


def _extract_cif_number(
        lines: list[str],
) -> str | None:
    for line in lines:
        match = CIF_PATTERN.search(line)

        if match:
            return match.group(1)

    return None


def _extract_micr(
        lines: list[str],
) -> str | None:
    for line in lines:
        match = MICR_PATTERN.search(line)

        if match:
            return match.group(1)

    return None


def _extract_customer_address(
    lines: list[str],
) -> str | None:
    """
    Extract the customer address from the explicit Address section.

    The customer address ends before the passbook's
    subsequent metadata/branch section.
    """

    address_index = None

    for index, line in enumerate(lines):
        if re.match(
            r"^\s*address\s*:",
            line,
            re.IGNORECASE,
        ):
            address_index = index
            break

    if address_index is None:
        return None

    first_line = re.sub(
        r"^\s*address\s*:\s*",
        "",
        lines[address_index],
        flags=re.IGNORECASE,
    ).strip()

    address_lines: list[str] = []

    if first_line:
        address_lines.append(first_line)

    stop_patterns = (
        r"^phone\s*:",
        r"^email\s*:",
        r"^d\.?o\.?b",
        r"^mop\.?\s*:",
        r"^nom\.?\s*\.?\s*reg\.?\s*no\.?\s*:",
    )

    for line in lines[address_index + 1:]:
        if any(
            re.search(
                pattern,
                line,
                re.IGNORECASE,
            )
            for pattern in stop_patterns
        ):
            break

        address_lines.append(line)

    if not address_lines:
        return None

    return " ".join(
        line.strip(" ,")
        for line in address_lines
        if line.strip()
    )


def _find_branch_start(
    lines: list[str],
) -> int | None:
    """
    Find the beginning of the branch section.

    The branch section is usually located between the
    Customer Name section and the S/D/W/H/o or Address section.
    """
    boundary_candidates: list[int] = []

    for index, line in enumerate(lines):
        if re.match(
            r"^\s*(?:s/d/w/h/o|address)\s*:",
            line,
            re.IGNORECASE,
        ):
            boundary_candidates.append(index)

    if not boundary_candidates:
        return None

    boundary = min(boundary_candidates)

    # Walk backwards from the boundary and collect meaningful
    # branch lines until we reach the account/customer header.
    start = boundary - 1

    while start >= 0:
        line = lines[start].strip()

        if not line:
            start -= 1
            continue

        # Stop at the customer/account header.
        if re.search(
            r"^(?:customer\s+name|"
            r"account\s+no|"
            r"cif\s+no|"
            r"savings\s+bank\s+account)$",
            line,
            re.IGNORECASE,
        ):
            break

        if re.search(
            r"^(?:a/c|account\s+number)\b",
            line,
            re.IGNORECASE,
        ):
            break

        start -= 1

    return start + 1


def _extract_branch(
    lines: list[str],
) -> str | None:

    # Simple labelled format:
    # Branch: Bengaluru Main Branch
    # or:
    # Branch
    # Bengaluru Main Branch
    simple_branch = _extract_label_value(
        lines,
        ["Branch Name", "Branch"],
    )

    if simple_branch:
        return simple_branch
    """
    Extract branch name/address and branch code.

    The branch section begins after the passbook metadata
    section, typically after "Nom. Reg. No.", and ends
    before branch contact/IFSC information.
    """

    branch_code = None
    branch_code_index = None

    # Find Branch Code.
    for index, line in enumerate(lines):
        match = re.search(
            r"\bbranch\s+code\s*[:\-]?\s*([A-Z0-9]+)",
            line,
            re.IGNORECASE,
        )

        if match:
            branch_code = match.group(1).strip()
            branch_code_index = index
            break

    if branch_code_index is None:
        return None

    # Find the branch-section boundary.
    #
    # Expected structure:
    #
    #   MOP.:SINGLE
    #   Nom. Reg. No.:
    #
    #   MANCHERIAL
    #   HNO 18-649,MUKHARANI
    #   IB CHOWRAS
    #
    #   Phone:...
    #   Email:...
    #   Branch Code:6267
    #
    branch_start = None

    for index in range(branch_code_index - 1, -1, -1):
        line = lines[index].strip()

        if re.match(
            r"^nom\.?\s*\.?\s*reg\.?\s*no\.?\s*:",
            line,
            re.IGNORECASE,
        ):
            branch_start = index + 1
            break

    # Fallback if Nom. Reg. No. is missing.
    if branch_start is None:
        for index in range(branch_code_index - 1, -1, -1):
            line = lines[index].strip()

            if re.match(
                r"^mop\.?\s*:",
                line,
                re.IGNORECASE,
            ):
                branch_start = index + 1
                break

    if branch_start is None:
        return f"Branch Code: {branch_code}"

    branch_lines: list[str] = []

    for line in lines[branch_start:branch_code_index]:
        line = line.strip()

        if not line:
            continue

        # Branch contact information is not part of branch name/address.
        if re.match(
            r"^(?:phone|email)\s*:",
            line,
            re.IGNORECASE,
        ):
            continue

        # Ignore issue/date information.
        if re.match(
            r"^date\s+of\s+issue",
            line,
            re.IGNORECASE,
        ):
            continue

        # Ignore standalone date/reference lines.
        if re.fullmatch(
            r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}(?:\s+\d+)?",
            line,
        ):
            continue

        # Ignore branch manager information.
        if re.match(
            r"^branch\s+manager\b",
            line,
            re.IGNORECASE,
        ):
            continue

        # Ignore IFSC.
        if IFSC_PATTERN.search(line):
            continue

        branch_lines.append(line)

    if branch_code:
        branch_lines.append(
            f"Branch Code: {branch_code}"
        )

    if not branch_lines:
        return None

    return ", ".join(
        line.strip(" ,")
        for line in branch_lines
        if line.strip()
    )


def _normalize_passbook_lines(
    ocr_text: str,
) -> list[str]:
    """
    Normalize OCR output that may contain Markdown tables.

    Example:

        | Account No : | 38170554361 | HNO 18-649, MUKHARANI |

    becomes:

        Account No : 38170554361
        HNO 18-649, MUKHARANI
    """

    normalized_lines: list[str] = []

    for raw_line in ocr_text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Markdown table separator:
        # |---|---|---|
        if re.fullmatch(
            r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?",
            line,
        ):
            continue

        if "|" not in line:
            normalized_lines.append(line)
            continue

        cells = [
            cell.strip()
            for cell in line.strip("|").split("|")
        ]

        cells = [
            cell
            for cell in cells
            if cell
        ]

        if not cells:
            continue

        # Handle labelled table rows.
        first_cell = cells[0]

        if re.match(
            r"^(?:CIF\s+No|Account\s+No)\s*:",
            first_cell,
            re.IGNORECASE,
        ):
            if len(cells) >= 2:
                normalized_lines.append(
                    f"{first_cell} {cells[1]}"
                )

            # Preserve the third cell because it may actually
            # belong to the branch section.
            if len(cells) >= 3:
                normalized_lines.append(cells[2])

            continue

        # Generic table row.
        normalized_lines.extend(cells)

    return normalized_lines


def extract_passbook(
    ocr_text: str,
) -> BankPassbookData:

    lines = _normalize_passbook_lines(ocr_text)

    account_number = _extract_account_number(lines)

    ifsc = _extract_ifsc(lines)

    bank_name = _extract_bank_name(lines)

    account_holder_name = _extract_account_holder_name(
        lines
    )

    branch = _extract_branch(lines)

    cif_number = _extract_cif_number(lines)

    micr = _extract_micr(lines)

    customer_address = _extract_customer_address(lines)

    additional_fields: dict[str, str] = {}

    if cif_number:
        additional_fields["cif_number"] = cif_number

    if customer_address:
        additional_fields["customer_address"] = (
            customer_address
        )

    if micr:
        additional_fields["micr"] = micr

    return BankPassbookData(
        account_number=account_number,
        ifsc=ifsc,
        bank_name=bank_name,
        branch=branch,
        account_holder_name=account_holder_name,
        additional_fields=additional_fields,
    )