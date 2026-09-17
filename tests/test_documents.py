from app.extractors import extract_pan, extract_aadhaar, extract_bank_passbook, extract_cancelled_cheque

from app.validators import validate_pan_number, validate_aadhaar_format, validate_aadhaar_verhoeff, validate_account_number, validate_ifsc


def test_extract_pan():

    ocr_text = """
    INCOME TAX DEPARTMENT
    GOVT. OF INDIA
    
    Name: RISHIKESH KHARADE
    Father's Name: TEST FATHER
    Date of Birth: 01/01/2000
    
    Permanent Account Number:
    ABCDE1234F
    """

    result = extract_pan(ocr_text)

    print("\nPAN EXTRACTION RESULT:")
    print(result)

    assert result.pan_number == "ABCDE1234F"
    assert result.name == "RISHIKESH KHARADE"
    assert result.father_name == "TEST FATHER"
    assert result.dob == "01/01/2000"


def test_extract_aadhaar():

    ocr_text = """
    GOVERNMENT OF INDIA
    
    Name: RISHIKESH KHARADE
    Date of Birth: 01/01/2000
    Gender: Male
    Address: BENGALURU, KARNATAKA
    
    Aadhaar Number:
    2345 6789 0123
    """

    result = extract_aadhaar(ocr_text)

    print("\nAADHAAR EXTRACTION RESULT:")
    print(result)

    assert result.aadhar_number == "234567890123"
    assert result.name == "RISHIKESH KHARADE"
    assert result.dob == "01/01/2000"
    assert result.gender == "Male"
    assert result.address == "BENGALURU, KARNATAKA"



def test_extract_bank_passbook():

    ocr_text = """
    BANK PASSBOOK

    Bank Name: STATE BANK OF INDIA
    Branch: BENGALURU MAIN BRANCH
    Account Holder Name: RISHIKESH KHARADE
    Account Number: 123456789012
    IFSC: SBIN0001234
    """

    result = extract_bank_passbook(ocr_text)

    print("\nBANK PASSBOOK EXTRACTION RESULT:")
    print(result)

    assert result.account_number == "123456789012"
    assert result.ifsc == "SBIN0001234"
    assert result.bank_name == "STATE BANK OF INDIA"
    assert result.branch == "BENGALURU MAIN BRANCH"
    assert result.account_holder_name == "RISHIKESH KHARADE"


def test_extract_cancelled_cheque():
    ocr_text = """
    CANCELLED CHEQUE

    Bank Name: STATE BANK OF INDIA
    Account Holder Name: RISHIKESH KHARADE
    Account Number: 123456789012
    IFSC: SBIN0001234
    """

    result = extract_cancelled_cheque(ocr_text)

    print("\nCANCELLED CHEQUE EXTRACTION RESULT:")
    print(result)

    assert result.account_number == "123456789012"
    assert result.ifsc == "SBIN0001234"
    assert result.bank_name == "STATE BANK OF INDIA"
    assert result.account_holder_name == "RISHIKESH KHARADE"


def test_validate_pan_number():

    assert validate_pan_number("ABCDE1234F") is True

    assert validate_pan_number("ABCDE12345") is False

    assert validate_pan_number("AB1234XVY44") is False

    assert validate_pan_number(None) is False

def test_validate_aadhaar_number():

    assert validate_aadhaar_format("234567890128") is True

    assert validate_aadhaar_format("12345678901") is False

    assert validate_aadhaar_format("1234567890123") is False

    assert validate_aadhaar_format(None) is False


def test_validate_aadhaar_verhoeff():

    # Valid 12-digit Verhoeff number
    assert validate_aadhaar_verhoeff("123456789010") is True

    # Changed final digit → invalid
    assert validate_aadhaar_verhoeff("123456789011") is False

    # Wrong length
    assert validate_aadhaar_verhoeff("12345678901") is False

    # Non-numeric
    assert validate_aadhaar_verhoeff("12345678901A") is False

    # Missing value
    assert validate_aadhaar_verhoeff(None) is False

def test_validate_account_number():

    assert validate_account_number("123456789012") is True

    assert validate_account_number("12345678") is False

    assert validate_account_number("1234567890123456789") is False

    assert validate_account_number("12345ABCDE") is False

    assert validate_account_number(None) is False


def test_validate_ifsc():

    assert validate_ifsc("SBIN0001234") is True

    assert validate_ifsc("SBIN1234567") is False

    assert validate_ifsc("SBI0001234") is False

    assert validate_ifsc("SBIN00012345") is False

    assert validate_ifsc(None) is False


def test_validate_cancelled_cheque_fields():

    account_number = "123456789012"
    ifsc = "SBIN0001234"

    assert validate_account_number(account_number) is True
    assert validate_ifsc(ifsc) is True

    assert validate_account_number("12345678") is False
    assert validate_ifsc("SBIN1234567") is False
