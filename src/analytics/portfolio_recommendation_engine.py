from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path("output")

# -------------------------
# LOAD DATA
# -------------------------

simulation = pd.read_excel(
    OUTPUT_DIR / "portfolio_simulation.xlsx"
)

risk = pd.read_excel(
    OUTPUT_DIR / "risk_scores.xlsx"
)

# -------------------------
# INVESTOR PROFILES
# -------------------------

profiles = pd.DataFrame([
    {
        "investor_type": "Conservative",
        "recommended_portfolio": "Quality",
        "reason": "Lowest risk and stable returns"
    },
    {
        "investor_type": "Growth",
        "recommended_portfolio": "Growth",
        "reason": "Highest expected return"
    },
    {
        "investor_type": "Value",
        "recommended_portfolio": "Value",
        "reason": "Focus on undervalued opportunities"
    },
    {
        "investor_type": "Long Term Compounder",
        "recommended_portfolio": "Compounder",
        "reason": "Balanced quality and growth"
    }
])

# -------------------------
# STRATEGY RECOMMENDATIONS
# -------------------------

recommendations = pd.DataFrame([
    {
        "investor_type": "Conservative",
        "recommended_strategy": "Quality"
    },
    {
        "investor_type": "Growth",
        "recommended_strategy": "Growth"
    },
    {
        "investor_type": "Value",
        "recommended_strategy": "Value"
    },
    {
        "investor_type": "Long Term Compounder",
        "recommended_strategy": "Compounder"
    }
])

# -------------------------
# SAVE
# -------------------------

profiles.to_excel(
    OUTPUT_DIR / "investor_profiles.xlsx",
    index=False
)

simulation.to_excel(
    OUTPUT_DIR / "recommended_portfolios.xlsx",
    index=False
)

recommendations.to_excel(
    OUTPUT_DIR / "strategy_recommendations.xlsx",
    index=False
)

print("Saved -> output/investor_profiles.xlsx")
print("Saved -> output/recommended_portfolios.xlsx")
print("Saved -> output/strategy_recommendations.xlsx")