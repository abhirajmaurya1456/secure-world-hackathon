import pandas as pd

FILE_PATH = "data/raw/tranco_top1m.csv"

df = pd.read_csv(FILE_PATH, header=None, names=["rank", "domain"])

print("Dataset shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 10 rows:")
print(df.head(10))

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate domains:")
print(df.iloc[:, 1].duplicated().sum())