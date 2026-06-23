from pathlib import Path
import pandas as pd

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
OUTPUT = Path("output")

PROCESSED.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

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


def clean_all_files():
    companies = load_excel("companies.xlsx")
    companies["id"] = companies["id"].apply(clean_id)
    valid_ids = set(companies["id"].dropna())

    companies.to_csv(PROCESSED / "companies.csv", index=False)

    files = [
        "profitandloss.xlsx",
        "balancesheet.xlsx",
        "cashflow.xlsx",
        "analysis.xlsx",
        "documents.xlsx",
        "prosandcons.xlsx",
        "sectors.xlsx",
        "stock_prices.xlsx",
        "market_cap.xlsx",
        "financial_ratios.xlsx",
        "peer_groups.xlsx",
    ]

    audit = []

    for file in files:
        df = load_excel(file)
        original_rows = len(df)

        if "company_id" in df.columns:
            df["company_id"] = df["company_id"].apply(clean_id)
            df = df[df["company_id"].isin(valid_ids)]
             # remove duplicates based on business keys
        if {"company_id", "year"}.issubset(df.columns):
            df = df.drop_duplicates(subset=["company_id", "year"], keep="first")
        elif "id" in df.columns:
            df = df.drop_duplicates(subset=["id"], keep="first")
        else:
            df = df.drop_duplicates()

        output_name = file.replace(".xlsx", ".csv")
        df.to_csv(PROCESSED / output_name, index=False)

        audit.append({
            "file": file,
            "rows_before": original_rows,
            "rows_after": len(df),
            "rows_removed": original_rows - len(df)
        })

        print(f"Cleaned {file}: {original_rows} -> {len(df)}")

    pd.DataFrame(audit).to_csv(OUTPUT / "cleaning_audit.csv", index=False)

    print("\nCleaning completed.")
    print("Saved cleaned CSVs in data/processed/")
    print("Saved audit: output/cleaning_audit.csv")


if __name__ == "__main__":
    clean_all_files()