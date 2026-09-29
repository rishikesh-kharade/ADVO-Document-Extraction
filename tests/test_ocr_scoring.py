from PIL import Image

from app import ocr
from app.ocr.scoring import score_ocr_text, rank_ocr_candidates
from app.ocr.tesseract import OCRCandidate, TesseractOCR
from app.ocr.candidate_selection import (evaluate_pan_candidate, select_best_candidate, select_best_pan_candidate, is_plausible_person_name,)
from app.extractors import extract_pan
from app.validators import validate_pan_number


def test_empty_text_has_zero_score():
    assert score_ocr_text("") == 0.0

def test_whitespace_only_has_zero_score():
    assert score_ocr_text("\n\t") == 0.0

def test_clean_ocr_text_scores_higher_than_garbage():
    clean_text = """
    INCOME TAX DEPARTMENT
    Permanent Account Number Card
    RISHIKESH ASHOK KHARADE
    19/05/2002
    JTKPK6540K
    """

    garbage_text = """
    @@@ !!! ### $$$ %%% ^^^
    &&& *** ((( )))) !!!
    """

    clean_score = score_ocr_text(clean_text)
    garbage_score = score_ocr_text(garbage_text)

    assert clean_score > garbage_score

def test_score_is_between_zero_and_hundred():
    text = """
    GOVERNMENT OF INDIA
    RAHUL KUMAR
    15-08-1994
    """

    score = score_ocr_text(text)

    assert 0.0 <= score <= 100.0

def test_candidates_are_ranked_by_score():
    candidates = [
        OCRCandidate(
            variant_name="adaptive",
            psm_mode = 6,
            text = "low quality text",
            score = 30.0,
        ),
        OCRCandidate(
            variant_name="grayscale",
            psm_mode = 3,
            text = "high quality text",
            score = 90.0,
        ),
        OCRCandidate(
            variant_name="otsu",
            psm_mode = 6,
            text = "medium quality text",
            score = 60.0,
        ),
    ]

    ranked = rank_ocr_candidates(candidates)

    assert ranked[0].score == 90.0
    assert ranked[1].score == 60.0
    assert ranked[2].score == 30.0


def test_extract_best_candidate_returns_highest_scored_candidate():
    ocr = TesseractOCR(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    image = Image.new("RGB", (500, 300), "white")

    candidate = ocr.extract_best_candidate(
        image = image,
        variant_names=("grayscale",),
        psm_modes=(3,6),
    )

    assert candidate is not None
    assert candidate.score >= 0.0
    assert candidate.score <= 100.0


def test_print_best_pan_candidate():
    ocr = TesseractOCR(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    image_path = r"D:\Projects\ADVO-Document-Extraction\tests\data\Pan_Sample.jpg"

    candidate = ocr.extract_candidates_from_file(
        image_path=image_path,
    )

    ranked = rank_ocr_candidates(candidate)

    print("\n==== OCR CANDIDATES ====")

    for item in ranked:
        print(
            f"\nScore: {item.score}"
            f"\nVariant: {item.variant_name}"
            f"\nPSM: {item.psm_mode}"
            f"\nText:\n{item.text[:1000]}"
        )

    print("\n==== BEST CANDIDATES ====")
    print("Score:", ranked[0].score)
    print("Variant:", ranked[0].variant_name)
    print("PSM:", ranked[0].psm_mode)
    print(ranked[0].text)

    assert ranked


def test_clean_structured_text_scores_higher_than_fragmented_text():
    clean_text = """
    INCOME TAX DEPARTMENT
    Permanent Account Number Card
    JTKPK6540K
    RISHIKESH ASHOK KHARADE
    ASHOK PRABHAKAR KHARADE
    19/05/2002
    """

    fragmemted_text = """
    @@@ !!! ###
    a
    f
    \
    nll
    FIR
    filed
    %%
    **
    RISHIKESH
    @@@
    """

    clean_score = score_ocr_text(clean_text)
    fragmemted_text = score_ocr_text(fragmemted_text)

    assert clean_score > fragmemted_text


def test_select_best_candidate_returns_highest_scored_candidate():
    candidates = [
        OCRCandidate(
            variant_name="adaptive",
            psm_mode = 6,
            text = "low quality text",
            score = 40.0,
        ),
        OCRCandidate(
            variant_name="grayscale",
            psm_mode = 3,
            text = "high quality text",
            score = 85.0,
        ),
        OCRCandidate(
            variant_name="otsu",
            psm_mode = 6,
            text = "medium quality text",
            score = 65.0,
        ),
    ]

    best_candidate = select_best_candidate(candidates)

    assert best_candidate.score == 85.0
    assert best_candidate.variant_name == "grayscale"
    assert best_candidate.psm_mode == 3

def test_select_best_candidate_rejects_empty_candidates():
    try:
        select_best_candidate([])
        assert False
    except ValueError as exc:
        assert str(exc) == "No OCR candidate available"


def test_pan_candidate_gets_document_score():
    candidate = OCRCandidate(
        variant_name="grayscale",
        psm_mode=3,
        text="""
        INCOME TAX DEPARTMENT
        Permanent Account Number Card

        JTKPK6540K

        Name
        RISHIKESH ASHOK KHARADE

        Father's Name
        ASHOK PRABHAKAR KHARADE

        Date of Birth
        19/05/2002
        """,
        score=70.0,
    )

    document_score = evaluate_pan_candidate(candidate)

    assert document_score > candidate.score
    assert document_score <= 100.0


def test_select_best_pan_candidate_uses_document_score():
    candidates = [
        OCRCandidate(
            variant_name="adaptive",
            psm_mode=6,
            text="""
            INCOME TAX DEPARTMENT
            JTKPK6540K
            RISHIKESH ASHOK KHARADE
            ASHOK PRABHAKAR KHARADE
            19/05/2002
            """,
            score=70.0,
        ),
        OCRCandidate(
            variant_name="grayscale",
            psm_mode=3,
            text="""
            random OCR text
            lots of unrelated content
            """,
            score=85.0,
        ),
    ]

    best_candidate = select_best_pan_candidate(candidates)

    assert best_candidate.variant_name == "adaptive"
    assert best_candidate.psm_mode == 6


def test_compare_generic_and_pan_best_candidate():
    ocr = TesseractOCR(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    image_path = r"D:\Projects\ADVO-Document-Extraction\tests\data\Pan_Sample.jpg"

    candidates = ocr.extract_candidates_from_file(
        image_path=image_path,
    )

    generic_best = select_best_candidate(candidates)
    pan_best = select_best_pan_candidate(candidates)

    print("\n===== GENERIC BEST =====")
    print("Score:", generic_best.score)
    print("Variant:", generic_best.variant_name)
    print("PSM:", generic_best.psm_mode)
    print(generic_best.text)

    print("\n===== PAN BEST =====")
    print(
        "Document score:",
        evaluate_pan_candidate(pan_best),
    )
    print("OCR score:", pan_best.score)
    print("Variant:", pan_best.variant_name)
    print("PSM:", pan_best.psm_mode)
    print(pan_best.text)

    assert candidates

def test_inspect_pan_candidate_evaluation():
    ocr = TesseractOCR(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    image_path = r"D:\Projects\ADVO-Document-Extraction\tests\data\Pan_Sample.jpg"

    candidates = ocr.extract_candidates_from_file(
        image_path=image_path,
    )

    ranked = sorted(
        candidates,
        key=evaluate_pan_candidate,
        reverse=True,
    )

    print("\n===== PAN CANDIDATE EVALUATION =====")

    for candidate in ranked[:5]:
        extracted = extract_pan(candidate.text)

        print("\n-----------------------------")
        print("Variant:", candidate.variant_name)
        print("PSM:", candidate.psm_mode)
        print("OCR score:", candidate.score)
        print(
            "PAN document score:",
            evaluate_pan_candidate(candidate),
        )
        print("PAN:", extracted.pan_number)
        print("Name:", extracted.name)
        print("Father:", extracted.father_name)
        print("DOB:", extracted.dob)

        if extracted.pan_number:
            print(
                "PAN valid:",
                validate_pan_number(extracted.pan_number),
            )

    assert ranked

def test_plausible_person_name_accepts_multiple_words():
    assert is_plausible_person_name(
        "RISHIKESH ASHOK KHARADE"
    )


def test_plausible_person_name_rejects_single_word():
    assert not is_plausible_person_name(
        "RISHIKESH"
    )


def test_plausible_person_name_rejects_empty_value():
    assert not is_plausible_person_name(
        None
    )