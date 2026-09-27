from src.email_rules import (
    analyse_email,
    extract_sender,
    extract_urls,
)


def test_extract_sender():

    email = """
From: security@example.com
Subject: Test
"""

    assert (
        extract_sender(email)
        == "security@example.com"
    )


def test_sender_not_detected():

    email = "This email has no sender header."

    assert (
        extract_sender(email)
        == "Not detected"
    )


def test_extract_url():

    email = """
Click here:
https://example.com/login
"""

    urls = extract_urls(email)

    assert urls == [
        "https://example.com/login"
    ]


def test_legitimate_email_has_low_risk():

    email = """
From: lecturer@university.edu
Subject: Lecture timetable

Hello,

The lecture will begin tomorrow at 10:00.

Kind regards,
University
"""

    result = analyse_email(email)

    assert (
        result["classification"]
        == "Low phishing likelihood"
    )

    assert result["severity"] == "Low"


def test_phishing_email_detected():

    email = """
From: attacker@example.com
Subject: Urgent account warning

Your account will be suspended within 24 hours.

Verify your login credentials immediately:

https://secure-login-account-update.example.com/verify

Microsoft Security Team
"""

    result = analyse_email(email)

    assert result["classification"] == "Likely phishing"

    assert result["severity"] == "High"

    assert result["score"] >= 70


def test_risk_score_never_exceeds_100():

    email = """
From: attacker@example.com

URGENT immediately act now final warning.

Your account will be suspended within 24 hours.

Verify your account.
Confirm your identity.
Enter your password and login credentials.

Payment invoice bank refund transaction billing.

https://secure-login-account-update.example.com/verify

Microsoft Support Team
"""

    result = analyse_email(email)

    assert result["score"] <= 100


def test_suspicious_url_detected():

    email = """
From: attacker@example.com

Visit:
https://secure-login-account-update.example.com/verify
"""

    result = analyse_email(email)

    indicator_types = [
        item["type"]
        for item in result["indicators"]
    ]

    assert "Suspicious URL Pattern" in indicator_types