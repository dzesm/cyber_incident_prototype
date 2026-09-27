from pathlib import Path

import pytest

from src.ocr_analyser import OCRAnalyser


@pytest.fixture(scope="module")
def ocr():
    return OCRAnalyser()


def test_missing_image_raises_error(ocr):
    with pytest.raises(FileNotFoundError):
        ocr.analyse(
            "data/ocr_samples/does_not_exist.png"
        )


def test_ocr_returns_expected_structure(ocr):
    sample_path = Path(
        "data/ocr_samples/sample_phishing.png"
    )

    if not sample_path.exists():
        pytest.skip(
            "OCR sample image not available."
        )

    result = ocr.analyse(
        str(sample_path)
    )

    assert "extracted_text" in result
    assert "items" in result
    assert "average_confidence" in result
    assert "item_count" in result

    assert isinstance(
        result["extracted_text"],
        str,
    )

    assert (
        0.0
        <= result["average_confidence"]
        <= 1.0
    )