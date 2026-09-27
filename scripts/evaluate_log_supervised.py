import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split


DATA_FILE = Path("data/hdfs/HDFS_blocks.csv")
RESULTS_DIR = Path("results")
MODEL_DIR = Path("models")

RANDOM_STATE = 42


# -------------------------------------------------
# Load dataset
# -------------------------------------------------

print("Loading processed HDFS block dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Total blocks: {len(df)}")
print(f"Normal blocks: {(df['Label'] == 'Normal').sum()}")
print(f"Anomalous blocks: {(df['Label'] == 'Anomaly').sum()}")


# -------------------------------------------------
# Train/test split
# -------------------------------------------------

train_df, test_df = train_test_split(
    df,
    test_size=0.30,
    random_state=RANDOM_STATE,
    stratify=df["Label"],
)

print(f"\nTraining blocks: {len(train_df)}")
print(f"Testing blocks: {len(test_df)}")

print("\nTest label distribution:")
print(test_df["Label"].value_counts())


# -------------------------------------------------
# Convert labels
# -------------------------------------------------

y_train = (
    train_df["Label"] == "Anomaly"
).astype(int)

y_test = (
    test_df["Label"] == "Anomaly"
).astype(int)


# -------------------------------------------------
# Event-sequence representation
#
# ngram_range=(1, 3) captures:
# individual events: E5
# pairs:             E5 E11
# triples:           E5 E11 E9
# -------------------------------------------------

vectorizer = TfidfVectorizer(
    token_pattern=r"E\d+",
    lowercase=False,
    ngram_range=(1, 3),
)

X_train = vectorizer.fit_transform(
    train_df["EventSequence"]
)

X_test = vectorizer.transform(
    test_df["EventSequence"]
)

print(
    f"\nSequence features generated: "
    f"{X_train.shape[1]}"
)


# -------------------------------------------------
# Train classifier
#
# class_weight='balanced' compensates for the
# strong Normal/Anomaly class imbalance.
# -------------------------------------------------

model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=RANDOM_STATE,
)

print("\nTraining Logistic Regression...")

model.fit(
    X_train,
    y_train,
)


# -------------------------------------------------
# Prediction
# -------------------------------------------------

y_pred = model.predict(
    X_test
)

probabilities = model.predict_proba(
    X_test
)[:, 1]


# -------------------------------------------------
# Evaluation
# -------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred,
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0,
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0,
)

matrix = confusion_matrix(
    y_test,
    y_pred,
)

tn, fp, fn, tp = matrix.ravel()


print("\n===================================")
print("SUPERVISED LOG EVALUATION RESULTS")
print("===================================")

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nConfusion Matrix:")
print(matrix)

print("\nDetailed results:")
print(f"True Negatives:  {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Positives:  {tp}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Normal",
            "Anomaly",
        ],
        zero_division=0,
    )
)


# -------------------------------------------------
# Save results
# -------------------------------------------------

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

results = {
    "dataset":
        "LogHub HDFS_v1 / HDFS_100k structured subset",

    "algorithm":
        "TF-IDF event n-grams + Logistic Regression",

    "total_blocks":
        len(df),

    "normal_blocks":
        int((df["Label"] == "Normal").sum()),

    "anomaly_blocks":
        int((df["Label"] == "Anomaly").sum()),

    "training_blocks":
        len(train_df),

    "testing_blocks":
        len(test_df),

    "sequence_features":
        X_train.shape[1],

    "accuracy":
        accuracy,

    "precision":
        precision,

    "recall":
        recall,

    "f1_score":
        f1,

    "true_negatives":
        int(tn),

    "false_positives":
        int(fp),

    "false_negatives":
        int(fn),

    "true_positives":
        int(tp),
}


with open(
    RESULTS_DIR / "log_supervised_evaluation.json",
    "w",
) as file:

    json.dump(
        results,
        file,
        indent=4,
    )


# -------------------------------------------------
# Save model
# -------------------------------------------------

joblib.dump(
    model,
    MODEL_DIR / "log_classifier.joblib",
)

joblib.dump(
    vectorizer,
    MODEL_DIR / "log_tfidf_vectorizer.joblib",
)


print(
    "\nResults saved to "
    "results/log_supervised_evaluation.json"
)

print(
    "Model saved to "
    "models/log_classifier.joblib"
)

print(
    "Vectorizer saved to "
    "models/log_tfidf_vectorizer.joblib"
)