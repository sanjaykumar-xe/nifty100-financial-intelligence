import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB = "db/nifty100.db"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

# -----------------------------------
# LOAD DATA
# -----------------------------------

ratios = pd.read_sql("""
SELECT *
FROM financial_ratios
WHERE year != 'TTM'
""", conn)

valuation = pd.read_excel(
    "output/valuation_summary.xlsx"
)

# latest year per company

ratios = (
    ratios
    .groupby("company_id")
    .tail(1)
    .copy()
)

# -----------------------------------
# NUMERIC CLEANING
# -----------------------------------

numeric_cols = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "interest_coverage",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "debt_to_equity",
    "fcf_conversion_rate_pct",
]

for col in numeric_cols:
    ratios[col] = pd.to_numeric(
        ratios[col],
        errors="coerce"
    )

valuation_cols = [
    "pe_vs_sector_median_pct",
    "pb_ratio",
    "ev_ebitda"
]

for col in valuation_cols:
    valuation[col] = pd.to_numeric(
        valuation[col],
        errors="coerce"
    )

# -----------------------------------
# MERGE
# -----------------------------------

df = ratios.merge(
    valuation[
        [
            "company_id",
            "pe_vs_sector_median_pct",
            "pb_ratio",
            "ev_ebitda"
        ]
    ],
    on="company_id",
    how="left"
)

# -----------------------------------
# PERCENTILE SCORING
# -----------------------------------

def pct_rank(series, ascending=True):

    rank = series.rank(
        pct=True,
        ascending=ascending
    )

    return rank * 100


# QUALITY

df["quality_score"] = (
    pct_rank(df["return_on_equity_pct"])
    + pct_rank(df["return_on_capital_employed_pct"])
    + pct_rank(df["net_profit_margin_pct"])
    + pct_rank(df["interest_coverage"])
) / 4

# GROWTH

df["growth_score"] = (
    pct_rank(df["revenue_cagr_5yr"])
    + pct_rank(df["pat_cagr_5yr"])
    + pct_rank(df["eps_cagr_5yr"])
) / 3

# BALANCE SHEET

df["balance_score"] = (
    pct_rank(df["debt_to_equity"], ascending=False)
    + pct_rank(df["fcf_conversion_rate_pct"])
) / 2

# VALUE

df["value_score"] = (
    pct_rank(
        df["pe_vs_sector_median_pct"],
        ascending=False
    )
    + pct_rank(
        df["pb_ratio"],
        ascending=False
    )
    + pct_rank(
        df["ev_ebitda"],
        ascending=False
    )
) / 3

# -----------------------------------
# FINAL SCORE
# -----------------------------------

df["compounder_score"] = (
    df["quality_score"] * 0.35
    + df["growth_score"] * 0.30
    + df["balance_score"] * 0.20
    + df["value_score"] * 0.15
)

# -----------------------------------
# RANKS
# -----------------------------------

df["overall_rank"] = (
    df["compounder_score"]
    .rank(
        ascending=False,
        method="dense"
    )
)

# -----------------------------------
# SAVE MASTER FILE
# -----------------------------------

df = df.sort_values(
    "compounder_score",
    ascending=False
)

master_cols = [
    "company_id",
    "quality_score",
    "growth_score",
    "balance_score",
    "value_score",
    "compounder_score",
    "overall_rank"
]

df[master_cols].to_excel(
    OUTPUT_DIR / "company_rankings.xlsx",
    index=False
)

# -----------------------------------
# TOP QUALITY
# -----------------------------------

(
    df.sort_values(
        "quality_score",
        ascending=False
    )
    .head(20)
    .to_excel(
        OUTPUT_DIR /
        "top_quality_companies.xlsx",
        index=False
    )
)

# -----------------------------------
# TOP GROWTH
# -----------------------------------

(
    df.sort_values(
        "growth_score",
        ascending=False
    )
    .head(20)
    .to_excel(
        OUTPUT_DIR /
        "top_growth_companies.xlsx",
        index=False
    )
)

# -----------------------------------
# TOP VALUE
# -----------------------------------

(
    df.sort_values(
        "value_score",
        ascending=False
    )
    .head(20)
    .to_excel(
        OUTPUT_DIR /
        "top_value_companies.xlsx",
        index=False
    )
)

# -----------------------------------
# TOP COMPOUNDERS
# -----------------------------------

(
    df.sort_values(
        "compounder_score",
        ascending=False
    )
    .head(20)
    .to_excel(
        OUTPUT_DIR /
        "top_compounders.xlsx",
        index=False
    )
)

print("Companies ranked:", len(df))
print("Saved -> output/company_rankings.xlsx")
print("Saved -> output/top_quality_companies.xlsx")
print("Saved -> output/top_growth_companies.xlsx")
print("Saved -> output/top_value_companies.xlsx")
print("Saved -> output/top_compounders.xlsx")