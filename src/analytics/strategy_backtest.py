import sqlite3
from pathlib import Path

import pandas as pd

DB = "db/nifty100.db"
OUTPUT_DIR = Path("output")

conn = sqlite3.connect(DB)

# -------------------------
# LOAD FINANCIAL RATIOS
# -------------------------

ratios = pd.read_sql("""
SELECT *
FROM financial_ratios
WHERE year != 'TTM'
""", conn)

latest = (
    ratios
    .groupby("company_id")
    .tail(1)
    .copy()
)

# -------------------------
# LOAD PORTFOLIOS
# -------------------------

portfolios = {
    "Compounder": pd.read_excel(
        OUTPUT_DIR / "top10_compounder_portfolio.xlsx"
    ),
    "Quality": pd.read_excel(
        OUTPUT_DIR / "top10_quality_portfolio.xlsx"
    ),
    "Growth": pd.read_excel(
        OUTPUT_DIR / "top10_growth_portfolio.xlsx"
    ),
    "Value": pd.read_excel(
        OUTPUT_DIR / "top10_value_portfolio.xlsx"
    )
}

results = []

# -------------------------
# ANALYZE PORTFOLIOS
# -------------------------

for strategy, portfolio in portfolios.items():

    merged = portfolio.merge(
        latest,
        on="company_id",
        how="left"
    )

    for col in [
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr"
    ]:
        merged[col] = pd.to_numeric(
            merged[col],
            errors="coerce"
        )

    results.append({
        "strategy": strategy,
        "avg_revenue_cagr_5yr":
            merged["revenue_cagr_5yr"].mean(),

        "avg_pat_cagr_5yr":
            merged["pat_cagr_5yr"].mean(),

        "avg_eps_cagr_5yr":
            merged["eps_cagr_5yr"].mean()
    })

# -------------------------
# SAVE OUTPUTS
# -------------------------

backtest = pd.DataFrame(results)

backtest.to_excel(
    OUTPUT_DIR / "strategy_backtest.xlsx",
    index=False
)

summary = (
    backtest
    .sort_values(
        "avg_eps_cagr_5yr",
        ascending=False
    )
)

summary.to_excel(
    OUTPUT_DIR / "strategy_summary.xlsx",
    index=False
)

print("Strategies analyzed:", len(backtest))
print("Saved -> output/strategy_backtest.xlsx")
print("Saved -> output/strategy_summary.xlsx")