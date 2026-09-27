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
from sklearn.model_selection import train_test_split
import joblib


INPUT_FILE = "data/processed/real_url_dataset.csv"
FEATURE_FILE = "data/processed/real_features.csv"
MODEL_FILE = "data/model/phishing_model_no_https.pkl"


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("Total URLs:", len(df))


# ============================================================
# 2. EXTRACT HOSTNAME
# ============================================================

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


# ============================================================
# 3. SAME HOSTNAME-AWARE SPLIT AS BASELINE
# ============================================================

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


# ============================================================
# 4. LOAD FEATURES
# ============================================================

features_df = pd.read_csv(FEATURE_FILE)

feature_columns = [
    column
    for column in features_df.columns
    if column not in ["label", "has_https"]
]

X = features_df[feature_columns]
y = features_df["label"]


print("\n========== FEATURES ==========")

print("Removed feature: has_https")
print("Number of features:", len(feature_columns))

print("Features used:")
print(feature_columns)


# ============================================================
# 5. CREATE TRAIN / TEST FEATURE SETS
# ============================================================

train_indices = train_df.index
test_indices = test_df.index

X_train = X.loc[train_indices]
y_train = y.loc[train_indices]

X_test = X.loc[test_indices]
y_test = y.loc[test_indices]


print("\nFeature matrix:")
print("X_train:", X_train.shape)
print("X_test :", X_test.shape)


# ============================================================
# 6. TRAIN RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)


print("\nTraining Random Forest without has_https...")

model.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# 7. PREDICTION
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 8. EVALUATION
# ============================================================

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

cm = confusion_matrix(y_test, y_pred)


print("\n========== MODEL RESULTS — WITHOUT HTTPS ==========")

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


# ============================================================
# 9. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": feature_columns,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)


print("\n========== FEATURE IMPORTANCE ==========")

print(
    importance.to_string(index=False)
)


# ============================================================
# 10. SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_FILE
)

print("\nModel saved to:", MODEL_FILE)