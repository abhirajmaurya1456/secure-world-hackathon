import re
import pandas as pd
from urllib.parse import urlparse
import math
from collections import Counter

INPUT_FILE = "data/processed/real_url_dataset.csv"
OUTPUT_FILE = "data/processed/real_features.csv"


SUSPICIOUS_KEYWORDS = [
    "login",
    "signin",
    "verify",
    "verification",
    "account",
    "secure",
    "update",
    "password",
    "credential",
    "authenticate",
    "bank",
    "confirm",
    "wallet",
]

def calculate_entropy(text):
    if not text:
        return 0.0

    counts = Counter(text)
    length = len(text)

    entropy = 0.0

    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy

def extract_features(url):
    parsed = urlparse(url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    hostname_lower = hostname.lower()
    # Extract TLD
    hostname_parts = hostname_lower.split(".")

    if len(hostname_parts) >= 2:
        tld = hostname_parts[-1]
    else:
        tld = ""

    tld_length = len(tld)

    # Count digits only inside hostname
    hostname_digit_count = sum(
        char.isdigit() for char in hostname
    )

    hostname_parts = hostname_lower.split(".")
    subdomain_count = max(len(hostname_parts) - 2, 0)

    # IPv4 address detection
    has_ip = int(
        bool(
            re.fullmatch(
                r"(?:\d{1,3}\.){3}\d{1,3}",
                hostname_lower
            )
        )
    )

    # Safely check for explicit port
    try:
        has_port = int(parsed.port is not None)
    except ValueError:
        has_port = 1

    url_lower = url.lower()

    suspicious_keyword_count = sum(
        keyword in url_lower
        for keyword in SUSPICIOUS_KEYWORDS
    )

    special_char_count = len(
        re.findall(r"[^a-zA-Z0-9]", url)
    )

    return {
        "url_entropy": calculate_entropy(url),
        "tld_length": tld_length,
        "hostname_digit_count": hostname_digit_count,
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),

        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "slash_count": url.count("/"),
        "digit_count": sum(char.isdigit() for char in url),

        "special_char_count": special_char_count,

        "subdomain_count": subdomain_count,

        "has_ip": has_ip,
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_port": has_port,
        "has_at_symbol": int("@" in url),
        "has_punycode": int("xn--" in hostname_lower),

        "suspicious_keyword_count": suspicious_keyword_count,
    }

def build_feature_dataset():

    df = pd.read_csv(INPUT_FILE)

    print("Input rows:", len(df))

    feature_rows = df["url"].apply(extract_features)

    features_df = pd.DataFrame(feature_rows.tolist())

    features_df["label"] = df["label"].values

    features_df.to_csv(OUTPUT_FILE, index=False)

    print("\nFeature dataset shape:", features_df.shape)
    print("\nFeatures:")
    print(features_df.columns.tolist())

    print("\nClass distribution:")
    print(features_df["label"].value_counts())

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    build_feature_dataset()