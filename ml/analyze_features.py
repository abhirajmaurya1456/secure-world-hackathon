import pandas as pd

FILE_PATH = "data/processed/real_features.csv"

df = pd.read_csv(FILE_PATH)

print("========== DATASET ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== FEATURE STATISTICS ==========")

feature_columns = [
    column for column in df.columns
    if column != "label"
]

print(
    df.groupby("label")[feature_columns]
      .mean()
      .T
      .round(3)
)

print("\n========== BINARY FEATURES ==========")

binary_features = [
    "has_ip",
    "has_https",
    "has_port",
    "has_at_symbol",
    "has_punycode",
]

for feature in binary_features:
    print(f"\n{feature}:")
    print(
        pd.crosstab(
            df[feature],
            df["label"],
            normalize="columns"
        ).round(3)
    )