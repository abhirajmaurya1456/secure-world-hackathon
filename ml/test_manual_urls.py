import pandas as pd
import joblib

from extract_features import extract_features


INPUT_FILE = "data/test/manual_test_urls.csv"
MODEL_FILE = "data/model/phishing_model_no_https.pkl"


# ============================================================
# 1. LOAD TEST URLS
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("Manual test URLs:", len(df))


# ============================================================
# 2. LOAD TRAINED MODEL
# ============================================================

model = joblib.load(MODEL_FILE)

print("Model loaded:", MODEL_FILE)


# ============================================================
# 3. EXTRACT FEATURES
# ============================================================

feature_rows = df["url"].apply(extract_features)

features_df = pd.DataFrame(feature_rows.tolist())


# Remove HTTPS because this model was trained without it.
features_df = features_df.drop(columns=["has_https"])


# Keep exactly the same feature order used during training.
feature_columns = [
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

X = features_df[feature_columns]


# ============================================================
# 4. PREDICT
# ============================================================

predictions = model.predict(X)

probabilities = model.predict_proba(X)


# Class 1 = phishing
phishing_probability = probabilities[:, 1]


df["predicted_label"] = predictions
df["phishing_probability"] = phishing_probability


# ============================================================
# 5. DISPLAY RESULTS
# ============================================================

print("\n========== MANUAL TEST RESULTS ==========")

for _, row in df.iterrows():

    prediction = (
        "PHISHING"
        if row["predicted_label"] == 1
        else "BENIGN"
    )

    print("\nURL:", row["url"])
    print("Expected :", "PHISHING" if row["expected_label"] == 1 else "BENIGN")
    print("Predicted :", prediction)
    print(
        "Phishing probability:",
        round(row["phishing_probability"] * 100, 2),
        "%"
    )


# ============================================================
# 6. OVERALL ACCURACY
# ============================================================

correct = (
    df["expected_label"] == df["predicted_label"]
).sum()

total = len(df)

accuracy = correct / total

print("\n========== MANUAL TEST SUMMARY ==========")

print("Correct:", correct)
print("Total  :", total)
print("Accuracy:", round(accuracy * 100, 2), "%")