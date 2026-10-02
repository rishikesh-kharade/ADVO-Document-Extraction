import re

from app.document_understanding.models.documents import AadhaarData


AADHAAR_PATTERN = re.compile(
    r"(?<!\d)(?:\d[\s-]?){12}(?!\d)"
)

DATE_PATTERN = re.compile(
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b"
)

MOBILE_PATTERN = re.compile(
    r"(?<!\d)[6-9]\d{9}(?!\d)"
)

ENROLLMENT_PATTERN = re.compile(
    r"\b\d{4,8}/\d{4,8}/\d{4,8}\b"
)


def _clean(value: str | None) -> str | None:
    if value is None:
        return None

    value = re.sub(r"\s+", " ", value).strip()

    return value or None


def _clean_aadhaar(value: str) -> str:
    return re.sub(r"\D", "", value)


def _extract_labeled_value(
    lines: list[str],
    patterns: list[str],
) -> str | None:
    for index, line in enumerate(lines):
        for pattern in patterns:
            match = re.search(
                pattern,
                line,
                re.IGNORECASE,
            )

            if not match:
                continue

            remainder = line[match.end():].strip(" :-")

            if remainder:
                return _clean(remainder)

            if index + 1 < len(lines):
                return _clean(lines[index + 1])

    return None


def _extract_name(lines: list[str]) -> str | None:
    """Extract the person's name using Aadhaar-specific label/layout context."""

    name_labels = (
        "name",
        "नाम",
    )

    excluded_patterns = (
        "date of birth",
        "dob",
        "gender",
        "address",
        "mobile",
        "aadhaar",
        "aadhar",
        "government",
        "unique identification",
        "enrolment",
        "enrollment",
        "help",
        "www.",
        "my aadhaar",
        "माझे आधार",
    )

    # 1. Prefer an explicitly labelled name.
    for index, line in enumerate(lines):
        normalized = line.strip().lower()

        if not any(label in normalized for label in name_labels):
            continue

        match = re.search(
            r"(?:name|नाम)\s*(?:/|:|-)?\s*(?:name|नाम)?"
            r"\s*[:\-]?\s*(.+)$",
            line,
            re.IGNORECASE,
        )

        if match:
            candidate = _clean(match.group(1))

            if candidate and candidate.lower() not in {"name", "नाम"}:
                if not any(
                    pattern in candidate.lower()
                    for pattern in excluded_patterns
                ):
                    return candidate

        # Name may be on the next line.
        if index + 1 < len(lines):
            candidate = _clean(lines[index + 1])

            if not candidate:
                continue

            if any(
                pattern in candidate.lower()
                for pattern in excluded_patterns
            ):
                continue

            if re.search(
                r"(?:date of birth|dob|gender|address|aadhaar|aadhar|"
                r"mobile|enrolment|enrollment|name|नाम)",
                candidate,
                re.IGNORECASE,
            ):
                continue

            if re.search(r"[A-Za-z]", candidate):
                return candidate

    # 2. Aadhaar commonly places the English name immediately before DOB.
    # Example:
    # Vilas Rakhe
    # जन्म तारीख/DOB: 30/05/1995
    dob_index = None

    for index, line in enumerate(lines):
        if re.search(
            r"(date\s+of\s+birth|\bdob\b|जन्म)",
            line,
            re.IGNORECASE,
        ):
            dob_index = index
            break

    if dob_index is not None:
        for index in range(dob_index - 1, max(-1, dob_index - 4), -1):
            candidate = _clean(lines[index])

            if not candidate:
                continue

            if any(
                pattern in candidate.lower()
                for pattern in excluded_patterns
            ):
                continue

            # Prefer the English/Latin representation when both
            # regional-language and English names are present.
            if re.search(r"[A-Za-z]", candidate):
                if not re.search(
                    r"(government|unique identification|aadhaar|aadhar)",
                    candidate,
                    re.IGNORECASE,
                ):
                    return candidate

    return None


def _extract_address(
    lines: list[str],
) -> str | None:

    start_index = None
    address_prefix = None

    for index, line in enumerate(lines):

        lower = line.lower().strip()

        if lower.startswith("address"):
            start_index = index
            address_prefix = re.sub(
                r"^\s*address\s*[:\-]?\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            break

        if (
            lower.startswith("s/o:")
            or lower.startswith("c/o:")
            or lower.startswith("d/o:")
        ):
            start_index = index
            break

    if start_index is None:
        return None

    address_lines: list[str] = []


    if address_prefix:
        address_lines.append(address_prefix)

    stop_patterns = (
        "mobile",
        "mob",
        "aadhaar no",
        "aadhaar number",
        "aadhar no",
        "aadhar number",
        "your aadhaar",
        "signature",
        "uidai",
        "www.",
        "enrolment",
        "enrollment",
        "gender",
        "date of birth",
        "dob",
        "details as on",
        "vid",
        "1947",
        "help@",
    )

    for line in lines[start_index + 1:]:

        lower = line.lower().strip()

        if any(
            lower.startswith(pattern)
            for pattern in stop_patterns
        ):
            break

        if not line.strip():
            continue

        address_lines.append(line.strip())

    if not address_lines:
        return None

    meaningful = [
        line
        for line in address_lines
        if len(line) > 1
    ]

    return (
        ", ".join(meaningful)
        if meaningful
        else None
    )


def _extract_additional_fields(
    lines: list[str],
    known_values: set[str | None],
) -> dict[str, str]:
    """
    Preserve only useful Aadhaar-specific additional information.
    Currently VID is the supported additional field.
    """

    additional_fields: dict[str, str] = {}

    for line in lines:
        cleaned = line.strip()

        if not cleaned:
            continue

        match = re.match(
            r"^\s*VID\s*[:\-]\s*(.+?)\s*$",
            cleaned,
            re.IGNORECASE,
        )

        if not match:
            continue

        value = _clean(match.group(1))

        if value:
            additional_fields["VID"] = value

    return additional_fields


def extract_aadhaar(
    ocr_text: str,
) -> AadhaarData:
    lines = [
        line.strip()
        for line in ocr_text.splitlines()
        if line.strip()
    ]


    aadhar_number = None

    for match in AADHAAR_PATTERN.finditer(ocr_text):
        candidate = _clean_aadhaar(
            match.group(0)
        )

        if len(candidate) == 12:
            aadhar_number = candidate
            break

    name = _extract_name(lines)

    dob = _extract_labeled_value(
        lines,
        [
            r"date\s+of\s+birth",
            r"\bdob\b",
            r"जन्म",
        ],
    )

    if dob:
        date_match = DATE_PATTERN.search(dob)

        dob = (
            date_match.group(0)
            if date_match
            else dob
        )

    if dob is None:
        for line in lines:
            if (
                "dob" in line.lower()
                or "date of birth" in line.lower()
            ):
                date_match = DATE_PATTERN.search(line)

                if date_match:
                    dob = date_match.group(0)
                    break



    gender = None

    gender_match = re.search(
        r"\b(MALE|FEMALE|OTHER)\b",
        ocr_text,
        re.IGNORECASE,
    )

    if gender_match:
        gender = gender_match.group(1).title()



    mobile_number = None

    mobile_match = re.search(
        r"(?:mobile|mob)\s*[:\-]?\s*"
        r"([6-9]\d{9})",
        ocr_text,
        re.IGNORECASE,
    )

    if mobile_match:
        mobile_number = mobile_match.group(1)
    else:
        for index, line in enumerate(lines):
            if "mobile" not in line.lower():
                continue

            number_match = MOBILE_PATTERN.search(line)

            if number_match:
                mobile_number = number_match.group(0)
                break

            if index + 1 < len(lines):
                number_match = MOBILE_PATTERN.search(
                    lines[index + 1]
                )

                if number_match:
                    mobile_number = number_match.group(0)
                    break



    enrollment_number = None

    enrollment_match = ENROLLMENT_PATTERN.search(
        ocr_text
    )

    if enrollment_match:
        enrollment_number = enrollment_match.group(0)



    address = _extract_address(
        lines,
    )



    known_values = {
        aadhar_number,
        name,
        dob,
        gender,
        address,
        mobile_number,
        enrollment_number,
    }

    additional_fields = _extract_additional_fields(
        lines,
        known_values,
    )


    return AadhaarData(
        aadhar_number=aadhar_number,
        name=name,
        dob=dob,
        gender=gender,
        address=address,
        mobile_number=mobile_number,
        enrollment_number=enrollment_number,
        additional_fields=additional_fields,
    )