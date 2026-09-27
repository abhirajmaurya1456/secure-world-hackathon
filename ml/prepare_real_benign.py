import pandas as pd

LEGITPHISH_FILE = "data/raw/url_features_extracted1.csv"
PHISHING_FILE = "data/processed/phishing_clean.csv"

OUTPUT_FILE = "data/processed/benign_real_clean.csv"


# -----------------------------------
# 1. Load LegitPhish
# -----------------------------------

df = pd.read_csv(LEGITPHISH_FILE)

print("Original LegitPhish rows:", len(df))


# Keep legitimate records only
df = df[df["ClassLabel"] == 1].copy()

print("Legitimate rows:", len(df))


# Keep only the raw URL
df = df[["URL"]].copy()

df = df.rename(columns={"URL": "url"})


# Remove missing URLs
df = df.dropna(subset=["url"])


# Remove duplicate URLs
df = df.drop_duplicates(subset="url")


print("Unique legitimate URLs:", len(df))


# -----------------------------------
# 2. Load our phishing URLs
# -----------------------------------

phishing_df = pd.read_csv(PHISHING_FILE)


# -----------------------------------
# 3. Remove exact URL overlap
# -----------------------------------

phishing_urls = set(
    phishing_df["url"].str.strip().str.lower()
)

df["url_normalized"] = (
    df["url"]
    .str.strip()
    .str.lower()
)

before = len(df)

df = df[
    ~df["url_normalized"].isin(phishing_urls)
].copy()

after = len(df)

print("Legitimate URLs before overlap removal:", before)
print("Exact URL overlaps removed:", before - after)
print("Legitimate URLs after overlap removal:", after)


# Remove temporary column
df = df.drop(columns=["url_normalized"])


# -----------------------------------
# 4. Add benign label
# -----------------------------------

df["label"] = 0


# -----------------------------------
# 5. Save
# -----------------------------------

df = df.reset_index(drop=True)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n========== RESULT ==========")
print("Final legitimate URLs:", len(df))
print("Label distribution:")
print(df["label"].value_counts())

print("\nFirst 10 URLs:")
print(df.head(10))

print("\nSaved to:", OUTPUT_FILE)