import json

import numpy as np
from ollama import chat


MODEL_NAME = "llama3.2:1b"


def make_json_safe(value):
    """
    Recursively convert NumPy and other non-standard
    values into normal Python types that json.dumps()
    can serialize.
    """

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, np.ndarray):
        return make_json_safe(
            value.tolist()
        )

    if isinstance(value, np.generic):
        return value.item()

    return value


class LLMReportGenerator:
    def generate(self, incident_context: dict) -> str:

        safe_context = make_json_safe(
            incident_context
        )

        evidence_json = json.dumps(
            safe_context,
            indent=2,
        )

        prompt = f"""
You are assisting with defensive cybersecurity
incident analysis.

Only use the evidence provided below.
Do not invent indicators or events.

Generate a concise incident intelligence report
with the following sections:

1. Incident Summary
2. Evidence
3. Severity Assessment
4. Recommended Investigation Actions
5. Limitations / Uncertainty

Evidence:
{evidence_json}
"""

        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.message.content