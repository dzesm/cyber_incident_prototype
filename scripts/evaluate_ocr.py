from pathlib import Path
import json

from jiwer import wer, cer

from src.ocr_analyser import OCRAnalyser
from src.phishing_model import PhishingModel


SAMPLES_DIR = Path("data/ocr_samples")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


ocr = OCRAnalyser()
phishing_model = PhishingModel()


results = []


for image_path in sorted(SAMPLES_DIR.glob("*.png")):

    ground_truth_path = image_path.with_suffix(".txt")

    if not ground_truth_path.exists():
        print(
            f"Skipping {image_path.name}: "
            "no matching ground-truth file."
        )
        continue

    ground_truth = ground_truth_path.read_text(
        encoding="utf-8"
    ).strip()

    print(
        f"\nEvaluating {image_path.name}..."
    )

    ocr_result = ocr.analyse(
        str(image_path)
    )

    extracted_text = (
        ocr_result["extracted_text"].strip()
    )

    character_error_rate = cer(
        ground_truth,
        extracted_text,
    )

    word_error_rate = wer(
        ground_truth,
        extracted_text,
    )

    phishing_result = (
        phishing_model.analyse(
            extracted_text
        )
        if extracted_text
        else None
    )

    result = {
        "image": image_path.name,
        "ground_truth": ground_truth,
        "extracted_text": extracted_text,
        "ocr_confidence":
            ocr_result["average_confidence"],
        "cer": character_error_rate,
        "wer": word_error_rate,
        "phishing_classification":
            phishing_result["classification"]
            if phishing_result
            else "Unknown",
        "phishing_confidence":
            phishing_result["confidence"]
            if phishing_result
            else 0.0,
    }

    results.append(result)

    print(
        f"OCR confidence: "
        f"{result['ocr_confidence']:.2%}"
    )

    print(
        f"CER: {result['cer']:.4f}"
    )

    print(
        f"WER: {result['wer']:.4f}"
    )

    print(
        "Phishing classification: "
        f"{result['phishing_classification']}"
    )

    print(
        "Phishing confidence: "
        f"{result['phishing_confidence']:.2%}"
    )


if results:

    avg_cer = sum(
        item["cer"]
        for item in results
    ) / len(results)

    avg_wer = sum(
        item["wer"]
        for item in results
    ) / len(results)

    avg_confidence = sum(
        item["ocr_confidence"]
        for item in results
    ) / len(results)

    summary = {
        "sample_count": len(results),
        "average_cer": avg_cer,
        "average_wer": avg_wer,
        "average_ocr_confidence":
            avg_confidence,
        "samples": results,
    }

    with open(
        RESULTS_DIR / "ocr_evaluation_results.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
        )

    print("\n==============================")
    print("OCR EVALUATION SUMMARY")
    print("==============================")

    print(
        f"Samples evaluated: "
        f"{len(results)}"
    )

    print(
        f"Average CER: "
        f"{avg_cer:.4f}"
    )

    print(
        f"Average WER: "
        f"{avg_wer:.4f}"
    )

    print(
        f"Average OCR confidence: "
        f"{avg_confidence:.2%}"
    )

    print(
        "\nResults saved to "
        "results/ocr_evaluation_results.json"
    )

else:

    print(
        "No OCR samples with matching "
        "ground-truth files were found."
    )