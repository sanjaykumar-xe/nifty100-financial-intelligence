import sqlite3
from pathlib import Path

import pandas as pd

DB = "db/nifty100.db"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

# ---------------------------------
# LOAD DATA
# ---------------------------------

rankings = pd.read_excel(
    "output/company_rankings.xlsx"
)

sectors = pd.read_sql("""
SELECT company_id,
       broad_sector
FROM sectors
""", conn)

# ---------------------------------
# MERGE
# ---------------------------------

df = rankings.merge(
    sectors,
    on="company_id",
    how="left"
)

# ---------------------------------
# SECTOR SUMMARY
# ---------------------------------

sector_summary = (
    df.groupby("broad_sector")
    .agg(
        companies=("company_id", "count"),
        avg_quality_score=("quality_score", "mean"),
        avg_growth_score=("growth_score", "mean"),
        avg_value_score=("value_score", "mean"),
        avg_compounder_score=("compounder_score", "mean")
    )
    .reset_index()
)

sector_summary = sector_summary.sort_values(
    "avg_compounder_score",
    ascending=False
)

# ---------------------------------
# TOP SECTOR TABLES
# ---------------------------------

top_quality_sector = (
    sector_summary
    .sort_values(
        "avg_quality_score",
        ascending=False
    )
)

top_growth_sector = (
    sector_summary
    .sort_values(
        "avg_growth_score",
        ascending=False
    )
)

top_value_sector = (
    sector_summary
    .sort_values(
        "avg_value_score",
        ascending=False
    )
)

# ---------------------------------
# SAVE
# ---------------------------------

sector_summary.to_excel(
    OUTPUT_DIR / "sector_summary.xlsx",
    index=False
)

top_quality_sector.to_excel(
    OUTPUT_DIR / "top_quality_sectors.xlsx",
    index=False
)

top_growth_sector.to_excel(
    OUTPUT_DIR / "top_growth_sectors.xlsx",
    index=False
)

top_value_sector.to_excel(
    OUTPUT_DIR / "top_value_sectors.xlsx",
    index=False
)

print("Sectors analyzed:", len(sector_summary))
print("Saved -> output/sector_summary.xlsx")
print("Saved -> output/top_quality_sectors.xlsx")
print("Saved -> output/top_growth_sectors.xlsx")
print("Saved -> output/top_value_sectors.xlsx")