from src.ocr_analyser import OCRAnalyser


ocr = OCRAnalyser()

result = ocr.analyse(
    "data/ocr_samples/sample_phishing.png"
)

print("Extracted text:")
print(result["extracted_text"])

print("\nAverage confidence:")
print(result["average_confidence"])

print("\nDetected items:")
for item in result["items"]:
    print(
        f"{item['text']} "
        f"({item['confidence']:.2%})"
    )