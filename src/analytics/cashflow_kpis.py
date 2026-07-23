
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB = "db/nifty100.db"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

# -----------------------------
# LOAD DATA
# -----------------------------

ratios = pd.read_sql("""
SELECT *
FROM financial_ratios
WHERE year != 'TTM'
""", conn)

cashflow = pd.read_sql("""
SELECT *
FROM cashflow
""", conn)

sectors = pd.read_sql("""
SELECT company_id, broad_sector
FROM sectors
""", conn)

# -----------------------------
# CLEAN DATA
# -----------------------------

latest_ratios = (
    ratios
    .groupby("company_id")
    .tail(1)
    .copy()
)

numeric_cols = [
    "free_cash_flow_cr",
    "fcf_conversion_rate_pct",
    "capex_intensity_pct",
    "total_debt_cr"
]

for col in numeric_cols:
    if col in latest_ratios.columns:
        latest_ratios[col] = pd.to_numeric(
            latest_ratios[col],
            errors="coerce"
        )

cashflow["operating_activity"] = pd.to_numeric(
    cashflow["operating_activity"],
    errors="coerce"
)

cashflow["investing_activity"] = pd.to_numeric(
    cashflow["investing_activity"],
    errors="coerce"
)

cashflow["financing_activity"] = pd.to_numeric(
    cashflow["financing_activity"],
    errors="coerce"
)

# -----------------------------
# CASHFLOW INTELLIGENCE
# -----------------------------

results = []

for company_id, grp in cashflow.groupby("company_id"):

    grp = grp.sort_values("year")

    latest_cf = grp.iloc[-1]

    cfo_values = grp["operating_activity"].tail(5)

    avg_cfo = cfo_values.mean()

    if avg_cfo > 0:
        cfo_quality_score = 100
        cfo_quality_label = "High Quality"
    elif avg_cfo > -100:
        cfo_quality_score = 60
        cfo_quality_label = "Moderate"
    else:
        cfo_quality_score = 30
        cfo_quality_label = "Accrual Risk"

    distress_flag = (
        latest_cf["operating_activity"] < 0
        and latest_cf["financing_activity"] > 0
    )

    deleveraging_flag = (
        latest_cf["financing_activity"] < 0
    )

    latest_ratio_row = latest_ratios[
        latest_ratios["company_id"] == company_id
    ]

    if latest_ratio_row.empty:
        continue

    latest_ratio_row = latest_ratio_row.iloc[0]

    capex_intensity_pct = latest_ratio_row.get(
        "capex_intensity_pct",
        np.nan
    )

    capex_label = latest_ratio_row.get(
        "capex_intensity_label",
        "Unknown"
    )

    fcf_conversion_pct = latest_ratio_row.get(
        "fcf_conversion_rate_pct",
        np.nan
    )

    sector_row = sectors[
        sectors["company_id"] == company_id
    ]

    sector = None

    if not sector_row.empty:
        sector = sector_row.iloc[0]["broad_sector"]

    capital_allocation_label = "Stable"

    if distress_flag:
        capital_allocation_label = "Distress Signal"

    elif (
        pd.notna(capex_intensity_pct)
        and capex_intensity_pct > 8
    ):
        capital_allocation_label = "Reinvestor"

    elif (
        pd.notna(fcf_conversion_pct)
        and fcf_conversion_pct > 80
    ):
        capital_allocation_label = "Cash Generator"

    results.append({
        "company_id": company_id,
        "sector": sector,
        "cfo_quality_score": cfo_quality_score,
        "cfo_quality_label": cfo_quality_label,
        "capex_intensity_pct": capex_intensity_pct,
        "capex_label": capex_label,
        "fcf_cagr_5yr": np.nan,
        "fcf_conversion_pct": fcf_conversion_pct,
        "distress_flag": distress_flag,
        "deleveraging_flag": deleveraging_flag,
        "capital_allocation_label": capital_allocation_label
    })

# -----------------------------
# ADD MISSING COMPANIES
# -----------------------------

all_companies = set(
    pd.read_sql(
        "SELECT id FROM companies",
        conn
    )["id"]
)

existing_companies = {
    row["company_id"]
    for row in results
}

missing_companies = all_companies - existing_companies

for company_id in missing_companies:

    sector_row = sectors[
        sectors["company_id"] == company_id
    ]

    sector = None

    if not sector_row.empty:
        sector = sector_row.iloc[0]["broad_sector"]

    results.append({
        "company_id": company_id,
        "sector": sector,
        "cfo_quality_score": np.nan,
        "cfo_quality_label": "Data Unavailable",
        "capex_intensity_pct": np.nan,
        "capex_label": "Data Unavailable",
        "fcf_cagr_5yr": np.nan,
        "fcf_conversion_pct": np.nan,
        "distress_flag": False,
        "deleveraging_flag": False,
        "capital_allocation_label": "Data Unavailable"
    })

# -----------------------------
# SAVE OUTPUTS
# -----------------------------

output = pd.DataFrame(results)

output.to_excel(
    OUTPUT_DIR / "cashflow_intelligence.xlsx",
    index=False
)

distress = output[
    output["distress_flag"] == True
]

distress.to_csv(
    OUTPUT_DIR / "distress_alerts.csv",
    index=False
)

print("Rows:", len(output))
print("Distress alerts:", len(distress))
print("Saved -> output/cashflow_intelligence.xlsx")
print("Saved -> output/distress_alerts.csv")

conn.close()

