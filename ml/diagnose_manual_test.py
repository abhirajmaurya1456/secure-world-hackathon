import pandas as pd
from extract_features import extract_features


INPUT_FILE = "data/test/manual_test_urls.csv"


df = pd.read_csv(INPUT_FILE)

feature_rows = df["url"].apply(extract_features)

features_df = pd.DataFrame(feature_rows.tolist())

features_df["url"] = df["url"]
features_df["expected_label"] = df["expected_label"]

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
    "has_https",
    "has_port",
    "has_at_symbol",
    "has_punycode",
    "suspicious_keyword_count"
]

print("\n========== MANUAL URL FEATURES ==========\n")

for _, row in features_df.iterrows():

    print("URL:", row["url"])
    print(
        "Expected:",
        "PHISHING" if row["expected_label"] == 1 else "BENIGN"
    )

    for feature in feature_columns:
        print(
            f"{feature:25s}: {row[feature]}"
        )

    print("-" * 70)