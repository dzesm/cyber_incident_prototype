from src.screenshot_analyser import ScreenshotAnalyser


analyser = ScreenshotAnalyser()

result = analyser.analyse(
    "data/ocr_samples/sample_phishing.png"
)


print("OCR TEXT:")
print(
    result["ocr"]["extracted_text"]
)

print("\nOCR CONFIDENCE:")
print(
    f"{result['ocr']['average_confidence']:.2%}"
)

print("\nPHISHING CLASSIFICATION:")
print(
    result[
        "phishing_analysis"
    ]["classification"]
)

print("\nMODEL CONFIDENCE:")
print(
    f"{result['phishing_analysis']['confidence']:.2%}"
)