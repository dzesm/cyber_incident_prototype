from collections import Counter

from datasets import load_dataset


DATASET_ID = "zefang-liu/phishing-email-dataset"


dataset = load_dataset(DATASET_ID)


print(dataset)

for split_name, split in dataset.items():
    print()
    print(f"Split: {split_name}")
    print(f"Rows: {len(split)}")
    print(f"Columns: {split.column_names}")

    print()
    print("First row:")
    print(split[0])

from collections import Counter

labels = dataset["train"]["Email Type"]

print("\nLabel distribution:")
for label, count in Counter(labels).items():
    percentage = (count / len(labels)) * 100
    print(f"{label}: {count} ({percentage:.2f}%)")