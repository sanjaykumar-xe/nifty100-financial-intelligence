import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)

from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

from src.etl.normaliser import normalize_year

DB = Path("db/nifty100.db")
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

query = """
SELECT
    p.company_id,
    p.year,
    p.sales,
    p.operating_profit,
    p.opm_percentage,
    p.other_income,
    p.interest,
    p.depreciation,
    p.net_profit,
    p.eps,
    p.dividend_payout,

    b.equity_capital,
    b.reserves,
    b.borrowings,
    b.investments,
    b.total_assets,

    cf.operating_activity,
    cf.investing_activity,
    cf.financing_activity,
    cf.net_cash_flow,

    c.face_value,
    s.broad_sector
FROM profitandloss p
LEFT JOIN balancesheet b
    ON p.company_id = b.company_id AND p.year = b.year
LEFT JOIN cashflow cf
    ON p.company_id = cf.company_id AND p.year = cf.year
LEFT JOIN companies c
    ON p.company_id = c.id
LEFT JOIN sectors s
    ON p.company_id = s.company_id
"""

df = pd.read_sql_query(query, conn)

df["year_num"] = df["year"].apply(normalize_year)

results = []
capital_rows = []

for _, row in df.iterrows():
    equity = (row["equity_capital"] or 0) + (row["reserves"] or 0)

    npm = net_profit_margin(row["net_profit"], row["sales"])
    opm = operating_profit_margin(row["operating_profit"], row["sales"])
    roe = return_on_equity(row["net_profit"], row["equity_capital"], row["reserves"])
    roce = return_on_capital_employed(
        row["operating_profit"],
        row["depreciation"],
        row["equity_capital"],
        row["reserves"],
        row["borrowings"],
    )
    roa = return_on_assets(row["net_profit"], row["total_assets"])

    de = debt_to_equity(row["borrowings"], row["equity_capital"], row["reserves"])
    high_de = high_leverage_flag(de, row["broad_sector"])

    icr = interest_coverage_ratio(row["operating_profit"], row["other_income"], row["interest"])
    icr_display = icr_label(icr)
    icr_warn = icr_warning_flag(icr)

    nd = net_debt(row["borrowings"], row["investments"])
    turnover = asset_turnover(row["sales"], row["total_assets"])

    fcf = free_cash_flow(row["operating_activity"], row["investing_activity"])
    capex = abs(row["investing_activity"])

    capex_result = capex_intensity(row["investing_activity"], row["sales"])
    if capex_result is None:
       capex_pct, capex_label = None, None
    else:
       capex_pct, capex_label = capex_result
    fcf_conv = fcf_conversion_rate(fcf, row["operating_profit"])

    shares = None
    book_value_per_share = None

    if row["face_value"] and row["equity_capital"] and row["equity_capital"] != 0:
        shares = row["equity_capital"] / row["face_value"]
        if shares != 0:
            book_value_per_share = equity / shares

    pattern = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"]
    )

    capital_rows.append({
        "company_id": row["company_id"],
        "year": row["year"],
        "cfo_sign": "+" if row["operating_activity"] >= 0 else "-",
        "cfi_sign": "+" if row["investing_activity"] >= 0 else "-",
        "cff_sign": "+" if row["financing_activity"] >= 0 else "-",
        "pattern_label": pattern
    })

    results.append({
        "company_id": row["company_id"],
        "year": row["year"],
        "net_profit_margin_pct": npm,
        "operating_profit_margin_pct": opm,
        "return_on_equity_pct": roe,
        "return_on_capital_employed_pct": roce,
        "return_on_assets_pct": roa,
        "debt_to_equity": de,
        "high_leverage_flag": high_de,
        "interest_coverage": icr,
        "icr_label": icr_display,
        "icr_warning_flag": icr_warn,
        "net_debt_cr": nd,
        "asset_turnover": turnover,
        "free_cash_flow_cr": fcf,
        "capex_cr": capex,
        "capex_intensity_pct": capex_pct,
        "capex_intensity_label": capex_label,
        "fcf_conversion_rate_pct": fcf_conv,
        "earnings_per_share": row["eps"],
        "book_value_per_share": book_value_per_share,
        "dividend_payout_ratio_pct": row["dividend_payout"],
        "total_debt_cr": row["borrowings"],
        "cash_from_operations_cr": row["operating_activity"],
    })

ratios = pd.DataFrame(results)

source = df[["company_id", "year", "year_num", "sales", "net_profit", "eps"]].copy()
source = source.dropna(subset=["year_num"])

for metric, col in [
    ("revenue", "sales"),
    ("pat", "net_profit"),
    ("eps", "eps"),
]:
    for years in [3, 5, 10]:
        value_col = f"{metric}_cagr_{years}yr"
        flag_col = f"{metric}_cagr_{years}yr_flag"

        ratios[value_col] = None
        ratios[flag_col] = None

        for company_id, group in source.groupby("company_id"):
            group = group.sort_values("year_num").reset_index(drop=True)

            for i in range(len(group)):
                if i < years:
                    value, flag = None, "INSUFFICIENT"
                else:
                    start_value = group.loc[i - years, col]
                    end_value = group.loc[i, col]
                    value, flag = calculate_cagr(start_value, end_value, years)

                mask = (
                    (ratios["company_id"] == company_id)
                    & (ratios["year"] == group.loc[i, "year"])
                )

                ratios.loc[mask, value_col] = value
                ratios.loc[mask, flag_col] = flag

score_cols = [
    "net_profit_margin_pct",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "return_on_assets_pct",
    "asset_turnover",
]

score_df = ratios[score_cols].copy()

for col in score_cols:
    score_df[col] = pd.to_numeric(score_df[col], errors="coerce")
    ratios[col + "_score"] = score_df[col].rank(pct=True) * 100

ratios["composite_quality_score"] = ratios[
    [col + "_score" for col in score_cols]
].mean(axis=1)

drop_score_cols = [col + "_score" for col in score_cols]
ratios = ratios.drop(columns=drop_score_cols)

# Add missing columns to SQLite table
existing_cols = pd.read_sql_query("PRAGMA table_info(financial_ratios);", conn)["name"].tolist()

for col in ratios.columns:
    if col not in existing_cols:
        conn.execute(f'ALTER TABLE financial_ratios ADD COLUMN "{col}" TEXT;')

conn.commit()

# Reload table columns after ALTER TABLE
table_cols = pd.read_sql_query("PRAGMA table_info(financial_ratios);", conn)["name"].tolist()

ratios = ratios[[col for col in ratios.columns if col in table_cols]]

# Replace old ratio rows
conn.execute("DELETE FROM financial_ratios;")
conn.commit()

ratios = ratios.replace({np.nan: None})
ratios.to_sql("financial_ratios", conn, if_exists="append", index=False)

pd.DataFrame(capital_rows).to_csv(OUTPUT / "capital_allocation.csv", index=False)

row_count = pd.read_sql_query("SELECT COUNT(*) AS count FROM financial_ratios;", conn)
print("financial_ratios row count:", row_count["count"].iloc[0])

conn.close()

print("Saved output/capital_allocation.csv")
print("Financial ratios table populated successfully.")