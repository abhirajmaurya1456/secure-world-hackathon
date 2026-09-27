import sys
from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT / "ml"))

from security_engine_v2 import analyze_url


DEMO_FILE = PROJECT_ROOT / "data" / "test" / "demo_urls.csv"


# ------------------------------------------------------------
# Load demo dataset
# ------------------------------------------------------------

df = pd.read_csv(DEMO_FILE)


print()
print("=" * 90)
print("PHISHGUARD — LIVE DEMO TEST")
print("=" * 90)

print(f"Demo URLs: {len(df)}")
print()


results = []


# ------------------------------------------------------------
# Analyze each URL
# ------------------------------------------------------------

for _, row in df.iterrows():

    url = row["url"]
    scenario = row["scenario"]
    expected = row["expected_verdict"]

    result = analyze_url(url)

    actual = result["verdict"]
    risk_score = result["risk_score"]

    # STRESS_CASE means we intentionally do not require
    # the current engine to classify it as phishing.
    if expected == "STRESS_CASE":
        status = "STRESS"
    else:
        status = "PASS" if actual == expected else "FAIL"

    results.append({
        "scenario": scenario,
        "expected": expected,
        "actual": actual,
        "risk_score": risk_score,
        "status": status
    })


# ------------------------------------------------------------
# Display results
# ------------------------------------------------------------

print(
    f"{'SCENARIO':45} "
    f"{'EXPECTED':12} "
    f"{'ACTUAL':12} "
    f"{'RISK':8} "
    f"{'STATUS'}"
)

print("-" * 90)


for item in results:

    scenario = item["scenario"][:43]

    print(
        f"{scenario:45} "
        f"{item['expected']:12} "
        f"{item['actual']:12} "
        f"{item['risk_score']:7.2f} "
        f"{item['status']}"
    )


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

normal_results = [
    item for item in results
    if item["status"] != "STRESS"
]

passed = sum(
    item["status"] == "PASS"
    for item in normal_results
)

failed = sum(
    item["status"] == "FAIL"
    for item in normal_results
)

stress_cases = sum(
    item["status"] == "STRESS"
    for item in results
)


print()
print("=" * 90)
print("DEMO SUMMARY")
print("=" * 90)

print(f"Normal test cases : {len(normal_results)}")
print(f"Passed            : {passed}")
print(f"Failed            : {failed}")
print(f"Stress cases      : {stress_cases}")

if normal_results:
    accuracy = (passed / len(normal_results)) * 100
    print(f"Demo accuracy     : {accuracy:.2f}%")

print("=" * 90)