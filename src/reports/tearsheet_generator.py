import sqlite3
from pathlib import Path

import pandas as pd

DB = "db/nifty100.db"

OUTPUT_DIR = Path("reports/tearsheets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)

# ----------------------------------
# LOAD DATABASE TABLES
# ----------------------------------

companies = pd.read_sql("""
SELECT *
FROM companies
""", conn)

financials = pd.read_sql("""
SELECT *
FROM financial_ratios
WHERE year != 'TTM'
""", conn)

# latest financial row per company
financials = (
    financials
    .groupby("company_id")
    .tail(1)
)

# ----------------------------------
# LOAD ANALYTICS OUTPUTS
# ----------------------------------

cashflow = pd.read_excel(
    "output/cashflow_intelligence.xlsx"
)

pros_cons = pd.read_csv(
    "output/pros_cons_generated.csv"
)

valuation = pd.read_excel(
    "output/valuation_summary.xlsx"
)

peer = pd.read_excel(
    "output/peer_comparison.xlsx"
)

# ----------------------------------
# GENERATE TEARSHEETS
# ----------------------------------

company_ids = sorted(companies["id"].unique())

generated = 0

for company_id in company_ids:

    company_info = companies[
        companies["id"] == company_id
    ]

    if company_info.empty:
        continue

    company_info = company_info.iloc[0]

    company_name = company_info["company_name"]

    financial_row = financials[
        financials["company_id"] == company_id
    ]

    cashflow_row = cashflow[
        cashflow["company_id"] == company_id
    ]

    valuation_row = valuation[
        valuation["company_id"] == company_id
    ]

    peer_rows = peer[
        peer["company_id"] == company_id
    ]

    pros = pros_cons[
        (pros_cons["company_id"] == company_id)
        & (pros_cons["type"] == "pro")
    ][["text", "confidence_pct"]]

    cons = pros_cons[
        (pros_cons["company_id"] == company_id)
        & (pros_cons["type"] == "con")
    ][["text", "confidence_pct"]]

    filepath = OUTPUT_DIR / f"{company_id}_tearsheet.xlsx"

    with pd.ExcelWriter(
        filepath,
        engine="openpyxl"
    ) as writer:

        # -------------------------
        # COMPANY PROFILE
        # -------------------------

        pd.DataFrame({
            "Field": [
                "Company ID",
                "Company Name",
                "Website",
                "ROE %",
                "ROCE %"
            ],
            "Value": [
                company_id,
                company_name,
                company_info.get("website"),
                company_info.get("roe_percentage"),
                company_info.get("roce_percentage")
            ]
        }).to_excel(
            writer,
            sheet_name="Profile",
            index=False
        )

        # -------------------------
        # FINANCIAL QUALITY
        # -------------------------

        if not financial_row.empty:
            financial_row.to_excel(
                writer,
                sheet_name="Financials",
                index=False
            )

        # -------------------------
        # CASHFLOW INTELLIGENCE
        # -------------------------

        if not cashflow_row.empty:
            cashflow_row.to_excel(
                writer,
                sheet_name="Cashflow",
                index=False
            )

        # -------------------------
        # VALUATION
        # -------------------------

        if not valuation_row.empty:
            valuation_row.to_excel(
                writer,
                sheet_name="Valuation",
                index=False
            )

        # -------------------------
        # PROS
        # -------------------------

        pros.to_excel(
            writer,
            sheet_name="Pros",
            index=False
        )

        # -------------------------
        # CONS
        # -------------------------

        cons.to_excel(
            writer,
            sheet_name="Cons",
            index=False
        )

        # -------------------------
        # PEER COMPARISON
        # -------------------------

        if not peer_rows.empty:
            peer_rows.to_excel(
                writer,
                sheet_name="Peers",
                index=False
            )

    generated += 1

print(f"Tearsheets generated: {generated}")
print("Location -> reports/tearsheets")