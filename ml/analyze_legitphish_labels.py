import pandas as pd

FILE_PATH = "data/raw/url_features_extracted1.csv"

df = pd.read_csv(FILE_PATH)

print("========== CLASS LABELS ==========")
print(df["ClassLabel"].value_counts(dropna=False))

print("\nExpected according to dataset documentation:")
print("0 = Phishing")
print("1 = Legitimate")

print("\n========== DUPLICATE URLs ==========")
print("Total rows:", len(df))
print("Unique URLs:", df["URL"].nunique())
print("Duplicate URL occurrences:", df["URL"].duplicated().sum())

print("\n========== MISSING VALUES ==========")
print(df[["URL", "ClassLabel"]].isnull().sum())

print("\n========== LEGITIMATE SUBSET ==========")
legit = df[df["ClassLabel"] == 1]

print("Legitimate rows:", len(legit))
print("Unique legitimate URLs:", legit["URL"].nunique())

print("\nFirst 10 legitimate URLs:")
print(legit["URL"].head(10).to_string(index=False))