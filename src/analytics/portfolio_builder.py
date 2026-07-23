import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("output")

rankings = pd.read_excel(
    OUTPUT_DIR / "company_rankings.xlsx"
)

# -----------------------------------
# TOP COMPOUNDER PORTFOLIO
# -----------------------------------

compounders = (
    rankings
    .sort_values(
        "compounder_score",
        ascending=False
    )
    .head(10)
    .copy()
)

compounders["weight_pct"] = 10.0

compounders[
    [
        "overall_rank",
        "company_id",
        "compounder_score",
        "weight_pct"
    ]
].to_excel(
    OUTPUT_DIR / "top10_compounder_portfolio.xlsx",
    index=False
)

# -----------------------------------
# TOP VALUE PORTFOLIO
# -----------------------------------

value_portfolio = (
    rankings
    .sort_values(
        "value_score",
        ascending=False
    )
    .head(10)
    .copy()
)

value_portfolio["weight_pct"] = 10.0

value_portfolio[
    [
        "company_id",
        "value_score",
        "weight_pct"
    ]
].to_excel(
    OUTPUT_DIR / "top10_value_portfolio.xlsx",
    index=False
)

# -----------------------------------
# TOP GROWTH PORTFOLIO
# -----------------------------------

growth_portfolio = (
    rankings
    .sort_values(
        "growth_score",
        ascending=False
    )
    .head(10)
    .copy()
)

growth_portfolio["weight_pct"] = 10.0

growth_portfolio[
    [
        "company_id",
        "growth_score",
        "weight_pct"
    ]
].to_excel(
    OUTPUT_DIR / "top10_growth_portfolio.xlsx",
    index=False
)

# -----------------------------------
# QUALITY PORTFOLIO
# -----------------------------------

quality_portfolio = (
    rankings
    .sort_values(
        "quality_score",
        ascending=False
    )
    .head(10)
    .copy()
)

quality_portfolio["weight_pct"] = 10.0

quality_portfolio[
    [
        "company_id",
        "quality_score",
        "weight_pct"
    ]
].to_excel(
    OUTPUT_DIR / "top10_quality_portfolio.xlsx",
    index=False
)

print("Saved -> output/top10_compounder_portfolio.xlsx")
print("Saved -> output/top10_value_portfolio.xlsx")
print("Saved -> output/top10_growth_portfolio.xlsx")
print("Saved -> output/top10_quality_portfolio.xlsx")