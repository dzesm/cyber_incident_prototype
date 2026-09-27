import pandas as pd


FILE_PATH = "data/hdfs/anomaly_label.csv"


df = pd.read_csv(FILE_PATH)

print("Columns:")
print(df.columns.tolist())

print("\nRows:")
print(len(df))

print("\nLabel distribution:")
print(df.iloc[:, -1].value_counts())

print("\nFirst five rows:")
print(df.head())