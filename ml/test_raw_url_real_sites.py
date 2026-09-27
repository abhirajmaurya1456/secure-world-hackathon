import pandas as pd
import joblib


MODEL_FILE = "data/model/raw_url_model.pkl"
VECTORIZER_FILE = "data/model/raw_url_vectorizer.pkl"

TEST_FILE = "data/test/real_site_test_urls.csv"


model = joblib.load(MODEL_FILE)
vectorizer = joblib.load(VECTORIZER_FILE)

df = pd.read_csv(TEST_FILE)

urls = df["url"].astype(str)

X = vectorizer.transform(urls)

predictions = model.predict(X)
probabilities = model.predict_proba(X)


print("\n" + "=" * 80)
print("RAW URL MODEL — REAL-SITE URL STRING TEST")
print("=" * 80)


correct = 0


for i, url in enumerate(urls):

    prediction = int(predictions[i])

    probability = float(probabilities[i][1])

    expected = int(df.iloc[i]["expected_label"])

    predicted_text = (
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

    print("\nURL:", url)
    print("Expected:", expected_text)
    print("Predicted:", predicted_text)
    print(
        "Phishing probability:",
        round(probability * 100, 2),
        "%"
    )
    print("Correct:", is_correct)


print("\n" + "=" * 80)

print("SUMMARY")

print("=" * 80)

print("Total:", len(df))
print("Correct:", correct)
print(
    "Accuracy:",
    round(correct / len(df) * 100, 2),
    "%"
)

print("=" * 80)