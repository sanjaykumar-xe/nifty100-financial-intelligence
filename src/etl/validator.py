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

    print("DQ-01 completed")


def validate_pk_pairs():
    files = ["profitandloss.csv", "balancesheet.csv", "cashflow.csv", "financial_ratios.csv"]

    for file in files:
        df = load_csv(file)

        if {"company_id", "year"}.issubset(df.columns):
            if df[["company_id", "year"]].duplicated().any():
                add_failure("DQ-02", file, "Duplicate company_id + year found", "CRITICAL")

    print("DQ-02 completed")


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

        missing = set(df["company_id"].dropna()) - valid_ids

        if missing:
            add_failure("DQ-03", file, f"Invalid FK company_id found: {list(missing)[:10]}", "CRITICAL")

    print("DQ-03 completed")


def validate_balance_sheet():
    df = load_csv("balancesheet.csv")

    assets = pd.to_numeric(df["total_assets"], errors="coerce")
    liabilities = pd.to_numeric(df["total_liabilities"], errors="coerce")

    diff_pct = abs(assets - liabilities) / assets.replace(0, pd.NA)

    if (diff_pct > 0.01).any():
        add_failure("DQ-04", "balancesheet", "Balance sheet mismatch > 1%", "WARNING")

    print("DQ-04 completed")


def validate_opm():
    df = load_csv("profitandloss.csv")

    sales = pd.to_numeric(df["sales"], errors="coerce")
    expenses = pd.to_numeric(df["expenses"], errors="coerce")
    operating_profit = pd.to_numeric(df["operating_profit"], errors="coerce")

    diff = abs((sales - expenses) - operating_profit)
    tolerance = sales.abs() * 0.01

    if (diff > tolerance).any():
        add_failure("DQ-05", "profitandloss", "Operating profit mismatch > 1%", "WARNING")

    print("DQ-05 completed")


def validate_positive_sales():
    df = load_csv("profitandloss.csv")
    sales = pd.to_numeric(df["sales"], errors="coerce")

    if (sales <= 0).any():
        add_failure("DQ-06", "profitandloss", "Sales <= 0 found", "WARNING")

    print("DQ-06 completed")


def validate_net_cash_flow():
    df = load_csv("cashflow.csv")

    op = pd.to_numeric(df["operating_activity"], errors="coerce")
    inv = pd.to_numeric(df["investing_activity"], errors="coerce")
    fin = pd.to_numeric(df["financing_activity"], errors="coerce")
    net = pd.to_numeric(df["net_cash_flow"], errors="coerce")

    diff = abs((op + inv + fin) - net)

    if (diff > 10).any():
        add_failure("DQ-07", "cashflow", "Net cash flow mismatch > 10 Cr", "WARNING")

    print("DQ-07 completed")


def validate_tax_rate():
    df = load_csv("profitandloss.csv")

    if "tax_percentage" in df.columns:
        tax = pd.to_numeric(df["tax_percentage"], errors="coerce")

        if ((tax < 0) | (tax > 60)).any():
            add_failure("DQ-08", "profitandloss", "Tax rate outside 0% to 60%", "WARNING")

    print("DQ-08 completed")


def validate_dividend_cap():
    df = load_csv("profitandloss.csv")

    if "dividend_payout" in df.columns:
        dividend = pd.to_numeric(df["dividend_payout"], errors="coerce")

        if (dividend > 150).any():
            add_failure("DQ-09", "profitandloss", "Dividend payout greater than 150%", "WARNING")

    print("DQ-09 completed")


def validate_url_fields():
    checks = [
        ("companies.csv", ["website", "nse_profile", "bse_profile"]),
        ("documents.csv", ["Annual_Report"]),
    ]

    for file, cols in checks:
        df = load_csv(file)

        for col in cols:
            if col in df.columns:
                invalid = df[col].dropna().astype(str).apply(
                    lambda x: not (x.startswith("http://") or x.startswith("https://"))
                )

                if invalid.any():
                    add_failure("DQ-10", file, f"Invalid URL format in {col}", "WARNING")

    print("DQ-10 completed")


def validate_eps_sign():
    df = load_csv("profitandloss.csv")

    if {"net_profit", "eps"}.issubset(df.columns):
        profit = pd.to_numeric(df["net_profit"], errors="coerce")
        eps = pd.to_numeric(df["eps"], errors="coerce")

        bad = ((profit > 0) & (eps <= 0)) | ((profit < 0) & (eps > 0))

        if bad.any():
            add_failure("DQ-11", "profitandloss", "EPS sign inconsistent with net profit", "WARNING")

    print("DQ-11 completed")


def validate_price_range():
    df = load_csv("stock_prices.csv")

    required = {"open_price", "high_price", "low_price", "close_price"}
    if required.issubset(df.columns):
        high = pd.to_numeric(df["high_price"], errors="coerce")
        low = pd.to_numeric(df["low_price"], errors="coerce")
        open_p = pd.to_numeric(df["open_price"], errors="coerce")
        close = pd.to_numeric(df["close_price"], errors="coerce")

        bad = (high < open_p) | (high < close) | (low > open_p) | (low > close)

        if bad.any():
            add_failure("DQ-12", "stock_prices", "OHLC price range invalid", "WARNING")

    print("DQ-12 completed")


def validate_market_cap_positive():
    df = load_csv("market_cap.csv")

    if "market_cap_crore" in df.columns:
        mcap = pd.to_numeric(df["market_cap_crore"], errors="coerce")

        if (mcap <= 0).any():
            add_failure("DQ-13", "market_cap", "Market cap <= 0 found", "WARNING")

    print("DQ-13 completed")


def validate_sector_coverage():
    companies = load_csv("companies.csv")
    sectors = load_csv("sectors.csv")

    missing = set(companies["id"].dropna()) - set(sectors["company_id"].dropna())

    if missing:
        add_failure("DQ-14", "sectors", f"Companies missing sector mapping: {list(missing)[:10]}", "CRITICAL")

    print("DQ-14 completed")


def validate_document_year():
    df = load_csv("documents.csv")

    if "Year" in df.columns:
        years = pd.to_numeric(df["Year"], errors="coerce")

        if ((years < 2010) | (years > 2026)).any():
            add_failure("DQ-15", "documents", "Document year outside expected range", "WARNING")

    print("DQ-15 completed")


def validate_financial_ratio_coverage():
    companies = load_csv("companies.csv")
    ratios = load_csv("financial_ratios.csv")

    covered = set(ratios["company_id"].dropna())
    missing = set(companies["id"].dropna()) - covered

    if missing:
        add_failure("DQ-16", "financial_ratios", f"Companies missing financial ratio coverage: {list(missing)[:10]}", "WARNING")

    print("DQ-16 completed")


def main():
    validate_companies()
    validate_pk_pairs()
    validate_foreign_keys()
    validate_balance_sheet()
    validate_opm()
    validate_positive_sales()
    validate_net_cash_flow()
    validate_tax_rate()
    validate_dividend_cap()
    validate_url_fields()
    validate_eps_sign()
    validate_price_range()
    validate_market_cap_positive()
    validate_sector_coverage()
    validate_document_year()
    validate_financial_ratio_coverage()

    result = pd.DataFrame(failures)

    if result.empty:
        result = pd.DataFrame(columns=["rule", "table", "issue", "severity"])

    result.to_csv(OUTPUT / "validation_failures.csv", index=False)

    critical_count = 0
    if not result.empty:
        critical_count = (result["severity"] == "CRITICAL").sum()

    print("\nValidation completed.")
    print(f"Total failures found: {len(result)}")
    print(f"Critical failures: {critical_count}")
    print("Saved: output/validation_failures.csv")


if __name__ == "__main__":
    main()