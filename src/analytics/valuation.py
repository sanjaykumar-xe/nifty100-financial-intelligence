import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

def main():
    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql("SELECT id, company_name FROM companies", conn)
    sectors = pd.read_sql("SELECT company_id, broad_sector FROM sectors", conn)
    ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
    market = pd.read_sql(
        "SELECT * FROM market_cap WHERE year='2024'", conn
    )

    conn.close()

    ratios = ratios[ratios["year"] != "TTM"]
    ratios = ratios.sort_values("year").groupby("company_id").tail(1)

    df = companies.merge(sectors, left_on="id", right_on="company_id", how="left")
    df = df.merge(ratios, left_on="id", right_on="company_id", how="left", suffixes=("", "_r"))
    df = df.merge(market, left_on="id", right_on="company_id", how="left", suffixes=("", "_m"))

    df["pe_ratio"] = pd.to_numeric(df["pe_ratio"], errors="coerce")
    df["pb_ratio"] = pd.to_numeric(df["pb_ratio"], errors="coerce")
    df["ev_ebitda"] = pd.to_numeric(df["ev_ebitda"], errors="coerce")
    df["free_cash_flow_cr"] = pd.to_numeric(df["free_cash_flow_cr"], errors="coerce")
    df["market_cap_crore"] = pd.to_numeric(df["market_cap_crore"], errors="coerce")

    # FCF Yield = FCF / market cap * 100
    df["fcf_yield_pct"] = (
        df["free_cash_flow_cr"] / df["market_cap_crore"] * 100
    ).round(2)

    # Sector median P/E (latest year)
    sector_median_pe = (
        df.groupby("broad_sector")["pe_ratio"]
        .median()
        .rename("sector_median_pe")
    )
    df = df.merge(sector_median_pe, on="broad_sector", how="left")

    df["pe_vs_sector_median_pct"] = (
        (df["pe_ratio"] / df["sector_median_pe"] - 1) * 100
    ).round(2)

    def flag_row(row):
        pe = row["pe_ratio"]
        med = row["sector_median_pe"]
        if pd.isna(pe) or pd.isna(med) or med == 0:
            return "Fair"
        if pe > med * 1.5:
            return "Caution"
        elif pe < med * 0.7:
            return "Discount"
        return "Fair"

    df["flag"] = df.apply(flag_row, axis=1)

    output = df[[
        "id", "company_name", "broad_sector",
        "pe_ratio", "pb_ratio", "ev_ebitda",
        "fcf_yield_pct", "sector_median_pe",
        "pe_vs_sector_median_pct", "flag"
    ]].rename(columns={
        "id": "company_id",
        "sector_median_pe": "5yr_median_PE"
    })

    output.to_excel("output/valuation_summary.xlsx", index=False)

    flagged = output[output["flag"].isin(["Caution", "Discount"])]
    flagged.to_csv("output/valuation_flags.csv", index=False)

    print(f"valuation_summary.xlsx: {len(output)} rows")
    print(f"valuation_flags.csv: {len(flagged)} flagged companies")


if __name__ == "__main__":
    main()