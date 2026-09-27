import pandas as pd


FILE_PATH = "data/hdfs/HDFS_100k.log_structured.csv"

df = pd.read_csv(FILE_PATH)

print("Columns:")
print(df.columns.tolist())

print("\nRows:")
print(len(df))

print("\nFirst five rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())