import re
from pathlib import Path

import pandas as pd


LOG_FILE = Path("data/hdfs/HDFS_100k.log_structured.csv")
LABEL_FILE = Path("data/hdfs/anomaly_label.csv")
OUTPUT_FILE = Path("data/hdfs/HDFS_blocks.csv")


def extract_block_ids(content):
    """
    Extract all HDFS block identifiers from a log message.

    Example:
    blk_-1608999687919862906
    """
    return re.findall(
        r"blk_-?\d+",
        str(content)
    )


print("Loading structured HDFS logs...")

logs = pd.read_csv(LOG_FILE)

print(f"Log lines loaded: {len(logs)}")


# -------------------------------------------------
# Extract block IDs from each log line
# -------------------------------------------------

records = []

for _, row in logs.iterrows():

    block_ids = extract_block_ids(
        row["Content"]
    )

    for block_id in block_ids:

        records.append({
            "BlockId": block_id,
            "EventId": row["EventId"],
            "Level": row["Level"],
            "Component": row["Component"],
        })


events = pd.DataFrame(records)

print(
    f"Log-event/block relationships extracted: "
    f"{len(events)}"
)

print(
    f"Unique blocks found: "
    f"{events['BlockId'].nunique()}"
)


# -------------------------------------------------
# Group events by HDFS block
# -------------------------------------------------

blocks = (
    events
    .groupby("BlockId")
    .agg(
        EventSequence=(
            "EventId",
            lambda values: " ".join(values)
        ),
        EventCount=(
            "EventId",
            "count"
        ),
        UniqueEventCount=(
            "EventId",
            "nunique"
        ),
        Components=(
            "Component",
            lambda values:
                " ".join(sorted(set(values)))
        ),
        Levels=(
            "Level",
            lambda values:
                " ".join(sorted(set(values)))
        ),
    )
    .reset_index()
)


# -------------------------------------------------
# Add official ground-truth labels
# -------------------------------------------------

labels = pd.read_csv(LABEL_FILE)

blocks = blocks.merge(
    labels,
    on="BlockId",
    how="left",
)


print("\nBlocks after grouping:")
print(len(blocks))

print("\nMissing labels:")
print(blocks["Label"].isna().sum())

print("\nLabel distribution:")
print(blocks["Label"].value_counts(dropna=False))


# Remove blocks for which ground truth is unavailable
blocks = blocks.dropna(
    subset=["Label"]
)


# -------------------------------------------------
# Save processed block dataset
# -------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

blocks.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\nSaved processed dataset to: "
    f"{OUTPUT_FILE}"
)

print("\nFirst five blocks:")
print(
    blocks[
        [
            "BlockId",
            "EventSequence",
            "EventCount",
            "UniqueEventCount",
            "Label",
        ]
    ].head()
)