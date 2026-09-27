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


# ============================================================
# LOAD MODELS
# ============================================================

rf_model = joblib.load(RF_MODEL_FILE)
raw_model = joblib.load(RAW_MODEL_FILE)
vectorizer = joblib.load(VECTORIZER_FILE)


# ============================================================
# RF FEATURE COLUMNS
# ============================================================

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
# LOAD TRANCO
# ============================================================

tranco_df = pd.read_csv(
    TRANCO_FILE,
    header=None,
    names=["rank", "domain"]
)

KNOWN_DOMAINS = set(
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

    if not hostname:
        return False

    parts = hostname.split(".")

    for i in range(len(parts) - 1):

        candidate = ".".join(parts[i:])

        if candidate in KNOWN_DOMAINS:
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

    return float(
        rf_model.predict_proba(X)[0][1]
    )


def get_raw_probability(url):

    X = vectorizer.transform([url])

    return float(
        raw_model.predict_proba(X)[0][1]
    )


def get_url_region_features(url):
    """
    Extract security-relevant features separately from
    hostname, path, and query.
    """
    from urllib.parse import urlsplit

    parsed = urlsplit(url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    path_parts = [part for part in path.split("/") if part]

    path_digit_count = sum(ch.isdigit() for ch in path)
    query_digit_count = sum(ch.isdigit() for ch in query)

    path_digit_ratio = (
        path_digit_count / len(path)
        if path else 0.0
    )

    query_digit_ratio = (
        query_digit_count / len(query)
        if query else 0.0
    )

    numeric_path_segments = sum(
        1 for part in path_parts
        if sum(ch.isdigit() for ch in part) >= 4
    )

    security_keywords = [
        "login",
        "signin",
        "verify",
        "verification",
        "password",
        "credential",
        "account",
        "secure",
        "update",
        "confirm",
        "wallet",
        "payment",
        "bank",
        "unlock",
    ]

    path_lower = path.lower()
    query_lower = query.lower()

    path_keyword_count = sum(
        keyword in path_lower
        for keyword in security_keywords
    )

    query_keyword_count = sum(
        keyword in query_lower
        for keyword in security_keywords
    )

    return {
        "path_depth": len(path_parts),
        "path_digit_ratio": path_digit_ratio,
        "numeric_path_segments": numeric_path_segments,
        "query_param_count": (
            len(query.split("&")) if query else 0
        ),
        "query_digit_ratio": query_digit_ratio,
        "path_keyword_count": path_keyword_count,
        "query_keyword_count": query_keyword_count,
        "path_length": len(path),
        "query_length": len(query),
    }

# ============================================================
# SECURITY INDICATORS
# ============================================================

def get_security_indicators(url):

    features = extract_features(url)

    indicators = []

    if features["has_ip"] == 1:
        indicators.append(
            "The URL uses an IP address instead of a normal domain."
        )

    if features["has_at_symbol"] == 1:
        indicators.append(
            "The URL contains an @ symbol that can obscure the destination."
        )

    if features["has_punycode"] == 1:
        indicators.append(
            "The hostname contains punycode, which can be associated with look-alike domains."
        )

    if features["has_port"] == 1:
        indicators.append(
            "The URL specifies a non-standard port."
        )

    if features["suspicious_keyword_count"] >= 3:
        indicators.append(
            "The URL contains multiple security-sensitive keywords."
        )

    elif features["suspicious_keyword_count"] >= 1:
        indicators.append(
            "The URL contains a security-sensitive keyword."
        )

    if features["digit_count"] >= 8:
        indicators.append(
            "The URL contains an unusually high number of digits."
        )

    if features["url_length"] >= 100:
        indicators.append(
            "The URL is unusually long."
        )

    return features, indicators


# ============================================================
# SECURITY ENGINE V2
# ============================================================

def analyze_url(url):

    hostname = get_hostname(url)

    rf_probability = get_rf_probability(url)

    raw_probability = get_raw_probability(url)

    features, indicators = get_security_indicators(url)

    region = get_url_region_features(url)

    path_depth = region["path_depth"]
    path_digit_ratio = region["path_digit_ratio"]
    numeric_path_segments = region["numeric_path_segments"]
    query_param_count = region["query_param_count"]
    query_digit_ratio = region["query_digit_ratio"]
    path_keyword_count = region["path_keyword_count"]
    query_keyword_count = region["query_keyword_count"]

    known_domain = is_known_domain(hostname)

    # --------------------------------------------------------
    # Strong security indicators
    # --------------------------------------------------------

    strong_indicators = 0

    if features["has_ip"] == 1:
        strong_indicators += 1

    if features["has_at_symbol"] == 1:
        strong_indicators += 1

    if features["has_punycode"] == 1:
        strong_indicators += 1

    if features["has_port"] == 1:
        strong_indicators += 1

    if features["suspicious_keyword_count"] >= 3:
        strong_indicators += 1

    # --------------------------------------------------------
    # Initial ensemble
    # --------------------------------------------------------

    ensemble_probability = (
        0.50 * rf_probability
        + 0.50 * raw_probability
    )

    reasons = list(indicators)

    # --------------------------------------------------------
    # REGION-AWARE URL ANALYSIS
    # --------------------------------------------------------

    # Query-string complexity is common on legitimate websites.
    # IDs, tracking values, UUIDs and application parameters
    # should therefore have weak influence on phishing risk.

    query_complexity = (
        query_param_count >= 3
        or query_digit_ratio >= 0.15
        or region["query_length"] >= 80
    )

    # Deep/numeric path structures are stronger evidence because
    # suspicious URLs often encode actions/resources in the path.

    suspicious_path_structure = (
        path_depth >= 4
        and (
            numeric_path_segments >= 1
            or path_digit_ratio >= 0.20
        )
    )

    # Security-sensitive words in the path.

    path_has_security_keyword = (
        path_keyword_count >= 1
    )

    # Multiple security-sensitive query keywords are stronger
    # than ordinary query complexity.

    strong_query_semantics = (
        query_keyword_count >= 2
    )

    # --------------------------------------------------------
    # Query complexity handling
    # --------------------------------------------------------

    # Do NOT penalize a URL simply because it has a long,
    # parameter-heavy query string.

    if (
        query_complexity
        and not strong_query_semantics
        and not suspicious_path_structure
        and strong_indicators == 0
    ):

        ensemble_probability *= 0.80

        reasons.append(
            "Most URL complexity is concentrated in query parameters, "
            "which are commonly used for IDs, tracking, and legitimate "
            "application data."
        )

    # --------------------------------------------------------
    # Suspicious path structure
    # --------------------------------------------------------

    if suspicious_path_structure:

        ensemble_probability = min(
            1.0,
            ensemble_probability + 0.12
        )

        reasons.append(
            "The URL contains a deep path with numeric segments, "
            "which increases phishing risk."
        )

    # --------------------------------------------------------
    # Security-sensitive path
    # --------------------------------------------------------

    if path_has_security_keyword:

        # On a known domain, a single word such as /login is
        # common and should not automatically increase risk.

        if known_domain and path_depth <= 2 and strong_indicators == 0:

            reasons.append(
                "The URL contains a security-sensitive path, "
                "but the domain is known and the path structure "
                "does not show additional strong phishing indicators."
            )

        else:

            ensemble_probability = min(
                1.0,
                ensemble_probability + 0.15
            )

            reasons.append(
                "The URL path contains security-sensitive actions such as "
                "login, verification, password, or account operations."
            )

    # --------------------------------------------------------
    # Security-sensitive query parameters
    # --------------------------------------------------------

    if strong_query_semantics:

        ensemble_probability = min(
            1.0,
            ensemble_probability + 0.10
        )

        reasons.append(
            "The query parameters contain multiple security-sensitive "
            "keywords."
        )

    # --------------------------------------------------------
    # Known-domain contextual adjustment
    # --------------------------------------------------------

    if known_domain and strong_indicators == 0:

        # Known domains are contextual evidence, NOT an automatic
        # safe-list. However, high ML risk on a known domain can
        # often be explained by legitimate URL complexity.

        if ensemble_probability >= 0.70:

            ensemble_probability *= 0.35

            reasons.append(
                "The domain is present in the known-domain list and "
                "no strong phishing indicators were detected; high "
                "URL-model risk may be caused by legitimate URL complexity."
            )

        elif ensemble_probability >= 0.40:

            ensemble_probability *= 0.50

            reasons.append(
                "The domain is present in the known-domain list and "
                "no strong phishing indicators were detected."
            )

    # --------------------------------------------------------
    # Strong evidence override
    # --------------------------------------------------------

    # Strong indicators should not be neutralized simply because
    # the domain is known.

    if strong_indicators >= 2:

        ensemble_probability = max(
            ensemble_probability,
            0.85
        )

    elif strong_indicators == 1 and not known_domain:

        ensemble_probability = max(
            ensemble_probability,
            0.70
        )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    risk_score = round(
        min(ensemble_probability * 100, 100),
        2
    )

    # --------------------------------------------------------
    # Verdict
    # --------------------------------------------------------

    if risk_score >= 70:

        verdict = "PHISHING"
        risk_level = "HIGH"

    elif risk_score >= 40:

        verdict = "SUSPICIOUS"
        risk_level = "MEDIUM"

    else:

        verdict = "SAFE"
        risk_level = "LOW"

    # --------------------------------------------------------
    # Default explanations
    # --------------------------------------------------------

    if not reasons:

        if known_domain:

            reasons.append(
                "No strong URL-level phishing indicators were detected."
            )

        else:

            reasons.append(
                "The machine-learning models did not detect strong "
                "phishing evidence."
            )

    return {

        "url": url,

        "hostname": hostname,

        "verdict": verdict,

        "risk_level": risk_level,

        "risk_score": risk_score,

        "rf_probability": round(
            rf_probability * 100,
            2
        ),

        "raw_probability": round(
            raw_probability * 100,
            2
        ),

        "known_domain": known_domain,

        "strong_indicators": strong_indicators,

        "reasons": reasons,

        "features": features
    }


# ============================================================
# QUICK MANUAL TEST
# ============================================================

if __name__ == "__main__":

    test_urls = [

        "https://www.google.com/",

        "https://github.com/",

        "https://github.com/login",

        "https://www.youtube.com/",

        "https://www.iitrpr.ac.in/",

        "https://www.iitrpr.ac.in/tenders",

        "https://example.com/",

        "https://secure-login-example.com/verify/account",

        "http://192.168.1.10/login/verify?password=12345678"

    ]

    print("\n============================================================")
    print("PHISHGUARD SECURITY ENGINE V2")
    print("============================================================")

    for url in test_urls:

        result = analyze_url(url)

        print("\nURL:", url)
        print("Verdict:", result["verdict"])
        print("Risk Level:", result["risk_level"])
        print("Risk Score:", result["risk_score"])
        print("RF Probability:", result["rf_probability"], "%")
        print("Raw Probability:", result["raw_probability"], "%")
        print("Known Domain:", result["known_domain"])
        print("Strong Indicators:", result["strong_indicators"])

        print("Reasons:")

        for reason in result["reasons"]:
            print(" -", reason)