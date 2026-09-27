import pandas as pd

from urllib.parse import urlparse

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

import joblib


INPUT_FILE = "data/processed/real_url_dataset.csv"
MODEL_FILE = "data/model/phishing_model.pkl"


# ==========================================
# 1. Load dataset
# ==========================================

df = pd.read_csv(INPUT_FILE)

print("Total URLs:", len(df))


# ==========================================
# 2. Extract hostname for domain-aware split
# ==========================================

def extract_hostname(url):
    try:
        hostname = urlparse(url).hostname

        if hostname:
            return hostname.lower()

        return ""

    except Exception:
        return ""


df["hostname"] = df["url"].apply(extract_hostname)

print("Unique hostnames:", df["hostname"].nunique())


# ==========================================
# 3. Create domain-level train/test split
# ==========================================

from sklearn.model_selection import train_test_split

unique_hosts = df["hostname"].unique()

train_hosts, test_hosts = train_test_split(
    unique_hosts,
    test_size=0.20,
    random_state=42
)

train_df = df[df["hostname"].isin(train_hosts)].copy()
test_df = df[df["hostname"].isin(test_hosts)].copy()


print("\n========== SPLIT ==========")
print("Training URLs:", len(train_df))
print("Testing URLs:", len(test_df))

print("\nTraining class distribution:")
print(train_df["label"].value_counts())

print("\nTesting class distribution:")
print(test_df["label"].value_counts())


# ==========================================
# 4. Load precomputed features
# ==========================================

features_df = pd.read_csv(
    "data/processed/real_features.csv"
)


# IMPORTANT:
# real_features.csv and real_url_dataset.csv
# have the same row order.

feature_columns = [
    column
    for column in features_df.columns
    if column != "label"
]

X = features_df[feature_columns]
y = features_df["label"]


# ==========================================
# 5. Use same train/test indices
# ==========================================

train_indices = train_df.index
test_indices = test_df.index

X_train = X.loc[train_indices]
y_train = y.loc[train_indices]

X_test = X.loc[test_indices]
y_test = y.loc[test_indices]


print("\nFeature matrix:")
print("X_train:", X_train.shape)
print("X_test :", X_test.shape)


# ==========================================
# 6. Train Random Forest
# ==========================================

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

print("\nTraining Random Forest...")

model.fit(X_train, y_train)

print("Training complete.")


# ==========================================
# 7. Predictions
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# 8. Evaluation
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

cm = confusion_matrix(
    y_test,
    y_pred
)


print("\n========== MODEL RESULTS ==========")

print("Accuracy :", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall   :", round(recall, 4))
print("F1 Score :", round(f1, 4))

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Benign", "Phishing"],
        zero_division=0
    )
)


# ==========================================
# 9. Feature importance
# ==========================================

importance = pd.DataFrame({
    "feature": feature_columns,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\n========== FEATURE IMPORTANCE ==========")
print(importance.to_string(index=False))


# ==========================================
# 10. Save model
# ==========================================

joblib.dump(
    model,
    MODEL_FILE
)

print("\nModel saved to:", MODEL_FILE)