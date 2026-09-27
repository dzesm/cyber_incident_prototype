from src.ocr_analyser import OCRAnalyser
from src.phishing_model import PhishingModel


class ScreenshotAnalyser:
    def __init__(self):
        self.ocr = OCRAnalyser()
        self.phishing_model = PhishingModel()

    def analyse(self, image_path: str) -> dict:
        ocr_result = self.ocr.analyse(
            image_path
        )

        extracted_text = (
            ocr_result["extracted_text"]
        )

        if extracted_text.strip():
            phishing_result = (
                self.phishing_model.analyse(
                    extracted_text
                )
            )
        else:
            phishing_result = {
                "classification": "Unknown",
                "confidence": 0.0,
                "phishing_probability": 0.0,
                "legitimate_probability": 0.0,
                "model": None,
            }

        return {
            "source_type": "screenshot",
            "ocr": ocr_result,
            "phishing_analysis": phishing_result,
        }