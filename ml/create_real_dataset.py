import pandas as pd

PHISHING_FILE = "data/processed/phishing_clean.csv"
BENIGN_FILE = "data/processed/benign_real_clean.csv"

OUTPUT_FILE = "data/processed/real_url_dataset.csv"


# -----------------------------------
# 1. Load datasets
# -----------------------------------

phishing_df = pd.read_csv(PHISHING_FILE)
benign_df = pd.read_csv(BENIGN_FILE)

print("Available phishing URLs:", len(phishing_df))
print("Available benign URLs:", len(benign_df))


# -----------------------------------
# 2. Match the class sizes
# -----------------------------------

sample_size = len(benign_df)

phishing_sample = phishing_df.sample(
    n=sample_size,
    random_state=42
).copy()

print("\nSelected phishing URLs:", len(phishing_sample))
print("Selected benign URLs:", len(benign_df))


# -----------------------------------
# 3. Combine
# -----------------------------------

df = pd.concat(
    [phishing_sample, benign_df],
    ignore_index=True
)


# -----------------------------------
# 4. Shuffle
# -----------------------------------

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# -----------------------------------
# 5. Save
# -----------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n========== FINAL DATASET ==========")
print("Total URLs:", len(df))

print("\nClass distribution:")
print(df["label"].value_counts())

print("\nFirst 10 rows:")
print(df.head(10))

print("\nSaved to:", OUTPUT_FILE)