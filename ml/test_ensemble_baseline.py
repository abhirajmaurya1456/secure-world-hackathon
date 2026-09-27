import pandas as pd
import joblib
from urllib.parse import urlparse

from extract_features import extract_features


# ============================================================
# FILES
# ============================================================

RF_MODEL_FILE = "data/model/phishing_model_no_https.pkl"
RAW_MODEL_FILE = "data/model/raw_url_model.pkl"
VECTORIZER_FILE = "data/model/raw_url_vectorizer.pkl"
TRANCO_FILE = "data/raw/tranco_top1m.csv"

MANUAL_TEST_FILE = "data/test/manual_test_urls.csv"
REAL_SITE_TEST_FILE = "data/test/real_site_test_urls.csv"
CONTROLLED_PHISHING_FILE = "data/test/controlled_phishing_urls.csv"

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
# LOAD TRANCO DOMAINS
# ============================================================

tranco_df = pd.read_csv(
    TRANCO_FILE,
    header=None,
    names=["rank", "domain"]
)

POPULAR_DOMAINS = set(
    tranco_df["domain"]
    .astype(str)
    .str.lower()
    .str.strip()
)


# ============================================================
# DOMAIN HELPERS
# ============================================================

def get_hostname(url):
    try:
        hostname = urlparse(url).hostname

        if hostname:
            return hostname.lower().strip(".")

        return ""

    except Exception:
        return ""


def is_known_domain(hostname):
    """
    Check whether the hostname itself or one of its parent domains
    exists in the Tranco popularity list.
    """

    if not hostname:
        return False

    parts = hostname.split(".")

    for i in range(len(parts) - 1):
        candidate = ".".join(parts[i:])

        if candidate in POPULAR_DOMAINS:
            return True

    return False


# ============================================================
# MODEL PREDICTIONS
# ============================================================

def get_rf_probability(url):
    features = extract_features(url)

    feature_values = {
        column: features[column]
        for column in FEATURE_COLUMNS
    }

    X = pd.DataFrame(
        [[feature_values[column] for column in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )

    probability = rf_model.predict_proba(X)[0][1]

    return float(probability)


def get_raw_probability(url):
    X = vectorizer.transform([url])

    probability = raw_model.predict_proba(X)[0][1]

    return float(probability)


# ============================================================
# ENSEMBLE
# ============================================================

def analyze_url(url):

    hostname = get_hostname(url)

    rf_probability = get_rf_probability(url)

    raw_probability = get_raw_probability(url)

    known_domain = is_known_domain(hostname)

    # Initial equal-weight ensemble.
    ensemble_probability = (
        0.50 * rf_probability
        + 0.50 * raw_probability
    )

    # Known/popular domain is context, NOT proof of safety.
    #
    # Therefore we only reduce the score when BOTH models
    # disagree strongly with the phishing hypothesis.
    #
    # We do not automatically mark a Tranco domain as safe.

    if known_domain and ensemble_probability < 0.50:
        ensemble_probability *= 0.70

    risk_score = round(ensemble_probability * 100, 2)

    if risk_score >= 70:
        verdict = "PHISHING"
    elif risk_score >= 40:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    return {
        "url": url,
        "hostname": hostname,
        "rf_probability": round(rf_probability * 100, 2),
        "raw_probability": round(raw_probability * 100, 2),
        "ensemble_probability": round(ensemble_probability * 100, 2),
        "risk_score": risk_score,
        "known_domain": known_domain,
        "verdict": verdict
    }


# ============================================================
# TEST FUNCTION
# ============================================================

def run_test(file_path):

    df = pd.read_csv(file_path)

    results = []

    for _, row in df.iterrows():

        result = analyze_url(row["url"])

        result["expected_label"] = row["expected_label"]
        result["test_case"] = row["test_case"]

        results.append(result)

    results_df = pd.DataFrame(results)

    print("\n============================================================")
    print("ENSEMBLE TEST")
    print("============================================================")
    print(f"File: {file_path}")

    print("\nResults:")

    print(
        results_df[
            [
                "test_case",
                "verdict",
                "risk_score",
                "rf_probability",
                "raw_probability",
                "known_domain",
                "expected_label"
            ]
        ].to_string(index=False)
    )

    correct = 0

    for _, row in results_df.iterrows():

        predicted_label = 1 if row["verdict"] == "PHISHING" else 0

        if predicted_label == row["expected_label"]:
            correct += 1

    accuracy = correct / len(results_df)

    print("\n------------------------------------------------------------")
    print(f"Correct: {correct}/{len(results_df)}")
    print(f"Accuracy: {accuracy * 100:.2f}%")
    print("------------------------------------------------------------")

    return results_df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("Tranco domains loaded:", len(POPULAR_DOMAINS))

    manual_results = run_test(MANUAL_TEST_FILE)

    real_site_results = run_test(REAL_SITE_TEST_FILE)

    controlled_results = run_test(CONTROLLED_PHISHING_FILE)