from datetime import datetime


def generate_incident_report(
    email_text: str,
    analysis: dict,
) -> str:

    indicators_text = "\n".join(
        [
            f"- {item['type']}: {item['evidence']}"
            for item in analysis["indicators"]
        ]
    ) or "- No major phishing indicators were detected."

    if analysis["severity"] == "High":
        recommendation = (
            "Block the sender, do not click links, investigate whether "
            "users interacted with the email, and review authentication "
            "logs for unusual activity."
        )

    elif analysis["severity"] == "Medium":
        recommendation = (
            "Quarantine the email, inspect the URLs safely, warn the "
            "recipient, and monitor related account activity."
        )

    else:
        recommendation = (
            "Keep the message under review and confirm sender legitimacy "
            "before taking further action."
        )

    report = f"""
INCIDENT INTELLIGENCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

1. Incident Summary
The submitted email was analysed for phishing-related indicators.
The prototype classified the message as: {analysis['classification']}.

2. Extracted Evidence
Sender: {analysis['sender']}
Detected URLs: {
    ', '.join(analysis['urls'])
    if analysis['urls']
    else 'None detected'
}

Indicators identified:
{indicators_text}

3. Severity Assessment
Severity: {analysis['severity']}
Risk score: {analysis['score']} / 100

4. Recommended Actions
{recommendation}

5. Prototype Note
This analysis supports analyst decision-making and should not be treated
as a final security verdict.
"""

    return report.strip()