import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import CountVectorizer
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


print("Loading processed HDFS block dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Total blocks: {len(df)}")
print(f"Normal blocks: {(df['Label'] == 'Normal').sum()}")
print(f"Anomalous blocks: {(df['Label'] == 'Anomaly').sum()}")


# -------------------------------------------------
# Split the dataset
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
# Create event-frequency features
# -------------------------------------------------

vectorizer = CountVectorizer(
    token_pattern=r"E\d+",
    lowercase=False,
)

X_train_all = vectorizer.fit_transform(
    train_df["EventSequence"]
)

X_test = vectorizer.transform(
    test_df["EventSequence"]
)


# -------------------------------------------------
# Isolation Forest is trained only on NORMAL blocks
# -------------------------------------------------

normal_mask = (
    train_df["Label"].values == "Normal"
)

X_train_normal = X_train_all[
    normal_mask
]

print(
    f"\nNormal blocks used to fit Isolation Forest: "
    f"{X_train_normal.shape[0]}"
)

print(
    f"Event features: "
    f"{X_train_normal.shape[1]}"
)


# -------------------------------------------------
# Train anomaly detector
# -------------------------------------------------

model = IsolationForest(
    n_estimators=200,
    contamination=0.04,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

print("\nTraining Isolation Forest...")

model.fit(X_train_normal)


# -------------------------------------------------
# Predict
#
# IsolationForest:
#  1 = normal
# -1 = anomaly
#
# Ground truth:
#  0 = normal
#  1 = anomaly
# -------------------------------------------------

predictions = model.predict(X_test)

y_pred = [
    1 if prediction == -1 else 0
    for prediction in predictions
]

y_true = [
    1 if label == "Anomaly" else 0
    for label in test_df["Label"]
]


# -------------------------------------------------
# Metrics
# -------------------------------------------------

accuracy = accuracy_score(
    y_true,
    y_pred,
)

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0,
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0,
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0,
)

matrix = confusion_matrix(
    y_true,
    y_pred,
)

report = classification_report(
    y_true,
    y_pred,
    target_names=[
        "Normal",
        "Anomaly",
    ],
    zero_division=0,
)


tn, fp, fn, tp = matrix.ravel()


# -------------------------------------------------
# Display results
# -------------------------------------------------

print("\n===================================")
print("HDFS LOG ANOMALY EVALUATION RESULTS")
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
print(report)


# -------------------------------------------------
# Save evaluation results
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
    "dataset": "LogHub HDFS_v1 / HDFS_100k structured subset",
    "total_blocks": len(df),
    "normal_blocks": int(
        (df["Label"] == "Normal").sum()
    ),
    "anomaly_blocks": int(
        (df["Label"] == "Anomaly").sum()
    ),
    "training_blocks": len(train_df),
    "testing_blocks": len(test_df),
    "normal_training_blocks": int(
        X_train_normal.shape[0]
    ),
    "event_features": int(
        X_train_normal.shape[1]
    ),
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
    RESULTS_DIR / "log_model_evaluation.json",
    "w",
) as file:
    json.dump(
        results,
        file,
        indent=4,
    )


# -------------------------------------------------
# Save trained model + vectorizer
# -------------------------------------------------

joblib.dump(
    model,
    MODEL_DIR / "log_isolation_forest.joblib",
)

joblib.dump(
    vectorizer,
    MODEL_DIR / "log_event_vectorizer.joblib",
)


print(
    "\nResults saved to "
    "results/log_model_evaluation.json"
)

print(
    "Model saved to "
    "models/log_isolation_forest.joblib"
)

print(
    "Vectorizer saved to "
    "models/log_event_vectorizer.joblib"
)