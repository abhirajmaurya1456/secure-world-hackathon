import pandas as pd

from security_engine_v2 import analyze_url


# ============================================================
# TEST FILES
# ============================================================

TEST_FILES = [
    "data/test/manual_test_urls.csv",
    "data/test/real_site_test_urls.csv",
    "data/test/controlled_phishing_urls.csv"
]


# ============================================================
# EVALUATION
# ============================================================

all_results = []

for file_path in TEST_FILES:

    df = pd.read_csv(file_path)

    for _, row in df.iterrows():

        result = analyze_url(row["url"])

        predicted_label = (
            1 if result["verdict"] == "PHISHING"
            else 0
        )

        # SUSPICIOUS is treated as benign for this
        # binary phishing-detection evaluation.
        #
        # We will separately report suspicious results
        # so they are not hidden.

        all_results.append({
            "file": file_path,
            "url": row["url"],
            "test_case": row["test_case"],
            "expected_label": int(row["expected_label"]),
            "predicted_label": predicted_label,
            "verdict": result["verdict"],
            "risk_score": result["risk_score"],
            "rf_probability": result["rf_probability"],
            "raw_probability": result["raw_probability"],
            "known_domain": result["known_domain"]
        })


results = pd.DataFrame(all_results)


# ============================================================
# OVERALL METRICS
# ============================================================

total = len(results)

correct = (
    results["expected_label"]
    == results["predicted_label"]
).sum()

accuracy = correct / total


# False positives:
# expected benign but predicted PHISHING

false_positives = (
    (results["expected_label"] == 0)
    & (results["predicted_label"] == 1)
).sum()


# False negatives:
# expected phishing but predicted non-PHISHING

false_negatives = (
    (results["expected_label"] == 1)
    & (results["predicted_label"] == 0)
).sum()


benign_count = (
    results["expected_label"] == 0
).sum()

phishing_count = (
    results["expected_label"] == 1
).sum()


false_positive_rate = (
    false_positives / benign_count
    if benign_count > 0
    else 0
)


phishing_detection_rate = (
    (phishing_count - false_negatives)
    / phishing_count
    if phishing_count > 0
    else 0
)


# ============================================================
# SUSPICIOUS COUNT
# ============================================================

suspicious_count = (
    results["verdict"] == "SUSPICIOUS"
).sum()


# ============================================================
# PRINT OVERALL RESULTS
# ============================================================

print("\n============================================================")
print("PHISHGUARD SECURITY ENGINE V2 — FULL EVALUATION")
print("============================================================")

print(f"Total test URLs:          {total}")
print(f"Correct predictions:      {correct}")
print(f"Accuracy:                 {accuracy * 100:.2f}%")

print("\nBenign URLs:")
print(f"Count:                    {benign_count}")
print(f"False positives:          {false_positives}")
print(f"False-positive rate:      {false_positive_rate * 100:.2f}%")

print("\nPhishing URLs:")
print(f"Count:                    {phishing_count}")
print(f"False negatives:          {false_negatives}")
print(
    f"Detection rate:           "
    f"{phishing_detection_rate * 100:.2f}%"
)

print("\nVerdict distribution:")
print(results["verdict"].value_counts())


# ============================================================
# RESULTS BY TEST FILE
# ============================================================

print("\n============================================================")
print("RESULTS BY TEST SET")
print("============================================================")

for file_path in TEST_FILES:

    subset = results[
        results["file"] == file_path
    ]

    subset_correct = (
        subset["expected_label"]
        == subset["predicted_label"]
    ).sum()

    subset_accuracy = (
        subset_correct / len(subset)
    )

    print("\n", file_path)
    print(
        f"Correct: {subset_correct}/{len(subset)}"
    )
    print(
        f"Accuracy: {subset_accuracy * 100:.2f}%"
    )


# ============================================================
# FALSE POSITIVES
# ============================================================

print("\n============================================================")
print("FALSE POSITIVES")
print("============================================================")

fp_results = results[
    (results["expected_label"] == 0)
    & (results["predicted_label"] == 1)
]

if len(fp_results) == 0:

    print("No false positives.")

else:

    for _, row in fp_results.iterrows():

        print(
            f"{row['risk_score']:6.2f}% | "
            f"{row['test_case']} | "
            f"{row['url']}"
        )


# ============================================================
# FALSE NEGATIVES
# ============================================================

print("\n============================================================")
print("FALSE NEGATIVES")
print("============================================================")

fn_results = results[
    (results["expected_label"] == 1)
    & (results["predicted_label"] == 0)
]

if len(fn_results) == 0:

    print("No false negatives.")

else:

    for _, row in fn_results.iterrows():

        print(
            f"{row['risk_score']:6.2f}% | "
            f"{row['test_case']} | "
            f"{row['url']}"
        )


# ============================================================
# SUSPICIOUS BENIGN URLs
# ============================================================

print("\n============================================================")
print("BENIGN URLs FLAGGED AS SUSPICIOUS")
print("============================================================")

suspicious_benign = results[
    (results["expected_label"] == 0)
    & (results["verdict"] == "SUSPICIOUS")
]

if len(suspicious_benign) == 0:

    print("None.")

else:

    for _, row in suspicious_benign.iterrows():

        print(
            f"{row['risk_score']:6.2f}% | "
            f"{row['test_case']} | "
            f"{row['url']}"
        )


print("\n============================================================")
print("EVALUATION COMPLETE")
print("============================================================")