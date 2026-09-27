import re
from pathlib import Path

import joblib


MODEL_FILE = Path("models/log_classifier.joblib")
VECTORIZER_FILE = Path("models/log_tfidf_vectorizer.joblib")


class LogAnalyser:
    def __init__(self):
        self.model = joblib.load(MODEL_FILE)
        self.vectorizer = joblib.load(VECTORIZER_FILE)

    def extract_event_sequence(self, log_text: str) -> str:
        """
        Extract HDFS EventIds such as E5, E11 and E22
        from supplied structured log evidence.
        """
        event_ids = re.findall(
            r"\bE\d+\b",
            log_text
        )

        return " ".join(event_ids)

    def analyse(self, log_text: str) -> dict:

        event_sequence = self.extract_event_sequence(
            log_text
        )

        if not event_sequence:
            return {
                "source_type": "security_log",
                "classification": "Unknown",
                "confidence": 0.0,
                "anomaly_probability": 0.0,
                "event_sequence": "",
                "event_count": 0,
                "reason":
                    "No HDFS EventIds were detected.",
            }

        features = self.vectorizer.transform(
            [event_sequence]
        )

        prediction = self.model.predict(
            features
        )[0]

        probabilities = self.model.predict_proba(
            features
        )[0]

        normal_probability = float(
            probabilities[0]
        )

        anomaly_probability = float(
            probabilities[1]
        )

        if prediction == 1:
            classification = "Anomalous"
            confidence = anomaly_probability
        else:
            classification = "Normal"
            confidence = normal_probability

        events = event_sequence.split()

        return {
            "source_type": "security_log",
            "classification": classification,
            "confidence": confidence,
            "anomaly_probability":
                anomaly_probability,
            "normal_probability":
                normal_probability,
            "event_sequence":
                event_sequence,
            "event_count":
                len(events),
            "unique_event_count":
                len(set(events)),
            "model":
                "TF-IDF event n-grams + Logistic Regression",
        }