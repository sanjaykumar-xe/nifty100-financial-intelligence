import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("output")

# -----------------------------------
# LOAD DATA
# -----------------------------------

compounder = pd.read_excel(
    OUTPUT_DIR / "top10_compounder_portfolio.xlsx"
)

quality = pd.read_excel(
    OUTPUT_DIR / "top10_quality_portfolio.xlsx"
)

growth = pd.read_excel(
    OUTPUT_DIR / "top10_growth_portfolio.xlsx"
)

value = pd.read_excel(
    OUTPUT_DIR / "top10_value_portfolio.xlsx"
)

sector_map = pd.read_excel(
    OUTPUT_DIR / "valuation_summary.xlsx"
)[["company_id", "broad_sector"]]

# -----------------------------------
# PORTFOLIOS
# -----------------------------------

portfolios = {
    "Compounder": compounder,
    "Quality": quality,
    "Growth": growth,
    "Value": value
}

risk_rows = []
sector_rows = []
concentration_rows = []

# -----------------------------------
# ANALYSIS
# -----------------------------------

for portfolio_name, df in portfolios.items():

    df = df.merge(
        sector_map,
        on="company_id",
        how="left"
    )

    total_stocks = len(df)

    sector_counts = (
        df.groupby("broad_sector")
        .size()
        .reset_index(name="count")
    )

    sector_counts["weight_pct"] = (
        sector_counts["count"]
        / total_stocks
        * 100
    )

    num_sectors = len(sector_counts)

    largest_sector_weight = (
        sector_counts["weight_pct"].max()
    )

    diversification_score = (
        (num_sectors / total_stocks) * 100
    )

    risk_rows.append({
        "portfolio": portfolio_name,
        "stocks": total_stocks,
        "sectors": num_sectors,
        "largest_sector_pct": round(
            largest_sector_weight, 2
        ),
        "diversification_score": round(
            diversification_score, 2
        )
    })

    for _, row in sector_counts.iterrows():

        sector_rows.append({
            "portfolio": portfolio_name,
            "sector": row["broad_sector"],
            "count": row["count"],
            "weight_pct": round(
                row["weight_pct"], 2
            )
        })

    largest_holding = (
        df.sort_values(
            "weight_pct",
            ascending=False
        )
        .iloc[0]
    )

    concentration_rows.append({
        "portfolio": portfolio_name,
        "largest_holding":
            largest_holding["company_id"],
        "weight_pct":
            largest_holding["weight_pct"]
    })

# -----------------------------------
# SAVE OUTPUTS
# -----------------------------------

risk_df = pd.DataFrame(risk_rows)

sector_df = pd.DataFrame(sector_rows)

concentration_df = pd.DataFrame(
    concentration_rows
)

risk_df.to_excel(
    OUTPUT_DIR / "portfolio_risk_analysis.xlsx",
    index=False
)

sector_df.to_excel(
    OUTPUT_DIR / "sector_exposure.xlsx",
    index=False
)

concentration_df.to_excel(
    OUTPUT_DIR / "concentration_risk.xlsx",
    index=False
)

print(
    "Saved -> output/portfolio_risk_analysis.xlsx"
)

print(
    "Saved -> output/sector_exposure.xlsx"
)

print(
    "Saved -> output/concentration_risk.xlsx"
)