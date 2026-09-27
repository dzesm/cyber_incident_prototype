import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


MODEL_ID = "aamoshdahal/email-phishing-distilbert-finetuned"


class PhishingModel:
    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_ID
        )

        self.model.to(self.device)
        self.model.eval()

    def analyse(self, email_text: str) -> dict:
        inputs = self.tokenizer(
            email_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=1,
        )[0]

        legitimate_probability = probabilities[0].item()
        phishing_probability = probabilities[1].item()

        if phishing_probability >= legitimate_probability:
            classification = "Phishing"
            confidence = phishing_probability
        else:
            classification = "Legitimate"
            confidence = legitimate_probability

        return {
            "classification": classification,
            "confidence": confidence,
            "phishing_probability": phishing_probability,
            "legitimate_probability": legitimate_probability,
            "model": MODEL_ID,
        }