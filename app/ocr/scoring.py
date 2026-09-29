import re


import re


def score_ocr_text(text: str) -> float:
    """
    Calculate a generic OCR quality score.

    The score rewards readable words and alphanumeric content,
    while penalizing fragmented and symbol-heavy OCR output.
    """

    if not text or not text.strip():
        return 0.0

    non_whitespace = [
        char for char in text
        if not char.isspace()
    ]

    if not non_whitespace:
        return 0.0

    alphanumeric_count = sum(
        char.isalnum()
        for char in non_whitespace
    )

    alphanumeric_ratio = (
        alphanumeric_count / len(non_whitespace)
    )

    tokens = re.findall(
        r"[A-Za-z0-9]{2,}",
        text,
    )

    token_count = len(tokens)

    if token_count:
        meaningful_tokens = [
            token
            for token in tokens
            if len(token) >= 3
        ]

        meaningful_token_ratio = (
            len(meaningful_tokens) / token_count
        )
    else:
        meaningful_token_ratio = 0.0

    isolated_character_count = len(
        re.findall(
            r"(?<![A-Za-z0-9])[A-Za-z0-9](?![A-Za-z0-9])",
            text,
        )
    )

    isolated_character_penalty = min(
        isolated_character_count / 20,
        1.0,
    )

    length_score = min(
        len(non_whitespace) / 500,
        1.0,
    )

    token_score = min(
        token_count / 30,
        1.0,
    )

    score = (
        (alphanumeric_ratio * 0.35)
        + (length_score * 0.15)
        + (token_score * 0.20)
        + (meaningful_token_ratio * 0.30)
        - (isolated_character_penalty * 0.20)
    )

    score = max(0.0, min(score, 1.0))

    return round(score * 100, 2)

def rank_ocr_candidates(candidates):
    return sorted(
        candidates,
        key=lambda candidate: candidate.score,
        reverse=True,
    )
