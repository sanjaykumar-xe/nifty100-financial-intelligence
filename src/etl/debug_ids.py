from pathlib import Path
import pandas as pd

RAW = Path("data/raw")

CORE_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}


def load_excel(file):
    if file in CORE_FILES:
        return pd.read_excel(RAW / file, header=1)
    return pd.read_excel(RAW / file)


def clean_id(value):
    if pd.isna(value):
        return None
    return (
        str(value)
        .strip()
        .upper()
        .replace(".NS", "")
        .replace("\n", "")
        .replace("\r", "")
        .replace(" ", "")
    )


companies = load_excel("companies.xlsx")
valid_ids = set(companies["id"].apply(clean_id).dropna())

print("Total companies in companies.xlsx:", len(valid_ids))
print("\nSample company ids:")
print(sorted(list(valid_ids))[:20])

files = [
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
    "financial_ratios.xlsx",
]

for file in files:
    df = load_excel(file)
    ids = set(df["company_id"].apply(clean_id).dropna())
    missing = sorted(list(ids - valid_ids))

    print("\nFILE:", file)
    print("Unique IDs:", len(ids))
    print("Missing from companies:", missing)