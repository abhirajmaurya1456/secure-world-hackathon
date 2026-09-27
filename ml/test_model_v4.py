import pandas as pd
import numpy as np
import joblib

from urllib.parse import urlsplit, parse_qsl

from scipy.sparse import hstack, csr_matrix


MODEL_FILE = "data/model/region_aware_model.pkl"
HOST_VECTOR_FILE = "data/model/v4_host_vectorizer.pkl"
PATH_VECTOR_FILE = "data/model/v4_path_vectorizer.pkl"
QUERY_VECTOR_FILE = "data/model/v4_query_vectorizer.pkl"


model = joblib.load(MODEL_FILE)
host_vectorizer = joblib.load(HOST_VECTOR_FILE)
path_vectorizer = joblib.load(PATH_VECTOR_FILE)
query_vectorizer = joblib.load(QUERY_VECTOR_FILE)


PATH_KEYWORDS = [
    "login", "signin", "sign-in", "verify", "verification",
    "account", "password", "passwd", "credential", "secure",
    "update", "confirm", "authentication", "auth", "bank",
    "payment", "wallet", "recover", "reset"
]

QUERY_KEYWORDS = [
    "login", "signin", "verify", "verification",
    "account", "password", "passwd", "credential",
    "token", "auth", "authentication", "redirect",
    "return", "payment", "wallet"
]


def parse_url(url):
    try:
        parsed = urlsplit(str(url))

        return (
            (parsed.hostname or "").lower(),
            parsed.path or "",
            parsed.query or ""
        )

    except Exception:
        return "", "", ""


def entropy(text):
    if not text:
        return 0.0

    counts = pd.Series(list(text)).value_counts(normalize=True)

    return float(-(counts * np.log2(counts)).sum())


def count_keyword_matches(text, keywords):
    text = text.lower()

    return sum(
        1 for keyword in keywords
        if keyword in text
    )


def path_depth(path):
    if not path or path == "/":
        return 0

    return len([
        part for part in path.split("/")
        if part
    ])


def numeric_path_segments(path):
    segments = [
        part for part in path.split("/")
        if part
    ]

    count = 0

    for segment in segments:
        digits = sum(ch.isdigit() for ch in segment)

        if digits >= 4:
            count += 1

    return count


def long_numeric_path_segments(path):
    segments = [
        part for part in path.split("/")
        if part
    ]

    count = 0

    for segment in segments:

        if len(segment) >= 8:

            digits = sum(ch.isdigit() for ch in segment)

            if digits / len(segment) >= 0.5:
                count += 1

    return count


def get_numeric_features(url):

    hostname, path, query = parse_url(url)

    full_url = str(url)

    query_params = parse_qsl(
        query,
        keep_blank_values=True
    )

    hostname_digits = sum(
        ch.isdigit()
        for ch in hostname
    )

    path_digits = sum(
        ch.isdigit()
        for ch in path
    )

    query_digits = sum(
        ch.isdigit()
        for ch in query
    )

    path_special = sum(
        not ch.isalnum()
        for ch in path
    )

    query_special = sum(
        not ch.isalnum()
        for ch in query
    )

    path_digit_ratio = (
        path_digits / len(path)
        if path
        else 0
    )

    query_digit_ratio = (
        query_digits / len(query)
        if query
        else 0
    )

    path_keywords = count_keyword_matches(
        path,
        PATH_KEYWORDS
    )

    query_keywords = count_keyword_matches(
        query,
        QUERY_KEYWORDS
    )

    return [

        # HOSTNAME
        len(hostname),
        hostname_digits,
        hostname.count("."),
        hostname.count("-"),
        len(hostname.split(".")) - 1,
        int(hostname.startswith("xn--")),
        int("@" in hostname),

        # PATH
        len(path),
        path_depth(path),
        path_digits,
        path_digit_ratio,
        path_special,
        entropy(path),
        numeric_path_segments(path),
        long_numeric_path_segments(path),
        path_keywords,

        # QUERY
        len(query),
        len(query_params),
        query_digits,
        query_digit_ratio,
        query_special,
        entropy(query),
        query_keywords,

        # FULL URL
        len(full_url)
    ]


def predict_url(url):

    hostname, path, query = parse_url(url)

    X_host = host_vectorizer.transform([hostname])
    X_path = path_vectorizer.transform([path])
    X_query = query_vectorizer.transform([query])

    X_numeric = csr_matrix([
        get_numeric_features(url)
    ])

    X = hstack([
        X_host,
        X_path,
        X_query,
        X_numeric
    ]).tocsr()

    probability = float(
        model.predict_proba(X)[0][1]
    )

    prediction = 1 if probability >= 0.5 else 0

    return prediction, probability


# ============================================================
# TEST URLS
# ============================================================

test_urls = [

    # -------------------------
    # NORMAL REAL SITES
    # -------------------------

    (
        "https://www.youtube.com/",
        0,
        "YouTube home"
    ),

    (
        "https://www.youtube.com/watch?v=wheOPSjBPoW&list=RDqInvYYaRdrU&index=27",
        0,
        "YouTube complex video"
    ),

    (
        "https://github.com/",
        0,
        "GitHub home"
    ),

    (
        "https://github.com/user/repository",
        0,
        "GitHub repository"
    ),

    (
        "https://github.com/login",
        0,
        "GitHub login"
    ),

    (
        "https://www.iitrpr.ac.in/",
        0,
        "IIT Ropar home"
    ),

    (
        "https://www.iitrpr.ac.in/tenders",
        0,
        "IIT Ropar tenders"
    ),

    (
        "https://www.amazon.in/b/?_encoding=UTF8&_encoding=UTF8&node=211756350031&ref_=pd_hp_d_r_stg_unk&pd_rd_w=f9gfT&content-id=amzn1.sym.c825e489-6b16-4623-91c6-af6ab2379055&pf_rd_p=c825e489-6b16-4623-91c6-af6ab2379055&pf_rd_r=FCNY13FNAQD726PB9M69&pd_rd_wg=uEZYL&pd_rd_r=cf90236a-62d4-4f9b-b9c6-e7fdcdf66c43",
        0,
        "Amazon complex query"
    ),

    (
        "https://in.pinterest.com/pin/10133167907367690/feedback/?invite_code=dd6c9a51d7cc46f792c6228521810743&sender_id=960111351718809891",
        0,
        "Pinterest complex URL"
    ),

    (
        "https://docs.google.com/presentation/d/e/2PACX-1vSpKXu1td_dnZbKzWX57BfTJWU8c14dsbqMBnK1JcxVITLwPoKdo4URVQUV1x0TzCFvros0R3bCItv/pub?start=false&loop=false&delayms=3000&slide=id.p",
        0,
        "Google Docs presentation"
    ),

    (
        "https://example.com/",
        0,
        "Example domain"
    ),

    # -------------------------
    # PHISHING-LIKE
    # -------------------------

    (
        "https://secure-login-example.com/verify/account",
        1,
        "Fake login domain"
    ),

    (
        "http://example.com/login/verify/password",
        1,
        "Credential path"
    ),

    (
        "http://192.168.1.10/login/verify?password=12345678",
        1,
        "IP + login + password"
    ),

    (
        "https://account-security-update-example.com/verify?id=93847291",
        1,
        "Account update phishing"
    ),

    (
        "https://secure-bank-login-example.com/account/verify",
        1,
        "Bank login phishing"
    ),

    (
        "https://login-verification-example.com/update/password?id=82736491",
        1,
        "Credential theft pattern"
    ),

    (
        "https://example.com/a/b/c/d/e/f/123456789",
        1,
        "Suspicious long numeric path"
    )
]


# ============================================================
# RUN TEST
# ============================================================

print("\n============================================================")
print("PHISHGUARD MODEL 4 — REAL URL TEST")
print("============================================================")

correct = 0

for url, expected, name in test_urls:

    prediction, probability = predict_url(url)

    verdict = (
        "PHISHING"
        if prediction == 1
        else "BENIGN"
    )

    expected_text = (
        "PHISHING"
        if expected == 1
        else "BENIGN"
    )

    is_correct = prediction == expected

    if is_correct:
        correct += 1

    print("\n----------------------------------------")
    print("Test:", name)
    print("URL:", url)
    print("Expected:", expected_text)
    print("Predicted:", verdict)
    print(
        "Phishing Probability:",
        round(probability * 100, 2),
        "%"
    )
    print(
        "Correct:",
        is_correct
    )


print("\n============================================================")
print("MODEL 4 TEST SUMMARY")
print("============================================================")

print(
    f"Correct: {correct}/{len(test_urls)}"
)

print(
    f"Accuracy: {correct / len(test_urls) * 100:.2f}%"
)

print("============================================================")