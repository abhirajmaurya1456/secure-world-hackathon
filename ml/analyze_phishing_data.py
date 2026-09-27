import pandas as pd

FILE_PATH = "data/raw/phishing.csv"

df = pd.read_csv(FILE_PATH)

print("========== BASIC INFORMATION ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n========== VERIFIED ==========")
print(df["verified"].value_counts(dropna=False))

print("\n========== ONLINE ==========")
print(df["online"].value_counts(dropna=False))

print("\n========== DUPLICATES ==========")
print("Duplicate URLs:", df["url"].duplicated().sum())
print("Unique URLs:", df["url"].nunique())

print("\n========== TARGETS ==========")
print("Unique targets:", df["target"].nunique())
print(df["target"].value_counts().head(20))