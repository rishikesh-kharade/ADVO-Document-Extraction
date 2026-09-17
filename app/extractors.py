import re

from .models import PanCardData, AadhaarData, BankPassbookData, CancelledChequeData

PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
)

def extract_pan(ocr_text: str) -> PanCardData:
    """
    Extract PAN-card fields from OCR text.
    """

    text = ocr_text.strip()

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    pan_match = re.search(
        r"\b[A-Z]{5}\d{4}[A-Z]\b",
        text,
        re.IGNORECASE,
    )

    pan_number = (
        pan_match.group(0).upper()
        if pan_match
        else None
    )

    def clean_name(value: str) -> str | None:
        words = re.findall(
            r"[A-Za-z]+",
            value,
        )

        return " ".join(words).upper() if words else None

    def value_after_label(
        index: int,
        label_match: re.Match[str],
    ) -> str | None:
        inline_value = lines[index][
            label_match.end():
        ].strip(" :/-")

        cleaned_inline_value = clean_name(
            inline_value,
        )

        if cleaned_inline_value:
            return cleaned_inline_value

        if index + 1 < len(lines):
            return clean_name(lines[index + 1])

        return None

    name = None
    father_name = None

    for index, line in enumerate(lines):
        if father_name is None:
            father_match = re.search(
                r"father['’]?s\s+name",
                line,
                re.IGNORECASE,
            )

            if father_match:
                father_name = value_after_label(
                    index,
                    father_match,
                )
                continue

        if name is None and "father" not in line.lower():
            name_match = re.search(
                r"\bname\b",
                line,
                re.IGNORECASE,
            )

            if name_match:
                name = value_after_label(
                    index,
                    name_match,
                )

    dob_match = re.search(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
        text,
    )

    dob = dob_match.group(0) if dob_match else None

    return PanCardData(
        pan_number=pan_number,
        name=name,
        father_name=father_name,
        dob=dob,
    )

AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")

def extract_aadhaar(ocr_text: str) -> AadhaarData:
    """
    Extract Aadhaar fields from labelled OCR text and card-style OCR text.
    """

    text = ocr_text.strip()

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    aadhaar_pattern = (
        r"\b(\d{4})[\s.-]*(\d{4})"
        r"[\s.-]*(\d{4})\b"
    )

    aadhaar_match = re.search(
        aadhaar_pattern,
        text,
    )

    aadhar_number = None

    if aadhaar_match:
        aadhar_number = "".join(
            aadhaar_match.groups()
        )

    def clean_person_name(value: str) -> str | None:
        words = re.findall(
            r"[A-Za-z]+",
            value,
        )

        if len(words) < 2:
            return None

        candidate = " ".join(words).upper()

        ignored_words = (
            "GOVERNMENT",
            "INDIA",
            "AADHAAR",
            "ADDRESS",
            "DATE",
            "BIRTH",
        )

        if any(
            word in candidate
            for word in ignored_words
        ):
            return None

        return candidate

    name = None
    gender = None
    address = None

    for line in lines:
        if name is None and re.match(
            r"^Name\s*:",
            line,
            re.IGNORECASE,
        ):
            name_value = re.sub(
                r"^Name\s*:\s*",
                "",
                line,
                flags=re.IGNORECASE,
            )

            name = clean_person_name(name_value)

        elif gender is None and re.match(
            r"^Gender\s*:",
            line,
            re.IGNORECASE,
        ):
            gender = re.sub(
                r"^Gender\s*:\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip().title()

        elif address is None and re.match(
            r"^Address\s*:",
            line,
            re.IGNORECASE,
        ):
            address = re.sub(
                r"^Address\s*:\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()

        elif gender is None and line.lower() in (
            "male",
            "female",
            "transgender",
        ):
            gender = line.title()

        elif name is None:
            name = clean_person_name(line)

    if address is None:
        for index, line in enumerate(lines):
            is_address_start = re.search(
                r"(?:[SDWC$]\s*/\s*O)\s*:",
                line,
                re.IGNORECASE,
            )

            if not is_address_start:
                continue

            address_lines = []

            for address_line in lines[index:]:
                if re.search(
                    aadhaar_pattern,
                    address_line,
                ):
                    break

                address_lines.append(address_line)

            if address_lines:
                address = ", ".join(address_lines)

            break

    dob_match = re.search(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
        text,
    )

    dob = dob_match.group(0) if dob_match else None

    return AadhaarData(
        aadhar_number=aadhar_number,
        name=name,
        dob=dob,
        gender=gender,
        address=address,
    )

ACCOUNT_LABEL_PATTERN = re.compile(
    r"(?:"
    r"Account\s+Number|"
    r"Account\s+No\.?|"
    r"A/C\s+Number|"
    r"A/C\s+No\.?|"
    r"AC\s+Number|"
    r"AC\s+No\.?"
    r")"
    r"\s*[:\-]?\s*"
    r"(\d{9,18})",
    re.IGNORECASE,
)

IFSC_PATTERN = re.compile(
    r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    re.IGNORECASE,
)

def extract_bank_passbook(
    ocr_text: str,
) -> BankPassbookData:
    """
    Extract bank-passbook fields from labelled and card-style OCR text.
    """

    lines = [
        line.strip()
        for line in ocr_text.splitlines()
        if line.strip()
    ]

    account_number = None
    ifsc = None
    bank_name = None
    branch = None
    account_holder_name = None

    def clean_person_name(value: str) -> str | None:
        words = re.findall(
            r"[A-Za-z]+",
            value,
        )

        ignored_words = {
            "MR",
            "MRS",
            "MS",
            "MISS",
        }

        words = [
            word
            for word in words
            if word.upper() not in ignored_words
        ]

        return " ".join(words).upper() if words else None

    for line in lines:
        lower_line = line.lower()

        account_label_match = re.search(
            r"\b(?:account|a/c|ac)\s*"
            r"(?:number|no\.?)\b",
            line,
            re.IGNORECASE,
        )

        if account_number is None and account_label_match:
            value_part = line[
                account_label_match.end():
            ]

            digits = "".join(
                re.findall(r"\d+", value_part)
            )

            if 9 <= len(digits) <= 18:
                account_number = digits

        if ifsc is None and "ifsc" in lower_line:
            normalized_line = re.sub(
                r"[^A-Za-z0-9$]",
                "",
                line,
            ).upper()

            normalized_line = normalized_line.replace(
                "$",
                "S",
            )

            ifsc_match = re.search(
                r"[A-Z]{4}0[A-Z0-9]{6}",
                normalized_line,
            )

            if ifsc_match:
                ifsc = ifsc_match.group(0)

        if bank_name is None:
            bank_name_match = re.match(
                r"^Bank\s+Name\s*:\s*(.+)$",
                line,
                re.IGNORECASE,
            )

            if bank_name_match:
                bank_name = bank_name_match.group(
                    1
                ).strip().upper()

            elif "state bank of india" in lower_line:
                bank_name = "STATE BANK OF INDIA"

        if branch is None:
            branch_label_match = re.match(
                r"^Branch\s*:\s*(.+)$",
                line,
                re.IGNORECASE,
            )

            if branch_label_match:
                branch = branch_label_match.group(
                    1
                ).strip().upper()

            else:
                branch_match = re.search(
                    r"\b([A-Za-z]+)\s+BRANCH\b",
                    line,
                    re.IGNORECASE,
                )

                if branch_match:
                    branch = (
                        f"{branch_match.group(1).upper()} "
                        "BRANCH"
                    )

        if account_holder_name is None:
            name_label_match = re.search(
                r"(?:account\s+holder(?:\s+name)?|"
                r"customer\s+name)\s*:",
                line,
                re.IGNORECASE,
            )

            if name_label_match:
                value_part = line[
                    name_label_match.end():
                ]

                account_holder_name = clean_person_name(
                    value_part
                )

    return BankPassbookData(
        account_number=account_number,
        ifsc=ifsc,
        bank_name=bank_name,
        branch=branch,
        account_holder_name=account_holder_name,
    )

def extract_cancelled_cheque(
    ocr_text: str,
) -> CancelledChequeData:
    """
    Extract cancelled-cheque fields from labelled and cheque-style OCR text.
    """

    lines = [
        line.strip()
        for line in ocr_text.splitlines()
        if line.strip()
    ]

    account_number = None
    ifsc = None
    bank_name = None
    account_holder_name = None

    def clean_person_name(value: str) -> str | None:
        words = re.findall(
            r"[A-Za-z]+",
            value,
        )

        return " ".join(words).upper() if words else None

    for line in lines:
        lower_line = line.lower()

        account_label_match = re.search(
            r"\b(?:account|a/c|ac)\s*"
            r"(?:number|no\.?)\b",
            line,
            re.IGNORECASE,
        )

        if account_number is None and account_label_match:
            value_part = line[
                account_label_match.end():
            ]

            digits = "".join(
                re.findall(r"\d+", value_part)
            )

            if 9 <= len(digits) <= 18:
                account_number = digits

        if ifsc is None and "ifsc" in lower_line:
            ifsc_match = re.search(
                r"[A-Z]{4}0[A-Z0-9]{6}",
                line,
                re.IGNORECASE,
            )

            if ifsc_match:
                ifsc = ifsc_match.group(0).upper()

        if bank_name is None:
            bank_name_match = re.match(
                r"^Bank\s+Name\s*:\s*(.+)$",
                line,
                re.IGNORECASE,
            )

            if bank_name_match:
                bank_name = bank_name_match.group(
                    1
                ).strip().upper()

            elif "state bank of india" in lower_line:
                bank_name = "STATE BANK OF INDIA"

        if account_holder_name is None:
            name_label_match = re.search(
                r"(?:account\s+holder(?:\s+name)?|"
                r"account\s+holder)\s*:",
                line,
                re.IGNORECASE,
            )

            if name_label_match:
                value_part = line[
                    name_label_match.end():
                ]

                account_holder_name = clean_person_name(
                    value_part
                )

            else:
                relation_match = re.match(
                    r"^([A-Z][A-Z\s]+?)\s+"
                    r"(?:S/O|D/O|W/O|C/O)\b",
                    line,
                    re.IGNORECASE,
                )

                if relation_match:
                    account_holder_name = clean_person_name(
                        relation_match.group(1)
                    )

    if account_number is None:
        for line in lines:
            digits_only = re.sub(r"\D", "", line)

            if (
                line.strip() == digits_only
                and 9 <= len(digits_only) <= 18
            ):
                account_number = digits_only
                break

    return CancelledChequeData(
        account_number=account_number,
        ifsc=ifsc,
        bank_name=bank_name,
        account_holder_name=account_holder_name,
    )