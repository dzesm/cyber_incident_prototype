from pathlib import Path

import easyocr


class OCRAnalyser:
    def __init__(self):
        # gpu=False keeps this predictable on machines without CUDA
        self.reader = easyocr.Reader(
            ["en"],
            gpu=False,
        )

    def analyse(self, image_path: str) -> dict:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        results = self.reader.readtext(
            str(path),
            detail=1,
            paragraph=False,
        )

        extracted_items = []

        for bounding_box, text, confidence in results:
            extracted_items.append({
                "text": text,
                "confidence": float(confidence),
                "bounding_box": bounding_box,
            })

        combined_text = " ".join(
            item["text"]
            for item in extracted_items
        )

        if extracted_items:
            average_confidence = sum(
                item["confidence"]
                for item in extracted_items
            ) / len(extracted_items)
        else:
            average_confidence = 0.0

        return {
            "source_type": "screenshot",
            "extracted_text": combined_text,
            "items": extracted_items,
            "average_confidence": average_confidence,
            "item_count": len(extracted_items),
        }