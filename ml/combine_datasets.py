import pandas as pd

PHISHING_FILE = "data/processed/phishing_clean.csv"
BENIGN_FILE = "data/processed/benign_clean.csv"
OUTPUT_FILE = "data/processed/combined_urls.csv"


# Load datasets
phishing_df = pd.read_csv(PHISHING_FILE)
benign_df = pd.read_csv(BENIGN_FILE)

print("Phishing rows:", len(phishing_df))
print("Benign rows:", len(benign_df))


# Combine
df = pd.concat(
    [phishing_df, benign_df],
    ignore_index=True
)


# Shuffle dataset
df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# Save
df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nCombined dataset:", len(df))

print("\nClass distribution:")
print(df["label"].value_counts())

print("\nFirst 10 rows:")
print(df.head(10))

print("\nSaved to:", OUTPUT_FILE)