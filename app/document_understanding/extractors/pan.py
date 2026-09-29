import re

from app.document_understanding.models.documents import PanCardData


PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b"
)


def _clean_name(value: str | None) -> str | None:
    if not value:
        return None

    value = re.sub(r"\s+", " ", value).strip()

    return value.upper() if value else None


def _extract_value_after_label(
    lines: list[str],
    index: int,
    label_pattern: str,
) -> str | None:

    line = lines[index]

    match = re.search(
        label_pattern,
        line,
        re.IGNORECASE,
    )

    if not match:
        return None

    # First try value on the same line.
    inline_value = line[match.end():].strip(" :-")

    if inline_value:
        return inline_value

    # Otherwise try the next non-empty line.
    if index + 1 < len(lines):
        return lines[index + 1].strip()

    return None


def extract_pan(
    ocr_text: str,
) -> PanCardData:

    lines = [
        line.strip()
        for line in ocr_text.splitlines()
        if line.strip()
    ]



    pan_match = PAN_PATTERN.search(ocr_text)

    pan_number = (
        pan_match.group(0).upper()
        if pan_match
        else None
    )

    name = None
    father_name = None
    dob = None
    date_of_issue = None


    for index, line in enumerate(lines):

        # Name
        if name is None and re.search(
                r"\bname\b",
                line,
                re.IGNORECASE,
        ) and not re.search(
            r"father(?:['’]s)?\s+name",
            line,
            re.IGNORECASE,
        ):
            value = _extract_value_after_label(
                lines,
                index,
                r"\bname\b",
            )

            name = _clean_name(value)


        if father_name is None and re.search(
                r"father(?:['’]s)?\s+name",
                line,
                re.IGNORECASE,
        ):
            value = _extract_value_after_label(
                lines,
                index,
                r"father(?:['’]s)?\s+name",
            )

            father_name = _clean_name(value)


        if dob is None and re.search(
            r"date\s+of\s+birth",
            line,
            re.IGNORECASE,
        ):

            value = _extract_value_after_label(
                lines,
                index,
                r"date\s+of\s+birth\s*:",
            )

            if value:
                match = DATE_PATTERN.search(value)

                if match:
                    dob = match.group(0)


        if date_of_issue is None and re.search(
            r"date\s+of\s+issue",
            line,
            re.IGNORECASE,
        ):

            value = _extract_value_after_label(
                lines,
                index,
                r"date\s+of\s+issue\s*:",
            )

            if value:
                match = DATE_PATTERN.search(value)

                if match:
                    date_of_issue = match.group(0)



    dates = DATE_PATTERN.findall(ocr_text)

    if dob is None and dates:
        dob = dates[0]

    if date_of_issue is None and len(dates) >= 2:
        date_of_issue = dates[1]

    return PanCardData(
        pan_number=pan_number,
        name=name,
        father_name=father_name,
        dob=dob,
        date_of_issue=date_of_issue,
    )