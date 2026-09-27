import re


SUSPICIOUS_KEYWORDS = {
    "urgent_language": [
        "urgent",
        "immediately",
        "within 24 hours",
        "final warning",
        "act now",
        "your account will be suspended",
        "limited time",
        "verify now",
    ],
    "credential_request": [
        "password",
        "login",
        "credentials",
        "verify your account",
        "confirm your identity",
        "update your details",
        "security verification",
    ],
    "financial_pressure": [
        "payment",
        "invoice",
        "bank",
        "refund",
        "transaction",
        "billing",
        "unusual purchase",
    ],
    "impersonation": [
        "microsoft",
        "paypal",
        "google",
        "apple",
        "admin",
        "support team",
        "security team",
        "it department",
    ],
}


SUSPICIOUS_DOMAINS = [
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "shorturl",
    "free",
    "verify",
    "secure-login",
    "account-update",
    "login-confirm",
    "webscr",
    "auth",
]


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s)>'\"]+", text)


def extract_sender(text: str) -> str:
    sender_match = re.search(
        r"from:\s*(.+)",
        text,
        re.IGNORECASE,
    )

    return sender_match.group(1).strip() if sender_match else "Not detected"


def analyse_email(email_text: str) -> dict:
    text_lower = email_text.lower()

    urls = extract_urls(email_text)
    sender = extract_sender(email_text)

    indicators = []
    score = 0

    # Keyword-based indicators
    for category, words in SUSPICIOUS_KEYWORDS.items():
        matched = [
            word
            for word in words
            if word in text_lower
        ]

        if matched:
            indicators.append({
                "type": category.replace("_", " ").title(),
                "evidence": ", ".join(matched[:5]),
            })

            score += len(matched) * 10

    # External links
    if urls:
        indicators.append({
            "type": "External Link",
            "evidence": ", ".join(urls[:3]),
        })

        score += 20

    # Suspicious URL patterns
    suspicious_urls = []

    for url in urls:
        url_lower = url.lower()

        if any(
            domain_indicator in url_lower
            for domain_indicator in SUSPICIOUS_DOMAINS
        ):
            suspicious_urls.append(url)

    if suspicious_urls:
        indicators.append({
            "type": "Suspicious URL Pattern",
            "evidence": ", ".join(suspicious_urls[:3]),
        })

        score += 25

    # Brand impersonation
    if sender != "Not detected":
        sender_lower = sender.lower()

        known_brands = [
            "microsoft",
            "paypal",
            "google",
            "apple",
        ]

        if any(
            brand in text_lower
            for brand in known_brands
        ):
            if not any(
                brand in sender_lower
                for brand in known_brands
            ):
                indicators.append({
                    "type": "Possible Brand Impersonation",
                    "evidence": (
                        f"Sender appears as '{sender}', "
                        "while the message references a known service."
                    ),
                })

                score += 20

    score = min(score, 100)

    if score >= 70:
        classification = "Likely phishing"
        severity = "High"

    elif score >= 40:
        classification = "Suspicious"
        severity = "Medium"

    else:
        classification = "Low phishing likelihood"
        severity = "Low"

    return {
        "sender": sender,
        "urls": urls,
        "indicators": indicators,
        "score": score,
        "classification": classification,
        "severity": severity,
    }