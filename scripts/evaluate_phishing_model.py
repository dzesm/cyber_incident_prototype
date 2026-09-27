from pathlib import Path
import json

from datasets import load_dataset
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split

from src.phishing_model import PhishingModel


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DATASET_ID = "zefang-liu/phishing-email-dataset"
SAMPLE_SIZE = 500
RANDOM_STATE = 42

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading phishing email dataset...")

dataset = load_dataset(DATASET_ID)
data = dataset["train"]

texts = data["Email Text"]
labels = data["Email Type"]


# Convert:
# Safe Email     -> 0
# Phishing Email -> 1

binary_labels = [
    1 if label == "Phishing Email" else 0
    for label in labels
]


# --------------------------------------------------
# Create reproducible stratified sample
# --------------------------------------------------

sample_texts, _, sample_labels, _ = train_test_split(
    texts,
    binary_labels,
    train_size=SAMPLE_SIZE,
    stratify=binary_labels,
    random_state=RANDOM_STATE,
)

print(f"Evaluation sample size: {len(sample_texts)}")
print(f"Phishing emails: {sum(sample_labels)}")
print(
    f"Safe emails: "
    f"{len(sample_labels) - sum(sample_labels)}"
)


# --------------------------------------------------
# Load model
# --------------------------------------------------

print("\nLoading phishing detection model...")

model = PhishingModel()


# --------------------------------------------------
# Generate predictions
# --------------------------------------------------

predictions = []

print("Running model evaluation...")

for index, email_text in enumerate(sample_texts, start=1):

    if email_text is None:
        email_text = ""

    result = model.analyse(email_text)

    if result["classification"] == "Phishing":
        prediction = 1
    else:
        prediction = 0

    predictions.append(prediction)

    if index % 50 == 0:
        print(
            f"Processed {index}/{SAMPLE_SIZE} emails"
        )


# --------------------------------------------------
# Metrics
# --------------------------------------------------

accuracy = accuracy_score(
    sample_labels,
    predictions,
)

precision = precision_score(
    sample_labels,
    predictions,
    zero_division=0,
)

recall = recall_score(
    sample_labels,
    predictions,
    zero_division=0,
)

f1 = f1_score(
    sample_labels,
    predictions,
    zero_division=0,
)

cm = confusion_matrix(
    sample_labels,
    predictions,
)

tn, fp, fn, tp = cm.ravel()


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n===================================")
print("PHISHING MODEL EVALUATION RESULTS")
print("===================================")

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nConfusion Matrix:")
print(cm)

print("\nDetailed results:")
print(f"True Negatives:  {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Positives:  {tp}")

print("\nClassification Report:")

report = classification_report(
    sample_labels,
    predictions,
    target_names=[
        "Safe Email",
        "Phishing Email",
    ],
    zero_division=0,
)

print(report)


# --------------------------------------------------
# Save results
# --------------------------------------------------

results = {
    "dataset": DATASET_ID,
    "dataset_total_rows": len(data),
    "evaluation_sample_size": SAMPLE_SIZE,
    "random_state": RANDOM_STATE,
    "safe_emails_in_sample": (
        len(sample_labels) - sum(sample_labels)
    ),
    "phishing_emails_in_sample": sum(sample_labels),
    "accuracy": accuracy,
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "true_negatives": int(tn),
    "false_positives": int(fp),
    "false_negatives": int(fn),
    "true_positives": int(tp),
}

with open(
    RESULTS_DIR / "phishing_model_results.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        results,
        file,
        indent=4,
    )

with open(
    RESULTS_DIR / "phishing_model_classification_report.txt",
    "w",
    encoding="utf-8",
) as file:
    file.write(report)

print(
    "\nResults saved in the 'results' directory."
)