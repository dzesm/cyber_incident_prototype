import pytest

from src.phishing_model import PhishingModel


@pytest.fixture(scope="module")
def model():
    return PhishingModel()


def test_model_detects_phishing(model):
    email = """
    Your account will be suspended immediately.

    Verify your login credentials here:
    https://secure-account-login.example.com
    """

    result = model.analyse(email)

    assert result["classification"] == "Phishing"

    assert 0 <= result["confidence"] <= 1


def test_model_detects_legitimate_email(model):
    email = """
    Hello,

    The project meeting has been moved to Tuesday at 14:00.

    Please let me know if you are unable to attend.

    Kind regards,
    Project Team
    """

    result = model.analyse(email)

    assert result["classification"] == "Legitimate"

    assert 0 <= result["confidence"] <= 1


def test_probabilities_sum_to_one(model):
    email = "Please review tomorrow's meeting agenda."

    result = model.analyse(email)

    total = (
        result["phishing_probability"]
        + result["legitimate_probability"]
    )

    assert total == pytest.approx(
        1.0,
        abs=0.001,
    )