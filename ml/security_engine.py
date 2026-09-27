import re
import joblib
from urllib.parse import urlparse
import pandas as pd
from extract_features import extract_features


MODEL_FILE = "data/model/phishing_model_no_https.pkl"


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


TRUSTED_DOMAINS = {
    "google.com",
    "stackoverflow.com",
    "github.com",
    "wikipedia.org",
    "microsoft.com"
}

def is_trusted_domain(hostname):

    hostname = hostname.lower().strip(".")

    for domain in TRUSTED_DOMAINS:

        if hostname == domain:
            return True

        if hostname.endswith("." + domain):
            return True

    return False

# ------------------------------------------------------------
# Load model once
# ------------------------------------------------------------

model = joblib.load(MODEL_FILE)


# ------------------------------------------------------------
# Extract hostname
# ------------------------------------------------------------

def get_hostname(url):

    try:
        hostname = urlparse(url).hostname

        if hostname:
            return hostname.lower()

        return ""

    except Exception:
        return ""


# ------------------------------------------------------------
# Rule-based security checks
# ------------------------------------------------------------

def security_rules(url, features):

    reasons = []
    rule_score = 0

    hostname = get_hostname(url)

    # IP address instead of domain
    if features["has_ip"] == 1:
        reasons.append(
            "The URL uses an IP address instead of a normal domain name."
        )
        rule_score += 25

    # @ symbol
    if features["has_at_symbol"] == 1:
        reasons.append(
            "The URL contains an @ symbol, which can be used to obscure the destination."
        )
        rule_score += 25

    # Punycode
    if features["has_punycode"] == 1:
        reasons.append(
            "The hostname contains punycode, which can be associated with look-alike domains."
        )
        rule_score += 20

    # Suspicious keywords
    keyword_count = features["suspicious_keyword_count"]

    if keyword_count >= 3:
        reasons.append(
            "The URL contains multiple security-sensitive keywords such as login, verify, account or password."
        )
        rule_score += 20

    elif keyword_count >= 1:
        reasons.append(
            "The URL contains a security-sensitive keyword."
        )
        rule_score += 8

    # Very long URL
    if features["url_length"] >= 75:
        reasons.append(
            "The URL is unusually long."
        )
        rule_score += 10

    # Deep path
    if features["path_length"] >= 30:
        reasons.append(
            "The URL contains an unusually long path."
        )
        rule_score += 10

    # Many path segments
    if features["slash_count"] >= 8:
        reasons.append(
            "The URL contains many path segments."
        )
        rule_score += 10

    # Large number of digits
    if features["digit_count"] >= 8:
        reasons.append(
            "The URL contains an unusually high number of digits."
        )
        rule_score += 10

    # Suspicious port
    if features["has_port"] == 1:
        reasons.append(
            "The URL specifies a non-standard port."
        )
        rule_score += 15

    return rule_score, reasons


# ------------------------------------------------------------
# Main analysis function
# ------------------------------------------------------------

def analyze_url(url):

    # Feature extraction
    feature_dict = extract_features(url)

    feature_values = {
        column: feature_dict[column]
        for column in FEATURE_COLUMNS
    }

    # Convert to model input
    X = pd.DataFrame(
        [[feature_values[column] for column in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )

    # ML prediction
    prediction = int(model.predict(X)[0])

    probabilities = model.predict_proba(X)[0]

    phishing_probability = float(probabilities[1])

    # Rule-based analysis
    rule_score, reasons = security_rules(
        url,
        feature_dict
    )

    # ML score: 0-100
    ml_score = phishing_probability * 100

    # Combine ML and rule evidence
    combined_score = (
        0.70 * ml_score +
        0.30 * min(rule_score, 100)
    )

    combined_score = round(
        min(combined_score, 100),
        2
    )

    hostname = get_hostname(url)
    trusted_domain = is_trusted_domain(hostname)

    if trusted_domain and combined_score < 85:
        combined_score = min(combined_score, 25)

        reasons = [
        "Hostname matches a domain in the prototype's trusted-domain list."
        ]


    # Determine risk level
    if combined_score >= 70:

        risk_level = "HIGH"
        verdict = "PHISHING"

    elif combined_score >= 40:

        risk_level = "MEDIUM"
        verdict = "SUSPICIOUS"

    else:

        risk_level = "LOW"
        verdict = "SAFE"

    # If ML predicts phishing but has no explanation,
    # provide a generic explanation.
    if prediction == 1 and not reasons:

        reasons.append(
            "The machine-learning model detected URL characteristics associated with phishing."
        )

    return {
        "url": url,
        "verdict": verdict,
        "risk_level": risk_level,
        "risk_score": combined_score,
        "phishing_probability": round(
            phishing_probability * 100,
            2
        ),
        "reasons": reasons,
        "features": feature_values,
        "trusted_domain": trusted_domain,
    }


# ------------------------------------------------------------
# Local testing
# ------------------------------------------------------------

if __name__ == "__main__":

    test_urls = [
        "https://www.google.com/",
        "https://github.com/login",
        "https://secure-login-example.com/verify/account",
        "http://192.168.1.10/login/verify"
    ]

    for url in test_urls:

        result = analyze_url(url)

        print("\n" + "=" * 70)

        print("URL:", result["url"])
        print("Verdict:", result["verdict"])
        print("Risk level:", result["risk_level"])
        print("Risk score:", result["risk_score"])
        print(
            "Phishing probability:",
            result["phishing_probability"],
            "%"
        )

        print("\nReasons:")

        for reason in result["reasons"]:
            print("-", reason)