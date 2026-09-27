import pandas as pd
import joblib


MODEL_FILE = "data/model/raw_url_model.pkl"
VECTORIZER_FILE = "data/model/raw_url_vectorizer.pkl"

TEST_FILE = "data/test/manual_test_urls.csv"


# ------------------------------------------------------------
# Load model and vectorizer
# ------------------------------------------------------------

model = joblib.load(MODEL_FILE)

vectorizer = joblib.load(VECTORIZER_FILE)


# ------------------------------------------------------------
# Load manual test URLs
# ------------------------------------------------------------

df = pd.read_csv(TEST_FILE)


urls = df["url"].astype(str)

expected = df["expected_label"]


# ------------------------------------------------------------
# Convert raw URLs into TF-IDF features
# ------------------------------------------------------------

X = vectorizer.transform(urls)


# ------------------------------------------------------------
# Predictions
# ------------------------------------------------------------

predictions = model.predict(X)

probabilities = model.predict_proba(X)


# ------------------------------------------------------------
# Display results
# ------------------------------------------------------------

print("\n" + "=" * 80)

print("RAW URL MODEL — MANUAL UNSEEN URL TEST")

print("=" * 80)


correct = 0


for i, url in enumerate(urls):

    prediction = int(predictions[i])

    phishing_probability = float(
        probabilities[i][1]
    )

    expected_label = int(expected.iloc[i])

    predicted_text = (
        "PHISHING"
        if prediction == 1
        else "BENIGN"
    )

    expected_text = (
        "PHISHING"
        if expected_label == 1
        else "BENIGN"
    )

    is_correct = prediction == expected_label

    if is_correct:
        correct += 1

    print("\nURL:", url)

    print("Expected:", expected_text)

    print("Predicted:", predicted_text)

    print(
        "Phishing probability:",
        round(phishing_probability * 100, 2),
        "%"
    )

    print(
        "Correct:",
        is_correct
    )


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

accuracy = correct / len(df) * 100


print("\n" + "=" * 80)

print("MANUAL TEST SUMMARY")

print("=" * 80)

print("Total URLs:", len(df))

print("Correct:", correct)

print("Accuracy:", round(accuracy, 2), "%")

print("=" * 80)