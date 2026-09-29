from app.document_understanding.extractors.pan import extract_pan


def test_extract_pan_from_ocr_text():
    ocr_text = """
    INCOME TAX DEPARTMENT

    GOVT. OF INDIA
    penta oat
    eared char deer ars

    Permanent Account Number Card

    ABCDE1234F

    art / Name

    ROHIT KUMAR

    faar ar art / Father's Name

    SURESH KUMAR

    =H fAfer / Date of Birth

    15/08/1990

    ars ont act a faite
    Date of Issue
    20/05/2024
    """

    result = extract_pan(ocr_text)

    assert result.pan_number == "ABCDE1234F"
    assert result.name == "ROHIT KUMAR"
    assert result.father_name == "SURESH KUMAR"
    assert result.dob == "15/08/1990"
    assert result.date_of_issue == "20/05/2024"