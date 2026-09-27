from src.evidence import EvidenceResult


class IncidentOrchestrator:

    SUSPICIOUS_CLASSIFICATIONS = {
        "phishing",
        "anomalous",
        "suspicious",
    }

    def combine(
        self,
        evidence_items: list[EvidenceResult],
    ) -> dict:

        suspicious_items = [
            item
            for item in evidence_items
            if item.classification.lower()
            in self.SUSPICIOUS_CLASSIFICATIONS
        ]

        indicators = []

        for item in evidence_items:
            indicators.extend(
                item.indicators
            )

        confidence_values = [
            item.confidence
            for item in suspicious_items
            if item.confidence is not None
        ]

        highest_confidence = (
            max(confidence_values)
            if confidence_values
            else 0.0
        )

        # -----------------------------------------
        # Severity reasoning
        # -----------------------------------------

        if len(suspicious_items) >= 2:
            severity = "High"

        elif (
            len(suspicious_items) == 1
            and highest_confidence >= 0.90
        ):
            severity = "High"

        elif len(suspicious_items) == 1:
            severity = "Medium"

        else:
            severity = "Low"

        return {
            "evidence_count":
                len(evidence_items),

            "suspicious_evidence_count":
                len(suspicious_items),

            "classifications": [
                item.classification
                for item in evidence_items
            ],

            "highest_suspicious_confidence":
                highest_confidence,

            "combined_indicators":
                indicators,

            "severity":
                severity,

            "evidence": [
                item.to_dict()
                for item in evidence_items
            ],
        }