import pandas as pd

RAW_FILE = "data/raw/phishing.csv"
OUTPUT_FILE = "data/processed/phishing_clean.csv"

# Load raw dataset
df = pd.read_csv(RAW_FILE)

print("Original rows:", len(df))

# Keep only the URL column for our classification dataset
df = df[["url"]].copy()

# Remove duplicate URLs
df = df.drop_duplicates(subset="url")

# Remove empty/null URLs
df = df.dropna(subset=["url"])

# Add phishing label
df["label"] = 1

# Reset row numbers
df = df.reset_index(drop=True)

# Save cleaned dataset
df.to_csv(OUTPUT_FILE, index=False)

print("Cleaned rows:", len(df))
print("\nClass distribution:")
print(df["label"].value_counts())

print("\nSaved to:", OUTPUT_FILE)