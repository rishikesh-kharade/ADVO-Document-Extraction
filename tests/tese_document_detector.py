from app.document_detector import DocumentDetector, DocumentType


def test_detect_pan():
    text = """
    INCOME TAX DEPARTMENT
    PERMANENT ACCOUNT NUMBER
    RISHIKESH ASHOK KHARADE
    JTKPK6540K
    """

    detector = DocumentDetector()

    assert detector.detect(text) == DocumentType.PAN


def test_detect_aadhaar():
    text = """
    GOVERNMENT OF INDIA
    AADHAAR
    RAHUL KUMAR
    1234 5678 9012
    """

    detector = DocumentDetector()

    assert detector.detect(text) == DocumentType.AADHAAR


def test_detect_passbook():
    text = """
    STATE BANK OF INDIA
    CUSTOMER NAME
    ACCOUNT NUMBER
    BRANCH
    IFSC
    """

    detector = DocumentDetector()

    assert detector.detect(text) == DocumentType.PASSBOOK


def test_detect_cancelled_cheque():
    text = """
    STATE BANK OF INDIA
    CANCELLED CHEQUE
    A/C NO
    IFSC
    """

    detector = DocumentDetector()

    assert detector.detect(text) == DocumentType.CANCELLED_CHEQUE


def test_detect_unknown_document():
    text = """
    THIS IS A DRIVING LICENCE
    LICENSE NUMBER
    DATE OF ISSUE
    """

    detector = DocumentDetector()

    assert detector.detect(text) == DocumentType.UNKNOWN


def test_empty_text_is_unknown():
    detector = DocumentDetector()

    assert detector.detect("") == DocumentType.UNKNOWN