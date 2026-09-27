import pandas as pd
import joblib

from urllib.parse import urlparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ------------------------------------------------------------
# Files
# ------------------------------------------------------------

INPUT_FILE = "data/processed/real_url_dataset.csv"

MODEL_FILE = "data/model/raw_url_model.pkl"

VECTORIZER_FILE = "data/model/raw_url_vectorizer.pkl"


# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Dataset shape:", df.shape)

print("\nClass distribution:")
print(df["label"].value_counts())


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


df["hostname"] = df["url"].apply(get_hostname)


# ------------------------------------------------------------
# Hostname-aware train/test split
# ------------------------------------------------------------

unique_hosts = df["hostname"].drop_duplicates().sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


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
print("Testing rows:", len(test_df))

print("\nTraining class distribution:")
print(train_df["label"].value_counts())

print("\nTesting class distribution:")
print(test_df["label"].value_counts())


# ------------------------------------------------------------
# Raw URLs
# ------------------------------------------------------------

X_train_text = train_df["url"].astype(str)

X_test_text = test_df["url"].astype(str)

y_train = train_df["label"]

y_test = test_df["label"]


# ------------------------------------------------------------
# Character-level TF-IDF
# ------------------------------------------------------------

print("\nTraining character-level TF-IDF...")


vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    min_df=2,
    max_features=200000,
    sublinear_tf=True
)


X_train = vectorizer.fit_transform(X_train_text)

X_test = vectorizer.transform(X_test_text)


print("Training matrix shape:", X_train.shape)

print("Testing matrix shape:", X_test.shape)


# ------------------------------------------------------------
# Logistic Regression
# ------------------------------------------------------------

print("\nTraining Logistic Regression...")


model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)


model.fit(X_train, y_train)


# ------------------------------------------------------------
# Evaluation
# ------------------------------------------------------------

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


print("\n" + "=" * 60)

print("RAW URL MODEL — RESULTS")

print("=" * 60)

print(f"Accuracy : {accuracy:.4f}")

print(f"Precision: {precision:.4f}")

print(f"Recall   : {recall:.4f}")

print(f"F1 Score : {f1:.4f}")

print("\nConfusion Matrix:")

print(cm)


# ------------------------------------------------------------
# Save model and vectorizer
# ------------------------------------------------------------

joblib.dump(
    model,
    MODEL_FILE
)

joblib.dump(
    vectorizer,
    VECTORIZER_FILE
)


print("\nSaved model:")
print(MODEL_FILE)

print("\nSaved vectorizer:")
print(VECTORIZER_FILE)

print("=" * 60)