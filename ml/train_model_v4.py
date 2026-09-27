import pandas as pd
import numpy as np
import joblib

from urllib.parse import urlsplit, parse_qsl

from scipy.sparse import hstack, csr_matrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


INPUT_FILE = "data/processed/real_url_dataset.csv"

MODEL_FILE = "data/model/region_aware_model.pkl"

HOST_VECTOR_FILE = "data/model/v4_host_vectorizer.pkl"
PATH_VECTOR_FILE = "data/model/v4_path_vectorizer.pkl"
QUERY_VECTOR_FILE = "data/model/v4_query_vectorizer.pkl"


# ============================================================
# URL PARSING
# ============================================================

def parse_url(url):
    try:
        parsed = urlsplit(str(url))

        hostname = parsed.hostname or ""
        hostname = hostname.lower()

        path = parsed.path or ""

        query = parsed.query or ""

        return hostname, path, query

    except Exception:
        return "", "", ""


# ============================================================
# REGION-AWARE NUMERIC FEATURES
# ============================================================

PATH_KEYWORDS = [
    "login",
    "signin",
    "sign-in",
    "verify",
    "verification",
    "account",
    "password",
    "passwd",
    "credential",
    "secure",
    "update",
    "confirm",
    "authentication",
    "auth",
    "bank",
    "payment",
    "wallet",
    "recover",
    "reset",
]


QUERY_KEYWORDS = [
    "login",
    "signin",
    "verify",
    "verification",
    "account",
    "password",
    "passwd",
    "credential",
    "token",
    "auth",
    "authentication",
    "redirect",
    "return",
    "payment",
    "wallet",
]


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

    features = [

        # -------------------------
        # HOSTNAME
        # -------------------------

        len(hostname),

        hostname_digits,

        hostname.count("."),

        hostname.count("-"),

        len(hostname.split(".")) - 1,

        int(hostname.startswith("xn--")),

        int("@" in hostname),

        # -------------------------
        # PATH
        # -------------------------

        len(path),

        path_depth(path),

        path_digits,

        path_digit_ratio,

        path_special,

        entropy(path),

        numeric_path_segments(path),

        long_numeric_path_segments(path),

        path_keywords,

        # -------------------------
        # QUERY
        # -------------------------

        len(query),

        len(query_params),

        query_digits,

        query_digit_ratio,

        query_special,

        entropy(query),

        query_keywords,

        # -------------------------
        # FULL URL
        # -------------------------

        len(full_url),

    ]

    return features


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("============================================================")
print("PHISHGUARD MODEL 4 — REGION-AWARE URL MODEL")
print("============================================================")

print("\nDataset shape:", df.shape)

print("\nClass distribution:")
print(df["label"].value_counts())


# ============================================================
# HOSTNAME-AWARE SPLIT
# ============================================================

df["hostname"] = df["url"].apply(
    lambda url: parse_url(url)[0]
)

unique_hosts = (
    df["hostname"]
    .drop_duplicates()
    .sample(frac=1, random_state=42)
    .reset_index(drop=True)
)

test_size = 0.20

test_host_count = int(
    len(unique_hosts) * test_size
)

test_hosts = set(
    unique_hosts.iloc[:test_host_count]
)

test_mask = df["hostname"].isin(test_hosts)

train_df = df[~test_mask].copy()
test_df = df[test_mask].copy()

print("\nHostname-aware split:")
print("Training rows:", len(train_df))
print("Testing rows :", len(test_df))


# ============================================================
# TEXT REGIONS
# ============================================================

train_host = train_df["url"].apply(
    lambda url: parse_url(url)[0]
)

test_host = test_df["url"].apply(
    lambda url: parse_url(url)[0]
)

train_path = train_df["url"].apply(
    lambda url: parse_url(url)[1]
)

test_path = test_df["url"].apply(
    lambda url: parse_url(url)[1]
)

train_query = train_df["url"].apply(
    lambda url: parse_url(url)[2]
)

test_query = test_df["url"].apply(
    lambda url: parse_url(url)[2]
)


# ============================================================
# HOSTNAME CHARACTER MODEL
# ============================================================

host_vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 5),
    min_df=2,
    max_features=60000,
    sublinear_tf=True
)

X_train_host = host_vectorizer.fit_transform(train_host)

X_test_host = host_vectorizer.transform(test_host)


# ============================================================
# PATH CHARACTER MODEL
# ============================================================

path_vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 5),
    min_df=2,
    max_features=80000,
    sublinear_tf=True
)

X_train_path = path_vectorizer.fit_transform(train_path)

X_test_path = path_vectorizer.transform(test_path)


# ============================================================
# QUERY CHARACTER MODEL
# ============================================================

query_vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 5),
    min_df=2,
    max_features=80000,
    sublinear_tf=True
)

X_train_query = query_vectorizer.fit_transform(train_query)

X_test_query = query_vectorizer.transform(test_query)


# ============================================================
# NUMERIC FEATURES
# ============================================================

X_train_numeric = np.array([
    get_numeric_features(url)
    for url in train_df["url"]
])

X_test_numeric = np.array([
    get_numeric_features(url)
    for url in test_df["url"]
])


X_train_numeric = csr_matrix(X_train_numeric)

X_test_numeric = csr_matrix(X_test_numeric)


# ============================================================
# COMBINE ALL REGIONS
# ============================================================

X_train = hstack([
    X_train_host,
    X_train_path,
    X_train_query,
    X_train_numeric
]).tocsr()


X_test = hstack([
    X_test_host,
    X_test_path,
    X_test_query,
    X_test_numeric
]).tocsr()


print("\nFeature matrices:")

print(
    "Training matrix shape:",
    X_train.shape
)

print(
    "Testing matrix shape:",
    X_test.shape
)


# ============================================================
# MODEL
# ============================================================

y_train = train_df["label"]

y_test = test_df["label"]


model = LogisticRegression(
    max_iter=1500,
    class_weight="balanced",
    random_state=42
)


print("\nTraining Model 4...")

model.fit(
    X_train,
    y_train
)


# ============================================================
# EVALUATION
# ============================================================

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)

cm = confusion_matrix(
    y_test,
    predictions
)


print("\n============================================================")
print("MODEL 4 — RESULTS")
print("============================================================")

print(
    f"Accuracy : {accuracy:.4f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall   : {recall:.4f}"
)

print(
    f"F1 Score : {f1:.4f}"
)

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# SAVE
# ============================================================

joblib.dump(
    model,
    MODEL_FILE
)

joblib.dump(
    host_vectorizer,
    HOST_VECTOR_FILE
)

joblib.dump(
    path_vectorizer,
    PATH_VECTOR_FILE
)

joblib.dump(
    query_vectorizer,
    QUERY_VECTOR_FILE
)


print("\nSaved:")

print(MODEL_FILE)
print(HOST_VECTOR_FILE)
print(PATH_VECTOR_FILE)
print(QUERY_VECTOR_FILE)

print("\n============================================================")
print("MODEL 4 TRAINING COMPLETE")
print("============================================================")