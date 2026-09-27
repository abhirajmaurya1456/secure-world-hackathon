import pandas as pd
from urllib.parse import urlparse

PHISHING_FILE = "data/processed/phishing_clean.csv"
TRANCO_FILE = "data/raw/tranco_top1m.csv"
OUTPUT_FILE = "data/processed/benign_clean.csv"

# -----------------------------
# 1. Load phishing URLs
# -----------------------------
phishing_df = pd.read_csv(PHISHING_FILE)

print("Phishing URLs:", len(phishing_df))


# -----------------------------
# 2. Extract domains from phishing URLs
# -----------------------------
def extract_domain(url):
    try:
        return urlparse(url).netloc.lower().split(":")[0]
    except Exception:
        return ""


phishing_domains = set(
    phishing_df["url"]
    .map(extract_domain)
)

phishing_domains.discard("")

print("Unique phishing domains:", len(phishing_domains))


# -----------------------------
# 3. Load Tranco
# -----------------------------
tranco_df = pd.read_csv(
    TRANCO_FILE,
    header=None,
    names=["rank", "domain"]
)

print("Tranco domains:", len(tranco_df))


# -----------------------------
# 4. Clean domain column
# -----------------------------
tranco_df["domain"] = (
    tranco_df["domain"]
    .astype(str)
    .str.strip()
    .str.lower()
)

tranco_df = tranco_df.drop_duplicates(subset="domain")


# -----------------------------
# 5. Remove domains appearing
#    in phishing dataset
# -----------------------------
before = len(tranco_df)

tranco_df = tranco_df[
    ~tranco_df["domain"].isin(phishing_domains)
].copy()

after = len(tranco_df)

print("Tranco domains before overlap removal:", before)
print("Tranco domains after overlap removal:", after)
print("Potential overlaps removed:", before - after)


# -----------------------------
# 6. Select benign sample
# -----------------------------
BENIGN_COUNT = 77321

if len(tranco_df) < BENIGN_COUNT:
    raise ValueError("Not enough benign domains available.")

benign_df = tranco_df.head(BENIGN_COUNT).copy()


# -----------------------------
# 7. Convert domains to URLs
# -----------------------------
benign_df["url"] = "https://" + benign_df["domain"] + "/"

# Keep only required columns
benign_df = benign_df[["url"]].copy()

# Add benign label
benign_df["label"] = 0

# Reset index
benign_df = benign_df.reset_index(drop=True)


# -----------------------------
# 8. Save
# -----------------------------
benign_df.to_csv(OUTPUT_FILE, index=False)

print("\n========== RESULT ==========")
print("Benign URLs:", len(benign_df))
print("\nClass distribution:")
print(benign_df["label"].value_counts())

print("\nFirst 10 rows:")
print(benign_df.head(10))

print("\nSaved to:", OUTPUT_FILE)