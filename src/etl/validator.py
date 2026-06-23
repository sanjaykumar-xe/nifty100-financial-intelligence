from pathlib import Path
import pandas as pd

PROCESSED = Path("data/processed")
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

failures = []


def add_failure(rule, table, issue, severity="WARNING"):
    failures.append({
        "rule": rule,
        "table": table,
        "issue": issue,
        "severity": severity
    })


def load_csv(file):
    return pd.read_csv(PROCESSED / file)


def validate_companies():
    df = load_csv("companies.csv")

    if df["id"].duplicated().any():
        add_failure("DQ-01", "companies", "Duplicate company id found", "CRITICAL")

    if df["id"].isna().any():
        add_failure("DQ-01", "companies", "Missing company id found", "CRITICAL")

    print("companies validated")


def validate_profitandloss():
    df = load_csv("profitandloss.csv")

    if df[["company_id", "year"]].duplicated().any():
        add_failure("DQ-02", "profitandloss", "Duplicate company_id + year found", "CRITICAL")

    if "sales" in df.columns and (df["sales"] <= 0).any():
        add_failure("DQ-06", "profitandloss", "Sales <= 0 found", "WARNING")

    if {"sales", "expenses", "operating_profit"}.issubset(df.columns):
        sales = pd.to_numeric(df["sales"], errors="coerce")
        expenses = pd.to_numeric(df["expenses"], errors="coerce")
        operating_profit = pd.to_numeric(df["operating_profit"], errors="coerce")

        diff = abs((sales - expenses) - operating_profit)
        tolerance = sales.abs() * 0.01

        if (diff > tolerance).any():
            add_failure("DQ-05", "profitandloss", "Operating profit mismatch > 1%", "WARNING")

    print("profitandloss validated")


def validate_balancesheet():
    df = load_csv("balancesheet.csv")

    if df[["company_id", "year"]].duplicated().any():
        add_failure("DQ-02", "balancesheet", "Duplicate company_id + year found", "CRITICAL")

    if {"total_assets", "total_liabilities"}.issubset(df.columns):
        assets = pd.to_numeric(df["total_assets"], errors="coerce")
        liabilities = pd.to_numeric(df["total_liabilities"], errors="coerce")

        diff_pct = abs(assets - liabilities) / assets.replace(0, pd.NA)

        if (diff_pct > 0.01).any():
            add_failure("DQ-04", "balancesheet", "Balance sheet mismatch > 1%", "WARNING")

    print("balancesheet validated")


def validate_cashflow():
    df = load_csv("cashflow.csv")

    if df[["company_id", "year"]].duplicated().any():
        add_failure("DQ-02", "cashflow", "Duplicate company_id + year found", "CRITICAL")

    if {"operating_activity", "investing_activity", "financing_activity", "net_cash_flow"}.issubset(df.columns):
        op = pd.to_numeric(df["operating_activity"], errors="coerce")
        inv = pd.to_numeric(df["investing_activity"], errors="coerce")
        fin = pd.to_numeric(df["financing_activity"], errors="coerce")
        net = pd.to_numeric(df["net_cash_flow"], errors="coerce")

        diff = abs((op + inv + fin) - net)

        if (diff > 10).any():
            add_failure("DQ-07", "cashflow", "Net cash flow mismatch > 10 Cr", "WARNING")

    print("cashflow validated")


def validate_foreign_keys():
    companies = load_csv("companies.csv")
    valid_ids = set(companies["id"].dropna())

    files = [
        "profitandloss.csv",
        "balancesheet.csv",
        "cashflow.csv",
        "analysis.csv",
        "documents.csv",
        "prosandcons.csv",
        "sectors.csv",
        "stock_prices.csv",
        "market_cap.csv",
        "financial_ratios.csv",
        "peer_groups.csv",
    ]

    for file in files:
        df = load_csv(file)

        if "company_id" not in df.columns:
            continue

        ids = set(df["company_id"].dropna())
        missing = ids - valid_ids

        if missing:
            add_failure(
                "DQ-03",
                file,
                f"Invalid FK company_id found: {sorted(list(missing))[:10]}",
                "CRITICAL"
            )

    print("foreign keys validated")


def main():
    validate_companies()
    validate_profitandloss()
    validate_balancesheet()
    validate_cashflow()
    validate_foreign_keys()

    result = pd.DataFrame(failures)

    if result.empty:
        result = pd.DataFrame(columns=["rule", "table", "issue", "severity"])

    result.to_csv(OUTPUT / "validation_failures.csv", index=False)

    print("\nValidation completed.")
    print(f"Failures found: {len(result)}")
    print("Saved: output/validation_failures.csv")


if __name__ == "__main__":
    main()