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


def _extract_account_number(lines: list[str]) -> str | None:
    """
    Prefer explicitly labelled account numbers so CIF,
    MICR and other numeric values are not accidentally selected.
    """

    for line in lines:
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
        r"^mop\.?",
        r"^nom\.?",
    )

    for line in lines[address_index + 1:]:
        if any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in stop_patterns
        ):
            break

        address_lines.append(line)

    if not address_lines:
        return None

    return " ".join(address_lines).strip()


def _find_branch_start(
    lines: list[str],
) -> int | None:
    """
    Find the beginning of the branch section.

    The OCR may place the branch section either before or after
    Customer Name, so we use the structural boundary created by
    S/D/W/H/o and Address instead of assuming a fixed order.
    """

    address_index = None
    relation_index = None

    for index, line in enumerate(lines):
        if re.match(
            r"^\s*address\s*:",
            line,
            re.IGNORECASE,
        ):
            address_index = index
            break

    for index, line in enumerate(lines):
        if re.match(
            r"^\s*s/d/w/h/o\s*:",
            line,
            re.IGNORECASE,
        ):
            relation_index = index
            break

    # The branch section is immediately before the
    # S/D/W/H/o / Address section.
    boundary_candidates = [
        index
        for index in (
            relation_index,
            address_index,
        )
        if index is not None
    ]

    if not boundary_candidates:
        return None

    boundary = min(boundary_candidates)

    # Walk backwards until we find the first meaningful
    # branch line after the account/customer header area.
    start = boundary - 1

    branch_lines: list[str] = []

    while start >= 0:
        line = lines[start].strip()

        if not line:
            start -= 1
            continue

        # Stop at known header/metadata sections.
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
            r"^(?:a/c|account\s+number)",
            line,
            re.IGNORECASE,
        ):
            break

        # Ignore relationship line if encountered.
        if re.match(
            r"^s/d/w/h/o\s*:",
            line,
            re.IGNORECASE,
        ):
            start -= 1
            continue

        branch_lines.insert(0, line)
        start -= 1

    if not branch_lines:
        return None

    return start + 1


def _extract_branch(
    lines: list[str],
) -> str | None:
    """
    Extract branch name/address and branch code.

    Example:

        MANCHERIAL
        HNO 18-649, MUKHARAMI
        IB CHOWRAS
        Phone:252598
        Email:sbi.6267@sbi.co.in
        Branch Code:6267

    becomes:

        MANCHERIAL, HNO 18-649, MUKHARAMI,
        IB CHOWRAS, Branch Code: 6267
    """

    branch_code_index = None
    branch_code = None

    # Find Branch Code.
    for index, line in enumerate(lines):
        match = re.search(
            r"\bbranch\s+code\s*[:\-]?\s*([A-Z0-9]+)",
            line,
            re.IGNORECASE,
        )

        if match:
            branch_code_index = index
            branch_code = match.group(1).strip()
            break

    if branch_code_index is None or branch_code is None:
        return None

    # Find the nearest structural boundary before the branch section.
    #
    # In this passbook the structure is:
    #
    # MOP
    # Nom. Reg. No.
    #
    # MANCHERIAL
    # HNO ...
    # IB CHOWRAS
    #
    # Phone
    # Email
    # Branch Code
    #
    boundary_index = None

    boundary_patterns = (
        r"^nom\.?\s*reg\.?\s*no\.?",
        r"^mop\.?",
        r"^d\.?o\.?b",
        r"^address\s*:",
        r"^s/d/w/h/o\s*:",
        r"^customer\s+name\s*:",
        r"^account\s+no\b",
        r"^cif\s+no\b",
        r"^savings\s+bank\s+account$",
    )

    for index in range(branch_code_index - 1, -1, -1):
        line = lines[index].strip()

        if any(
            re.search(pattern, line, re.IGNORECASE)
            for pattern in boundary_patterns
        ):
            boundary_index = index
            break

    # If we found a structural boundary, start after it.
    if boundary_index is not None:
        candidate_lines = lines[boundary_index + 1:branch_code_index]
    else:
        candidate_lines = lines[:branch_code_index]

    branch_lines: list[str] = []

    for line in candidate_lines:
        line = line.strip()

        if not line:
            continue

        # These belong to metadata around the branch section,
        # not the branch itself.
        if re.match(
            r"^(?:phone|email)\s*:",
            line,
            re.IGNORECASE,
        ):
            continue

        if re.match(
            r"^date\s+of\s+issue",
            line,
            re.IGNORECASE,
        ):
            continue

        if re.match(
            r"^branch\s+manager",
            line,
            re.IGNORECASE,
        ):
            continue

        if IFSC_PATTERN.search(line):
            continue

        if re.search(
            r"^micr\s*:",
            line,
            re.IGNORECASE,
        ):
            continue

        branch_lines.append(line)

    if branch_code:
        branch_lines.append(f"Branch Code: {branch_code}")

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