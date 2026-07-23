import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB = "db/nifty100.db"
OUTPUT_DIR = Path("output")

conn = sqlite3.connect(DB)

# -----------------------------------
# LOAD DATA
# -----------------------------------

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

for col in [
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr"
]:
    latest[col] = pd.to_numeric(
        latest[col],
        errors="coerce"
    )

# -----------------------------------
# PORTFOLIOS
# -----------------------------------

portfolio_files = {
    "Compounder":
        OUTPUT_DIR / "top10_compounder_portfolio.xlsx",

    "Quality":
        OUTPUT_DIR / "top10_quality_portfolio.xlsx",

    "Growth":
        OUTPUT_DIR / "top10_growth_portfolio.xlsx",

    "Value":
        OUTPUT_DIR / "top10_value_portfolio.xlsx"
}

simulation_results = []

# -----------------------------------
# MONTE CARLO
# -----------------------------------

for portfolio_name, file_path in portfolio_files.items():

    portfolio = pd.read_excel(file_path)

    merged = portfolio.merge(
        latest,
        on="company_id",
        how="left"
    )

    growth_vector = (
        merged["eps_cagr_5yr"]
        .fillna(0)
        .values
    )

    simulations = []

    for _ in range(5000):

        random_returns = np.random.normal(
            loc=growth_vector,
            scale=np.abs(growth_vector) * 0.5 + 5
        )

        portfolio_return = np.mean(
            random_returns
        )

        simulations.append(
            portfolio_return
        )

    simulations = np.array(simulations)

    expected_return = simulations.mean()

    volatility = simulations.std()

    best_case = np.percentile(
        simulations,
        95
    )

    worst_case = np.percentile(
        simulations,
        5
    )

    risk_score = max(
        0,
        100 - volatility
    )

    if volatility < 15:
        risk_category = "Low Risk"

    elif volatility < 30:
        risk_category = "Moderate Risk"

    else:
        risk_category = "High Risk"

    simulation_results.append({
        "portfolio": portfolio_name,
        "expected_return_pct":
            round(expected_return, 2),

        "volatility_pct":
            round(volatility, 2),

        "best_case_pct":
            round(best_case, 2),

        "worst_case_pct":
            round(worst_case, 2),

        "risk_score":
            round(risk_score, 2),

        "risk_category":
            risk_category
    })

# -----------------------------------
# SAVE OUTPUTS
# -----------------------------------

results = pd.DataFrame(
    simulation_results
)

results.to_excel(
    OUTPUT_DIR / "portfolio_simulation.xlsx",
    index=False
)

risk_scores = (
    results[
        [
            "portfolio",
            "risk_score",
            "risk_category"
        ]
    ]
)

risk_scores.to_excel(
    OUTPUT_DIR / "risk_scores.xlsx",
    index=False
)

print(
    "Portfolios simulated:",
    len(results)
)

print(
    "Saved -> output/portfolio_simulation.xlsx"
)

print(
    "Saved -> output/risk_scores.xlsx"
)