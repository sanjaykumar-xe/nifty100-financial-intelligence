import sqlite3
import pandas as pd
from pathlib import Path

DB = "db/nifty100.db"

conn = sqlite3.connect(DB)

df = pd.read_sql("""
SELECT *
FROM financial_ratios
WHERE year != 'TTM'
""", conn)

conn.close()

# latest available year per company
latest = (
    df.sort_values(["company_id"])
      .groupby("company_id")
      .tail(1)
      .copy()
)

numeric_cols = [
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "operating_profit_margin_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "return_on_capital_employed_pct"
]

for col in numeric_cols:
    latest[col] = pd.to_numeric(latest[col], errors="coerce")

records = []

for _, row in latest.iterrows():

    cid = row["company_id"]

    # ---------- PROS ----------

    if pd.notna(row["return_on_equity_pct"]) and row["return_on_equity_pct"] > 20:
        records.append([
            cid,
            "pro",
            "PRO_01",
            "Consistently high return on equity above 20% demonstrates exceptional capital efficiency",
            90
        ])

    if pd.notna(row["free_cash_flow_cr"]) and row["free_cash_flow_cr"] > 0:
        records.append([
            cid,
            "pro",
            "PRO_02",
            "Strong free cash flow generation signals healthy business fundamentals",
            80
        ])

    if row["debt_to_equity"] == 0:
        records.append([
            cid,
            "pro",
            "PRO_03",
            "Debt-free balance sheet provides financial flexibility and eliminates interest burden",
            95
        ])

    if pd.notna(row["revenue_cagr_5yr"]) and row["revenue_cagr_5yr"] > 15:
        records.append([
            cid,
            "pro",
            "PRO_04",
            "Revenue growing above 15% CAGR reflects strong business momentum",
            85
        ])

    if pd.notna(row["operating_profit_margin_pct"]) and row["operating_profit_margin_pct"] > 25:
        records.append([
            cid,
            "pro",
            "PRO_05",
            "Operating profit margin above 25% indicates strong pricing power and cost discipline",
            80
        ])

    # ---------- CONS ----------

    if pd.notna(row["debt_to_equity"]) and row["debt_to_equity"] > 2:
        records.append([
            cid,
            "con",
            "CON_01",
            f"Debt-to-equity ratio of {row['debt_to_equity']:.2f} is elevated and warrants monitoring",
            90
        ])

    if pd.notna(row["free_cash_flow_cr"]) and row["free_cash_flow_cr"] < 0:
        records.append([
            cid,
            "con",
            "CON_02",
            "Negative free cash flow raises concern about cash generation quality",
            80
        ])

    if pd.notna(row["interest_coverage"]) and row["interest_coverage"] < 1.5:
        records.append([
            cid,
            "con",
            "CON_03",
            "Interest coverage ratio below 1.5x indicates elevated debt servicing risk",
            90
        ])

    if pd.notna(row["return_on_capital_employed_pct"]) and row["return_on_capital_employed_pct"] < 10:
        records.append([
            cid,
            "con",
            "CON_04",
            "Return on capital employed below 10% suggests weak capital efficiency",
            75
        ])

    if pd.notna(row["revenue_cagr_5yr"]) and row["revenue_cagr_5yr"] < 5:
        records.append([
            cid,
            "con",
            "CON_05",
            "Revenue growth below 5% over five years suggests limited business momentum",
            75
        ])

# guarantee at least 1 pro and 1 con per company
companies = latest["company_id"].unique()

for company in companies:

    company_rows = [r for r in records if r[0] == company]

    has_pro = any(r[1] == "pro" for r in company_rows)
    has_con = any(r[1] == "con" for r in company_rows)

    if not has_pro:
        records.append([
            company,
            "pro",
            "PRO_DEFAULT",
            "Business maintains a measurable operating presence within its sector",
            61
        ])

    if not has_con:
        records.append([
            company,
            "con",
            "CON_DEFAULT",
            "Company should continue monitoring operational and market risks",
            61
        ])

output = pd.DataFrame(
    records,
    columns=[
        "company_id",
        "type",
        "rule_id",
        "text",
        "confidence_pct"
    ]
)

Path("output").mkdir(exist_ok=True)

output.to_csv(
    "output/pros_cons_generated.csv",
    index=False
)

print("Rows generated:", len(output))
print("Companies covered:", output["company_id"].nunique())
print("Saved -> output/pros_cons_generated.csv")

