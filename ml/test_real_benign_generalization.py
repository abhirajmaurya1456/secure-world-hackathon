import pandas as pd
import joblib
from urllib.parse import urlparse

from extract_features import extract_features


# ============================================================
# FILES
# ============================================================

DATASET_FILE = "data/processed/real_url_dataset.csv"

RF_MODEL_FILE = "data/model/phishing_model_no_https.pkl"
RAW_MODEL_FILE = "data/model/raw_url_model.pkl"
VECTORIZER_FILE = "data/model/raw_url_vectorizer.pkl"

SAMPLE_SIZE = 500


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATASET_FILE)

# label 0 = benign
benign_df = df[df["label"] == 0].copy()

print("Total benign URLs:", len(benign_df))


# Random sample — NOT used for training/tuning
test_df = benign_df.sample(
    n=SAMPLE_SIZE,
    random_state=2026
).reset_index(drop=True)


# ============================================================
# LOAD MODELS
# ============================================================

rf_model = joblib.load(RF_MODEL_FILE)
raw_model = joblib.load(RAW_MODEL_FILE)
vectorizer = joblib.load(VECTORIZER_FILE)


FEATURE_COLUMNS = [
    "url_entropy",
    "tld_length",
    "hostname_digit_count",
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "dot_count",
    "hyphen_count",
    "slash_count",
    "digit_count",
    "special_char_count",
    "subdomain_count",
    "has_ip",
    "has_port",
    "has_at_symbol",
    "has_punycode",
    "suspicious_keyword_count"
]


# ============================================================
# PREDICTION FUNCTIONS
# ============================================================

def rf_probability(url):

    features = extract_features(url)

    feature_values = {
        column: features[column]
        for column in FEATURE_COLUMNS
    }

    X = pd.DataFrame(
        [[feature_values[column] for column in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )

    return float(
        rf_model.predict_proba(X)[0][1]
    )


def raw_probability(url):

    X = vectorizer.transform([url])

    return float(
        raw_model.predict_proba(X)[0][1]
    )


# ============================================================
# TEST
# ============================================================

results = []

for _, row in test_df.iterrows():

    url = row["url"]

    rf_prob = rf_probability(url)
    raw_prob = raw_probability(url)

    ensemble_prob = (
        0.50 * rf_prob
        + 0.50 * raw_prob
    )

    results.append({
        "url": url,
        "rf_probability": rf_prob,
        "raw_probability": raw_prob,
        "ensemble_probability": ensemble_prob
    })


results_df = pd.DataFrame(results)


# ============================================================
# METRICS
# ============================================================

rf_fp = (results_df["rf_probability"] >= 0.50).sum()
raw_fp = (results_df["raw_probability"] >= 0.50).sum()
ensemble_fp = (results_df["ensemble_probability"] >= 0.50).sum()


print("\n============================================================")
print("REAL BENIGN GENERALIZATION TEST")
print("============================================================")

print(f"Sample size: {SAMPLE_SIZE}")

print("\nFalse positives:")
print(f"RF Model:        {rf_fp}/{SAMPLE_SIZE}")
print(f"Raw URL Model:   {raw_fp}/{SAMPLE_SIZE}")
print(f"50/50 Ensemble:  {ensemble_fp}/{SAMPLE_SIZE}")

print("\nFalse-positive rates:")

print(
    f"RF Model:        {rf_fp / SAMPLE_SIZE * 100:.2f}%"
)

print(
    f"Raw URL Model:   {raw_fp / SAMPLE_SIZE * 100:.2f}%"
)

print(
    f"50/50 Ensemble:  {ensemble_fp / SAMPLE_SIZE * 100:.2f}%"
)


# ============================================================
# MOST PROBLEMATIC URLs
# ============================================================

print("\n============================================================")
print("TOP 20 HIGHEST-RISK BENIGN URLS")
print("============================================================")

top_risk = results_df.sort_values(
    "ensemble_probability",
    ascending=False
).head(20)

for _, row in top_risk.iterrows():

    print(
        f"{row['ensemble_probability'] * 100:6.2f}% | "
        f"RF={row['rf_probability'] * 100:6.2f}% | "
        f"RAW={row['raw_probability'] * 100:6.2f}% | "
        f"{row['url']}"
    )