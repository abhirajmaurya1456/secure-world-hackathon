import pandas as pd

FILE_PATH = "data/raw/url_features_extracted1.csv"

df = pd.read_csv(FILE_PATH)

print("========== BASIC INFORMATION ==========")
print("Shape:", df.shape)

print("\n========== COLUMNS ==========")
print(df.columns.tolist())

print("\n========== FIRST 10 ROWS ==========")
print(df.head(10).to_string())

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== UNIQUE VALUES PER COLUMN ==========")
for column in df.columns:
    print(f"{column}: {df[column].nunique()}")